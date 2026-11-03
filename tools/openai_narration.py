#!/usr/bin/env python3
"""Bounded OpenAI narration generation and v0.6 assembly; credentials never leave memory."""
import argparse,array,base64,hashlib,importlib.util,io,json,math,os,re,subprocess,time,urllib.request,urllib.error,wave
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'build/video-v0.6';STEMS=WORK/'narration'
BASE=ROOT/'build/video-v0.5/Ayah-Lens-Demo-v0.5.mp4'
BASE_HASH='eda86f8188c7e8d472d700964eabf3ec65e50813e9639fc3936875f25764cfc8'
OUT=WORK/'Ayah-Lens-Demo-v0.6.mp4';PROTECTED=[(0,8),(30,38),(60,90)]
PLAN=json.loads((ROOT/'submission/narration-v0.6.json').read_text())
MODEL=PLAN['model'];VOICE=PLAN['voice'];DURATION=PLAN['duration_seconds']
COMMON=('Professional documentary narration, warm and human, never theatrical or salesy. '
        'Speak exactly the supplied words, no introductions or added sounds. '
        'Pronounce Ayah Lens as eye-ah lens, Quran as kuh-raan, Hifz as hifz, Salat as suh-laat, Muse as myooz. '
        'No music or sound effects. Clear English, consistent natural voice. ')
EXPRESSIVE=('Perform as a founder excitedly sharing a meaningful breakthrough with a friend, not a neutral documentary announcer. '
            'Audibly warm and emotionally engaged, gently smiling. Use noticeable, natural variation in pitch, pace and energy across phrases. '
            'Keep the performance grounded and sincere, with no shouting or sadness. Speak exactly the supplied words, no added commentary. '
            'Pronounce Ayah Lens as eye-ah lens, Quran as kuh-raan, Hifz as hifz, Salat as suh-laat, Muse as myooz. '
            'No music, effects or added nonverbal sounds. ')
def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,**kw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def duration(p):return float(probe(p)['format']['duration'])
def request_body(text,instructions,speed=1,voice=None):return {'model':MODEL,'voice':voice or VOICE,'input':text,'instructions':instructions,'response_format':'wav','speed':speed}
def identity(text,instructions,speed=1,voice=None):return hashlib.sha256(json.dumps(request_body(text,instructions,speed,voice),sort_keys=True).encode()).hexdigest()
def safe_error(text,key):return text.replace(key,'[REDACTED]')[:1000]
def normalize_wav(blob):
    with wave.open(io.BytesIO(blob),'rb') as w:
        channels=w.getnchannels();rate=w.getframerate();width=w.getsampwidth();frames=w.readframes(w.getnframes())
    seconds=len(frames)/(channels*rate*width)
    if not seconds or seconds>120:raise ValueError('OpenAI returned empty or unexpectedly long audio')
    clean=io.BytesIO()
    with wave.open(clean,'wb') as w:
        w.setnchannels(channels);w.setsampwidth(width);w.setframerate(rate);w.writeframes(frames)
    return clean.getvalue(),seconds,channels,rate
def key():
    value=os.environ.get('OPENAI_API_KEY')
    if value:return value
    p=Path.home()/'.secrets/ayah-lens-openai.env'
    for line in p.read_text().splitlines():
        if line.startswith('OPENAI_API_KEY='):
            value=line.split('=',1)[1].strip().strip('\"\'')
            if value:return value
    raise ValueError('OpenAI credential is empty in the private file')
