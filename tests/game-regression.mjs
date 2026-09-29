// Runs gameplay against actual Three.js math/geometry with a stub renderer.
// THREE_CORE points to three@0.180.0/build/three.core.js (saved as .mjs).
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const core=await import(pathToFileURL(process.env.THREE_CORE));
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
let source=html.split('<script type="module">')[1].split('</script>')[0].replace(/^import .*;$/gm,'');
const nodes=new Map(),makeNode=()=>({style:{},dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return true;}},getContext(){return {createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4)}),putImageData(){},fillRect(){}}}});
const document={querySelector(s){if(!nodes.has(s))nodes.set(s,makeNode());return nodes.get(s);},querySelectorAll(){return [];},createElement:makeNode};
class Renderer{constructor(){this.domElement=makeNode();this.shadowMap={};}setPixelRatio(){}setSize(){}}
class Controls{constructor(){this.isLocked=true;}addEventListener(){}lock(){this.isLocked=true;}unlock(){this.isLocked=false;}}
class Composer{addPass(){}render(){}setSize(){}}
const storage=new Map();
const context=vm.createContext({THREE:{...core,WebGLRenderer:Renderer},document,PointerLockControls:Controls,EffectComposer:Composer,RenderPass:class{},UnrealBloomPass:class{},devicePixelRatio:1,innerWidth:1440,innerHeight:900,performance,Math,Number,JSON,Float32Array,localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v)},addEventListener(){},requestAnimationFrame(){},setTimeout(){}});
vm.runInContext(source+`;globalThis.game={camera,keys,movePlayer,playerBlocked,scene,flashlight,missions,readSave,interact,useTool,mcur,controls,getCoins:()=>coins,setStarted:()=>{started=true},setMode:m=>{mode=m;missionIndex=0},marker,placeObjective,save,saved};`,context);
const g=context.game;
for(const [key,axis,sign] of [['KeyW','z',-1],['KeyS','z',1],['KeyA','x',-1],['KeyD','x',1]]){g.camera.position.set(0,1.68,8.8);for(const k in g.keys)delete g.keys[k];g.keys[key]=true;g.movePlayer(.1);const delta=g.camera.position[axis]-(axis==='z'?8.8:0);assert.ok(Number.isFinite(delta)&&delta*sign>0,key);}
assert.ok(g.playerBlocked(new core.Vector3(13,1.68,0)),'exterior walls block');
assert.ok(!g.playerBlocked(new core.Vector3(0,1.68,8.8)),'floor does not block player');
assert.ok(g.scene.children.includes(g.camera),'camera flashlight is attached');
assert.equal(g.missions.flat().length,750);
g.setStarted();g.setMode(0);g.placeObjective();g.camera.position.copy(g.marker.position);g.useTool();assert.equal(g.getCoins(),100);g.controls.lock();g.useTool();assert.equal(g.getCoins(),100,'no repeat reward');
g.setMode(2);g.placeObjective();g.camera.position.set(0,1.68,2);g.interact();assert.equal(g.mcur().progress,0,'stairs do not complete seals');
storage.set('wraithSaveV2','{broken');assert.equal(g.readSave().coins,0,'corrupt save recovery');
storage.set('wraithSaveV2',JSON.stringify({coins:-90,progress:[900,-2,'invalid'],injectors:-2}));const safe=g.readSave();assert.equal(safe.coins,0);assert.equal(safe.progress[0],150);assert.equal(safe.progress[1],0);
console.log('PASS: initialization, WASD directions, collisions, flashlight, 750 entries, objective reward guard, stairs isolation, save recovery.');
