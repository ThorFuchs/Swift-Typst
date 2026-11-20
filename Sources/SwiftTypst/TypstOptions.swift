import Foundation

/// A PDF standard supported by the pinned Typst backend.
public enum TypstPDFStandard: String, Codable, Sendable, CaseIterable {
    /// PDF 1.4.
    case pdf14 = "1.4"
    /// PDF 1.5.
    case pdf15 = "1.5"
    /// PDF 1.6.
    case pdf16 = "1.6"
    /// PDF 1.7.
    case pdf17 = "1.7"
    /// PDF 2.0.
    case pdf20 = "2.0"
    /// PDF/A-1b.
    case a1b = "a-1b"
    /// PDF/A-1a.
    case a1a = "a-1a"
    /// PDF/A-2b.
    case a2b = "a-2b"
    /// PDF/A-2u.
    case a2u = "a-2u"
    /// PDF/A-2a.
    case a2a = "a-2a"
    /// PDF/A-3b.
    case a3b = "a-3b"
    /// PDF/A-3u.
    case a3u = "a-3u"
    /// PDF/A-3a.
    case a3a = "a-3a"
    /// PDF/A-4.
    case a4 = "a-4"
    /// PDF/A-4f.
    case a4f = "a-4f"
    /// PDF/A-4e.
    case a4e = "a-4e"
    /// PDF/UA-1.
    case ua1 = "ua-1"
}

/// An inclusive one-based page range. A missing end means the last page.
public struct TypstPageRange: Sendable, Equatable, Codable {
    /// The first selected page, or `nil` for the beginning.
    public var start: Int?
    /// The last selected page, or `nil` for the end.
    public var end: Int?

    /// Creates an inclusive page range using one-based page numbers.
    /// - Parameters:
    ///   - start: The first page, or `nil` for the beginning.
    ///   - end: The last page, or `nil` for the end.
    public init(start: Int? = nil, end: Int? = nil) {
        self.start = start
        self.end = end
    }

    /// Selects one page using a one-based page number.
    public static func page(_ number: Int) -> Self { .init(start: number, end: number) }
}

/// PDF export settings. By default Typst emits tagged PDF with its default standard.
public struct TypstPDFOptions: Sendable, Equatable {
    /// PDF standards requested from the exporter.
    public var standards: [TypstPDFStandard]
    /// Whether the PDF should contain accessibility tags.
    public var tagged: Bool
    /// Nil selects all pages; supplied ranges use one-based inclusive coordinates.
    public var pages: [TypstPageRange]?
    /// PDF creation metadata, independent of the date exposed to Typst documents.
    public var creationDate: Date?

    /// Creates PDF export settings.
    /// - Parameters:
    ///   - standards: PDF standards requested from Typst.
    ///   - tagged: Whether to produce a tagged PDF.
    ///   - pages: Optional one-based inclusive page ranges.
    ///   - creationDate: Optional PDF creation metadata timestamp.
    public init(
        standards: [TypstPDFStandard] = [],
        tagged: Bool = true,
        pages: [TypstPageRange]? = nil,
        creationDate: Date? = nil
    ) {
        self.standards = standards
        self.tagged = tagged
        self.pages = pages
        self.creationDate = creationDate
    }
}

/// The instant and local UTC offset exposed to `datetime.today()`.
public enum TypstClock: Sendable, Equatable {
    /// Capture the current instant and local offset at the start of compilation.
    case system
    /// Use a fixed instant and a local UTC offset in seconds.
    case fixed(Date, localOffsetSeconds: Int)
    /// Make the current date unavailable to Typst.
    case unavailable
}

/// Optional bounds on supplied file/font bytes and on the returned PDF.
/// These are not execution time or peak-memory limits.
public struct TypstResourceLimits: Sendable, Equatable {
    /// Maximum combined bytes of supplied project files, packages, and fonts.
    public var maximumResourceBytes: Int?
    /// Maximum returned PDF size, checked after export.
    public var maximumPDFBytes: Int?

    /// Creates optional byte limits; `nil` means no wrapper limit.
    /// - Parameters:
    ///   - maximumResourceBytes: Maximum aggregate supplied resource bytes.
    ///   - maximumPDFBytes: Maximum exported PDF bytes, checked after export.
    public init(maximumResourceBytes: Int? = nil, maximumPDFBytes: Int? = nil) {
        self.maximumResourceBytes = maximumResourceBytes
        self.maximumPDFBytes = maximumPDFBytes
    }
}

/// Options for a single compilation.
public struct TypstCompileOptions: Sendable, Equatable {
    /// String-valued inputs visible through Typst's `sys.inputs`.
    public var inputs: [String: String]
    /// The clock made available to the document.
    public var clock: TypstClock
    /// Settings used for PDF export.
    public var pdf: TypstPDFOptions
    /// Optional bounds for supplied resources and returned PDF bytes.
    public var limits: TypstResourceLimits

    /// Creates settings for one compile.
    /// - Parameters:
    ///   - inputs: Values made available through Typst's `sys.inputs`.
    ///   - clock: The time exposed to the document.
    ///   - pdf: PDF export settings.
    ///   - limits: Optional supplied-resource and output byte limits.
    public init(
        inputs: [String: String] = [:],
        clock: TypstClock = .system,
        pdf: TypstPDFOptions = .init(),
        limits: TypstResourceLimits = .init()
    ) {
        self.inputs = inputs
        self.clock = clock
        self.pdf = pdf
        self.limits = limits
    }
}
