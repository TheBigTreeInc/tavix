import {TAVIX_ICON_NAMES,createTaviIcon} from './kit/icons.js';
import {createTaviUIController} from './kit/ui.js';
const root=document.body;
const actions=document.getElementById('actions');
for(const name of ['search','folder','save','pencil','trash-2']){
 const button=document.createElement('button');button.type='button';button.className='tavix-icon-button';
 button.setAttribute('aria-label',name);button.append(createTaviIcon(name));
 button.addEventListener('click',()=>document.getElementById('message').textContent=`Selected ${name}`);actions.append(button);
}
const catalog=document.getElementById('catalog');
for(const name of TAVIX_ICON_NAMES){
 const item=document.createElement('div');item.className='tavix-button';
 item.style.display='flex';item.style.alignItems='center';item.style.gap='8px';
 item.append(createTaviIcon(name),document.createTextNode(name));catalog.append(item);
}
// Optional host SDK; in local loopback preview no host privileges are available.
// A host-style message sent by another iframe never establishes a capability.
let sdk=null;
if(window.parent!==window){
 const module=await import('./tavix-sdk.mjs').catch(()=>null);
 if(module)sdk=module.createTaviXSDK();
}
const controller=createTaviUIController(root,{sdk});
const status=document.getElementById('viewport-status');
let source='local';
function updateStatus(){status.textContent=`${source==='host'?'Tavi host':'Local preview'} · ${root.dataset.taviLayout} layout · ${root.dataset.taviTheme} theme`;}
updateStatus(); // Never block first paint on optional host discovery.
void controller.ready.then(result=>{source=result.source;updateStatus();});
const observation=typeof ResizeObserver==='function'?new ResizeObserver(updateStatus):null;
observation?.observe(root);
window.addEventListener('pagehide',()=>{observation?.disconnect();controller.dispose();sdk?.dispose();},{once:true});
