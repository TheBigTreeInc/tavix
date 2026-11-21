import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { invoke } from '@tauri-apps/api/core';
import {
  Alert, Button, Card, CardBody, CardTitle, Label, Masthead, MastheadBrand,
  MastheadContent, MastheadMain, Nav, NavItem, NavList, Page, PageSection,
  PageSidebar, PageSidebarBody, Spinner
} from '@patternfly/react-core';
import '@patternfly/react-core/dist/styles/base.css';
import './studio.css';
import {PackBrowser} from './pack-browser';
import {PublishingSetup} from './publishing-setup';
import {PackageSelector} from './package-selector';
import {BlueprintLibrary,type Blueprint} from './blueprint-library';
import {ImportSetupDialog} from './import-setup';
import {TavibImportDialog,type TavibDiscovery} from './tavib-import';
import {planBlueprintReview} from './blueprint-review-action.mjs';

type Package = { id: string; name: string; version: string; classification: 'app' | 'game' };
type Snapshot = { toolVersion: string; gitCommit: string; gitDirty: boolean; assetsCheckoutDetected: boolean; packages: Package[] };
type Event = { id: string; level: string; code: string; timestamp: string };
type HealthCheck = { id:string; status:'ready'|'blocked'|'pending'; code:string; message:string; nextStep:string };
type Attempt = { at:string; operation:string; code:string; kind:string; digestPrefix:string };
type Health = { schema:string; source:string; checks:HealthCheck[]; recentAttempts:Attempt[]; diagnosticOnly:boolean };
type Failure = { at:string; operation:string; code:string };
type Finding = { code:string; severity:string; message:string; resource:string };
type Submission = {
  sha256:string; kind:'tavix'|'tavia'; packageId:string; version:string; title:string;
  canonicalValid:boolean; storeReady:boolean; status:'draft'|'changes_requested'|'review_approved';
  submittedAt:number; reviewerNote:string; issues:Finding[];
  blueprint:{id:string; title:string; present:number; required:number; designerChecklist:string[]}|null;
  assetDependencies:number;
};
type Section = 'overview'|'submissions'|'packages'|'blueprints'|'assets'|'storefront'|'publishing'|'connections'|'operations'|'events';
const sections: { id:Section; label:string }[] = [
  {id:'overview',label:'Overview'}, {id:'submissions',label:'Submission review'},
  {id:'packages',label:'Games & apps'}, {id:'blueprints',label:'Asset blueprints'},
  {id:'assets',label:'Assets & objects'}, {id:'storefront',label:'Official storefront'}, {id:'publishing',label:'Publishing'},
  {id:'connections',label:'Connections'}, {id:'operations',label:'Operations'}, {id:'events',label:'Events'}
];
const STUDIO_UI_VERSION = '0.1.60';
const isValidated = (item:Submission) => item.canonicalValid && item.storeReady;

