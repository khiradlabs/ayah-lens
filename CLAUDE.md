# Ayah Lens working rules

Read NEXT-TASK.md, CHECKPOINT.md and SPEC.md before implementation. This is a hackathon prototype; the first milestone is real Arabic/translation output with simultaneous glasses microphone capture. Preserve the explicit manual-selection label until recognition is wired.

## Gotchas

- DAT registration is not device readiness. Creating AutoDeviceSelector inside the display-button handler and immediately creating a session races its asynchronous devicesStream updates. Retain the selector from startup, observe eligibility, and wait for a non-nil active device before session creation.
  Verify: `bash tools/test.sh` must pass delayed/nil/cancelled discovery checks; the actual glasses retest must then show readable Arabic before claiming the device bug is fixed.

- AVAudioEngine tap blocks created in MainActor code inherit actor isolation unless explicitly `@Sendable`. Apple invokes the block on an audio worker queue, causing `_dispatch_assert_queue_fail`. Keep the tap `@Sendable` and send only measured values to the UI actor. Verify: `python3 tools/test_audio_callback.py` executes the actual closure off the main queue and must deliver measured samples without trapping.

- Arabic opening words can be shorter than a proposed trailing fragment. Iterate valid prefix indices instead of constructing a closed range from independently clamped bounds. Verify: the unrelated trailing-word assertion in `testSharedVerseIsNotLostWhenWindowAlreadyIncludesNextOpeningWord` must return nil without trapping.
