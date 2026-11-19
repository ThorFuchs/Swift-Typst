import Foundation
import Testing
@testable import SwiftTypst

@Test func rendersSVGPathSegments() throws {
    // Exercise lines, quadratic and cubic curves, close, stroke, filled paths,
    // multiple subpaths, transformations and a quadratic after a close command.
    let svg = #"""
    <svg xmlns="http://www.w3.org/2000/svg" width="360" height="220" viewBox="0 0 360 220">
      <rect width="360" height="220" fill="white"/>
      <path d="M 15 25 L 95 25 Q 130 25 130 60 C 130 95 95 100 70 80 Z" fill="#4286c3" stroke="#123456" stroke-width="3"/>
      <path d="M 155 25 Q 220 -20 255 60 Q 285 130 335 50" fill="none" stroke="#bf374e" stroke-width="4"/>
      <path d="M 15 145 C 45 100 75 200 105 145 L 125 180 Z M 40 155 Q 60 130 80 155 Z" fill="#72a75b" fill-rule="evenodd"/>
      <path d="M 150 145 L 180 125 L 205 145 Z Q 235 195 265 145" fill="none" stroke="#6a3980" stroke-width="3"/>
      <g transform="translate(280 140) rotate(25)"><path d="M 0 0 Q 25 -30 50 0 L 50 35 Q 25 55 0 35 Z" fill="#e7ab31"/></g>
      <path d="M 151.123 201.875 Q 233.716 154.129 349.251 199.307" fill="none" stroke="#14786f" stroke-width="2"/>
    </svg>
    """#
    let project = TypstProject(main: "main.typ", files: [
        "main.typ": .text("#set page(width: 14cm, height: 10cm, margin: 1cm)\n#image(\"paths.svg\", width: 12cm)"),
        "paths.svg": .bytes(Data(svg.utf8)),
    ])
    let result = try TypstCompiler().compilePDF(project)
    #expect(result.pageCount == 1)
    #expect(result.warnings.isEmpty)
    #expect(result.pdf.starts(with: Data("%PDF-".utf8)))
}
