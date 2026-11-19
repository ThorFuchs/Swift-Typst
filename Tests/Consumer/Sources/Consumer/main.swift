import Foundation
import SwiftTypst

let compiler = TypstCompiler()
let result = try compiler.compilePDF("= Swift Typst consumer\n\nHello from the PDF bridge.")
guard result.pdf.starts(with: Data("%PDF-".utf8)), result.pageCount == 1 else {
    fatalError("Invalid PDF")
}
let project = TypstProject(main: "main.typ", files: [
    "main.typ": .text("""
    #import "chapter.typ": title
    #assert.eq(sys.inputs.customer, "Rhoe")
    = #title
    #image("image.svg")
    """),
    "chapter.typ": .text("#let title = [Imported title]"),
    "image.svg": .bytes(Data("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"5\" height=\"5\"></svg>".utf8)),
])
let projectResult = try compiler.compilePDF(project, options: .init(inputs: ["customer": "Rhoe"]))
guard projectResult.pageCount == 1 else { fatalError("Project compilation failed") }
let package = TypstPackage(name: "@local/hello:1.0.0", files: [
    "typst.toml": .text("""
    [package]
    name = "hello"
    version = "1.0.0"
    entrypoint = "lib.typ"
    authors = ["Test"]
    license = "MIT"
    description = "Test package"
    """),
    "lib.typ": .text("#let greeting = [Hello from a package]"),
])
let packageProject = TypstProject(main: "main.typ", files: [
    "main.typ": .text("#import \"@local/hello:1.0.0\": greeting\n#greeting")
], packages: [package])
guard try compiler.compilePDF(packageProject).pageCount == 1 else { fatalError("Package compilation failed") }
let fontResult = try compiler.compilePDF("#set text(font: \"STIX Two Text\")\nRegular text")
guard fontResult.pdf.range(of: Data("STIXTwoText".utf8)) != nil,
      fontResult.pdf.range(of: Data("NewCM10-Regular".utf8)) == nil else {
    fatalError("Unexpected STIX Two Text face")
}
let mathResult = try compiler.compilePDF("Formula: $ x^2 + y^2 $")
guard mathResult.warnings.isEmpty, mathResult.pdf.range(of: Data("STIXTwoMath".utf8)) != nil else {
    fatalError("Unexpected default math font")
}
let pages = try compiler.compilePDF("First#pagebreak()Second", options: .init(pdf: .init(tagged: false, pages: [.page(2)])))
guard pages.pageCount == 1, pages.documentPageCount == 2 else { fatalError("Page selection failed") }
let clock = TypstCompileOptions(clock: .fixed(Date(timeIntervalSince1970: 0), localOffsetSeconds: 0))
_ = try compiler.compilePDF("#assert.eq(datetime.today(offset: 0), datetime(year: 1970, month: 1, day: 1))", options: clock)
do {
    _ = try compiler.compilePDF("hello", options: .init(limits: .init(maximumResourceBytes: 2)))
    fatalError("Expected a resource limit error")
} catch let error as TypstError {
    guard error.code == .resourceLimitExceeded else { throw error }
}
if CommandLine.arguments.count > 1 {
    try result.pdf.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
}
do {
    _ = try compiler.compilePDF("#let x = (")
    fatalError("Expected a compilation failure")
} catch let error as TypstError {
    guard error.code == .compilationFailed, !error.diagnostics.isEmpty else { throw error }
}
print("consumer: PDF and diagnostics OK")