def beats():
    spec=importlib.util.spec_from_file_location('opening',ROOT/'tools/problem-opening/timing.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    texts=m.narration_sentences();starts=m.TIMELINE['narration_starts']
    tones=['Thoughtful and empathetic, not sad.','Calm sense of scale and importance.','Curious inviting question, a gentle lift on What if, emphasize personal Quran translator.','Warm discovery, emphasize right in front of your eyes.','Clear confident explanation, emphasize follows and automatically.','Crisp restrained emphasis, no scrolling.','Crisp restrained emphasis, no tapping.','Warm quiet invitation, sincere.','Warm sincere resolution, understand.']
    result=[]
    for i,(text,start,tone) in enumerate(zip(texts,starts,tones)):
        end=(starts[i+1]-.065 if i+1<len(starts) else 29.7)
        result.append({'id':f'opening-{i:02}','start':start,'end':end,'text':text,'tone':tone})
    plan=json.loads((ROOT/'submission/video-edit.json').read_text())
    for i,st,en,tone in [(3,38,48,'Confident introduction with a hint of excitement, not shouting.'),(4,48,60,'Warm, respectful and practical.'),(6,90,112,'Interested discovery; gently emphasize the technical challenge and hands-free following.'),(7,112,138,'Precise, confident and intelligible technical explanation.'),(8,138,152,'Warm and supportive, describing memorization practice.'),(9,152,168,'Proud but grounded; distinguish working foundations from future teaching.'),(10,168,179.9,'Reflective, warm and sincere closing; settle gently on meaning.')]:
        result.append({'id':f'scene-{i:02}','start':st+.15,'end':en-.2,'text':plan['segments'][i]['narration'],'tone':tone})
    return result
def fit_tempo(seconds,available):
    if seconds<=0 or available<=0:raise ValueError('Audio duration must be positive')
    tempo=max(1,seconds/available)
    if tempo>PLAN['max_fitting_tempo']:raise ValueError(f'Regenerate with clearer pacing: required tempo {tempo:.3f}')
    return tempo
def validate_windows(clips):
    prev=-1
    for c in sorted(clips,key=lambda c:c['start']):
        a=c['start'];b=a+c['duration']
        if a<0 or b>DURATION or any(a<y and b>x for x,y in PROTECTED):raise ValueError('Narration touches protected recitation')
        if a<prev-1e-6:raise ValueError('Narration overlap')
        prev=b
def planning_cost():
    ledger=WORK/'costs.jsonl';own=sum(json.loads(x).get('estimated_cost_usd',0) for x in ledger.read_text().splitlines()) if ledger.exists() else 0
    review=sum(json.loads(p.read_text()).get('estimated_cost_usd',0) for p in (WORK/'qa').glob('*audio*review.json'))
    return own+review
def generate(text,instructions,out,note,speed=1,voice=None):
    voice=voice or VOICE;out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);receipt=out.with_suffix('.json');fingerprint=identity(text,instructions,speed,voice)
    if out.exists() and receipt.exists():
        old=json.loads(receipt.read_text())
        if old.get('identity')==fingerprint and old.get('sha256')==sha(out) and duration(out)>0:return old
        raise ValueError('Existing generation differs; use a versioned output instead of silently spending again')
    ledger=WORK/'costs.jsonl'
    spent=planning_cost()
    # Reserve a conservative maximum of two minutes per call before requesting audio.
    if spent+.08>1:raise ValueError('Narration planning budget would exceed USD1')
    body=request_body(text,instructions,speed,voice);secret=key();req=urllib.request.Request('https://api.openai.com/v1/audio/speech',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+secret,'Content-Type':'application/json'})
    started=time.monotonic()
    try:
        with urllib.request.urlopen(req,timeout=120) as response:blob=response.read();request_id=response.headers.get('x-request-id')
    except urllib.error.HTTPError as e:
        try:message=json.loads(e.read(8192)).get('error',{}).get('message','Request rejected')
        except Exception:message='Request rejected; body suppressed'
        raise RuntimeError(f'OpenAI HTTP {e.code}: '+safe_error(message,secret)) from None
    except urllib.error.URLError:raise RuntimeError('OpenAI network failure; no automatic retry') from None
    raw_hash=hashlib.sha256(blob).hexdigest();blob,seconds,channels,rate=normalize_wav(blob)
    out.write_bytes(blob)
    estimated=seconds*50*12/1_000_000+math.ceil(len(text)/3)*.6/1_000_000
    data={'provider':'OpenAI','model':MODEL,'voice':voice,'identity':fingerprint,'text':text,'instructions':instructions,'speed':speed,'duration':seconds,'sample_rate':rate,'channels':channels,'sha256':sha(out),'raw_response_sha256':raw_hash,'wav_header_normalized':True,'request_id':request_id,'elapsed_seconds':round(time.monotonic()-started,3),'estimated_cost_usd':round(estimated,6),'cost_method':'Planning estimate: 50 audio tokens/second at $12/M plus ceil(characters/3) text tokens at $0.60/M. Tokens are not reported by the binary response; not invoice actuals.','note':note,'created_at':datetime.now(timezone.utc).isoformat()}
    receipt.write_text(json.dumps(data,indent=2)+'\n');WORK.mkdir(exist_ok=True)
    with ledger.open('a') as log:log.write(json.dumps(data)+'\n')
    return data
