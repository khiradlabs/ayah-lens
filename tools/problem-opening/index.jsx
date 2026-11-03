import React from 'react';
import {AbsoluteFill, Composition, OffthreadVideo, Sequence, interpolate, registerRoot, spring, staticFile, useCurrentFrame} from 'remotion';
import timeline from './timing.json';
const C={paper:'#F3EFE5',ink:'#1A1A18',red:'#D34B38',blue:'#53749B'};
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const ease=(f,start,d=28)=>spring({frame:f-start,fps:30,config:{damping:19,stiffness:105,mass:.8},durationInFrames:d});
const tween=(f,a,b,x,y)=>interpolate(f,[a,b],[x,y],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
const Text=({children,x=100,y=100,size=80,width=1600,color=C.ink,style={}})=><div style={{position:'absolute',left:x,top:y,width,fontSize:size,lineHeight:1.07,fontWeight:650,letterSpacing:-2,...style,color}}>{children}</div>;
const Label=({children,x=100,y=70,color=C.ink,width=1700})=><div style={{position:'absolute',left:x,top:y,width,fontSize:23,letterSpacing:2.3,textTransform:'uppercase',fontWeight:650,color}}>{children}</div>;
const Listener=({x=0,y=0,scale=1,gaze=0})=><div style={{position:'absolute',left:x,top:y,width:640,height:740,transform:`scale(${scale})`,transformOrigin:'50% 50%'}}><svg width="640" height="740" viewBox="0 0 640 740">
 <ellipse cx="308" cy="687" rx="274" ry="20" fill={C.ink} opacity=".10"/>
 <path d="M72 677L106 484Q146 427 250 423L386 423Q489 444 525 510L566 677Z" fill={C.blue}/>
 <path d="M204 449L274 528L363 451" fill="none" stroke={C.paper} strokeWidth="5"/>
 <path d="M260 364L256 446Q300 484 355 443L357 350" fill="#D4B998" stroke={C.ink} strokeWidth="5"/>
 <g transform={`rotate(${gaze} 318 270)`}>
 <path d="M190 231C174 105 266 66 348 97Q438 122 428 222L460 271L427 286Q432 360 370 383L265 363Q213 321 190 231Z" fill="#DDC6AA" stroke={C.ink} strokeWidth="5"/>
 <path d="M187 238Q149 122 240 77Q350 25 411 119L426 194L374 174Q337 128 290 168L246 232L233 301Q200 291 187 238Z" fill={C.ink}/>
 <path d="M239 233Q204 215 203 257Q205 293 237 292" fill="#DDC6AA" stroke={C.ink} strokeWidth="5"/>
 <path d="M216 253Q232 240 232 272" fill="none" stroke={C.ink} strokeWidth="4"/>
 <path d="M361 217L393 215" stroke={C.ink} strokeWidth="6" strokeLinecap="round"/>
 <circle cx="383" cy="235" r="7" fill={C.ink}/>
 <path d="M398 310Q412 317 426 309" fill="none" stroke={C.ink} strokeWidth="4"/>
 </g>
 <path d="M147 527L120 665M470 536L501 675" stroke={C.ink} strokeWidth="5" fill="none" opacity=".55"/>
 </svg></div>;
const Waves=({f,x=0,y=0,scale=1,color=C.blue,opacity=1})=><svg style={{position:'absolute',left:x,top:y,transform:`scale(${scale})`,transformOrigin:'left center',opacity}} width="850" height="650" viewBox="0 0 850 650">{[0,1,2,3].map(i=><path key={i} d={`M${60+i*120} 120Q${260+i*120} 325 ${60+i*120} 530`} fill="none" stroke={color} strokeWidth={7-i} opacity={.8-i*.15} transform={`translate(${Math.sin(f/25+i)*12} 0)`}/>)}</svg>;
const Corner=({children})=><div style={{position:'absolute',left:100,bottom:40,fontSize:22,color:C.ink,letterSpacing:.2}}>{children}</div>;
const Familiar=({f})=>{
 const intro=ease(f,240,38), scatter=ease(f,323,30);
 return <><div style={{position:'absolute',inset:0,transform:`translateX(${(1-intro)*180}px)`}}>
 <Waves f={f} x={780} y={240} scale={.83} opacity={.70}/>
 <Listener x={1130-intro*115} y={250} scale={1.04}/>
 <div style={{position:'absolute',left:770,top:480,transform:`rotate(-9deg) translate(${scatter*35}px,${scatter*-45}px)`,width:230,height:180,background:C.paper,border:`3px solid ${C.red}`,boxShadow:'12px 14px 0 #1a1a1815',opacity:scatter}}><div style={{fontSize:95,textAlign:'center',paddingTop:30,color:C.red}}>?</div></div>
 </div>
 <Label>01 / A familiar sound</Label>
 <Text x={100} y={205} size={94} width={1010} style={{transform:`translateY(${(1-intro)*45}px)`}}>Hearing the Quran.<br/>Every day.</Text>
 <div style={{position:'absolute',left:100,top:470,width:925,overflow:'hidden',height:265}}><Text x={0} y={0} size={86} width={920} color={C.red} style={{transform:`translateY(${(1-scatter)*275}px)`}}>Without following<br/>its meaning.</Text></div>
 <Text x={105} y={805} size={31} width={930} style={{fontWeight:450,lineHeight:1.3,letterSpacing:0}}>A familiar experience for many Muslims<br/>who do not understand Arabic.</Text>
 <Corner>Concept illustration · no app output</Corner>
 </>;
};
const Scale=({f})=>{
 const t=ease(f,514,38);const turn=tween(f,524,570,-18,0);
 return <><div style={{position:'absolute',inset:0,transform:`translateY(${(1-t)*130}px)`}}>
 <Label>02 / The wider context</Label>
 <Text y={205} size={190} width={1000}>About <span style={{color:C.red}}>2B</span></Text>
 <Text y={415} size={73} width={950}>people are Muslim.</Text>
 <Text y={590} size={57} width={930} style={{fontWeight:450}}>Roughly one quarter<br/>of humanity.</Text>
 <svg style={{position:'absolute',left:1165,top:245,transform:`rotate(${turn}deg) scale(${.75+t*.25})`}} width="550" height="550" viewBox="0 0 550 550"><circle cx="275" cy="275" r="238" fill="none" stroke="#D8D4CB" strokeWidth="48"/><circle cx="275" cy="275" r="238" fill="none" stroke={C.red} strokeWidth="48" strokeDasharray={`${2*Math.PI*238*.256} ${2*Math.PI*238*.744}`} transform="rotate(-90 275 275)"/>{Array.from({length:100},(_,i)=>{let x=130+(i%10)*32,y=130+Math.floor(i/10)*32;return <circle key={i} cx={x} cy={y} r="8" fill={i<26?C.red:C.ink} opacity={i<26?1:.25}/>})}</svg>
 <div style={{position:'absolute',left:1165,top:830,width:550,textAlign:'center',fontSize:25}}>Population context, not a measure of need.</div>
 </div>
 <div style={{position:'absolute',left:100,top:935,fontSize:24,lineHeight:1.3}}>Pew Research Center · 2020 estimate, published 2025<br/>Underlying share: 25.6% · This does not imply all Muslims need translation.</div>
 </>;
};
const Phone=({f})=>{
 const t=ease(f,658,25),look=ease(f,673,35),bridge=ease(f,742,30);
 const px=1080-t*140,py=530;
 return <><Label>03 / The attention cost</Label>
 <div style={{position:'absolute',inset:0,transform:`translateX(${-bridge*1950}px) rotate(${-bridge*8}deg)`,transformOrigin:'55% 80%'}}>
 <Waves f={f} x={1080} y={30} scale={.72} opacity={.45}/>
 <Listener x={1120-t*360} y={170-t*70} scale={.99} gaze={look*25}/>
 <svg style={{position:'absolute',left:1000,top:340,width:500,height:450,opacity:look}} viewBox="0 0 500 450"><path d="M160 80Q240 240 180 350" stroke={C.red} strokeWidth="5" strokeDasharray="12 12" fill="none"/><path d="M164 330L180 356L204 337" stroke={C.red} strokeWidth="5" fill="none"/></svg>
 <div style={{position:'absolute',left:px,top:py,width:254,height:420,background:C.ink,borderRadius:35,boxShadow:'20px 23px 0 #1a1a181b',transform:`rotate(${-12+look*6}deg) translateY(${(1-t)*480}px)`}}><div style={{position:'absolute',inset:14,background:C.paper,borderRadius:23,padding:25,paddingTop:47}}><div style={{fontSize:23,color:C.blue,fontWeight:650,letterSpacing:0}}>Translation</div>{[1,.8,.95,.6,.9,.7].map((n,i)=><div key={i} style={{height:8,width:`${n*100}%`,marginTop:20,background:C.ink,opacity:.32}}/>)}<div style={{marginTop:27,fontSize:14,letterSpacing:0}}>Concept illustration</div></div><div style={{position:'absolute',left:90,top:18,width:75,height:12,borderRadius:9,background:C.ink}}/></div>
 <Text y={220} size={91} width={830}>The meaning<br/>is on a phone.</Text>
 <Text y={540} size={81} width={770} color={C.red}>Your gaze<br/>leaves the moment.</Text>
 <Corner>Concept illustration · no app output</Corner>
 </div>
 <div style={{position:'absolute',inset:0,transform:`translateX(${(1-bridge)*2200}px)`}}>
 <Text x={130} y={250} size={119} width={1650}>Now listen again.</Text>
 <Text x={130} y={440} size={98} width={1650} color={C.blue}>With the meaning<br/>in view.</Text>
 <svg style={{position:'absolute',left:135,top:755}} width="1640" height="150"><path d="M0 40H1500L1450 0M1500 40L1450 80" stroke={C.blue} strokeWidth="7" fill="none" strokeDasharray="1700" strokeDashoffset={(1-bridge)*1700}/></svg>
 <Corner>Next: the same eight seconds of actual recitation</Corner>
 </div>
 </>;
};
const Listen=({f})=>{const question=ease(f,132,35);return <>
 <Label>Quran recitation · original audio</Label>
 <Text x={100} y={205} size={151} width={1250}>Just listen.</Text>
 <Waves f={f} x={1030} y={195} scale={.75}/>
 <div style={{position:'absolute',left:1400,top:340,width:160,height:235,border:`9px solid ${C.ink}`,borderRadius:'54% 50% 50% 45%',transform:`rotate(-16deg) translateY(${Math.sin(f/30)*4}px)`}}><div style={{position:'absolute',left:40,top:45,width:65,height:130,border:`7px solid ${C.ink}`,borderRightColor:'transparent',borderRadius:'50%'}}/></div>
 <Text x={100} y={555} size={96} width={1390} color={C.red} style={{transform:`translateY(${(1-question)*60}px)`,opacity:question}}>Can you follow<br/>its meaning?</Text>
 <Corner>Genuine recitation · the same excerpt will return with the recorded display</Corner>
 </>};
const Replay=({f})=>{const t=ease(f,0,25);return <>
 <div style={{position:'absolute',left:92,top:65,fontSize:30,fontWeight:650,color:C.blue}}>Actual glasses display · same passage replayed</div>
 <Text x={92} y={195} size={83} width={1035}>The same words.<br/><span style={{color:C.blue}}>Now with meaning.</span></Text>
 <div style={{position:'absolute',left:92,top:458,fontSize:25,width:1020}}>Enlarged crop from the same recording</div>
 <div style={{position:'absolute',left:92,top:530,width:960,height:240,overflow:'hidden',boxShadow:`0 0 0 4px ${C.blue}`,transform:`translateY(${(1-t)*25}px)`}}><OffthreadVideo muted src={staticFile('media/native.mp4')} style={{position:'absolute',width:1626.6666667,height:2160,left:-346.6666667,top:-1386.6666667}}/></div>
 <div style={{position:'absolute',left:1185,top:100,fontSize:24}}>Native camera + display composite</div>
 <OffthreadVideo muted src={staticFile('media/native.mp4')} style={{position:'absolute',left:1185,top:145,width:635,height:844}}/>
 <Text x={92} y={825} size={29} width={1000} style={{fontWeight:450,lineHeight:1.4,letterSpacing:0}}>Actual Arabic and English from the source frames.<br/>Enlarged for this video. No generated device output.</Text>
 <div style={{position:'absolute',left:1185,top:1010,fontSize:22}}>Earlier prototype footage · original speed</div>
 <Corner>Source: supplied native display capture · this is a replay</Corner>
 </>};
const Opening=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{backgroundColor:C.paper,color:C.ink,fontFamily:'Arial, Helvetica, sans-serif',overflow:'hidden'}}>
 <div style={{position:'absolute',inset:26,border:`1px solid ${C.ink}18`,pointerEvents:'none'}}/>
 {f<240?<Listen f={f}/>:f<timeline.scenes[1][2]?<Familiar f={f}/>:f<timeline.scenes[2][2]?<Scale f={f}/>:f<840?<Phone f={f}/>:<Sequence from={840} durationInFrames={240}><Replay f={f-840}/></Sequence>}
 <div style={{position:'absolute',left:0,bottom:0,height:5,width:`${f/1079*100}%`,background:C.red}}/>
 </AbsoluteFill>};
registerRoot(()=><Composition id="ProblemOpening" component={Opening} durationInFrames={1080} fps={30} width={1920} height={1080}/>);
