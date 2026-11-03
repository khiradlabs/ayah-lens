# Full demo v0.5 integration

Faraz approved the v0.5 opening and requested integration into the complete video within three minutes. Preserve every earlier export. This is local video assembly, not publication or new recording.

## Inputs and timeline

- Opening: build/video-v0.5-opening/Ayah-Lens-Opening-v0.5.mp4, 38 seconds. Accepted SHA256: 0ee67a247163bb5d01176c1bc6722ed28a9db7e338beee0d48912d7d869e9d2e.
- Existing master: build/video-v0.2.1/Ayah-Lens-Demo-v0.2.1.mp4, 179.900 seconds. SHA256: a23d319e234c5c71a40600cc37294572dea7666e14211b91b0c330a7572871e5.
- Replace the old first 36 seconds with the accepted 38-second opening.
- Reclaim two seconds from the original 36–48 product/stack illustration. Output that scene at 38–48, retaining its full narration and all Meta stack names. Prefer a consistent 12-to-10 second retime of this editorial illustration and temporary guide voice. It is not genuine live proof footage. Use pitch-preserving audio tempo. Do not truncate words or discard the Meta tooling explanation.
- Copy the original 48–179.9 tail at the same absolute output times. The reserved masjid block remains exactly 60–90, including its persistent replacement labels. All genuine recitation/proof footage after 48 seconds remains at its original speed. Replace only the burned-in editorial version badge in rectangle x1420, y30, width 460, height 48 from 38 seconds onward. This header is outside genuine device text. Mask exactly that rectangle in both frames for source comparisons; compare every other region.
- Target 179.900 seconds, 5,397 frames, 1920×1080 at 30fps, 48kHz stereo. Never exceed 180 seconds in either picture or audio.

## Deliverables

Build build/video-v0.5/Ayah-Lens-Demo-v0.5.mp4 plus current viewing notes, merged approximate captions, source/timeline manifest, and private technical/visual receipts. Add a maintained assembly helper with a read-only check mode and focused timing/source invariants. Update submission/VIDEO-REVIEW.md to identify the new full review cut. Preserve the original renderer and its older plan; use a separate assembly manifest rather than making its assumptions inconsistent.

The full cut still contains temporary local guide narration and a labelled reserved masjid fill. Do not relabel it as completed masjid proof. No new API calls, generated assets, app change, official Meta asset reuse, capture, publication, merge or submission.

## Acceptance

Verify input hashes before and after assembly. Verify exact frame and stream duration, resolution, full decode, non-clipping audio peaks and no drift/shortened picture at the joins. Normalize video parameters to avoid the known color-metadata/concat timestamp failure. Check source correspondence across the accepted opening, retimed product and unchanged tail. Verify opening audio and tail audio against input sources. Check product audio against the same reference tempo and confirm its final words survive. Re-time captions to the actual new intervals without crossing scene boundaries.

Privately inspect encoded samples around 37–39, 47–49, 59–61, 89–91 seconds and late frames. Confirm a coherent opening-to-product transition, all Meta stack names, readable disclaimers and persistent masjid labels. Independent specification review precedes independent quality review. No app tests for this video-only integration.
