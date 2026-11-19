import Foundation
import SwiftTypst

// Both modes use the same text fonts and the same source. Only the selected
// mathematics font changes. Font bytes are supplied by the caller.
guard CommandLine.arguments.count >= 6 else {
    fatalError("Usage: CorpusProbe <fixtures> <output> <newcm-math> <stix-math> <text-font> [text-font ...]")
}
let args = CommandLine.arguments
let fixtures = URL(fileURLWithPath: args[1], isDirectory: true)
let output = URL(fileURLWithPath: args[2], isDirectory: true)
let fileManager = FileManager.default
if fileManager.fileExists(atPath: output.path) {
    guard try fileManager.contentsOfDirectory(atPath: output.path).isEmpty else {
        fatalError("Output directory must be empty")
    }
} else {
    try fileManager.createDirectory(at: output, withIntermediateDirectories: true)
}
let commonFonts = try args[5...].map { try Data(contentsOf: URL(fileURLWithPath: $0)) }
let paths = try fileManager.contentsOfDirectory(at: fixtures, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "typ" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
guard !paths.isEmpty else { fatalError("No Typst fixtures") }
let compiler = TypstCompiler()
let options = TypstCompileOptions(clock: .fixed(Date(timeIntervalSince1970: 0), localOffsetSeconds: 0))
struct Record: Encodable {
    let fixture: String
    let mode: String
    let pages: Int?
    let bytes: Int?
    let warnings: [String]
    let error: String?
}
var records: [Record] = []
for (mode, fontPath, family) in [("newcm", args[3], "New Computer Modern Math"), ("stix", args[4], "STIX Two Math")] {
    let mathFont = try Data(contentsOf: URL(fileURLWithPath: fontPath))
    let directory = output.appendingPathComponent(mode, isDirectory: true)
    try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
    for path in paths {
        let source = try String(contentsOf: path, encoding: .utf8)
        let prefix = "#set page(width: 16cm, height: 22cm, margin: 1.2cm)\n#set text(font: \"Libertinus Serif\", size: 11pt)\n#show math.equation: set text(font: \"\(family)\")\n"
        let project = TypstProject(main: "main.typ", files: ["main.typ": .text(prefix + source)], fonts: commonFonts + [mathFont], useBundledFonts: false)
        do {
            let result = try compiler.compilePDF(project, options: options)
            try result.pdf.write(to: directory.appendingPathComponent(path.deletingPathExtension().lastPathComponent + ".pdf"))
            let warnings = result.warnings.map(\.message)
            print("\(mode) \(path.lastPathComponent): pages=\(result.pageCount) warnings=\(warnings.count)")
            records.append(.init(fixture: path.lastPathComponent, mode: mode, pages: result.pageCount, bytes: result.pdf.count, warnings: warnings, error: nil))
        } catch {
            print("\(mode) \(path.lastPathComponent): ERROR \(error)")
            records.append(.init(fixture: path.lastPathComponent, mode: mode, pages: nil, bytes: nil, warnings: [], error: String(describing: error)))
        }
    }
}
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
try encoder.encode(records).write(to: output.appendingPathComponent("results.json"))
if records.contains(where: { $0.error != nil }) { exit(1) }
