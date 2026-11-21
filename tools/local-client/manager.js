// Operator-only UI. Never inject credential values into extension frames or logs.
const $ = id => document.getElementById(id);
const apiBase = '/__manager/v1';
let csrf = '', state = null, current = null, localApps = [], toastTimeout;
let eventsState = {events:[]}, currentView = 'overview';

function notify(message, error=false) {
  const toast=$('toast'); toast.textContent=message; toast.className='toast show'+(error?' error':'');
  $('footerStatus').textContent=error?'Action declined':'Local workspace';
  clearTimeout(toastTimeout); toastTimeout=setTimeout(()=>toast.className='toast',6500);
}
function make(tag, value, klass) {
  const item=document.createElement(tag);
  if(value!==undefined && value!==null) item.textContent=String(value);
  if(klass)item.className=klass;
  return item;
}
function empty(container,label) {container.replaceChildren(make('p',label,'muted'));}
function item(container,title,detail,action,buttonText='Open') {
  const row=make('div',null,'item'), body=make('div',null,'itemBody');
  body.append(make('strong',title),make('small',detail));row.append(body);
  if(action) {const b=make('button',buttonText);b.type='button';b.addEventListener('click',action);row.append(b);}
  container.append(row);
}
async function api(path,{method='GET',data,binary=false}={}) {
  const headers={};
  if(method!=='GET')headers['X-TaviX-Local-CSRF']=csrf;
  if(data!==undefined)headers['Content-Type']=binary?'application/octet-stream':'application/json';
  const res=await fetch(apiBase+path,{method,headers,body:data===undefined?undefined:binary?data:JSON.stringify(data),cache:'no-store'});
  let body;try{body=await res.json();}catch{throw Error('Unexpected response from local manager');}
  if(!res.ok){const e=Error(body.error||'Management request failed');e.eventId=body.eventId;e.errorCode=body.errorCode;throw e;}
  return body;
}
async function legacy(path,{method='GET',data}={}) {
  const headers={};if(method!=='GET')headers['X-TaviX-Local-CSRF']=csrf;
  if(data)headers['Content-Type']='application/octet-stream';
  const r=await fetch(path,{method,headers,body:data,cache:'no-store'});
  const body=await r.json();if(!r.ok){const e=Error(body.error||'Request failed');e.eventId=body.eventId;e.errorCode=body.errorCode;throw e;}return body;
}
async function run(job) {try{await job();}catch(err){
  const code=err.errorCode ? ` [${err.errorCode}]` : '';
  const id=err.eventId ? ` · event ${err.eventId}` : '';
  notify((err.message||'Operation failed')+code+id,true);
  if(!err.eventId)browserDiagnostic('UI_NETWORK_ERROR');
  // An error opens its diagnostic context rather than hiding it in a short toast.
  choose('events');
  await refreshEvents().catch(()=>{});
}}
function choose(view) {
  currentView=view;
  document.querySelectorAll('.view').forEach(e=>e.classList.toggle('active',e.id===view));
  document.querySelectorAll('nav [data-view]').forEach(e=>e.classList.toggle('active',e.dataset.view===view));
  $('pageTitle').textContent=({overview:'Overview',packages:'Games & applications',assets:'Assets & objects',storefront:'Storefront',connections:'Connections',operations:'Operations',events:'Events & diagnostics'})[view];
  window.scrollTo({top:0,behavior:'instant'});
  if(view==='events')refreshEvents().catch(()=>{ $('eventSummary').textContent='Events could not be loaded from the local server.'; });
}
document.querySelectorAll('nav [data-view]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.view)));
function renderState() {
  $('eventCount').textContent=String(state.diagnosticEvents||0);
  $('statApps').textContent=state.catalog.length;
  $('statInstalled').textContent=localApps.length;
  $('statAssets').textContent=state.assetDrafts.length;
  $('statPrices').textContent=state.priceDrafts.length;
  const summary=$('summary');summary.replaceChildren();
  for(const [title,detail] of [
    ['Git source',state.git.available?`${state.git.branch||'detached'} · ${(state.git.head||'').slice(0,12)} · ${state.git.trackedDirty?'tracked changes':'clean tracked files'}`:'Not in a Git checkout'],
    ['GitHub',state.githubConnected?'Credential connected; publication still gated':'Not connected'],
    ['Tavi Assets',state.assetsSourceReady?'Canonical validator available':'Start server with --assets-root'],
    ['LoopRD',state.looprdConfigured?'Endpoints configured; server permission still required':'Not configured'],
    ['Credentials',state.credentialsPersistent?'OS-protected persistent store':'Session-only; no plaintext persistence']]) {
    item(summary,title,detail,null);
  }
  $('assetsRootState').textContent=state.assetsSourceReady?'Canonical Tavi Assets source checkout detected.':'No asset checkout configured. Restart with --assets-root pointing to the Tavi Assets repository.';
  $('importAsset').disabled=!state.assetsSourceReady;
  $('githubState').textContent=state.githubConnected?`Connected credential for ${state.githubRepository}; remote writes are disabled.`:'No GitHub credential connected.';
  $('ghRepo').value=state.githubRepository;
  $('lrCatalog').value=state.looprdCatalogEndpoint;
  $('lrAdmin').value=state.looprdAdminEndpoint;
  const assetSelect=$('stageAsset');assetSelect.replaceChildren();
  for(const draft of state.assetDrafts){const opt=document.createElement('option');opt.value=draft.sha256;opt.textContent=`${draft.id}@${draft.version} · ${draft.sha256.slice(0,12)}`;assetSelect.add(opt);}
  $('looprdState').textContent=state.looprdConfigured?
    `Configured. Read: ${state.looprdReadConnected?'yes':'no'} · Ingest: ${state.looprdIngestConnected?'yes':'no'} · Publish: ${state.looprdPublishConnected?'yes':'no'}`:
    'No approved DAPI endpoints configured.';
  const git=$('gitState');git.replaceChildren();
  for(const [label,value] of Object.entries(state.git))item(git,label,String(value),null);
  renderCatalog();renderAssets();renderPrices();
  $('health').textContent='Local session · no publish';$('health').className='pill';
}
function showPreview(app) {
  current=app;$('title').textContent=`${app.name} · ${app.version}`;
  const deps=app.assetDependencies||[];
  $('details').textContent=`${app.id} · ${app.classification?.type||'app'} · permissions: ${(app.permissions||[]).join(', ')||'none'} · asset requests (not granted): ${deps.map(d=>d.packId).join(', ')||'none'}`;
  $('panel').src=app.panel;choose('packages');notify(`Previewing ${app.id}, without host permissions`);
}
function renderCatalog() {
  const list=$('storeEntries');list.replaceChildren();
  for(const app of state.catalog)item(list,`${app.name||app.id} · ${app.version}`,`${app.kind} · ${app.publisher||'unknown'} · catalog candidate`,()=>{
    $('priceKind').value=app.kind==='game'?'game':'store-listing';$('priceId').value=app.id;$('priceVersion').value=app.version;
    updatePriceFields();choose('storefront');notify('Draft fields populated. This does not edit the published index.');
  },'Draft value');
  if(!state.catalog.length)empty(list,'No repository catalog entries');
  const repo=$('apps');repo.replaceChildren();
  (window.repositoryApps||[]).forEach(a=>item(repo,`${a.name} · ${a.version}`,
    `${a.classification?.type||'app'} · ${(a.assetDependencies||[]).length} requested asset packs`,()=>showPreview(a),'Preview'));
  if(!repo.childElementCount)empty(repo,'No valid repository panel manifests');
}
function renderLocal() {
  const list=$('localapps');list.replaceChildren();
  for(const a of localApps){
    const row=make('div',null,'item'),body=make('div',null,'itemBody');
    body.append(make('strong',`${a.name} · ${a.version}`),make('small',`${a.id} · local only`));
    const preview=make('button','Preview');preview.onclick=()=>showPreview(a);
    const remove=make('button','Remove');remove.onclick=()=>run(async()=>{
      if(!window.confirm(`Remove local ${a.id}@${a.version}? It won't affect Tavi installations.`))return;
      await legacy('/__local_client/install/'+encodeURIComponent(a.id)+'/'+encodeURIComponent(a.version),{method:'DELETE'});
      await refresh();notify('Removed local package');
    });row.append(body,preview,remove);list.append(row);
  }
  if(!localApps.length)empty(list,'No local apps installed yet');
}
function renderAssets() {
  const list=$('assetDrafts');list.replaceChildren();
  for(const a of state.assetDrafts)item(list,`${a.display?.name||a.id} · ${a.version}`,
    `${a.resources?.length||0} resources · ${a.objects?.length||0} objects · validated locally`,()=>{
      const details=$('assetDetails');details.replaceChildren();
      const lines=[`Pack ${a.id}@${a.version}`,`Digest ${a.sha256}`,
        `Resources: ${(a.resources||[]).join(', ')||'none'}`,
        `Objects: ${(a.objects||[]).join(', ')||'none'}`,
        `Collections: ${(a.collections||[]).join(', ')||'none'}`,
        'Status: draft, not an installed/owned/published pack'];
      details.append(make('pre',lines.join('\n')));
      $('priceKind').value='asset-pack';$('priceId').value=a.id;$('priceVersion').value=a.version; updatePriceFields();
    },'Inspect');
  if(!state.assetDrafts.length)empty(list,'No validated .tavia drafts');
}
function renderPrices() {
  const list=$('priceDrafts');list.replaceChildren();
  for(const d of state.priceDrafts)item(list,`${d.id} · ${d.version}`,
    `${d.kind}${d.packId?' in '+d.packId:''} · ${d.priceGold} Gold · local proposal only`,null);
  if(!state.priceDrafts.length)empty(list,'No proposals saved');
}
function eventReport(){
  return {schema:'tavix.diagnostic-export/v1',application:'TaviX local management suite',
          version:'0.1.27',generatedAt:new Date().toISOString(),level:$('eventFilter').value,
          diagnosticOnly:true,events:eventsState.events};
}
async function refreshEvents(){
  eventsState=await api('/events?level='+encodeURIComponent($('eventFilter').value));
  const rows=eventsState.events, target=$('eventList');target.replaceChildren();
  $('eventSummary').textContent=`${rows.length} matching event(s). Newest first. Open this panel after a failed import to see the diagnostic code and event ID.`;
  for(const evt of rows){
    const elem=make('article',null,'eventItem '+evt.level);
    const top=make('div',null,'eventHeader');
    top.append(make('strong',evt.level.toUpperCase()),make('span',evt.at),make('code',evt.code),make('code','#'+evt.id));
    elem.append(top,make('p',evt.message));
    const description=Object.entries(evt.details||{}).map(([k,v])=>k+': '+v).join(' · ');
    if(description)elem.append(make('div',description,'eventDetails'));
    target.append(elem);
  }
  if(!rows.length)empty(target,'No events matching this filter.');
  $('eventCount').textContent=String(eventsState.totalEvents||0);
}
$('eventFilter').onchange=()=>run(refreshEvents);
$('eventRefresh').onclick=()=>run(async()=>{await refreshEvents();notify('Local events refreshed')});
$('eventCopy').onclick=()=>run(async()=>{
  await refreshEvents();
  await navigator.clipboard.writeText(JSON.stringify(eventReport(),null,2));
  notify('Diagnostic report copied. You can paste it into our conversation.');
});
$('eventExport').onclick=()=>run(async()=>{
  await refreshEvents();
  const data=JSON.stringify(eventReport(),null,2);
  const blob=new Blob([data],{type:'application/json'});
  const url=URL.createObjectURL(blob);
  const anchor=document.createElement('a');anchor.href=url;anchor.download='tavix-events-'+new Date().toISOString().slice(0,10)+'.json';
  document.body.append(anchor);anchor.click();anchor.remove();
  URL.revokeObjectURL(url);
  notify('Sanitized diagnostic events exported');
});
async function refresh() {
  const init=await api('/bootstrap');csrf=init.csrf;delete init.csrf;state=init;
  const [repo,local]=await Promise.all([legacy('/__local_client/apps'),legacy('/__local_client/installed')]);
  window.repositoryApps=repo;localApps=local;renderState();renderLocal();
  if(currentView==='events')await refreshEvents();
}
$('refresh').onclick=()=>run(async()=>{await refresh();notify('Local repositories and drafts refreshed')});
$('install').onclick=()=>run(async()=>{
  const file=$('file').files[0];if(!file)throw Error('Choose a .tavix package');
  const result=await legacy('/__local_client/install',{method:'POST',data:file});
  await refresh();notify(`Installed ${result.id}@${result.version} locally, publisher trust unverified`);
});
$('importAsset').onclick=()=>run(async()=>{
  const file=$('assetfile').files[0];if(!file)throw Error('Choose a .tavia archive');
  const result=await api('/assets/import',{method:'POST',data:file,binary:true});
  await refresh();notify(`Validated ${result.id}@${result.version}; stored as a local draft`);
});
$('reload').onclick=()=>{if(current){$('panel').src=current.panel+'?reload='+Date.now();notify('Local preview reloaded')}};
$('account').onchange=()=>notify('Visual marker changed; no host identity was changed');
function updatePriceFields(){
  const object=$('priceKind').value==='asset-object';
  $('pricePackRow').hidden=!object;$('pricePack').required=object;
}
$('priceKind').addEventListener('change',updatePriceFields);updatePriceFields();
$('openEditor').onclick=()=>showPreview({id:'example.org.tavix-store-editor',name:'TaviX Store Editor',
  version:'0.1.1',panel:'/examples/store-editor/ui/index.html',permissions:['ui.panel'],assetDependencies:[]});
$('openEditorFull').onclick=()=>window.open('/examples/store-editor/ui/index.html','_blank','noopener,noreferrer');
$('priceForm').onsubmit=e=>{e.preventDefault();run(async()=>{
  const data={kind:$('priceKind').value,id:$('priceId').value.trim(),version:$('priceVersion').value.trim(),priceGold:Number($('priceGold').value)};
  if(data.kind==='asset-object')data.packId=$('pricePack').value.trim();
  await api('/prices',{method:'POST',data});await refresh();notify('Saved as a local price proposal, not a live Gold price');
})};
$('githubForm').onsubmit=e=>{e.preventDefault();run(async()=>{
  const token=$('ghToken').value;
  const result=await api('/github/connect',{method:'POST',data:{repository:$('ghRepo').value.trim(),token}});
  $('ghToken').value='';await refresh();notify(`GitHub ${result.login||'operator'} verified; source pushes remain gated`);
})};
$('githubCheck').onclick=()=>run(async()=>{
  const result=await api('/github');$('githubState').textContent=`${result.repository} · ${result.defaultBranch} · permissions: ${JSON.stringify(result.permissions)}`;
});
$('looprdForm').onsubmit=e=>{e.preventDefault();run(async()=>{
  const data={catalog:$('lrCatalog').value.trim(),admin:$('lrAdmin').value.trim(),
    readToken:$('lrRead').value,ingestToken:$('lrIngest').value,publishToken:$('lrPublish').value};
  await api('/looprd/connect',{method:'POST',data});
  ['lrRead','lrIngest','lrPublish'].forEach(id=>$(id).value='');
  await refresh();notify('Scoped LoopRD connection saved; no remote mutation performed');
})};
for(const [id,action] of [['lrCatalogCheck','catalog'],['lrInspect','inspect'],['lrAudit','audit']]){
  $(id).onclick=()=>run(async()=>{const result=await api('/looprd/'+action);
    $('remoteResult').textContent=JSON.stringify(result,null,2);notify('LoopRD read-only '+action+' succeeded');});
}
function browserDiagnostic(code){
  if(!csrf)return;
  api('/events/client',{method:'POST',data:{code}}).then(()=>{if(currentView==='events')refreshEvents().catch(()=>{});}).catch(()=>{});
}
window.addEventListener('error',()=>{browserDiagnostic('UI_UNCAUGHT_ERROR');notify('Local UI error recorded in Events',true);});
window.addEventListener('unhandledrejection',()=>{browserDiagnostic('UI_UNHANDLED_REJECTION');notify('Local UI operation error recorded in Events',true);});
run(refresh);

$('stageForm').onsubmit=e=>{e.preventDefault();run(async()=>{
  const sha256=$('stageAsset').value;if(!sha256)throw Error('Import a validated TAVIA first');
  let receipt;try{receipt=JSON.parse($('stageReceipt').value)}catch{throw Error('Approval receipt is invalid JSON')}
  if(!window.confirm(`Stage the exact asset ${sha256}? This uploads data to your configured LoopRD server but does NOT publish it.`))return;
  const result=await api('/looprd/stage',{method:'POST',data:{sha256,receipt}});
  $('operationResult').textContent=JSON.stringify(result,null,2);
  notify('LoopRD staging accepted; publication remains separate');
})};
$('transitionForm').onsubmit=e=>{e.preventDefault();run(async()=>{
  let receipt;try{receipt=JSON.parse($('transitionReceipt').value)}catch{throw Error('Approval receipt is invalid JSON')}
  const data={action:$('transitionAction').value,packId:$('transitionPack').value.trim(),
    version:$('transitionVersion').value.trim(),manifestSha256:$('transitionDigest').value.trim(),receipt};
  if(!window.confirm(`${data.action.toUpperCase()} ${data.packId}@${data.version} matching ${data.manifestSha256}? This is a REMOTE mutation and requires independent operator approval.`))return;
  const result=await api('/looprd/transition',{method:'POST',data});
  $('operationResult').textContent=JSON.stringify(result,null,2);
  notify(`LoopRD ${data.action} accepted by the authoritative service`);
})};
