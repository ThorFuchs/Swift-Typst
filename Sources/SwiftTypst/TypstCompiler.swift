import CTypstBridge
import Foundation

/// Compiles in-memory Typst projects to PDF using the embedded Typst engine.
///
/// Calls are synchronous and may take substantial time. Schedule work away
/// from the main actor when compiling from an interactive application.
public struct TypstCompiler: Sendable {
    /// The pinned upstream Typst release.
    public static let engineVersion = "0.15.1"

    /// Creates a compiler for independent synchronous compile calls.
    public init() {}

    /// Compiles a single UTF-8 source using bundled fonts.
    /// - Parameters:
    ///   - source: The Typst source text.
    ///   - options: Input, clock, PDF, and resource settings.
    /// - Returns: The exported PDF, page counts, and warnings.
    /// - Throws: A ``TypstError`` if compilation or export fails.
    public func compilePDF(
        _ source: String,
        options: TypstCompileOptions = .init()
    ) throws -> TypstPDFResult {
        try compilePDF(
            TypstProject(main: "main.typ", files: ["main.typ": .text(source)]),
            options: options
        )
    }

    /// Compiles a snapshot with explicitly supplied files, packages, and fonts.
    /// - Parameters:
    ///   - project: The entry point and its in-memory resources.
    ///   - options: Input, clock, PDF, and resource settings.
    /// - Returns: The exported PDF, page counts, and warnings.
    /// - Throws: A ``TypstError`` if compilation or export fails.
    public func compilePDF(
        _ project: TypstProject,
        options: TypstCompileOptions = .init()
    ) throws -> TypstPDFResult {
        guard (options.limits.maximumResourceBytes ?? 0) >= 0,
              (options.limits.maximumPDFBytes ?? 0) >= 0 else {
            throw TypstError(.invalidRequest, message: "Resource limits must be nonnegative")
        }
        var blob = Data()
        func checkResourceSize(_ size: Int) throws {
            let (total, overflow) = blob.count.addingReportingOverflow(size)
            guard !overflow, options.limits.maximumResourceBytes.map({ total <= $0 }) ?? true else {
                throw TypstError(.resourceLimitExceeded, message: "File and font bytes exceed the configured limit")
            }
        }
        var files: [FileEntry] = []
        for (path, file) in project.files.sorted(by: { $0.key < $1.key }) {
            let data = file.data
            try checkResourceSize(data.count)
            files.append(.init(path: path, package: nil, offset: blob.count, length: data.count))
            blob.append(data)
        }
        for package in project.packages {
            for (path, file) in package.files.sorted(by: { $0.key < $1.key }) {
                let data = file.data
                try checkResourceSize(data.count)
                files.append(.init(path: path, package: package.name, offset: blob.count, length: data.count))
                blob.append(data)
            }
        }
        var fonts: [BufferRange] = []
        for data in project.fonts {
            try checkResourceSize(data.count)
            fonts.append(.init(offset: blob.count, length: data.count))
            blob.append(data)
        }
        let (clock, offset) = try Self.clock(options.clock)
        let request = Request(
            main: project.main,
            files: files,
            fonts: fonts,
            bundledFonts: project.useBundledFonts,
            inputs: options.inputs,
            clockUnixSeconds: clock,
            localOffsetSeconds: offset,
            pdf: .init(
                standards: options.pdf.standards.map(\.rawValue),
                tagged: options.pdf.tagged,
                pageRanges: options.pdf.pages,
                creationTimestamp: try options.pdf.creationDate.map(Self.seconds)
            )
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = .sortedKeys
        let encoded: Data
        do {
            encoded = try encoder.encode(request)
        } catch {
            throw TypstError(.bridgeError, message: "Failed to encode the compile request: \(error)")
        }

        // Rust requires non-null pointers even for empty buffers.
        let blobLength = blob.count
        if blob.isEmpty { blob.append(0) }
        let handle = encoded.withUnsafeBytes { requestBytes in
            blob.withUnsafeBytes { blobBytes in
                swift_typst_compile(
                    requestBytes.bindMemory(to: UInt8.self).baseAddress, encoded.count,
                    blobBytes.bindMemory(to: UInt8.self).baseAddress, blobLength
                )
            }
        }
        guard let handle else { throw TypstError(.bridgeError, message: "Failed to create a bridge result") }
        defer { swift_typst_result_free(handle) }

        guard let metadataPointer = swift_typst_metadata_data(handle) else {
            throw TypstError(.bridgeError, message: "Bridge returned invalid metadata")
        }
        let metadataBytes = Data(bytes: metadataPointer, count: swift_typst_metadata_length(handle))
        let metadata: Metadata
        do {
            metadata = try JSONDecoder().decode(Metadata.self, from: metadataBytes)
        } catch {
            throw TypstError(.bridgeError, message: "Failed to decode bridge metadata: \(error)")
        }
        guard metadata.status == "ok" else {
            throw TypstError(.init(rawValue: metadata.status), message: metadata.message, diagnostics: metadata.diagnostics)
        }
        let pdfLength = swift_typst_pdf_length(handle)
        guard options.limits.maximumPDFBytes.map({ pdfLength <= $0 }) ?? true else {
            throw TypstError(.resourceLimitExceeded, message: "PDF exceeds the configured limit")
        }
        guard let pdfPointer = swift_typst_pdf_data(handle) else {
            throw TypstError(.bridgeError, message: "Bridge returned invalid PDF data")
        }
        return TypstPDFResult(
            pdf: Data(bytes: pdfPointer, count: pdfLength),
            pageCount: metadata.pageCount,
            documentPageCount: metadata.documentPageCount,
            warnings: metadata.diagnostics
        )
    }

    private static func seconds(_ date: Date) throws -> Int64 {
        let value = date.timeIntervalSince1970.rounded(.down)
        guard value.isFinite, value >= Double(Int64.min), value < Double(Int64.max) else {
            throw TypstError(.invalidRequest, message: "Date is outside the supported timestamp range")
        }
        return Int64(value)
    }

    private static func clock(_ clock: TypstClock) throws -> (Int64?, Int) {
        switch clock {
        case .system:
            let now = Date()
            return (try seconds(now), TimeZone.current.secondsFromGMT(for: now))
        case .fixed(let date, let offset):
            guard (-86_399...86_399).contains(offset) else {
                throw TypstError(.invalidRequest, message: "Local UTC offset must be less than 24 hours")
            }
            return (try seconds(date), offset)
        case .unavailable:
            return (nil, 0)
        }
    }
}

private struct BufferRange: Encodable {
    let offset: Int
    let length: Int
}

private struct FileEntry: Encodable {
    let path: String
    let package: String?
    let offset: Int
    let length: Int
}

private struct Request: Encodable {
    struct PDF: Encodable {
        let standards: [String]
        let tagged: Bool
        let pageRanges: [TypstPageRange]?
        let creationTimestamp: Int64?
    }
    let main: String
    let files: [FileEntry]
    let fonts: [BufferRange]
    let bundledFonts: Bool
    let inputs: [String: String]
    let clockUnixSeconds: Int64?
    let localOffsetSeconds: Int
    let pdf: PDF
}

private struct Metadata: Decodable {
    let status: String
    let message: String?
    let diagnostics: [TypstDiagnostic]
    let pageCount: Int
    let documentPageCount: Int
}
