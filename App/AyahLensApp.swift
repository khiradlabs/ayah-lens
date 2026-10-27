import SwiftUI

@main
struct AyahLensApp: App {
    @State private var model = GlassesModel()

    var body: some Scene {
        WindowGroup {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 22) {
                        Text("Follow the words.\nFind the meaning.")
                            .font(.largeTitle.bold())
                        Text("Hardware prototype · Manual verse selection")
                            .font(.subheadline).foregroundStyle(.secondary)
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
                                .disabled(!model.registered || model.busy)
                            Button("Start microphone + lens") { model.startCombined() }
                                .disabled(!model.registered || model.busy || model.listening)
                            Button("Next verse · manual") { model.nextVerse() }.disabled(model.busy)
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
                        Text("Live verse recognition is not connected in this build.")
                            .font(.footnote).foregroundStyle(.secondary)
                    }.padding(24)
                }.navigationTitle("Ayah Lens")
            }.tint(.teal)
                .onOpenURL { model.handleURL($0) }
        }
    }
}
