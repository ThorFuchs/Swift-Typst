use std::{collections::HashMap, str::FromStr};
use typst::{
    Library, LibraryExt, World,
    diag::{FileError, FileResult},
    foundations::{Bytes, Datetime, Dict, Duration, IntoValue, NativeElement, Recipe, Selector, Styles, Transformation},
    syntax::{FileId, RootedPath, Source, Span, VirtualPath, VirtualRoot, package::PackageSpec},
    text::{Font, FontBook, FontFamily, FontList, TextElem},
    math::EquationElem,
    utils::LazyHash,
};
use crate::Request;

pub struct MemoryWorld {
    library: LazyHash<Library>,
    book: LazyHash<FontBook>,
    main: FileId,
    files: HashMap<FileId, Bytes>,
    sources: HashMap<FileId, Source>,
    fonts: Vec<Font>,
    clock: Option<i64>,
    local_offset: i32,
}

fn path(input: &str) -> Result<VirtualPath, String> {
    if input.is_empty() || input.starts_with('/') || input.contains('\\') || input.contains('\0')
        || input.split('/').any(|part| part.is_empty() || part == "." || part == "..") {
        return Err(format!("invalid virtual path: {input:?}"));
    }
    VirtualPath::new(input).map_err(|e| format!("invalid virtual path {input:?}: {e}"))
}

fn buffer(blob: &[u8], offset: usize, length: usize) -> Result<&[u8], String> {
    let end = offset.checked_add(length).ok_or("buffer range overflow")?;
    blob.get(offset..end).ok_or_else(|| "buffer range is outside request data".to_string())
}

impl MemoryWorld {
    pub fn new(request: &Request, blob: &[u8]) -> Result<Self, String> {
        let main = FileId::new(RootedPath::new(VirtualRoot::Project, path(&request.main)?));
        let mut files = HashMap::new();
        let mut sources = HashMap::new();
        for file in &request.files {
            let root = match &file.package {
                Some(spec) => VirtualRoot::Package(PackageSpec::from_str(spec).map_err(|e| e.to_string())?),
                None => VirtualRoot::Project,
            };
            let id = FileId::new(RootedPath::new(root, path(&file.path)?));
            let data = buffer(blob, file.offset, file.length)?;
            if files.contains_key(&id) { return Err(format!("duplicate virtual path: {}", file.path)); }
            if let Ok(text) = std::str::from_utf8(data) {
                sources.insert(id, Source::new(id, text.to_owned()));
            }
            files.insert(id, Bytes::new(data.to_vec()));
        }
        if !files.contains_key(&main) { return Err(format!("main source not found: {}", request.main)); }
        if !sources.contains_key(&main) { return Err("main source is not valid UTF-8".into()); }
        let mut fonts: Vec<Font> = Vec::new();
        for data in &request.fonts {
            let bytes = buffer(blob, data.offset, data.length)?;
            let parsed: Vec<_> = Font::iter(Bytes::new(bytes.to_vec())).collect();
            if parsed.is_empty() { return Err("a supplied font contains no readable faces".into()); }
            fonts.extend(parsed);
        }
        if request.bundled_fonts {
            // Pinned Libertinus, STIX Two and DejaVu faces. The typst-assets
            // bundled-font feature remains disabled.
            let selected: &[&'static [u8]] = &[
                include_bytes!("../fonts/LibertinusSerif-Regular.otf") as &'static [u8],
                include_bytes!("../fonts/LibertinusSerif-Bold.otf") as &'static [u8],
                include_bytes!("../fonts/LibertinusSerif-Italic.otf") as &'static [u8],
                include_bytes!("../fonts/LibertinusSerif-BoldItalic.otf") as &'static [u8],
                include_bytes!("../fonts/LibertinusSerif-Semibold.otf") as &'static [u8],
                include_bytes!("../fonts/LibertinusSerif-SemiboldItalic.otf") as &'static [u8],
                include_bytes!("../fonts/STIXTwoMath-Regular.otf") as &'static [u8],
                include_bytes!("../fonts/STIXTwoText-Regular.otf") as &'static [u8],
                include_bytes!("../fonts/STIXTwoText-Italic.otf") as &'static [u8],
                include_bytes!("../fonts/STIXTwoText-Bold.otf") as &'static [u8],
                include_bytes!("../fonts/STIXTwoText-BoldItalic.otf") as &'static [u8],
                include_bytes!("../fonts/DejaVuSansMono-Bold.ttf") as &'static [u8],
                include_bytes!("../fonts/DejaVuSansMono-BoldOblique.ttf") as &'static [u8],
                include_bytes!("../fonts/DejaVuSansMono-Oblique.ttf") as &'static [u8],
                include_bytes!("../fonts/DejaVuSansMono.ttf") as &'static [u8]
            ];
            fonts.extend(selected.iter().flat_map(|data| Font::iter(Bytes::new(*data))));
        }
        let mut inputs = Dict::new();
        for (key, value) in &request.inputs { inputs.insert(key.as_str().into(), value.clone().into_value()); }
        if request.clock_unix_seconds.is_some_and(|seconds| time::OffsetDateTime::from_unix_timestamp(seconds).is_err()) {
            return Err("invalid clock timestamp".into());
        }
        if request.local_offset_seconds.unsigned_abs() >= 86_400 { return Err("local UTC offset must be less than 24 hours".into()); }
        let mut library = Library::builder().with_inputs(inputs).build();
        if request.bundled_fonts {
            // A library-level show-set rule preserves source ranges and allows
            // the caller's document-level show rules to override this default.
            let mut math = Styles::new();
            math.set(TextElem::font, FontList(vec![FontFamily::new("STIX Two Math")]));
            library.styles.push(Recipe::new(
                Some(Selector::Elem(EquationElem::ELEM, None)),
                Transformation::Style(math),
                Span::detached(),
            ));
        }
        Ok(Self {
            library: LazyHash::new(library),
            book: LazyHash::new(FontBook::from_fonts(&fonts)),
            main, files, sources, fonts,
            clock: request.clock_unix_seconds,
            local_offset: request.local_offset_seconds,
        })
    }
}

