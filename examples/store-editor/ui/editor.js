/* TaviX Store Editor: no network requests or privileged host API. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const encoder = new TextEncoder();
  const state = {
    entries: null, manifest: null, importedVersion: '',
    iconUrl: 'sample-icon.png', coverUrl: 'sample-cover.webp', shots: [],
    uploads: new Map(), importedUrls: [], selectedScreen: 'catalog', device: 'phone', renderMode: 'current'
  };
  const fields = ['name', 'summary', 'description', 'version', 'category'];
  function setStatus(message, type) {
    const element = $('status'); element.textContent = message;
    element.className = 'status'+(type ? ' '+type : '');
  }
  function versionParts(s) {
    if(!/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(s))return null;
    return s.split('.').map(Number);
  }
  function newerVersion(next, last) {
    const a=versionParts(next), b=versionParts(last); if(!a||!b)return false;
    for(let i=0;i<3;i++) { if(a[i]>b[i])return true; if(a[i]<b[i])return false; }
    return false;
  }
  function nextPatch(version) {
    const p = versionParts(version);
    return p ? p[0]+'.'+p[1]+'.'+(p[2]+1) : version;
  }
  function checkInput() {
    const name=$('name').value.trim(), summary=$('summary').value.trim(), version=$('version').value.trim();
    if(!name||name.length>60)throw new Error('App name must contain 1–60 characters.');
    if(!summary||summary.length>240)throw new Error('Summary must contain 1–240 characters.');
    if(!versionParts(version))throw new Error('Use a release version such as 0.1.2.');
    return {name,summary,version};
  }
  function inputCategory(manifest) {
    const category=manifest?.classification?.categories;
    return category && category.length ? category.map(x=>x.replace(/\b\w/g,y=>y.toUpperCase())).join(' · ') : (manifest?.classification?.type === 'game' ? 'Games' : 'Apps');
  }
  function removeUrls() {
    for(const u of state.importedUrls) URL.revokeObjectURL(u);
    state.importedUrls=[];
  }
  function blobUrl(bytes, filename) {
    const suffix=filename.split('.').pop().toLowerCase();
    const mime = {png:'image/png',webp:'image/webp',svg:'image/svg+xml'}[suffix] || 'application/octet-stream';
    const u=URL.createObjectURL(new Blob([bytes],{type:mime}));
    state.importedUrls.push(u);return u;
  }
  function getImageUrl(path) {
    const bytes=state.uploads.get(path)||state.entries?.get(path);
    return bytes ? blobUrl(bytes,path) : '';
  }
  function galleryPaths(entries) {
    return [...entries.keys()].filter(path => /^store\/(screenshot|editor-shot)[\w-]*\.(png|webp)$/.test(path)).sort().slice(0,3);
  }
  function render() {
    const name=$('name').value.trim()||'Your game', summary=$('summary').value.trim()||'Discover something fun',category=$('category').value.trim()||'Apps';
    const publisher=$('publisher').value.trim()||'unknown';
    $('summaryCount').textContent=$('summary').value.length+' / 240';
    $('cardName').textContent=name; $('cardCategory').textContent=category;
    $('detailName').textContent=name; $('detailPublisher').textContent='by '+publisher;
    $('detailType').textContent=state.manifest?.classification?.type==='game' ? 'GAME' : 'APP';
    $('detailSummary').textContent=summary;
    $('detailDescription').textContent=state.renderMode==='future' ? ($('description').value.trim()||summary) : summary;
    $('detailMeta').textContent=($('version').value||'?')+' · '+$('platforms').value+' · '+$('permissions').textContent;
    for(const id of ['cardIcon','detailIcon']) {
      const node=$(id);node.replaceChildren();
      if(state.iconUrl) { const img=document.createElement('img');img.src=state.iconUrl;img.alt='';node.append(img); }
      else node.textContent='🃏';
    }
    $('detailCover').classList.toggle('hidden',state.renderMode!=='future'||!state.coverUrl);
    if(state.coverUrl && state.renderMode==='future')$('detailCover').src=state.coverUrl;
    $('gallery').replaceChildren();
    if(state.renderMode==='future') for(const [i,url] of state.shots.entries()) {
      const img=document.createElement('img');img.src=url;img.alt='Screenshot '+(i+1);img.loading='lazy';$('gallery').append(img);
    }
    $('catalogPane').classList.toggle('hidden',state.selectedScreen!=='catalog');
    $('detailsPane').classList.toggle('hidden',state.selectedScreen!=='details');
    $('device').className='device '+state.device;
    document.querySelectorAll('[data-screen]').forEach(b=>{b.classList.toggle('active',b.dataset.screen===state.selectedScreen);b.setAttribute('aria-pressed',String(b.dataset.screen===state.selectedScreen));});
    document.querySelectorAll('[data-device]').forEach(b=>{b.classList.toggle('active',b.dataset.device===state.device);b.setAttribute('aria-pressed',String(b.dataset.device===state.device));});
    $('exportPackage').disabled=!state.entries;
    $('exportPackage').title=state.entries?'Export with a bumped immutable release version':'Import a .tavix file first';
    document.querySelector('.preview-footnote').textContent = state.renderMode==='current'
      ? 'Current Tavi 0.3.175: name, icon, summary, install approval and technical details. Store cover/gallery data is not yet consumed by the live host.'
      : 'Rich-product concept: cover, screenshots and extended descriptions are EDITOR PREVIEW ONLY. Tavi needs a separately approved metadata contract to render these publicly.';
  }
  function setAssetUrls() {
    removeUrls();
    const icon=state.manifest?.icon;
    state.iconUrl=icon ? getImageUrl(icon) : '';
    const cover=[...state.uploads.keys()].find(x=>/^store\/editor-cover\.(webp|png|svg)$/.test(x)) ||
      ['store/editor-cover.webp','store/editor-cover.png','store/editor-cover.svg','store/cover.webp','store/cover.png'].find(x=>state.entries?.has(x));
    state.coverUrl=cover ? getImageUrl(cover) : '';
    const ss=state.entries ? galleryPaths(new Map([...state.entries,...state.uploads])) : [];
    state.shots=ss.map(p=>getImageUrl(p));
  }
  async function importPackage(file) {
    if(!file) return;
    setStatus('Checking archive integrity...', 'loading');
    try {
      const entries=await TaviXZip.open(file);
      const manifest=await TaviXZip.check(entries);
      const draft=entries.has('store/editor-draft.json') ? JSON.parse(TaviXZip.txt(entries,'store/editor-draft.json')) : null;
      state.entries=entries;state.manifest=manifest;state.uploads.clear();state.importedVersion=manifest.version;
      $('name').value=manifest.name; $('summary').value=manifest.summary;
      $('description').value=draft?.description||manifest.summary;
      $('category').value=draft?.category||inputCategory(manifest);
      $('version').value=nextPatch(manifest.version);$('publisher').value=manifest.publisher;
      $('platforms').value=(manifest.platforms||['web']).map(x=>x==='windows'?'Windows':x==='android'?'Android':'Web').join(' · ');
      $('appId').textContent=manifest.id;$('permissions').textContent=(manifest.permissions||[]).join(' · ');
      setAssetUrls(); render();
      setStatus('✓ '+manifest.name+' '+manifest.version+' imported. ZIP hashes verified. New export version suggested: '+$('version').value,'success');
    } catch (e) {setStatus('Import blocked: '+e.message,'error');}
  }
  function mimeExt(file) {
    const t = {'image/png':'png','image/webp':'webp','image/svg+xml':'svg'}[file.type];
    if(!t)throw new Error('Use PNG, WebP or SVG artwork.');
    if(file.size>1_000_000)throw new Error('Images must be smaller than 1 MB.');
    return t;
  }
  async function artwork(file,kind) {
    if(!file)return;
    try {
      const ext=mimeExt(file), bytes=new Uint8Array(await file.arrayBuffer());
      if(kind==='icon') {
        const path='store/editor-icon.'+ext;
        state.uploads.set(path,bytes);
        if(!state.manifest)state.manifest={schema:'tavi.extension/v1',kind:'app',id:'example.org.klondike',publisher:'example-org',classification:{type:'game'}};
        state.manifest.icon=path;
      } else if(kind==='cover') {
        for(const key of [...state.uploads.keys()])if(/^store\/editor-cover\./.test(key))state.uploads.delete(key);
        state.uploads.set('store/editor-cover.'+ext,bytes);
      }
      setAssetUrls();render();setStatus('Artwork updated in preview. Export the rebuilt package to include it.','success');
    } catch(e) {setStatus(e.message,'error');}
  }
  async function screenshots(files) {
    if(!files?.length)return;
    if(files.length>3){setStatus('Choose up to three screenshots.','error');return;}
    try {
      const uploaded=[];
      for(let i=0;i<files.length;i++) {
        const ext=mimeExt(files[i]);
        if(ext==='svg')throw new Error('Screenshots must be PNG or WebP.');
        uploaded.push(['store/editor-shot-'+(i+1)+'.'+ext,new Uint8Array(await files[i].arrayBuffer())]);
      }
      for(const key of [...state.uploads.keys()])if(/^store\/editor-shot-/.test(key))state.uploads.delete(key);
      for(const [p,bytes] of uploaded)state.uploads.set(p,bytes);
      setAssetUrls();render();setStatus(files.length+' screenshot(s) added.','success');
    } catch(e) {setStatus(e.message,'error');}
  }
  function draft() {
    const m=checkInput();
    return {
      schema:'tavix.store-listing-draft/v1',status:'draft_only_not_published',
      appId:state.manifest?.id||'example.org.klondike',
      sourceVersion:state.importedVersion||null,version:m.version,name:m.name,summary:m.summary,
      description:$('description').value.trim(),category:$('category').value.trim(),
      publisher:state.manifest?.publisher||'example-org',
      platformSupport:state.manifest?.platforms||['web','windows','android'],
      imagery:{icon:state.manifest?.icon||null,cover:[...state.uploads.keys(),...state.entries?.keys()||[]].find(p=>/^store\/(?:editor-)?cover\.(png|webp|svg)$/.test(p))||null,screenshots:state.entries?galleryPaths(new Map([...state.entries,...state.uploads])):[]},
      review:'Publisher provenance, source ownership, platform acceptance and release authorization required. Pricing is server-owned. Store cover/gallery fields are not live Tavi 0.3.175 metadata.'
    };
  }
  function save(blob,name) {
    const url=URL.createObjectURL(blob), a=document.createElement('a');
    a.href=url;a.download=name;document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),15000);
  }
  async function exportPackage() {
    try {
      if(!state.entries)throw new Error('Open a .tavix package first.');
      const values=checkInput();
      if(!newerVersion(values.version,state.importedVersion)) throw new Error('Choose a package version higher than imported '+state.importedVersion+'.');
      if(!state.manifest?.id||!state.manifest?.publisher)throw new Error('Cannot export an unidentified publisher package.');
      setStatus('Rebuilding TaviX integrity lock and archive...','loading');
      const newManifest={...state.manifest,name:values.name,summary:values.summary,version:values.version};
      const entries=new Map(state.entries);
      entries.delete('tavix.lock.json');
      for(const [path,bytes] of state.uploads) entries.set(path,bytes);
      entries.set('store/editor-draft.json',encoder.encode(JSON.stringify(draft(),null,2)+'\n'));
      const packed=await TaviXZip.relock(entries,newManifest);
      await TaviXZip.check(packed);
      const blob=TaviXZip.build(packed);
      if(blob.size>25*1024*1024)throw new Error('Export exceeds the editor import size limit; optimize your media first.');
      const copied=await TaviXZip.open(new File([blob],'check.tavix'));
      await TaviXZip.check(copied);
      const filename=newManifest.id+'-'+newManifest.version+'.tavix';
      save(blob,filename);
      setStatus('✓ Rebuilt '+filename+' ('+Math.round(blob.size/1024)+' KB) and verified the new lockfile. Publisher staging and native acceptance still required.','success');
    } catch(e){setStatus('Export blocked: '+e.message,'error');}
  }
  function exportDraft() {
    try {
      const data=draft();
      save(new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'}),(state.manifest?.id||'tavix')+'-store-draft.json');
      setStatus('Listing draft exported locally. This does not register a public Store listing.','success');
    }catch(e){setStatus('Draft error: '+e.message,'error');}
  }
  function demo() {
    removeUrls();state.entries=null;state.importedVersion='';state.uploads.clear();
    state.manifest={schema:'tavi.extension/v1',id:'example.org.klondike',publisher:'example-org',kind:'app',classification:{type:'game',categories:['cards','solitaire']},permissions:['ui.panel','storage.private'],platforms:['windows','android','web'],icon:null};
    $('name').value='Klondike Solitaire';$('summary').value='A fully offline Klondike card game. No network, no account, no advertising, no purchases.';
    $('description').value='Arrange the cards into four foundations and unwind with classic solitaire. Enjoy relaxed play with no advertisements.';
    $('version').value='0.1.2';$('publisher').value='example-org';$('category').value='Cards · Solitaire';$('platforms').value='Windows · Android · Web';
    $('appId').textContent=state.manifest.id;$('permissions').textContent=state.manifest.permissions.join(' · ');
    state.iconUrl='sample-icon.png';state.coverUrl='sample-cover.webp';state.shots=[];render();
    setStatus('Demo mode: preview-only. Open your actual .tavix package to edit and export it.','success');
  }
  $('packageFile').addEventListener('change',e=>importPackage(e.target.files?.[0]));
  $('demoBtn').addEventListener('click',demo);
  for(const id of fields)$(id).addEventListener('input',render);
  $('iconFile').addEventListener('change',e=>artwork(e.target.files?.[0],'icon'));
  $('coverFile').addEventListener('change',e=>artwork(e.target.files?.[0],'cover'));
  $('screensFile').addEventListener('change',e=>screenshots(e.target.files));
  $('exportDraft').addEventListener('click',exportDraft);$('exportPackage').addEventListener('click',exportPackage);
  $('cardSelect').addEventListener('click',()=>{state.selectedScreen='details';render();});
  $('backToCatalog').addEventListener('click',()=>{state.selectedScreen='catalog';render();});
  $('fakeInstall').addEventListener('click',()=>setStatus('Install is a visual preview only. No host service has been called.'));
  document.querySelector('.detail-install').addEventListener('click',()=>setStatus('Install is a visual preview only. No host service has been called.'));
  document.querySelectorAll('[data-screen]').forEach(b=>b.addEventListener('click',()=>{state.selectedScreen=b.dataset.screen;render();}));
  document.querySelectorAll('[data-device]').forEach(b=>b.addEventListener('click',()=>{state.device=b.dataset.device;render();}));
  $('renderMode').addEventListener('change',e=>{state.renderMode=e.target.value;render();});
  demo();
  window.TaviXEditorTest = Object.freeze({newerVersion,checkInput});
})();
