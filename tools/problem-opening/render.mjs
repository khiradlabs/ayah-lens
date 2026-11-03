import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import path from 'node:path';
const out=path.resolve('../../build/video-v0.3-opening');
const storyboard=process.argv.includes('--storyboard-only');
const serveUrl=await bundle({entryPoint:path.resolve('index.jsx'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try {
 const common={serveUrl,browserInstance:browser,logLevel:'warn'};
 const composition=await selectComposition({...common,id:'ProblemOpening'});
 if(storyboard){for(const frame of [30,150,285,390,585,720,795,930]){
   await renderStill({...common,composition,frame,output:path.join(out,`storyboard-${frame}.png`)});
   console.log(`STILL ${frame}`);
 }} else {
 await renderMedia({...common,composition,codec:'h264',crf:15,pixelFormat:'yuv420p',concurrency:3,outputLocation:path.join(out,'picture.mp4'),onProgress:({progress})=>{if(Math.round(progress*100)%10===0)process.stdout.write(`\rRender ${Math.round(progress*100)}%`);}});
 }
} finally {await browser.close({silent:true});}
