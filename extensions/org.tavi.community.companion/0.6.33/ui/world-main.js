'use strict';
(()=>{
const __modules=Object.create(null);
const __inlineConfigurations={"cat-clips.json":{"idle":{"schema":1,"rig":"cat-v1","duration":4,"loop":true,"tracks":[{"part":"torso","channel":"y","keys":[[0,0],[2,-1],[4,0]]},{"part":"head","channel":"y","keys":[[0,0],[2,-1],[4,0]]},{"part":"tail","channel":"angle","keys":[[0,-5],[2,7],[4,-5]]},{"part":"earRight","channel":"angle","keys":[[0,0],[2.8,0],[3,12],[3.2,0],[4,0]]}]},"walk":{"schema":1,"rig":"cat-v1","duration":0.8,"loop":true,"tracks":[{"part":"torso","channel":"y","keys":[[0,0],[0.2,-1],[0.4,0],[0.6,-1],[0.8,0]]},{"part":"torso","channel":"angle","keys":[[0,3],[0.8,3]]},{"part":"legLeft","channel":"x","keys":[[0,-7],[0.4,7],[0.8,-7]]},{"part":"legRight","channel":"x","keys":[[0,7],[0.4,-7],[0.8,7]]},{"part":"legLeft","channel":"y","keys":[[0,0],[0.2,-5],[0.4,0],[0.8,0]]},{"part":"legRight","channel":"y","keys":[[0,0],[0.4,0],[0.6,-5],[0.8,0]]},{"part":"armLeft","channel":"angle","keys":[[0,-8],[0.4,8],[0.8,-8]]},{"part":"armRight","channel":"angle","keys":[[0,8],[0.4,-8],[0.8,8]]},{"part":"forearmLeft","channel":"angle","keys":[[0,6],[0.4,-4],[0.8,6]]},{"part":"forearmRight","channel":"angle","keys":[[0,-4],[0.4,6],[0.8,-4]]},{"part":"tail","channel":"angle","keys":[[0,-5],[0.4,5],[0.8,-5]]}]},"wave":{"schema":1,"rig":"cat-v1","duration":2.4,"loop":false,"tracks":[{"part":"armRight","channel":"angle","keys":[[0,0],[0.4,-115],[1.7,-115],[2.4,0]]},{"part":"forearmRight","channel":"angle","keys":[[0,0],[0.4,-40],[0.7,-65],[1,-40],[1.3,-65],[1.6,-40],[1.8,-40],[2.4,0]]},{"part":"head","channel":"angle","keys":[[0,0],[0.5,-6],[1.8,-6],[2.4,0]]},{"part":"tail","channel":"angle","keys":[[0,0],[1,9],[2.4,0]]}]}},"cat-painted-layout.json":{"schema":1,"species":"cat","colors":{"label":"Cat colors","defaultPreset":"ginger","preserveDefaults":true,"defaults":{"coat":"#dba36a","markings":"#ac6038","cream":"#fae4b6","innerEar":"#dca6ab"},"channels":[{"id":"coat","label":"Fur"},{"id":"markings","label":"Stripes"},{"id":"cream","label":"Muzzle & paws"},{"id":"innerEar","label":"Inner ears"}],"presets":{"ginger":{"label":"Ginger","colors":{"coat":"#dba36a","markings":"#ac6038","cream":"#fae4b6","innerEar":"#dca6ab"}},"silver":{"label":"Silver","colors":{"coat":"#a8adb8","markings":"#53606d","cream":"#f2ecdf","innerEar":"#cf9da8"}},"lavender":{"label":"Lavender","colors":{"coat":"#b497ca","markings":"#6d527d","cream":"#f2e8e7","innerEar":"#d6a3bd"}}},"materials":{"fur":[{"channel":"cream","hue":[30,65],"lightness":[0.78,0.98],"saturation":[0.18,1],"sourceLightness":0.85},{"channel":"markings","hue":[0,28],"lightness":[0.26,0.62],"saturation":[0.22,1],"sourceLightness":0.45},{"channel":"coat","hue":[10,58],"lightness":[0.26,0.96],"saturation":[0.2,1],"sourceLightness":0.64}],"earFur":[{"channel":"innerEar","hue":[330,360],"saturation":[0.12,1],"lightness":[0.35,0.94],"sourceLightness":0.76},{"channel":"innerEar","hue":[0,15],"saturation":[0.12,1],"lightness":[0.35,0.94],"sourceLightness":0.76},{"channel":"cream","hue":[30,65],"lightness":[0.78,0.98],"saturation":[0.18,1],"sourceLightness":0.85},{"channel":"markings","hue":[0,28],"lightness":[0.26,0.62],"saturation":[0.22,1],"sourceLightness":0.45},{"channel":"coat","hue":[10,58],"lightness":[0.26,0.96],"saturation":[0.2,1],"sourceLightness":0.64}]}},"width":1254,"height":1254,"parts":{"legSideLeft":{"atlas":"profileLegs","source":[77,19,142,218],"size":[25,32],"pivot":[9,10],"recolor":"fur"},"legSideRight":{"atlas":"profileLegs","source":[310,20,134,218],"size":[25,32],"pivot":[9,10],"recolor":"fur"},"earSideNear":{"atlas":"profileEars","source":[35,29,154,205],"size":[27,24],"pivot":[13.5,20],"recolor":"earFur"},"earSideFar":{"atlas":"profileEars","source":[247,66,104,168],"size":[12,18],"pivot":[6,16],"recolor":"earFur"},"front":{"source":[4,50,310,240],"size":[74,56],"pivot":[37,28],"recolor":"fur","protectedRegions":[{"center":[0.35,0.5],"radius":[0.085,0.14],"hue":[35,150]},{"center":[0.7,0.5],"radius":[0.085,0.14],"hue":[35,150]}]},"side":{"source":[346,49,276,241],"size":[74,56],"pivot":[37,28],"recolor":"fur","protectedRegions":[{"center":[0.73,0.49],"radius":[0.1,0.15],"hue":[35,150]}]},"front-blink":{"source":[627,50,314,238],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"side-blink":{"source":[960,49,286,241],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"torso-front":{"source":[36,324,278,292],"size":[57,66],"pivot":[28.5,33],"recolor":"fur"},"torso-side":{"source":[372,323,241,300],"size":[53,66],"pivot":[26.5,33],"recolor":"fur"},"armLeft":{"source":[704,348,141,253],"size":[20,42],"pivot":[10,5],"recolor":"fur"},"armRight":{"source":[1031,346,141,255],"size":[20,42],"pivot":[10,5],"recolor":"fur"},"legLeft":{"source":[74,635,170,270],"size":[25,32],"pivot":[12.5,10],"recolor":"fur"},"legRight":{"source":[410,635,168,270],"size":[25,32],"pivot":[12.5,10],"recolor":"fur"},"tail":{"source":[640,627,296,285],"size":[66,64],"pivot":[62,55],"recolor":"fur"},"earLeft":{"source":[1010,670,189,225],"size":[24,30],"pivot":[12,26],"recolor":"earFur"},"earRight":{"source":[74,955,194,224],"size":[24,30],"pivot":[12,26],"recolor":"earFur"},"happy":{"source":[314,941,313,245],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"curious":{"source":[630,941,311,247],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"sleepy":{"source":[941,941,313,247],"size":[74,56],"pivot":[37,28],"recolor":"fur"}},"atlases":{"profileLegs":{"width":512,"height":256},"profileEars":{"width":384,"height":256}}},"unicorn-layout.json":{"schema":1,"species":"unicorn","rig":"cat-v1","colors":{"label":"Unicorn colors","defaultPreset":"pearl","defaults":{"coat":"#e9e5df","mane":"#aa89d9","horn":"#e4bd6b","hooves":"#645275"},"channels":[{"id":"coat","label":"Coat"},{"id":"mane","label":"Mane & tail"},{"id":"horn","label":"Horn"},{"id":"hooves","label":"Hooves"}],"presets":{"pearl":{"label":"Pearl","colors":{"coat":"#e9e5df","mane":"#aa89d9","horn":"#e4bd6b","hooves":"#645275"}},"twilight":{"label":"Twilight","colors":{"coat":"#53617c","mane":"#d592bb","horn":"#efc575","hooves":"#40364f"}},"meadow":{"label":"Meadow","colors":{"coat":"#bfd1ae","mane":"#548e94","horn":"#e2c17a","hooves":"#526b57"}}},"materials":{"coat":[{"channel":"coat","chroma":[0,0.18],"lightness":[0.13,1],"sourceLightness":0.86}],"limb":[{"channel":"hooves","hue":[145,205],"saturation":[0.2,1],"lightness":[0.1,1],"sourceLightness":0.42},{"channel":"coat","chroma":[0,0.18],"lightness":[0.13,1],"sourceLightness":0.86}],"mane":[{"channel":"mane","lightness":[0.1,1],"sourceLightness":0.58}],"horn":[{"channel":"horn","lightness":[0.1,1],"sourceLightness":0.62}]}},"width":1280,"height":1024,"parts":{"front":{"source":[25,61,250,188],"size":[74,56],"pivot":[37,28],"recolor":"coat"},"side":{"source":[298,64,255,187],"size":[80,56],"pivot":[40,28],"recolor":"coat"},"front-blink":{"source":[556,62,251,187],"size":[74,56],"pivot":[37,28],"recolor":"coat"},"side-blink":{"source":[819,64,263,189],"size":[80,56],"pivot":[40,28],"recolor":"coat"},"horn":{"source":[1117,45,113,210],"size":[12,30],"pivot":[6,27],"recolor":"horn"},"torso-front":{"source":[25,267,263,253],"size":[57,66],"pivot":[28.5,33],"recolor":"coat"},"torso-side":{"source":[311,266,242,255],"size":[53,66],"pivot":[26.5,33],"recolor":"coat"},"armLeft":{"source":[581,282,155,233],"size":[20,42],"pivot":[10,5],"recolor":"limb"},"armRight":{"source":[809,281,153,234],"size":[20,42],"pivot":[10,5],"recolor":"limb"},"tail":{"source":[998,277,268,256],"size":[42,52],"pivot":[38,26],"recolor":"mane"},"legLeft":{"source":[51,531,164,229],"size":[25,32],"pivot":[12.5,10],"recolor":"limb"},"legRight":{"source":[314,531,166,229],"size":[25,32],"pivot":[12.5,10],"recolor":"limb"},"legSideLeft":{"source":[559,533,169,222],"size":[25,32],"pivot":[9,10],"recolor":"limb","placementOffset":[-7,0]},"legSideRight":{"source":[774,532,169,223],"size":[25,32],"pivot":[9,10],"recolor":"limb","placementOffset":[7,0]},"maneFront":{"atlas":"unicornMane","source":[34,68,224,120],"size":[56,23],"pivot":[28,31],"recolor":"mane","placementOffset":[0,1]},"earLeft":{"source":[39,773,177,216],"size":[16,36],"pivot":[8,32],"recolor":"coat"},"earRight":{"source":[310,772,177,216],"size":[16,36],"pivot":[8,32],"recolor":"coat"},"earSideNear":{"source":[545,767,154,229],"size":[15,32],"pivot":[7.5,28],"recolor":"coat"},"earSideFar":{"source":[782,772,175,224],"size":[11,27],"pivot":[5.5,24],"recolor":"coat"},"maneSide":{"atlas":"unicornMane","source":[59,226,147,252],"size":[31,82],"pivot":[41,27],"recolor":"mane","placementOffset":[2,0]},"maneSideForelock":{"atlas":"unicornMane","source":[294,66,191,132],"size":[44,20],"pivot":[22,32],"recolor":"mane","placementOffset":[0,1]},"maneFrontBack":{"atlas":"unicornMane","source":[297,312,168,133],"size":[60,34],"pivot":[30,14],"recolor":"mane"}},"atlases":{"unicornMane":{"width":512,"height":512}}}};
const __bundledJSON=async name=>{const key=String(name).replace(/^\.\//,'');if(!Object.hasOwn(__inlineConfigurations,key))throw Error('Unknown painted layout');return structuredClone(__inlineConfigurations[key]);};
const __loadBundledImage=async name=>{const chunks=globalThis.__taviCompanionImageChunks?.[name];if(!Array.isArray(chunks)||!chunks.length)throw Error('Missing painted artwork: '+name);const img=new Image();img.src='data:image/png;base64,'+chunks.join('');await img.decode();return img;};
// world/object-catalog.mjs
__modules["world/object-catalog.mjs"]=(()=>{
const __moduleURL=new URL("./world/object-catalog.mjs",document.baseURI).href;
// Tavi-authored, data-driven world objects. The supplied Creatures COBs are
// design references only: no third-party CAOS, binary assets or original rules
// are shipped or executed here.
const OBJECT_CATALOG_SCHEMA='tavi.world-objects/v1';
const NEEDS=new Set(['fullness','cleanliness','happiness','energy','affection']);
const allowedActions=new Set(['eat','sit','bathe','sleep','play']);

const entries=[
  {id:'snack',label:'Fruit bowl',room:'kitchen',x:230,category:'food',action:'eat',duration:6,effects:{fullness:22},need:'fullness'},
  {id:'table',label:'Dining table',room:'dining',x:710,category:'social',action:'sit',duration:6,effects:{affection:22},need:'affection'},
  {id:'honey',label:'Honey jar',room:'dining',x:870,category:'food',action:'eat',duration:4,effects:{fullness:15,happiness:5},need:'fullness',capacity:10,refillable:true},
  {id:'bath',label:'Warm spring',room:'bathroom',x:1190,category:'comfort',action:'bathe',duration:6,effects:{cleanliness:22,happiness:3},need:'cleanliness'},
  {id:'bed',label:'Little bed',room:'bedroom',x:1660,category:'rest',action:'sleep',duration:10,effects:{energy:22},need:'energy'},
  {id:'toy',label:'Garden ball',room:'garden',x:2140,category:'play',action:'play',duration:6,effects:{happiness:22},need:'happiness'},
];

function validateObjectCatalog(list){
  if(!Array.isArray(list)||!list.length)throw Error('Object catalog must be a nonempty array');
  const ids=new Set();
  for(const item of list){
    if(!/^[a-z][a-z0-9-]{1,39}$/.test(item.id??'')||ids.has(item.id))throw Error('Invalid or duplicate object ID');
    ids.add(item.id);
    if(typeof item.label!=='string'||!item.label.trim()||typeof item.room!=='string'||!item.room.trim()||!Number.isFinite(item.x)||item.x<0)throw Error('Invalid object placement');
    if(!allowedActions.has(item.action)||!Number.isFinite(item.duration)||item.duration<=0||item.duration>30)throw Error('Invalid object action');
    if(!NEEDS.has(item.need)||!item.effects||typeof item.effects!=='object')throw Error('Invalid object needs');
    for(const [need,value]of Object.entries(item.effects))if(!NEEDS.has(need)||!Number.isFinite(value)||value<0||value>100)throw Error('Invalid object effect');
    if(item.capacity!==undefined&&(!Number.isSafeInteger(item.capacity)||item.capacity<1||item.capacity>100))throw Error('Invalid object capacity');
    if(item.refillable&&!item.capacity)throw Error('Refillable object must have a capacity');
  }
  return true;
}
validateObjectCatalog(entries);
const objects=Object.freeze(entries.map(entry=>Object.freeze({...entry,effects:Object.freeze({...entry.effects})})));
const objectById=id=>objects.find(item=>item.id===id);
const initialObjectState=()=>Object.fromEntries(objects.filter(item=>item.capacity).map(item=>[item.id,{usesRemaining:item.capacity}]));
function isObjectAvailable(s,id){
  const obj=objectById(id);
  return Boolean(obj&&(!obj.capacity||(s.objectState?.[id]?.usesRemaining??obj.capacity)>0));
}
function refillObject(s,id){
  const obj=objectById(id);
  if(!obj?.refillable)return false;
  if(!s.objectState)s.objectState=initialObjectState();
  if(s.objectState[id]?.usesRemaining===obj.capacity)return false;
  s.objectState[id]={usesRemaining:obj.capacity};
  s.message=`The ${obj.label.toLowerCase()} has been refilled.`;
  return true;
}
function completeObjectUse(s,id){
  const obj=objectById(id);
  if(!isObjectAvailable(s,id))return false;
  for(const [need,benefit]of Object.entries(obj.effects))s.needs[need]=Math.max(0,Math.min(100,s.needs[need]+benefit));
  if(obj.capacity){
    const left=(s.objectState?.[id]?.usesRemaining??obj.capacity)-1;
    s.objectState[id]={usesRemaining:left};
    s.message=left>0?`Enjoyed some honey. ${left} servings remain.`:'Enjoyed the last honey. The jar is empty.';
  }
  return true;
}

return {OBJECT_CATALOG_SCHEMA,validateObjectCatalog,objects,objectById,initialObjectState,isObjectAvailable,refillObject,completeObjectUse};
})();
// world/genetics.mjs
__modules["world/genetics.mjs"]=(()=>{
const __moduleURL=new URL("./world/genetics.mjs",document.baseURI).href;
/**
 * Tavi companion adaptive genetics v2. The ONE creature's genes change during
 * its lifetime as a bounded, deterministic consequence of experienced events.
 * No breeding, parents, mating, pedigree or species appearance inference.
 * This is original simulation logic, NOT a decoder of Creatures .gen/.EXP.
 * Pure JSON API suitable for porting to Rust/native engine adapters.
 */
const GENOME_SCHEMA='tavi.companion.genome/v2';
const TRAIT_KEYS=Object.freeze(['curiosity','sociability','playfulness','calmness','appetite','stamina']);
const EVOLUTION_EVENTS=Object.freeze(['explore','play','rest','nourish','bathe','bond']);
const TRAITS=new Set(TRAIT_KEYS),EVENTS=new Set(EVOLUTION_EVENTS);
const record=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const match=(v,keys)=>record(v)&&Object.keys(v).length===keys.length&&Object.keys(v).every(k=>keys.includes(k));
const boundInt=(x,min,max)=>Number.isSafeInteger(x)&&x>=min&&x<=max;
const seedValid=x=>boundInt(x,0,0xffffffff);
const maxCount=1000000;
function seededRandom(seed){
  if(!seedValid(seed))throw Error('Invalid genetic seed');
  let state=seed>>>0;
  return ()=>{
    state=(state+0x6D2B79F5)>>>0;
    let t=state;
    t=Math.imul(t^(t>>>15),t|1);
    t^=t+Math.imul(t^(t>>>7),t|61);
    return ((t^(t>>>14))>>>0)/4294967296;
  };
}
function assemble(genes,revision=0,exposures=Object.fromEntries(EVOLUTION_EVENTS.map(e=>[e,0]))){
  const result={schema:GENOME_SCHEMA,revision,genes,exposures};validateGenome(result);return result;
}
function validateGenome(genome){
  if(!match(genome,['schema','revision','genes','exposures'])||genome.schema!==GENOME_SCHEMA||!boundInt(genome.revision,0,maxCount)||!match(genome.genes,TRAIT_KEYS)||!match(genome.exposures,EVOLUTION_EVENTS))throw Error('Invalid adaptive genome');
  if(TRAIT_KEYS.some(key=>!boundInt(genome.genes[key],0,510)))throw Error('Invalid adaptive gene');
  if(EVOLUTION_EVENTS.some(key=>!boundInt(genome.exposures[key],0,maxCount)))throw Error('Invalid evolution exposure');
  const total=EVOLUTION_EVENTS.reduce((sum,key)=>sum+genome.exposures[key],0);
  if(total!==genome.revision)throw Error('Evolution revision / exposure mismatch');
  return true;
}
function neutralGenome(){return assemble(Object.fromEntries(TRAIT_KEYS.map(key=>[key,256])));}
function createGenome(seed=0x54415649){
  const next=seededRandom(seed);
  return assemble(Object.fromEntries(TRAIT_KEYS.map(key=>[key,Math.floor(next()*511)])));
}
function phenotypeFor(genome){
  validateGenome(genome);
  return Object.fromEntries(TRAIT_KEYS.map(key=>[key,genome.genes[key]/510]));
}
function traitFor(world,key){
  if(!TRAITS.has(key))throw Error('Unknown companion trait');
  return world?.phenotype?.[key]??0.5;
}
// Change applies only after a completed experience, never because time passed.
// Repeated events have diminishing influence but are still bounded and auditable.
const CHANGES=Object.freeze({
  explore:{curiosity:4,calmness:-1},
  play:{playfulness:5,curiosity:2,stamina:1},
  rest:{calmness:3,stamina:4},
  nourish:{appetite:2,calmness:1},
  bathe:{calmness:4},
  bond:{sociability:5,calmness:1},
});
function evolveGenome(genome,event){
  validateGenome(genome);
  if(!EVENTS.has(event))throw Error('Unknown evolution event');
  if(genome.revision===maxCount||genome.exposures[event]===maxCount)return structuredClone(genome);
  const exposures={...genome.exposures,[event]:genome.exposures[event]+1};
  const count=exposures[event];
  const scale=count<=4?1:count<=12?0.75:count<=32?0.5:0.25;
  const genes={...genome.genes};
  for(const [key,base] of Object.entries(CHANGES[event])){
    const diff=Math.sign(base)*Math.max(1,Math.round(Math.abs(base)*scale));
    genes[key]=Math.max(0,Math.min(510,genes[key]+diff));
  }
  return assemble(genes,genome.revision+1,exposures);
}
function evolveCompanion(world,event){
  if(!world||!record(world))throw Error('Invalid evolving companion');
  const next=evolveGenome(world.genome,event);
  if(next.revision===world.genome.revision)return false;
  world.genome=next;
  world.phenotype=phenotypeFor(next);
  return true;
}

return {GENOME_SCHEMA,TRAIT_KEYS,EVOLUTION_EVENTS,seededRandom,validateGenome,neutralGenome,createGenome,phenotypeFor,traitFor,evolveGenome,evolveCompanion};
})();
// world/creature-profile.mjs
__modules["world/creature-profile.mjs"]=(()=>{
const __moduleURL=new URL("./world/creature-profile.mjs",document.baseURI).href;
// Session-local creature personality, separate from painted character choice.
// This is a Tavi design contract, NOT a decoded Creatures .GEN/.EXP genome.
const {traitFor}=__modules["world/genetics.mjs"];
const {objects}=__modules["world/object-catalog.mjs"];
const PROFILE_SCHEMA='tavi.creature-profile/v3';
const HABIT_CAP=24;
const ASSOCIATION_CAP=24;
const EVIDENCE_CAP=50;
const OUTCOMES=Object.freeze(['pleasant','disappointing','unfamiliar']);
const validObjectIds=new Set(objects.map(o=>o.id));
const neutralAssociation=()=>({score:0,pleasant:0,disappointing:0,unfamiliar:0});
const bound=(v,min,max)=>Math.max(min,Math.min(max,v));
const PERSONALITY_KEYS=Object.freeze(['curiosity','sociability','playfulness','calmness']);
function createProfile(preferences={}){
  const profile={schema:PROFILE_SCHEMA,preferences:{},experience:{},habits:{},associations:{}};
  for(const [id,value]of Object.entries(preferences)){
    if(!/^[a-z][a-z0-9-]{1,39}$/.test(id)||!Number.isFinite(value)||value< -1||value>1)throw Error('Invalid companion preference');
    profile.preferences[id]=value;
  }
  return profile;
}
function preferenceFor(state,id){
  const value=state.profile?.preferences?.[id];
  return Number.isFinite(value)?Math.max(-1,Math.min(1,value)):0;
}
/** The effect that actually occurred, rather than the action requested, teaches
 * the companion what felt satisfying. First helpful uses are unfamiliar, then
 * subsequent rewarding uses become pleasant; low-benefit uses can disappoint.
 * All three outcomes are gentle labels, not claims of sentience or distress.
 */
function classifyConsequence({previousVisits=0,needBefore=0,needAfter=0,secondaryGain=0}={}){
  const gain=Math.max(0,needAfter-needBefore)+Math.max(0,secondaryGain)*0.25;
  if(!Number.isFinite(gain))throw Error('Invalid outcome benefit');
  if(gain<4)return 'disappointing';
  return previousVisits===0?'unfamiliar':'pleasant';
}
function validateAssociation(value){
  if(!value||typeof value!=='object'||Array.isArray(value))return false;
  const keys=['score',...OUTCOMES];
  if(Object.keys(value).length!==keys.length||!keys.every(k=>Object.hasOwn(value,k)))return false;
  return Number.isSafeInteger(value.score)&&Math.abs(value.score)<=ASSOCIATION_CAP
    && OUTCOMES.every(k=>Number.isSafeInteger(value[k])&&value[k]>=0&&value[k]<=EVIDENCE_CAP);
}
function associationFor(s,id){
  const value=s.profile?.associations?.[id];
  return validateAssociation(value)?value:neutralAssociation();
}
function learnConsequence(s,id,outcome){
  if(!validObjectIds.has(id)||!OUTCOMES.includes(outcome))throw Error('Invalid companion outcome');
  if(!s.profile?.associations)throw Error('Missing companion learning state');
  const previous=associationFor(s,id),next={...previous};
  next[outcome]=Math.min(EVIDENCE_CAP,next[outcome]+1);
  // A previous impression is revisable. No object becomes permanently forbidden.
  next.score=bound(next.score+(outcome==='pleasant'?4:outcome==='disappointing'?-5:0),-ASSOCIATION_CAP,ASSOCIATION_CAP);
  s.profile.associations[id]=next;
  return next;
}
function describeConsequences(s,items){
  return items.filter(o=>s.profile?.associations?.[o.id]&&validateAssociation(s.profile.associations[o.id]))
    .map(o=>({id:o.id,label:o.label,...associationFor(s,o.id)}))
    .sort((a,b)=>Math.abs(b.score)-Math.abs(a.score)||
      (b.pleasant+b.disappointing+b.unfamiliar)-(a.pleasant+a.disappointing+a.unfamiliar)||a.id.localeCompare(b.id))
    .slice(0,6);
}
/** A habit only forms after an actual completed object interaction.
 * The need BEFORE the effect and the individual's present phenotype inform
 * reinforcement; simple activity repetition cannot invent a need penalty.
 * Positive preferences are bounded and never prevent trying other objects.
 */
function habitFor(s,id){
  const value=s.profile?.habits?.[id];
  return Number.isSafeInteger(value)?bound(value,0,HABIT_CAP):0;
}
function rememberExperience(s,id,{needBefore=85,action='',outcome='unfamiliar'}={}){
  if(!s.profile?.experience)return;
  const previous=s.profile.experience[id]??0;
  s.profile.experience[id]=Math.min(50,previous+1);
  if(!s.profile.habits)s.profile.habits={};
  const trait=action==='play'?'playfulness':action==='sit'?'sociability':action==='sleep'?'stamina':action==='eat'?'appetite':'calmness';
  const affinity=traitFor(s,trait);
  const need=Math.max(0,Math.min(100,Number.isFinite(needBefore)?needBefore:85));
  const novelty=previous>=12?1:previous>=4?2:3;
  const reward=(need<55?2:need<80?1:0)+(affinity>=.7?1:0);
  // Unrewarding activities should not create a strong favorite through mere
  // repetition. Existing habits can be revised without erasing the visit.
  const gain=outcome==='disappointing'?-Math.min(4,2+Math.floor(previous/4))
    :outcome==='unfamiliar'?1:Math.min(5,novelty+reward);
  s.profile.habits[id]=bound(habitFor(s,id)+gain,0,HABIT_CAP);
  learnConsequence(s,id,outcome);
}
function describeHabits(s,items){
  return items.filter(o=>(s.profile?.experience?.[o.id]??0)>=2 && habitFor(s,o.id)>0)
    .map(o=>({id:o.id,label:o.label,affinity:habitFor(s,o.id),visits:s.profile.experience[o.id]}))
    .sort((a,b)=>b.affinity-a.affinity||b.visits-a.visits||a.id.localeCompare(b.id))
    .slice(0,3);
}
/** Inspectable activity outlook that shares its *exact* weighting with autonomy.
 * This is a projection, not a promise about the next random draw. No mutation,
 * storage I/O, or host API calls are made when showing it to the player.
 */
function activityOutlook(s,candidates){
  if(!Array.isArray(candidates)||!candidates.length)return [];
  const inCare=s.care===true;
  const outlook=candidates.map(item=>{
    const past=associationFor(s,item.id),habit=habitFor(s,item.id);
    const preference=preferenceFor(s,item.id);
    const curiosity=traitFor(s,'curiosity');
    const need=Math.max(0,Math.min(100,s.needs[item.need]??100));
    const score=inCare
      ?100-need+preference*10+(item.action==='play'?traitFor(s,'playfulness')*4:0)+habit*.4+past.score*.2
      :Math.max(.25,(1+preference)*(1+curiosity*(s.visits?.[item.id]?0:.5))
        *(item.action==='play'?.6+traitFor(s,'playfulness')*.8:1)
        *(item.action==='sleep'?1.2-traitFor(s,'calmness')*.4:1)
        *(1+habit/40)*(1+past.score/40));
    let reason;
    if(inCare&&need<55)reason='A little care would help';
    else if(past.score>=8)reason='Happy memories here';
    else if(habit>=8)reason='A familiar favorite';
    else if(!s.visits?.[item.id]&&curiosity>=.5)reason='Something new to discover';
    else if(preference>=.4)reason='An activity they enjoy';
    else if(past.score<=-8)reason='Giving it another chance';
    else reason='Part of their little world';
    return {id:item.id,label:item.label,score,reason};
  });
  if(inCare)return outlook.map((v,i)=>({...v,preferred:!outlook.some((other,j)=>j!==i&&other.score>v.score),chance:null}));
  const total=outlook.reduce((sum,v)=>sum+v.score,0);
  return outlook.map(v=>({...v,chance:v.score/total,preferred:false}));
}

/** Applies the same recent-visit exclusion as the autonomous scheduler. */
function nextActivityOutlook(s,available=objects){
  if(s.paused)return {mode:s.care?'care':'explore',choices:[]};
  const candidates=available.filter(item=>isAvailableForOutlook(s,item));
  const alternatives=candidates.filter(item=>item.id!==s.lastVisited);
  const pool=alternatives.length?alternatives:candidates;
  const ranked=activityOutlook(s,pool);
  if(s.care){
    return {mode:'care',choices:ranked.sort((a,b)=>b.score-a.score)};
  }
  return {mode:'explore',choices:ranked.sort((a,b)=>b.chance-a.chance||a.id.localeCompare(b.id))};
}
function isAvailableForOutlook(s,item){
  if(!item||typeof item.id!=='string'||!validObjectIds.has(item.id))return false;
  // Mirror the catalog's capacity availability, without accepting arbitrary
  // injected objects or modifying the world.
  const original=objects.find(o=>o.id===item.id);
  return !original.capacity||(s.objectState?.[original.id]?.usesRemaining??0)>0;
}

function selectAutonomousObject(s,candidates,random=Math.random){
  if(!candidates.length)return null;
  const scores=activityOutlook(s,candidates);
  if(s.care){
    // Stable tie breaking retains the existing first-available choice policy.
    let best=0;
    for(let i=1;i<scores.length;i++)if(scores[i].score>scores[best].score)best=i;
    return candidates[best];
  }
  const total=scores.reduce((sum,v)=>sum+v.score,0);
  let draw=Math.min(1-Number.EPSILON,Math.max(0,Number(random())||0))*total;
  for(let i=0;i<candidates.length;i++){draw-=scores[i].score;if(draw<0)return candidates[i];}
  return candidates.at(-1);
}

return {PROFILE_SCHEMA,HABIT_CAP,ASSOCIATION_CAP,EVIDENCE_CAP,OUTCOMES,PERSONALITY_KEYS,createProfile,preferenceFor,classifyConsequence,validateAssociation,associationFor,learnConsequence,describeConsequences,habitFor,rememberExperience,describeHabits,activityOutlook,nextActivityOutlook,selectAutonomousObject};
})();
// world/invitation-policy.mjs
__modules["world/invitation-policy.mjs"]=(()=>{
const __moduleURL=new URL("./world/invitation-policy.mjs",document.baseURI).href;
/**
 * A deterministic, inspectable invitation decision. The player is never
 * refused based on arbitrary request counts, randomness or hidden timers.
 * Care-based needs only gate invitations when the player opts into care.
 * No state mutation, network requests, or host API dependencies here.
 */
const {objectById,isObjectAvailable}=__modules["world/object-catalog.mjs"];
const INVITATION_RULES=Object.freeze({
  URGENT_ENERGY:15,
  URGENT_FULLNESS:12,
  PROTECTED_REMAINING:2,
});

function evaluateInvitation(state,id){
  const object=objectById(id);
  if(!object)return {allowed:false,reason:'unknown-object',message:'',emotion:null};
  if(!isObjectAvailable(state,id))return {allowed:false,reason:'unavailable',message:`The ${object.label.toLowerCase()} is empty. Refill it first.`,emotion:null};
  if(state.action==='walk'&&state.target===id)return {
    allowed:true,reason:'already-going',alreadyGoing:true,
    message:`Already on the way to the ${object.label.toLowerCase()}.`,emotion:null,
  };
  if(state.action==='sleep'&&state.remaining>INVITATION_RULES.PROTECTED_REMAINING)return {
    allowed:false,reason:'rest-in-progress',message:'Still enjoying a nap. Maybe in a moment.',emotion:'sleepy',
  };
  if(state.action==='bathe'&&state.remaining>INVITATION_RULES.PROTECTED_REMAINING)return {
    allowed:false,reason:'bath-in-progress',message:'Not quite finished in the bath yet.',emotion:null,
  };
  if(state.care===true){
    if(state.needs.energy<INVITATION_RULES.URGENT_ENERGY&&id!=='bed')return {
      allowed:false,reason:'needs-rest',message:'Feeling very tired. The little bed comes first; you can also turn off gentle care.',emotion:'sleepy',
    };
    if(state.needs.fullness<INVITATION_RULES.URGENT_FULLNESS&&id!=='snack'&&id!=='honey'&&!(state.needs.energy<INVITATION_RULES.URGENT_ENERGY&&id==='bed'))return {
      allowed:false,reason:'needs-food',message:'Feeling very hungry. The fruit bowl or honey jar comes first; you can also turn off gentle care.',emotion:null,
    };
  }
  return {allowed:true,reason:'accepted',alreadyGoing:false,
    message:`An invitation to the ${object.label.toLowerCase()}. On the way.`,emotion:'curious'};
}

return {INVITATION_RULES,evaluateInvitation};
})();
// world/simulation.mjs
__modules["world/simulation.mjs"]=(()=>{
const __moduleURL=new URL("./world/simulation.mjs",document.baseURI).href;
const {objects,objectById,isObjectAvailable,initialObjectState,completeObjectUse,refillObject}=__modules["world/object-catalog.mjs"];
const {createProfile,rememberExperience,classifyConsequence,selectAutonomousObject}=__modules["world/creature-profile.mjs"];
const {createGenome,validateGenome,phenotypeFor,traitFor,evolveCompanion}=__modules["world/genetics.mjs"];
const {evaluateInvitation}=__modules["world/invitation-policy.mjs"];

const WORLD_WIDTH = 2400;
const rooms = [
  { id:'kitchen', name:'Foraging edge', x:0, color:'#e4d5ac' },
  { id:'dining', name:'Gathering cave', x:480, color:'#d5d8b4' },
  { id:'bathroom', name:'Crystal grotto', x:960, color:'#c3dbd2' },
  { id:'bedroom', name:'Sleeping hollow', x:1440, color:'#d6cad9' },
  { id:'garden', name:'Sunlit garden', x:1920, color:'#acc8a0' },
];
function createWorld({preferences={},genome=null,genomeSeed=0x54415649}={}) {
  const initialGenome=genome??createGenome(genomeSeed);
  validateGenome(initialGenome);
  const safeGenome=structuredClone(initialGenome);
  return {x:690,facing:1,target:null,action:'idle',time:0,remaining:4,decisionIn:5,
    care:false,paused:false,lookUntil:0,nextBondEvolutionAt:0,emotion:'content',message:'Taking in the new home.',
    needs:{fullness:76,cleanliness:86,happiness:82,energy:72,affection:78},
    form:'cat',genome:safeGenome,phenotype:phenotypeFor(safeGenome),profile:createProfile(preferences),objectState:initialObjectState(),visits:{},memories:[],lastVisited:null,requests:0};
}
const clamp=n=>Math.max(0,Math.min(100,n));
function remember(s,text) {s.memories=[text,...s.memories.filter(m=>m!==text)].slice(0,6);}
function finishVisit(s) {
  const object=objectById(s.target);
  if(!object)return;
  const needBefore=s.needs[object.need];
  const needsBefore={...s.needs};
  if(!completeObjectUse(s,object.id)){
    s.target=null;s.action='idle';s.remaining=3;return;
  }
  const secondaryGain=Object.keys(object.effects).filter(k=>k!==object.need)
    .reduce((sum,k)=>sum+Math.max(0,s.needs[k]-needsBefore[k]),0);
  const outcome=classifyConsequence({previousVisits:s.visits[object.id]??0,needBefore,
    needAfter:s.needs[object.need],secondaryGain});
  rememberExperience(s,object.id,{needBefore,action:object.action,outcome});
  // A successful completed interaction changes this individual's genome.
  const event=object.action==='eat'?'nourish':object.action==='sit'?'bond':object.action==='sleep'?'rest':object.action==='bathe'?'bathe':'play';
  evolveCompanion(s,event);
  if(!s.visits[object.id])evolveCompanion(s,'explore');
  s.visits[object.id]=(s.visits[object.id]??0)+1;
  s.lastVisited=object.id;
  if(outcome==='disappointing')remember(s,`The ${object.label.toLowerCase()} wasn't very satisfying this time.`);
  else if(outcome==='pleasant')remember(s,`Had a pleasant time at the ${object.label.toLowerCase()}.`);
  else remember(s,`The ${object.label.toLowerCase()} is still new and interesting.`);
  if(s.visits[object.id]===2)remember(s,`Visited the ${object.label.toLowerCase()} twice. A small routine is forming.`);
  else if(s.visits[object.id]===1)remember(s,`Discovered the ${object.label.toLowerCase()}.`);
  s.target=null;s.action='idle';s.remaining=3;s.emotion=outcome==='unfamiliar'?'curious':'content';
}
function requestObject(s,id) {
  const decision=evaluateInvitation(s,id);
  if(!decision.allowed){
    if(decision.message)s.message=decision.message;
    if(decision.emotion)s.emotion=decision.emotion;
    return false;
  }
  // Repeated taps on a current destination are acknowledgements, not a fresh
  // trip or interrupted action. This also prevents rapid taps farming requests.
  if(decision.alreadyGoing){s.message=decision.message;return true;}
  s.requests++;
  s.target=id;s.action='walk';s.emotion='curious';s.message=decision.message;
  return true;
}
function express(s,action) {
  if(action==='look') {
    if(s.action==='sleep'){s.message='Eyes still closed. Let’s let this nap finish.';return false;}
    s.lookUntil=s.time+4;s.emotion='curious';s.message='Turns to look at you, with a curious little glance.';return true;
  }
  if(action==='pet') {s.lookUntil=s.time+4;s.emotion='happy';s.needs.affection=clamp(s.needs.affection+6+4*traitFor(s,'sociability'));s.message='Leans into your hand.';remember(s,'Shared a quiet moment together.');
    // Petting is immediate, but it cannot farm infinite evolution in one frame.
    if(!s.paused&&s.time>=s.nextBondEvolutionAt){evolveCompanion(s,'bond');s.nextBondEvolutionAt=s.time+30;}
    return true;}
  if(action==='wave') {
    if(s.action==='sleep'||s.action==='bathe'){s.message='A dance can wait until this is finished.';return false;}
    s.target=null;s.action='wave';s.remaining=6;s.emotion='happy';s.message='A little wave, just for you.';return true;
  }
  return false;
}
function tick(s,seconds,random=Math.random) {
  if(s.paused)return;
  const dt=Math.max(0,Math.min(.1,Number.isFinite(seconds)?seconds:0));s.time+=dt;
  if(s.care) for(const key of ['fullness','cleanliness','happiness','energy']){
    // Tiny optional on-screen metabolic effects. No offscreen/offline catch-up.
    const multiplier=key==='fullness'?0.75+traitFor(s,'appetite')*.5:key==='energy'?1.25-traitFor(s,'stamina')*.5:1;
    s.needs[key]=clamp(s.needs[key]-dt*.035*multiplier);
  }
  if(s.action==='walk') {
    const object=objectById(s.target);
    if(!object||!isObjectAvailable(s,object.id)){s.action='idle';s.target=null;return;}
    const delta=object.x-s.x;s.facing=delta<0?-1:1;
    s.x=Math.max(50,Math.min(WORLD_WIDTH-50,s.x+Math.sign(delta)*Math.min(Math.abs(delta),dt*76)));
    if(Math.abs(object.x-s.x)<1){s.action=object.action;s.remaining=object.duration;s.message=`Spending a moment at the ${object.label.toLowerCase()}.`;s.emotion=object.action==='sleep'?'sleepy':'happy';}
    return;
  }
  s.remaining-=dt;
  if(s.remaining>0)return;
  if(s.target)finishVisit(s);
  else if(s.action==='wave'){s.action='idle';s.remaining=3;s.emotion='content';return;}
  else {
    const available=objects.filter(o=>isObjectAvailable(s,o.id));
    const alternatives=available.filter(o=>o.id!==s.lastVisited);
    const choice=selectAutonomousObject(s,alternatives.length?alternatives:available,random);
    if(!choice){s.action='idle';s.remaining=3;return;}
    s.target=choice.id;s.action='walk';s.message=`A little curiosity about the ${choice.label.toLowerCase()}.`;s.emotion='curious';
  }
}

return {WORLD_WIDTH,rooms,createWorld,requestObject,express,tick,objects,isObjectAvailable,refillObject};
})();
// world/forms.mjs
__modules["world/forms.mjs"]=(()=>{
const __moduleURL=new URL("./world/forms.mjs",document.baseURI).href;
// Only completed painted character packs can be selected in the main world.
const startingForms={
  cat:{label:'Cat',description:'Detailed painted fur, whiskers and an animated tail'},
  unicorn:{label:'Unicorn',description:'Detailed painted coat, flowing mane and gentle horn'}
};
function applyForm(state,id){
  if(!Object.hasOwn(startingForms,id))return false;
  state.form=id;
  return true;
}

return {startingForms,applyForm};
})();
// world/engine-port.mjs
__modules["world/engine-port.mjs"]=(()=>{
const __moduleURL=new URL("./world/engine-port.mjs",document.baseURI).href;
/**
 * Language-neutral companion-engine boundary.
 * JS is just the local reference adapter; a Rust/C#/native implementation can
 * consume the same serializable requests without owning Tavi's UI or identity.
 */
const {createWorld,tick,requestObject,express,refillObject}=__modules["world/simulation.mjs"];
const {applyForm}=__modules["world/forms.mjs"];
const ENGINE_PROTOCOL='tavi.companion.engine/v1';
const COMMANDS=new Set(['invite','express','choose-form','set-care','set-paused','refill']);
const EXPRESSIONS=new Set(['look','pet','wave']);
const ID=/^[a-z][a-z0-9-]{1,39}$/;
const keysMatch=(request,keys)=>Object.keys(request).every(key=>keys.includes(key));

function validateEngineRequest(request){
  if(!request||typeof request!=='object'||Array.isArray(request)||request.schema!==ENGINE_PROTOCOL)throw Error('Unsupported companion engine protocol');
  if(request.op==='advance'){
    if(!keysMatch(request,['schema','op','seconds'])||!Number.isFinite(request.seconds)||request.seconds<0||request.seconds>0.1)throw Error('Invalid engine step');
    return true;
  }
  if(request.op==='read'){if(!keysMatch(request,['schema','op']))throw Error('Invalid engine read');return true;}
  if(request.op!=='command'||!COMMANDS.has(request.command))throw Error('Unsupported engine operation');
  if(request.command==='invite'||request.command==='refill'){
    if(!keysMatch(request,['schema','op','command','id'])||typeof request.id!=='string'||!ID.test(request.id))throw Error('Invalid object ID');
  }else if(request.command==='express'){
    if(!keysMatch(request,['schema','op','command','action'])||!EXPRESSIONS.has(request.action))throw Error('Invalid expression');
  }else if(request.command==='choose-form'){
    if(!keysMatch(request,['schema','op','command','form'])||typeof request.form!=='string'||!ID.test(request.form))throw Error('Invalid form');
  }else if(!keysMatch(request,['schema','op','command','enabled'])||typeof request.enabled!=='boolean')throw Error('Invalid toggle');
  return true;
}

function createLocalCompanionEngine({state=createWorld(),random=Math.random}={}){
  if(!state||typeof state!=='object'||typeof random!=='function')throw Error('Invalid engine configuration');
  let revision=0;
  function advance(seconds){
    validateEngineRequest({schema:ENGINE_PROTOCOL,op:'advance',seconds});
    if(!state.paused){tick(state,seconds,random);revision++;}
    return state;
  }
  function command(type,value){
    let message={schema:ENGINE_PROTOCOL,op:'command',command:type};
    if(type==='invite'||type==='refill')message.id=value;
    else if(type==='express')message.action=value;
    else if(type==='choose-form')message.form=value;
    else message.enabled=value;
    validateEngineRequest(message);
    let accepted=false;
    switch(type){
      case 'invite':accepted=requestObject(state,value);break;
      case 'express':accepted=express(state,value);break;
      case 'choose-form':accepted=applyForm(state,value);break;
      case 'set-care':state.care=value;accepted=true;break;
      case 'set-paused':state.paused=value;accepted=true;break;
      case 'refill':accepted=refillObject(state,value);break;
    }
    if(accepted)revision++;
    return accepted;
  }
  function exchange(message){
    validateEngineRequest(message);
    let accepted=true;
    if(message.op==='advance')advance(message.seconds);
    if(message.op==='command'){
      const value=message.command==='express'?message.action:message.command==='choose-form'?message.form:
        message.command==='set-care'||message.command==='set-paused'?message.enabled:message.id;
      accepted=command(message.command,value);
    }
    // Structured-clone/JSON compatible; external/native adapters can return the
    // same shape without sharing JS object references or DOM access.
    return {schema:ENGINE_PROTOCOL,ok:accepted,revision,state:JSON.parse(JSON.stringify(state))};
  }
  return {get state(){return state;},get revision(){return revision;},advance,command,exchange};
}

return {ENGINE_PROTOCOL,validateEngineRequest,createLocalCompanionEngine};
})();
// vendor/tavix-sdk-1.0.0/index.js
__modules["vendor/tavix-sdk-1.0.0/index.js"]=(()=>{
const __moduleURL=new URL("./vendor/tavix-sdk-1.0.0/index.js",document.baseURI).href;
/** TaviX 1.0 browser SDK.
 *
 * The stable wire channel remains `tavi.extension/v1` for compatibility with
 * existing Tavi applications. TaviX standardizes that deployed protocol; it
 * does not expose Social credentials or native privileges to the iframe.
 */
const TAVIX_STANDARD='tavix/1.0';
const TAVIX_CHANNEL='tavi.extension/v1';
const TAVIX_HOST_API='1.0.0';

function assertTaviXHostInfo(info){
 if(!info||typeof info!=='object'||info.standard!==TAVIX_STANDARD||info.channel!==TAVIX_CHANNEL||typeof info.api!=='string'||!/^1\.\d+\.\d+$/.test(info.api)||typeof info.extensionId!=='string'||info.mode!=='embedded'||info.navigation!=='host'||!Array.isArray(info.features))throw Error('Host is not TaviX 1.0 compatible');
 return info;
}

function createTaviXSDK(target=window.parent,source=window){
 let nextId=0;
 const pending=new Map(),listeners=new Map();
 const receiver=e=>{
  if(e.source!==target||e.data?.channel!==TAVIX_CHANNEL)return;
  if(e.data.direction==='event'){
   const handlers=listeners.get(e.data.event);if(handlers)for(const fn of [...handlers]){try{fn(e.data.payload);}catch{}}
   return;
  }
  if(e.data.direction!=='response')return;
  const item=pending.get(e.data.id);if(!item)return;pending.delete(e.data.id);clearTimeout(item.timer);
  if(e.data.ok)item.resolve(e.data.result);else item.reject(Error(e.data.error||'TaviX request failed'));
 };
 source.addEventListener('message',receiver);
 const request=(method,args={})=>{
  const id=++nextId;
  return new Promise((resolve,reject)=>{
   if(pending.size>=20)return reject(Error('Too many TaviX requests'));
   const timer=setTimeout(()=>{pending.delete(id);reject(Error('TaviX host did not respond'));},10000);
   pending.set(id,{resolve,reject,timer});
   target.postMessage({channel:TAVIX_CHANNEL,direction:'request',id,method,...args},'*');
  });
 };
 const call=(method,params={})=>request(method,{params});
 const on=(event,handler)=>{
  if(typeof event!=='string'||!event||typeof handler!=='function')throw Error('Invalid TaviX event listener');
  const set=listeners.get(event)||new Set();set.add(handler);listeners.set(event,set);
  return ()=>{set.delete(handler);if(!set.size)listeners.delete(event);};
 };
 return {
  info:()=>request('host.info'),
  conformance:async()=>assertTaviXHostInfo(await request('host.info')),
  capabilities:()=>request('host.capabilities'),
  navigation:{back:()=>request('navigation.back'),close:()=>request('navigation.close')},
  storage:{get:key=>request('storage.get',{key}),set:(key,value)=>request('storage.set',{key,value})},
  ui:{toast:message=>request('ui.toast',{message}),close:()=>request('ui.close'),
    // Compatibility only. New integrations should negotiate tavix.surface/v1.
    requestGameLaunch:handoff=>request('ui.requestGameLaunch',{handoff})},
  // TaviX optional module. Tavi 0.3.108 deliberately fails closed until the
  // generic nested surface broker is implemented and advertised by host.info.
  surfaces:{requestOpen:surface=>request('surface.requestOpen',{surface})},
  on,
  wallet:{balance:()=>call('wallet.balance'),transactions:params=>call('wallet.transactions',params),
    claim:params=>call('wallet.claim',params),convert:params=>call('wallet.convert',params),
    purchase:params=>call('wallet.purchase',params),orderStatus:params=>call('wallet.orderStatus',params),
    transfer:params=>call('wallet.transfer',params)},
  pets:{list:params=>call('pets.list',params),get:params=>call('pets.get',params),command:params=>call('pets.command',params)},
  contacts:{list:params=>call('contacts.list',params)},
  messages:{list:params=>call('messages.list',params),send:params=>call('messages.send',params)},
  events:{list:params=>call('events.list',params)},
  services:{list:()=>call('services.list')},
  dispose:()=>{source.removeEventListener('message',receiver);for(const item of pending.values()){clearTimeout(item.timer);item.reject(Error('TaviX disconnected'));}pending.clear();listeners.clear();}
 };
}

// Deployed-source compatibility name. Existing apps do not need a rewrite.
const createTaviExtensionSDK=createTaviXSDK;

return {TAVIX_STANDARD,TAVIX_CHANNEL,TAVIX_HOST_API,assertTaviXHostInfo,createTaviXSDK,createTaviExtensionSDK};
})();
// tavi-sdk.mjs
__modules["tavi-sdk.mjs"]=(()=>{
const __moduleURL=new URL("./tavi-sdk.mjs",document.baseURI).href;
/** TaviX 1.0 runtime plus the narrowly scoped Companion cloud extension.
 *
 * The official @tavi/tavix-sdk source is vendored byte-for-byte under
 * ui/vendor/tavix-sdk-1.0.0. TaviX intentionally keeps the deployed wire
 * channel at tavi.extension/v1. Companion cloud get/put/preview remain a
 * reviewed application-specific extension until they become a standard module.
 */
const {
  TAVIX_STANDARD,TAVIX_CHANNEL,TAVIX_HOST_API,assertTaviXHostInfo,
  createTaviXSDK,createTaviExtensionSDK
}=__modules["vendor/tavix-sdk-1.0.0/index.js"];

function createCompanionBridge(target,source){
  // Official SDK requests use positive numeric IDs. Companion-specific calls
  // deliberately use negative IDs so both listeners can share the same stable
  // channel without ever resolving each other's pending requests.
  let nextId=-1;
  const pending=new Map();
  const receiver=e=>{
    if(e.source!==target||e.data?.channel!==TAVIX_CHANNEL||e.data?.direction!=='response'||typeof e.data.id!=='number'||e.data.id>=0)return;
    const item=pending.get(e.data.id);if(!item)return;pending.delete(e.data.id);clearTimeout(item.timer);
    if(e.data.ok)item.resolve(e.data.result);else item.reject(Error(e.data.error||'Companion host request failed'));
  };
  source.addEventListener('message',receiver);
  const request=(method,args={})=>{
    const id=nextId--;
    return new Promise((resolve,reject)=>{
      if(pending.size>=8)return reject(Error('Too many Companion host requests'));
      const timer=setTimeout(()=>{pending.delete(id);reject(Error('Companion host did not respond'));},10000);
      pending.set(id,{resolve,reject,timer});
      target.postMessage({channel:TAVIX_CHANNEL,direction:'request',id,method,...args},'*');
    });
  };
  return {
    api:{
      publishPreview:preview=>request('companion.preview',{preview}),
      load:()=>request('companion.get'),
      save:({snapshot,revision,epoch})=>request('companion.put',{snapshot,revision,epoch}),
    },
    dispose(){source.removeEventListener('message',receiver);for(const item of pending.values()){clearTimeout(item.timer);item.reject(Error('Companion bridge disconnected'));}pending.clear();}
  };
}

function createTaviCompanionSDK(target=window.parent,source=window){
  const core=createTaviXSDK(target,source);
  const bridge=createCompanionBridge(target,source);
  return Object.freeze({
    ...core,
    companion:Object.freeze(bridge.api),
    dispose(){bridge.dispose();core.dispose();}
  });
}

return {createTaviCompanionSDK,TAVIX_STANDARD,TAVIX_CHANNEL,TAVIX_HOST_API,assertTaviXHostInfo,createTaviXSDK,createTaviExtensionSDK};
})();
// world/tavi-host.mjs
__modules["world/tavi-host.mjs"]=(()=>{
const __moduleURL=new URL("./world/tavi-host.mjs",document.baseURI).href;
/**
 * Optional Tavi host connection. TaviX 1.0 is preferred while the legacy
 * extension/v1 host remains a compatibility path for currently reviewed Tavi.
 * No Social credentials or game API endpoints enter the Companion frame.
 */
const {createTaviCompanionSDK,assertTaviXHostInfo,TAVIX_STANDARD}=__modules["tavi-sdk.mjs"];
function identifyHost(info){
  if(!info||info.extensionId!=='org.tavi.community.companion'||info.mode!=='embedded')throw Error('Not the companion host');
  if(Object.hasOwn(info,'standard')){
    if(info.standard!==TAVIX_STANDARD)throw Error('Unsupported Tavix standard');
    assertTaviXHostInfo(info);
    return 'tavix';
  }
  if(info.api!=='1.0.0')throw Error('Unsupported legacy host');
  return 'legacy';
}

async function connectTaviHost({windowRef,createSDK=createTaviCompanionSDK}={}){
  const win=windowRef??(typeof window!=='undefined'?window:null);
  if(!win||!win.parent||win.parent===win)return null;
  const sdk=createSDK(win.parent,win);
  try{
    const info=await sdk.info();
    const hostKind=identifyHost(info);
    const capabilities=await sdk.capabilities();
    if(!Array.isArray(capabilities)||!capabilities.includes('ui.panel')||!info.features?.includes('tavi.companion.cloud/v1'))throw Error('Companion cloud host unavailable');
    if(!sdk.companion?.load||!sdk.companion?.save||!sdk.companion?.publishPreview)throw Error('Companion bridge unavailable');
    return {
      mode:'tavi',
      standard:hostKind==='tavix'?TAVIX_STANDARD:'tavi.extension/v1',
      canStore:capabilities.includes('storage.private'),
      cloud:true,
      load:()=>sdk.companion.load(),
      save:(snapshot,revision,epoch)=>sdk.companion.save({snapshot,revision,epoch}),
      read:key=>sdk.storage.get(key),
      write:(key,value)=>sdk.storage.set(key,value),
      close:()=>hostKind==='tavix'?sdk.navigation.back():sdk.ui.close(),
      publishPortrait:preview=>sdk.companion.publishPreview(preview),
      dispose:()=>sdk.dispose(),
    };
  }catch{
    sdk.dispose();return null;
  }
}

return {connectTaviHost};
})();
// world/session-codec.mjs
__modules["world/session-codec.mjs"]=(()=>{
const __moduleURL=new URL("./world/session-codec.mjs",document.baseURI).href;
/** Portable, bounded session data; no DOM, Tavi account token, or JS class instances. */
const {createWorld,WORLD_WIDTH}=__modules["world/simulation.mjs"];
const {objects,initialObjectState}=__modules["world/object-catalog.mjs"];
const {startingForms}=__modules["world/forms.mjs"];
const {validateGenome}=__modules["world/genetics.mjs"];
const {HABIT_CAP,validateAssociation}=__modules["world/creature-profile.mjs"];
const SESSION_SCHEMA='tavi.companion.session/v5';
const PREVIOUS_SESSION_SCHEMA='tavi.companion.session/v4';
const SESSION_STORAGE_KEY='companion_session_v1';
const MAX_BYTES=8192; // Matches the currently deployed Tavi extension storage limit.
const needNames=['fullness','cleanliness','happiness','energy','affection'];
const id=/^[a-z][a-z0-9-]{1,39}$/;
const bounded=(v,min,max)=>Number.isFinite(v)&&v>=min&&v<=max;
const obj=o=>Boolean(o&&typeof o==='object'&&!Array.isArray(o));

function encodeSession({chosen,name,state}){
  if(!state||!obj(state.profile))throw Error('Invalid session state');
  const data={schema:SESSION_SCHEMA,chosen:chosen===true,name:String(name??'').slice(0,32),world:{
    form:state.form,x:state.x,care:state.care===true,genome:state.genome,
    needs:Object.fromEntries(needNames.map(k=>[k,state.needs[k]])),
    preferences:{...state.profile.preferences},experience:{...state.profile.experience},habits:{...state.profile.habits},associations:{...state.profile.associations},
    objectState:Object.fromEntries(objects.filter(o=>o.capacity).map(o=>[o.id,{usesRemaining:state.objectState?.[o.id]?.usesRemaining??o.capacity}])),
    visits:{...state.visits},lastVisited:state.lastVisited,
    memories:state.memories.slice(0,6),
  }};
  const json=JSON.stringify(data);
  if(json.length>MAX_BYTES)throw Error('Companion session is too large');
  // Round-trip through the same validation used for untrusted host storage.
  if(!decodeSession(json))throw Error('Invalid companion session snapshot');
  return json;
}

/** Strict v5 snapshot; one direct v4 upgrade preserves the current companion. */
function decodeSession(raw){
  if(typeof raw!=='string'||raw.length>MAX_BYTES||!raw.length)return null;
  let data;try{data=JSON.parse(raw);}catch{return null;}
  if(!obj(data)||![SESSION_SCHEMA,PREVIOUS_SESSION_SCHEMA].includes(data.schema)||typeof data.chosen!=='boolean'||typeof data.name!=='string'||data.name.length>32||!obj(data.world))return null;
  const w=data.world;
  if(!Object.hasOwn(startingForms,w.form)||!bounded(w.x,0,WORLD_WIDTH)||typeof w.care!=='boolean'||!obj(w.needs)||!obj(w.preferences)||!obj(w.experience)||!obj(w.objectState)||!obj(w.visits)||!Array.isArray(w.memories)||w.memories.length>6)return null;
  for(const k of needNames)if(!bounded(w.needs[k],0,100))return null;
  if(Object.keys(w.needs).some(k=>!needNames.includes(k)))return null;
  const validPreference=(key,value)=>id.test(key)&&bounded(value,-1,1);
  if(Object.keys(w.preferences).length>32||Object.entries(w.preferences).some(([k,v])=>!validPreference(k,v)))return null;
  if(Object.keys(w.experience).length>32||Object.entries(w.experience).some(([k,v])=>!id.test(k)||!Number.isSafeInteger(v)||v<0||v>50))return null;
  if(!obj(w.habits)||Object.keys(w.habits).length>32||Object.entries(w.habits).some(([k,v])=>!objects.some(o=>o.id===k)||!Number.isSafeInteger(v)||v<0||v>HABIT_CAP))return null;
  if(data.schema===SESSION_SCHEMA){
    if(!obj(w.associations)||Object.keys(w.associations).length>32||Object.entries(w.associations).some(([k,v])=>!objects.some(o=>o.id===k)||!validateAssociation(v)))return null;
  }else if(Object.hasOwn(w,'associations'))return null;
  const capacity=objects.filter(o=>o.capacity);
  if(Object.keys(w.objectState).some(k=>!capacity.some(o=>o.id===k)))return null;
  for(const o of capacity)if(!obj(w.objectState[o.id])||!Number.isSafeInteger(w.objectState[o.id].usesRemaining)||w.objectState[o.id].usesRemaining<0||w.objectState[o.id].usesRemaining>o.capacity)return null;
  if(Object.keys(w.visits).length>32||Object.entries(w.visits).some(([k,v])=>!id.test(k)||!Number.isSafeInteger(v)||v<0||v>1000000))return null;
  if(w.lastVisited!==null&&(typeof w.lastVisited!=='string'||!id.test(w.lastVisited)))return null;
  if(w.memories.some(m=>typeof m!=='string'||m.length>160))return null;
  try{validateGenome(w.genome);}catch{return null;}
  const genome=w.genome;
  // Never replay offline time or interrupted activities. Invalid data cannot
  // mutate an existing live world; a fresh validated world is constructed.
  let state;try{state=createWorld({preferences:w.preferences,genome});}catch{return null;}
  state.form=w.form;state.x=w.x;state.care=w.care;
  state.needs={...w.needs};state.profile.experience={...w.experience};state.profile.habits={...w.habits};
  state.profile.associations=data.schema===SESSION_SCHEMA?structuredClone(w.associations):{};
  state.objectState=initialObjectState();
  for(const o of capacity)state.objectState[o.id]={usesRemaining:w.objectState[o.id].usesRemaining};
  state.visits={...w.visits};state.lastVisited=w.lastVisited;
  state.memories=[...w.memories];state.action='idle';state.target=null;state.remaining=4;
  return {chosen:data.chosen,name:data.name,state,migrated:data.schema!==SESSION_SCHEMA};
}

return {SESSION_SCHEMA,PREVIOUS_SESSION_SCHEMA,SESSION_STORAGE_KEY,encodeSession,decodeSession};
})();
// world/companion-colors.mjs
__modules["world/companion-colors.mjs"]=(()=>{
const __moduleURL=new URL("./world/companion-colors.mjs",document.baseURI).href;
const neutralCoat={channel:'coat',chroma:[0,.18],lightness:[.13,1],sourceLightness:.86};
const furRules=[
 {channel:'cream',hue:[30,65],lightness:[.78,.98],saturation:[.18,1],sourceLightness:.85},
 {channel:'markings',hue:[0,28],lightness:[.26,.62],saturation:[.22,1],sourceLightness:.45},
 {channel:'coat',hue:[10,58],lightness:[.26,.96],saturation:[.2,1],sourceLightness:.64}
];
const colorProfiles={
 unicorn:{
  label:'Unicorn colors',defaultPreset:'pearl',
  defaults:{coat:'#e9e5df',mane:'#aa89d9',horn:'#e4bd6b',hooves:'#645275'},
  channels:[{id:'coat',label:'Coat'},{id:'mane',label:'Mane & tail'},{id:'horn',label:'Horn'},{id:'hooves',label:'Hooves'}],
  presets:{
   pearl:{label:'Pearl',colors:{coat:'#e9e5df',mane:'#aa89d9',horn:'#e4bd6b',hooves:'#645275'}},
   twilight:{label:'Twilight',colors:{coat:'#53617c',mane:'#d592bb',horn:'#efc575',hooves:'#40364f'}},
   meadow:{label:'Meadow',colors:{coat:'#bfd1ae',mane:'#548e94',horn:'#e2c17a',hooves:'#526b57'}}
  },
  materials:{
   coat:[neutralCoat],
   limb:[{channel:'hooves',hue:[145,205],saturation:[.2,1],lightness:[.1,1],sourceLightness:.42},neutralCoat],
   mane:[{channel:'mane',lightness:[.1,1],sourceLightness:.58}],
   horn:[{channel:'horn',lightness:[.1,1],sourceLightness:.62}]
  }
 },
 cat:{
  label:'Cat colors',defaultPreset:'ginger',preserveDefaults:true,
  defaults:{coat:'#dba36a',markings:'#ac6038',cream:'#fae4b6',innerEar:'#dca6ab'},
  channels:[{id:'coat',label:'Fur'},{id:'markings',label:'Stripes'},{id:'cream',label:'Muzzle & paws'},{id:'innerEar',label:'Inner ears'}],
  presets:{
   ginger:{label:'Ginger',colors:{coat:'#dba36a',markings:'#ac6038',cream:'#fae4b6',innerEar:'#dca6ab'}},
   silver:{label:'Silver',colors:{coat:'#a8adb8',markings:'#53606d',cream:'#f2ecdf',innerEar:'#cf9da8'}},
   lavender:{label:'Lavender',colors:{coat:'#b497ca',markings:'#6d527d',cream:'#f2e8e7',innerEar:'#d6a3bd'}}
  },
  materials:{
   fur:furRules,
   earFur:[
    {channel:'innerEar',hue:[330,360],saturation:[.12,1],lightness:[.35,.94],sourceLightness:.76},
    {channel:'innerEar',hue:[0,15],saturation:[.12,1],lightness:[.35,.94],sourceLightness:.76},
    ...furRules
   ]
  }
 }
};
const unicornPalette=colorProfiles.unicorn.defaults;
const unicornPresets=Object.fromEntries(Object.entries(colorProfiles.unicorn.presets).map(([id,p])=>[id,p.colors]));
function validateColorProfile(profile){
 if(!profile||!Array.isArray(profile.channels)||!profile.channels.length||profile.channels.length>12||!profile.defaults||!profile.materials)throw Error('Invalid companion color profile');
 const ids=new Set();
 for(const {id,label}of profile.channels){
  if(!/^[a-zA-Z][a-zA-Z0-9]*$/.test(id)||ids.has(id)||typeof label!=='string'||!label)throw Error('Invalid color channel');
  ids.add(id);
 }
 validatePalette(profile.defaults,profile);
 if(!profile.presets?.[profile.defaultPreset])throw Error('Missing default palette');
 for(const preset of Object.values(profile.presets))validatePalette(preset.colors,profile);
 for(const rules of Object.values(profile.materials)){
  if(!Array.isArray(rules)||!rules.length||rules.length>16)throw Error('Invalid material rules');
  for(const rule of rules){
   if(!ids.has(rule.channel)||!Number.isFinite(rule.sourceLightness)||rule.sourceLightness<=0||rule.sourceLightness>=1)throw Error('Invalid material channel');
   for(const key of ['hue','saturation','lightness','chroma'])if(rule[key]){
    const range=rule[key],max=key==='hue'?360:1;
    if(!Array.isArray(range)||range.length!==2||range.some(n=>!Number.isFinite(n))||range[0]<0||range[1]>max||range[0]>range[1])throw Error('Invalid color selector');
   }
  }
 }
 return profile;
}
function validatePalette(palette,profile=colorProfiles.unicorn){
 if(!palette||profile.channels.some(({id})=>!/^#[0-9a-f]{6}$/i.test(palette[id]??'')))throw Error('Invalid companion palette');
 return palette;
}
function hsl(r,g,b){
 r/=255;g/=255;b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min,l=(max+min)/2;
 let h=0;if(d)h=max===r?((g-b)/d+(g<b?6:0)):max===g?(b-r)/d+2:(r-g)/d+4;
 return [h*60,d?d/(1-Math.abs(2*l-1)):0,l];
}
function rgb(h,s,l){
 const c=(1-Math.abs(2*l-1))*s,x=c*(1-Math.abs((h/60)%2-1)),m=l-c/2;
 const v=h<60?[c,x,0]:h<120?[x,c,0]:h<180?[0,c,x]:h<240?[0,x,c]:h<300?[x,0,c]:[c,0,x];
 return v.map(n=>Math.round((n+m)*255));
}
// Materials, selectors and user-facing channels come from the asset pack.
// This runs only when preparing cached tiles, never on an animation frame.
function recolorPixels(data,material,palette,profile=colorProfiles.unicorn,{width=0,height=0,protectedRegions=[]}={}){
 validatePalette(palette,profile);
 const rules=profile.materials[material];if(!rules)throw Error('Unknown companion material: '+material);
 if(profile.preserveDefaults&&profile.channels.every(({id})=>palette[id].toLowerCase()===profile.defaults[id].toLowerCase()))return data;
 const targets=Object.fromEntries(profile.channels.map(({id})=>[id,hsl(...[1,3,5].map(i=>parseInt(palette[id].slice(i,i+2),16)))]));
 for(let i=0;i<data.length;i+=4){
  if(!data[i+3])continue;
  const [h,s,l]=hsl(data[i],data[i+1],data[i+2]);
  if(protectedRegions.length&&width&&height){
   const x=((i/4)%width+.5)/width,y=(Math.floor(i/4/width)+.5)/height;
   if(protectedRegions.some(region=>h>=region.hue[0]&&h<=region.hue[1]&&((x-region.center[0])/region.radius[0])**2+((y-region.center[1])/region.radius[1])**2<=1))continue;
  }
  const chroma=(Math.max(data[i],data[i+1],data[i+2])-Math.min(data[i],data[i+1],data[i+2]))/255;
  let rule;
  for(const candidate of rules){
   if((!candidate.hue||(h>=candidate.hue[0]&&h<=candidate.hue[1]))&&(!candidate.saturation||(s>=candidate.saturation[0]&&s<=candidate.saturation[1]))&&(!candidate.lightness||(l>=candidate.lightness[0]&&l<=candidate.lightness[1]))&&(!candidate.chroma||(chroma>=candidate.chroma[0]&&chroma<=candidate.chroma[1]))){rule=candidate;break;}
  }
  if(!rule)continue;
  const channel=rule.channel;
  if(profile.preserveDefaults&&palette[channel].toLowerCase()===profile.defaults[channel].toLowerCase())continue;
  const [th,ts,tl]=targets[channel],base=rule.sourceLightness;
  const light=l<base?l*(tl/base):tl+(1-tl)*((l-base)/(1-base));
  const result=rgb(th,ts*(l>.9?.65:1),Math.max(0,Math.min(1,light)));
  data[i]=result[0];data[i+1]=result[1];data[i+2]=result[2];
 }
 return data;
}


return {colorProfiles,unicornPalette,unicornPresets,validateColorProfile,validatePalette,recolorPixels};
})();
// world/rig-diagnostics.mjs
__modules["world/rig-diagnostics.mjs"]=(()=>{
const __moduleURL=new URL("./world/rig-diagnostics.mjs",document.baseURI).href;
// Source-only diagnostic geometry: no mutation of atlases or persistent creature state.
// Bounds are expressed in the same local coordinates used by stamp() in the painter.
const RIG_INSPECTOR_MODES=Object.freeze(['off','head','legs','all']);
const PART_GROUPS={
  head:/^(front|side|front-blink|side-blink|ear|horn|mane)/,
  legs:/^leg/,
};
function inRigGroup(id,mode){
  if(!RIG_INSPECTOR_MODES.includes(mode))throw Error('Unsupported rig inspector mode');
  return mode==='all'||(mode!=='off'&&PART_GROUPS[mode].test(id));
}
function inspectRigLayout(layout,mode='all'){
  if(!layout||!layout.parts||typeof layout.parts!=='object')throw Error('Missing rig layout');
  return Object.entries(layout.parts).filter(([id])=>inRigGroup(id,mode)).map(([id,part])=>{
    const {source,pivot,size,atlas,placementOffset=[0,0]}=part;
    if(!Array.isArray(source)||source.length!==4||!Array.isArray(pivot)||pivot.length!==2||!Array.isArray(size)||size.length!==2||![...source,...pivot,...size].every(Number.isFinite))throw Error('Invalid rig part '+id);
    if(!Array.isArray(placementOffset)||placementOffset.length!==2||placementOffset.some(n=>!Number.isFinite(n)||Math.abs(n)>16))throw Error('Invalid rig placement '+id);
    return {id,atlas:atlas||'base',source:[...source],size:[...size],pivot:[...pivot],placementOffset:[...placementOffset],relativeBounds:[-pivot[0],-pivot[1],size[0],size[1]],placedBounds:[placementOffset[0]-pivot[0],placementOffset[1]-pivot[1],size[0],size[1]]};
  });
}
// Applied AFTER drawImage while in the exact transformed source-part frame.
// With diagnostics=off no extra drawing happens in the production renderer.
function drawRigPartOutline(ctx,id,part,mode){
  if(!inRigGroup(id,mode))return;
  const [w,h]=part.size,[px,py]=part.pivot;
  ctx.save();
  ctx.strokeStyle=/^leg/.test(id)?'#14647b':/^mane/.test(id)?'#b52f7b':'#d66a16';
  ctx.lineWidth=.75;
  ctx.strokeRect(-px,-py,w,h);
  ctx.beginPath();ctx.moveTo(-3,0);ctx.lineTo(3,0);ctx.moveTo(0,-3);ctx.lineTo(0,3);ctx.stroke();
  ctx.font='7px sans-serif';ctx.fillStyle=ctx.strokeStyle;
  ctx.fillText(id,-px,-py-2);
  ctx.restore();
}

return {RIG_INSPECTOR_MODES,inRigGroup,inspectRigLayout,drawRigPartOutline};
})();
// world/cat-painted.mjs
__modules["world/cat-painted.mjs"]=(()=>{
const __moduleURL=new URL("./world/cat-painted.mjs",document.baseURI).href;
// Painted raster parts share the existing cat-v1 motion tracks.
// Artwork provenance and CC0 scope: ../assets/CREDITS.md.
const {recolorPixels,validateColorProfile,validatePalette}=__modules["world/companion-colors.mjs"];
const {drawRigPartOutline,RIG_INSPECTOR_MODES}=__modules["world/rig-diagnostics.mjs"];
const paintedParts=['front','side','front-blink','side-blink','torso-front','torso-side','armLeft','armRight','legLeft','legRight','tail','earLeft','earRight','legSideLeft','legSideRight','earSideNear','earSideFar'];
const optionalParts=['horn','maneFront','maneSide','maneSideForelock','maneFrontBack'];
const companionParts=layout=>[...paintedParts,...optionalParts.filter(id=>layout.parts?.[id])];
function catPresentation(action,lookAtViewer){
  return {view:action==='walk'?'side':lookAtViewer?'front':'side',lookAtViewer:Boolean(lookAtViewer)};
}
function validatePaintedLayout(layout,width,height){
  if(layout.schema!==1||layout.width!==width||layout.height!==height)throw Error('Cat atlas dimensions do not match');
  for(const id of companionParts(layout)){
    const part=layout.parts[id];
    if(!part||!Array.isArray(part.source)||part.source.length!==4||!part.source.every(Number.isFinite))throw Error('Missing cat part: '+id);
    if(layout.colors&&!layout.colors.materials?.[part.recolor])throw Error('Missing part material: '+id);
    if(part.placementOffset && (!Array.isArray(part.placementOffset)||part.placementOffset.length!==2||part.placementOffset.some(n=>!Number.isFinite(n)||Math.abs(n)>16)))throw Error('Invalid painted attachment offset: '+id);
    if(part.protectedRegions){
      if(!Array.isArray(part.protectedRegions)||part.protectedRegions.length>8)throw Error('Invalid protected color regions');
      for(const region of part.protectedRegions)for(const [key,max]of [['center',1],['radius',1],['hue',360]]){
        if(!Array.isArray(region[key])||region[key].length!==2||region[key].some(n=>!Number.isFinite(n)||n<0||n>max)||(key==='radius'&&region[key].some(n=>n===0))||(key==='hue'&&region[key][0]>region[key][1]))throw Error('Invalid protected color region');
      }
    }
    const [x,y,w,h]=part.source;
    const bounds=part.atlas?layout.atlases?.[part.atlas]:{width,height};
    if(!bounds||!Number.isFinite(bounds.width)||!Number.isFinite(bounds.height)||x<0||y<0||w<=0||h<=0||x+w>bounds.width||y+h>bounds.height||!Array.isArray(part.size)||part.size.length!==2||part.size.some(n=>!Number.isFinite(n)||n<=0||n>192)||!Array.isArray(part.pivot)||part.pivot.length!==2||!part.pivot.every(Number.isFinite))throw Error('Invalid cat part: '+id);
  }
  return layout;
}
function createPaintedCat(makeCanvas,atlas,layout,extraAtlases={},{palette=layout.colors?.defaults}={}){
  validatePaintedLayout(layout,atlas.naturalWidth??atlas.width,atlas.naturalHeight??atlas.height);
  if(layout.colors){validateColorProfile(layout.colors);validatePalette(palette,layout.colors);}
  const sourceColors=layout.colors?.preserveDefaults&&layout.colors.channels.every(({id})=>palette[id].toLowerCase()===layout.colors.defaults[id].toLowerCase());
  const tiles=new Map();let rgbaBytes=0;
  for(const id of companionParts(layout)){
    const p=layout.parts[id],c=makeCanvas(Math.ceil(p.size[0]*2),Math.ceil(p.size[1]*2));
    const source=p.atlas?extraAtlases[p.atlas]:atlas;
    const bounds=p.atlas?layout.atlases[p.atlas]:layout;
    if(!source||(source.naturalWidth??source.width)!==bounds.width||(source.naturalHeight??source.height)!==bounds.height)throw Error('Cat part atlas unavailable: '+id);
    c.getContext('2d').drawImage(source,...p.source,0,0,c.width,c.height);tiles.set(id,c);rgbaBytes+=c.width*c.height*4;
    if(p.recolor&&!sourceColors){
      const context=c.getContext('2d'),pixels=context.getImageData(0,0,c.width,c.height);
      if(!layout.colors)throw Error('Missing asset color profile');
      recolorPixels(pixels.data,p.recolor,palette,layout.colors,{width:c.width,height:c.height,protectedRegions:p.protectedRegions});context.putImageData(pixels,0,0);
    }
    if(id==='earSideNear'){
      const context=c.getContext('2d'),blend=context.createLinearGradient(0,0,0,c.height);
      blend.addColorStop(0,'#fff');blend.addColorStop(.65,'#fff');blend.addColorStop(1,'#ffffff00');
      context.globalCompositeOperation='destination-in';context.fillStyle=blend;context.fillRect(0,0,c.width,c.height);context.globalCompositeOperation='source-over';
    }
  }
  const armSegments=new Map();
  for(const id of ['armLeft','armRight'])for(const upper of [true,false]){
    const height=upper?30:24,c=makeCanvas(40,height*2),p=c.getContext('2d');
    p.drawImage(tiles.get(id),0,upper?0:36,40,height*2,0,0,40,height*2);
    // Rounded overlapping masks hide the rectangular crop edge at the elbow.
    p.globalCompositeOperation='destination-in';p.beginPath();
    p.rect(0,upper?0:12,40,upper?48:height*2-12);
    p.ellipse(20,upper?48:12,20,12,0,0,Math.PI*2);p.fill();p.globalCompositeOperation='source-over';
    armSegments.set(id+(upper?'Upper':'Lower'),c);rgbaBytes+=40*height*2*4;
  }
  let activeDiagnostics='off';
  function stamp(ctx,id,x,y,motion={},fit={}){
    const p=layout.parts[id];ctx.save();ctx.translate(x+(p.placementOffset?.[0]??0)+(motion.x||0),y+(p.placementOffset?.[1]??0)+(motion.y||0));ctx.rotate((motion.angle||0)*Math.PI/180);
    ctx.rotate((fit.angle||0)*Math.PI/180);ctx.scale(fit.scaleX??1,fit.scaleY??1);
    ctx.drawImage(tiles.get(fit.tile??id),-p.pivot[0],-p.pivot[1],...(fit.drawSize??p.size));
    if(activeDiagnostics!=='off')drawRigPartOutline(ctx,id,p,activeDiagnostics);ctx.restore();
  }
  // Both segments use the original painted arm tile, overlapping at the elbow.
  // Source crops preserve the fur instead of inventing a geometric joint.
  function arm(ctx,id,x,y,upper={},lower={},segment='both'){
    ctx.save();ctx.translate(x+(upper.x||0),y+(upper.y||0));ctx.rotate((upper.angle||0)*Math.PI/180);
    if(segment!=='lower')ctx.drawImage(armSegments.get(id+'Upper'),-10,-9,20,30);
    if(segment!=='upper'){
      ctx.translate(0,15);ctx.translate(lower.x||0,lower.y||0);ctx.rotate((lower.angle||0)*Math.PI/180);
      ctx.drawImage(armSegments.get(id+'Lower'),-10,-6,20,24);
    }
    ctx.restore();
  }
  function head(ctx,pose,view,blink){
    const m=pose.head??{};ctx.save();ctx.translate((m.x||0)+(view==='side'?4:0),-103+(m.y||0));ctx.rotate((m.angle||0)*Math.PI/180);
    const profile=view==='side';
    if(profile){
      // Profile projects the ears onto nearly the same screen position.
      // Painter order provides depth: far ear, skull, then near ear.
      // Head's +4 offset puts the near ear on the shoulder's x=8 axis.
      stamp(ctx,'earSideFar',0,-22,pose.earLeft);
      if(tiles.has('maneSide'))stamp(ctx,'maneSide',0,0);
      stamp(ctx,view+(blink?'-blink':''),0,0);
      if(tiles.has('maneSideForelock'))stamp(ctx,'maneSideForelock',0,0);
      stamp(ctx,'earSideNear',4,-22,pose.earRight);
      if(tiles.has('horn'))stamp(ctx,'horn',20,-22);
    }else{
      if(tiles.has('maneFrontBack'))stamp(ctx,'maneFrontBack',0,0);
      stamp(ctx,'earLeft',-20,-15,pose.earLeft);
      stamp(ctx,'earRight',20,-15,pose.earRight);
      stamp(ctx,view+(blink?'-blink':''),0,0);
      if(tiles.has('maneFront'))stamp(ctx,'maneFront',0,0);
      if(tiles.has('horn'))stamp(ctx,'horn',0,-24);
    }
    ctx.restore();
  }
  return {
    tileCount:tiles.size+armSegments.size,rgbaBytes,
    draw(ctx,x,ground,pose,{scale=1,view='side',lookAtViewer=false,blink=false,diagnostics='off'}={}){
      if(!RIG_INSPECTOR_MODES.includes(diagnostics))throw Error('Invalid diagnostics mode');
      const previous=activeDiagnostics;activeDiagnostics=diagnostics;
      ctx.save();ctx.imageSmoothingEnabled=true;ctx.translate(x,ground);ctx.scale(scale,scale);
      ctx.translate(pose.root?.x||0,pose.root?.y||0);
      stamp(ctx,'tail',-21,-26,pose.tail);
      // In profile both hips project onto the same walking plane. Widely
      // separated hip anchors made the side walk read as a frontal shuffle.
      stamp(ctx,view==='side'?'legSideLeft':'legLeft',view==='side'?-4:-14,-22,pose.legLeft);
      const torso=pose.torso??{};
      ctx.save();ctx.translate(torso.x||0,-57+(torso.y||0));ctx.rotate((torso.angle||0)*Math.PI/180);ctx.translate(0,57);
      const profile=view==='side',nearX=profile?8:21,shoulderY=-70;
      // The frontal right-arm drawing curls left, toward the belly. Both
      // profile paws must curl right, in the direction the cat is facing.
      const nearArmArt=profile?'armLeft':'armRight';
      arm(ctx,'armLeft',profile?-3:-21,shoulderY,pose.armLeft,pose.forearmLeft);
      stamp(ctx,'torso-'+view,0,-54);
      arm(ctx,nearArmArt,nearX,shoulderY,pose.armRight,pose.forearmRight,'upper');
      head(ctx,pose,lookAtViewer?'front':view,blink);
      arm(ctx,nearArmArt,nearX,shoulderY,pose.armRight,pose.forearmRight,'lower');
      ctx.restore();stamp(ctx,view==='side'?'legSideRight':'legRight',view==='side'?-1:14,-22,pose.legRight);ctx.restore();
      activeDiagnostics=previous;
    },
    portrait(ctx,x,y,{scale=1,blink=false,diagnostics='off'}={}){
      if(!RIG_INSPECTOR_MODES.includes(diagnostics))throw Error('Invalid diagnostics mode');
      const previous=activeDiagnostics;activeDiagnostics=diagnostics;
      ctx.save();ctx.imageSmoothingEnabled=true;ctx.translate(x,y+103*scale);ctx.scale(scale,scale);head(ctx,{},'front',blink);ctx.restore();
      activeDiagnostics=previous;
    }
  };
}
// Both companions use this renderer; the original name remains for older callers.
const createPaintedCompanion=createPaintedCat;

return {paintedParts,companionParts,catPresentation,validatePaintedLayout,createPaintedCat,createPaintedCompanion};
})();
// world/cat-motion.mjs
__modules["world/cat-motion.mjs"]=(()=>{
const __moduleURL=new URL("./world/cat-motion.mjs",document.baseURI).href;
// Motion is data, independent of the character's artwork and world simulation.
const catParts=['root','torso','head','earLeft','earRight','armLeft','armRight','forearmLeft','forearmRight','legLeft','legRight','tail'];
const channels=['x','y','angle'];
function validateClip(clip){
  if(!clip||clip.schema!==1||clip.rig!=='cat-v1'||!Number.isFinite(clip.duration)||clip.duration<=0||clip.duration>30||typeof clip.loop!=='boolean'||!Array.isArray(clip.tracks)||clip.tracks.length>60)throw Error('Invalid cat motion clip');
  const seen=new Set();
  for(const track of clip.tracks){
    const id=track.part+':'+track.channel;
    if(!catParts.includes(track.part)||!channels.includes(track.channel)||seen.has(id)||!Array.isArray(track.keys)||!track.keys.length||track.keys.length>120)throw Error('Invalid motion track');
    seen.add(id);let previous=-1;
    for(const key of track.keys){
      if(!Array.isArray(key)||key.length!==2||!key.every(Number.isFinite)||key[0]<0||key[0]>clip.duration||key[0]<=previous||Math.abs(key[1])>(track.channel==='angle'?180:48))throw Error('Invalid motion key');
      previous=key[0];
    }
  }
  return clip;
}
function sampleClip(clip,time){
  const t=clip.loop?((time%clip.duration)+clip.duration)%clip.duration:Math.max(0,Math.min(clip.duration,time));
  const pose=Object.fromEntries(catParts.map(id=>[id,{x:0,y:0,angle:0}]));
  for(const track of clip.tracks){
    let a=track.keys[0],b=a;
    for(const key of track.keys){if(key[0]<=t)a=key;else{b=key;break;}b=a;}
    const blend=b[0]===a[0]?0:(t-a[0])/(b[0]-a[0]);
    pose[track.part][track.channel]=a[1]+(b[1]-a[1])*blend;
  }
  return pose;
}

return {catParts,validateClip,sampleClip};
})();
// world/studio-renderer.mjs
__modules["world/studio-renderer.mjs"]=(()=>{
const __moduleURL=new URL("./world/studio-renderer.mjs",document.baseURI).href;
// The main world uses only the same detailed painted character rigs as the art studio.
// No procedural/pixel character renderer or fallback is permitted here.
const {createPaintedCompanion,catPresentation}=__modules["world/cat-painted.mjs"];
const {sampleClip,validateClip}=__modules["world/cat-motion.mjs"];
const paintedSpecies=Object.freeze(['cat','unicorn']);
const WORLD_PRESENTATION=Object.freeze({
  cat:Object.freeze({scale:.98,groundOffset:0,shadowWidth:58,shadowHeight:8}),
  unicorn:Object.freeze({scale:1.02,groundOffset:0,shadowWidth:66,shadowHeight:9}),
});
function worldPresentationFor(form){
  const value=WORLD_PRESENTATION[form];if(!value)throw Error('Unsupported painted world form: '+form);return value;
}
function drawCompanionGrounding(ctx,x,ground,state){
  const p=worldPresentationFor(state.form),sleeping=state.action==='sleep';
  const width=p.shadowWidth*(sleeping?1.18:1),height=p.shadowHeight*(sleeping?1.12:1);
  ctx.save();ctx.fillStyle='#403a342f';
  if(typeof ctx.ellipse==='function'&&typeof ctx.beginPath==='function'&&typeof ctx.fill==='function'){ctx.beginPath();ctx.ellipse(Math.round(x),Math.round(ground-2),width/2,height/2,0,0,Math.PI*2);ctx.fill();}
  else ctx.fillRect(Math.round(x-width/2),Math.round(ground-height/2-2),Math.round(width),Math.round(height));
  ctx.restore();return {width,height,groundOffset:p.groundOffset,scale:p.scale};
}
const packs=new Map();
let loading=null,clips=null,loadError=null;
const makeCanvas=(width,height)=>{
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;return canvas;
};
async function loadImage(file){return __loadBundledImage(file);}
async function loadJSON(file){return __bundledJSON(file);}
function loadPaintedCharacters(){
  if(loading)return loading;
  if(typeof document==='undefined'||typeof Image==='undefined'||typeof fetch!=='function')return Promise.resolve(false);
  loading=(async()=>{
    const [motion,catAtlas,catLayout,catLegs,catEars,unicornAtlas,unicornLayout,unicornMane]=await Promise.all([
      loadJSON('./cat-clips.json'),
      loadImage('cat-painted-atlas.png'),loadJSON('./cat-painted-layout.json'),loadImage('cat-profile-legs.png'),loadImage('cat-profile-ears.png'),
      loadImage('unicorn-atlas.png'),loadJSON('./unicorn-layout.json'),loadImage('unicorn-mane-v2.png')
    ]);
    for(const clip of Object.values(motion))validateClip(clip);
    clips=motion;
    packs.set('cat',createPaintedCompanion(makeCanvas,catAtlas,catLayout,{profileLegs:catLegs,profileEars:catEars},{palette:catLayout.colors.defaults}));
    packs.set('unicorn',createPaintedCompanion(makeCanvas,unicornAtlas,unicornLayout,{unicornMane},{palette:unicornLayout.colors.defaults}));
    return true;
  })().catch(error=>{loadError=error;return false;});
  return loading;
}
const paintedError=()=>loadError;
const paintedReady=()=>packs.size===paintedSpecies.length&&Boolean(clips);
const clipForAction=action=>action==='walk'?'walk':action==='wave'?'wave':'idle';
function drawPaintedWorld(ctx,x,ground,state,{reducedMotion=false,scale=1,lookAtViewer=false}={}){
  const art=packs.get(state.form);if(!art||!clips)return false;
  const clipName=clipForAction(state.action);
  const pose=sampleClip(clips[clipName],reducedMotion?0:state.time);
  const blink=!reducedMotion&&state.action!=='sleep'&&state.time%4.2>4;
  ctx.save();
  if(state.facing<0){ctx.translate(Math.round(x)*2,0);ctx.scale(-1,1);}
  art.draw(ctx,Math.round(x),Math.round(ground),pose,{scale:1.06*scale,...catPresentation(clipName,lookAtViewer),blink});
  ctx.restore();
  return true;
}
function drawPaintedPortrait(ctx,state,{x=180,y=210,scale=3,reducedMotion=false}={}){
  const art=packs.get(state.form);if(!art||!clips)return false;
  const blink=!reducedMotion&&state.action!=='sleep'&&state.time%4.2>4;
  art.portrait(ctx,Math.round(x),Math.round(y-12),{scale:.92*scale,blink});
  return true;
}

return {paintedSpecies,WORLD_PRESENTATION,worldPresentationFor,drawCompanionGrounding,loadPaintedCharacters,paintedError,paintedReady,clipForAction,drawPaintedWorld,drawPaintedPortrait};
})();
// world/scenery.mjs
__modules["world/scenery.mjs"]=(()=>{
const __moduleURL=new URL("./world/scenery.mjs",document.baseURI).href;
// A continuous, strictly side-on cave cross section with daylight at both ends.
// This module owns ONLY static scenery. Interactable objects are rendered in
// world-props.mjs and remain anchored by the simulation's object catalog.
const {rooms,WORLD_WIDTH}=__modules["world/simulation.mjs"];
const FLOOR=346;
const CAVE_START=235;
const CAVE_END=2165;
const CAVE_PRESENTATION_SCHEMA='tavi.cave-presentation/v2';
const paint=(ctx,x,y,w,h,color)=>{ctx.fillStyle=color;ctx.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h));};
function polygon(ctx,vertices,color){
  ctx.fillStyle=color;
  // Minimal Canvas test doubles can still exercise all scenery layers.
  if(typeof ctx.moveTo!=='function'||typeof ctx.lineTo!=='function'||typeof ctx.fill!=='function'){
    const xs=vertices.map(p=>p[0]),ys=vertices.map(p=>p[1]);
    ctx.fillRect(Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys));return;
  }
  ctx.beginPath();ctx.moveTo(...vertices[0]);for(const pair of vertices.slice(1))ctx.lineTo(...pair);ctx.closePath();ctx.fill();
}
function tree(ctx,x,height=80){
  paint(ctx,x-6,FLOOR-height+17,12,height-17,'#657557');
  polygon(ctx,[[x-43,FLOOR-height+45],[x,FLOOR-height-19],[x+44,FLOOR-height+45]],'#507d65');
  polygon(ctx,[[x-34,FLOOR-height+23],[x,FLOOR-height-39],[x+34,FLOOR-height+23]],'#679579');
  polygon(ctx,[[x-24,FLOOR-height+2],[x,FLOOR-height-50],[x+24,FLOOR-height+2]],'#85a787');
}
function exterior(ctx,left,right){
  paint(ctx,left,0,right-left,FLOOR,'#b9d9d1');
  polygon(ctx,[[left,220],[left+90,101],[left+220,242],[right,185],[right,FLOOR],[left,FLOOR]],'#a6b9a2');
  polygon(ctx,[[left,262],[left+80,171],[left+175,260],[right,226],[right,FLOOR],[left,FLOOR]],'#799e8a');
  paint(ctx,left,309,right-left,37,'#8bae83');
  for(let x=left+40;x<right;x+=108)tree(ctx,x,70+(x%3)*12);
}
function caveLight(ctx,from,to,side){
  // Flat translucent bands: light enters horizontally from each opening rather
  // than using perspective rays or a vanishing point.
  const width=to-from;
  paint(ctx,from,66,width,244,'#e7d9b322');
  paint(ctx,side==='left'?from:to-width*.62,90,width*.62,210,'#f7e8bd20');
  paint(ctx,side==='left'?from:to-width*.28,126,width*.28,172,'#fff0c928');
}
function mossShelf(ctx,x,y,w){
  paint(ctx,x,y,w,5,'#657b62');
  for(let i=0;i<Math.max(1,Math.floor(w/28));i++)paint(ctx,x+4+i*27,y-3-(i%2)*2,15,4,'#80946f');
}
function rockBand(ctx,from,to,index){
  const colors=['#978d88','#928985','#a39a8d','#99918e'];
  paint(ctx,from,50,to-from,296,colors[index%colors.length]);
  // Three horizontal depth bands keep the cave readable without perspective.
  polygon(ctx,[[from,64],[from+75,85],[from+205,63],[from+347,100],[to,74],[to,244],[from,249]],'#a7a198');
  polygon(ctx,[[from,174],[from+130,157],[from+267,194],[to,161],[to,316],[from,316]],'#afa89c');
  paint(ctx,from,242,to-from,70,'#a29a8f66');
  // A narrow, continuous side-on rocky walking axis.
  paint(ctx,from,312,to-from,34,'#968879');
  paint(ctx,from,336,to-from,10,'#756c64');
  for(let i=0;i<8;i++){
    const x=from+25+i*53;
    polygon(ctx,[[x,120+(i%3)*26],[x+24,130+(i%3)*26],[x+9,156+(i%3)*26]],'#8b8983');
    paint(ctx,x+((i*7)%17),305,15,3,'#bfb6a0');
    if(i%3===0)mossShelf(ctx,x-4,303,34);
  }
  // Stalagmites and hairline cracks stay behind the walking lane.
  for(let i=0;i<4;i++){
    const x=from+90+i*115;
    polygon(ctx,[[x-13,313],[x,272+(i%2)*15],[x+12,313]],'#7f817c');
  }
  for(let i=0;i<3;i++){
    const x=from+52+i*141,y=118+(i%2)*53;
    paint(ctx,x,y,2,28,'#766f72');paint(ctx,x+2,y+18,10,2,'#766f72');paint(ctx,x+10,y+18,2,15,'#766f72');
  }
}
function drawScenery(ctx,width,height,camera,time=0,reduced=false){
  ctx.save();ctx.translate(-Math.round(camera),0);
  paint(ctx,0,0,WORLD_WIDTH,height,'#b8ccc0');
  exterior(ctx,0,CAVE_START);exterior(ctx,CAVE_END,WORLD_WIDTH);
  // Each five-zone block is decor, not a separately enclosed room.
  for(let i=0;i<rooms.length;i++){
    const left=rooms[i].x,right=left+480;
    if(right<camera-100||left>camera+width+100)continue;
    if(left<CAVE_END&&right>CAVE_START)rockBand(ctx,Math.max(left,CAVE_START),Math.min(right,CAVE_END),i);
  }
  // Far cave wall and earth continue uninterrupted across the entire world.
  paint(ctx,CAVE_START,0,CAVE_END-CAVE_START,37,'#605c65');
  paint(ctx,CAVE_START,37,CAVE_END-CAVE_START,16,'#817b7c');
  caveLight(ctx,CAVE_START,CAVE_START+260,'left');caveLight(ctx,CAVE_END-260,CAVE_END,'right');
  paint(ctx,0,FLOOR,WORLD_WIDTH,Math.max(0,height-FLOOR),'#776b62');
  // A single contact strip makes characters and props read as standing on the
  // same axis, without introducing a perspective floor plane.
  paint(ctx,0,FLOOR-5,WORLD_WIDTH,5,'#a49a82');
  paint(ctx,0,FLOOR,WORLD_WIDTH,6,'#6d625a');
  for(let x=CAVE_START;x<CAVE_END;x+=92){
    const h=23+(x*7%37);
    polygon(ctx,[[x,53],[x+19,53],[x+10,53+h]],'#69636a');
  }
  // Bright, full-height openings at either end; never an overhead/3D view.
  polygon(ctx,[[CAVE_START-28,0],[CAVE_START+13,25],[CAVE_START+19,80],[CAVE_START+4,177],[CAVE_START+15,310],[CAVE_START-4,346],[CAVE_START+31,346],[CAVE_START+53,213],[CAVE_START+55,85],[CAVE_START+29,0]],'#68656a');
  polygon(ctx,[[CAVE_END+28,0],[CAVE_END-13,25],[CAVE_END-19,80],[CAVE_END-4,177],[CAVE_END-15,310],[CAVE_END+4,346],[CAVE_END-31,346],[CAVE_END-53,213],[CAVE_END-55,85],[CAVE_END-29,0]],'#68656a');
  for(let i=0;i<rooms.length;i++){
    const room=rooms[i],x=room.x;
    if(x+480<camera||x>camera+width)continue;
    ctx.fillStyle='#eae1cb';ctx.font='12px Georgia';ctx.fillText(room.name,x+26,394);
  }
  if(!reduced)for(let i=0;i<9;i++){
    const x=260+i*223+Math.sin(time*.3+i)*9;
    if(x>=CAVE_START&&x<=CAVE_END)paint(ctx,x,94+(i*29)%135+Math.sin(time+i)*5,2,2,'#fff1d7');
  }
  ctx.restore();
}

return {FLOOR,CAVE_START,CAVE_END,CAVE_PRESENTATION_SCHEMA,drawScenery};
})();
// world/world-props.mjs
__modules["world/world-props.mjs"]=(()=>{
const __moduleURL=new URL("./world/world-props.mjs",document.baseURI).href;
// Independently drawn and hit-tested world props. The catalog owns each ID,
// destination and availability; neither the cave background nor these visuals
// create gameplay objects or modify persisted creature state.
const {objects,isObjectAvailable}=__modules["world/object-catalog.mjs"];
const {FLOOR}=__modules["world/scenery.mjs"];
const PROP_LAYOUT=Object.freeze({
  snack:Object.freeze({halfWidth:49,top:263,bottom:FLOOR}),
  table:Object.freeze({halfWidth:70,top:267,bottom:FLOOR}),
  honey:Object.freeze({halfWidth:38,top:260,bottom:FLOOR}),
  bath:Object.freeze({halfWidth:79,top:263,bottom:FLOOR}),
  bed:Object.freeze({halfWidth:84,top:275,bottom:FLOOR}),
  toy:Object.freeze({halfWidth:43,top:295,bottom:FLOOR}),
});
const fill=(c,x,y,w,h,color)=>{c.fillStyle=color;c.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h));};
function objectHitbox(item){
  const entry=typeof item==='string'?objects.find(obj=>obj.id===item):item;
  if(!entry||!PROP_LAYOUT[entry.id])return null;
  const layout=PROP_LAYOUT[entry.id];
  return {id:entry.id,left:entry.x-layout.halfWidth,right:entry.x+layout.halfWidth,top:layout.top,bottom:layout.bottom};
}
function hitTestObject(worldX,screenY,state){
  if(!Number.isFinite(worldX)||!Number.isFinite(screenY))return null;
  return objects.filter(item=>isObjectAvailable(state,item.id)).find(item=>{
    const bounds=objectHitbox(item);
    return worldX>=bounds.left&&worldX<=bounds.right&&screenY>=bounds.top&&screenY<=bounds.bottom;
  })?.id??null;
}
function drawPropGrounding(c,obj,state){
  const layout=PROP_LAYOUT[obj.id];if(!layout)return;
  const available=isObjectAvailable(state,obj.id);
  const width=Math.max(28,Math.round(layout.halfWidth*1.35));
  fill(c,obj.x-width/2,FLOOR-7,width,5,available?'#4f473f2e':'#4f473f18');
  fill(c,obj.x-width*.35,FLOOR-4,width*.7,2,available?'#d1c2a65c':'#c0b6a45c');
}
function drawObject(c,obj,state){
  const x=obj.x;
  if(obj.id==='snack'){
    fill(c,x-31,314,62,12,'#785e54');fill(c,x-4,323,8,23,'#816b59');
    fill(c,x-33,298,66,17,'#bca58c');fill(c,x-29,290,58,13,'#d6c3a5');
    for(const [dx,dy,col] of [[-15,286,'#a65e59'],[1,282,'#e6bf6b'],[16,287,'#8eaa6e']]){
      fill(c,x+dx-9,dy,18,11,col);fill(c,x+dx,dy-3,2,5,'#536b48');
    }
  }else if(obj.id==='table'){
    fill(c,x-63,300,126,13,'#b3997c');fill(c,x-52,313,12,33,'#775b54');fill(c,x+38,313,12,33,'#775b54');
    fill(c,x-39,292,79,8,'#e9d5ac');fill(c,x-13,286,27,6,'#fbebc5');
  }else if(obj.id==='honey'){
    fill(c,x-30,318,60,9,'#796a55');fill(c,x-5,327,10,19,'#75614c');
    const remaining=state?.objectState?.honey?.usesRemaining??10;
    fill(c,x-16,283,32,35,remaining>0?'#bc8749':'#99988b');
    fill(c,x-19,279,38,6,'#e8c37d');fill(c,x-14,292,28,10,remaining>0?'#e5b954':'#d2d0bf');
    fill(c,x-9,272,18,7,'#755b4b');
  }else if(obj.id==='bath'){
    fill(c,x-73,318,146,19,'#c7c5b1');fill(c,x-68,301,136,21,'#78b1ae');
    fill(c,x-75,301,150,9,'#dedbc7');fill(c,x-70,337,14,9,'#a6a492');fill(c,x+56,337,14,9,'#a6a492');
    fill(c,x+53,281,7,20,'#8d9f90');fill(c,x+43,277,17,6,'#8d9f90');
  }else if(obj.id==='bed'){
    fill(c,x-80,300,160,39,'#9e7b76');fill(c,x-75,286,150,29,'#a69caf');
    fill(c,x-73,280,43,17,'#f0ddbd');fill(c,x-22,291,91,21,'#7d91a2');
    fill(c,x-80,337,13,9,'#675c58');fill(c,x+67,337,13,9,'#675c58');
  }else if(obj.id==='toy'){
    fill(c,x-31,307,62,29,'#7f9982');fill(c,x-28,299,56,28,'#d7b2a1');
    fill(c,x-25,306,50,9,'#e7cdab');fill(c,x-3,299,7,29,'#f0e1c1');
    fill(c,x-31,331,62,5,'#657d62');
  }
}
function drawWorldObjects(ctx,camera,state,viewportWidth=960){
  ctx.save();ctx.translate(-Math.round(camera),0);
  for(const obj of objects){
    const bounds=objectHitbox(obj);
    if(bounds.right<camera||bounds.left>camera+viewportWidth)continue;
    drawPropGrounding(ctx,obj,state);
    drawObject(ctx,obj,state);
    ctx.fillStyle=isObjectAvailable(state,obj.id)?'#f2e6d1':'#d2c6ba';
    ctx.font='11px Georgia';ctx.textAlign='center';ctx.fillText(obj.label,obj.x,253);
  }
  ctx.restore();
}
function drawWorldForeground(ctx,camera,state){
  // The lip of the spring is a foreground occluder for bathing, not backdrop.
  if(state.action==='bathe'&&state.target==='bath'){
    const x=objects.find(obj=>obj.id==='bath').x-camera;
    fill(ctx,x-73,318,146,18,'#dcd8c5');fill(ctx,x-62,313,124,5,'#9ecac2');
  }
}

return {PROP_LAYOUT,objectHitbox,hitTestObject,drawWorldObjects,drawWorldForeground};
})();
// world/growth.mjs
__modules["world/growth.mjs"]=(()=>{
const __moduleURL=new URL("./world/growth.mjs",document.baseURI).href;
/**
 * Tavi Companion lifetime growth/v1. A view of an individual's completed
 * experiences, not a clock, birth date, breeding generation or second genome.
 * Stateless so reopening Tavi cannot cause catch-up or mismatched milestones.
 */
const {TRAIT_KEYS,validateGenome,phenotypeFor}=__modules["world/genetics.mjs"];
const GROWTH_SCHEMA='tavi.companion.growth/v1';
const GROWTH_STAGES=Object.freeze([
  Object.freeze({at:0,name:'Finding a home',description:'Every new experience helps shape who they become.'}),
  Object.freeze({at:12,name:'Finding their rhythm',description:'Small preferences are starting to become familiar habits.'}),
  Object.freeze({at:40,name:'Growing into themselves',description:'Their own ways of exploring, resting and connecting are taking shape.'}),
  Object.freeze({at:100,name:'A distinctive companion',description:'A lifetime of little experiences has given them a recognizable character.'}),
]);
const FOCUS=Object.freeze({
  curiosity:'exploration',sociability:'connection',playfulness:'play',
  calmness:'quiet moments',appetite:'food and treats',stamina:'activity and rest',
});
function growthForGenome(genome){
  validateGenome(genome);
  const experiences=genome.revision;
  let stageIndex=0;
  for(let i=1;i<GROWTH_STAGES.length;i++)if(experiences>=GROWTH_STAGES[i].at)stageIndex=i;
  const stage=GROWTH_STAGES[stageIndex],next=GROWTH_STAGES[stageIndex+1]??null;
  const levels=phenotypeFor(genome);
  // The standout trait is descriptive, not a judgment or a hidden score.
  // Stable canonical trait ordering also prevents ties from flickering.
  const focus=TRAIT_KEYS.reduce((best,key)=>levels[key]>levels[best]?key:best,TRAIT_KEYS[0]);
  const progress=next?(experiences-stage.at)/(next.at-stage.at):1;
  return Object.freeze({
    schema:GROWTH_SCHEMA,stageIndex,stage:stage.name,description:stage.description,
    experiences, nextAt:next?.at??null, nextStage:next?.name??null,
    progress:Math.max(0,Math.min(1,progress)),focus:FOCUS[focus],
  });
}

return {GROWTH_SCHEMA,GROWTH_STAGES,growthForGenome};
})();
// world/companion-preview.mjs
__modules["world/companion-preview.mjs"]=(()=>{
const __moduleURL=new URL("./world/companion-preview.mjs",document.baseURI).href;
/** Only a painted visual and a display name are exported to Tavi's main shell.
 * No genome, care/need data, messages, credentials, or other private state.
 */
const PREVIEW_SCHEMA='tavi.companion.preview/v1';
const PREVIEW_PIXEL_SIZE=80;
const PREVIEW_DATA_LIMIT=90000;
function normalizePreviewName(input){
  return typeof input==='string'?input.trim().slice(0,32):'';
}
function makeCompanionPreview({name,form,source,makeCanvas=()=>document.createElement('canvas')}){
  if(!['cat','unicorn'].includes(form))throw Error('Unsupported painted form');
  if(!source||typeof source.width!=='number'||typeof source.height!=='number'||source.width<1||source.height<1)throw Error('Missing portrait canvas');
  const out=makeCanvas();out.width=PREVIEW_PIXEL_SIZE;out.height=PREVIEW_PIXEL_SIZE;
  const ctx=out.getContext('2d');if(!ctx)throw Error('Portrait context unavailable');
  ctx.imageSmoothingEnabled=true;
  ctx.drawImage(source,0,0,source.width,source.height,0,0,PREVIEW_PIXEL_SIZE,PREVIEW_PIXEL_SIZE);
  const image=out.toDataURL('image/png');
  if(!/^data:image\/png;base64,iVBORw0KGgo[A-Za-z0-9+/]*={0,2}$/.test(image)||image.length>PREVIEW_DATA_LIMIT)throw Error('Invalid painted preview image');
  return {schema:PREVIEW_SCHEMA,name:normalizePreviewName(name),form,image};
}

return {PREVIEW_SCHEMA,PREVIEW_PIXEL_SIZE,PREVIEW_DATA_LIMIT,normalizePreviewName,makeCompanionPreview};
})();
// world/host-session.mjs
__modules["world/host-session.mjs"]=(()=>{
const __moduleURL=new URL("./world/host-session.mjs",document.baseURI).href;
/** Companion-side lifecycle helpers. Tavi owns authentication, sandboxing,
 * installed-extension grants and account/server namespacing. No credentials
 * or private simulation state leave this module except via storage.private.
 */
async function restoreEmbeddedCompanion({host,key,decode,selectionMade,applyRestored,queuePortrait}){
  if(!host?.canStore)return {status:'storage-unavailable'};
  try{
    const saved=decode(await host.read(key));
    if(!saved)return {status:'no-valid-session'};
    // A choice made during the asynchronous Tavi handshake must win.
    if(selectionMade())return {status:'selection-kept'};
    applyRestored(saved);
    // An existing portrait in Tavi may be missing or stale (e.g. host update).
    // Queue only after state and name have been restored; rendering assets may
    // finish asynchronously, in which case app.mjs queues again on readiness.
    if(saved.chosen)queuePortrait();
    return {status:'restored',migrated:!!saved.migrated};
  }catch{return {status:'storage-error'};}
}

/** A known-good private-storage session is required before closing when Tavi
 * granted storage.private. Preview is cosmetic and must never block Home.
 */
async function closeEmbeddedCompanion({host,save,publishPortrait}){
  if(!host)return {closed:false,reason:'no-host'};
  if(host.canStore){
    try{if(await save()!==true)return {closed:false,reason:'save-failed'};}
    catch{return {closed:false,reason:'save-failed'};}
  }
  try{await publishPortrait();}catch{/* Optional contribution. */}
  try{await host.close();return {closed:true};}
  catch{return {closed:false,reason:'close-failed'};}
}

return {restoreEmbeddedCompanion,closeEmbeddedCompanion};
})();
// world/cloud-session.mjs
__modules["world/cloud-session.mjs"]=(()=>{
const __moduleURL=new URL("./world/cloud-session.mjs",document.baseURI).href;
/** Server-owned singleton, strict CAS revision and reset epoch.
 * This never chooses an offline/local save as authority or auto-merges forks.
 */
const CLOUD_SCHEMA='tavi.companion.cloud/v1';
const goodMeta=r=>r&&r.schema===CLOUD_SCHEMA&&typeof r.epoch==='string'&&/^[a-zA-Z0-9_-]{1,64}$/.test(r.epoch)&&Number.isSafeInteger(r.revision)&&r.revision>=0;
function createCloudSession({load,save,decode}){
 let epoch=null,revision=null,ready=false,blocked=false;
 function accept(response){
  if(!goodMeta(response)||!(response.snapshot===null||typeof response.snapshot==='string'))throw Error('Invalid Companion server response');
  const decoded=response.snapshot===null?null:decode(response.snapshot);
  if(response.snapshot!==null&&(!decoded||!decoded.chosen))throw Error('Invalid server Companion state');
  epoch=response.epoch;revision=response.revision;ready=true;blocked=false;
  return {snapshot:response.snapshot,decoded,revision,epoch};
 }
 return {
  get ready(){return ready;},get blocked(){return blocked;},get revision(){return revision;},get epoch(){return epoch;},
  async load(){return accept(await load());},
  async poll(){
   if(!ready)throw Error('Companion server not loaded');
   const response=await load();
   if(!goodMeta(response))throw Error('Invalid Companion server response');
   if(response.epoch===epoch&&response.revision===revision)return null;
   blocked=true;
   return accept(response);
  },
  async commit(snapshot){
   if(!ready||blocked)throw Error('Companion cannot save before authoritative server loading');
   if(typeof snapshot!=='string'||!decode(snapshot)?.chosen)throw Error('Invalid Companion save');
   try{
    const response=await save(snapshot,revision,epoch);
    if(!goodMeta(response)||response.epoch!==epoch||response.revision!==revision+1)throw Error('Invalid Companion server acknowledgement');
    revision=response.revision;return response;
   }catch(error){blocked=true;throw error;}
  }
 };
}

return {CLOUD_SCHEMA,createCloudSession};
})();
// world/app.mjs
__modules["world/app.mjs"]=(()=>{
const __moduleURL=new URL("./world/app.mjs",document.baseURI).href;
const {createWorld,objects,isObjectAvailable,rooms,WORLD_WIDTH}=__modules["world/simulation.mjs"];
const {createLocalCompanionEngine}=__modules["world/engine-port.mjs"];
const {connectTaviHost}=__modules["world/tavi-host.mjs"];
const {SESSION_STORAGE_KEY,encodeSession,decodeSession}=__modules["world/session-codec.mjs"];
const {drawPaintedWorld,drawPaintedPortrait,drawCompanionGrounding,worldPresentationFor,loadPaintedCharacters,paintedReady,paintedError}=__modules["world/studio-renderer.mjs"];
const {drawScenery,FLOOR}=__modules["world/scenery.mjs"];
const {drawWorldObjects,drawWorldForeground,hitTestObject}=__modules["world/world-props.mjs"];
const {startingForms,applyForm}=__modules["world/forms.mjs"];
const {TRAIT_KEYS}=__modules["world/genetics.mjs"];
const {growthForGenome}=__modules["world/growth.mjs"];
const {describeHabits,describeConsequences,nextActivityOutlook}=__modules["world/creature-profile.mjs"];
const {makeCompanionPreview}=__modules["world/companion-preview.mjs"];
const {restoreEmbeddedCompanion,closeEmbeddedCompanion}=__modules["world/host-session.mjs"];
const {createCloudSession}=__modules["world/cloud-session.mjs"];
const $=id=>document.getElementById(id);
// A new individual gets a locally generated genotype; the test engine keeps a
// deterministic seed for reproducible native-adapter contract tests.
const freshSeed=globalThis.crypto?.getRandomValues?globalThis.crypto.getRandomValues(new Uint32Array(1))[0]:(Date.now()>>>0);
let engine=createLocalCompanionEngine({state:createWorld({genomeSeed:freshSeed})});
let state=engine.state;
let taviHost=null,cloud=null,cloudPending=typeof window!=='undefined'&&window.parent!==window,cloudFailed=false,saveTimer=null,saveInFlight=null,lastSaved=null,nextAutoSave=20,portraitTimer=null;
let chosen=false,name='',camera=230,following=true,lastTime=0,viewportWidth=960,viewportHeight=422,drag=null,lastMessage='',lastMemory='',lastTraitRevision=-1,lastHabitSignature='',lastConsequenceSignature='',lastOutlookSignature='';
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const canvas=$('world'),ctx=canvas.getContext('2d');
const previews=[];
// Tavi's extension host is OPTIONAL. Standalone preview remains usable and never
// talks to LoopRD or demands an account token. Host I/O happens out of the frame loop.
function sendCommand(type,value){
  if(cloudPending||cloudFailed)return false;
  const result=engine.command(type,value);
  if(result&&chosen)scheduleSave();
  return result;
}
// Synchronize only selected painted appearance. Never send genes/needs or chat data.
function queuePortrait(){
  if(!chosen||cloudPending||cloudFailed||!taviHost?.publishPortrait||portraitTimer)return;
  portraitTimer=setTimeout(()=>{portraitTimer=null;void publishPortrait();},650);
}
async function publishPortrait(){
  if(!chosen||cloudPending||cloudFailed||!taviHost?.publishPortrait||!paintedReady())return;
  try{
    portrait();
    const preview=makeCompanionPreview({name,form:state.form,source:$('portrait')});
    await taviHost.publishPortrait(preview);
  }catch{ /* Companions stays fully usable even if Tavi refuses this optional UI contribution. */ }
}
function scheduleSave(){
  if(!taviHost?.canStore||cloudPending||cloudFailed||!chosen||saveTimer)return;
  saveTimer=setTimeout(()=>{saveTimer=null;void saveSession();},2500);
}
async function saveSession(){
  if(!taviHost?.canStore||!chosen)return !cloudPending&&!cloudFailed;
  if(saveInFlight){try{await saveInFlight;}catch{ /* Retry with current state. */ }}
  let snapshot;
  try{snapshot=encodeSession({chosen,name,state});}catch{return false;}
  if(snapshot===lastSaved)return true;
  const current=cloud?cloud.commit(snapshot):taviHost.write(SESSION_STORAGE_KEY,snapshot);
  saveInFlight=current;
  try{await current;lastSaved=snapshot;return true;}
  catch{cloudFailed=true; $('art-status').textContent='Companion could not be saved to the server. Reopen from Tavi to reload the latest authoritative copy.';return false; }
  finally{if(saveInFlight===current)saveInFlight=null;}
}
function applyCloudSession(record){
  if(record.decoded){
    const saved=record.decoded;
    engine=createLocalCompanionEngine({state:saved.state});state=engine.state;
    chosen=true;name=saved.name;
    $('name').value=name;$('care').checked=state.care;
    nextAutoSave=state.time+20;
    lastSaved=record.snapshot;
  }else{
    // Operator reset or fresh account: older device-local snapshots MUST NOT
    // silently recreate this character. The server remains authoritative.
    chosen=false;name='';engine=createLocalCompanionEngine({state:createWorld({genomeSeed:freshSeed})});state=engine.state;
    $('name').value='';lastSaved=null;
    nextAutoSave=state.time+20;
  }
  lastTraitRevision=-1;lastHabitSignature='';lastConsequenceSignature='';lastOutlookSignature='';
  syncControls();updateText();
  if(chosen)queuePortrait();
}
async function initializeTaviHost(){
  const connection=await connectTaviHost();
  if(!connection){
    if(typeof window!=='undefined'&&window.parent!==window){cloudFailed=true;cloudPending=false;
      $('art-status').textContent='This Tavi build does not provide secure server Companion storage. Update Tavi and retry.';syncControls();}
    else cloudPending=false;
    return;
  }
  taviHost=connection;
  $('return-to-tavi').hidden=false;
  $('return-to-tavi').disabled=false;
  // There is deliberately no device-local fallback for an embedded account.
  cloud=createCloudSession({load:connection.load,save:connection.save,decode:decodeSession});
  try{
    const record=await cloud.load();
    cloudPending=false;
    applyCloudSession(record);
    // Polling detects updates from the other device and operator reset. Tavi
    // additionally enforces epoch+revision on EVERY write.
    setInterval(async()=>{
      if(document.hidden||cloudPending||cloudFailed||saveInFlight)return;
      try{
        const refreshed=await cloud.poll();
        if(refreshed){
          if(saveTimer){clearTimeout(saveTimer);saveTimer=null;}
          applyCloudSession(refreshed);
          $('art-status').textContent=refreshed.snapshot===null?'Your companion was reset by the server. You may choose a new one.':'Updated your companion from another device.';
        }
      }catch{cloudFailed=true;$('art-status').textContent='Server sync interrupted. Reopen Companion to reconnect.';syncControls();}
    },30000);
  }catch{
    cloudFailed=true;cloudPending=false;
    $('art-status').textContent='Unable to load your server companion. No local replacement will be created.';syncControls();
  }
}
$('return-to-tavi').addEventListener('click',async()=>{
  if(!taviHost)return;
  $('return-to-tavi').disabled=true;
  if(saveTimer){clearTimeout(saveTimer);saveTimer=null;}
  if(portraitTimer){clearTimeout(portraitTimer);portraitTimer=null;}
  const result=await closeEmbeddedCompanion({host:taviHost,save:saveSession,publishPortrait});
  if(!result.closed){
    $('return-to-tavi').disabled=false;
    $('art-status').textContent=result.reason==='save-failed'
      ?'Could not save your companion. Please try Back to Tavi again or use Tavi’s main Home navigation.'
      :'Could not close the panel. Use Tavi’s main Home navigation.';
  }
});
function renderTraits(){
  if(!chosen||lastTraitRevision===state.genome.revision)return;
  lastTraitRevision=state.genome.revision;
  $('trait-list').replaceChildren();
  for(const key of TRAIT_KEYS){
    const li=document.createElement('li');
    li.textContent=`${key[0].toUpperCase()+key.slice(1)}: ${Math.round(state.phenotype[key]*100)}%`;
    $('trait-list').append(li);
  }
  const growth=growthForGenome(state.genome);
  $('trait-evolution').textContent=`${growth.experiences} evolving experiences · changes persist with this companion`;
  $('growth-stage').textContent=growth.stage;
  $('growth-description').textContent=growth.description;
  $('growth-focus').textContent=`Currently drawn toward ${growth.focus}.`;
  $('growth-progress').value=growth.progress;
  $('growth-progress').setAttribute('aria-valuetext',growth.nextAt?`${growth.experiences} of ${growth.nextAt} experiences toward ${growth.nextStage}`:`${growth.experiences} experiences; all current milestones reached`);
  $('growth-next').textContent=growth.nextAt?`${growth.nextAt-growth.experiences} more evolving experiences toward ${growth.nextStage}`:'All current milestones reached; evolution continues.';
}
function renderHabits(){
  if(!chosen)return;
  const items=describeHabits(state,objects);
  const signature=JSON.stringify(items);
  if(signature===lastHabitSignature)return;
  lastHabitSignature=signature;
  const list=$('habit-list');list.replaceChildren();
  if(!items.length){
    const li=document.createElement('li');li.textContent='Favorite places will emerge through play.';list.append(li);
  }else for(const item of items){
    const li=document.createElement('li');
    li.textContent=`${item.label} · ${item.visits} visits · ${item.affinity>=16?'a favorite':item.affinity>=8?'becoming familiar':'getting acquainted'}`;
    list.append(li);
  }
}
function renderConsequences(){
  if(!chosen)return;
  const observations=describeConsequences(state,objects);
  const signature=JSON.stringify(observations);
  if(signature===lastConsequenceSignature)return;
  lastConsequenceSignature=signature;
  const list=$('consequence-list');list.replaceChildren();
  if(!observations.length){
    const li=document.createElement('li');li.textContent='First impressions will form after completed activities.';list.append(li);
  }else for(const item of observations){
    const li=document.createElement('li');
    const impression=item.score>=8?'often enjoyable':item.score<=-8?'not very rewarding lately':
      item.unfamiliar>0&&!item.pleasant&&!item.disappointing?'still discovering':'still learning';
    li.textContent=`${item.label} · ${impression} · ${item.pleasant} pleasant, ${item.unfamiliar} unfamiliar, ${item.disappointing} disappointing`;
    list.append(li);
  }
}
function renderActivityOutlook(){
  if(!chosen||cloudPending||cloudFailed)return;
  const outlook=nextActivityOutlook(state,objects);
  const choices=outlook.choices.slice(0,3);
  const signature=JSON.stringify({mode:outlook.mode,paused:state.paused,choices:choices.map(c=>[c.id,c.reason,c.chance===null?null:Math.round(c.chance*100)])});
  if(signature===lastOutlookSignature)return;
  lastOutlookSignature=signature;
  const list=$('activity-outlook-list');list.replaceChildren();
  $('activity-outlook-intro').textContent=state.paused?'Taking a quiet break from exploring.':outlook.mode==='care'?'A few needs may guide the next stop.':'Each visit and little memory can change what feels interesting.';
  if(!choices.length){const li=document.createElement('li');li.textContent='Enjoying a quiet moment for now.';list.append(li);return;}
  for(const item of choices){
    const li=document.createElement('li');
    li.textContent=outlook.mode==='care'
      ?`${item.label} · ${item.reason}`
      :`${item.label} · about ${Math.round(item.chance*100)}% chance next time · ${item.reason}`;
    list.append(li);
  }
}
function syncControls(){
  $('welcome').hidden=chosen||cloudPending||cloudFailed;
  $('companion-name').textContent=name||'Your companion';
  $('portrait-hint').textContent=chosen?(name||'Your companion'):'? Choose a companion';
  $('portrait-button').setAttribute('aria-label',chosen?`Face portrait of ${name||'your companion'}. Change starting look.`:'Choose your companion');
  $('needs').hidden=!state.care;
  $('traits').hidden=!chosen;
  $('growth').hidden=!chosen;
  $('habits').hidden=!chosen;
  $('consequences').hidden=!chosen;
  $('activity-outlook').hidden=!chosen;
  renderHabits();
  renderConsequences();
  renderActivityOutlook();
  renderTraits();
  $('form').value=state.form;
  $('follow').setAttribute('aria-pressed',String(following));
  $('pause').setAttribute('aria-pressed',String(state.paused));$('pause').textContent=state.paused?'Resume world':'Pause world';
  for(const control of document.querySelectorAll('.companion-controls button, .companion-controls input, .companion-controls select'))control.disabled=!chosen||cloudPending||cloudFailed;
  for(const button of document.querySelectorAll('[data-object]'))button.disabled=!chosen||cloudPending||cloudFailed||!isObjectAvailable(state,button.dataset.object);
  $('refill-honey').disabled=!chosen||cloudPending||cloudFailed||state.objectState.honey.usesRemaining===10;
}
function updateText(){
  if(chosen && lastMessage!==state.message){$('thought').textContent=state.message;lastMessage=state.message;}
  $('emotion').textContent=chosen?`${state.emotion.toUpperCase()} · ${state.action==='walk'?'FOLLOWING A LITTLE CURIOSITY':state.action==='idle'?'AT HOME':state.action.toUpperCase()}`:'A LITTLE LIFE, AT ITS OWN PACE';
  const memoryKey=state.memories.join('|');
  if(lastMemory!==memoryKey){lastMemory=memoryKey;$('memories').replaceChildren();for(const text of state.memories){const li=document.createElement('li');li.textContent=text;$('memories').append(li);}}
  for(const [key,value]of Object.entries(state.needs)){$('need-'+key).value=value;}
  $('honey-remaining').textContent=`${state.objectState.honey.usesRemaining} servings left`;
  for(const button of document.querySelectorAll('[data-object]'))button.disabled=!chosen||cloudPending||cloudFailed||!isObjectAvailable(state,button.dataset.object);
  $('refill-honey').disabled=!chosen||cloudPending||cloudFailed||state.objectState.honey.usesRemaining===10;
}
function resize(){
  viewportWidth=Math.max(280,Math.round($('viewport').clientWidth));viewportHeight=$('viewport').clientHeight;
  const density=Math.min(2,Math.ceil(devicePixelRatio||1));canvas.width=viewportWidth*density;canvas.height=viewportHeight*density;
  ctx.setTransform(density,0,0,density,0,0);ctx.imageSmoothingEnabled=false;$('pan').max=Math.max(0,WORLD_WIDTH-viewportWidth);
}
function portrait(){
  const p=$('portrait').getContext('2d');p.clearRect(0,0,360,360);p.imageSmoothingEnabled=false;
  if(chosen)drawPaintedPortrait(p,state,{reducedMotion:reduced.matches});
  else {p.font='76px Georgia';p.fillStyle='#8c9d77';p.textAlign='center';p.fillText('?',180,185);}
}
function frame(timestamp){
  const delta=lastTime?Math.min(.1,(timestamp-lastTime)/1000):0;lastTime=timestamp;
  if(!document.hidden){
    if(chosen&&!cloudPending&&!cloudFailed)engine.advance(delta);
    if(chosen&&state.time>=nextAutoSave){nextAutoSave=state.time+20;scheduleSave();}
    if(chosen && following)camera+=(state.x-viewportWidth/2-camera)*(reduced.matches?1:Math.min(1,delta*3));
    camera=Math.max(0,Math.min(Math.max(0,WORLD_WIDTH-viewportWidth),camera));
    ctx.clearRect(0,0,viewportWidth,viewportHeight);drawScenery(ctx,viewportWidth,viewportHeight,camera,state.time,reduced.matches);drawWorldObjects(ctx,camera,state,viewportWidth);
    if(chosen){
      ctx.save();
      if(state.action==='bathe'&&state.target==='bath'){
        ctx.beginPath();ctx.rect(0,0,viewportWidth,318);ctx.clip();
      }
      const presentation=worldPresentationFor(state.form),ground=FLOOR+presentation.groundOffset;
      drawCompanionGrounding(ctx,state.x-camera,ground,state);
      drawPaintedWorld(ctx,state.x-camera,ground,state,{reducedMotion:reduced.matches,scale:presentation.scale,lookAtViewer:state.action!=='sleep'&&(state.time<(state.lookUntil??0)||(['idle','sit'].includes(state.action)&&state.time%14>=9))});ctx.restore();
    }
    drawWorldForeground(ctx,camera,state);portrait();
    if($('selection').open)for(const preview of previews){
      preview.state.time=timestamp/1000;
      const context=preview.canvas.getContext('2d');context.clearRect(0,0,360,320);
      drawPaintedWorld(context,180,292,preview.state,{reducedMotion:reduced.matches,scale:2});
    }
    $('pan').value=Math.round(camera);
    $('where').textContent=rooms.filter(r=>r.x+480>camera&&r.x<camera+viewportWidth).map(r=>r.name).join(' · ');
    renderTraits();renderHabits();renderConsequences();renderActivityOutlook();updateText();
  }
  requestAnimationFrame(frame);
}
function pan(value){following=false;camera=Math.max(0,Math.min(WORLD_WIDTH-viewportWidth,value));syncControls();}
$('pan-left').addEventListener('click',()=>pan(camera-250));$('pan-right').addEventListener('click',()=>pan(camera+250));
$('pan').addEventListener('input',()=>pan(Number($('pan').value)));
$('follow').addEventListener('click',()=>{following=!following;syncControls();});
canvas.addEventListener('pointerdown',event=>{drag={x:event.clientX,y:event.clientY,camera,moved:false};});
canvas.addEventListener('pointermove',event=>{
  if(!drag)return;const dx=event.clientX-drag.x,dy=event.clientY-drag.y;
  if(Math.abs(dx)>8 && Math.abs(dx)>Math.abs(dy)){drag.moved=true;canvas.setPointerCapture(event.pointerId);pan(drag.camera-dx);}
});
canvas.addEventListener('pointerup',event=>{
  if(!drag)return;
  if(!drag.moved&&chosen){const bounds=canvas.getBoundingClientRect();const x=event.clientX-bounds.left+camera,y=event.clientY-bounds.top;const id=hitTestObject(x,y,state);if(id)sendCommand('invite',id);}
  drag=null;
});
canvas.addEventListener('pointercancel',()=>{drag=null;});
canvas.addEventListener('keydown',event=>{if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();pan(camera+(event.key==='ArrowLeft'?-180:180));}});
$('pause').addEventListener('click',()=>{sendCommand('set-paused',!state.paused);syncControls();});
for(const button of document.querySelectorAll('[data-object]'))button.addEventListener('click',()=>{if(chosen)sendCommand('invite',button.dataset.object);});
$('refill-honey').addEventListener('click',()=>{if(chosen)sendCommand('refill','honey');});
$('pet').addEventListener('click',()=>{if(chosen)sendCommand('express','pet');});$('wave').addEventListener('click',()=>{if(chosen)sendCommand('express','wave');});
$('look').addEventListener('click',()=>{if(chosen)sendCommand('express','look');});
$('name').addEventListener('input',()=>{name=$('name').value.trim().slice(0,32);syncControls();scheduleSave();queuePortrait();});
$('form').addEventListener('change',()=>{sendCommand('choose-form',$('form').value);syncControls();queuePortrait();});
$('care').addEventListener('change',()=>{sendCommand('set-care',$('care').checked);syncControls();});
function openSelection(){if(cloudPending||cloudFailed)return;if(!$('selection').open)$('selection').showModal();}
$('portrait-button').addEventListener('click',openSelection);$('choose').addEventListener('click',openSelection);$('close-selection').addEventListener('click',()=>$('selection').close());
for(const button of document.querySelectorAll('[data-form]')){
  const preview=createWorld();applyForm(preview,button.dataset.form);preview.facing=1;
  const previewCanvas=button.querySelector('canvas');
  drawPaintedWorld(previewCanvas.getContext('2d'),180,292,preview,{reducedMotion:true,scale:2});
  previews.push({canvas:previewCanvas,state:preview});
  button.setAttribute('aria-label',`${startingForms[button.dataset.form].label}: ${startingForms[button.dataset.form].description}`);
  button.addEventListener('click',()=>{if(cloudPending||cloudFailed)return;sendCommand('choose-form',button.dataset.form);chosen=true;$('selection').close();syncControls();scheduleSave();queuePortrait();$('wave').focus();});
}
for(const [key,value]of Object.entries(state.needs)){
  const label=document.createElement('label');label.className='need';label.textContent=key[0].toUpperCase()+key.slice(1);
  const meter=document.createElement('meter');meter.id='need-'+key;meter.min=0;meter.max=100;meter.value=value;meter.setAttribute('aria-label',key);label.append(meter);$('needs').append(label);
}
new ResizeObserver(resize).observe($('viewport'));
document.addEventListener('visibilitychange',()=>{lastTime=0;if(document.hidden)void saveSession();});
resize();syncControls();requestAnimationFrame(frame);
void initializeTaviHost();
// Asset loading is explicit. Never substitute an unrelated or generated creature if it fails.
loadPaintedCharacters().then(ok=>{
  $('art-status').textContent=ok?'Painted character artwork ready':'Painted artwork unavailable. Check the preview files and reload.';
  if(ok)queuePortrait();
}).catch(()=>{$('art-status').textContent='Painted artwork unavailable. Check the preview files and reload.';});

return {};
})();
})();
