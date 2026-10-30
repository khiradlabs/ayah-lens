import Foundation
import Security

@MainActor
enum MuseCredential {
    private static let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "ai.khirad.ayahlens.muse",
        kSecAttrAccount as String: "model-api-key"
    ]

    /// Import a private development handoff once, then remove its plaintext copy.
    static func read() throws -> String? {
        let staging = FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("muse-key.once")
        if FileManager.default.fileExists(atPath: staging.path) {
            let key = try String(contentsOf: staging, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
            guard !key.isEmpty, key.count <= 4096 else { throw MuseError.rejected }
            var attributes = query
            attributes[kSecValueData as String] = Data(key.utf8)
            attributes[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
            let added = SecItemAdd(attributes as CFDictionary, nil)
            if added == errSecDuplicateItem {
                guard SecItemUpdate(query as CFDictionary, [kSecValueData as String: Data(key.utf8)] as CFDictionary) == errSecSuccess else {
                    throw MuseError.rejected
                }
            } else if added != errSecSuccess { throw MuseError.rejected }
            try FileManager.default.removeItem(at: staging)
        }
        var lookup = query
        lookup[kSecReturnData as String] = true
        lookup[kSecMatchLimit as String] = kSecMatchLimitOne
        var result: CFTypeRef?
        let status = SecItemCopyMatching(lookup as CFDictionary, &result)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess, let data = result as? Data else { throw MuseError.rejected }
        return String(data: data, encoding: .utf8)
    }
}
