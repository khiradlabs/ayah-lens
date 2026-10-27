# Ayah Lens working rules

Read NEXT-TASK.md, CHECKPOINT.md and SPEC.md before implementation. This is a hackathon prototype; the first milestone is real Arabic/translation output with simultaneous glasses microphone capture. Preserve the explicit manual-selection label until recognition is wired.

## Gotchas

- DAT registration is not device readiness. Creating AutoDeviceSelector inside the display-button handler and immediately creating a session races its asynchronous devicesStream updates. Retain the selector from startup, observe eligibility, and wait for a non-nil active device before session creation.
  Verify: `bash tools/test.sh` must pass delayed/nil/cancelled discovery checks; the actual glasses retest must then show readable Arabic before claiming the device bug is fixed.
