import Foundation

/// A file made available to Typst in the project's virtual filesystem.
public enum TypstFile: Sendable, Equatable {
    /// A UTF-8 text source or other textual resource.
    case text(String)
    /// An arbitrary binary resource, such as an image.
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
    /// Files keyed by their paths inside the package.
    public var files: [String: TypstFile]

    /// Creates an explicitly supplied package and its virtual files.
    /// - Parameters:
    ///   - name: The complete Typst package identity.
    ///   - files: The package files keyed by relative path.
    public init(name: String, files: [String: TypstFile]) {
        self.name = name
        self.files = files
    }
}

/// An immutable-at-compilation snapshot of sources, assets, packages, and fonts.
public struct TypstProject: Sendable, Equatable {
    /// The relative path of the entry-point Typst source.
    public var main: String
    /// Files keyed by relative path in the project's virtual filesystem.
    public var files: [String: TypstFile]
    /// Explicitly supplied packages available to the document.
    public var packages: [TypstPackage]
    /// Additional OpenType or TrueType font files, searched before bundled fonts.
    public var fonts: [Data]
    /// Whether the bundled font collection is available during compilation.
    public var useBundledFonts: Bool

    /// Creates a project snapshot for an in-memory compile.
    /// - Parameters:
    ///   - main: The path of the entry-point source in `files`.
    ///   - files: Project files and assets keyed by relative path.
    ///   - packages: Explicit packages available to the project.
    ///   - fonts: Additional OpenType or TrueType font files.
    ///   - useBundledFonts: Whether to include the built-in font collection.
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
