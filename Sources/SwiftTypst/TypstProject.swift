import Foundation

/// A file made available to Typst in the project's virtual filesystem.
public enum TypstFile: Sendable, Equatable {
    case text(String)
    case bytes(Data)

    var data: Data {
        switch self {
        case .text(let source): Data(source.utf8)
        case .bytes(let bytes): bytes
        }
    }
}

/// A specific Typst package and its in-memory files.
public struct TypstPackage: Sendable, Equatable {
    /// Typst package identity, such as `@local/example:1.0.0`.
    public var name: String
    public var files: [String: TypstFile]

    public init(name: String, files: [String: TypstFile]) {
        self.name = name
        self.files = files
    }
}

/// An immutable-at-compilation snapshot of sources, assets, packages, and fonts.
public struct TypstProject: Sendable, Equatable {
    public var main: String
    public var files: [String: TypstFile]
    public var packages: [TypstPackage]
    /// Additional OpenType or TrueType font files, searched before bundled fonts.
    public var fonts: [Data]
    public var useBundledFonts: Bool

    public init(
        main: String,
        files: [String: TypstFile],
        packages: [TypstPackage] = [],
        fonts: [Data] = [],
        useBundledFonts: Bool = true
    ) {
        self.main = main
        self.files = files
        self.packages = packages
        self.fonts = fonts
        self.useBundledFonts = useBundledFonts
    }
}
