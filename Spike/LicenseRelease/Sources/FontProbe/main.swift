import Foundation
import SwiftTypst

// Deliberately accept external font files: the probe does not redistribute them.
guard CommandLine.arguments.count == 4 else {
    fatalError("Usage: FontProbe <text-font> <math-font> <output-directory>")
}
let arguments = CommandLine.arguments
let fonts = try arguments[1...2].map { try Data(contentsOf: URL(fileURLWithPath: $0)) }
let output = URL(fileURLWithPath: arguments[3], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let cases = [
    ("implicit", "A formula: $ sum_(k=1)^n k = (n(n+1))/2 $"),
    ("explicit", "#show math.equation: set text(font: \"STIX Two Math\")\nA formula: $ sum_(k=1)^n k = (n(n+1))/2 $")
]
let compiler = TypstCompiler()
for (name, source) in cases {
    let project = TypstProject(
        main: "main.typ", files: ["main.typ": .text(source)],
        fonts: fonts, useBundledFonts: false
    )
    let result = try compiler.compilePDF(project)
    try result.pdf.write(to: output.appendingPathComponent("\(name).pdf"))
    print("\(name): pages=\(result.pageCount), bytes=\(result.pdf.count), warnings=\(result.warnings.count)")
    for warning in result.warnings { print("  warning: \(warning.message)") }
}