function App() {
  const [section,setSection] = useState<Section>('overview');
  const [snapshot,setSnapshot] = useState<Snapshot|null>(null);
  const [events,setEvents] = useState<Event[]>([]);
  const [health,setHealth] = useState<Health|null>(null);
  const [failures,setFailures] = useState<Failure[]>([]);
  const [reviews,setReviews] = useState<Submission[]>([]);
  const [blueprints,setBlueprints] = useState<Blueprint[]>([]);
  const [preferredBlueprintId,setPreferredBlueprintId] = useState('');
  const [importSetup,setImportSetup] = useState<Submission|null>(null);
  const [tavibDiscovery,setTavibDiscovery] = useState<TavibDiscovery|null>(null);
  const [refreshing,setRefreshing] = useState(false);
  const [selectedId,setSelectedId] = useState('');
  const [note,setNote] = useState('');
  const [error,setError] = useState('');
  const [serviceErrors,setServiceErrors] = useState<Record<string,string>>({});
  const [notice,setNotice] = useState('');
  const [loading,setLoading] = useState(true);
  const [busy,setBusy] = useState(false);
  const refresh = async () => {
    // Keep the current page mounted while refreshing; prevent scroll jumps.
    setRefreshing(true);
    const results = await Promise.allSettled([
      invoke<Snapshot>('workspace_snapshot'), invoke<Event[]>('recent_events'),
      invoke<Submission[]>('review_submissions'), invoke<Blueprint[]>('review_blueprints'),
      invoke<Health>('studio_health')
    ]);
    if (results[0].status==='fulfilled') setSnapshot(results[0].value);
    if (results[1].status==='fulfilled') setEvents(results[1].value);
    if (results[2].status==='fulfilled') setReviews(results[2].value);
    if (results[3].status==='fulfilled') setBlueprints(results[3].value);
    if (results[4].status==='fulfilled') setHealth(results[4].value);
    const names = ['workspace','events','submissions','blueprints','health'];
    const serviceCodes = ['STUDIO_WORKSPACE_UNAVAILABLE','STUDIO_EVENTS_UNAVAILABLE',
      'STUDIO_REVIEWS_UNAVAILABLE','STUDIO_BLUEPRINTS_UNAVAILABLE','STUDIO_HEALTH_UNAVAILABLE'];
    const failed: Record<string,string> = {};
    for (let i=0;i<results.length;i++) {
      const entry = results[i];
      if(entry.status==='rejected') {
        // Only a fixed code from the Rust boundary crosses into diagnostics;
        // Python stderr, paths and raw exception messages are never copied.
        const reason = String(entry.reason);
        const safe = /\b(STUDIO_[A-Z0-9_]{3,42}):/.exec(reason);
        failed[names[i]] = safe ? safe[1] : serviceCodes[i];
      }
    }
    setServiceErrors(failed);
    if (failed.workspace) setError('Workspace unavailable. Verify the TaviX source directory and rebuild the current native Studio.');
    const codes = Object.entries(failed).map(([operation,code])=>({at:new Date().toISOString(),operation,code}));
    if (codes.length) setFailures(previous=>[...previous,...codes].slice(-15));
    setLoading(false);setRefreshing(false);
  };
  useEffect(()=>{void refresh();},[]);
  const selected = reviews.find(r=>r.sha256===selectedId) || reviews[0];
  const choose = (item:Submission) => {setSelectedId(item.sha256);setNote(item.reviewerNote||'');};
  const perform = async (action:()=>Promise<unknown>, success:string, operation='review') => {
    setBusy(true);setNotice('');setError('');
    try {await action();setNotice(success);await refresh();}
    catch (err) {
      const message = String(err).slice(0,320);
      // Closing the trusted native file picker is not a failed submission.
      if(operation==='import' && message.includes('Import cancelled'))return;
      setError(message);
      const found = /^([A-Z][A-Z0-9_]{2,47}):/.exec(message);
      setFailures(previous=>[...previous,{at:new Date().toISOString(),operation,code:found?.[1]||'STUDIO_OPERATION_FAILED'}].slice(-15));
      // Refresh private, code-only native journal after an import failure, too.
      try {setHealth(await invoke<Health>('studio_health'));} catch { /* original error remains visible */ }
    }
    finally {setBusy(false);}
  };
  const importPackage = () => perform(async()=>{
    // Always retain and inspect the original before any optional blueprint choice.
    // No renderer-selected file path or privilege is passed to the native host.
    const item=await invoke<Submission>('review_import',{blueprintId:''});
    choose(item);setSection('submissions');setPreferredBlueprintId('');setImportSetup(item);
  },'Submission retained for local review. Select a blueprint or keep it custom.','import');
  const configureImported = (choice:string) => {
    if(!importSetup)return;
    const item=importSetup;
    if(choice && !blueprints.some(bp=>bp.id===choice)){setError('Selected blueprint is no longer in the local catalog. Refresh and choose again.');return;}
    const plan=planBlueprintReview(item.kind,item.blueprint?.id||'',choice);
    void perform(async()=>{
      if(plan.action==='recheck'){
        const updated=await invoke<Submission>('review_recheck',{id:item.sha256,blueprintId:plan.blueprintId});
        choose(updated);
      }
      setPreferredBlueprintId('');setImportSetup(null);
    },choice?'Blueprint checked against the retained pack. Manual review is still required.':
      'Submission kept as custom/unmapped. It is not store-ready.','recheck');
  };
  const decision = (status:'changes_requested'|'review_approved') => {
    if (!selected) return;
    if (status==='review_approved' && !window.confirm('Approve this exact package for a local publication handoff? This does NOT publish it or grant an entitlement.'))return;
    void perform(async()=>{
      const item=await invoke<Submission>('review_decide',{id:selected.sha256,decision:status,note});
      choose(item);
    },status==='review_approved'?'Review approved locally. Publication is still gated.':'Changes requested. Export a feedback ZIP to send the package back to its developer.','decision');
  };
  const exportBundle=(mode:'feedback'|'preview'|'approval')=>{
    if(!selected)return;
    void perform(async()=>{await invoke('review_export',{id:selected.sha256,mode});},
      mode==='preview'?'Developer preview handoff saved. Not listed in the official store.':
      mode==='approval'?'Approved review handoff saved. No automatic publication.':'Feedback ZIP saved with unchanged original package.','export');
  };
  const statusLabel=(item:Submission)=>item.status==='review_approved'?'Locally approved':item.status==='changes_requested'?'Changes requested':'Awaiting review';
  const readiness = health?.checks.find(c=>c.id==='tavia-validator');
  const diagnosticReport = JSON.stringify({
    schema:'tavix.studio.operator-diagnostics/v1',studioVersion:STUDIO_UI_VERSION,
    sourceVersion:snapshot?.toolVersion||'unavailable',serviceErrors,
    connectionSource:health?.source||'unknown',diagnosticOnly:true,
    checks:(health?.checks||[]).map(c=>({id:c.id,status:c.status,code:c.code,nextStep:c.nextStep})),
    recentAttempts:health?.recentAttempts||[],sessionFailures:failures,
    selectedSubmission:selected?{kind:selected.kind,digestPrefix:selected.sha256.slice(0,12),
      canonicalValid:selected.canonicalValid,storeReady:selected.storeReady,
      blueprint:selected.blueprint?.id||null,issueCodes:[...new Set(selected.issues.map(i=>i.code))].slice(0,40)}:null,
    note:'No passwords, tokens, source paths, package contents, reviewer notes or raw exception messages are included.'
  },null,2);
  const copyDiagnostics=async()=>{
    try {await navigator.clipboard.writeText(diagnosticReport);setNotice('Sanitized diagnostics copied. Review the report before sharing.');}
    catch {const field=document.getElementById('studio-diagnostic-report') as HTMLTextAreaElement|null;
      field?.select();setNotice('Automatic clipboard access unavailable. The report is selected; press Ctrl+C to copy.');}
  };
  const connectAssets=()=>void perform(async()=>{await invoke('studio_connect_assets');},
    'Local Tavi Assets checkout selected. The validator will be checked again.','connection');
  const resetAssets=()=>void perform(async()=>{await invoke('studio_reset_assets');},
    'Local override cleared. Studio will try its environment or sibling source.','connection');
  const currentPage=sections.find(item=>item.id===section)?.label||'Overview';
  const versionMismatch=Boolean(snapshot && snapshot.toolVersion!==STUDIO_UI_VERSION);
  const hasAlert=Boolean(error||notice||versionMismatch);
  const masthead=<Masthead><MastheadMain><MastheadBrand><strong className="studio-brand">TaviX Studio <small>v{STUDIO_UI_VERSION}</small></strong></MastheadBrand></MastheadMain>
    <MastheadContent><div className="studio-header-row">
      <h1 className="studio-header-title">{currentPage}</h1>
      <div className="studio-header-tools">
        <details className={'studio-notifications'+(error||versionMismatch?' studio-notifications-warning':'')}>
          <summary aria-label={hasAlert?'Open latest Studio notification':'Open Studio notifications'}>
            <span aria-hidden="true">{error||versionMismatch?'●':notice?'●':'○'}</span> Notifications{hasAlert?' · 1':''}
          </summary>
          <div className="studio-notifications-panel" role={error||versionMismatch?'alert':'status'}>
            {error?<><strong>Action unsuccessful</strong><p>{error}</p>
              <Button variant="link" onClick={()=>setSection('events')}>Show diagnostics</Button></>:
            versionMismatch?<><strong>Studio executable and checkout versions differ</strong><p>Source: {snapshot?.toolVersion}; executable: {STUDIO_UI_VERSION}. Rebuild and launch the current native Studio.</p></>:
            notice?<><strong>Latest action</strong><p>{notice}</p></>:
            <p>No new notifications.</p>}
            {(error||notice)&&<Button variant="link" onClick={()=>{setError('');setNotice('');}}>Dismiss</Button>}
          </div>
        </details>
        <Button variant="secondary" size="sm" onClick={()=>void refresh()} isDisabled={busy||refreshing||loading}>
          {refreshing?'Refreshing…':'Refresh'}
        </Button>
      </div>
    </div></MastheadContent></Masthead>;
  const sidebar=<PageSidebar isSidebarOpen><PageSidebarBody>
    <Nav aria-label="Studio navigation"><NavList>{sections.map(item=><NavItem key={item.id} itemId={item.id} isActive={section===item.id}
      onClick={()=>setSection(item.id)}>{item.label}</NavItem>)}</NavList></Nav>
  </PageSidebarBody></PageSidebar>;
  const queue = <div className="studio-queue-strip" aria-label="Local review status">
    <span><strong>{reviews.filter(r=>r.status==='draft').length}</strong> awaiting review</span>
    <span><strong>{reviews.filter(r=>r.status==='changes_requested').length}</strong> changes requested</span>
    <span><strong>{reviews.filter(r=>r.status==='review_approved').length}</strong> locally approved</span>
  </div>;
  return <Page masthead={masthead} sidebar={sidebar}><PageSection className="studio-main-content">
    {loading&&<Spinner aria-label="Loading workspace"/>}
    <TavibImportDialog discovery={tavibDiscovery} busy={busy} onCancel={()=>setTavibDiscovery(null)}
      onImport={members=>{if(!tavibDiscovery)return; const digest=tavibDiscovery.digest;
        void perform(async()=>{await invoke('review_commit_tavib',{digest,members});setTavibDiscovery(null);},
          'Selected TaviX blueprints imported locally. No application was installed or published.','tavib_import');}}/>
    <ImportSetupDialog item={importSetup} blueprints={blueprints} suggestedChoice={preferredBlueprintId} busy={busy}
      onClose={()=>setImportSetup(null)} onConfirm={configureImported}/>
    {!loading&&section==='overview'&&<>{queue}<div className="studio-grid">
      <Card><CardTitle>Source checkout</CardTitle><CardBody><p>Version: {snapshot?.toolVersion||'unavailable'}</p><p>Commit: {snapshot?.gitCommit||'unavailable'}</p><Label color={snapshot?.gitDirty?'orange':'green'}>{snapshot?.gitDirty?'Tracked changes':'No tracked changes reported'}</Label></CardBody></Card>
      <Card><CardTitle>Tavi Assets validator</CardTitle><CardBody>
        <Label color={readiness?.status==='ready'?'green':'orange'}>{readiness?.status==='ready'?'Validator ready':'Connection required'}</Label>
        <p>{readiness?.message||'Run the Connections readiness check.'}</p>
        {readiness?.status!=='ready'&&<Button variant="secondary" onClick={()=>setSection('connections')}>Connect Tavi Assets</Button>}
      </CardBody></Card>
    </div><Button onClick={()=>setSection('submissions')}>Open review queue</Button> <Button variant="secondary" onClick={()=>setSection('publishing')}>Sync GitHub catalog (Publishing)</Button></>}
    {!loading&&section==='submissions'&&<>
      {serviceErrors.submissions&&<Alert variant="warning" title="Submission history unavailable" isInline>Check Events for {serviceErrors.submissions}; import remains a separate operation.</Alert>}
      <div className="studio-review-toolbar">
        <Button onClick={()=>void importPackage()} isDisabled={busy}>Import package…</Button>
        {queue}
      </div>
      <div className="studio-review-grid">
        <Card><CardTitle>Review queue</CardTitle><CardBody>
          {reviews.length===0?<p>No submissions imported.</p>:reviews.map(item=><button key={item.sha256} type="button"
            className={'studio-review-item'+(selected?.sha256===item.sha256?' studio-review-item-active':'')}
            onClick={()=>choose(item)}>
            <strong>{item.title||item.packageId||'Unnamed package'}</strong><span>{item.kind.toUpperCase()} · {item.version||'unknown'}</span>
            <span>{statusLabel(item)}</span></button>)}
        </CardBody></Card>
        <Card><CardTitle>Review details</CardTitle><CardBody>
          {!selected?<p>Select an imported package.</p>:<>
            <p><strong>{selected.title||selected.packageId}</strong> · {selected.kind.toUpperCase()} {selected.version}</p>
            <p className="studio-mono" title={selected.sha256}>SHA-256: {selected.sha256.slice(0,16)}…</p>
            <details className="studio-identity-disclosure"><summary>Full package identity</summary>
              <p className="studio-mono">SHA-256: {selected.sha256}</p></details>
            <Label color={selected.canonicalValid?'green':'red'}>{selected.canonicalValid?'Canonical validator passed':'Canonical validation rejected / unavailable'}</Label>
            {' '}{selected.blueprint&&<Label color={selected.blueprint.present===selected.blueprint.required?'green':'orange'}>{selected.blueprint.present} / {selected.blueprint.required} blueprint resources</Label>}
            {' '}{<Label color={selected.storeReady?'green':'orange'}>{selected.storeReady?'Ready for manual review':'Review requirements incomplete'}</Label>}
            {selected.status==='review_approved'&&<div className="studio-local-approval" role="status">
              <div><Label color="blue">Locally approved</Label> <strong>Official-store publication has not been verified.</strong></div>
              {selected.issues.some(f=>f.code==='ASSET_DEPENDENCIES_EXTERNAL')&&
                <p>External asset dependencies still require installed-pack compatibility verification before claiming release readiness. A local review approval does not prove those dependencies work in Tavi.</p>}
              <Button size="sm" variant="link" onClick={()=>setSection('publishing')}>View publishing status</Button>
            </div>}
            <details className="studio-findings-disclosure" open={!selected.canonicalValid}>
              <summary>Findings ({selected.issues.length}){selected.issues.length>0&&` · ${selected.issues[0].code}`}</summary>
              {selected.issues.length===0?<p>No machine-detected findings. Manual visual review remains required.</p>:
                <ul>{selected.issues.map((finding,i)=><li key={i}><strong>{finding.severity} · {finding.code}</strong>: {finding.message}</li>)}</ul>}
            </details>
            {selected.blueprint&&<details className="studio-findings-disclosure"><summary>Designer checklist ({selected.blueprint.designerChecklist.length})</summary>
              <ul>{selected.blueprint.designerChecklist.map((item,i)=><li key={i}>{item}</li>)}</ul></details>}
            {selected.kind==='tavia'&&<div className="studio-blueprint-summary">
              <div><strong>Blueprint:</strong> {selected.blueprint?.title||'Custom / not assigned'}
                {!selected.blueprint&&<span className="studio-muted"> · Not yet store-ready</span>}
              </div>
              <Button variant="secondary" size="sm" onClick={()=>{setPreferredBlueprintId('');setImportSetup(selected);}} isDisabled={busy}>
                {selected.blueprint?'Change blueprint…':'Choose blueprint…'}
              </Button>
            </div>}
            <details className="studio-browser-disclosure"><summary>Inspect package files, objects and artwork</summary>
              <PackBrowser key={selected.sha256} id={selected.sha256}/>
            </details>
            <label htmlFor="reviewer-note"><strong>Reviewer feedback for developer</strong></label>
            <textarea className="studio-note-input" id="reviewer-note" value={note} maxLength={2000} onChange={e=>setNote(e.target.value)} placeholder="Specific art, gameplay, package or accessibility issues to correct..."/>
            <div className="studio-actions">
              <Button variant="danger" onClick={()=>decision('changes_requested')} isDisabled={busy||!note.trim()}>Request changes</Button>
              <Button onClick={()=>decision('review_approved')} isDisabled={busy||!isValidated(selected)}>Approve local review</Button>
              <Button variant="secondary" onClick={()=>exportBundle('feedback')} isDisabled={busy}>Export feedback ZIP</Button>
              <Button variant="secondary" onClick={()=>exportBundle('preview')} isDisabled={busy||!selected.canonicalValid}>Export developer preview</Button>
              <Button variant="secondary" onClick={()=>exportBundle('approval')} isDisabled={busy||selected.status!=='review_approved'}>Export approved handoff</Button>
            </div>
          </>}
        </CardBody></Card>
      </div>
    </>}
    {!loading&&section==='blueprints'&&<>
      {serviceErrors.blueprints&&<Alert variant="warning" title="Blueprint catalog unavailable" isInline>Check Events for {serviceErrors.blueprints}.</Alert>}
      <BlueprintLibrary blueprints={blueprints} busy={busy}
        onImportFromTavix={()=>void perform(async()=>{setTavibDiscovery(await invoke<TavibDiscovery>('review_discover_tavib'));},
          'Verified application scanned. Select blueprints to import.','tavib_discover')}
        onImport={()=>void perform(async()=>{await invoke('review_import_blueprint');},
          'Blueprint imported to this Studio profile. No asset, entitlement or store record was changed.','blueprint_import')}
        onUse={id=>{setPreferredBlueprintId(id);setSection('submissions');
          const candidate=reviews.find(r=>r.sha256===selectedId&&r.kind==='tavia')||reviews.find(r=>r.kind==='tavia');
          if(candidate){choose(candidate);setImportSetup(candidate);}
          else setNotice('Blueprint selected. Import a .tavia package to associate it with a review.');}}/>
    </>}
    {!loading&&section==='packages'&&<PackageSelector packages={snapshot?.packages||[]}/>}
    {!loading&&section==='assets'&&<Card><CardTitle>Assets & objects</CardTitle><CardBody>
      <p>Use Submission review to import and validate a `.tavia` pack against a designer blueprint. Source and data-only requirements are reviewed separately from pricing and ownership.</p>
      <Button onClick={()=>setSection('submissions')}>Review asset packs</Button>
      {selected&&selected.kind==='tavia'&&<PackBrowser key={selected.sha256} id={selected.sha256}/>}
    </CardBody></Card>}
    {!loading&&section==='storefront'&&<Card><CardTitle>Official store publication queue</CardTitle><CardBody>
      <Alert variant="warning" isInline title="Remote publication not connected" />
      <p>Review approval is a local decision. The official store additionally requires exact-artifact publisher trust, reviewed catalog/Git changes, server-side asset entitlements and separately authorized publication. A developer preview is never automatically shown as an official listing.</p>
      {reviews.filter(r=>r.status==='review_approved').length===0?<p>No locally approved packages.</p>:<ul>{reviews.filter(r=>r.status==='review_approved').map(r=><li key={r.sha256}>{r.packageId} {r.version} · {r.kind} · approved locally; publication pending</li>)}</ul>}
      <Button onClick={()=>setSection('publishing')}>Open publishing settings & live releases</Button>
      <Button isDisabled>Publish to official store — integration pending</Button>
    </CardBody></Card>}
    {!loading&&section==='publishing'&&<PublishingSetup approved={reviews}/> }
    {!loading&&section==='connections'&&<>
      {serviceErrors.health&&<Alert variant="warning" title="Validator readiness probe unavailable" isInline>Check Events for {serviceErrors.health}. You can still choose an Assets folder.</Alert>}
      <Card><CardTitle>Local asset source connection</CardTitle><CardBody>
        <p>Choose the root folder of an existing <code>tavi-assets</code> source checkout. Studio saves this preference in your private Windows profile; no local path is included in diagnostic exports.</p>
        <p><strong>Connection source:</strong> {health?.source||'not available'}</p>
        <div className="studio-actions">
          <Button onClick={connectAssets} isDisabled={busy}>Connect Tavi Assets folder</Button>
          <Button variant="secondary" onClick={resetAssets} isDisabled={busy}>Use automatic source detection</Button>
          <Button variant="secondary" onClick={()=>void refresh()} isDisabled={busy}>Check readiness</Button>
        </div>
      </CardBody></Card>
      <Card><CardTitle>Local validation components</CardTitle><CardBody>
        <div className="studio-health-list">{(health?.checks||[]).filter(check=>check.id==='tavix-validator'||check.id==='tavia-validator').map(check=><div key={check.id} className="studio-health-row">
          <strong>{check.id==='tavix-validator'?'TaviX package validator':'Tavi Assets pack validator'}</strong>
          <Label color={check.status==='ready'?'green':check.status==='blocked'?'red':'orange'}>{check.status==='ready'?'Available':check.status}</Label>
          <span>{check.message}</span>
          {check.status!=='ready'&&check.nextStep&&<small>{check.nextStep}</small>}
        </div>)}</div>
        <details className="studio-local-diagnostics"><summary>Detailed local and gateway diagnostic codes</summary>
          <ul>{(health?.checks||[]).map(check=><li key={check.id}><code>{check.code}</code> · {check.message}</li>)}</ul>
        </details>
      </CardBody></Card>
      <div className="studio-connection-link"><div><strong>Remote services and release settings</strong>
        <p>GitHub login, live releases, destination reachability and LoopRD publication status live in Publishing. Local validator availability does not prove remote authorization.</p></div>
        <Button onClick={()=>setSection('publishing')}>Open Publishing</Button></div>
    </>}
    {!loading&&section==='operations'&&<Card><CardTitle>Trusted operator boundary</CardTitle><CardBody>
      <p>GitHub and LoopRD publishing operations remain behind the existing credential and exact-artifact approval paths. No tokens are exposed to the Studio frontend, and no package approval modifies Gold or Wallet entitlements.</p>
      <Alert variant="info" isInline title="Native remote publisher integration pending" />
      <Button variant="secondary" onClick={()=>setSection('connections')}>Inspect connection readiness</Button>
<Button onClick={()=>setSection('publishing')}>Open publishing workspace</Button>
    </CardBody></Card>}
    {!loading&&section==='events'&&<>
      <Card><CardTitle>Shareable Studio diagnostic report</CardTitle><CardBody>
        <p>Includes validator readiness, safe failure codes and truncated package digests. No credentials, full local paths, package contents or reviewer notes are collected. Check the content before sharing.</p>
        <div className="studio-actions"><Button onClick={()=>void copyDiagnostics()}>Copy diagnostic report</Button>
          <Button variant="secondary" onClick={()=>void refresh()}>Refresh diagnostics</Button></div>
        <label htmlFor="studio-diagnostic-report">Report (can also be selected and copied manually)</label>
        <textarea id="studio-diagnostic-report" className="studio-diagnostic-output" readOnly value={diagnosticReport} rows={15}/>
      </CardBody></Card>
      <Card><CardTitle>Recent Studio import diagnostics</CardTitle><CardBody>
        {(health?.recentAttempts||[]).length===0?<p>No recent package-review findings yet.</p>:
          <table className="studio-table"><thead><tr><th>When</th><th>Action</th><th>Code</th><th>Format</th></tr></thead><tbody>
          {(health?.recentAttempts||[]).slice(-20).reverse().map((item,i)=><tr key={i}><td>{item.at}</td><td>{item.operation}</td><td>{item.code}</td><td>{item.kind}</td></tr>)}
          </tbody></table>}
      </CardBody></Card>
      <Card><CardTitle>Legacy management event identifiers</CardTitle><CardBody>
        <p>Bounded legacy event IDs only; original event text is not exposed.</p>
        {events.length===0?<p>No events in the old journal.</p>:<table className="studio-table"><thead><tr><th>When</th><th>Level</th><th>Code</th><th>ID</th></tr></thead><tbody>
          {events.map((e,i)=><tr key={e.id+i}><td>{e.timestamp}</td><td>{e.level}</td><td>{e.code}</td><td>{e.id}</td></tr>)}
        </tbody></table>}
      </CardBody></Card>
    </>}
  </PageSection></Page>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
