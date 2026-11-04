# Ayah Lens live demo deck, SPEC (2026-11-04 14:10)

Goal: a browser slide deck Faraz drives with the keyboard while screen-recording and narrating live. Every animation is built in; footage plays inside slides; the long-verse ribbon steps itself from the video clock. Target run time 2.5 to 3 minutes when narrated at his pace.

Constraints: single `deck/index.html` plus `deck/deck.css`, `deck/deck.js`, media under `deck/media/`, font `deck/fonts/UthmanicHafs1Ver18.ttf`; no CDN, no build step, works offline in Chrome and Safari from `file://`; 16:9, designed at 1920x1080, scales to any window (CSS transform); palette paper #ECE7D3, ink #1E1E1E, blue #465D79, red #B94B37; all text 40 px or larger at 1080p; honesty labels exactly as written here. A second page `deck/notes.html` shows the speaker notes for the current slide and step, synced over BroadcastChannel, for a second window or the phone (served from the same folder).

Keys: Right / Space = next build step (advances within a slide, then to the next slide); Left = previous step; Home/End; F = fullscreen; M = mute/unmute clip audio; R = restart the current clip; N = open notes window; keys 1-7 jump to a slide. A thin progress bar at the bottom, 4 px, blue.

Transitions: slide change = 350 ms crossfade on paper; build steps = 300 ms fade-and-rise (12 px); the pipeline nodes light in sequence; numbers count up over 800 ms; the ribbon lit span moves with a 200 ms ease. No bouncing, no spinning.

Media files (already cut, 1080p H.264 + AAC): glasses-open.mp4 (9.9 s: 2:281 portions, 2:282 arrives at ~9.5 s), glasses-2-282.mp4 (15.3 s: verse 2:282, portion counter 4-5/36 to 10-11/36), glasses-arrival.mp4 (4.7 s: 2:282 arrives at ~4.0 s), glasses-112.mp4 (15.5 s: 112:1→112:4, clean wall), phone-stream-faraz.mp4 (24 s, portrait, Faraz with the stream), phone-73-20.mp4 (24 s, portrait phone screen, 73:20 portions), phone-lookup.mp4 (19 s, portrait, scrolling the app). Data: verse-2-282.json (128 words, KFGQPC Hafs), ribbon-2-282.json (observed lit spans per counter state with clip-relative times; if absent, use these clip-relative step times and word spans: 0.0→10-14, 0.53→13-18, 2.70→15-22, 5.53→19-24, 10.63→23-27, 11.00→25-30, 13.33→28-34; 1-based inclusive word indices).

Slides and build steps (each bullet is one key press):

1. What I see. Full-bleed glasses-open.mp4, autoplay with audio, label top-right "What I see through the glasses" (48 px, ink on paper plate).
   - Caption bottom-left: "The verse appears with its meaning. When the reciter moves on, the lens follows."
   - Caption: "Nothing is tapped to follow."
   Notes: I'm listening to a reciter streaming on my laptop, wearing Meta's display glasses. This is what I see…

2. Why. Paper. Big number counts up "2,000,000,000" then settles to "About 2 billion Muslims", small line "Pew Research Center, 2020 estimate, published 2025" (40 px).
   - Line: "Many of us hear the Quran daily and cannot follow the Arabic."
   - Line: "Looking a verse up pulls you out of the moment." beside phone-lookup.mp4 (portrait, pillar-boxed on paper, muted).
   - Line, red: "The meaning should come to you."

3. Ayah Lens. Title "Ayah Lens" 160 px, then a five-node pipeline across the slide, nodes appear one per key: "Meta Ray-Ban Display glasses · listens" → "Muse Voice · live Arabic transcript" → "Our software · finds the verse and your place in it" → "Muse Spark · prepares the English match" with a tag "prepared in advance" → "Lens · the meaning follows the recitation". Under the Muse Voice node a 40 px line "audio goes to Muse Voice". On the right, phone-73-20.mp4 plays muted, labelled "Phone screen recording".
   - last step: a line "And that is the easy part."

4. The hard case. glasses-2-282.mp4 autoplay with audio in an 820 px wide window, pin "2:282" ringed red top-left (56 px), label "Glasses display recording". Under it the ribbon: all 128 words of 2:282 in UthmanicHafs, right-to-left, 42 px, dim ink at 55% on paper; the lit span (blue plate, paper text) follows the video's currentTime through the step table; a 48 px tag "Illustration, not in the app" above the ribbon; a counter "Portion k of 36 on the lens" that updates with the steps.
   - Caption: "Same verse number, the whole way."
   - Caption: "The words on the lens keep moving: Ayah Lens follows your place inside the verse."
   - Caption: "The longest verse in the Quran, 128 words."

5. Hifz (only if deck/media/toggle.mp4 exists at load; otherwise the slide is skipped and numbering stays). toggle.mp4 full-bleed with audio, label "Glasses display recording".
   - Caption: "English off. The Arabic keeps following."
   - Caption: "English back whenever you want it."

6. What is real. Three numbers count up on paper: "114 surahs", "6,236 ayahs bundled", "59 tests passed, Nov 2".
   - Line: "Transcription and tracking run live."
   - Line: "Only Spark's English pairing is prepared in advance."
   - Line: "The software was written in ten days, Oct 26 to Nov 4."

7. Close. glasses-arrival.mp4 autoplay with audio, label "Glasses display recording"; on the last step a paper card over the lower third: "Ayah Lens · github.com/khiradlabs/ayah-lens".
   - Card appears.

Behaviour: a clip starts when its slide is entered and pauses when left; R restarts it; the ribbon recomputes on every timeupdate and on seek; when a clip ends it holds its last frame. Notes page: shows slide number, title, the step count, and the notes paragraph (the script lines from submission/DEMO-SCRIPT-V1.0.md draft 5, adapted to first person); large type, dark background.

Acceptance: opens from file:// in Chrome with no console errors; every key above works; all seven (or six) slides render at 1920x1080 and at a 1280x720 window without clipped text; the ribbon's lit words match the Arabic on the lens at each step (a QA subagent compares frames); no text under 40 px; a `deck/CHECK.md` listing what was verified and how.
