# Opening order0.2.1 — Implementation Plan
Goal: Put the first three approved sections in orderlisten→impact→meaningreveal.
Architecture: Maintain semantic scene identities while placing existing content on revised timeline. Preserve later timings and render a separate review artifact.
Tech stack: ExistingPython/Pillow/FFmpeg/localguidevoice.
Execution: use execute-plan; one fresh implementation task, followed by spec/quality/visual checks. User authorized the order correction.

## Task1 — reorder existing opening and render
Files / Touches: tools/render_demo_video.py,tools/editorial_motion.py,video-order behaviorcheck helperifneeded,submission/video-edit.json,submission/demo-timeline.json,submission/DEMO-SCRIPT.md,submission/VIDEO-REVIEW.md,submission/README.md. Generatedoutputbuild/video-v0.2.1/only. Noapp/Core/oldmasterchanges.
Steps: Observe a meaningful failingcheckforreorderedsceneidentity/footage/audio; implementtheminimumsemanticmappingneeded;putold0,2,1scenesat0–8,8–28,28–36; keepallremainingboundaries. Updateversionbadge0.2.1andoutputpaths. Preservegenuinenativereplayaudio/video andpopulationguidevoice. Updatehelpersemanticchecks/previewtimessotheytestcontentnotassumedposition. Regeneratescript,approxSRT,notes,storyboardand179–180s1080p30fpsmaster. Runvideo/order/semanticcheck;decodeandinspectopening/boundaries,59coretestcardandmasjidslotunchanged. Originalv0.2hashmustremainunchanged. GraphicschangesuseactualrenderQA;semanticselectionlogicusesbehavioralRED/GREEN. Commitownedsource/docs.
Donewhen: revisedfullmasterandsourceJSONagreeonorder; correctsourcevideoandaudioinmeaningreveal; laterboundariesunchanged;videocheckpasses;independentspec/qualityandopeningvisualreviewpass. Noapp testsforvideoonlychanges. NoMetawebsiteanimationreusedwhilelicensingunconfirmed. Localrenderbudget20minutes.

## Completion

DONE: opening and fullmaster rendered. Five regressionchecks,semanticcheck,video checker,full decode and independent spec/quality/sampledvisualreviewpassed. Exact8/28/36 and laterboundaries/nativeaudio/caption/sourcehashes were verified. User review remains.
