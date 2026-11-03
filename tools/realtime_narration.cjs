// One bounded speech-only audition. No microphone input, automatic retry or video changes.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const WebSocket = require('./problem-opening/node_modules/ws');
const args = process.argv.slice(2);
const manifest = args[0];
const noteIndex = args.indexOf('--note');
const note = noteIndex >= 0 ? args[noteIndex+1] : '';
if (!manifest || !note || note.startsWith('--')) throw new Error('Usage: node tools/realtime_narration.cjs TAKE.json --note REASON [--dry-run]');
const root = path.resolve(__dirname, '..');
const take = JSON.parse(fs.readFileSync(manifest, 'utf8'));
const {model, voice, text, instructions} = take;
if (model !== 'gpt-realtime-2.1' || voice !== 'cedar' || !text || !instructions) throw new Error('Expected a bounded Realtime Cedar English audition');
const speed = take.speed ?? 1;
if (speed !== 1) throw new Error('Auditions preserve generated playback speed');
const wavpath = path.resolve(root, take.output);
if (!wavpath.startsWith(path.join(root,'build')+path.sep) || path.extname(wavpath)!=='.wav') throw new Error('Output must be a private build WAV');
const outdir = path.dirname(wavpath);
const config = {type:'realtime', model, output_modalities:['audio'], instructions, audio:{input:{turn_detection:null},output:{format:{type:'audio/pcm',rate:24000},voice,speed}}};
if (args.includes('--dry-run')) {console.log(JSON.stringify({output:wavpath,session:config,text,note},null,2));process.exit(0);}
if (fs.existsSync(wavpath)) throw new Error('Audition already exists; no new charge made');
fs.mkdirSync(outdir,{recursive:true});
const keyfile = path.join(require('os').homedir(), '.secrets/ayah-lens-openai.env');
const line = fs.readFileSync(keyfile, 'utf8').split(/\r?\n/).find(v => v.startsWith('OPENAI_API_KEY='));
const secret = line?.slice('OPENAI_API_KEY='.length).trim().replace(/^["']|["']$/g, '');
if (!secret) throw new Error('Private OpenAI credential is empty');
let parts = [], transcript = '', finished = false, bytes = 0;
const started = Date.now();
const ws = new WebSocket('wss://api.openai.com/v1/realtime?model='+model, {headers:{Authorization:'Bearer '+secret}});
const timer = setTimeout(()=>fail('Audition timed out; no automatic retry, billing outcome uncertain'),60000);
function fail(message){if(finished)return;finished=true;clearTimeout(timer);ws.terminate();console.error(String(message).split(secret).join('[REDACTED]').slice(0,700));process.exitCode=1;}
ws.on('error',()=>fail('Realtime connection failed; no automatic retry'));
ws.on('close',()=>{if(!finished)fail('Connection closed before response completion');});
ws.on('message', raw=>{
 let e;try{e=JSON.parse(raw.toString());}catch{return fail('Invalid server event');}
 if(e.type==='error')return fail('Realtime error: '+e.error?.message);
 if(e.type==='session.created') ws.send(JSON.stringify({type:'session.update',session:config}));
 if(e.type==='session.updated') {
  ws.send(JSON.stringify({type:'conversation.item.create',item:{type:'message',role:'user',content:[{type:'input_text',text:'Read this script exactly once:\n'+text}]}}));
  ws.send(JSON.stringify({type:'response.create',response:{max_output_tokens:1800}}));
 }
 if(e.type==='response.output_audio.delta'){
  const p=Buffer.from(e.delta,'base64');bytes+=p.length;if(bytes>24000*2*40)return fail('Output exceeded40seconds; stopped');parts.push(p);
 }
 if(e.type==='response.output_audio_transcript.delta')transcript+=e.delta;
 if(e.type==='response.done'){
  if(e.response.status!=='completed')return fail('Response did not complete: '+e.response.status);
  if(!bytes||bytes%2)return fail('No complete PCM audio returned');
  const pcm=Buffer.concat(parts), h=Buffer.alloc(44);h.write('RIFF');h.writeUInt32LE(36+pcm.length,4);h.write('WAVEfmt ',8);h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(1,22);h.writeUInt32LE(24000,24);h.writeUInt32LE(48000,28);h.writeUInt16LE(2,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(pcm.length,40);
  const wav=Buffer.concat([h,pcm]);fs.writeFileSync(wavpath,wav);
  const usage=e.response.usage, inp=usage?.input_token_details, output=usage?.output_token_details;
  const estimated=usage ? ((inp?.text_tokens||0)*4+(inp?.audio_tokens||0)*32+(output?.text_tokens||0)*24+(output?.audio_tokens||0)*64)/1e6 : null;
  const receipt={provider:'OpenAI',model,voice,text,instructions,transcript,duration:pcm.length/48000,sha256:crypto.createHash('sha256').update(wav).digest('hex'),usage,estimated_cost_usd:estimated,cost_method:'Token-based estimate at documented uncached rates; not invoice actuals.',pricing_source:'https://developers.openai.com/api/docs/models/gpt-realtime-2.1',continuous_take:true,time_stretching:false,note, speed,created_at:new Date().toISOString(),elapsed_seconds:(Date.now()-started)/1000};
  fs.writeFileSync(wavpath.replace('.wav','.json'),JSON.stringify(receipt,null,2)+'\n');fs.appendFileSync(path.join(outdir,'costs.jsonl'),JSON.stringify(receipt)+'\n');
  finished=true;clearTimeout(timer);ws.close();console.log(JSON.stringify({output:wavpath,model,voice,duration:receipt.duration,transcript,usage,estimated_cost_usd:estimated},null,2));
 }
});
