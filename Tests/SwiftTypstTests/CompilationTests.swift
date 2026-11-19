import Foundation
import Testing
@testable import SwiftTypst

@Test func compilesOneShotPDF() throws {
    let result = try TypstCompiler().compilePDF("= Hello from Swift\n")
    #expect(result.pdf.starts(with: Data("%PDF-".utf8)))
    #expect(result.pageCount == 1)
    #expect(result.documentPageCount == 1)
    #expect(result.warnings.allSatisfy { $0.severity == .warning })
}

@Test func reportsSourceDiagnostics() throws {
    do {
        _ = try TypstCompiler().compilePDF("Hello 🐎\n#let x = (")
        Issue.record("Invalid source compiled successfully")
    } catch let error as TypstError {
        #expect(error.code == .compilationFailed)
        #expect(error.diagnostics.contains { $0.severity == .error && $0.path == "main.typ" })
        for diagnostic in error.diagnostics {
            if let range = diagnostic.range {
                #expect(range.start >= 0)
                #expect(range.end >= range.start)
                #expect(range.end <= "Hello 🐎\n#let x = (".utf8.count)
            }
        }
    }
}

@Test func compilesProjectWithImportsAndInput() throws {
    let project = TypstProject(
        main: "main.typ",
        files: [
            "main.typ": .text("""
            #import "chapter.typ": greeting
            #assert.eq(sys.inputs.customer, "Rhoe")
            = #greeting
            """),
            "chapter.typ": .text("#let greeting = [Hello from an import]"),
        ]
    )
    let result = try TypstCompiler().compilePDF(project, options: .init(inputs: ["customer": "Rhoe"]))
    #expect(result.pageCount == 1)
    #expect(result.pdf.starts(with: Data("%PDF-".utf8)))
}

@Test func compilesInMemoryPackageAndAsset() throws {
    let package = TypstPackage(name: "@local/greetings:1.0.0", files: [
        "typst.toml": .text("""
        [package]
        name = "greetings"
        version = "1.0.0"
        entrypoint = "lib.typ"
        authors = ["Example"]
        license = "MIT"
        description = "Test package"
        """),
        "lib.typ": .text("#let hello = [Hello from a package]"),
    ])
    let project = TypstProject(
        main: "main.typ",
        files: [
            "main.typ": .text("""
            #import "@local/greetings:1.0.0": hello
            #hello
            #image("logo.svg")
            """),
            "logo.svg": .bytes(Data("""
            <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
              <rect width="10" height="10" fill="red"/>
            </svg>
            """.utf8)),
        ],
        packages: [package]
    )
    let result = try TypstCompiler().compilePDF(project)
    #expect(result.pageCount == 1)
    #expect(result.pdf.starts(with: Data("%PDF-".utf8)))
}

@Test func selectsPagesAndKeepsDocumentCount() throws {
    let source = "First page\n#pagebreak()\nSecond page"
    let options = TypstCompileOptions(pdf: .init(tagged: false, pages: [.page(2)]))
    let result = try TypstCompiler().compilePDF(source, options: options)
    #expect(result.documentPageCount == 2)
    #expect(result.pageCount == 1)
}

@Test func taggedPDFRejectsPageSelection() throws {
    do {
        _ = try TypstCompiler().compilePDF("Hello", options: .init(pdf: .init(pages: [.page(1)])))
        Issue.record("Tagged PDF with page selection was accepted")
    } catch let error as TypstError {
        #expect(error.code == .exportFailed)
        #expect(error.diagnostics.contains { $0.message.contains("tagged PDF") })
    }
}

@Test func usesFixedClock() throws {
    let source = "#assert.eq(datetime.today(offset: 0), datetime(year: 1970, month: 1, day: 1))"
    let options = TypstCompileOptions(clock: .fixed(Date(timeIntervalSince1970: 0), localOffsetSeconds: 0))
    let result = try TypstCompiler().compilePDF(source, options: options)
    #expect(result.pageCount == 1)
}

@Test func usesLocalAndFractionalHourOffsets() throws {
    let source = """
    #assert.eq(datetime.today(), datetime(year: 1969, month: 12, day: 31))
    #assert.eq(datetime.today(offset: duration(minutes: 330)), datetime(year: 1970, month: 1, day: 1))
    """
    let options = TypstCompileOptions(clock: .fixed(Date(timeIntervalSince1970: 0), localOffsetSeconds: -1800))
    #expect(try TypstCompiler().compilePDF(source, options: options).pageCount == 1)
}

@Test func rejectsInvalidFontData() throws {
    let project = TypstProject(main: "main.typ", files: ["main.typ": .text("Hi")], fonts: [Data([0, 1, 2])])
    do {
        _ = try TypstCompiler().compilePDF(project)
        Issue.record("Invalid font bytes were accepted")
    } catch let error as TypstError {
        #expect(error.code == .invalidRequest)
    }
}

