// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "AyahLensCore",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [.library(name: "AyahLensCore", targets: ["AyahLensCore"])],
    targets: [
        .target(name: "AyahLensCore"),
        .testTarget(name: "AyahLensCoreTests", dependencies: ["AyahLensCore"])
    ]
)
