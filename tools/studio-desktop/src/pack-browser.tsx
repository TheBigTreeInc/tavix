import React, {useEffect, useRef, useState} from 'react';
import {invoke} from '@tauri-apps/api/core';
import {Alert, Button, Card, CardBody, CardTitle, Label} from '@patternfly/react-core';
import {PackGrid, type CatalogRow} from './pack-grid';

type Counts = {files:number;resources:number;objects:number;collections:number;dependencies:number};
type Summary = {id:string;version:string;kind:string;type:string;counts:Counts;dependencies:CatalogRow[]};
type Page = {section:string;total:number;offset?:number;summary?:Summary;items:Array<CatalogRow|Summary>};
type Preview = {member:string;mime:string;dataUrl:string};
const sections = ['resources','objects','collections','files','dependencies'] as const;
const PAGE_SIZE = 12; // Match the native, bounded review_catalog page size.
const labels:Record<string,string> = {resources:'Resources',objects:'Objects',collections:'Collections',files:'Files',dependencies:'Dependencies'};
type Section = typeof sections[number];
const safeError = (error:unknown) => String(error).replace(/([A-Za-z]:\\[^\s]+|\/Users\/[^\s]+|\/home\/[^\s]+)/g,'[local path]').slice(0,180);

export function PackBrowser({id}:{id:string}) {
  const [tab,setTab] = useState<Section>('resources');
  const [view,setView] = useState<'grid'|'list'>('grid');
  const [page,setPage] = useState<Page|null>(null);
  const [overview,setOverview] = useState<Summary|null>(null);
  const [offset,setOffset] = useState(0);
  const [preview,setPreview] = useState<Preview|null>(null);
  const [error,setError] = useState('');
  const [loading,setLoading] = useState(false);
  const [previewLoading,setPreviewLoading] = useState(false);
  const previewToken = useRef(0);
  useEffect(()=>{previewToken.current+=1;setTab('resources');setView('grid');setOffset(0);setPreview(null);setPage(null);setOverview(null);},[id]);
  useEffect(()=>{
    if(!id)return;
    let alive=true;
    previewToken.current+=1;setPreviewLoading(false);
    setLoading(true);setError('');setPreview(null);
    Promise.all([invoke<Page>('review_catalog',{id,section:tab,offset}),invoke<Page>('review_catalog',{id,section:'summary',offset:0})])
      .then(([detail,summary])=>{if(alive){setPage(detail);setOverview(summary.items[0] as Summary);}})
      .catch(e=>{if(alive)setError(safeError(e));})
      .finally(()=>{if(alive)setLoading(false);});
    return ()=>{alive=false;};
  },[id,tab,offset]);
  const openPreview=async(member:string)=>{
    const token=++previewToken.current;
    setPreview(null);setError('');setPreviewLoading(true);
    try {const image=await invoke<Preview>('review_preview',{id,member});
      if(token===previewToken.current)setPreview(image);}
    catch(e){if(token===previewToken.current)setError(safeError(e));}
    finally {if(token===previewToken.current)setPreviewLoading(false);}
  };
  const clearPreview=()=>{previewToken.current+=1;setPreviewLoading(false);setPreview(null);};
  if(!id)return <p>Select an imported package to browse its contents.</p>;
  return <Card><CardTitle>Package contents — read-only</CardTitle><CardBody>
    <p>Browse the original, digest-verified archive. This inspector never runs extension code or grants approval.</p>
    {overview&&<>
      <strong>{overview.id} · {overview.version}</strong><p>Type: {overview.type||overview.kind}</p>
      <div className="studio-pack-counts">{Object.entries(overview.counts).map(([name,value])=><span key={name}><strong>{value}</strong> {name}</span>)}</div>
    </>}
    <div className="studio-actions" role="group" aria-label="Package content categories">
      {sections.map(s=><Button key={s} size="sm" variant={tab===s?'primary':'secondary'} aria-label={labels[s]} onClick={()=>{setTab(s);setOffset(0);}}>{labels[s]}</Button>)}
    </div>
    {error&&<Alert variant="warning" title="Cannot inspect this resource" isInline>{error}</Alert>}
    <div className="studio-pack-inspector">
      <div className="studio-pack-results">
        {loading?<p>Reading original archive…</p>:<>
          <div className="studio-pack-page-header"><strong>{page?.total??0} {tab}</strong>
            <span>Showing {(page?.items?.length??0)?offset+1:0}–{offset+(page?.items?.length??0)}</span>
            <div className="studio-pack-view-toggle" role="group" aria-label="Package view">
              <Button size="sm" variant={view==='grid'?'primary':'secondary'} aria-pressed={view==='grid'} onClick={()=>setView('grid')}>Grid</Button>
              <Button size="sm" variant={view==='list'?'primary':'secondary'} aria-pressed={view==='list'} onClick={()=>setView('list')}>List</Button>
            </div></div>
          {view==='grid'?<PackGrid id={id} items={(page?.items||[]) as CatalogRow[]} onPreview={member=>void openPreview(member)}/>:<div className="studio-pack-list">
            {page?.items.map((raw,index)=>{
              const item=raw as CatalogRow;
              const member=item.path||'';
              const canPreview=/\.(svg|png|jpg|jpeg|webp)$/i.test(member);
              return <div className="studio-pack-row" key={(item.id||item.packId||'row')+index}>
                <div><strong>{item.name||item.id||item.packId||member||'Unnamed record'}</strong>
                  <div className="studio-mono">{member||item.kind||''}</div>
                  {item.kind&&<Label>{item.kind}</Label>}
                  {item.size!==undefined&&<small> {item.size} bytes</small>}
                  {item.entries!==undefined&&<small> {item.entries} entries</small>}
                  {item.resources&&<small> Resources: {item.resources.join(', ')}</small>}
                </div>
                {canPreview&&<Button size="sm" variant="link" aria-label={'View artwork for '+(item.name||item.id||member)} onClick={()=>void openPreview(member)}>View artwork</Button>}
              </div>;
            })}
            {page?.items.length===0&&<p>No records in this category.</p>}
          </div>}
          <div className="studio-actions studio-pack-pager">
            <Button variant="secondary" size="sm" isDisabled={offset===0} onClick={()=>setOffset(Math.max(0,offset-PAGE_SIZE))}>Previous</Button>
            <span>Page {Math.floor(offset/PAGE_SIZE)+1} of {Math.max(1,Math.ceil((page?.total||0)/PAGE_SIZE))}</span>
            <Button variant="secondary" size="sm" isDisabled={!page||offset+PAGE_SIZE>=page.total} onClick={()=>setOffset(offset+PAGE_SIZE)}>Next</Button>
          </div>
        </>}
      </div>
      <aside className="studio-pack-preview" aria-label="Artwork inspector" aria-live="polite">
        {previewLoading?<p>Verifying original artwork…</p>:preview?<>
          <strong>Artwork preview</strong>
          <span className="studio-mono">{preview.member}</span>
          <img src={preview.dataUrl} alt={'Preview of '+preview.member} />
          <p>Digest-verified image only. Not a live game preview or store approval.</p>
          <Button variant="secondary" size="sm" onClick={clearPreview}>Close preview</Button>
        </>:<p>Select <strong>View artwork</strong> on a resource to inspect its original image here.</p>}
      </aside>
    </div>
  </CardBody></Card>;
}
