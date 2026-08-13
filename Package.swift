// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "BellCat",
    platforms: [.macOS(.v13)],
    products: [.executable(name: "BellCat", targets: ["BellCat"])],
    targets: [.executableTarget(name: "BellCat", path: "Sources/BellCat")]
)
