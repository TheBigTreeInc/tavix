import React,{useEffect,useMemo,useState} from 'react';
import {invoke} from '@tauri-apps/api/core';
import {Alert,Button,Label} from '@patternfly/react-core';
import {cleanDraft,draftEquals,publicationRows,type PublicationDraft} from './catalog-rows.mjs';

type Review={sha256:string;kind:'tavix'|'tavia';packageId:string;version:string;title?:string;status:string;canonicalValid:boolean;storeReady:boolean};
type Pack={packId:string;version:string;status?:string};
type DraftEnvelope={schema:string;entries:Record<string,PublicationDraft>};
type DraftReply={rowKey:string;draft:PublicationDraft;remoteApplied:boolean};
const empty:PublicationDraft={priceGold:null,listed:false,testing:false,summary:''};

/** Each edit is an operator-local draft, never a LoopRD price/listing mutation. */
export function CatalogManager({submissions=[],published=[],inspected=[],registryChecked=false}:{
 submissions?:Review[];published?:Pack[];inspected?:Pack[];registryChecked?:boolean;
}) {
 const [stored,setStored]=useState<Record<string,PublicationDraft>>({});
 const [editing,setEditing]=useState<Record<string,PublicationDraft>>({});
 const [filter,setFilter]=useState('');
 const [kind,setKind]=useState('all');
 const [busy,setBusy]=useState('');
 const [error,setError]=useState('');
 const [notice,setNotice]=useState('');
 const [loadState,setLoadState]=useState<'loading'|'ready'|'failed'>('loading');
 const rows=useMemo(()=>publicationRows(submissions,published,inspected,registryChecked),[
    submissions,published,inspected,registryChecked]);
 useEffect(()=>{
   let active=true;
   void invoke<DraftEnvelope>('studio_catalog_drafts').then(v=>{
     if(!active)return;
     if(v.schema!=='tavix.studio.catalog-drafts/v1')throw new Error('Unsupported catalog draft schema');
     const saved=Object.fromEntries(Object.entries(v.entries||{}).map(([k,val])=>[k,cleanDraft(val)]));
     setStored(saved);setEditing(saved);setLoadState('ready');
   }).catch(()=>{if(active){setLoadState('failed');setError('Local publication drafts could not be loaded. No edits will be saved until this is repaired.');}});
   return ()=>{active=false;};
 },[]);
 const visible=rows.filter(row=>(kind==='all'||row.kind===kind)&&(
   `${row.name} ${row.id} ${row.type} ${row.version}`.toLowerCase().includes(filter.trim().toLowerCase())));
 const edit=(key:string,patch:Partial<PublicationDraft>)=>{
   setEditing(previous=>({...previous,[key]:{...empty,...(previous[key]||stored[key]),...patch}}));
   setNotice('');
 };
 const save=async(key:string)=>{
   if(loadState!=='ready'||busy)return;
   const draft=cleanDraft(editing[key]||stored[key]||empty);
   setBusy(key);setError('');setNotice('');
   try{
     const result=await invoke<DraftReply>('studio_catalog_save_draft',{
       rowKey:key,priceGold:draft.priceGold,listed:draft.listed,testing:draft.testing,summary:draft.summary});
     if(result.rowKey!==key||result.remoteApplied!==false)throw new Error('Invalid native draft response');
     setStored(previous=>({...previous,[key]:cleanDraft(result.draft)}));
     setEditing(previous=>({...previous,[key]:cleanDraft(result.draft)}));
     setNotice('Catalog metadata draft saved privately on this device. No price, testing flag or listing was changed remotely.');
   }catch{setError('Unable to save the local catalog draft. Check the item exists in Studio and view the operator diagnostics.');}
   finally{setBusy('');}
 };
 return <section className="studio-catalog-manager" aria-label="Publishing catalog management">
   <div className="studio-catalog-heading">
     <div><h2>Catalog &amp; release metadata</h2>
       <p className="studio-muted">Manage local publication drafts for applications and asset packs. Blueprints are compatibility definitions in Asset blueprints, not store items. Live LoopRD status is read-only. <strong>Gold prices and listing/testing flags are not supported by the current remote registry API.</strong></p></div>
     <Label color="blue">Local drafts · not published</Label>
   </div>
   {error&&<Alert variant="danger" title={error} isInline/>}
   {notice&&<Alert variant="success" title={notice} isInline/>}
   <div className="studio-catalog-toolbar">
     <label>Find an item<input type="search" value={filter} onChange={e=>setFilter(e.target.value)} placeholder="Search applications and asset packs…"/></label>
     <label>Type<select aria-label="Filter publication item type" value={kind} onChange={e=>setKind(e.target.value)}>
       <option value="all">All types</option><option value="tavix">Applications · TAVIX</option>
       <option value="tavia">Asset packs · TAVIA</option>
     </select></label>
     <span>{visible.length} of {rows.length} items · {registryChecked?'Live registry checked':'Live registry not loaded'}</span>
   </div>
   {loadState==='loading'&&<p>Loading local catalog drafts…</p>}
   <div className="studio-catalog-scroller" role="region" aria-label="Publication item table" tabIndex={0}>
     <table className="studio-catalog-table">
       <thead><tr><th scope="col">Item / ID</th><th scope="col">Type / version</th><th scope="col">Review / live</th>
         <th scope="col">Gold price</th><th scope="col">Listed</th><th scope="col">Testing</th>
         <th scope="col">Description / notes</th><th scope="col">Draft</th></tr></thead>
       <tbody>{visible.map(row=>{
         const data=editing[row.key]||stored[row.key]||empty;
         const changed=!draftEquals(data,stored[row.key]||empty);
         const readonly=!row.editable||loadState!=='ready';
         return <tr key={row.key}>
           <th scope="row"><div className="studio-catalog-name">{row.name}</div>
             <small title={row.id}>{row.id}</small><div className="studio-muted">{row.source}</div></th>
           <td><strong>{row.type}</strong><div className="studio-muted">v{row.version}</div></td>
           <td><span>{row.review}</span><div><Label color={row.live==='published'?'green':row.live==='ready'?'blue':'grey'}>{row.live}</Label></div></td>
           <td><input type="number" min={0} max={1000000} step={1} inputMode="numeric" className="studio-catalog-price"
             aria-label={`Draft Gold price for ${row.name}`} placeholder="—" disabled={readonly||Boolean(busy)}
             value={data.priceGold??''} onChange={e=>{
               const value=e.target.value;
               if(value===''){edit(row.key,{priceGold:null});return;}
               if(/^\d{1,7}$/.test(value)&&Number(value)<=1000000){edit(row.key,{priceGold:Number(value)});return;}
               setError('Gold prices must be whole numbers between 0 and 1,000,000.');
             }}/>
             <small>0 = free</small></td>
           <td><input type="checkbox" aria-label={`Propose listed for ${row.name}`} checked={data.listed}
             disabled={readonly||Boolean(busy)} onChange={e=>edit(row.key,{listed:e.target.checked})}/></td>
           <td><input type="checkbox" aria-label={`Propose testing for ${row.name}`} checked={data.testing}
             disabled={readonly||Boolean(busy)} onChange={e=>edit(row.key,{testing:e.target.checked})}/></td>
           <td><input type="text" maxLength={240} aria-label={`Draft description for ${row.name}`} placeholder="Optional store description"
             value={data.summary} disabled={readonly||Boolean(busy)} onChange={e=>edit(row.key,{summary:e.target.value})}/></td>
           <td>{row.editable?<><Button size="sm" variant="secondary" isDisabled={readonly||Boolean(busy)||!changed}
               onClick={()=>void save(row.key)}>Save draft</Button><div className="studio-muted">{changed?'Unsaved':stored[row.key]?'Saved locally':'Not configured'}</div></>:
               <span className="studio-muted">Live · read only</span>}</td>
         </tr>;
       })}{visible.length===0&&<tr><td colSpan={8}>No items match. Import an application or asset pack, or load the live LoopRD catalog.</td></tr>}</tbody>
     </table>
   </div>
   <p className="studio-muted">These proposed values remain in the operator's private Studio profile. They do not change the official Tavi Store, GitHub releases, authoritative Gold pricing or LoopRD entitlements. Remote price/listing/testing support needs an approved Tavi Assets/LoopRD contract.</p>
 </section>;
}