def sample(note,expressive=False):
    # Only the seven opening hook beats, not subsequent full-video scenes.
    text=' '.join(b['text'] for b in beats()[2:9])
    instructions=COMMON+'Begin with warm curiosity. Deliver benefits confidently with crisp No scrolling and No tapping. Close warmly, with a short pause between Just listen and And understand.'
    filename='OpenAI-Cedar-hook-sample.wav'
    if expressive:
        instructions=EXPRESSIVE+("On What if, give an audible warm smile and curious rising intonation, a personal invitation. Emphasize your glasses and personal Quran translator. "
          "Then express genuine discovery and delight on the meaning right in front of your eyes. Make the following benefit reassuring and confident, with a rhythmic lift. "
          "Give No scrolling and No tapping crisp separate emphasis, as satisfying benefits. Soften and slow Just listen; finish And understand with warm relief and heartfelt resolution. "
          "Avoid a flat bullet-list cadence. The emotional arc must be audible: curiosity, discovery, confident benefits, gentle resolution. Never overact.")
        filename='OpenAI-Cedar-hook-sample-expressive-v2.wav'
    return generate(text,instructions,WORK/filename,note,voice='cedar')
def normalized_words(text):return re.findall(r"[a-z0-9]+",text.lower().replace('’',"'"))
def canonical_words(text):
    text=text.lower().replace('’',"'")
    for pattern,replacement in [(r'\bfifty[ -]+nine\b','59'),(r'\bone hundred (?:and )?fourteen\b','114'),(r'\btwo billion\b','2 billion'),(r'\bayah? len[sz]\b','ayah lens'),(r'\bmetaglasses\b','meta glasses'),(r'\bsuras\b','surahs'),(r'\bkoran\b','quran'),(r'\bhifts\b','hifz'),(r"\bdon't\b",'do not')]:text=re.sub(pattern,replacement,text)
    return normalized_words(text)
def align_phrases(phrases,words,seconds):
    wanted=[w for text in phrases for w in normalized_words(text)]
    actual=[w for row in words for w in normalized_words(row['word'])]
    if wanted!=actual:raise ValueError('Recognized words differ from the approved hook; do not slice or use this take')
    spans=[];offset=0;left=0
    for i,text in enumerate(phrases):
        offset+=len(normalized_words(text))
        right=seconds if i==len(phrases)-1 else (words[offset-1]['end']+words[offset]['start'])/2
        if right<=left:raise ValueError('Invalid acoustic phrase boundaries')
        spans.append((left,right));left=right
    return spans
def validate_transcription_source(path):
    path=Path(path).resolve()
    if not path.is_relative_to(WORK.resolve()):raise ValueError('Only generated English narration may be transcribed')
    receipt=json.loads(path.with_suffix('.json').read_text())
    if receipt.get('provider')!='OpenAI' or not receipt.get('text') or re.search(r'[\u0600-\u06ff]',receipt['text']):raise ValueError('Only receipted synthetic English narration may be uploaded')
    if receipt.get('sha256')!=sha(path):raise ValueError('Synthetic source hash differs from receipt')