pub fn display_id(id: FileId) -> String {
    let name = id.vpath().get_without_slash();
    match id.get().root() {
        VirtualRoot::Project => name.to_string(),
        VirtualRoot::Package(spec) => format!("{spec}/{name}"),
    }
}

impl World for MemoryWorld {
    fn library(&self) -> &LazyHash<Library> { &self.library }
    fn book(&self) -> &LazyHash<FontBook> { &self.book }
    fn main(&self) -> FileId { self.main }
    fn source(&self, id: FileId) -> FileResult<Source> {
        if let Some(source) = self.sources.get(&id) { return Ok(source.clone()); }
        if self.files.contains_key(&id) { return Err(FileError::InvalidUtf8); }
        Err(FileError::NotFound(id.vpath().get_without_slash().into()))
    }
    fn file(&self, id: FileId) -> FileResult<Bytes> {
        self.files.get(&id).cloned().ok_or_else(|| FileError::NotFound(id.vpath().get_without_slash().into()))
    }
    fn font(&self, index: usize) -> Option<Font> { self.fonts.get(index).cloned() }
    fn today(&self, offset: Option<Duration>) -> Option<Datetime> {
        let instant = time::OffsetDateTime::from_unix_timestamp(self.clock?).ok()?;
        let seconds = match offset {
            None => i64::from(self.local_offset),
            Some(duration) => {
                let [weeks, days, hours, minutes, seconds] = duration.decompose();
                weeks.checked_mul(604_800)?.checked_add(days.checked_mul(86_400)?)?
                    .checked_add(hours.checked_mul(3_600)?)?.checked_add(minutes.checked_mul(60)?)?
                    .checked_add(seconds)?
            }
        };
        let date = instant.checked_add(time::Duration::seconds(seconds))?.date();
        Datetime::from_ymd(date.year(), date.month() as u8, date.day())
    }
}
