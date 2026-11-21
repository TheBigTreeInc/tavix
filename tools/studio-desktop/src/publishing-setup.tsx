import React,{useEffect,useState} from 'react';
import {invoke} from '@tauri-apps/api/core';
import {Alert,Button,Card,CardBody,CardTitle,Label} from '@patternfly/react-core';
import {publishingReadiness} from './publishing-readiness.mjs';
import {CatalogManager} from './catalog-manager';

type Publishing = {githubRepository:string;assetsRegistryEndpoint:string;assetsRegistryAdminPath:string;assetsRegistryCatalogPath:string;assetsRegistryPathsConfigured:boolean;githubConfigured:boolean;assetsRegistryConfigured:boolean;githubWriteAuthorized:boolean;assetsPublishAuthorized:boolean;developerPreviewDistributionConnected:boolean;remotePublishAvailable:boolean;nextSteps:string[]};
type Probe = {schema:string;checkedAt:string;readOnly:boolean;authenticated:boolean;publishingAvailable:boolean;
  checks:{service:string;status:string;code:string}[]};
type Auth = {authenticated:boolean;code:string;howToConnect:string};
type Release = {tag:string;title:string;publishedAt:string;draft:boolean;prerelease:boolean;url:string};
type Releases = {repository:string;scope:string;authenticated:boolean;authCode:string;releases:Release[];officialStorePublished:boolean;catalog?:{status:string;code:string;schema?:string;entries?:number}};
type RegistryCheck={service:string;code:string;count?:number};
type RegistryConnection={schema:string;configured:boolean;read:boolean;inspect:boolean;
 ingestCredentialPresent:boolean;publishCredentialPresent:boolean;serverPublisherApproved:boolean;checks:RegistryCheck[]};
