import Foundation
import SwiftTypst
import UIKit

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        configurationForConnecting session: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        let config = UISceneConfiguration(name: nil, sessionRole: session.role)
        config.delegateClass = SceneDelegate.self
        return config
    }
}

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let scene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: scene)
        let controller = UIViewController()
        controller.view.backgroundColor = .systemBackground
        let label = UILabel()
        label.accessibilityIdentifier = "artifact-consumer-result"
        label.numberOfLines = 0
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        controller.view.addSubview(label)
        NSLayoutConstraint.activate([
            label.leadingAnchor.constraint(equalTo: controller.view.safeAreaLayoutGuide.leadingAnchor, constant: 24),
            label.trailingAnchor.constraint(equalTo: controller.view.safeAreaLayoutGuide.trailingAnchor, constant: -24),
            label.centerYAnchor.constraint(equalTo: controller.view.centerYAnchor),
        ])
        label.text = "Compiling…"
        window.rootViewController = controller
        self.window = window
        window.makeKeyAndVisible()
        Task {
            let message = await Task.detached {
                do {
                    let compiler = TypstCompiler()
                    let pdf = try compiler.compilePDF("= iOS SwiftPM Consumer").pdf
                    guard pdf.starts(with: Data("%PDF-".utf8)) else { return "INVALID PDF" }
                    do {
                        _ = try compiler.compilePDF("#let x = (")
                        return "INVALID SOURCE ACCEPTED"
                    } catch let error as TypstError {
                        return "SWIFTPM SUCCESS\nPDF: \(pdf.count) bytes\n\(error.description)"
                    }
                } catch {
                    return "SWIFTPM FAILURE: \(error)"
                }
            }.value
            label.text = message
            print(message)
        }
    }
}
