public enum DisplayReadinessError: Error { case unavailable }

public enum DisplayReadiness {
    public static func firstAvailable<S: AsyncSequence>(in updates: S) async throws -> String where S.Element == String? {
        try Task.checkCancellation()
        for try await identifier in updates {
            try Task.checkCancellation()
            if let identifier { return identifier }
        }
        try Task.checkCancellation()
        throw DisplayReadinessError.unavailable
    }
}
