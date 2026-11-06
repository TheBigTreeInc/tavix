'use strict';
(()=>{
const __modules=Object.create(null);
const __inlineConfigurations={"cat-clips.json":{"idle":{"schema":1,"rig":"cat-v1","duration":4,"loop":true,"tracks":[{"part":"torso","channel":"y","keys":[[0,0],[2,-1],[4,0]]},{"part":"head","channel":"y","keys":[[0,0],[2,-1],[4,0]]},{"part":"tail","channel":"angle","keys":[[0,-5],[2,7],[4,-5]]},{"part":"earRight","channel":"angle","keys":[[0,0],[2.8,0],[3,12],[3.2,0],[4,0]]}]},"walk":{"schema":1,"rig":"cat-v1","duration":0.8,"loop":true,"tracks":[{"part":"torso","channel":"y","keys":[[0,0],[0.2,-1],[0.4,0],[0.6,-1],[0.8,0]]},{"part":"torso","channel":"angle","keys":[[0,3],[0.8,3]]},{"part":"legLeft","channel":"x","keys":[[0,-7],[0.4,7],[0.8,-7]]},{"part":"legRight","channel":"x","keys":[[0,7],[0.4,-7],[0.8,7]]},{"part":"legLeft","channel":"y","keys":[[0,0],[0.2,-5],[0.4,0],[0.8,0]]},{"part":"legRight","channel":"y","keys":[[0,0],[0.4,0],[0.6,-5],[0.8,0]]},{"part":"armLeft","channel":"angle","keys":[[0,-8],[0.4,8],[0.8,-8]]},{"part":"armRight","channel":"angle","keys":[[0,8],[0.4,-8],[0.8,8]]},{"part":"forearmLeft","channel":"angle","keys":[[0,6],[0.4,-4],[0.8,6]]},{"part":"forearmRight","channel":"angle","keys":[[0,-4],[0.4,6],[0.8,-4]]},{"part":"tail","channel":"angle","keys":[[0,-5],[0.4,5],[0.8,-5]]}]},"wave":{"schema":1,"rig":"cat-v1","duration":2.4,"loop":false,"tracks":[{"part":"armRight","channel":"angle","keys":[[0,0],[0.4,-115],[1.7,-115],[2.4,0]]},{"part":"forearmRight","channel":"angle","keys":[[0,0],[0.4,-40],[0.7,-65],[1,-40],[1.3,-65],[1.6,-40],[1.8,-40],[2.4,0]]},{"part":"head","channel":"angle","keys":[[0,0],[0.5,-6],[1.8,-6],[2.4,0]]},{"part":"tail","channel":"angle","keys":[[0,0],[1,9],[2.4,0]]}]}},"cat-painted-layout.json":{"schema":1,"species":"cat","colors":{"label":"Cat colors","defaultPreset":"ginger","preserveDefaults":true,"defaults":{"coat":"#dba36a","markings":"#ac6038","cream":"#fae4b6","innerEar":"#dca6ab"},"channels":[{"id":"coat","label":"Fur"},{"id":"markings","label":"Stripes"},{"id":"cream","label":"Muzzle & paws"},{"id":"innerEar","label":"Inner ears"}],"presets":{"ginger":{"label":"Ginger","colors":{"coat":"#dba36a","markings":"#ac6038","cream":"#fae4b6","innerEar":"#dca6ab"}},"silver":{"label":"Silver","colors":{"coat":"#a8adb8","markings":"#53606d","cream":"#f2ecdf","innerEar":"#cf9da8"}},"lavender":{"label":"Lavender","colors":{"coat":"#b497ca","markings":"#6d527d","cream":"#f2e8e7","innerEar":"#d6a3bd"}}},"materials":{"fur":[{"channel":"cream","hue":[30,65],"lightness":[0.78,0.98],"saturation":[0.18,1],"sourceLightness":0.85},{"channel":"markings","hue":[0,28],"lightness":[0.26,0.62],"saturation":[0.22,1],"sourceLightness":0.45},{"channel":"coat","hue":[10,58],"lightness":[0.26,0.96],"saturation":[0.2,1],"sourceLightness":0.64}],"earFur":[{"channel":"innerEar","hue":[330,360],"saturation":[0.12,1],"lightness":[0.35,0.94],"sourceLightness":0.76},{"channel":"innerEar","hue":[0,15],"saturation":[0.12,1],"lightness":[0.35,0.94],"sourceLightness":0.76},{"channel":"cream","hue":[30,65],"lightness":[0.78,0.98],"saturation":[0.18,1],"sourceLightness":0.85},{"channel":"markings","hue":[0,28],"lightness":[0.26,0.62],"saturation":[0.22,1],"sourceLightness":0.45},{"channel":"coat","hue":[10,58],"lightness":[0.26,0.96],"saturation":[0.2,1],"sourceLightness":0.64}]}},"width":1254,"height":1254,"parts":{"legSideLeft":{"atlas":"profileLegs","source":[77,19,142,218],"size":[25,32],"pivot":[9,10],"recolor":"fur"},"legSideRight":{"atlas":"profileLegs","source":[310,20,134,218],"size":[25,32],"pivot":[9,10],"recolor":"fur"},"earSideNear":{"atlas":"profileEars","source":[35,29,154,205],"size":[27,24],"pivot":[13.5,20],"recolor":"earFur"},"earSideFar":{"atlas":"profileEars","source":[247,66,104,168],"size":[12,18],"pivot":[6,16],"recolor":"earFur"},"front":{"source":[4,50,310,240],"size":[74,56],"pivot":[37,28],"recolor":"fur","protectedRegions":[{"center":[0.35,0.5],"radius":[0.085,0.14],"hue":[35,150]},{"center":[0.7,0.5],"radius":[0.085,0.14],"hue":[35,150]}]},"side":{"source":[346,49,276,241],"size":[74,56],"pivot":[37,28],"recolor":"fur","protectedRegions":[{"center":[0.73,0.49],"radius":[0.1,0.15],"hue":[35,150]}]},"front-blink":{"source":[627,50,314,238],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"side-blink":{"source":[960,49,286,241],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"torso-front":{"source":[36,324,278,292],"size":[57,66],"pivot":[28.5,33],"recolor":"fur"},"torso-side":{"source":[372,323,241,300],"size":[53,66],"pivot":[26.5,33],"recolor":"fur"},"armLeft":{"source":[704,348,141,253],"size":[20,42],"pivot":[10,5],"recolor":"fur"},"armRight":{"source":[1031,346,141,255],"size":[20,42],"pivot":[10,5],"recolor":"fur"},"legLeft":{"source":[74,635,170,270],"size":[25,32],"pivot":[12.5,10],"recolor":"fur"},"legRight":{"source":[410,635,168,270],"size":[25,32],"pivot":[12.5,10],"recolor":"fur"},"tail":{"source":[640,627,296,285],"size":[66,64],"pivot":[62,55],"recolor":"fur"},"earLeft":{"source":[1010,670,189,225],"size":[24,30],"pivot":[12,26],"recolor":"earFur"},"earRight":{"source":[74,955,194,224],"size":[24,30],"pivot":[12,26],"recolor":"earFur"},"happy":{"source":[314,941,313,245],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"curious":{"source":[630,941,311,247],"size":[74,56],"pivot":[37,28],"recolor":"fur"},"sleepy":{"source":[941,941,313,247],"size":[74,56],"pivot":[37,28],"recolor":"fur"}},"atlases":{"profileLegs":{"width":512,"height":256},"profileEars":{"width":384,"height":256}}},"unicorn-layout.json":{"schema":1,"species":"unicorn","rig":"cat-v1","colors":{"label":"Unicorn colors","defaultPreset":"pearl","defaults":{"coat":"#e9e5df","mane":"#aa89d9","horn":"#e4bd6b","hooves":"#645275"},"channels":[{"id":"coat","label":"Coat"},{"id":"mane","label":"Mane & tail"},{"id":"horn","label":"Horn"},{"id":"hooves","label":"Hooves"}],"presets":{"pearl":{"label":"Pearl","colors":{"coat":"#e9e5df","mane":"#aa89d9","horn":"#e4bd6b","hooves":"#645275"}},"twilight":{"label":"Twilight","colors":{"coat":"#53617c","mane":"#d592bb","horn":"#efc575","hooves":"#40364f"}},"meadow":{"label":"Meadow","colors":{"coat":"#bfd1ae","mane":"#548e94","horn":"#e2c17a","hooves":"#526b57"}}},"materials":{"coat":[{"channel":"coat","chroma":[0,0.18],"lightness":[0.13,1],"sourceLightness":0.86}],"limb":[{"channel":"hooves","hue":[145,205],"saturation":[0.2,1],"lightness":[0.1,1],"sourceLightness":0.42},{"channel":"coat","chroma":[0,0.18],"lightness":[0.13,1],"sourceLightness":0.86}],"mane":[{"channel":"mane","lightness":[0.1,1],"sourceLightness":0.58}],"horn":[{"channel":"horn","lightness":[0.1,1],"sourceLightness":0.62}]}},"width":1280,"height":1024,"parts":{"front":{"source":[25,61,250,188],"size":[74,56],"pivot":[37,28],"recolor":"coat"},"side":{"source":[298,64,255,187],"size":[80,56],"pivot":[40,28],"recolor":"coat"},"front-blink":{"source":[556,62,251,187],"size":[74,56],"pivot":[37,28],"recolor":"coat"},"side-blink":{"source":[819,64,263,189],"size":[80,56],"pivot":[40,28],"recolor":"coat"},"horn":{"source":[1117,45,113,210],"size":[12,30],"pivot":[6,27],"recolor":"horn"},"torso-front":{"source":[25,267,263,253],"size":[57,66],"pivot":[28.5,33],"recolor":"coat"},"torso-side":{"source":[311,266,242,255],"size":[53,66],"pivot":[26.5,33],"recolor":"coat"},"armLeft":{"source":[581,282,155,233],"size":[20,42],"pivot":[10,5],"recolor":"limb"},"armRight":{"source":[809,281,153,234],"size":[20,42],"pivot":[10,5],"recolor":"limb"},"tail":{"source":[998,277,268,256],"size":[42,52],"pivot":[38,26],"recolor":"mane"},"legLeft":{"source":[51,531,164,229],"size":[25,32],"pivot":[12.5,10],"recolor":"limb"},"legRight":{"source":[314,531,166,229],"size":[25,32],"pivot":[12.5,10],"recolor":"limb"},"legSideLeft":{"source":[559,533,169,222],"size":[25,32],"pivot":[9,10],"recolor":"limb","placementOffset":[-7,0]},"legSideRight":{"source":[774,532,169,223],"size":[25,32],"pivot":[9,10],"recolor":"limb","placementOffset":[7,0]},"maneFront":{"atlas":"unicornMane","source":[34,68,224,120],"size":[56,23],"pivot":[28,31],"recolor":"mane","placementOffset":[0,1]},"earLeft":{"source":[39,773,177,216],"size":[16,36],"pivot":[8,32],"recolor":"coat"},"earRight":{"source":[310,772,177,216],"size":[16,36],"pivot":[8,32],"recolor":"coat"},"earSideNear":{"source":[545,767,154,229],"size":[15,32],"pivot":[7.5,28],"recolor":"coat"},"earSideFar":{"source":[782,772,175,224],"size":[11,27],"pivot":[5.5,24],"recolor":"coat"},"maneSide":{"atlas":"unicornMane","source":[59,226,147,252],"size":[31,82],"pivot":[41,27],"recolor":"mane","placementOffset":[2,0]},"maneSideForelock":{"atlas":"unicornMane","source":[294,66,191,132],"size":[44,20],"pivot":[22,32],"recolor":"mane","placementOffset":[0,1]},"maneFrontBack":{"atlas":"unicornMane","source":[297,312,168,133],"size":[60,34],"pivot":[30,14],"recolor":"mane"}},"atlases":{"unicornMane":{"width":512,"height":512}}}};
const __bundledJSON=async name=>{const key=String(name).replace(/^\.\//,'');if(!Object.hasOwn(__inlineConfigurations,key))throw Error('Unknown painted layout');return structuredClone(__inlineConfigurations[key]);};
const __loadBundledImage=async name=>{const chunks=globalThis.__taviCompanionImageChunks?.[name];if(!Array.isArray(chunks)||!chunks.length)throw Error('Missing painted artwork: '+name);const img=new Image();img.src='data:image/png;base64,'+chunks.join('');await img.decode();return img;};
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
// world/cat-study.mjs
__modules["world/cat-study.mjs"]=(async ()=>{
const __moduleURL=new URL("./world/cat-study.mjs",document.baseURI).href;
const {connectTaviHost}=__modules["world/tavi-host.mjs"];
const {createPaintedCompanion,catPresentation}=__modules["world/cat-painted.mjs"];
const {sampleClip,validateClip}=__modules["world/cat-motion.mjs"];
const {validatePalette,validateColorProfile}=__modules["world/companion-colors.mjs"];
const {inspectRigLayout}=__modules["world/rig-diagnostics.mjs"];
const $=id=>document.getElementById(id),canvas=$('cat'),ctx=canvas.getContext('2d'),face=$('portrait').getContext('2d');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const makeCanvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
let art,clips,pack,palette,active='idle',diagnostics='off',time=0,previous=0,painted=0,front=false,paused=false,sequence=0,colorTimer;
const packs=new Map(),paletteStates=new Map();
async function image(file){return __loadBundledImage(file);}
async function json(file){return __bundledJSON(file);}
async function loadPack(id){
 if(!packs.has(id))packs.set(id,(async()=>{
  if(id==='unicorn'){
   const [atlas,layout,mane]=await Promise.all([image('unicorn-atlas.png'),json('unicorn-layout.json'),image('unicorn-mane-v2.png')]);return {id,atlas,layout,extras:{unicornMane:mane}};
  }
  const [atlas,layout,legs,ears]=await Promise.all([image('cat-painted-atlas.png'),json('cat-painted-layout.json'),image('cat-profile-legs.png'),image('cat-profile-ears.png')]);
  return {id,atlas,layout,extras:{profileLegs:legs,profileEars:ears}};
 })());
 return packs.get(id);
}
function draw(){
 if(!art||!clips)return;
 const pose=sampleClip(clips[active],reduced.matches?0:time),blink=!reduced.matches&&time%4.2>4;
 ctx.fillStyle='#e7eddf';ctx.fillRect(0,0,768,384);ctx.fillStyle='#d2dbc3';ctx.fillRect(0,304,768,80);
 ctx.fillStyle='#c0ccae';ctx.fillRect(0,304,768,2);ctx.fillStyle='#a3b48e55';ctx.beginPath();ctx.ellipse(384,310,75,9,0,0,Math.PI*2);ctx.fill();
 art.draw(ctx,384,304,pose,{scale:1.75,...catPresentation(active,front),blink,diagnostics});
 face.clearRect(0,0,192,192);art.portrait(face,96,106,{scale:2,blink,diagnostics});
}
function updateRigReport(){
 const panel=$('rig-details');panel.hidden=diagnostics==='off';
 if(!pack||diagnostics==='off')return;
 const entries=inspectRigLayout(pack.layout,diagnostics);
 $('rig-report').textContent=entries.map(p=>`${p.id.padEnd(18)} atlas=${p.atlas.padEnd(12)} pivot=${p.pivot.join(',')} bounds=${p.relativeBounds.join(',')} offset=${p.placementOffset.join(',')} placed=${p.placedBounds.join(',')} crop=${p.source.join(',')}`).join('\n');
}
function rebuild(){
 if(!pack)return;
 art=createPaintedCompanion(makeCanvas,pack.atlas,pack.layout,pack.extras,{palette});updateRigReport();draw();
}
function syncPalette(){for(const {id}of pack.layout.colors.channels)$('color-'+id).value=palette[id];}
function renderPaletteControls(){
 const profile=pack.layout.colors,owner=pack.id;$('palette-title').textContent=profile.label;
 $('palette-inputs').replaceChildren();$('palette-preset').replaceChildren();
 for(const {id,label:text}of profile.channels){
  const label=document.createElement('label'),input=document.createElement('input');
  label.append(document.createTextNode(text));input.type='color';input.id='color-'+id;input.value=palette[id];label.append(input);$('palette-inputs').append(label);
  input.oninput=()=>{
   if(pack.id!==owner)return;
   palette={...palette,[id]:input.value};validatePalette(palette,profile);
   paletteStates.set(owner,{colors:palette,preset:'custom'});$('palette-preset').value='custom';clearTimeout(colorTimer);colorTimer=setTimeout(rebuild,80);
  };
 }
 for(const [id,preset]of Object.entries(profile.presets)){
  const option=document.createElement('option');option.value=id;option.textContent=preset.label;$('palette-preset').append(option);
 }
 const custom=document.createElement('option');custom.value='custom';custom.textContent='Custom';$('palette-preset').append(custom);
 $('palette-preset').value=paletteStates.get(owner).preset;
}
async function selectCompanion(){
 const request=++sequence,id=$('companion').value;clearTimeout(colorTimer);$('palette-controls').disabled=true;$('status').textContent='Loading '+(id==='unicorn'?'unicorn':'cat')+'…';
 try{
  const loaded=await loadPack(id);if(request!==sequence)return;
  const profile=validateColorProfile(loaded.layout.colors);
  if(!paletteStates.has(id))paletteStates.set(id,{colors:{...profile.defaults},preset:profile.defaultPreset});
  pack=loaded;palette=paletteStates.get(id).colors;rebuild();renderPaletteControls();$('palette-controls').disabled=false;
  $('portrait').setAttribute('aria-label','Front-facing '+id+' portrait');canvas.setAttribute('aria-label','Animated '+id+' companion');
  $('status').textContent=active[0].toUpperCase()+active.slice(1);
 }catch(error){if(request===sequence)$('status').textContent='The companion could not load. '+error.message;}
}
function applyPreset(id){
 if(!pack?.layout.colors.presets[id])return;
 clearTimeout(colorTimer);palette={...pack.layout.colors.presets[id].colors};paletteStates.set(pack.id,{colors:palette,preset:id});syncPalette();$('palette-preset').value=id;rebuild();
}
try{
 clips=await json('cat-clips.json');for(const clip of Object.values(clips))validateClip(clip);
 await selectCompanion();$('companion').onchange=selectCompanion;
 for(const button of document.querySelectorAll('[data-clip]'))button.onclick=()=>{
  active=button.dataset.clip;time=0;$('status').textContent=button.textContent;
  for(const other of document.querySelectorAll('[data-clip]'))other.setAttribute('aria-pressed',String(other===button));draw();
 };
 $('rig-mode').onchange=()=>{diagnostics=$('rig-mode').value;updateRigReport();draw();};
 $('look').onclick=()=>{front=!front;$('look').setAttribute('aria-pressed',String(front));draw();};
 $('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'Resume':'Pause';$('pause').setAttribute('aria-pressed',String(paused));};
 $('palette-preset').onchange=()=>applyPreset($('palette-preset').value);$('reset-colors').onclick=()=>{if(pack)applyPreset(pack.layout.colors.defaultPreset);};
 function frame(now){
  if(!document.hidden&&!paused&&!reduced.matches){time+=Math.min(.1,(now-previous)/1000||0);if(now-painted>=1000/30){draw();painted=now;}}
  previous=now;if(!document.hidden)requestAnimationFrame(frame);
 }
 document.addEventListener('visibilitychange',()=>{previous=0;if(!document.hidden)requestAnimationFrame(frame);});
 reduced.addEventListener('change',draw);requestAnimationFrame(frame);
}catch(error){$('status').textContent='The companion study could not load. '+error.message;}


// The art studio is a separate route, but must preserve the same Tavi escape
// control as the main world when hosted in an approved extension frame.
void connectTaviHost().then(host=>{
 if(!host)return;
 const back=document.getElementById('return-to-tavi');
 back.hidden=false;back.disabled=false;
 back.addEventListener('click',async()=>{
   back.disabled=true;
   try{await host.close();}
   catch{back.disabled=false;back.textContent='Tavi unavailable — use the main navigation';}
 });
});

return {};
})();
})();
