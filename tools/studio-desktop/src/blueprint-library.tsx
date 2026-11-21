import React,{useMemo,useState} from 'react';
import {Alert,Button,Card,CardBody,CardTitle,Label,Title} from '@patternfly/react-core';

export type Blueprint = {
  id:string;title:string;version:string;description:string;applicablePackTypes:string[];
  requiredCount:number;requiredResources?:string[];requiredPrefixes?:Record<string,number>;
  designerChecklist:string[];origin?:'bundled'|'operator'|'app';digestPrefix?:string;sourceApp?:string;sourceAppVersion?:string;upstreamId?:string;
};

export function BlueprintLibrary({blueprints,busy,onImport,onImportFromTavix,onUse}:{
  blueprints:Blueprint[];busy:boolean;onImport:()=>void;onImportFromTavix:()=>void;onUse:(id:string)=>void;
}){
  const [search,setSearch]=useState('');
  const [filter,setFilter]=useState<'all'|'bundled'|'operator'|'app'>('all');
  const [chosen,setChosen]=useState('');
  const filtered=useMemo(()=>blueprints.filter(b=>{
    const terms=`${b.id} ${b.title} ${b.description} ${b.applicablePackTypes.join(' ')}`.toLowerCase();
    return (filter==='all'||(b.origin||'bundled')===filter)&&terms.includes(search.toLowerCase());
  }),[blueprints,search,filter]);
  const active=filtered.find(b=>b.id===chosen)||filtered[0];
  return <>
    <Alert variant="info" isInline title="Where blueprints come from">
      Built-in profiles ship with the TaviX Studio source in <code>tools/studio-desktop/blueprints/</code>.
      You can also import a reviewed <code>tavix.studio.asset-blueprint/v1</code> JSON file;
      it is retained privately in your local Studio profile under <code>blueprints/</code>.
      You can also import portable app-provided <code>.tavib</code> blueprints from a verified <code>.tavix</code> package. Import grants no publishing permission.
    </Alert>
    <div className="studio-actions"><Button onClick={onImportFromTavix} isDisabled={busy}>Import from TaviX…</Button><Button variant="secondary" onClick={onImport} isDisabled={busy}>Import blueprint JSON</Button>
      <span className="studio-muted">Custom IDs start with <code>local-</code>; each imported ID is immutable.</span>
    </div>
    <div className="studio-blueprint-layout">
      <div className="studio-blueprint-list">
        <label htmlFor="blueprint-search">Find a blueprint</label>
        <input id="blueprint-search" className="studio-publish-input" placeholder="Tarot, dice, card back…" value={search} onChange={e=>setSearch(e.target.value)}/>
        <label htmlFor="blueprint-source">Source</label>
        <select id="blueprint-source" className="studio-select" value={filter} onChange={e=>setFilter(e.target.value as typeof filter)}>
          <option value="all">All sources</option><option value="bundled">Bundled with Studio</option><option value="operator">Imported locally</option><option value="app">Embedded in TaviX app</option>
        </select>
        <p className="studio-muted">{filtered.length} matching blueprint(s)</p>
        {filtered.map(b=><button className={'studio-review-item '+(active?.id===b.id?'studio-review-item-active':'')} key={b.id} type="button" onClick={()=>setChosen(b.id)}>
          <strong>{b.title}</strong>
          <span>{b.id} · v{b.version}</span>
          <span>{b.origin==='app'?'From '+(b.sourceApp||'TaviX app'):b.origin==='operator'?'Imported locally':'Bundled with Studio'} · {b.requiredCount} required</span>
        </button>)}
      </div>
      <Card><CardTitle>{active?.title||'Choose a blueprint'}</CardTitle><CardBody>
        {active?<>
          <div className="studio-actions"><Label color={active.origin==='app'?'purple':active.origin==='operator'?'blue':'grey'}>{active.origin==='app'?'App-provided blueprint':active.origin==='operator'?'Operator import':'Studio bundled'}</Label>
            <span className="studio-muted">{active.id} · v{active.version}</span></div>
          <p>{active.description}</p>
          <p><strong>Applies to:</strong> {active.applicablePackTypes.join(', ')}</p>
          <p><strong>Required resource positions:</strong> {active.requiredCount}</p>
          <p className="studio-muted">{active.origin==='app'?
            `Provenance: verified local .tavix ${active.sourceApp||''} v${active.sourceAppVersion||''}, upstream ${active.upstreamId||''}, archive SHA prefix ${active.digestPrefix||''}. Locally imported only; not publisher-trusted.`:active.origin==='operator'?
            'Provenance: locally imported JSON in your private Studio profile. It is not part of the public catalog and will not be synced or installed on users’ devices.':
            'Provenance: embedded read-only TaviX Studio designer profile, versioned with the source checkout.'}</p>
          <details><summary>Exact resource requirements</summary>
            <ul>{(active.requiredResources||[]).map(v=><li key={v}><code>{v}</code></li>)}
              {Object.entries(active.requiredPrefixes||{}).map(([k,v])=><li key={k}><code>{k}*</code> — at least {v}</li>)}</ul>
          </details>
          <Title headingLevel="h3" size="md">Designer checklist</Title>
          <ul>{active.designerChecklist.map((v,i)=><li key={i}>{v}</li>)}</ul>
          <Button onClick={()=>onUse(active.id)}>Choose for submission review</Button>
        </>:<p>No blueprints match your filters. Import a reviewed JSON blueprint or clear the search.</p>}
      </CardBody></Card>
    </div>
    <p className="studio-muted">Blueprints check declared resource layout; canonical Tavi Assets validation and explicit review remain independent. Import never grants publishing rights.</p>
  </>;
}
