import Foundation
import SwiftTypst

struct ProbeFailure: Error {}

func check(_ source: String, shouldFail: Bool) throws {
    do {
        let result = try TypstCompiler().compilePDF(source)
        if shouldFail || !result.pdf.starts(with: Data("%PDF-".utf8)) { throw ProbeFailure() }
    } catch let error as TypstError {
        if !shouldFail || error.diagnostics.isEmpty { throw ProbeFailure() }
    }
}

@main struct Stress {
    static func main() async throws {
        let valid = "= Test\nA formula $ integral_0^1 x^2 dif x = 1 / 3 $ and text."
        let invalid = ["#let x = (", "#import \"missing.typ\"", "#assert(false)", "#image(\"absent.svg\")"]
        for i in 0..<400 {
            try check(i.isMultiple(of: 2) ? valid : invalid[i % invalid.count], shouldFail: !i.isMultiple(of: 2))
        }
        try await withThrowingTaskGroup(of: Void.self) { group in
            for i in 0..<8 {
                group.addTask {
                    for j in 0..<30 {
                        let fail = (i + j).isMultiple(of: 2)
                        try check(fail ? invalid[(i + j) % invalid.count] : valid, shouldFail: fail)
                    }
                }
            }
            try await group.waitForAll()
        }
        print("Passed 400 sequential and 240 concurrent PDF/diagnostic checks")
    }
}
