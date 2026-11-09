import test from 'node:test';
import assert from 'node:assert/strict';
import {createTaviXSDK,assertTaviXHostInfo,LOCAL_FILE_FEATURE,LOCAL_FILE_PERMISSION} from '../sdk/tavix-sdk.mjs';

function mockHost({mode='embedded',feature=true,permission=true,denyRead=false,holdPicker=false}={}){
 let subscriber;
 const sent=[];
 const handle='abcdefghijklmnop';
 const reply=(id,ok,result,code)=>queueMicrotask(()=>subscriber({channel:'tavi.extension/v1',direction:'response',id,ok,...(ok?{result}:{error:'Denied',errorCode:code})}));
 const transport={
  subscribe(fn){subscriber=fn;return()=>{subscriber=null;}},
  send(msg){
   sent.push(msg);
   switch(msg.method){
    case 'host.info':reply(msg.id,true,{standard:'tavix/1.0',channel:'tavi.extension/v1',api:'1.0.0',extensionId:'example.org.local-file-import',mode,navigation:'host',features:feature?[LOCAL_FILE_FEATURE]:[]});break;
    case 'host.capabilities':reply(msg.id,true,permission?[LOCAL_FILE_PERMISSION,'ui.panel']:['ui.panel']);break;
    case 'files.local.pick':if(!holdPicker)reply(msg.id,true,{status:'selected',file:{handle,name:'cards.tavia',size:3,mimeType:'application/zip'},limits:{maxChunkBytes:65536}});break;
    case 'files.local.read':if(denyRead)reply(msg.id,false,null,'PERMISSION_DENIED');else reply(msg.id,true,{handle,offset:msg.params.offset,bytesRead:3,encoding:'base64',data:'YWJj',eof:true});break;
    case 'files.local.close':reply(msg.id,true,{closed:true});break;
    case 'files.local.cancel':reply(msg.id,true,{cancelled:true});if(holdPicker)reply(msg.params.targetRequestId,true,{status:'cancelled'});break;
    default:reply(msg.id,false,null,'NOT_SUPPORTED');
   }
  }
 };
 return {transport,sent};
}
const accept={extensions:['.tavia'],mimeTypes:['application/zip']};

test('embedded and detached transport negotiate and send bounded params envelope',async()=>{
 for(const mode of ['embedded','detached']){
  const host=mockHost({mode});const sdk=createTaviXSDK(null,null,{transport:host.transport});
  const negotiated=await sdk.localFiles.negotiate();assert.equal(negotiated.mode,mode);
  const promise=sdk.localFiles.pick(accept,1024);
  assert.equal(host.sent.at(-1).method,'files.local.pick');
  assert.deepEqual(host.sent.at(-1).params,{accept,maxBytes:1024});
  const selected=await promise;assert.equal(selected.status,'selected');
  const block=await sdk.localFiles.read(selected.file.handle,0,3);
  assert.equal(block.data,'YWJj');assert.equal(block.encoding,'base64');
  assert.deepEqual(await sdk.localFiles.close(selected.file.handle),{closed:true});
  sdk.dispose();
 }
});

test('capability and grant both required, no silent fallback',async()=>{
 for(const opts of [{feature:false},{permission:false}]){
  const host=mockHost(opts);const sdk=createTaviXSDK(null,null,{transport:host.transport});
  await assert.rejects(sdk.localFiles.negotiate());
  await assert.rejects(sdk.localFiles.pick(accept,1024));
  assert.ok(!host.sent.some(m=>m.method==='files.local.pick'));
  sdk.dispose();
 }
});

test('native cancellation is explicit and targets only own pending request',async()=>{
 const host=mockHost({holdPicker:true});const sdk=createTaviXSDK(null,null,{transport:host.transport});
 await sdk.localFiles.negotiate();const ticket=sdk.localFiles.pickCancelable(accept,1024);
 assert.equal(host.sent.at(-1).id,ticket.requestId);
 assert.deepEqual(await ticket.cancel(),{cancelled:true});
 assert.deepEqual(await ticket.result,{status:'cancelled'});
 assert.equal(host.sent.at(-1).params.targetRequestId,ticket.requestId);
 sdk.dispose();
});

test('host errors preserve machine-readable code and read bound',async()=>{
 const host=mockHost({denyRead:true});const sdk=createTaviXSDK(null,null,{transport:host.transport});
 await sdk.localFiles.negotiate();
 await assert.rejects(sdk.localFiles.read('abcdefghijklmnop',0,3),e=>e.code==='PERMISSION_DENIED');
 const before=host.sent.length;
 await assert.rejects(sdk.localFiles.read('abcdefghijklmnop',0,65537));
 assert.equal(host.sent.length,before);
 sdk.dispose();
});

test('detached info assertion accepts only host-owned modes',()=>{
 const base={standard:'tavix/1.0',channel:'tavi.extension/v1',api:'1.0.0',extensionId:'example.org.local-file-import',navigation:'host',features:[]};
 assert.equal(assertTaviXHostInfo({...base,mode:'detached'}).mode,'detached');
 assert.throws(()=>assertTaviXHostInfo({...base,mode:'opener'}));
});


test('embedded postMessage transport accepts only parent responses',async()=>{
 const listeners=new Set();
 const source={addEventListener:(name,fn)=>{assert.equal(name,'message');listeners.add(fn);},removeEventListener:(name,fn)=>{listeners.delete(fn);}};
 const target={postMessage:(msg)=>{
   const respond=result=>queueMicrotask(()=>{
     for(const fn of listeners)fn({source:{},data:{channel:'tavi.extension/v1',direction:'response',id:msg.id,ok:true,result}});
     for(const fn of listeners)fn({source:target,data:{channel:'tavi.extension/v1',direction:'response',id:msg.id,ok:true,result}});
   });
   if(msg.method==='host.info')respond({standard:'tavix/1.0',channel:'tavi.extension/v1',api:'1.0.0',extensionId:'example.org.local-file-import',mode:'embedded',navigation:'host',features:[LOCAL_FILE_FEATURE]});
   else if(msg.method==='host.capabilities')respond([LOCAL_FILE_PERMISSION]);
   else if(msg.method==='files.local.pick')respond({status:'cancelled'});
 }};
 const sdk=createTaviXSDK(target,source);
 await sdk.localFiles.negotiate();
 assert.deepEqual(await sdk.localFiles.pick(accept,1024),{status:'cancelled'});
 sdk.dispose();assert.equal(listeners.size,0);
});
