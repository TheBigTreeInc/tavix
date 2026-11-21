import {createTaviXSDK} from './tavix-sdk.mjs';
const EXPECTED='ziprunner.cockpit-projects.v1';
const FEATURE='ziprunner.status.read/v1';
// A TaviX package is an untrusted iframe. It never fetches remote ZipRunner
// URLs, stores tokens, or asks for unrestricted HTTP/command capabilities.
let sdk=null,connected=false,rows=[];
const $=id=>document.getElementById(id);
function state(s){$('state').textContent=s;}
function render(){const q=$('filter').value.toLowerCase();const body=$('rows');body.replaceChildren();for(const p of rows.filter(p=>p.key.toLowerCase().includes(q))){
 const tr=document.createElement('tr');let cell=document.createElement('td');const b=document.createElement('button');b.textContent=p.key;b.addEventListener('click',()=>{$('detail').textContent=p.key+' — Build '+p.build+', QA '+p.qa.status+' ('+p.qa.failed+' failed). This is recorded evidence, not operator approval.'});cell.appendChild(b);tr.appendChild(cell);
 for(const v of [p.version||'—',p.build,p.qa.status]){cell=document.createElement('td');cell.textContent=String(v);tr.appendChild(cell)}body.appendChild(tr)}}
export function validateResponse(value){if(!value||value.schema!==EXPECTED||value.mode!=='read_only'||value.actions_enabled!==false||!Array.isArray(value.projects)||value.projects.length>250)throw Error('Invalid ZipRunner status response');
 for(const p of value.projects){if(!p||typeof p.key!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$/.test(p.key)||!p.qa||typeof p.build!=='string')throw Error('Unexpected project status');}return value.projects;}
export async function loadStatus(client){const data=await client.request('ziprunner.status.read',{params:{schema:EXPECTED}});return validateResponse(data)}
async function refresh(){if(!connected)return;state('Reading ZipRunner status…');try{rows=await loadStatus(sdk);state(rows.length+' projects · read-only');render();}catch(error){state('ZipRunner unavailable: '+error.message)}}
async function start(){try{
 const hostTransport=window.taviHostTransportV1;
 sdk=hostTransport?createTaviXSDK(null,null,{transport:hostTransport}):createTaviXSDK(window.parent,window);
 const info=await sdk.info();if(!Array.isArray(info.features)||!info.features.includes(FEATURE))throw Error('Tavi host has no ZipRunner relay');
 const caps=await sdk.capabilities();if(!Array.isArray(caps)||!caps.includes('ziprunner.status.read'))throw Error('ZipRunner status access not granted');
 connected=true;$('refresh').disabled=false;await refresh();
 }catch(error){state('Connection required: '+error.message);$('refresh').disabled=true;}}
$('refresh').addEventListener('click',refresh);$('filter').addEventListener('input',render);window.addEventListener('pagehide',()=>{sdk?.dispose();});start();
