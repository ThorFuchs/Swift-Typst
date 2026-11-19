import Foundation

/// A PDF standard supported by the pinned Typst backend.
public enum TypstPDFStandard: String, Codable, Sendable, CaseIterable {
    case pdf14 = "1.4", pdf15 = "1.5", pdf16 = "1.6", pdf17 = "1.7", pdf20 = "2.0"
    case a1b = "a-1b", a1a = "a-1a", a2b = "a-2b", a2u = "a-2u", a2a = "a-2a"
    case a3b = "a-3b", a3u = "a-3u", a3a = "a-3a", a4 = "a-4", a4f = "a-4f", a4e = "a-4e"
    case ua1 = "ua-1"
}

/// An inclusive one-based page range. A missing end means the last page.
public struct TypstPageRange: Sendable, Equatable, Codable {
    public var start: Int?
    public var end: Int?

    public init(start: Int? = nil, end: Int? = nil) {
        self.start = start
        self.end = end
    }

    public static func page(_ number: Int) -> Self { .init(start: number, end: number) }
}

/// PDF export settings. By default Typst emits tagged PDF with its default standard.
public struct TypstPDFOptions: Sendable, Equatable {
    public var standards: [TypstPDFStandard]
    public var tagged: Bool
    /// Nil selects all pages; supplied ranges use one-based inclusive coordinates.
    public var pages: [TypstPageRange]?
    /// PDF creation metadata, independent of the date exposed to Typst documents.
    public var creationDate: Date?

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
    public var maximumResourceBytes: Int?
    public var maximumPDFBytes: Int?

    public init(maximumResourceBytes: Int? = nil, maximumPDFBytes: Int? = nil) {
        self.maximumResourceBytes = maximumResourceBytes
        self.maximumPDFBytes = maximumPDFBytes
    }
}

/// Options for a single compilation.
public struct TypstCompileOptions: Sendable, Equatable {
    /// String-valued inputs visible through Typst's `sys.inputs`.
    public var inputs: [String: String]
    public var clock: TypstClock
    public var pdf: TypstPDFOptions
    public var limits: TypstResourceLimits

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
