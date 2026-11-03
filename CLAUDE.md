# Ayah Lens working rules

Read NEXT-TASK.md, CHECKPOINT.md and SPEC.md before implementation. This is a hackathon prototype; the first milestone is real Arabic/translation output with simultaneous glasses microphone capture. Preserve the explicit manual-selection label until recognition is wired.

## Gotchas

- DAT registration is not device readiness. Creating AutoDeviceSelector inside the display-button handler and immediately creating a session races its asynchronous devicesStream updates. Retain the selector from startup, observe eligibility, and wait for a non-nil active device before session creation.
  Verify: `bash tools/test.sh` must pass delayed/nil/cancelled discovery checks; the actual glasses retest must then show readable Arabic before claiming the device bug is fixed.

- AVAudioEngine tap blocks created in MainActor code inherit actor isolation unless explicitly `@Sendable`. Apple invokes the block on an audio worker queue, causing `_dispatch_assert_queue_fail`. Keep the tap `@Sendable` and send only measured values to the UI actor. Verify: `python3 tools/test_audio_callback.py` executes the actual closure off the main queue and must deliver measured samples without trapping.

- Arabic opening words can be shorter than a proposed trailing fragment. Iterate valid prefix indices instead of constructing a closed range from independently clamped bounds. Verify: the unrelated trailing-word assertion in `testSharedVerseIsNotLostWhenWindowAlreadyIncludesNextOpeningWord` must return nil without trapping.

- Swift 6 rejects shared `[String: Any]` credential dictionaries without isolation and `await` inside assertion autoclosures. Isolate Keychain access on MainActor and await probe values before assertions. Verify: signed build and `python3 tools/probe_muse.py` must compile and pass.

- Exact short-opening recognition must retain word boundaries in aliases; concatenation accepts wrongly split fragments. Verify: `testEarlyOpeningRequiresCompleteWordsAndUniqueReference` rejects incomplete words and alternate splits while accepting complete unique openings.

- A constant CFBundleVersion of 1 hid install identity across prototype updates. The build helper now increments from the previous artifact and revision count, and the app displays it. Verify: the device-reported bundleVersion must equal the newly built Info.plist and the on-screen Build label.

- Version-check negative cases must pass AYAH_DEVICE_ID and inspect the specific mismatch error; a missing-device argument error is not stale-build proof. Verify the before/after app-info receipts and compare the final installed bundleVersion with the signed artifact.

- Al-Fatihah is an integration fixture, not the delivery scope. Verify the full-corpus milestone includes 114 surahs and 6,236 aligned ayah/translation rows plus global retrieval. Extra short-surah demos do not satisfy it. Spark remains unimplemented until its real adapter and approved validation are complete.

- The opening “الله لا إله إلا هو الحي القيوم” is shared by 2:255 and 3:2. Global retrieval must abstain without context; tests identifying 2:255 need its distinctive continuation. Verify the full-corpus shared-phrase test.

- Global retrieval must rank recent recitation evidence during passage changes; a long cumulative transcript can hide a new short surah. Verify testCumulativeRecitationCanSwitchFromFatihahToIkhlas and the same actual glasses sequence. The regression now covers all four Al-Ikhlas transitions; physical validation remains pending.

- Long-ayah listening cannot rely on character-only manual pages or verse-ID-only refreshes. Track the current source-word position, update within the same ayah, and keep live controls off the lens. Verify all reported 2:102 and 73:20 portion transitions with bash tools/probe_portions.sh, then check the actual lens.

- Do not compare a full-ayah phone card with a portion-only lens as a latency measurement, or await every SDK send in the recognition loop. Mirror the selected reading window, keep only the newest pending frame, and separate queue/SDK timing. Verify LatestLensSenderTests plus the actual phone/lens check.

- A commit command must stop when its staged diff check fails. Use fail-fast shell execution for the sequence. Verify: git diff --cached --check exits zero before git commit.

- Meta Ray-Ban Display has native Record display for DAT content. Check the current official Wearables FAQ before requiring an external lens camera. Verify: a short native capture includes actual app text while live recognition continues.

- Missing English alone does not prove the meaning switch was used: unpaired portions also omit English. Verify the actual toggle changes before calling footage a switch demonstration.

- Concat segments with changing color metadata can reset FFmpeg filter timestamps and shorten picture while audio stays full length. Normalize segment tags and preserve filter state. Verify picture duration and late-frame extraction, not container duration alone.

- Swift6 diagnostic tasks must return Sendable typed records, not arrays of dictionaries containing Any. Verify the harness compiles before loading credentials or starting a live replay.

- The prototype audio cap and native glasses Display Recording limit are separate. A cap change does not fix an earlier recognition hold. Verify the real-client synthetic budget probe, then a physical session beyond two minutes before claiming live validation.

- Body-style live text was barely readable in the actual glasses. Use heading style with compact source windows. Verify automatic long-ayah bounds, then obtain wearer confirmation of Arabic and English readability without clipping.

- Sandboxed macOS say can exit successfully with a zero-duration AIFF when voice-service access is blocked. Verify narration has positive duration and rerun with local speech access before rendering; never accept the empty file.
