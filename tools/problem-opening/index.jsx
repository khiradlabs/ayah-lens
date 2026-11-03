import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,interpolate,registerRoot,spring,staticFile,useCurrentFrame} from 'remotion';
import timeline from './timing.json';
const replay=timeline.scenes.find(([name])=>name==='replay')[1];
const cues=timeline.narration_starts.map(s=>Math.round(s*timeline.fps));
const C={paper:'#F3EFE5',ink:'#1A1A18',red:'#B94B37',blue:'#465D79'};
const tween=(f,a,b,x,y)=>interpolate(f,[a,b],[x,y],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
const ease=(f,start,d=30)=>spring({frame:f-start,fps:30,config:{damping:22,stiffness:90,mass:.9},durationInFrames:d});
const Text=({children,x=100,y=150,size=85,width=1100,color=C.ink,style={}})=><div style={{position:'absolute',left:x,top:y,width,fontSize:size,lineHeight:1.09,fontWeight:650,letterSpacing:-2,color,...style}}>{children}</div>;
const Label=({children,x=100,y=65,color=C.ink})=><div style={{position:'absolute',left:x,top:y,fontSize:25,fontWeight:650,letterSpacing:1.5,color}}>{children}</div>;
const Footer=({children})=><div style={{position:'absolute',left:100,bottom:43,fontSize:22,letterSpacing:.1,color:C.ink}}>{children}</div>;
const Art=({f,opacity=1,scale=1})=><div style={{position:'absolute',inset:0,opacity,transform:`scale(${scale})`,transformOrigin:'76% 56%'}}>
 <Img src={staticFile('media/listener-muse.png')} style={{position:'absolute',inset:0,width:1920,height:1080}}/>
 <div style={{position:'absolute',inset:0,clipPath:'inset(24% 0 0 59%)',transform:`translate(${Math.sin(f/90)*4}px,${Math.sin(f/80)*-3}px)`}}><Img src={staticFile('media/listener-muse.png')} style={{width:1920,height:1080}}/></div>
 </div>;
const Sound=({f,y=810,width=950,opacity=1})=><svg style={{position:'absolute',left:100,top:y,width,height:80,opacity}} viewBox={`0 0 ${width} 80`}>
 <path d={`M0 40H${width}`} stroke={C.blue} strokeWidth="2" opacity=".25"/>
 {Array.from({length:57},(_,i)=>{const h=8+Math.abs(Math.sin(i*1.12+f*.07))*Math.sin(i/56*Math.PI)*43;return <path key={i} d={`M${i*width/56} ${40-h/2}V${40+h/2}`} stroke={C.blue} strokeWidth="5" strokeLinecap="round"/>})}
 </svg>;
const Person=({x,y,blue=false,opacity=1})=><g transform={`translate(${x} ${y})`} fill={blue?C.blue:C.ink} opacity={opacity}><circle cx="18" cy="14" r="12"/><path d="M1 68V45Q2 31 18 31Q34 31 35 45V68Z"/></g>;
const Listen=({f})=>{const q=ease(f,132,40);return <>
 <Art f={f} scale={1+tween(f,0,240,0,.018)}/><Label>Quran recitation · original audio</Label>
 <Text y={205} size={139}>Just listen.</Text>
 <Text y={500} size={85} color={C.red} style={{opacity:q,transform:`translateY(${(1-q)*35}px)`}}>Can you follow<br/>its meaning?</Text>
 <Sound f={f}/><Footer>Concept illustration made with Muse Image · genuine recitation audio</Footer>
 </>};
const Problem=({f})=>{const t=ease(f,240,27);return <>
 <Art f={f} scale={1.018}/><Label>A familiar sound. An unfamiliar language.</Label>
 <Text y={200} size={101} style={{opacity:t,transform:`translateY(${(1-t)*30}px)`}}>You hear the words.</Text>
 <Text y={360} size={97} color={C.red}>Can you follow<br/>the meaning?</Text>
 <Text y={720} size={31} width={950} style={{fontWeight:450,letterSpacing:0,lineHeight:1.35}}>For many who do not understand Arabic,<br/>the recitation is familiar.</Text>
 <Sound f={f} y={855}/>
 </>};
const Scale=({f})=>{const p=ease(f,360,28);return <>
 <Art f={f} opacity={.45} scale={1.018}/>
 <div style={{position:'absolute',inset:0,background:`linear-gradient(90deg,${C.paper}ee 0%,${C.paper}cc 54%,transparent 84%)`}}/>
 <Label>One listener. A worldwide community.</Label>
 <Text y={150} size={175} style={{transform:`translateY(${(1-p)*-30}px)`}}>2 billion</Text>
 <Text y={365} size={66}>Muslims worldwide.</Text>
 <svg style={{position:'absolute',left:110,top:485,width:1020,height:330}} viewBox="0 0 1020 330">{Array.from({length:40},(_,i)=><Person key={i} x={(i%10)*99} y={Math.floor(i/10)*78} blue={i<10} opacity={tween(f,360+i*.7,382+i*.7,0,.85)}/>)}</svg>
 <Text y={840} size={47} color={C.blue}>Roughly one quarter of humanity.</Text>
 <div style={{position:'absolute',left:100,bottom:40,fontSize:21,lineHeight:1.35}}>Pew Research Center · 2020 estimate, published 2025 · 25.6%<br/>Population context, not a count of people needing translation.</div>
 </>};
const Hook=({f})=>{const t=ease(f,cues[2],26),line=tween(f,cues[2]+20,cues[2]+60,0,1);return <>
 <Art f={f} scale={1.018}/><Label>Ayah Lens</Label>
 <div style={{transform:`translateY(${(1-t)*28}px)`,opacity:t}}>
 <Text y={190} size={89} width={1200}>What if your glasses<br/>became your personal<br/><span style={{color:C.blue}}>Quran translator?</span></Text>
 <div style={{position:'absolute',left:103,top:517,height:5,width:line*855,background:C.blue}}/>
 </div>
 <Sound f={f} y={855}/>
 </>};
const Meaning=({f})=>{const t=ease(f,cues[3],24),bracket=tween(f,cues[3],cues[3]+45,0,1);return <>
 <Label>01 / Meaning in view</Label>
 <div style={{position:'absolute',left:83,top:177,width:1035,height:430,transform:`scaleX(${bracket})`,transformOrigin:'left center',borderTop:`3px solid ${C.blue}`,borderBottom:`3px solid ${C.blue}`,opacity:.45}}/>
 <Text y={210} size={104} style={{transform:`translateY(${(1-t)*26}px)`}}>The meaning.</Text>
 <Text y={370} size={85} color={C.blue} style={{opacity:t}}>Right in front<br/>of your eyes.</Text>
 </>};
const Following=({f})=>{const t=ease(f,cues[4],24),progress=tween(f,cues[4]+8,cues[5]-5,0,1);return <>
 <Label>02 / Follows automatically</Label>
 <Text y={205} size={100}>The text follows<br/>the recitation.</Text>
 <Text y={470} size={81} color={C.blue} style={{transform:`translateX(${(1-t)*-60}px)`,opacity:t}}>Automatically.</Text>
 <div style={{position:'absolute',left:106,top:650,width:925,height:9,background:`${C.blue}24`}}><div style={{height:9,width:`${progress*100}%`,background:C.blue}}/><div style={{position:'absolute',left:progress*925-9,top:-5,width:19,height:19,borderRadius:'50%',background:C.blue}}/></div>
 </>};
const HandsFree=({f})=>{const tap=f>=cues[6],n=tap?cues[6]:cues[5],t=ease(f,n,18);return <>
 <Label>03 / Hands-free following</Label>
 <Text y={195} size={108} style={{transform:`translateY(${(1-t)*25}px)`,opacity:t}}>{tap?'No tapping.':'No scrolling.'}</Text>
 <svg style={{position:'absolute',left:110,top:400,width:760,height:210}} viewBox="0 0 760 210">
 {tap?<g><circle cx="125" cy="105" r="61" fill="none" stroke={C.blue} strokeWidth="6"/><circle cx="125" cy="105" r="91" fill="none" stroke={C.blue} strokeWidth="3" opacity=".25"/><path d="M58 175L192 35" stroke={C.red} strokeWidth="10" strokeDasharray="200" strokeDashoffset={(1-t)*200}/></g>:<g><path d="M74 48H160M117 20V175M74 146L117 185L160 146" fill="none" stroke={C.blue} strokeWidth="6"/><path d="M47 185L192 20" stroke={C.red} strokeWidth="10" strokeDasharray="230" strokeDashoffset={(1-t)*230}/></g>}
 <text x="265" y="119" fontSize="46" fontFamily="Arial" fill={C.blue}>Stay with the recitation.</text>
 </svg>
 <Text y={720} size={27} style={{fontWeight:450,letterSpacing:0}}>Automatic following while listening.</Text>
 </>};
const Benefits=({f})=>{
 const finale=f>=cues[7],understand=f>=cues[8],expand=tween(f,replay-28,replay-1,0,1),preview=f>=replay-24;
 const left=100+expand*28,top=855-expand*405,width=950+expand*714,height=70+expand*346;
 return <>
 <Art f={f} opacity={1-expand} scale={1.018}/>
 {!finale?(f<cues[4]?<Meaning f={f}/>:f<cues[5]?<Following f={f}/>:<HandsFree f={f}/>):<>
 <Label>Ayah Lens · meaning in view</Label>
 <Text x={128} y={175} size={113} width={1600}>Just listen.</Text>
 <Text x={128} y={325} size={101} width={1600} color={C.blue} style={{opacity:understand?ease(f,cues[8],15):0}}>And understand.</Text>
 </>}
 <div style={{position:'absolute',left,top,width,height,overflow:'hidden',boxSizing:'border-box',border:`${expand>0?3:0}px solid ${C.blue}`,background:preview?C.ink:'transparent'}}>
 {preview?<Img src={staticFile('media/native-crop-frame0.png')} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>:null}
 <svg style={{position:'absolute',inset:0,width:'100%',height:'100%',opacity:1-expand}} viewBox="0 0 950 70">{Array.from({length:57},(_,i)=><path key={i} d={`M${i*17} ${35-Math.abs(Math.sin(i+f*.07))*20}V${35+Math.abs(Math.sin(i+f*.07))*20}`} stroke={C.blue} strokeWidth="4"/>)}</svg>
 </div>
 </>;
};
const Replay=()=> <>
 <div style={{position:'absolute',left:128,top:62,fontSize:48,fontWeight:650,color:C.blue}}>Recorded glasses display</div>
 <div style={{position:'absolute',left:128,top:127,fontSize:30}}>Arabic + English in the glasses · same passage replayed</div>
 <Text x={128} y={210} size={78} width={1664}>The same words.<br/><span style={{color:C.blue}}>Now with meaning.</span></Text>
 <div style={{position:'absolute',left:128,top:450,width:1664,height:416,overflow:'hidden',boxShadow:`0 0 0 3px ${C.blue}`}}><OffthreadVideo muted src={staticFile('media/native.mp4')} style={{position:'absolute',width:2819.5555556,height:3744,left:-600.8888889,top:-2403.5555556}}/></div>
 <Text x={128} y={910} size={28} width={1664} style={{fontWeight:450,letterSpacing:0}}>Enlarged from native camera + display recording · unchanged source text</Text>
 <div style={{position:'absolute',left:128,top:963,fontSize:26}}>Background: camera view · Text: recorded glasses display</div>
 <Footer>Earlier prototype footage · original speed · same source replay</Footer>
 </>;
const Opening=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{backgroundColor:C.paper,color:C.ink,fontFamily:'Arial, Helvetica, sans-serif',overflow:'hidden'}}>
 {f<240?<Listen f={f}/>:f<360?<Problem f={f}/>:f<465?<Scale f={f}/>:f<574?<Hook f={f}/>:f<replay?<Benefits f={f}/>:<Sequence from={replay} durationInFrames={240}><Replay/></Sequence>}
 <div style={{position:'absolute',left:0,bottom:0,height:4,width:`${f/(timeline.frames-1)*100}%`,background:C.red}}/>
 </AbsoluteFill>};
registerRoot(()=><Composition id="ProblemOpening" component={Opening} durationInFrames={timeline.frames} fps={timeline.fps} width={1920} height={1080}/>);
