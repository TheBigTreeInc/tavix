/** TaviX 1.0 browser SDK.
 *
 * Reference SDK for host-optional local file import (TaviX 0.1.13).
 * The stable wire channel remains `tavi.extension/v1` for compatibility with
 * existing Tavi applications. TaviX standardizes that deployed protocol; it
 * does not expose Social credentials or native privileges to the iframe.
 */
export const TAVIX_STANDARD='tavix/1.0';
export const TAVIX_CHANNEL='tavi.extension/v1';
export const TAVIX_HOST_API='1.0.0';
export const LOCAL_FILE_FEATURE='tavix.local-file-import/v1';
export const LOCAL_FILE_PERMISSION='files.local.import';

export function assertTaviXHostInfo(info){
 if(!info||typeof info!=='object'||info.standard!==TAVIX_STANDARD||info.channel!==TAVIX_CHANNEL||typeof info.api!=='string'||!/^1\.\d+\.\d+$/.test(info.api)||typeof info.extensionId!=='string'||!['embedded','detached'].includes(info.mode)||info.navigation!=='host'||!Array.isArray(info.features))throw Error('Host is not TaviX 1.0 compatible');
 return info;
}

/**
 * Embedded: createTaviXSDK(window.parent, window)
 * Detached: createTaviXSDK(null, null, {transport: hostProvidedTransport})
 * A detached transport MUST be supplied and authenticated by the Tavi host.
 * transport.send(message); transport.subscribe(onMessage) -> unsubscribe()
 * No arbitrary window.opener fallback is used.
 */
export function createTaviXSDK(target=window.parent,source=window,options={}){
 const transport=options?.transport ?? null;
 if(transport && (typeof transport.send!=='function'||typeof transport.subscribe!=='function'))throw Error('Invalid TaviX host transport');
 if(!transport && (!target||!source||typeof target.postMessage!=='function'||typeof source.addEventListener!=='function'))throw Error('No TaviX host transport');
 let localFileNegotiated=false;
 let nextId=0;
 const pending=new Map(),listeners=new Map();
 const receiver=e=>{
  const data=transport?e:e?.data;
  if((!transport&&e.source!==target)||data?.channel!==TAVIX_CHANNEL)return;
  if(data.direction==='event'){
   const handlers=listeners.get(data.event);if(handlers)for(const fn of [...handlers]){try{fn(data.payload);}catch{}}
   return;
  }
  if(data.direction!=='response')return;
  const item=pending.get(data.id);if(!item)return;pending.delete(data.id);clearTimeout(item.timer);
  if(data.ok)item.resolve(data.result);
  else{const error=Error(data.error||'TaviX request failed');if(typeof data.errorCode==='string')error.code=data.errorCode;item.reject(error);}
 };
 const unsubscribe=transport?transport.subscribe(receiver):(source.addEventListener('message',receiver),()=>source.removeEventListener('message',receiver));
 const requestTicket=(method,args={})=>{
  const id=++nextId;
  const result=new Promise((resolve,reject)=>{
   if(pending.size>=20)return reject(Error('Too many TaviX requests'));
   const timeout=method==='files.local.pick'?180000:10000;
   const timer=setTimeout(()=>{pending.delete(id);reject(Error('TaviX host did not respond'));},timeout);
   pending.set(id,{resolve,reject,timer});
   try{
    const msg={channel:TAVIX_CHANNEL,direction:'request',id,method,...args};
    if(transport)transport.send(msg);else target.postMessage(msg,'*');
   }catch(error){clearTimeout(timer);pending.delete(id);reject(error);}
  });
  return {id,result};
 };
 const request=(method,args={})=>requestTicket(method,args).result;
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
  workspace:{info:()=>request('workspace.info')},
  uiContext:()=>request('ui.info'),
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
  localFiles:{
    /** Call during startup, before a user clicks Import. This does not grant permission. */
    negotiate:async()=>{
      localFileNegotiated=false;
      const info=assertTaviXHostInfo(await request('host.info'));
      if(!info.features.includes(LOCAL_FILE_FEATURE))throw Error('Native file import unavailable');
      const grants=await request('host.capabilities');
      if(!Array.isArray(grants)||!grants.includes(LOCAL_FILE_PERMISSION))throw Error('Native file import permission denied');
      localFileNegotiated=true;
      return {feature:LOCAL_FILE_FEATURE,permission:LOCAL_FILE_PERMISSION,mode:info.mode};
    },
    /** Call directly from a user click; no pre-picker await or implicit HTML fallback. */
    pick:(accept,maxBytes)=>{
      if(!localFileNegotiated)return Promise.reject(Error('Native file import not negotiated'));
      return request('files.local.pick',{params:{accept,maxBytes}});
    },
    /** Returns a request ID for optional cancellation while the native picker is pending. */
    pickCancelable:(accept,maxBytes)=>{
      if(!localFileNegotiated)throw Error('Native file import not negotiated');
      const ticket=requestTicket('files.local.pick',{params:{accept,maxBytes}});
      return {requestId:ticket.id,result:ticket.result,cancel:()=>request('files.local.cancel',{params:{targetRequestId:ticket.id}})};
    },
    read:(handle,offset,length)=>{
      if(!localFileNegotiated)return Promise.reject(Error('Native file import not negotiated'));
      if(!Number.isSafeInteger(offset)||offset<0||!Number.isSafeInteger(length)||length<1||length>65536)return Promise.reject(Error('Invalid local file read range'));
      return request('files.local.read',{params:{handle,offset,length}});
    },
    close:handle=>request('files.local.close',{params:{handle}}),
    cancel:targetRequestId=>request('files.local.cancel',{params:{targetRequestId}})
  },
  dispose:()=>{localFileNegotiated=false;unsubscribe();for(const item of pending.values()){clearTimeout(item.timer);item.reject(Error('TaviX disconnected'));}pending.clear();listeners.clear();}
 };
}

// Deployed-source compatibility name. Existing apps do not need a rewrite.
export const createTaviExtensionSDK=createTaviXSDK;
