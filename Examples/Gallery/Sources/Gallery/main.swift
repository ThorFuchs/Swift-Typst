import Foundation
import SwiftTypst

func report(_ message: String) {
    FileHandle.standardError.write(Data((message + "\n").utf8))
}

func renderGallery() throws {
    let arguments = CommandLine.arguments
    guard arguments.count == 3 else {
        throw GalleryError.usage
    }
    let sourceDirectory = URL(fileURLWithPath: arguments[1], isDirectory: true)
    let outputDirectory = URL(fileURLWithPath: arguments[2], isDirectory: true)
    let filenames = ["01-editorial", "02-mathematics", "03-report", "04-invoice", "05-resume", "06-letter"]
    let fixedDate = Date(timeIntervalSince1970: 1_735_689_600)
    let options = TypstCompileOptions(
        clock: .fixed(fixedDate, localOffsetSeconds: 0),
        pdf: .init(creationDate: fixedDate)
    )
    let compiler = TypstCompiler()
    try FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)
    for name in filenames {
        let sourceURL = sourceDirectory.appendingPathComponent(name + ".typ")
        let outputURL = outputDirectory.appendingPathComponent(name + ".pdf")
        let source = try String(contentsOf: sourceURL, encoding: .utf8)
        do {
            let result = try compiler.compilePDF(source, options: options)
            guard result.pageCount == 1, result.documentPageCount == 1 else {
                throw GalleryError.invalidPageCount(name, result.documentPageCount)
            }
            guard result.warnings.isEmpty else {
                throw GalleryError.warnings(name, result.warnings.map(\.message))
            }
            try result.pdf.write(to: outputURL, options: .atomic)
            print("\(name): one page, no warnings")
        } catch let error as TypstError {
            for diagnostic in error.diagnostics {
                report("\(name): \(diagnostic.message) (\(diagnostic.path ?? "main.typ"):\(diagnostic.start ?? 0))")
                for hint in diagnostic.hints { report("  hint: \(hint.message)") }
            }
            throw error
        }
    }
}

enum GalleryError: Error, CustomStringConvertible {
    case usage
    case invalidPageCount(String, Int)
    case warnings(String, [String])

    var description: String {
        switch self {
        case .usage: "Usage: Gallery <source-directory> <output-directory>"
        case let .invalidPageCount(name, count): "\(name): expected one page, got \(count)"
        case let .warnings(name, messages): "\(name): " + messages.joined(separator: "; ")
        }
    }
}

do {
    try renderGallery()
} catch {
    report("Gallery: \(error)")
    exit(1)
}
