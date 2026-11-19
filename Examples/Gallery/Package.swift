// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "TypstGallery",
    platforms: [.macOS(.v14)],
    dependencies: [.package(name: "Swift-Typst", path: "../..")],
    targets: [
        .executableTarget(name: "Gallery", dependencies: [
            .product(name: "SwiftTypst", package: "Swift-Typst")
        ])
    ],
    swiftLanguageModes: [.v6]
)
