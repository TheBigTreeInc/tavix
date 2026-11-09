import test from 'node:test';
import assert from 'node:assert/strict';
import {createTaviUIController} from '../sdk/ui-kit/ui.js';

function fixture(width=350) {
 const listeners = new Map();
 const mediaListeners = new Set();
 const root={clientWidth:width,dataset:{}};
 const windowRef={innerWidth:width,innerHeight:700,
  addEventListener(type,fn){listeners.set(type,fn);},
  removeEventListener(type,fn){if(listeners.get(type)===fn)listeners.delete(type);},
  matchMedia:()=>({matches:false,addEventListener(type,fn){mediaListeners.add(fn);},removeEventListener(type,fn){mediaListeners.delete(fn);}})};
 let observer;
 class ResizeObserverClass {
  constructor(fn){this.fn=fn;observer=this;this.disconnected=false;}
  observe(el){assert.equal(el,root);}
  disconnect(){this.disconnected=true;}
  resize(){this.fn();}
 }
 return {root,windowRef,ResizeObserverClass,readObserver:()=>observer};
}

test('offline UI has a safe local appearance and follows its own viewport',async()=>{
 const f=fixture(355);const controller=createTaviUIController(f.root,f);
 assert.deepEqual(await controller.ready,{source:'local'});
 assert.equal(f.root.dataset.taviTheme,'light');
 assert.equal(f.root.dataset.taviLayout,'compact');
 f.root.clientWidth=650;f.readObserver().resize();
 assert.equal(f.root.dataset.taviLayout,'medium');
 f.root.clientWidth=1024;f.readObserver().resize();
 assert.equal(f.root.dataset.taviLayout,'wide');
 controller.dispose();controller.dispose();
 assert.equal(f.readObserver().disconnected,true);
 f.root.clientWidth=300;f.readObserver().resize();
 assert.equal(f.root.dataset.taviLayout,'wide');
});

test('host theme and platform are respected; narrow detached desktop still compact',async()=>{
 const f=fixture(340);
 const events=new Map();let infoCalls=0,uiCalls=0,removed=0;
 const sdk={info:async()=>{infoCalls++;return {features:['tavix.ui/v1']};},
  uiContext:async()=>{uiCalls++;return {schema:'tavix.ui/v1',theme:'dark',device:'desktop',orientation:'landscape',chat:{placement:'left'}};},
  on:(name,fn)=>{events.set(name,fn);return ()=>{removed++;events.delete(name);};}};
 const ctrl=createTaviUIController(f.root,{...f,sdk});
 assert.deepEqual(await ctrl.ready,{source:'host'});
 assert.equal(infoCalls,1);assert.equal(uiCalls,1);
 assert.equal(f.root.dataset.taviDevice,'desktop');
 assert.equal(f.root.dataset.taviLayout,'compact');
 assert.equal(f.root.dataset.taviTheme,'dark');
 events.get('ui.contextChanged')({schema:'tavix.ui/v1',theme:'light',device:'tablet',orientation:'portrait',chat:{placement:'center'}});
 assert.equal(f.root.dataset.taviTheme,'light');
 ctrl.dispose();assert.equal(removed,1);
 assert.equal(events.has('ui.contextChanged'),false);
});

test('unadvertised UI feature never invokes UI info or subscribes',async()=>{
 const f=fixture();
 const sdk={info:async()=>({features:[]}),uiContext:async()=>{throw Error('should not run');},on:()=>{throw Error('should not subscribe');}};
 const ctrl=createTaviUIController(f.root,{...f,sdk});
 assert.deepEqual(await ctrl.ready,{source:'local'});
 ctrl.dispose();
});

test('newer host context event wins over delayed snapshot',async()=>{
 const f=fixture();let releaseSnapshot;let cb;
 const sdk={info:async()=>({features:['tavix.ui/v1']}),
  on:(_event,fn)=>{cb=fn;return ()=>{};},
  uiContext:()=>new Promise(resolve=>releaseSnapshot=resolve)};
 const ctrl=createTaviUIController(f.root,{...f,sdk});
 // Flush the feature probe and subscribe.
 for(let i=0;i<3;i++)await Promise.resolve();
 cb({schema:'tavix.ui/v1',theme:'dark',device:'phone'});
 releaseSnapshot({schema:'tavix.ui/v1',theme:'light',device:'phone'});
 assert.deepEqual(await ctrl.ready,{source:'host'});
 assert.equal(f.root.dataset.taviTheme,'dark');
 ctrl.dispose();
});

test('unsupported SDK or failed negotiation never crashes the UI',async()=>{
 const f=fixture();const ctrl=createTaviUIController(f.root,{...f,sdk:{info:async()=>{throw Error('Host offline');},uiContext(){},on(){}}});
 assert.deepEqual(await ctrl.ready,{source:'local'});
 assert.equal(f.root.dataset.taviLayout,'compact');ctrl.dispose();
});
