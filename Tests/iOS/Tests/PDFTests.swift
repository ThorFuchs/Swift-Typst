import Foundation
import SwiftTypst
import XCTest

final class PDFTests: XCTestCase {
    func testPDFAndDiagnostic() async throws {
        let (result, font, diagnostic): (TypstPDFResult, TypstPDFResult, TypstError?) = try await Task.detached(priority: .utility) {
            let compiler = TypstCompiler()
            let result = try compiler.compilePDF("= iOS SwiftPM test")
            let font = try compiler.compilePDF("$ x^2 + y^2 $")
            do {
                _ = try compiler.compilePDF("#let x = (")
                return (result, font, nil)
            } catch let error as TypstError {
                return (result, font, error)
            }
        }.value
        XCTAssertTrue(result.pdf.starts(with: Data("%PDF-".utf8)))
        XCTAssertEqual(result.pageCount, 1)
        XCTAssertNotNil(font.pdf.range(of: Data("STIXTwoMath".utf8)))
        XCTAssertNil(font.pdf.range(of: Data("NewCM10-Regular".utf8)))
        let error = try XCTUnwrap(diagnostic)
        XCTAssertEqual(error.code, .compilationFailed)
        XCTAssertFalse(error.diagnostics.isEmpty)
    }
}
