import React,{useEffect,useRef,useState} from 'react';
import {Button,Label} from '@patternfly/react-core';
import type {Blueprint} from './blueprint-library';

type Imported = {sha256:string;kind:'tavia'|'tavix';packageId:string;title:string;version:string;
  canonicalValid:boolean;status:string;storeReady:boolean;
  blueprint:{id:string;title:string}|null};

/** A native browser dialog, driven only by a retained review ID. The trusted
 * Rust picker selects and inspects the actual archive before this is shown. */
export function ImportSetupDialog({item,blueprints,suggestedChoice,busy,onClose,onConfirm}:{
  item:Imported|null;blueprints:Blueprint[];suggestedChoice:string;busy:boolean;
  onClose:()=>void;onConfirm:(blueprintId:string)=>void;
}){
  const ref=useRef<HTMLDialogElement>(null);
  const [choice,setChoice]=useState('');
  useEffect(()=>{
    const node=ref.current;
    if(item){setChoice(suggestedChoice||item.blueprint?.id||'');if(node&&!node.open)node.showModal();}
    else if(node?.open)node.close();
  },[item,suggestedChoice]);
  const chosen=blueprints.find(b=>b.id===choice);
  return <dialog ref={ref} className="studio-import-dialog" aria-labelledby="studio-import-heading"
    onCancel={event=>{if(busy)event.preventDefault();}}
    onClose={onClose}>
    {item&&<div className="studio-import-panel">
      <div className="studio-dialog-heading">
        <div><h2 id="studio-import-heading">{item.kind==='tavia'?'Set up asset review':'Submission imported'}</h2>
          <p className="studio-muted">The original package has been retained locally. Nothing was installed or published.</p></div>
        <Button variant="plain" aria-label="Close import setup" onClick={onClose} isDisabled={busy}>✕</Button>
      </div>
      <div className="studio-import-identity">
        <strong>{item.title||item.packageId||'Imported package'}</strong>
        <span>{item.kind.toUpperCase()} · {item.version}</span>
        <Label color={item.canonicalValid?'green':'red'}>
          {item.canonicalValid?'Canonical validation passed':'Canonical validation incomplete'}</Label>
      </div>
      {item.kind==='tavia'?<>
        <label htmlFor="import-blueprint-choice"><strong>Blueprint for review</strong></label>
        <select id="import-blueprint-choice" className="studio-select" value={choice} onChange={e=>setChoice(e.target.value)}>
          <option value="">Custom / no blueprint yet</option>
          {blueprints.map(b=><option key={b.id} value={b.id}>
            {b.title} · {b.origin==='operator'?'Imported locally':'Built in'}
          </option>)}
        </select>
        {chosen?<div className="studio-blueprint-help">
          <strong>{chosen.title}</strong> · {chosen.requiredCount} required resource positions
          <p>{chosen.description}</p>
          {chosen.id==='tarot-standard-78'&&<p className="studio-muted">The generic Tarot profile requires <code>tarot.major.*</code> and <code>tarot.minor.*</code> identifiers. A deck using <code>tarot.card.*</code> must not be mapped automatically; use a reviewed compatible blueprint instead.</p>}
          <p className="studio-muted">A blueprint check may report missing or incompatible resource IDs. It cannot authorize a store listing.</p>
        </div>:<div className="studio-blueprint-help">
          <strong>Custom / unmapped</strong>
          <p>This pack stays in the review queue without a blueprint. You can inspect the artwork and attach a blueprint later. It is not store-ready.</p>
        </div>}
        {item.blueprint?.id && item.blueprint.id!==choice&&<p className="studio-muted">Changing or clearing a previously checked blueprint resets the old local review decision.</p>}
      </>:<p>This app can be reviewed directly. Asset blueprints apply only to `.tavia` packs.</p>}
      <div className="studio-dialog-actions">
        <Button onClick={()=>onConfirm(item.kind==='tavia'?choice:'')} isDisabled={busy}>
          {busy?'Checking…':item.kind!=='tavia'?'Open review':choice?'Check blueprint & open review':'Keep custom & open review'}
        </Button>
        <Button variant="secondary" onClick={onClose} isDisabled={busy}>Review later</Button>
      </div>
    </div>}
  </dialog>;
}
