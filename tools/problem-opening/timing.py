"""One explicit 36-second proof timeline, without changing the full master."""
import json
from pathlib import Path
TIMELINE = json.loads(Path(__file__).with_name('timing.json').read_text())
FPS = TIMELINE['fps']
FRAMES = TIMELINE['frames']
SCENES = TIMELINE['scenes']
NARRATION = 'Imagine hearing the Quran every day, without understanding its meaning. For many Muslims who don’t understand Arabic, that is familiar. About two billion people are Muslim, roughly one quarter of humanity. Reading a translation pulls your eyes down to your phone. Now listen again, with the meaning in view.'
def scene_at(frame):
    for name,start,end in SCENES:
        if start <= frame < end: return name
    raise ValueError('frame outside the 36-second proof')
def source_frame(frame):
    scene = scene_at(frame)
    return frame if scene == 'listen' else frame-840 if scene == 'replay' else None
def audio_sources():
    return ['build/video-v0.2.1/audio/00.wav','build/video-v0.2.1/audio/02.wav']
def narration_windows(durations):
    windows=[(s,s+d/1.03) for s,d in zip(TIMELINE['narration_starts'],durations)]
    if any(a<8 or b>28 for a,b in windows): raise ValueError('narration outside its phase')
    if any(left[1]>right[0] for left,right in zip(windows,windows[1:])): raise ValueError('narration sentences overlap')
    return windows
