# Ayah Lens Version 3 review video

The review cut uses actual native glasses and phone-preview footage with designed graphics and a temporary local guide narrator. It is a review artifact, not a submitted final video.

## Reserved masjid recording

One30-second replacement slot remains at 1:00–1:30. Its current six-second placeholder and 24-second phone reference are labelled throughout. Replace this block with the selected masjid recording. The reference fill is not presented as completed 30-second masjid proof.

## Available footage and graphics

The opening repeats the same recorded audio and then reveals readable native display content. The enlarged display comes from the same frames. The long-verse explanation uses the reviewed 73:20 phone recording. Hifz uses an explanatory modes graphic because the supplied short phone clip does not show the English toggle changing.

The models section distinguishes live Muse Voice, cached Spark phrase plans, local tracking and source preservation. The final engineering card labels teaching as future work requiring development and extensive testing.

## Local review artifacts

The video is generated under build/video-review/Ayah-Lens-Version-3-Review.mp4. Guide captions and viewing notes are beside it. Source recordings, temporary speech tracks, QA images and the master remain ignored by Git.

Run python3 tools/render_demo_video.py to reproduce the review cut. It uses Pillow, FFmpeg and the local macOS Daniel voice. No paid generation service is required. The maintained edit plan is video-edit.json.

Run python3 tools/check_submission.py --video /absolute/path/to/review.mp4 to check duration and picture/audio coverage. Visual review must confirm exact slot boundaries, readable source text, source labels and absence of unrelated personal UI.
