import Foundation

/// A zero-based, half-open UTF-8 byte range in a virtual file.
public struct TypstSourceRange: Sendable, Equatable, Codable {
    /// The virtual source path, including package identity when applicable.
    public let path: String
    /// The inclusive start offset in UTF-8 bytes.
    public let start: Int
    /// The exclusive end offset in UTF-8 bytes.
    public let end: Int
}

/// A compiler warning or error, including upstream hints and trace messages.
public struct TypstDiagnostic: Sendable, Equatable, Decodable {
    /// A warning or error emitted by the Typst engine.
    public enum Severity: String, Sendable, Decodable {
        /// A fatal diagnostic that prevented a successful result.
        case error
        /// A non-fatal diagnostic reported with the result.
        case warning
    }
    /// An upstream hint or trace point, optionally associated with a source range.
    public struct Note: Sendable, Equatable, Decodable {
        /// The human-readable hint or trace message.
        public let message: String
        /// The virtual source path, when available.
        public let path: String?
        /// The inclusive UTF-8 byte offset, when available.
        public let start: Int?
        /// The exclusive UTF-8 byte offset, when available.
        public let end: Int?

        /// A range when the path and both offsets are available.
        public var range: TypstSourceRange? {
            guard let path, let start, let end else { return nil }
            return TypstSourceRange(path: path, start: start, end: end)
        }
    }
    /// The diagnostic's severity.
    public let severity: Severity
    /// The human-readable message from Typst.
    public let message: String
    /// The virtual source path, when available.
    public let path: String?
    /// The inclusive UTF-8 byte offset, when available.
    public let start: Int?
    /// The exclusive UTF-8 byte offset, when available.
    public let end: Int?
    /// Additional hints supplied by the engine.
    public let hints: [Note]
    /// Trace entries describing the diagnostic's context.
    public let trace: [Note]

    /// A range when the path and both offsets are available.
    public var range: TypstSourceRange? {
        guard let path, let start, let end else { return nil }
        return TypstSourceRange(path: path, start: start, end: end)
    }
}

/// A failure from the wrapper, compiler, or PDF exporter.
public struct TypstError: Error, Sendable, CustomStringConvertible {
    /// A stable wrapper-level failure category.
    public struct Code: RawRepresentable, Sendable, Equatable, Hashable {
        /// The code's string representation.
        public let rawValue: String
        /// Creates a code from its string representation.
        public init(rawValue: String) { self.rawValue = rawValue }
        /// The wrapper could not accept the request.
        public static let invalidRequest = Self(rawValue: "invalidRequest")
        /// Typst could not compile the document.
        public static let compilationFailed = Self(rawValue: "compilationFailed")
        /// PDF export failed after compilation.
        public static let exportFailed = Self(rawValue: "exportFailed")
        /// The Swift and engine bridge could not complete the request.
        public static let bridgeError = Self(rawValue: "bridgeError")
        /// A configured supplied-resource or output-size limit was exceeded.
        public static let resourceLimitExceeded = Self(rawValue: "resourceLimitExceeded")
    }
    /// The wrapper-level failure category.
    public let code: Code
    /// A summary message when available.
    public let message: String?
    /// Engine diagnostics associated with the failure.
    public let diagnostics: [TypstDiagnostic]

    /// A readable summary of the failure.
    public var description: String {
        message ?? diagnostics.first(where: { $0.severity == .error })?.message
            ?? diagnostics.first?.message ?? "Typst error: \(code.rawValue)"
    }

    init(_ code: Code, message: String? = nil, diagnostics: [TypstDiagnostic] = []) {
        self.code = code
        self.message = message
        self.diagnostics = diagnostics
    }
}

/// The PDF and warnings produced by one compilation.
public struct TypstPDFResult: Sendable {
    /// The exported PDF bytes.
    public let pdf: Data
    /// Pages in the exported PDF, after page selection.
    public let pageCount: Int
    /// Pages in the laid-out document, before page selection.
    public let documentPageCount: Int
    /// Non-fatal diagnostics emitted during compilation and export.
    public let warnings: [TypstDiagnostic]
}
