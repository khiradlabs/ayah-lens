"""One explicit opening timeline, preserving genuine recitation source offsets."""
import json,re
from pathlib import Path
TIMELINE = json.loads(Path(__file__).with_name('timing.json').read_text())
FPS = TIMELINE['fps']
FRAMES = TIMELINE['frames']
SCENES = TIMELINE['scenes']
REPLAY_FRAME = next(start for name,start,end in SCENES if name=='replay')
REPLAY_START = REPLAY_FRAME/FPS
DURATION = FRAMES/FPS
NARRATION = 'For many who don’t understand Arabic, the sound is familiar. Two billion Muslims, roughly a quarter of humanity. What if your glasses became your personal Quran translator? The meaning, right in front of your eyes. The text follows the recitation automatically. No scrolling. No tapping. Just listen. And understand.'
def narration_sentences(): return re.split(r'(?<=[.?])\s+',NARRATION)
def scene_at(frame):
    for name,start,end in SCENES:
        if start <= frame < end: return name
    raise ValueError('frame outside the opening proof')
def source_frame(frame):
    scene = scene_at(frame)
    return frame if scene == 'listen' else frame-REPLAY_FRAME if scene == 'replay' else None
def audio_sources():
    return ['build/video-v0.2.1/audio/00.wav','build/video-v0.2.1/audio/02.wav']
def narration_windows(durations):
    starts=TIMELINE['narration_starts']
    if len(durations)!=len(starts) or len(starts)!=len(narration_sentences()):
        raise ValueError('narration sentence/start/duration count mismatch')
    windows=[(s,s+d/TIMELINE['tempo']) for s,d in zip(starts,durations)]
    if any(a<8 or b>REPLAY_START for a,b in windows): raise ValueError('narration outside its phase')
    if any(left[1]>right[0] for left,right in zip(windows,windows[1:])): raise ValueError('narration sentences overlap')
    return windows
