import test from 'node:test';
import assert from 'node:assert/strict';
import {createKlondikeAssetController,safeCardBack,CARD_PACK} from '../examples/klondike-assets-0.1.2/ui/asset-integration.mjs';

function fixture(){
 const attributes=new Map(),css=new Map(),events=new Map();
 const root={style:{setProperty:(k,v)=>css.set(k,v),removeProperty:k=>css.delete(k)},setAttribute:(k,v)=>attributes.set(k,v),removeAttribute:k=>attributes.delete(k)};
 const ref=()=>({visibilityState:'visible',addEventListener:(k,v)=>events.set(k,v),removeEventListener:k=>events.delete(k)});
 const doc=ref(),win=ref();let supported=true,granted=true,fail=false;
 const host={info:async()=>({features:supported?['tavi.assets/v1']:[]}),capabilities:async()=>granted?['assets.read']:[],dispose:()=>{}};
 const assets={connect:async()=>({feature:'tavi.assets/v1'}),resolve:async(p,c)=>{if(fail)throw Error('revoked');return {schema:'tavi.assets.resource/v1',packId:p,capability:c,contentType:'image/png',encoding:'base64',data:'AA=='};}};
 const controller=createKlondikeAssetController({host,root,documentRef:doc,windowRef:win,assets});
 return {controller,root,css,attributes,host,assets,setGranted:v=>granted=v,setSupported:v=>supported=v,setFail:v=>fail=v};
}

test('granted card-back resource is rendered without touching game state or storage',async()=>{
 const f=fixture();assert.equal(await f.controller.start(),true);assert.equal(f.attributes.get('data-tavi-card-back'),'granted');
 assert.equal(f.css.get('--tavi-card-back-image'),'url("data:image/png;base64,AA==")');f.controller.dispose();assert.equal(f.css.size,0);
});
test('no feature, no permission, and revoked host resolution reset to bundled deck',async()=>{
 const f=fixture();await f.controller.start();f.setGranted(false);assert.equal(await f.controller.refresh(),false);assert.equal(f.css.size,0);
 f.setGranted(true);f.setSupported(false);assert.equal(await f.controller.refresh(),false);
 f.setSupported(true);f.setFail(true);assert.equal(await f.controller.refresh(),false);f.controller.dispose();
});
test('only own card-back media is accepted; no HTML, URL, forged pack, overlarge data',()=>{
 const base={schema:'tavi.assets.resource/v1',packId:CARD_PACK,capability:'card.back',contentType:'image/svg+xml',encoding:'base64',data:'PHN2Zz48L3N2Zz4='};
 assert.match(safeCardBack(base),/^url\("data:image\/svg\+xml;base64,/);
 for(const v of [{packId:'org.tavi.other'},{capability:'card.front'},{contentType:'text/html'},{data:'https://evil.example'},{data:'A'.repeat(1400004)},{encoding:'url'}])assert.throws(()=>safeCardBack({...base,...v}),/Invalid or unauthorized/);
});
test('asynchronous grant change cannot repaint after disposal',async()=>{
 const f=fixture();let resolve;f.assets.resolve=()=>new Promise(r=>{resolve=r});const pending=f.controller.start();
 for(let i=0;i<10&&!resolve;i++)await Promise.resolve();assert.ok(resolve);
 f.controller.dispose();resolve({schema:'tavi.assets.resource/v1',packId:CARD_PACK,capability:'card.back',contentType:'image/png',encoding:'base64',data:'AA=='});
 assert.equal(await pending,false);assert.equal(f.css.size,0);
});
