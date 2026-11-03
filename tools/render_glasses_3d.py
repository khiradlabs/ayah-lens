#!/usr/bin/env python3
"""Render an original reference-guided glasses mesh with local Three.js/Chrome.

The ignored build folder holds free npm dependencies and every generated asset.
This model is an editorial approximation, not manufacturer CAD.
"""
import argparse
import functools
import http.server
import json
from pathlib import Path
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build/video-v0.2'
WORK = BUILD / '3d'

SCENE = r'''<!doctype html><html><head><style>body{margin:0;overflow:hidden}canvas{display:block}</style></head><body>
<script type="importmap">{"imports":{"three":"/3d/node_modules/three/build/three.module.js","three/addons/":"/3d/node_modules/three/examples/jsm/"}}</script>
<script type="module">
import * as T from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setSize(1920,1080); renderer.setPixelRatio(1);
renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1;
renderer.outputColorSpace=T.SRGBColorSpace;document.body.appendChild(renderer.domElement);
const scene=new T.Scene();scene.background=new T.Color('#F3EFE5');
const env=new T.PMREMGenerator(renderer);scene.environment=env.fromScene(new RoomEnvironment(),0.04).texture;
const camera=new T.PerspectiveCamera(30,1920/1080,1,2000);
camera.position.set(126,94,345);camera.lookAt(0,0,-54);
camera.setViewOffset(1920,1080,-320,5,1920,1080);
scene.add(new T.HemisphereLight(0xfff8ec,0x767c89,1.2));
const key=new T.DirectionalLight(0xfff6e8,2.4);key.position.set(-150,210,180);scene.add(key);
const rim=new T.DirectionalLight(0xc9dcf3,1.8);rim.position.set(170,80,-170);scene.add(rim);
const fill=new T.DirectionalLight(0xffffff,.9);fill.position.set(0,-50,250);scene.add(fill);
const product=new T.Group();scene.add(product);
const black=new T.MeshPhysicalMaterial({color:0x101112,roughness:.36,specularIntensity:.12,metalness:0,clearcoat:.08,clearcoatRoughness:.3,envMapIntensity:.04});
const innerBlack=new T.MeshPhysicalMaterial({color:0x171818,roughness:.35,metalness:.08,clearcoat:.7});
const darkGlass=new T.MeshPhysicalMaterial({color:0x09131b,roughness:.08,metalness:.3,clearcoat:1});
const steel=new T.MeshStandardMaterial({color:0x606064,roughness:.31,metalness:.75});
const lensMaterial=new T.MeshPhysicalMaterial({color:0xcbd7d4,roughness:.08,metalness:0,transmission:.94,thickness:1.5,ior:1.52,transparent:true,opacity:.4,side:T.DoubleSide,depthWrite:false,envMapIntensity:.65});
const parts=[];
function add(name,geo,mat=black){const m=new T.Mesh(geo,mat);m.name=name;product.add(m);parts.push(m);return m;}
function shape(side=1,scale=1){
 const s=new T.Shape();const p=(x,y)=>[side*x*scale,y*scale];
 s.moveTo(...p(-24,16));s.bezierCurveTo(...p(-18,22),...p(12,23),...p(26,18));
 s.bezierCurveTo(...p(29,16),...p(28,10),...p(25,-2));
 s.lineTo(...p(20,-17));s.bezierCurveTo(...p(18,-23),...p(5,-24),...p(-7,-22));
 s.bezierCurveTo(...p(-17,-21),...p(-20,-15),...p(-23,-5));
 s.bezierCurveTo(...p(-26,5),...p(-27,12),...p(-24,16));return s;
}
function extrude(s,depth,bevel=1){return new T.ExtrudeGeometry(s,{depth,bevelEnabled:true,bevelSegments:4,steps:1,bevelSize:bevel,bevelThickness:bevel,curveSegments:28});}
for(const side of [-1,1]){
 const s=shape(side);const hole=shape(side,.805);s.holes.push(new T.Path(hole.getPoints(120).reverse()));
 const frame=add('lens_rim_'+side,extrude(s,6,1.05));frame.position.set(side*32,0,0);frame.rotation.y=side*-.045;
 const lens=add('lens_'+side,extrude(shape(side,.79),.75,.25),lensMaterial);lens.position.set(side*32,0,3);lens.rotation.y=side*-.045;
 // Brow wing and the unusually tall electronics housings distinguish Display.
 const wing=new T.Shape();wing.moveTo(58,23);wing.lineTo(71,22);wing.quadraticCurveTo(75,19,74,10);wing.lineTo(64,7);wing.lineTo(59,11);wing.closePath();
 const wg=extrude(wing,10,1);if(side<0){wg.scale(-1,1,1);const a=wg.attributes.position;for(let i=0;i<a.count;i+=3){for(let j=0;j<3;j++){const v=a.getComponent(i+1,j);a.setComponent(i+1,j,a.getComponent(i+2,j));a.setComponent(i+2,j,v);}}wg.computeVertexNormals();}
 add('brow_wing_'+side,wg);
 // Side silhouette drawn in the z/y plane, then extruded across x.
 const t=new T.Shape();t.moveTo(0,21);t.lineTo(57,20);t.quadraticCurveTo(77,19,91,12);
 t.quadraticCurveTo(102,7,109,-8);t.lineTo(118,-29);t.quadraticCurveTo(120,-35,116,-36);
 t.quadraticCurveTo(112,-36,111,-31);t.lineTo(102,-9);t.quadraticCurveTo(95,2,86,2);
 t.lineTo(56,4);t.lineTo(4,6);t.quadraticCurveTo(0,7,0,10);t.closePath();
 const temple=add('temple_'+side,extrude(t,6.5,1.15));
 temple.rotation.y=Math.PI/2;temple.position.set(side*70-3.25,0,-4);
 // Geometry maps local horizontal to negative depth; temples remain open.
 const seam=add('hinge_'+side,new T.BoxGeometry(.45,15,9),steel);seam.position.set(side*72.8,14,-4);
 const pad=add('nose_support_'+side,new T.SphereGeometry(1,24,16),innerBlack);pad.scale.set(3.5,8,3);pad.position.set(side*10,-1,-4);pad.rotation.z=side*.22;
 // A narrow side inset indicates a physical touch surface without invented text.
 const touch=add('temple_inset_'+side,new T.BoxGeometry(.15,9.5,32),innerBlack);touch.position.set(side*74.6,13,-31);
 const mic=add('microphone_'+side,new T.SphereGeometry(.55,12,8),darkGlass);mic.position.set(side*74.8,7,-40);
}
const bridgeShape=new T.Shape();bridgeShape.moveTo(-13,17);bridgeShape.quadraticCurveTo(0,22,13,17);bridgeShape.lineTo(12,9);bridgeShape.quadraticCurveTo(0,17,-12,9);bridgeShape.closePath();
add('bridge',extrude(bridgeShape,7,.9));
function disk(name,x,y,r,z,material){const m=add(name,new T.CylinderGeometry(r,r,1.1,48),material);m.rotation.x=Math.PI/2;m.position.set(x,y,z);return m;}
// Front view: one camera at viewer-left, unlike the opposite opal capture LED.
disk('camera_bezel',-66.4,16,2.85,11.1,steel);disk('camera',-66.4,16,2.2,11.8,darkGlass);
disk('camera_optic',-66.4,16,1.18,12.4,new T.MeshPhysicalMaterial({color:0x132c3b,roughness:.04,metalness:.45,clearcoat:1}));
disk('indicator_bezel',66.4,16,2.5,11.1,innerBlack);
disk('indicator',66.4,16,1.65,11.8,new T.MeshPhysicalMaterial({color:0xbbbdb6,roughness:.28,metalness:.1,clearcoat:1}));
// The right-lens display combiner is a faint physical coating, never a fake UI.
const combiner=add('right_lens_combiner',new T.PlaneGeometry(12,15),new T.MeshPhysicalMaterial({color:0xadb8bb,transparent:true,opacity:.08,roughness:.1,metalness:.4,side:T.DoubleSide,depthWrite:false}));combiner.position.set(-44,-3,4);
// All triangles are original procedural geometry; no imported meshes or photos.
function frame(n,centered=false){
 const phase=n/360*Math.PI*2;
 product.rotation.set(.025*Math.sin(phase),-.20+.36*Math.sin(phase),-.025+.035*Math.sin(phase+.4));
 product.position.y=1.2*Math.sin(phase);
 camera.setViewOffset(1920,1080,centered?0:-320,centered?0:5,1920,1080);
 key.position.x=-150+45*Math.sin(phase+.6);scene.updateMatrixWorld(true);renderer.render(scene,camera);
 const box=new T.Box3().setFromObject(product);const projected=[];
 for(const m of parts){const a=m.geometry.attributes.position;for(let i=0;i<a.count;i+=1){const v=new T.Vector3().fromBufferAttribute(a,i).applyMatrix4(m.matrixWorld).project(camera);projected.push([(v.x+1)*960,(1-v.y)*540]);}}
 const xs=projected.map(p=>p[0]),ys=projected.map(p=>p[1]);
 const landmarks=[new T.Vector3(-66,16,12),new T.Vector3(66,16,12),new T.Vector3(72,12,-80)].map(v=>v.applyMatrix4(product.matrixWorld).project(camera).toArray());
 return {frame:n,bounds:[xs.reduce((a,b)=>Math.min(a,b),Infinity),ys.reduce((a,b)=>Math.min(a,b),Infinity),xs.reduce((a,b)=>Math.max(a,b),-Infinity),ys.reduce((a,b)=>Math.max(a,b),-Infinity)],landmarks,worldDepth:box.max.z-box.min.z};
}
window.renderFrame=frame;
window.meshReceipt=()=>({parts:parts.map(m=>({name:m.name,vertices:m.geometry.attributes.position.count,triangles:m.geometry.index?m.geometry.index.count/3:m.geometry.attributes.position.count/3})),localDepth:new T.Box3().setFromObject(product).getSize(new T.Vector3()).z});
window.meshJSON=()=>product.toJSON();window.ready=true;frame(0);
</script></body></html>'''

