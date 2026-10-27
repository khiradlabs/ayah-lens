# Ayah Lens hackathon prototype

## Goal and timing

Build a useful, verifiable glasses experience for following Quran recitation. Faraz confirmed on October 26 that organizers opened the building period. His kickoff slide states new work may be built October 26 through November 4. Submission remains November 4 at 8 PM Houston time.

## First milestone

A native SwiftUI iPhone application connects to Meta Ray-Ban Display, sends an attributed Arabic ayah and published English translation, and captures glasses microphone samples while the lens remains active. This resolves the combined-hardware uncertainty before recognition integration.

Native SwiftUI keeps this prototype directly on the already-proven iOS SDK path. The earlier Expo bridge is deferred; cross-platform delivery is not required for this milestone.

## Acceptance

- Development build signs and installs on the approved connected iPhone.
- Registration completes through Meta AI Developer Mode and its installed glasses component.
- A selected canonical Arabic ayah and its published translation appear in the actual lens.
- Audio input is verified as Bluetooth HFP; the phone microphone is never silently substituted.
- Combined mode configures audio before creating the display session. If display startup fails, audio stops and the error is visible.
- The phone shows actual microphone level and received sample count; selected verse controls are explicitly labelled manual.
- Stop releases microphone capture and the display session.
- Hardware results come from a wearer observation; compilation alone is insufficient.

## Next milestones, by scoring value

1. Compare Meta recognition candidates on cleared recordings and integrate the chosen listener.
2. Match transcript fragments to canonical verses; handle uncertain matches, pauses and repeats.
3. Demonstrate one short passage without manual verse selection.
4. Validate a narrow Spark contribution and small human-benefit test.
5. Produce and rehearse a three-minute video around verified functionality.

## Boundaries

This is a foreground hackathon prototype. All-day battery, thermal endurance, broad background support, production accounts and App Store release are deferred. Fine-tuning, revision feedback and additional models must earn time through rubric evidence.

No API keys are embedded in the app or repository. Cloud inference and recording upload require a cleared recording source and approved spending. Model-generated Quran text or translations are excluded.

## Initial evidence

Faraz confirmed stock lens tutorial output, clear wearer audio, and clear external-device recitation. External audio quality varies with head direction. Arabic rendering and simultaneous audio/display are still unverified at specification time.