@Test func enforcesResourceAndOutputLimits() throws {
    let compiler = TypstCompiler()
    for limits in [TypstResourceLimits(maximumResourceBytes: 2), TypstResourceLimits(maximumPDFBytes: 10)] {
        do {
            _ = try compiler.compilePDF("hello", options: .init(limits: limits))
            Issue.record("Limit was not enforced")
        } catch let error as TypstError {
            #expect(error.code == .resourceLimitExceeded)
        }
    }
    do {
        _ = try compiler.compilePDF("hello", options: .init(limits: .init(maximumPDFBytes: -1)))
        Issue.record("Invalid limit was accepted")
    } catch let error as TypstError {
        #expect(error.code == .invalidRequest)
    }
}

@Test func rejectsUnsafePathsAndIncompatibleStandards() throws {
    let project = TypstProject(main: "../main.typ", files: ["../main.typ": .text("hello")])
    #expect(throws: TypstError.self) { try TypstCompiler().compilePDF(project) }
    do {
        _ = try TypstCompiler().compilePDF("hello", options: .init(pdf: .init(standards: [.pdf14, .pdf20])))
        Issue.record("Incompatible PDF standards were accepted")
    } catch let error as TypstError {
        #expect(error.code == .invalidRequest)
    }
}

@Test func reportsMissingImport() throws {
    do {
        _ = try TypstCompiler().compilePDF("#include \"missing.typ\"")
        Issue.record("Missing file was accepted")
    } catch let error as TypstError {
        #expect(error.code == .compilationFailed)
        #expect(error.diagnostics.contains { $0.message.localizedCaseInsensitiveContains("not found") })
    }
}

@Test func returnsWarningsForMissingFont() throws {
    let result = try TypstCompiler().compilePDF("#set text(font: \"SwiftTypstMissingFontForTest\")\nHello")
    #expect(result.warnings.contains { $0.severity == .warning && $0.message.contains("font") })
}

@Test func usesBundledSTIXForDefaultMath() throws {
    let result = try TypstCompiler().compilePDF("Formula: $ sum_(i=1)^n i = n(n+1)/2 $")
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) != nil)
}

@Test func usesBundledSTIXTextAndWarnsForMissingNewCM() throws {
    let compiler = TypstCompiler()
    let stix = try compiler.compilePDF("#set text(font: \"STIX Two Text\")\nNormal, *bold* and _italic_ text.")
    #expect(stix.warnings.isEmpty)
    #expect(stix.pdf.range(of: Data("STIXTwoText".utf8)) != nil)
    let missing = try compiler.compilePDF("#set text(font: \"New Computer Modern\")\nRegular text")
    #expect(missing.warnings.contains { $0.message.localizedCaseInsensitiveContains("font") })
}

@Test func documentMathRuleOverridesBundledDefault() throws {
    let source = "#show math.equation: set text(font: \"STIX Two Text\")\n$ x^2 + y^2 $"
    let result = try TypstCompiler().compilePDF(source)
    #expect(result.warnings.contains { $0.message.contains("not designed for math") })
}

#if !os(WASI)
@Test func acceptsCallerSuppliedMathFontWithoutBundledFonts() throws {
    let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
        .deletingLastPathComponent().deletingLastPathComponent()
    let font = try Data(contentsOf: root.appendingPathComponent("Rust/fonts/STIXTwoMath-Regular.otf"))
    let source = "#set text(font: \"STIX Two Math\")\n#show math.equation: set text(font: \"STIX Two Math\")\n$ x^2 + y^2 $"
    let project = TypstProject(main: "main.typ", files: ["main.typ": .text(source)],
                               fonts: [font], useBundledFonts: false)
    let result = try TypstCompiler().compilePDF(project)
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) != nil)
}
#endif

@Test func bundledMathHandlesRepresentativeDocuments() throws {
    let sources = [
        "$ integral_0^infinity e^(-x^2) dif x = sqrt(pi) / 2 $",
        "$ A = mat(1, 2; 3, 4), quad vec(v) = vec(x, y, z) $",
        "$ f(x) = cases(x^2 & \"if\" x >= 0, -x & \"otherwise\") $",
        "Ελληνικά: Καλημέρα. Кириллица: Привет. $ alpha + beta = gamma $",
        "$ forall x in RR: x^2 >= 0 quad exists y in RR: y^2 = 2 $",
    ]
    let compiler = TypstCompiler()
    for source in sources {
        let result = try compiler.compilePDF(source)
        #expect(result.pageCount == 1)
        #expect(result.warnings.isEmpty)
        #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) != nil)
    }
}

@Test func reportsImportedSourceLocation() throws {
    let project = TypstProject(main: "main.typ", files: [
        "main.typ": .text("#include \"broken.typ\""),
        "broken.typ": .text("#let x = ("),
    ])
    do {
        _ = try TypstCompiler().compilePDF(project)
        Issue.record("Invalid imported source compiled successfully")
    } catch let error as TypstError {
        #expect(error.diagnostics.contains { $0.severity == .error && $0.range?.path == "broken.typ" })
    }
}

@Test func concurrentIndependentCompiles() async throws {
    let compiler = TypstCompiler()
    try await withThrowingTaskGroup(of: Int.self) { group in
        for index in 0..<2 {
            group.addTask {
                let result = try compiler.compilePDF("= Document \(index)")
                return result.pageCount
            }
        }
        var counts: [Int] = []
        for try await count in group { counts.append(count) }
        #expect(counts.sorted() == [1, 1])
    }
}
