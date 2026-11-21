import React,{useEffect,useRef,useState} from 'react';
import {invoke} from '@tauri-apps/api/core';
import {Alert,Button,Label} from '@patternfly/react-core';

export type TavibCandidate={member:string;id:string;version:string;title:string;sha256:string;minResources:number};
export type TavibDiscovery={schema:string;digest:string;appId:string;appVersion:string;candidates:TavibCandidate[]};
type TavibDetail={schema:string;member:string;appId:string;appVersion:string;sha256:string;
 title:string;description:string;version:string;applicablePackTypes:string[];requiredResources:string[];
 requiredPrefixes:Record<string,number>;optionalResources:string[];designerChecklist:string[];
 readme:string;previewBase64:string|null;localOnly:boolean;publicationAuthorized:boolean};

export function TavibImportDialog({discovery,busy,onCancel,onImport}:{
 discovery:TavibDiscovery|null;busy:boolean;onCancel:()=>void;onImport:(members:string[])=>void;
}){
 const ref=useRef<HTMLDialogElement>(null);
 const [chosen,setChosen]=useState<string[]>([]);
 const [inspecting,setInspecting]=useState('');
 const [detail,setDetail]=useState<TavibDetail|null>(null);
 const [detailError,setDetailError]=useState('');
 const [loading,setLoading]=useState(false);
 useEffect(()=>{const node=ref.current;
   if(discovery){setChosen([]);setDetail(null);setInspecting('');setDetailError('');if(node&&!node.open)node.showModal();}
   else if(node?.open)node.close();},[discovery]);
 useEffect(()=>{
   if(!discovery||!inspecting){setDetail(null);return;}
   let active=true;setLoading(true);setDetail(null);setDetailError('');
   void invoke<TavibDetail>('review_tavib_detail',{digest:discovery.digest,member:inspecting})
     .then(data=>{if(active && data.member===inspecting && data.appId===discovery.appId && data.schema==='tavix.studio.tavib-inspection/v1')setDetail(data);
       else if(active)setDetailError('Blueprint detail identity does not match the verified application.');})
     .catch(()=>{if(active)setDetailError('Unable to inspect this embedded blueprint; import is unavailable until rechecked.');})
     .finally(()=>{if(active)setLoading(false);});
   return()=>{active=false;};
 },[discovery,inspecting]);
 const flip=(name:string,checked:boolean)=>setChosen(previous=>checked?[...previous,name]:previous.filter(x=>x!==name));
 return <dialog ref={ref} className="studio-import-dialog" aria-labelledby="tavib-import-heading" onClose={onCancel}
   onCancel={e=>{if(busy)e.preventDefault();}}>
   {discovery&&<div className="studio-import-panel">
     <div className="studio-dialog-heading"><div><h2 id="tavib-import-heading">Inspect blueprints from TaviX</h2>
       <p className="studio-muted">Verified application: {discovery.appId} v{discovery.appVersion} · {discovery.digest.slice(0,12)}…</p></div>
       <Button variant="plain" aria-label="Close blueprint import" onClick={onCancel} isDisabled={busy}>✕</Button></div>
     <Alert variant="info" title="Inspect before importing" isInline>Inspect each blueprint’s purpose, required and optional resources, checklist and preview. Reading never installs or runs the app or grants publication rights.</Alert>
     {discovery.candidates.length===0?<p>No embedded <code>schematics/*.tavib</code> found in this verified app.</p>:
       <div className="studio-tavib-candidates">{discovery.candidates.map(c=><div key={c.member} className={'studio-tavib-candidate '+(inspecting===c.member?'studio-tavib-candidate-selected':'')}>
         <input type="checkbox" aria-label={`Select ${c.title} for import`} checked={chosen.includes(c.member)} onChange={e=>flip(c.member,e.target.checked)} />
         <span><strong>{c.title}</strong><small>{c.id} · v{c.version} · minimum {c.minResources} resources · {c.sha256.slice(0,12)}…</small></span>
         <Button variant="link" size="sm" onClick={()=>setInspecting(c.member)} isDisabled={busy}>Inspect</Button>
       </div>)}</div>}
     {inspecting&&<section className="studio-tavib-details" aria-label="Embedded blueprint details" aria-live="polite">
       {loading?<p>Checking blueprint details against the retained application…</p>:
       detailError?<Alert variant="warning" title={detailError} isInline/>:detail?<>
         <h3>{detail.title}</h3><p>{detail.description}</p>
         <div className="studio-actions"><Label color="purple">App-provided</Label><span>v{detail.version}</span><span>Types: {detail.applicablePackTypes.join(', ')}</span></div>
         {detail.previewBase64&&<img className="studio-tavib-preview" alt={`Optional artwork preview for ${detail.title}`} src={'data:image/webp;base64,'+detail.previewBase64}/>}
         <div className="studio-tavib-lists"><div><strong>Required resource names</strong>
           {detail.requiredResources.length?<ul>{detail.requiredResources.map(n=><li key={n}><code>{n}</code></li>)}</ul>:<p>None individually required.</p>}
           <strong>Minimum compatible resources</strong>
           {Object.keys(detail.requiredPrefixes).length?<ul>{Object.entries(detail.requiredPrefixes).map(([prefix,min])=><li key={prefix}><code>{prefix}*</code> · at least {min}</li>)}</ul>:<p>No prefix minimum.</p>}
         </div><div><strong>Optional resources</strong>
           {detail.optionalResources.length?<ul>{detail.optionalResources.map(n=><li key={n}><code>{n}</code></li>)}</ul>:<p>None declared.</p>}
           <strong>Designer checklist</strong><ul>{detail.designerChecklist.map((item,i)=><li key={i}>{item}</li>)}</ul></div></div>
         {detail.readme&&<details><summary>Embedded author notes</summary><pre>{detail.readme}</pre></details>}
         <p className="studio-muted">Source: {detail.appId} v{detail.appVersion} · embedded member <code>{detail.member}</code> · SHA-256 {detail.sha256}. Local review only; publisher trust unverified.</p>
       </>:<p>Select Inspect on a blueprint to review its requirements before import.</p>}
     </section>}
     <div className="studio-dialog-actions"><Button isDisabled={busy||chosen.length===0||loading} onClick={()=>onImport(chosen)}>
       Import {chosen.length} selected blueprint{chosen.length===1?'':'s'}</Button>
       <Button variant="secondary" onClick={onCancel} isDisabled={busy}>Cancel</Button></div>
   </div>}
 </dialog>;
}
