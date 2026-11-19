// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "Consumer",
    platforms: [.macOS(.v14), .iOS(.v17)],
    dependencies: [.package(name: "Swift-Typst", path: "../..")],
    targets: [.executableTarget(name: "Consumer", dependencies: [
        .product(name: "SwiftTypst", package: "Swift-Typst")
    ])],
    swiftLanguageModes: [.v6]
)