type RegistryCatalog={schema:string;scope:string;connected:boolean;packs:{packId:string;version:string;manifestSha256:string;status:string}[];truncated:boolean};
type RegistryInspection={schema:string;scope:string;connected:boolean;versions:{packId:string;version:string;manifestSha256:string;status:string}[]};
type RegistryMutation={status:string;packId:string;version:string;published?:boolean;officialRegistryPublished?:boolean;entitlementsGranted?:boolean};
type Approved = {sha256:string;packageId:string;version:string;kind:'tavix'|'tavia';status:string;canonicalValid:boolean;storeReady:boolean;issues?:{code:string}[]};
type GithubCatalog={schema:string;repository:string;branch:string;revision:string;sourceSha:string;indexSha:string;sourceEntries:number;publicPacks:number;publicSchematics:number;publicIndexCurrent:boolean;readOnly:boolean;packs:{id:string;version:string;status:string;visibility:string;sha256:string}[]};
type CatalogProposal={schema:string;repository:string;baseRevision:string;proposalSha256:string;packageSha256:string;entry:{id:string;version:string;artifact:string;status:string;visibility:string;sha256:string};diff:{file:string;action:string;before:null;after:Record<string,string>};catalogJsonChanged:boolean;assetUploaded:boolean;priceChanged:boolean;effect:string};
type CatalogPullRequest={status:string;url:string;branch:string;repository:string;publicCatalogUpdated:boolean;officialStorePublished:boolean};
type PublishingPane='catalog'|'githubCatalog'|'settings'|'github'|'registry';
const publishingPanes:{id:PublishingPane;label:string}[]=[
  {id:'catalog',label:'Catalog'},
  {id:'githubCatalog',label:'GitHub catalog sync'},
  {id:'settings',label:'Connections'},
  {id:'github',label:'GitHub releases'},
  {id:'registry',label:'Tavi Assets / LoopRD'}
];
export function PublishingSetup({approved=[]}:{approved?:Approved[]}){
  const [activePane,setActivePane]=useState<PublishingPane>('catalog');
  const [profile,setProfile]=useState<Publishing|null>(null);
  const [repo,setRepo]=useState('');
  const [endpoint,setEndpoint]=useState('');
  const [adminPath,setAdminPath]=useState('');
  const [catalogPath,setCatalogPath]=useState('');
  const [registry,setRegistry]=useState<RegistryConnection|null>(null);
  const [registryCatalog,setRegistryCatalog]=useState<RegistryCatalog|null>(null);
  const [registryInspection,setRegistryInspection]=useState<RegistryInspection|null>(null);
  const [busy,setBusy]=useState(false);
  const [message,setMessage]=useState('');
  const [error,setError]=useState('');
  const [probe,setProbe]=useState<Probe|null>(null);
  const [auth,setAuth]=useState<Auth|null>(null);
  const [live,setLive]=useState<Releases|null>(null);
  const [catalogRemote,setCatalogRemote]=useState<GithubCatalog|null>(null);
  const [catalogProposal,setCatalogProposal]=useState<CatalogProposal|null>(null);
  const [catalogPullRequest,setCatalogPullRequest]=useState<CatalogPullRequest|null>(null);
  const [catalogChosen,setCatalogChosen]=useState('');
  const [chosen,setChosen]=useState('');
  const [receipt,setReceipt]=useState<{status:string;tag?:string;repo:string;digest:string}|null>(null);
  const selected=approved.find(r=>r.sha256===chosen);
  const readiness=publishingReadiness(profile,auth,live,repo,endpoint);
  const confirmedReceipt=receipt?.repo===profile?.githubRepository && receipt?.digest===chosen?receipt:null;
  const eligible=approved.filter(r=>r.status==='review_approved'&&r.canonicalValid&&r.storeReady);
  const eligibleAssets=eligible.filter(r=>r.kind==='tavia');
  useEffect(()=>{
    // Initial destination and login checks are independent. An absent gh login
    // must not hide public GitHub releases or mark the registry connected.
    void invoke<Publishing>('studio_publishing_targets').then(v=>{
      setProfile(v);setRepo(v.githubRepository);setEndpoint(v.assetsRegistryEndpoint);
      setAdminPath(v.assetsRegistryAdminPath||'');setCatalogPath(v.assetsRegistryCatalogPath||'');
    }).catch(()=>setError('Unable to read local publication destination configuration'));
    void invoke<Auth>('studio_github_auth').then(setAuth).catch(()=>
      setAuth({authenticated:false,code:'GITHUB_AUTH_UNAVAILABLE',howToConnect:'Check GitHub CLI installation and sign-in outside Studio'}));
  },[]);
  useEffect(()=>{
    setReceipt(null);
    if(!chosen||!profile?.githubRepository)return;
    let active=true;
    void invoke<{status:string;tag?:string;repo?:string}>('studio_github_release_receipt',{digest:chosen})
      .then(value=>{if(active && value.repo===profile.githubRepository && ['draft','public'].includes(value.status))setReceipt({...value,repo:profile.githubRepository,digest:chosen});})
      .catch(()=>{});
    return ()=>{active=false;};
  },[chosen,profile?.githubRepository]);
  const save=async()=>{
    setBusy(true);setMessage('');setError('');
    try{const v=await invoke<Publishing>('studio_save_publishing_targets',{githubRepository:repo,assetsRegistryEndpoint:endpoint,assetsRegistryAdminPath:adminPath,assetsRegistryCatalogPath:catalogPath});
      setProfile(v);setProbe(null);setLive(null);setReceipt(null);setRegistry(null);setRegistryCatalog(null);setRegistryInspection(null);setMessage('Destinations saved locally. No connection, authorization or publication was performed.');}
    catch{setError('Settings not saved. Use owner/repo, an HTTPS hostname and verified relative /admin and /catalog DAPI paths.');}
    finally{setBusy(false);}
  };
  const check=async()=>{
    setBusy(true);setError('');setMessage('');setProbe(null);
    try{setProbe(await invoke<Probe>('studio_probe_publishing_targets'));}
    catch{setError('Read-only connection check failed. Confirm saved destination and TLS/network settings.');}
    finally{setBusy(false);}
  };
  const checkLogin=async()=>{
    setBusy(true);setError('');
    try{setAuth(await invoke<Auth>('studio_github_auth'));}
    catch{setAuth({authenticated:false,code:'GITHUB_AUTH_UNAVAILABLE',howToConnect:'Check GitHub CLI and sign in outside Studio'});}
    finally{setBusy(false);}
  };
  const refreshLive=async()=>{
    if(!readiness.mayInspectReleases){setError('Save the GitHub repository destination before refreshing live releases.');return;}
    setBusy(true);setError('');setMessage('');
    // Public discovery is supported without gh login. Inspect each result
    // separately so failure to check authentication cannot hide public data.
    const requests=[invoke<Auth>('studio_github_auth'),invoke<Releases>('studio_github_releases')] as const;
    const [authResult,liveResult]=await Promise.allSettled(requests);
    if(authResult.status==='fulfilled')setAuth(authResult.value);
    else setAuth({authenticated:false,code:'GITHUB_AUTH_UNAVAILABLE',howToConnect:'Check GitHub CLI outside Studio'});
    if(liveResult.status==='fulfilled' && liveResult.value.repository===profile?.githubRepository){
      setLive(liveResult.value);
      setMessage('Live GitHub releases refreshed. This is not the official Tavi Assets store catalog.');
    }else{
      setLive(null);
      setError('Live GitHub release discovery failed; authentication can still be checked separately.');
    }
    setBusy(false);
  };
  const githubLogin=async()=>{
    setBusy(true);setError('');setMessage('');
    try{const result=await invoke<{launched:boolean;message:string}>('studio_github_login');
      if(result.launched)setMessage(result.message);
      else setError('Unable to launch GitHub browser login.');
    }catch(e){setError('GitHub sign-in could not be started: '+String(e).slice(0,180));}
    finally{setBusy(false);}
  };
  const syncGithubCatalog=async()=>{
    setBusy(true);setError('');setMessage('');setCatalogProposal(null);setCatalogPullRequest(null);
    try{const result=await invoke<GithubCatalog>('studio_github_catalog_sync');
      if(result.schema!=='tavix.studio.github-catalog/v1'||result.repository!=='TheBigTreeInc/tavi-assets'||!result.publicIndexCurrent)
        throw new Error('Unexpected GitHub catalog response');
      setCatalogRemote(result);setMessage('GitHub catalog loaded from revision '+result.revision.slice(0,12)+'. No remote changes were made.');
    }catch(e){setCatalogRemote(null);setError('GitHub catalog sync failed: '+String(e).slice(0,220));}
    finally{setBusy(false);}
  };
  const reviewGithubChange=async()=>{
    if(!catalogRemote || !catalogChosen){setError('Sync the current GitHub catalog, then choose one approved asset pack.');return;}
    setBusy(true);setError('');setMessage('');setCatalogProposal(null);setCatalogPullRequest(null);
    try{const result=await invoke<CatalogProposal>('studio_github_catalog_preview',
      {digest:catalogChosen,baseRevision:catalogRemote.revision});
      if(result.schema!=='tavix.studio.catalog-proposal/v1'||result.baseRevision!==catalogRemote.revision||
         result.packageSha256!==catalogChosen||result.entry.status!=='draft'||result.catalogJsonChanged||result.assetUploaded)
        throw new Error('Unexpected catalog proposal');
      setCatalogProposal(result);setMessage('Review the exact draft-only change below. No GitHub write was made.');
    }catch(e){setError('Catalog review failed: '+String(e).slice(0,210));}
    finally{setBusy(false);}
  };
  const prepareGithubChange=async()=>{
    const proposal=catalogProposal;
    if(!catalogRemote||!proposal||!catalogChosen||!readiness.githubAuthenticated){
      setError('Refresh the catalog, review the change and sign in to GitHub first.');return;
    }
    if(!window.confirm(`Prepare a DRAFT pull request in ${proposal.repository} for ${proposal.entry.id} v${proposal.entry.version}?\n\nOnly catalog.source.json gets a proposed DRAFT entry. No package binary, public catalog, Gold price or Store listing is published. The new GitHub branch and PR in a public repository may be visible to others.`))return;
    const typed=window.prompt('Confirm this exact locally approved asset: paste its complete SHA-256:', '');
    if(typed!==catalogChosen){setError('SHA-256 confirmation does not match. Nothing was sent to GitHub.');return;}
    if(!window.confirm('FINAL CONFIRMATION: create a GitHub DRAFT PULL REQUEST now? This is a remote branch/PR write, not publication or merge.'))return;
    setBusy(true);setError('');setMessage('');
    try{const result=await invoke<CatalogPullRequest>('studio_github_catalog_prepare',{
      digest:catalogChosen,baseRevision:proposal.baseRevision,proposalSha256:proposal.proposalSha256,
      confirmDigest:typed,operatorApproved:true});
      if(result.status!=='draft_pr_created'||result.publicCatalogUpdated||result.officialStorePublished)
        throw new Error('Unexpected GitHub PR result');
      setCatalogPullRequest(result);setMessage('A draft catalog pull request was created. Neither public index nor official store was published.');
    }catch(e){setError('GitHub catalog proposal not confirmed: '+String(e).slice(0,200));}
    finally{setBusy(false);}
  };
  const action=async(mode:'draft'|'publish')=>{
    if(!selected || !readiness.mayRequestGitHubWrite){setError('Save the target repository and verify your GitHub CLI sign-in before publishing.');return;}
    const intent=mode==='draft'?'create a private GitHub draft':'make the GitHub release publicly downloadable';
    if(!window.confirm(`You are about to ${intent} for ${selected.packageId} v${selected.version} in ${profile?.githubRepository}.\n\nThis is GitHub distribution ONLY, not Tavi Assets / LoopRD publication. Continue?`))return;
    const verified=window.prompt('To approve this exact operation, paste the FULL SHA-256 of the selected artifact:', '');
    if(verified!==selected.sha256){setError('Exact SHA-256 confirmation did not match. No release operation was performed.');return;}
    if(!window.confirm(mode==='publish'?'FINAL CONFIRMATION: make the GitHub draft PUBLIC now?':'Confirm creation of a new GitHub DRAFT only?'))return;
    setBusy(true);setError('');setMessage('');
    try{
      const result=await invoke<{status:string;tag:string}>(mode==='draft'?'studio_github_create_draft':'studio_github_publish_draft',
        {digest:selected.sha256,confirmDigest:verified,publicDistributionApproved:true});
      setReceipt({status:result.status,tag:result.tag,repo:profile!.githubRepository,digest:selected.sha256});
      setMessage(`GitHub ${result.status==='draft'?'draft created':'release published'}: ${result.tag}. LoopRD registry publication and entitlements remain separate.`);
      try{setLive(await invoke<Releases>('studio_github_releases'));}catch{/* Keep confirmed action outcome. */}
    }catch(e){setError(String(e).slice(0,220));}
    finally{setBusy(false);}
  };
  const registrySaved=Boolean(profile?.assetsRegistryConfigured && profile?.assetsRegistryPathsConfigured &&
    endpoint===profile?.assetsRegistryEndpoint && adminPath===profile?.assetsRegistryAdminPath &&
    catalogPath===profile?.assetsRegistryCatalogPath);
  const connectRegistry=async()=>{
    setBusy(true);setError('');setMessage('');setRegistry(null);setRegistryCatalog(null);setRegistryInspection(null);
    try{const status=await invoke<RegistryConnection>('studio_looprd_connect');setRegistry(status);
      setMessage(status.read||status.inspect?'LoopRD responded to the authorized registry request(s). Connection status is shown below.':'LoopRD destination checked; no authorized registry scope was verified.');}
    catch(e){setError('LoopRD connection check failed: '+String(e).slice(0,190));}
    finally{setBusy(false);}
  };
  const viewRegistry=async(section:'catalog'|'inspect')=>{
    setBusy(true);setError('');setMessage('');
    try{if(section==='catalog'){const result=await invoke<RegistryCatalog>('studio_looprd_catalog');setRegistryCatalog(result);}
      else {const result=await invoke<RegistryInspection>('studio_looprd_inspect');setRegistryInspection(result);}
      setMessage(section==='catalog'?'Live published catalog loaded.':'Live staged and published versions loaded.');}
    catch(e){setError('LoopRD '+section+' failed: '+String(e).slice(0,190));}
    finally{setBusy(false);}
  };
  const registryAction=async(mode:'stage'|'publish')=>{
    if(!selected || selected.kind!=='tavia' || !registrySaved){setError('Select a locally approved TAVIA pack and save the LoopRD DAPI paths first.');return;}
    const label=mode==='stage'?'stage this asset pack in LoopRD':'publish this already-staged pack in the official registry';
    if(!window.confirm(`Do you want to ${label}?\n\n${selected.packageId} v${selected.version}\nEndpoint: ${endpoint}${adminPath}\n\nThis operation needs a separate exact-artifact receipt.`))return;
    const digest=window.prompt('Paste the entire SHA-256 of the selected approved TAVIA archive:', '');
    if(digest!==selected.sha256){setError('Exact artifact digest does not match. No registry operation was attempted.');return;}
    if(!window.confirm(mode==='publish'?'FINAL CONFIRMATION: publish this staged version to the official Tavi Assets registry?':'FINAL CONFIRMATION: upload and stage this reviewed TAVIA in LoopRD?'))return;
    setBusy(true);setError('');setMessage('');
    try{const result=await invoke<RegistryMutation>(mode==='stage'?'studio_looprd_stage':'studio_looprd_publish',
       {digest:selected.sha256,confirmDigest:digest,operatorApproved:true});
      setRegistryInspection(null);setRegistryCatalog(null);
      setMessage(`LoopRD confirmed ${result.status} for ${result.packId} v${result.version}. This does not issue Wallet/Gold entitlements. Refresh the live registry to confirm.`);
    }catch(e){setError('Registry '+mode+' not completed: '+String(e).slice(0,220));}
    finally{setBusy(false);}
  };
  const tabKeyDown=(event:React.KeyboardEvent<HTMLButtonElement>,index:number)=>{
    let next=index;
    if(event.key==='ArrowRight')next=(index+1)%publishingPanes.length;
    else if(event.key==='ArrowLeft')next=(index+publishingPanes.length-1)%publishingPanes.length;
    else if(event.key==='Home')next=0;
    else if(event.key==='End')next=publishingPanes.length-1;
    else return;
    event.preventDefault();
    const pane=publishingPanes[next];setActivePane(pane.id);
    document.getElementById('studio-publishing-tab-'+pane.id)?.focus();
  };
  return <div className="studio-publishing-workspace">
    <nav className="studio-publishing-tabs" role="tablist" aria-label="Publishing workspace sections">
      {publishingPanes.map((pane,index)=><button key={pane.id} type="button" role="tab"
        id={'studio-publishing-tab-'+pane.id} aria-controls={'studio-publishing-panel-'+pane.id}
        aria-selected={activePane===pane.id} tabIndex={activePane===pane.id?0:-1}
        className={'studio-publishing-tab'+(activePane===pane.id?' studio-publishing-tab-active':'')}
        onClick={()=>setActivePane(pane.id)} onKeyDown={event=>tabKeyDown(event,index)}>{pane.label}</button>)}
    </nav>
    {error&&<Alert variant="danger" title={error} isInline/>}
    {message&&<Alert variant="success" title={message} isInline/>}
    <section id="studio-publishing-panel-catalog" role="tabpanel" aria-labelledby="studio-publishing-tab-catalog"
      className="studio-publishing-pane" hidden={activePane!=='catalog'}>
    <Card><CardBody><div className="studio-catalog-sync-strip">
      <div><strong>GitHub asset catalog</strong><p className="studio-muted">Source: TheBigTreeInc/tavi-assets · sync approved public asset metadata, separate from app releases and LoopRD pricing.</p></div>
      <Button variant="primary" isDisabled={busy} onClick={()=>{setActivePane('githubCatalog');void syncGithubCatalog();}}>Sync from GitHub</Button>
      <Button variant="secondary" onClick={()=>setActivePane('githubCatalog')}>Review changes</Button>
    </div></CardBody></Card>
    <CatalogManager submissions={approved} published={registryCatalog?.packs||[]}
      inspected={registryInspection?.versions||[]} registryChecked={Boolean(registryCatalog||registryInspection)}/>
    </section>
    <section id="studio-publishing-panel-githubCatalog" role="tabpanel" aria-labelledby="studio-publishing-tab-githubCatalog"
      className="studio-publishing-pane" hidden={activePane!=='githubCatalog'}>
      <Card><CardTitle>GitHub asset catalog synchronization</CardTitle><CardBody>
        <p>Studio edits <code>catalog.source.json</code> in <strong>TheBigTreeInc/tavi-assets</strong>.
          <code>catalog.json</code> is the generated public index. This does not change the application repository
          <code>tavi.repository.json</code> or LoopRD store offers.</p>
        <div className="studio-actions"><Button onClick={()=>void syncGithubCatalog()} isDisabled={busy}>Sync from GitHub</Button>
          <Button variant="secondary" onClick={()=>void githubLogin()} isDisabled={busy||auth?.authenticated===true}>Sign in with GitHub (browser)</Button>
          <Button variant="secondary" onClick={()=>void checkLogin()} isDisabled={busy}>Check GitHub sign-in</Button></div>
        <p className="studio-muted">GitHub login uses the native GitHub CLI and your browser. Tokens are managed outside Studio;
          you never paste a personal access token here. An interactive login window may open on Windows.
          {auth?.authenticated?' GitHub CLI currently signed in.':' Sign in before submitting a draft PR; public catalog sync does not require login.'}</p>
        {catalogRemote?<>
          <div className="studio-github-snapshot" role="status">
            <strong>Remote: {catalogRemote.repository}</strong>
            <span>Branch: <code>{catalogRemote.branch}</code> · revision <code title={catalogRemote.revision}>{catalogRemote.revision.slice(0,12)}</code></span>
            <span>{catalogRemote.sourceEntries} source records · {catalogRemote.publicPacks} published public packs · {catalogRemote.publicSchematics} compatibility blueprints</span>
          </div>
          <p className="studio-muted">Last fetched revision shown above. The public index was checked against its source at the same revision. Blueprint entries are compatibility-only, never saleable.</p>
          {catalogRemote.packs.length>0&&<details><summary>View existing GitHub pack source records</summary>
            <div className="studio-github-source-list">{catalogRemote.packs.map(p=><p key={p.id+'@'+p.version}>
              <strong>{p.id} v{p.version}</strong> · {p.status} · {p.visibility}</p>)}</div>
          </details>}
        </>:<Alert variant="info" title="Start by syncing the asset catalog" isInline>
          This reads the current catalog revision without changing any GitHub files.
        </Alert>}
      </CardBody></Card>
      <Card><CardTitle>Review one proposed catalog update</CardTitle><CardBody>
        <p>A locally approved <code>.tavia</code> can be proposed as a <strong>draft</strong> source record.
          No archive is uploaded and it does not appear in the public index until independently approved and distributed.
          Gold prices, Listed and Testing remain local drafts until LoopRD supports authoritative offers.</p>
        <label htmlFor="studio-github-catalog-candidate"><strong>Locally approved asset pack</strong></label>
        <select id="studio-github-catalog-candidate" value={catalogChosen} className="studio-select" onChange={e=>{
          setCatalogChosen(e.target.value);setCatalogProposal(null);setCatalogPullRequest(null);}}>
          <option value="">Choose an approved TAVIA…</option>
          {eligibleAssets.map(p=><option key={p.sha256} value={p.sha256}>{p.packageId} · v{p.version} · {p.sha256.slice(0,12)}</option>)}
        </select>
        <div className="studio-actions"><Button variant="secondary" isDisabled={busy||!catalogRemote||!catalogChosen}
          onClick={()=>void reviewGithubChange()}>Review changes</Button></div>
        {catalogProposal&&<div className="studio-github-diff" aria-label="Exact proposed GitHub catalog change">
          <strong>Proposed change · catalog.source.json</strong>
          <p>Base revision <code>{catalogProposal.baseRevision.slice(0,12)}</code> · new local draft source SHA-256 <code>{catalogProposal.proposalSha256.slice(0,16)}…</code></p>
          <pre>{JSON.stringify(catalogProposal.diff,null,2)}</pre>
          <p className="studio-muted">{catalogProposal.effect}</p>
          <Button variant="primary" isDisabled={busy||!readiness.githubAuthenticated}
            onClick={()=>void prepareGithubChange()}>Prepare draft GitHub pull request…</Button>
          {!readiness.githubAuthenticated&&<p className="studio-muted">Sign in with GitHub and check the session before preparing a PR.</p>}
        </div>}
        {catalogPullRequest&&<Alert variant="success" title="GitHub draft pull request created" isInline>
          <a href={catalogPullRequest.url} target="_blank" rel="noreferrer">Open reviewed catalog draft</a>
          <p>Public catalog and LoopRD store remain unchanged. No release was performed.</p>
        </Alert>}
      </CardBody></Card>
    </section>
    <section id="studio-publishing-panel-settings" role="tabpanel" aria-labelledby="studio-publishing-tab-settings"
      className="studio-publishing-pane" hidden={activePane!=='settings'}>
    <Card><CardTitle>Publishing destinations & authorization</CardTitle><CardBody>
      <p>First-class operator settings. No credentials are stored in the Studio webview.</p>
      <div className="studio-publishing-destinations-grid">
        <div><label htmlFor="studio-publish-repo"><strong>GitHub catalog repository</strong> (owner/repo)</label>
          <input id="studio-publish-repo" className="studio-publish-input" placeholder="TheBigTreeInc/tavi-assets" value={repo} maxLength={165} onChange={e=>setRepo(e.target.value)}/></div>
        <div><label htmlFor="studio-publish-registry"><strong>LoopRD asset registry</strong> (HTTPS hostname only)</label>
          <input id="studio-publish-registry" className="studio-publish-input" placeholder="https://registry.example.org" value={endpoint} maxLength={180} onChange={e=>setEndpoint(e.target.value)}/></div>
      </div>
      <div className="studio-registry-controls">
        <div><label htmlFor="studio-registry-admin"><strong>DAPI admin path</strong></label>
          <input id="studio-registry-admin" className="studio-publish-input" placeholder="/your/deployed/component/admin" value={adminPath} maxLength={180} onChange={e=>setAdminPath(e.target.value)}/></div>
        <div><label htmlFor="studio-registry-catalog"><strong>DAPI catalog path</strong></label>
          <input id="studio-registry-catalog" className="studio-publish-input" placeholder="/your/deployed/component/catalog" value={catalogPath} maxLength={180} onChange={e=>setCatalogPath(e.target.value)}/></div>
      </div>
      <p className="studio-registry-help">These paths are deployment-specific. Copy them from the LoopRD component's approved DAPI routes; don't guess from the hostname. Credentials are never entered in this screen.</p>
      <div className="studio-actions"><Button onClick={()=>void save()} isDisabled={busy}>Save publishing settings</Button>
        <Button variant="secondary" onClick={()=>void check()} isDisabled={busy||readiness.pendingChanges||!(profile?.githubConfigured||profile?.assetsRegistryConfigured)}>Check HTTPS reachability</Button>
        <Button variant="secondary" onClick={()=>void checkLogin()} isDisabled={busy}>Check GitHub sign-in</Button>
        <Button variant="secondary" onClick={()=>{setActivePane('github');void refreshLive();}} isDisabled={busy||!readiness.mayInspectReleases}>Refresh live GitHub releases</Button>
      </div>
      <div className="studio-publish-readiness" role="status" aria-label="Publishing connection status">
        <div><strong>GitHub destination</strong><Label color={readiness.githubConfigured&&!readiness.pendingChanges?'green':'orange'}>
          {readiness.pendingChanges?'Save changes':readiness.githubConfigured?'Saved':'Not configured'}</Label></div>
        <div><strong>GitHub CLI sign-in</strong><Label color={readiness.githubAuthenticated?'green':'orange'}>
          {auth===null?'Checking…':readiness.githubAuthenticated?'Signed in (repo rights unverified)':auth.code==='GITHUB_CLI_MISSING'?'CLI missing':'Not signed in'}</Label></div>
        <div><strong>GitHub release visibility</strong><Label color={readiness.liveFresh?'green':'orange'}>
          {readiness.liveFresh?'Fetched live':readiness.pendingChanges?'Unsaved destination':'Not checked'}</Label></div>
        <div><strong>Official Tavi Assets / LoopRD</strong><Label color={registry?.inspect?'green':registry?.read?'blue':'orange'}>
          {registry?.inspect?'Registry operator access verified':registry?.read?'Catalog read verified':registrySaved?'Not connected':'Configure DAPI paths'}</Label></div>
      </div>
      {(readiness.pendingChanges || Boolean(profile && (adminPath!==profile.assetsRegistryAdminPath || catalogPath!==profile.assetsRegistryCatalogPath))) &&
        <p className="studio-muted">Publication settings have changed. Save all destinations and DAPI paths before checking the live registry or creating a release.</p>}
      {auth&&!auth.authenticated&&<p className="studio-muted">{auth.howToConnect}</p>}
      {probe&&<div className="studio-connection-results"><strong>Transport check · {probe.checkedAt}</strong>
        {probe.checks.map(c=><p key={c.service}><strong>{c.service}:</strong> <Label color={c.status==='responding'?'green':'orange'}>{c.status}</Label> <code>{c.code}</code></p>)}
        <p className="studio-muted">HTTPS responding does not prove publisher authorization or LoopRD API compatibility.</p></div>}
    </CardBody></Card>
    </section>
    <section id="studio-publishing-panel-registry" role="tabpanel" aria-labelledby="studio-publishing-tab-registry"
      className="studio-publishing-pane" hidden={activePane!=='registry'}>
    <Card><CardTitle>Connect to live Tavi Assets / LoopRD</CardTitle><CardBody>
      <p>Connect using the saved HTTPS DAPI routes and separately provisioned short-lived, scoped service credentials in the trusted native Studio process. A Tavi account login alone does not grant publisher rights.</p>
      <div className="studio-actions"><Button onClick={()=>void connectRegistry()} isDisabled={busy||!registrySaved}>Connect / test permissions</Button>
        <Button variant="secondary" onClick={()=>void viewRegistry('catalog')} isDisabled={busy||!registrySaved}>View published catalog</Button>
        <Button variant="secondary" onClick={()=>void viewRegistry('inspect')} isDisabled={busy||!registrySaved}>View staged &amp; published versions</Button></div>
      {!registrySaved&&<Alert variant="info" title="Save the DAPI routes first" isInline>The registry hostname, admin path and catalog path must all be saved before this connection can be tested.{' '}
        <Button variant="link" size="sm" onClick={()=>setActivePane('settings')}>Open connections</Button></Alert>}
      {registry&&<><div className="studio-registry-row"><strong>Published catalog read</strong><Label color={registry.read?'green':'orange'}>{registry.read?'Authorized':'Not verified'}</Label>
        <strong>Operator inspection</strong><Label color={registry.inspect?'green':'orange'}>{registry.inspect?'Authorized':'Not verified'}</Label></div>
        <p className="studio-muted">Credential injection detected: ingest {registry.ingestCredentialPresent?'present (unverified)':'absent'}, publish {registry.publishCredentialPresent?'present (unverified)':'absent'}.
        Credential presence does not prove server authorization.</p>
        {registry.checks.map(c=><p key={c.service}><strong>{c.service}:</strong> <code>{c.code}</code>{c.count===undefined?'':` · ${c.count} records`}</p>)}
      </>}
      {registryCatalog&&<div><strong>Live catalog: {registryCatalog.packs.length} published entries</strong>
        {registryCatalog.packs.length===0?<p>No published packs returned.</p>:<div className="studio-release-list">{registryCatalog.packs.map(r=><div key={`${r.packId}:${r.version}`} className="studio-registry-row"><strong>{r.packId} v{r.version}</strong><Label color="green">Published</Label><code>{r.manifestSha256.slice(0,12)}…</code></div>)}</div>}
        {registryCatalog.truncated&&<p className="studio-muted">Catalog response was truncated for safe display.</p>}</div>}
      {registryInspection&&<div><strong>Registry inspection: {registryInspection.versions.length} versions</strong>
        <div className="studio-release-list">{registryInspection.versions.map(r=><div key={`${r.packId}:${r.version}`} className="studio-registry-row"><strong>{r.packId} v{r.version}</strong><Label color={r.status==='published'?'green':r.status==='ready'?'blue':'orange'}>{r.status}</Label><code>{r.manifestSha256.slice(0,12)}…</code></div>)}</div>
      </div>}
      <details><summary>How to provide an authorized connection</summary>
        <p>LoopRD must have the Tavi Assets component deployed with <code>assets:read</code> on /catalog and service-principal <code>assets:ingest</code> or <code>assets:publish</code> on /admin. Studio receives <code>LOOPRD_ASSETS_READ_TOKEN</code>, <code>LOOPRD_ASSETS_INGEST_TOKEN</code> and <code>LOOPRD_ASSETS_PUBLISH_TOKEN</code> only from its trusted launcher or session broker, never the renderer or saved settings. Restart Studio after provisioning them.</p>
        <p>Official operator publication requires an independently approved receipt for the exact operation, pack, version, digest and endpoint, plus a separate confirmation. The Tavi/Social <code>ecosystemAdmin</code> delegation broker is a separate prerequisite for automatic account-based login; this adapter does not impersonate it.</p>
      </details>
    </CardBody></Card>
    <Card><CardTitle>Stage or publish an approved Tavi Assets pack</CardTitle><CardBody>
      <Alert variant="warning" title="Separate official publication approval" isInline>
        Only approved <code>.tavia</code> packs may be staged or published. Publication requires a live authorized operator service principal, an independent exact-artifact receipt chosen through the native file picker, and a second confirmation. Neither action grants entitlements or updates Gold.</Alert>
      <p><strong>Selected pack:</strong> {selected?.kind==='tavia'?`${selected.packageId} v${selected.version}`:'Choose a locally approved .tavia pack in the release selector under GitHub releases.'}</p>
      <div className="studio-actions"><Button variant="secondary" onClick={()=>void registryAction('stage')} isDisabled={busy||!registrySaved||!registry?.ingestCredentialPresent||selected?.kind!=='tavia'}>Stage in LoopRD…</Button>
        <Button variant="danger" onClick={()=>void registryAction('publish')} isDisabled={busy||!registrySaved||!registry?.inspect||!registry.publishCredentialPresent||selected?.kind!=='tavia'}>Publish staged pack…</Button>
        <Button variant="link" onClick={()=>setActivePane('github')}>Choose approved package</Button></div>
      <p className="studio-muted">Stage requires canonical Tavi Assets validation and an <code>assets:ingest</code> credential; publish requires an existing server-side ready version and <code>assets:publish</code>. No source Git pull, commit or push is made.</p>
    </CardBody></Card>
    </section>
    <section id="studio-publishing-panel-github" role="tabpanel" aria-labelledby="studio-publishing-tab-github"
      className="studio-publishing-pane" hidden={activePane!=='github'}>
    <Card><CardTitle>What is live on GitHub?</CardTitle><CardBody>
      <p>Current releases for <strong>{profile?.githubRepository||'unconfigured repository'}</strong>.
        This lists GitHub release artifacts, not the official Tavi Store catalog.</p>
      {live&&<><p><strong>Public catalog.json:</strong> <Label color={live.catalog?.status==='visible'?'green':'orange'}>{live.catalog?.status||'not checked'}</Label> {live.catalog?.schema||live.catalog?.code||''} {typeof live.catalog?.entries==='number'?`· ${live.catalog.entries} entries`:''}</p><p className="studio-muted">Visibility: {live.scope==='authenticated'?'Authenticated account (includes drafts)':'Public releases only'}</p>
        {live.releases.length===0?<p>No GitHub releases returned.</p>:
        <div className="studio-release-list">{live.releases.map(r=><div key={r.tag} className="studio-release-item">
          <strong>{r.title||r.tag}</strong> <Label color={r.draft?'orange':'green'}>{r.draft?'Draft':'Published'}</Label>
          <small>{r.tag} · {r.publishedAt||'unpublished'}</small>
          {r.url&&<a href={r.url} target="_blank" rel="noreferrer">View GitHub release</a>}
        </div>)}</div>}</>}
      {!live&&<p className="studio-muted">Refresh this repository’s releases to load the current remote state.</p>}
      <div className="studio-actions"><Button variant="secondary" onClick={()=>void refreshLive()} isDisabled={busy||!readiness.mayInspectReleases}>Refresh live GitHub releases</Button></div>
    </CardBody></Card>
    <Card><CardTitle>Release an approved artifact from Studio</CardTitle><CardBody>
      <Alert variant="warning" title="Public distribution only" isInline>
        GitHub releases can make downloads publicly accessible. Do not publish paid/restricted packs here.
        This workflow never registers the pack in LoopRD, grants Gold/entitlements, or publishes to the official Tavi Store.
      </Alert>
      <label htmlFor="studio-publish-approval"><strong>Locally approved package</strong></label>
      <select id="studio-publish-approval" className="studio-select" value={chosen} onChange={e=>setChosen(e.target.value)}>
        <option value="">Choose an approved submission…</option>
        {eligible.map(item=><option key={item.sha256} value={item.sha256}>{item.packageId} · {item.version} · {item.kind} · {item.sha256.slice(0,12)}</option>)}
      </select>
      {selected&&<><p className="studio-mono">Exact SHA-256: {selected.sha256}</p>
        {selected.issues?.some(f=>f.code==='ASSET_DEPENDENCIES_EXTERNAL')&&<p className="studio-publish-dependency-warning">
          This package has external asset dependencies. Local approval is not proof that required packs are installed or compatible; verify this before distribution.
        </p>}</>}
      {confirmedReceipt&&<p>Local GitHub receipt for this exact artifact and repository: <Label color={confirmedReceipt.status==='public'?'green':'orange'}>{confirmedReceipt.status}</Label> {confirmedReceipt.tag}</p>}
      <div className="studio-actions"><Button onClick={()=>void action('draft')} isDisabled={busy||!selected||!readiness.mayRequestGitHubWrite||confirmedReceipt?.status==='draft'||confirmedReceipt?.status==='public'}>Create GitHub draft</Button>
        <Button variant="danger" onClick={()=>void action('publish')} isDisabled={busy||!selected||!readiness.mayRequestGitHubWrite||confirmedReceipt?.status!=='draft'}>Publish GitHub draft publicly…</Button></div>
      <p className="studio-muted">Requires <code>gh</code> authenticated outside Studio (for example <code>gh auth login</code>). Every write requires a separate operator confirmation with the complete artifact SHA-256. No source checkout pull, commit or push is executed.</p>
    </CardBody></Card>
    </section>
  </div>;
}
