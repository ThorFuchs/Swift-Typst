import Foundation
import Testing
@testable import SwiftTypst

private func originalMathFont() throws -> Data {
    let path = try #require(ProcessInfo.processInfo.environment["SWIFT_TYPST_TEST_NEWCM_MATH"])
    return try Data(contentsOf: URL(fileURLWithPath: path))
}

@Test func candidateDefaultMathUsesSTIXWithoutWarnings() throws {
    let result = try TypstCompiler().compilePDF("Formula: $ sum_(i=1)^n i = n(n+1)/2 $")
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) != nil)
}

@Test func explicitMathFontRuleOverridesCandidateDefault() throws {
    let source = "#show math.equation: set text(font: \"New Computer Modern Math\")\n$ x^2 + y^2 $"
    let project = TypstProject(main: "main.typ", files: ["main.typ": .text(source)], fonts: [try originalMathFont()])
    let result = try TypstCompiler().compilePDF(project)
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.range(of: Data("NewCMMath".utf8)) != nil)
    #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) == nil)
}

@Test func disabledBundledFontsRetainUpstreamDefault() throws {
    let source = "$ x^2 + y^2 $"
    let project = TypstProject(main: "main.typ", files: ["main.typ": .text(source)], fonts: [try originalMathFont()], useBundledFonts: false)
    let result = try TypstCompiler().compilePDF(project)
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.range(of: Data("NewCMMath".utf8)) != nil)
    #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) == nil)
}

@Test func explicitNewCMTextWithoutFontProducesWarning() throws {
    let result = try TypstCompiler().compilePDF("#set text(font: \"New Computer Modern\")\nRegular text")
    #expect(result.warnings.contains { $0.message.localizedCaseInsensitiveContains("font") })
}

@Test func candidateSTIXTextFacesCanBeSelected() throws {
    let source = "#set text(font: \"STIX Two Text\")\nNormal, *bold* and _italic_."
    let result = try TypstCompiler().compilePDF(source)
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.range(of: Data("STIXTwoText".utf8)) != nil)
}

@Test func candidateCorpusRunsWithoutUserFontOverrides() throws {
    let path = try #require(ProcessInfo.processInfo.environment["SWIFT_TYPST_TEST_CORPUS"])
    let directory = URL(fileURLWithPath: path, isDirectory: true)
    let fixtures = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        .filter { $0.pathExtension == "typ" }
        .sorted { $0.lastPathComponent < $1.lastPathComponent }
    #expect(fixtures.count == 6)
    let compiler = TypstCompiler()
    for fixture in fixtures {
        let source = try String(contentsOf: fixture, encoding: .utf8)
        let result = try compiler.compilePDF(source)
        #expect(result.warnings.isEmpty, "Unexpected warning in \(fixture.lastPathComponent)")
        #expect(result.pdf.range(of: Data("STIXTwoMath".utf8)) != nil, "STIX not embedded for \(fixture.lastPathComponent)")
    }
}
