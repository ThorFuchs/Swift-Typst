// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "Swift-Typst",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [.library(name: "SwiftTypst", targets: ["SwiftTypst"])],
    targets: [
        .binaryTarget(name: "CTypstBridge", url: "https://github.com/ThorFuchs/Swift-Typst/releases/download/bridge-v1.0.0/CTypstBridge.zip", checksum: "c27788475defb885943d978406ab787a87339314251b9a3305e5499207c1cf76"),
        .target(name: "SwiftTypst", dependencies: ["CTypstBridge"]),
        .testTarget(name: "SwiftTypstTests", dependencies: ["SwiftTypst"]),
    ],
    swiftLanguageModes: [.v6]
)
