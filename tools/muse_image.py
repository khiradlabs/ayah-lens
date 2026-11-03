#!/usr/bin/env python3
"""One original Muse Image illustration per explicit call, with private cost receipts.

Official contract: https://dev.meta.ai/docs/image-generation
Price: https://dev.meta.ai/docs/pricing-rate-limits ($0.01/image).
No retry; --note is required. Outputs must stay under ignored build/.
"""
import argparse,base64,hashlib,io,json,os,time,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def request_body(prompt):
    return {'model':'muse-image-1.0','prompt':prompt,'n':1,'size':'1792x1024','response_format':'b64_json','output_format':'png','reasoning_strength':'high','tool_enablement':{'enable_web_search':False,'enable_image_search':False,'enable_shell':False}}

def save_result(result,out,prompt,note,elapsed):
    try:
        rows=result['data']
        if len(rows)!=1:raise ValueError('Expected one returned image')
        blob=base64.b64decode(rows[0]['b64_json'],validate=True)
        with Image.open(io.BytesIO(blob)) as image:
            image.verify()
        with Image.open(io.BytesIO(blob)) as image: dimensions=list(image.size)
    except Exception as e:raise ValueError('Muse returned no valid single image') from e
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
    receipt={'ts':datetime.now(timezone.utc).isoformat(),'model':'muse-image-1.0','prompt':prompt,'note':note,'elapsed_seconds':elapsed,'dimensions':dimensions,'sha256':hashlib.sha256(blob).hexdigest(),'usage':result.get('usage',{}),'est_cost_usd':.01,'price_source':'https://dev.meta.ai/docs/pricing-rate-limits','output':str(out)}
    out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    with (out.parent/'costs.jsonl').open('a') as log:log.write(json.dumps(receipt)+'\n')
    return receipt

def api_key():
    key=os.environ.get('META_API_KEY')
    if key:return key
    for line in (Path.home()/'.secrets/ayah-lens.env').read_text().splitlines():
        if line.startswith('META_API_KEY='):return line.split('=',1)[1].strip().strip('\"\'')
    raise ValueError('META_API_KEY missing in private credential file')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prompt-file',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--note',required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    out=a.out.resolve()
    if not out.is_relative_to(ROOT/'build'):p.error('Use an ignored output under project build/')
    if out.exists():p.error('Output exists; choose a new versioned filename')
    prompt=a.prompt_file.read_text();body=request_body(prompt)
    if a.dry_run:print(json.dumps({'request':body,'est_cost_usd':.01,'note':a.note},indent=2));return
    req=urllib.request.Request('https://api.meta.ai/v1/images/generations',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+api_key(),'Content-Type':'application/json'})
    start=time.monotonic()
    try:
        with urllib.request.urlopen(req,timeout=300) as response:result=json.load(response)
    except urllib.error.HTTPError as e:raise SystemExit(f'Muse HTTP {e.code}; no automatic retry. Response body suppressed.') from None
    except urllib.error.URLError:raise SystemExit('Muse network error; no automatic retry. Check account before retrying.') from None
    receipt=save_result(result,out,prompt,a.note,round(time.monotonic()-start,3))
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('prompt','usage')},indent=2))
if __name__=='__main__':main()
