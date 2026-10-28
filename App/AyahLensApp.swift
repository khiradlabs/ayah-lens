import SwiftUI

@main
struct AyahLensApp: App {
    @State private var model = GlassesModel()

    private var buildLabel: String {
        let version = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "unknown"
        let build = Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? "unknown"
        return "Version \(version) · Build \(build)"
    }

    var body: some Scene {
        WindowGroup {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 22) {
                        Text("Follow the words.\nFind the meaning.")
                            .font(.largeTitle.bold())
                        Text(model.recognitionActive ? "\(model.recognitionSource) · Al-Fatihah" : "Hardware prototype · Manual verse selection")
                            .font(.subheadline).foregroundStyle(.secondary)
                        Text(buildLabel).font(.caption).foregroundStyle(.secondary)
                            .accessibilityIdentifier("build_version")
                        if let verse = model.verse {
                            VStack(alignment: .leading, spacing: 14) {
                                Text("Al-Fatihah · \(verse.id)").font(.caption.bold()).foregroundStyle(.teal)
                                Text(verse.arabic).font(.system(size: 30)).frame(maxWidth: .infinity, alignment: .trailing)
                                Text(verse.translation).font(.title3)
                                Text("Arabic: Tanzil · Translation: Pickthall").font(.caption).foregroundStyle(.secondary)
                                Link("Tanzil source and text updates", destination: URL(string: "https://tanzil.net/")!).font(.caption)
                            }.padding().background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20))
                        }
                        Text(model.status).accessibilityIdentifier("session_status")
                        if let error = model.error { Text(error).foregroundStyle(.red).accessibilityIdentifier("session_error") }
                        VStack(spacing: 12) {
                            Button(model.registered ? "Glasses registered" : "Register glasses") { model.register() }
                                .disabled(model.registered || model.busy)
                            Button("Show selected verse on lens") { model.showSelectedVerse() }
                                .disabled(!model.registered || !model.hasDisplayDevice || model.busy || model.recognitionActive)
                            Button("Start Muse live Al-Fatihah") { model.startMuse() }
                                .disabled(!model.museConfigured || !model.registered || !model.hasDisplayDevice || model.busy || model.listening)
                            if !model.museConfigured { Text("Muse API access has not been provisioned on this phone.").font(.caption) }
                            Button("Start local fallback") { model.startRecognition() }
                                .disabled(!model.registered || !model.hasDisplayDevice || model.busy || model.listening)
                            Button("Start microphone + lens") { model.startCombined() }
                                .disabled(!model.registered || !model.hasDisplayDevice || model.busy || model.listening)
                            Button("Next verse · manual") { model.nextVerse() }.disabled(model.busy || model.recognitionActive)
                            Button("Stop", role: .destructive) { model.stop() }
                        }.buttonStyle(.borderedProminent).frame(maxWidth: .infinity)
                        if model.listening {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Glasses microphone active").font(.headline)
                                ProgressView(value: min(1, max(0, (model.decibels + 80) / 80)))
                                Text("\(model.decibels, specifier: "%.1f") dBFS · \(model.sampleCount) samples · \(model.sampleRate, specifier: "%.0f") Hz")
                                    .font(.caption.monospacedDigit())
                            }.accessibilityIdentifier("microphone_status")
                        }
                        if model.recognitionActive {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(model.recognitionStatus).font(.headline)
                                if !model.transcript.isEmpty { Text(model.transcript).font(.body) }
                                if !model.museActive {
                                    Text("Inference: \(model.inferenceMilliseconds, specifier: "%.0f") ms · 5 s window · 1 s update interval")
                                        .font(.caption.monospacedDigit())
                                }
                            }
                        }
                        Text("Muse mode sends glasses audio to Meta for live transcription. Local fallback keeps audio on this iPhone. Both select published text; uncertain matches hold the current verse.")
                            .font(.footnote).foregroundStyle(.secondary)
                        if let gap = model.museGapMilliseconds {
                            DisclosureGroup("Muse timing") {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text(buildLabel).foregroundStyle(.secondary)
                                        .accessibilityIdentifier("timing_build_version")
                                    Text("Audio processing gap: \(gap, specifier: "%.0f") ms")
                                    if let peak = model.museLatency.peakAudioGapMilliseconds { Text("Peak audio gap: \(peak, specifier: "%.0f") ms") }
                                    if let first = model.museLatency.firstTranscriptMilliseconds { Text("First text after audio start: \(first / 1000, specifier: "%.2f") s") }
                                    if let wait = model.museLatency.firstMatchAfterTranscriptMilliseconds { Text("First match after text: \(wait / 1000, specifier: "%.2f") s") }
                                    if let match = model.matcherMilliseconds { Text("Verse matching: \(match, specifier: "%.0f") ms") }
                                    if let send = model.lensSendMilliseconds { Text("Lens send completion: \(send, specifier: "%.0f") ms") }
                                    Text("Audio gap is provider progress, not word timing. Lens timing measures the SDK send completing.")
                                        .font(.caption).foregroundStyle(.secondary)
                                    Text("First-text time includes any silence before recitation starts.")
                                        .font(.caption).foregroundStyle(.secondary)
                                }.font(.caption.monospacedDigit()).padding(.top, 8)
                            }
                        }
                    }.padding(24)
                }.navigationTitle("Ayah Lens")
            }.tint(.teal)
                .onOpenURL { model.handleURL($0) }
        }
    }
}