def transcribe(path,note):
    path=Path(path).resolve();saved=path.with_suffix('.words.json')
    validate_transcription_source(path)
    if saved.exists():
        result=json.loads(saved.read_text())
        if result['source_sha256']==sha(path):return result
        raise ValueError('Transcription cache source changed')
    boundary='----AyahLensOpenAIWordTimestamps';chunks=[]
    for name,value in [('model','whisper-1'),('response_format','verbose_json'),('timestamp_granularities[]','word'),('language','en')]:
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="narration.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()+path.read_bytes()+b'\r\n');chunks.append(f'--{boundary}--\r\n'.encode())
    secret=key();req=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=b''.join(chunks),headers={'Authorization':'Bearer '+secret,'Content-Type':'multipart/form-data; boundary='+boundary})
    try:
        with urllib.request.urlopen(req,timeout=120) as response:result=json.load(response)
    except urllib.error.HTTPError as e:
        try:message=json.loads(e.read(8192)).get('error',{}).get('message','Request rejected')
        except Exception:message='Request rejected; body suppressed'
        raise RuntimeError(f'OpenAI transcription HTTP {e.code}: '+safe_error(message,secret)) from None
    except (urllib.error.URLError,TimeoutError):raise RuntimeError('OpenAI transcription network timeout/failure; no automatic retry, billing outcome unknown') from None
    estimated=math.ceil(duration(path))*.006/60
    result.update(provider='OpenAI',model='whisper-1',source_sha256=sha(path),note=note,estimated_cost_usd=round(estimated,6),cost_method='Estimated from decoded audio duration rounded up to seconds at documented Whisper USD0.006/minute; not invoice actuals.',pricing_source='https://developers.openai.com/api/docs/models/whisper-1')
    saved.write_text(json.dumps(result,indent=2)+'\n')
    with (WORK/'costs.jsonl').open('a') as log:log.write(json.dumps({'provider':'OpenAI','model':'whisper-1','source':str(path.relative_to(ROOT)),'source_sha256':sha(path),'estimated_cost_usd':result['estimated_cost_usd'],'cost_method':result['cost_method'],'note':note})+'\n')
    return result
def marin_sample(note):
    text=' '.join(b['text'] for b in beats()[2:9])
    direction=("Tell this like an enthusiastic, warm conversational storyteller sharing a breakthrough with a close friend. Make the emotional arc clearly audible. "
      "Begin What if with an audible smile and genuine wonder, a curious lift in pitch. Emphasize your glasses and personal Quran translator. "
      "The meaning right in front of your eyes should sound like a delightful discovery. Give the following benefit energetic rhythmic confidence. "
      "Make No scrolling and No tapping crisp and satisfying, each with its own emphasis. Then soften Just listen and finish And understand with sincere warm relief and resolution. "
      "Use varied pitch and energy rather than neutral announcer or bullet-list cadence. Speak every supplied word, including the final And understand. No extra words, music or effects. Pronounce Quran as kuh-raan.")
    return generate(text,direction,WORK/'OpenAI-Marin-hook-sample-expressive-v3.wav',note,voice='marin')
def edge_bounds(path):
    d=duration(path)
    r=run(['ffmpeg','-hide_banner','-i',path,'-af','silencedetect=noise=-50dB:d=0.07','-f','null','-'],capture_output=True,text=True)
    starts=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r.stderr)]
    ends=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r.stderr)]
    a=0;b=d
    if starts and ends and starts[0]<.001:a=max(0,ends[0]-.06)
    if starts and ends and abs(ends[-1]-d)<.015:b=min(d,starts[-1]+.09)
    if b<=a:raise ValueError('No positive speech region remains')
    return a,b