RUNNER = r'''
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const [url,out,check]=process.argv.slice(2);
const browser=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--no-sandbox','--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage','--hide-scrollbars']});
try {
const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
page.on('pageerror',e=>console.error(e));await page.goto(url);await page.waitForFunction('window.ready===true',{timeout:60000});
const receipt={mesh:await page.evaluate(()=>window.meshReceipt()),shots:[]};
fs.writeFileSync(out+'/mesh.json',JSON.stringify(await page.evaluate(()=>window.meshJSON())));
for(const n of [0,90,180,270]){
 receipt.shots.push(await page.evaluate(n=>window.renderFrame(n),n));await page.screenshot({path:out+'/preview-'+n+'.png'});
}
await page.evaluate(()=>window.renderFrame(0,true));await page.screenshot({path:out+'/full-product.png'});
fs.writeFileSync(out+'/receipt.json',JSON.stringify(receipt,null,2));
if(check!=='check')for(let n=0;n<360;n++){
 await page.evaluate(n=>window.renderFrame(n),n);await page.screenshot({path:out+'/frames/'+String(n).padStart(4,'0')+'.png'});
 if(n%60===0)console.log('Rendered frame '+n+'/360');
}
} finally {await browser.close();}
'''

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def verify(receipt):
    parts = receipt['mesh']['parts']
    names = [p['name'] for p in parts]
    assert sum(n.startswith('lens_rim_') for n in names) == 2, 'Expected two volumetric lens rims'
    assert names.count('camera') == 1, 'Expected one camera, not a mirrored pair'
    assert names.count('indicator') == 1, 'Expected one opposite-side capture indicator'
    assert receipt['mesh']['localDepth'] > 100, 'Expected temples extending in genuine 3D depth'
    assert sum(p['triangles'] for p in parts) > 10000, 'Expected real curved surface geometry'
    shots = receipt['shots']
    assert abs(shots[1]['landmarks'][2][0] - shots[3]['landmarks'][2][0]) > .05, 'Perspective must change with object rotation'
    for shot in shots:
        x0,y0,x1,y1=shot['bounds']
        assert x0 >= 780 and x1 <= 1900, f'Product overlaps typography or frame: {shot}'
        assert y0 >= 220 and y1 <= 920, f'Product leaves safe vertical region: {shot}'
    from PIL import Image, ImageChops, ImageStat
    a=Image.open(WORK/'preview-90.png').convert('RGB')
    b=Image.open(WORK/'preview-270.png').convert('RGB')
    difference=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)
    assert difference > 2, 'Rendered frames must change, not merely metadata'
    assert a.getpixel((100,100)) == (243,239,229), 'Paper background must match editorial palette'
    print(json.dumps({'result':'PASS','mesh_parts':len(parts),'triangles':int(sum(p['triangles'] for p in parts)), 'depth_mm':round(receipt['mesh']['localDepth'],2),'frame_pixel_difference':round(difference,3),'shot_bounds':[s['bounds'] for s in shots]},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Render and validate four views plus full-product preview')
    args=parser.parse_args()
    WORK.mkdir(parents=True,exist_ok=True)
    if not (WORK/'node_modules/three').exists() or not (WORK/'node_modules/puppeteer-core').exists():
        raise SystemExit('Install free local dependencies: npm install --prefix build/video-v0.2/3d three puppeteer-core')
    (WORK/'scene.html').write_text(SCENE)
    (WORK/'render.mjs').write_text(RUNNER)
    (WORK/'frames').mkdir(exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(BUILD)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        subprocess.run(['node',str(WORK/'render.mjs'),f'http://127.0.0.1:{server.server_port}/3d/scene.html',str(WORK),'check' if args.check else 'render'],check=True)
    finally:
        server.shutdown();server.server_close()
    verify(json.loads((WORK/'receipt.json').read_text()))
    if not args.check:
        assets=BUILD/'assets';assets.mkdir(exist_ok=True)
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(WORK/'frames/%04d.png'),'-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(assets/'glasses-turntable.mp4')],check=True)
        print('Rendered:',assets/'glasses-turntable.mp4')

if __name__=='__main__':
    main()
