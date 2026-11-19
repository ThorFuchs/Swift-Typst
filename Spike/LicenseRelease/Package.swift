// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "FontProbe",
    platforms: [.macOS(.v14)],
    dependencies: [.package(path: "../..")],
    targets: [
        .executableTarget(
            name: "FontProbe",
            dependencies: [.product(name: "SwiftTypst", package: "Swift-Typst")]
        ),
        .executableTarget(
            name: "CorpusProbe",
            dependencies: [.product(name: "SwiftTypst", package: "Swift-Typst")]
        )
    ]
)
