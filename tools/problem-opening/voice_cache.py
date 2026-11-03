"""Cache local guide speech by the actual sentence and speech settings."""
import json

def ensure_voice(audio, sentence, voice, rate, generate, measure):
    marker=audio.with_suffix('.json')
    identity={'sentence':sentence,'voice':voice,'rate':rate}
    if audio.exists() and marker.exists() and json.loads(marker.read_text())==identity and measure(audio)>0:
        return False
    generate(audio,sentence,voice,rate)
    assert measure(audio)>0,'local speech service returned empty audio; rerun with local speech access'
    marker.write_text(json.dumps(identity,indent=2)+'\n')
    return True
