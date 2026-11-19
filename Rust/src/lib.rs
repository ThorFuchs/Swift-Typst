//! Internal Swift-Typst C bridge. All returned storage remains Rust-owned.
mod world;

use serde::{Deserialize, Serialize};
use std::{collections::BTreeMap, num::NonZeroUsize, panic::catch_unwind, slice};
use typst::{WorldExt, diag::{Severity, SourceDiagnostic}, foundations::{Datetime, Smart}, layout::PageRanges, syntax::DiagSpan};
use typst_layout::PagedDocument;
use typst_pdf::{PdfOptions, PdfStandard, PdfStandards, Timestamp};
use world::MemoryWorld;

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Request {
    main: String,
    files: Vec<FileEntry>,
    fonts: Vec<BufferRange>,
    bundled_fonts: bool,
    inputs: BTreeMap<String, String>,
    clock_unix_seconds: Option<i64>,
    local_offset_seconds: i32,
    pdf: PDFOptions,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct FileEntry {
    path: String,
    package: Option<String>,
    offset: usize,
    length: usize,
}

#[derive(Deserialize)]
struct BufferRange { offset: usize, length: usize }

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct PDFOptions {
    standards: Vec<String>,
    tagged: bool,
    page_ranges: Option<Vec<PageRange>>,
    creation_timestamp: Option<i64>,
}

#[derive(Deserialize)]
struct PageRange { start: Option<usize>, end: Option<usize> }

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Diagnostic {
    severity: &'static str,
    message: String,
    path: Option<String>,
    start: Option<usize>,
    end: Option<usize>,
    hints: Vec<DiagnosticNote>,
    trace: Vec<DiagnosticNote>,
}

#[derive(Serialize)]
struct DiagnosticNote {
    message: String,
    path: Option<String>,
    start: Option<usize>,
    end: Option<usize>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Metadata {
    status: &'static str,
    message: Option<String>,
    diagnostics: Vec<Diagnostic>,
    page_count: usize,
    document_page_count: usize,
}

pub struct CompileResult { pdf: Vec<u8>, metadata: Vec<u8> }

fn result(status: &'static str, message: Option<String>, diagnostics: Vec<Diagnostic>, pdf: Vec<u8>, page_count: usize, document_page_count: usize) -> CompileResult {
    let metadata = Metadata { status, message, diagnostics, page_count, document_page_count };
    CompileResult { pdf, metadata: serde_json::to_vec(&metadata).unwrap_or_else(|_| b"{\"status\":\"bridgeError\"}".to_vec()) }
}

fn configuration_error(message: impl Into<String>) -> CompileResult {
    result("invalidRequest", Some(message.into()), vec![], vec![], 0, 0)
}

fn pdf_standard(value: &str) -> Option<PdfStandard> {
    Some(match value {
        "1.4" => PdfStandard::V_1_4, "1.5" => PdfStandard::V_1_5,
        "1.6" => PdfStandard::V_1_6, "1.7" => PdfStandard::V_1_7,
        "2.0" => PdfStandard::V_2_0, "a-1b" => PdfStandard::A_1b,
        "a-1a" => PdfStandard::A_1a, "a-2b" => PdfStandard::A_2b,
        "a-2u" => PdfStandard::A_2u, "a-2a" => PdfStandard::A_2a,
        "a-3b" => PdfStandard::A_3b, "a-3u" => PdfStandard::A_3u,
        "a-3a" => PdfStandard::A_3a, "a-4" => PdfStandard::A_4,
        "a-4f" => PdfStandard::A_4f, "a-4e" => PdfStandard::A_4e,
        "ua-1" => PdfStandard::Ua_1, _ => return None,
    })
}

fn pdf_options(input: &PDFOptions) -> Result<PdfOptions, String> {
    let standards: Vec<_> = input.standards.iter().map(|s| pdf_standard(s).ok_or_else(|| format!("unknown PDF standard: {s}"))).collect::<Result<_, _>>()?;
    let standards = PdfStandards::new(&standards).map_err(|e| e.message().to_string())?;
    let page_ranges = input.page_ranges.as_ref().map(|ranges| {
        if ranges.is_empty() { return Err("page ranges must not be empty".to_string()); }
        let mut parsed = Vec::with_capacity(ranges.len());
        for range in ranges {
            let start = range.start.map(|n| NonZeroUsize::new(n).ok_or("page numbers start at 1")).transpose()?;
            let end = range.end.map(|n| NonZeroUsize::new(n).ok_or("page numbers start at 1")).transpose()?;
            if start.is_none() && end.is_none() { return Err("page range needs at least one bound".to_string()); }
            if matches!((start, end), (Some(a), Some(b)) if a > b) { return Err("page range start exceeds end".to_string()); }
            parsed.push(start..=end);
        }
        Ok(PageRanges::new(parsed))
    }).transpose()?;
    let timestamp = input.creation_timestamp.map(|seconds| {
        let dt = time::OffsetDateTime::from_unix_timestamp(seconds).map_err(|_| "invalid PDF creation timestamp")?;
        let typst_dt = Datetime::from_ymd_hms(dt.year(), dt.month() as u8, dt.day(), dt.hour(), dt.minute(), dt.second()).ok_or("invalid PDF creation timestamp")?;
        Ok::<_, &str>(Timestamp::new_utc(typst_dt))
    }).transpose().map_err(str::to_string)?;
    Ok(PdfOptions { standards, tagged: input.tagged, page_ranges, timestamp, creator: Smart::Auto, ident: Smart::Auto, pretty: false })
}

fn diagnostic(world: &MemoryWorld, item: &SourceDiagnostic) -> Diagnostic {
    let id = item.span.id();
    let range = world.range(item.span);
    Diagnostic {
        severity: match item.severity { Severity::Error => "error", Severity::Warning => "warning" },
        message: item.message.to_string(),
        path: id.map(world::display_id),
        start: range.as_ref().map(|r| r.start),
        end: range.as_ref().map(|r| r.end),
        hints: item.hints.iter().map(|h| note(world, h.v.to_string(), h.span)).collect(),
        trace: item.trace.iter().map(|t| note(world, t.v.to_string(), t.span.into())).collect(),
    }
}

fn note(world: &MemoryWorld, message: String, span: DiagSpan) -> DiagnosticNote {
    let range = world.range(span);
    DiagnosticNote {
        message,
        path: span.id().map(world::display_id),
        start: range.as_ref().map(|r| r.start),
        end: range.as_ref().map(|r| r.end),
    }
}

fn compile(request: &[u8], blob: &[u8]) -> CompileResult {
    let request: Request = match serde_json::from_slice(request) {
        Ok(value) => value, Err(error) => return configuration_error(error.to_string())
    };
    let options = match pdf_options(&request.pdf) { Ok(value) => value, Err(message) => return configuration_error(message) };
    let world = match MemoryWorld::new(&request, blob) { Ok(value) => value, Err(message) => return configuration_error(message) };
    let compiled = typst::compile::<PagedDocument>(&world);
    let mut diagnostics: Vec<_> = compiled.warnings.iter().map(|d| diagnostic(&world, d)).collect();
    let document = match compiled.output {
        Ok(doc) => doc,
        Err(errors) => {
            diagnostics.extend(errors.iter().map(|d| diagnostic(&world, d)));
            return result("compilationFailed", None, diagnostics, vec![], 0, 0);
        }
    };
    let total = document.pages().len();
    let selected = (0..total).filter(|&i| options.page_ranges.as_ref().is_none_or(|ranges| ranges.includes_page_index(i))).count();
    match typst_pdf::pdf(&document, &options) {
        Ok(pdf) => result("ok", None, diagnostics, pdf, selected, total),
        Err(errors) => {
            diagnostics.extend(errors.iter().map(|d| diagnostic(&world, d)));
            result("exportFailed", None, diagnostics, vec![], 0, total)
        }
    }
}

/// Pointers must reference readable memory of the given lengths for the duration of the call.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn swift_typst_compile(request: *const u8, request_len: usize, blob: *const u8, blob_len: usize) -> *mut CompileResult {
    if request.is_null() || blob.is_null() || request_len > isize::MAX as usize || blob_len > isize::MAX as usize { return std::ptr::null_mut(); }
    let outcome = catch_unwind(|| {
        // SAFETY: The caller promises valid buffers and both sizes were bounded.
        compile(unsafe { slice::from_raw_parts(request, request_len) }, unsafe { slice::from_raw_parts(blob, blob_len) })
    }).unwrap_or_else(|_| result("bridgeError", Some("Typst panicked".into()), vec![], vec![], 0, 0));
    Box::into_raw(Box::new(outcome))
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn swift_typst_pdf_data(result: *const CompileResult) -> *const u8 { unsafe { (*result).pdf.as_ptr() } }
#[unsafe(no_mangle)]
pub unsafe extern "C" fn swift_typst_pdf_length(result: *const CompileResult) -> usize { unsafe { (*result).pdf.len() } }
#[unsafe(no_mangle)]
pub unsafe extern "C" fn swift_typst_metadata_data(result: *const CompileResult) -> *const u8 { unsafe { (*result).metadata.as_ptr() } }
#[unsafe(no_mangle)]
pub unsafe extern "C" fn swift_typst_metadata_length(result: *const CompileResult) -> usize { unsafe { (*result).metadata.len() } }
/// The handle must have been returned by swift_typst_compile and be freed exactly once.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn swift_typst_result_free(result: *mut CompileResult) {
    if !result.is_null() { drop(unsafe { Box::from_raw(result) }); }
}
