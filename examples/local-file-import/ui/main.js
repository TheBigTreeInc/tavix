import {createTaviXSDK} from './tavix-sdk.mjs';

const $=id=>document.getElementById(id);
// A detached Tavi window needs an authenticated transport provided by the
// native host. The extension cannot create one from window.opener itself.
const hostTransport=window.taviHostTransportV1;
const sdk=hostTransport?createTaviXSDK(null,null,{transport:hostTransport}):createTaviXSDK(window.parent,window);
const accept={extensions:['.tavia'],mimeTypes:['application/zip','application/octet-stream']};
const maxBytes=134217728;
let pending=null;
function status(message){$('availability').textContent=message;}
function detail(message){$('details').textContent=message;}

(async()=>{
  try{
    const host=await sdk.localFiles.negotiate();
    status(`Native picker available (${host.mode}). Choose a file to inspect.`);
    $('pick').disabled=false;
  }catch(error){status(`Native file import unavailable: ${error.message}. The host must implement tavix.local-file-import/v1.`);}
})();

$('pick').addEventListener('click',()=>{
  // IMPORTANT: dispatch pick directly from this click, not after an await.
  const ticket=sdk.localFiles.pickCancelable(accept,maxBytes);
  pending=ticket;
  $('pick').disabled=true;$('cancel').disabled=false;
  status('Waiting for native file selection…');
  (async()=>{
    let handle=null;
    try{
      const selection=await ticket.result;
      if(selection.status==='cancelled'){status('File selection cancelled.');return;}
      if(selection.status!=='selected')throw Error('Unexpected picker response');
      const file=selection.file;handle=file.handle;
      const length=Math.min(65536,selection.limits.maxChunkBytes,file.size);
      let header='';
      if(length>0){
        const block=await sdk.localFiles.read(handle,0,length);
        const bytes=Uint8Array.from(atob(block.data),c=>c.charCodeAt(0));
        header=[...bytes.slice(0,32)].map(b=>b.toString(16).padStart(2,'0')).join(' ');
      }
      detail(`Name: ${file.name}\nSize: ${file.size} bytes\nMIME: ${file.mimeType}\nFirst bytes: ${header||'(empty file)'}`);
      status('Local read completed. Nothing installed or uploaded.');
    }catch(error){status(`File import failed: ${error.code||'ERROR'} — ${error.message}`);}
    finally{
      if(handle){try{await sdk.localFiles.close(handle);}catch{}}
      pending=null;$('pick').disabled=false;$('cancel').disabled=true;
    }
  })();
});
$('cancel').addEventListener('click',async()=>{
  if(!pending)return;
  try{await pending.cancel();status('Cancellation requested.');}catch(error){status(`Cancel failed: ${error.message}`);}
});
window.addEventListener('pagehide',()=>{sdk.dispose();});
