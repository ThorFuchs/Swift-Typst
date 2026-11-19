import Foundation

/// A zero-based, half-open UTF-8 byte range in a virtual file.
public struct TypstSourceRange: Sendable, Equatable, Codable {
    public let path: String
    public let start: Int
    public let end: Int
}

/// A compiler warning or error, including upstream hints and trace messages.
public struct TypstDiagnostic: Sendable, Equatable, Decodable {
    public enum Severity: String, Sendable, Decodable { case error, warning }
    /// An upstream hint or trace point, optionally associated with a source range.
    public struct Note: Sendable, Equatable, Decodable {
        public let message: String
        public let path: String?
        public let start: Int?
        public let end: Int?

        public var range: TypstSourceRange? {
            guard let path, let start, let end else { return nil }
            return TypstSourceRange(path: path, start: start, end: end)
        }
    }
    public let severity: Severity
    public let message: String
    public let path: String?
    public let start: Int?
    public let end: Int?
    public let hints: [Note]
    public let trace: [Note]

    public var range: TypstSourceRange? {
        guard let path, let start, let end else { return nil }
        return TypstSourceRange(path: path, start: start, end: end)
    }
}

/// A failure from the wrapper, compiler, or PDF exporter.
public struct TypstError: Error, Sendable, CustomStringConvertible {
    public struct Code: RawRepresentable, Sendable, Equatable, Hashable {
        public let rawValue: String
        public init(rawValue: String) { self.rawValue = rawValue }
        public static let invalidRequest = Self(rawValue: "invalidRequest")
        public static let compilationFailed = Self(rawValue: "compilationFailed")
        public static let exportFailed = Self(rawValue: "exportFailed")
        public static let bridgeError = Self(rawValue: "bridgeError")
        public static let resourceLimitExceeded = Self(rawValue: "resourceLimitExceeded")
    }
    public let code: Code
    public let message: String?
    public let diagnostics: [TypstDiagnostic]

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
    public let pdf: Data
    /// Pages in the exported PDF, after page selection.
    public let pageCount: Int
    /// Pages in the laid-out document, before page selection.
    public let documentPageCount: Int
    public let warnings: [TypstDiagnostic]
}