def prepare(note):
    if sha(BASE)!=BASE_HASH:raise ValueError('Accepted full v0.5 source changed')
    STEMS.mkdir(parents=True,exist_ok=True);clips=[]
    hook=ROOT/PLAN['coherent_hook'];assert sha(hook)==PLAN['coherent_hook_sha256']
    transcript=transcribe(hook,note+' coherent hook timestamps')
    hook_spans=align_phrases([b['text'] for b in beats()[2:9]],transcript['words'],duration(hook))
    hook_generation=json.loads(hook.with_suffix('.json').read_text());assert hook_generation['voice']==VOICE
    for i,b in enumerate(beats()):
        available=b['end']-b['start'];words=len(b['text'].split())
        instructions=EXPRESSIVE+b['tone']+f' Aim for approximately {max(.65,available-.1):.2f} seconds of speech, around {round(words*60/max(.65,available-.1))} words per minute. Finish every word cleanly. Preserve short natural pauses.'
        override=PLAN['generation_overrides'].get(b['id'],{})
        if override:instructions+=' '+override['instructions']
        suffix=f"-style{PLAN['style_revision']}"+(f"-take{override['take']:02}" if override else '')
        source=STEMS/(b['id']+suffix+'.wav')
        if 2<=i<9:
            lo,hi=hook_spans[i-2]
            run(['ffmpeg','-v','error','-y','-i',hook,'-af',f'atrim=start={lo}:end={hi},asetpts=PTS-STARTPTS','-c:a','pcm_s16le',source])
            receipt={'provider':'OpenAI','model':MODEL,'voice':VOICE,'text':b['text'],'duration':duration(source),'sha256':sha(source),'derived_slice':True,'coherent_hook':str(hook.relative_to(ROOT)),'coherent_hook_sha256':sha(hook),'coherent_generation_receipt':str(hook.with_suffix('.json').relative_to(ROOT)),'word_timestamp_receipt':str(hook.with_suffix('.words.json').relative_to(ROOT)),'source_bounds':[lo,hi],'split_method':'Midpoints between adjacent phrase word timestamps; source PCM performance retained.'}
            source.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
            lo,hi=0,receipt['duration']
        else:
            receipt=generate(b['text'],instructions,source,note,override.get('speed',1))
            lo,hi=edge_bounds(source)
            if override.get('append_ending'):
                body_source=source;ending=STEMS/(b['id']+suffix+'-ending.wav')
                ending_receipt=generate(override['append_ending'],EXPRESSIVE+'A crisp, confident concluding benefit. Say the supplied words once, clearly, with a warm satisfying finish.',ending,note+' verified omitted-ending repair')
                ea,eb=edge_bounds(ending);source=STEMS/(b['id']+suffix+'-complete.wav')
                filters=f'[0:a]atrim=start={lo}:end={hi},asetpts=PTS-STARTPTS[body];anullsrc=r=24000:cl=mono,atrim=duration=0.1[pause];[1:a]atrim=start={ea}:end={eb},asetpts=PTS-STARTPTS[end];[body][pause][end]concat=n=3:v=0:a=1[a]'
                run(['ffmpeg','-v','error','-y','-i',body_source,'-i',ending,'-filter_complex',filters,'-map','[a]','-c:a','pcm_s16le',source])
                receipt={'provider':'OpenAI','model':MODEL,'voice':VOICE,'text':b['text'],'duration':duration(source),'sha256':sha(source),'derived_concat':True,'body_generation_receipt':str(body_source.with_suffix('.json').relative_to(ROOT)),'ending_generation_receipt':str(ending.with_suffix('.json').relative_to(ROOT)),'reason':'Independent transcription found this final clause absent in both original paragraph generations; append the same-voice standalone sentence, then require full lexical verification.'}
                source.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');lo,hi=0,receipt['duration']
        fitting_available=available+override.get('extra_fit_seconds',0)
        tempo=fit_tempo(hi-lo,fitting_available)
        fitted=source.with_stem(source.stem+'-fitted')
        run(['ffmpeg','-v','error','-y','-i',source,'-af',f'atrim=start={lo}:end={hi},asetpts=PTS-STARTPTS,atempo={tempo:.9f},aresample=48000,aformat=channel_layouts=stereo','-c:a','pcm_s16le',fitted])
        measured=duration(fitted)
        if measured>fitting_available+.012:raise ValueError(f"Fitted clip exceeds window: {b['id']}")
        clips.append({**b,'end':b['end']+override.get('extra_fit_seconds',0),'duration':measured,'raw_duration':receipt['duration'],'edge_trim':[lo,hi],'tempo':tempo,'fit_extra_seconds':override.get('extra_fit_seconds',0),'stem':str(fitted.relative_to(ROOT)),'stem_sha256':sha(fitted),'generation_receipt':str(source.with_suffix('.json').relative_to(ROOT))})
        print(f"Prepared {b['id']}: {measured:.3f}s, tempo {tempo:.3f}",flush=True)
    validate_windows(clips)
    manifest={'video_version':'0.6','provider':'OpenAI','model':MODEL,'voice':VOICE,'base':str(BASE.relative_to(ROOT)),'base_sha256':BASE_HASH,'duration_seconds':DURATION,'protected_audio':PROTECTED,'clips':clips,'ai_disclosure':'AI-generated English narration','badge_rectangle':[1420,30,460,48],'ai_label_rectangle':[1420,30,460,48],'coherent_hook':str(hook.relative_to(ROOT)),'coherent_hook_sha256':sha(hook),'hook_all_words_verified':True}
    (WORK/'narration-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (WORK/'narration-script.txt').write_text('\n\n'.join(f"{c['start']:.3f}–{c['start']+c['duration']:.3f}\n{c['text']}" for c in clips)+'\n')
    return manifest
def audio_track(manifest):
    # Explicit source/silence pieces prevent frame-evaluated volume gates leaking guide audio.
    pieces=[(0,8,True),(8,30,False),(30,38,True),(38,60,False),(60,90,True),(90,DURATION,False)]
    filters=[];labels=[]
    for i,(a,b,genuine) in enumerate(pieces):
        label=f'p{i}';labels.append(f'[{label}]')
        filters.append((f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo' if genuine else f'anullsrc=r=48000:cl=stereo,atrim=duration={b-a},asetpts=PTS-STARTPTS')+f'[{label}]')
    filters.append(''.join(labels)+'concat=n=6:v=0:a=1[base]')
    args=['ffmpeg','-v','error','-y','-i',BASE];mix=['[base]']
    for i,c in enumerate(manifest['clips'],1):
        args+=['-i',ROOT/c['stem']];filters.append(f'[{i}:a]adelay={round(c["start"]*48000)}S:all=1[v{i}]');mix.append(f'[v{i}]')
    filters.append(''.join(mix)+f'amix=inputs={len(mix)}:normalize=0,apad,atrim=duration={DURATION}[audio]')
    run(args+['-filter_complex',';'.join(filters),'-map','[audio]','-c:a','pcm_s16le',WORK/'narration-mix.wav'])
def badges():
    from PIL import Image,ImageDraw,ImageFont
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
    for filename,size,text in [('version-badge.png',(460,48),'VIDEO v0.6'),('ai-disclosure.png',(460,48),'v0.6 / AI-generated English narration')]:
        assert font.getlength(text)<=size[0]-20,'Editorial badge text exceeds its protected header'
        image=Image.new('RGB',size,'#F3EFE5');d=ImageDraw.Draw(image);d.text((10,10),text,font=font,fill='#69675F');image.save(WORK/filename)
def render(manifest):
    audio_track(manifest);badges()
    filters="[0:v][2:v]overlay=x=1420:y=30:enable='gte(t,38)':shortest=1[v];[v][3:v]overlay=x=1420:y=30:enable='gte(t,8)*lt(t,30)+gte(t,38)*lt(t,60)+gte(t,90)':shortest=1,format=yuv420p[out]"
    with (WORK/'receipts/render.log').open('w') as log:
        run(['ffmpeg','-hide_banner','-y','-reinit_filter','0','-i',BASE,'-i',WORK/'narration-mix.wav','-loop','1','-framerate','30','-i',WORK/'version-badge.png','-loop','1','-framerate','30','-i',WORK/'ai-disclosure.png','-filter_complex_threads','2','-filter_complex',filters,'-map','[out]','-map','1:a','-c:v','libx264','-preset','fast','-crf','17','-threads','4','-r','30','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',DURATION,'-movflags','+faststart','-map_metadata','-1',OUT],stdout=log,stderr=log)
    write_captions(manifest)
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def write_captions(manifest):
    cues=[(0,4.4,'Quran recitation · Just listen.'),(4.4,8,'Can you follow its meaning?')]
    cues.extend((c['start'],c['start']+c['duration'],c['text']) for c in manifest['clips'])
    cues.append((30,38,'The same words. Now with meaning.\nRecorded glasses display · same passage replayed'))
    cues.sort();(WORK/'approximate-captions.srt').write_text('\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}\n' for i,(a,b,text) in enumerate(cues)))
def verify_english(manifest,note):
    import difflib
    fingerprint=hashlib.sha256(''.join(c['stem_sha256'] for c in manifest['clips']).encode()).hexdigest()[:12]
    target=WORK/f'English-only-fitted-{fingerprint}.wav';args=['ffmpeg','-v','error','-y'];labels=[]
    for i,c in enumerate(manifest['clips']):args+=['-i',ROOT/c['stem']];labels.append(f'[{i}:a]')
    run(args+['-filter_complex',''.join(labels)+f'concat=n={len(labels)}:v=0:a=1,aresample=24000,aformat=channel_layouts=mono[a]','-map','[a]','-c:a','pcm_s16le',target])
    text=' '.join(c['text'] for c in manifest['clips'])
    target.with_suffix('.json').write_text(json.dumps({'provider':'OpenAI','voice':VOICE,'kind':'Concatenated fitted synthetic English stems only; genuine Quran audio excluded','text':text,'sha256':sha(target),'clips':[c['id'] for c in manifest['clips']]},indent=2)+'\n')
    result=transcribe(target,note+' final English-only coverage check')
    expected=canonical_words(text);actual=canonical_words(result['text']);diff=list(difflib.unified_diff(expected,actual,fromfile='approved',tofile='recognized',lineterm=''))
    receipt={'source':str(target.relative_to(ROOT)),'source_sha256':sha(target),'transcription':str(target.with_suffix('.words.json').relative_to(ROOT)),'all_approved_words_match':expected==actual,'normalized_word_count':len(expected),'recognized_word_count':len(actual),'word_diffs':diff,'orthographic_equivalents':'Numbers, Ayah/Aya Lenz, MetaGlasses spacing, surahs/suras, Quran/Koran. Hifts/Hifz is a phonetic spelling uncertainty; pronunciation remains unverified.','human_pronunciation_verified':False,'scope':'Automatic normalized lexical coverage, not human pronunciation or emotional approval'}
    (WORK/'receipts/english-word-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (WORK/f'receipts/english-word-check-{fingerprint}.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if diff:raise ValueError('Final English transcript differs; see receipts/english-word-check.json')
    return receipt
def pcm(path,start,length):
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t',str(length),'-ar','48000','-ac','2','-f','f32le','-'])
    a=array.array('f');a.frombytes(data);return a[::8]
def corr(a,b):
    n=min(len(a),len(b));a=a[:n];b=b[:n];ma=sum(a)/n;mb=sum(b)/n
    den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else 1 if a==b else 0
def source_ssim(t):
    masks=''
    if t>=38 or 8<=t<30:masks+=',drawbox=x=1420:y=30:w=460:h=48:color=black:t=fill'
    filt=f'[0:v]trim=end_frame=1,setpts=PTS-STARTPTS{masks}[a];[1:v]trim=end_frame=1,setpts=PTS-STARTPTS{masks}[b];[a][b]ssim'
    r=run(['ffmpeg','-hide_banner','-ss',t,'-i',OUT,'-ss',t,'-i',BASE,'-lavfi',filt,'-frames:v','1','-f','null','-'],capture_output=True,text=True)
    return float(re.findall(r'All:([0-9.]+)',r.stderr)[-1])
def check():
    if sha(BASE)!=BASE_HASH:raise ValueError('Accepted full v0.5 changed')
    m=json.loads((WORK/'narration-manifest.json').read_text());validate_windows(m['clips'])
    if len(m['clips'])!=16:raise ValueError('Wrong narration clip count')
    coverage=json.loads((WORK/'receipts/english-word-check.json').read_text())
    assert coverage['all_approved_words_match'] and not coverage['word_diffs'],'English lexical coverage has not passed'
    fingerprint=hashlib.sha256(''.join(c['stem_sha256'] for c in m['clips']).encode()).hexdigest()[:12]
    assert coverage['source']==str((WORK/f'English-only-fitted-{fingerprint}.wav').relative_to(ROOT)),'English coverage receipt is stale'
    assert coverage['source_sha256']==sha(ROOT/coverage['source'])
    for c,expected in zip(m['clips'],beats()):
        assert c['text']==expected['text'] and c['start']==expected['start']
        assert sha(ROOT/c['stem'])==c['stem_sha256']
        assert abs(duration(ROOT/c['stem'])-c['duration'])<.001
        g=json.loads((ROOT/c['generation_receipt']).read_text())
        assert g['provider']=='OpenAI' and g['voice']==VOICE and g['text']==c['text'] and g['duration']>0
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(OUT)]));v=next(x for x in p['streams'] if x['codec_type']=='video');a=next(x for x in p['streams'] if x['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'30/1',5397)
    assert (a['sample_rate'],a['channels'])==('48000',2)
    assert abs(float(v['duration'])-DURATION)<.001 and abs(float(a['duration'])-DURATION)<.025
    r=run(['ffmpeg','-hide_banner','-i',OUT,'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
    peak=float(re.search(r'max_volume: ([-0-9.]+) dB',r.stderr).group(1));assert peak<0,'Audio clips'
    protected={f'{lo}-{hi}':corr(pcm(OUT,lo,hi-lo),pcm(BASE,lo,hi-lo)) for lo,hi in PROTECTED}
    assert min(protected.values())>.995,'Genuine recitation changed'
    mixed=corr(pcm(OUT,0,DURATION),pcm(WORK/'narration-mix.wav',0,DURATION));assert mixed>.995,'Output differs from new narration reconstruction'
    old_guide=corr(pcm(OUT,112,26),pcm(BASE,112,26));assert abs(old_guide)<.8,'Old technical guide voice may remain'
    visuals={str(t):source_ssim(t) for t in [2,9,17,29,31,37,39,49,60.5,67,89.5,93,120,150,179.5]}
    assert min(visuals.values())>.96,'Picture changed outside documented labels'
    cost=planning_cost();assert cost<1
    return {'output_sha256':sha(OUT),'base_unchanged_sha256':sha(BASE),'duration_seconds':float(v['duration']),'audio_duration_seconds':float(a['duration']),'frames':int(v['nb_read_frames']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'sample_rate':a['sample_rate'],'channels':a['channels'],'peak_dbfs':peak,'full_decode':'pass','narration_clips':len(m['clips']),'voice':VOICE,'protected_audio_correlations':protected,'new_mix_correlation':mixed,'old_guide_correlation_in_technical_scene':old_guide,'source_frame_ssim':visuals,'estimated_generation_and_review_cost_usd':round(cost,6),'cost_is_invoice_actual':False,'english_coverage':coverage,'human_audible_pronunciation_or_emotion_reviewed':False,'automatic_audio_review':{'provider':'OpenAI','model':'gpt-audio-1.5','receipt':'build/video-v0.6/qa/openai-full-english-audio-review.json','scope':'Actual fitted synthetic English audio; clear consistent voice, no material defects; restrained emotion. Not human approval.'},'ai_disclosure_regions':[m['badge_rectangle'],m['ai_label_rectangle']]}
def notes():
    (WORK/'viewing-notes.txt').write_text(f'FULL VIDEO v0.6 REVIEW CUT\nOpenAI-generated English narration, gpt-4o-mini-tts, built-in {VOICE} voice.\nDelivery directed for curiosity, confident benefits and warm resolution. Actual OpenAI audio-model review of the final English-only track found clear consistent delivery, no material defects and restrained emotion. Human listening and approval remain unverified.\n179.900 seconds, same picture/timing as accepted v0.5 outside documented editorial labels.\nGenuine Quran audio preserved at0–8,30–38,60–90; no synthetic scripture or real-person voice clone.\nAI-generated English narration is disclosed during narration intervals only.\nMasjid replacement60–90 remains labelled placeholder/reference fill.\nApproximate captions use exact supplied words and measured clip timings.\nCosts are planning estimates from decoded durations, not invoice actuals.\nEarlier exports remain unchanged. No app change, new capture, Meta website assets or publication.\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sample',action='store_true');p.add_argument('--expressive-sample',action='store_true');p.add_argument('--marin-sample',action='store_true');p.add_argument('--transcribe',type=Path);p.add_argument('--prepare',action='store_true');p.add_argument('--verify-english',action='store_true');p.add_argument('--render',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--note',default='read-only verification');a=p.parse_args()
    if not a.check and a.note=='read-only verification':p.error('--note is required for generation or rendering')
    if a.check:print(json.dumps(check(),indent=2));return
    if a.dry_run:print(json.dumps({'model':MODEL,'voice':VOICE,'beats':beats(),'no_api_request':True},indent=2));return
    if a.sample:print(json.dumps(sample(a.note),indent=2));return
    if a.expressive_sample:print(json.dumps(sample(a.note,True),indent=2));return
    if a.marin_sample:print(json.dumps(marin_sample(a.note),indent=2));return
    if a.transcribe:print(json.dumps(transcribe(a.transcribe,a.note),indent=2));return
    if a.verify_english:print(json.dumps(verify_english(json.loads((WORK/'narration-manifest.json').read_text()),a.note),indent=2));return
    if a.prepare:
        m=prepare(a.note)
        if a.render:
            verify_english(m,a.note);render(m);notes();result=check();(WORK/'receipts/verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
        return
    if a.render:
        m=json.loads((WORK/'narration-manifest.json').read_text());verify_english(m,a.note);render(m);notes();result=check();(WORK/'receipts/verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
    raise SystemExit('Use --sample, --prepare or --dry-run')
if __name__=='__main__':main()
