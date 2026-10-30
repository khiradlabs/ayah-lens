# Ayah Lens submission draft review

Draft 1 is ready for script and form-copy review. The final video and form submission remain incomplete.

## Evidence and clarity review

| Check | Result | Next action |
|---|---|---|
| Rubric weights | 30, 25, 20 and 25 total 100, from the supplied participant guide. | Recheck authenticated guide before final submission if access is available. |
| Current form fields | Matched to the three October 29 screenshots. | Copy the accepted values and entrant’s own ratings into the final form. |
| Theme and track | Indie Developer and Build for Your World match the recorded application. | Confirm the entrant profile during submission. |
| Opening | The first eight seconds require the working product. | Capture a genuine readable take. |
| Live proof | The timeline reserves a 35-second continuous section. | Keep at least 25 seconds uncut with real recitation. |
| Meta role | Voice supplies partials; Spark supplies candidate decisions and paired source ranges. | Label the filmed long-ayah plans Cached. |
| Impact | Population and recurring-prayer claims have sources. | Avoid treating the whole population as current product demand. |
| Technical claims | Scope matches the frozen prototype and existing verification. | No accuracy percentage, acoustic timestamps or visible-pixel latency claim. |
| Original event work | Script and form distinguish implementation from existing inputs. | Show the event Git history and attribution. |
| Phone versus glasses | Capture labels distinguish preview from actual lens output. | Do not present a recreated overlay as device footage. |
| Subjective ratings | Left for Faraz. | Select both honestly before submitting. |
| Public repository | Public, but main currently contains only initial documentation. | Review and merge the prepared implementation before submission. |
| Final video | Not assembled. | Capture, edit, export and check the accessible link. |

This is an author review, not an independent cold-viewer test. Once the cut exists, show it to someone unfamiliar with the project. Ask what it does and what the glasses add. Resolve confusion before final export.

## Local checks

Run python3 tools/check_submission.py to verify timeline continuity, script consistency, form-field coverage and local references.

After exporting, run python3 tools/check_submission.py --video /absolute/path/to/final.mp4. It checks duration and audio/video streams with ffprobe. It cannot establish that footage is genuine or links are accessible.

The final manual pass checks readable text, truthful labels, recitation continuity, no private data in frames, accessible links and correct entrant details.
