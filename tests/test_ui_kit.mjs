import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {TAVIX_ICON_NAMES,createTaviIcon,hasTaviIcon} from '../sdk/ui-kit/icons.js';
import {createTaviXSDK} from '../sdk/tavix-sdk.mjs';
const read=p=>readFileSync(new URL(p,import.meta.url),'utf8');

test('TaviX source icons are fully bundled and strictly named',()=>{
 const catalog=JSON.parse(read('../contracts/tavix-ui-kit-v1.json'));
 assert.deepEqual(TAVIX_ICON_NAMES,catalog.icons.names);
 assert.equal(TAVIX_ICON_NAMES.length,50);
 assert.equal(hasTaviIcon('folder'),true);
 assert.equal(hasTaviIcon('__proto__'),false);
 assert.throws(()=>createTaviIcon('folder<svg>'),RangeError);
 const doc={createElementNS:()=>({attrs:{},setAttribute(k,v){this.attrs[k]=v;},innerHTML:''})};
 assert.equal(createTaviIcon('pencil',{documentRef:doc}).attrs['aria-hidden'],'true');
 assert.throws(()=>createTaviIcon('pencil',{decorative:false,documentRef:doc}),TypeError);
 assert.match(read('../sdk/ui-kit/LUCIDE_LICENSE.txt'),/Lucide Icons/);
});

test('optional read-only host UI calls do not request grants or change protocol',async()=>{
 const sent=[];let receive;
 const transport={subscribe(fn){receive=fn;return()=>{};},send(m){sent.push(m);
  queueMicrotask(()=>receive({channel:'tavi.extension/v1',direction:'response',id:m.id,ok:true,result:{schema:m.method==='ui.info'?'tavix.ui/v1':'tavi.workspace/v1'}}));}};
 const sdk=createTaviXSDK(null,null,{transport});
 assert.equal((await sdk.workspace.info()).schema,'tavi.workspace/v1');
 assert.equal((await sdk.uiContext()).schema,'tavix.ui/v1');
 assert.deepEqual(sent.map(x=>x.method),['workspace.info','ui.info']);
 sdk.dispose();
});
