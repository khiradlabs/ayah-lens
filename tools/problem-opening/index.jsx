import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,interpolate,registerRoot,spring,staticFile,useCurrentFrame} from 'remotion';
import timeline from './timing.json';
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
const Problem=({f})=>{const t=ease(f,244,40),meaning=ease(f,325,40);return <>
 <Art f={f} scale={1.018}/><Label>A familiar sound</Label>
 <Text y={190} size={100} style={{opacity:t,transform:`translateY(${(1-t)*30}px)`}}>Hearing the Quran.<br/>Every day.</Text>
 <Text y={465} size={88} color={C.red} style={{opacity:meaning,transform:`translateY(${(1-meaning)*30}px)`}}>Without following<br/>its meaning.</Text>
 <Text y={735} size={31} width={950} style={{fontWeight:450,letterSpacing:0,lineHeight:1.35}}>For many Muslims who do not understand Arabic,<br/>the sound is familiar. The meaning is out of reach.</Text>
 <Sound f={f} y={865} width={950}/><Footer>Concept illustration · no generated scripture or device output</Footer>
 </>};
const Scale=({f})=>{const p=ease(f,514,35);return <>
 <Art f={f} opacity={.45} scale={1.018}/>
 <div style={{position:'absolute',inset:0,background:`linear-gradient(90deg,${C.paper}ee 0%,${C.paper}cc 54%,transparent 84%)`}}/>
 <Label>One listener. A worldwide community.</Label>
 <Text y={150} size={175} style={{transform:`translateY(${(1-p)*-30}px)`}}>2 billion</Text>
 <Text y={365} size={66}>Muslims worldwide.</Text>
 <svg style={{position:'absolute',left:110,top:485,width:1020,height:330}} viewBox="0 0 1020 330">{Array.from({length:40},(_,i)=><Person key={i} x={(i%10)*99} y={Math.floor(i/10)*78} blue={i<10} opacity={tween(f,514+i*.9,540+i*.9,0,.85)}/>)}</svg>
 <Text y={840} size={47} color={C.blue}>Roughly one quarter of humanity.</Text>
 <div style={{position:'absolute',left:100,bottom:40,fontSize:21,lineHeight:1.35}}>Pew Research Center · 2020 estimate, published2025 · 25.6%<br/>Population context, not a count of people needing translation.</div>
 </>};
const Bridge=({f})=>{
 const returnToListener=ease(f,658,32),frame=tween(f,784,839,0,1),lift=tween(f,785,807,0,1),leave=tween(f,755,780,0,1);
 const left=100+frame*28,top=785-frame*335,width=950+frame*714,height=70+frame*346;
 return <>
 <Art f={f} opacity={1-frame} scale={1.018}/>
 <Label>Ayah Lens · meaning in view</Label>
 <div style={{opacity:1-leave,transform:`translateY(${(1-returnToListener)*35}px)`}}>
 <Text y={185} size={91}>What if your glasses<br/>could put the meaning<br/><span style={{color:C.blue}}>in view?</span></Text>
 </div>
 <Text x={128} y={165} size={88} width={1600} style={{opacity:lift}}>Listen again.</Text>
 <Text x={128} y={280} size={54} width={1600} color={C.blue} style={{opacity:lift}}>The same words. Now with meaning.</Text>
 <div style={{position:'absolute',left,top,width,height,border:`3px solid ${C.blue}`,background:`rgba(26,26,24,${frame*.98})`,overflow:'hidden',boxSizing:'border-box'}}>
 {f>=816?<Img src={staticFile('media/native-crop-frame0.png')} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>:null}
 <svg style={{position:'absolute',inset:0,width:'100%',height:'100%',opacity:1-frame}} viewBox="0 0 950 70">{Array.from({length:57},(_,i)=><path key={i} d={`M${i*17} ${35-Math.abs(Math.sin(i+f*.07))*20}V${35+Math.abs(Math.sin(i+f*.07))*20}`} stroke={C.blue} strokeWidth="4"/>)}</svg>
 </div>
 <Footer>Next: the same genuine passage, replayed with its recorded glasses display</Footer>
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
 {f<240?<Listen f={f}/>:f<514?<Problem f={f}/>:f<658?<Scale f={f}/>:f<840?<Bridge f={f}/>:<Sequence from={840} durationInFrames={240}><Replay/></Sequence>}
 <div style={{position:'absolute',left:0,bottom:0,height:4,width:`${f/1079*100}%`,background:C.red}}/>
 </AbsoluteFill>};
registerRoot(()=><Composition id="ProblemOpening" component={Opening} durationInFrames={timeline.frames} fps={timeline.fps} width={1920} height={1080}/>);
