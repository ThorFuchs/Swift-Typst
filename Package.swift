// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "Swift-Typst",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [.library(name: "SwiftTypst", targets: ["SwiftTypst"])],
    targets: [
        .binaryTarget(name: "CTypstBridge", path: "Artifacts/CTypstBridge.artifactbundle"),
        .target(name: "SwiftTypst", dependencies: ["CTypstBridge"]),
        .testTarget(name: "SwiftTypstTests", dependencies: ["SwiftTypst"]),
    ],
    swiftLanguageModes: [.v6]
)
