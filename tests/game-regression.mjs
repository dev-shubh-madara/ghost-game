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
vm.runInContext(source+`;globalThis.game={camera,keys,movePlayer,playerBlocked,scene,flashlight,missions,readSave,interact,useTool,mcur,controls,ghost,updateGhost,streamWorld,chunkMap,jump,inSanctuary,note,marker,placeObjective,getCoins:()=>coins,setStarted:()=>{started=true},setMode:m=>{mode=m;missionIndex=0},setTool:i=>activeTool=i,setFeet:y=>{feetY=y;floor=y>=2.7?1:0;grounded=true;velocityY=0;camera.position.y=y+1.68},getFeet:()=>feetY,getGrounded:()=>grounded,save,saved};`,context);
const g=context.game;
function resetKeys(){for(const k in g.keys)delete g.keys[k];}
for(const [key,axis,sign] of [['KeyW','z',-1],['KeyS','z',1],['KeyA','x',-1],['KeyD','x',1]]){g.camera.position.set(-1,1.68,8.8);g.setFeet(0);resetKeys();g.keys[key]=true;g.movePlayer(.1);const delta=g.camera.position[axis]-(axis==='z'?8.8:-1);assert.ok(Number.isFinite(delta)&&delta*sign>0,key);}
resetKeys();assert.ok(g.playerBlocked(new core.Vector3(500,1.68,0)),'1km boundary');assert.ok(!g.playerBlocked(new core.Vector3(0,1.68,8.8)),'clear spawn');
assert.ok(g.scene.children.includes(g.camera),'flashlight attached');assert.equal(g.missions.flat().length,750);
// Stairs climb by movement alone, then descend continuously.
g.camera.position.set(0,1.68,3.3);g.setFeet(0);g.keys.KeyW=true;for(let i=0;i<140;i++)g.movePlayer(.01);assert.ok(g.getFeet()>2.9,'walk upstairs');resetKeys();g.keys.KeyS=true;for(let i=0;i<145;i++)g.movePlayer(.01);assert.ok(g.getFeet()<.1,'walk downstairs');resetKeys();
g.camera.position.set(-2,1.68,8.8);g.setFeet(0);g.jump();g.movePlayer(.1);assert.ok(g.getFeet()>.1,'jump rises');for(let i=0;i<200;i++)g.movePlayer(.01);assert.ok(g.getGrounded()&&g.getFeet()===0,'jump lands');
// Wrong ordering cannot collect or reward the mission.
g.setStarted();g.setMode(0);g.placeObjective();g.camera.position.copy(g.marker.position);g.useTool();assert.equal(g.getCoins(),0);
g.camera.position.copy(g.note.position);g.interact();assert.equal(g.mcur().stage,1,'hint required');g.camera.position.copy(g.marker.position);g.useTool();assert.equal(g.getCoins(),0,'item must be picked up');g.interact();assert.equal(g.mcur().stage,2);g.camera.position.copy(g.marker.position);g.useTool();assert.equal(g.getCoins(),100,'correct complete chain');g.controls.lock();g.useTool();assert.equal(g.getCoins(),100,'reward idempotent');
// Ghost never appears at start or anywhere in the protected sanctuary.
g.camera.position.set(80,1.68,0);g.updateGhost(.1,30000);assert.equal(g.ghost.visible,false,'grace period');g.camera.position.set(0,1.68,8.8);g.updateGhost(.1,90000);assert.equal(g.ghost.visible,false,'sanctuary');g.camera.position.set(80,1.68,0);g.updateGhost(.1,90000);assert.equal(g.ghost.visible,true,'outside after grace');g.camera.position.set(0,4.68,8.8);g.updateGhost(.1,91000);assert.equal(g.ghost.visible,false,'upstairs sanctuary');
// The apparition ignores wall geometry while approaching the player.
g.camera.position.set(80,1.68,0);g.updateGhost(.1,100000);g.ghost.position.set(95,.08,0);const ghostBefore=g.ghost.position.x;g.updateGhost(1,101000);assert.ok(g.ghost.position.x<ghostBefore,'ghost phases through scenery');
const slab=g.scene.children.find(o=>o.geometry?.type==='ShapeGeometry');slab.geometry.computeBoundingBox();assert.equal(slab.geometry.boundingBox.max.x-slab.geometry.boundingBox.min.x,1000,'upper floor width');assert.equal(slab.geometry.boundingBox.max.y-slab.geometry.boundingBox.min.y,1000,'upper floor depth');
// Stream both extreme edges and limit active sectors.
for(const x of [-480,0,480]){g.camera.position.set(x,1.68,x);g.streamWorld(true);assert.ok(g.chunkMap.size<=25);assert.ok(g.chunkMap.size>=9);}
storage.set('wraithSaveV2','{broken');assert.equal(g.readSave().coins,0);storage.set('wraithSaveV2',JSON.stringify({coins:-90,progress:[900,-2,'invalid']}));assert.equal(g.readSave().progress[0],150);
console.log('PASS: WASD, 1km bounds, stairs up/down without E, jump/landing, hint-item-objective order, reward protection, ghost grace/safe zone on both floors, bounded sector streaming, save recovery.');
