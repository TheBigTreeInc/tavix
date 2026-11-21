import React, {useEffect, useState} from 'react';
import {invoke} from '@tauri-apps/api/core';
import {Label} from '@patternfly/react-core';

export type CatalogRow = {
  id?:string; name?:string; path?:string; kind?:string; size?:number;
  variants?:number; entries?:number; resources?:string[]; packId?:string; optional?:boolean;
};
type Preview = {member:string; mime:string; dataUrl:string};
type Thumb = {url:string|null};
const MAX_VISIBLE = 12;
const MAX_CONCURRENT = 3;
const safeImage = (path:string):boolean => /\.(svg|png|jpe?g|webp)$/i.test(path);
const safeDataUrl = (value:string):boolean => /^data:image\/(svg\+xml|png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(value);

// The native command verifies SHA-bound original media. Never read files via URL or embed a package WebView.
export function PackGrid({id,items,onPreview}:{id:string;items:CatalogRow[];onPreview:(member:string)=>void}) {
  const [thumbs,setThumbs] = useState<Record<string,Thumb>>({});
  useEffect(()=>{
    let alive=true;
    setThumbs({});
    const members=[...new Set(items.slice(0,MAX_VISIBLE).map(item=>item.path||'').filter(safeImage))];
    let next=0;
    const load=async()=>{
      while(alive && next<members.length){
        const member=members[next++];
        let url:string|null=null;
        try {
          const image=await invoke<Preview>('review_preview',{id,member});
          if(image.member===member && safeDataUrl(image.dataUrl)) url=image.dataUrl;
        } catch { /* Invalid or unavailable media remain text-only; review is unchanged. */ }
        if(alive) setThumbs(previous=>({...previous,[member]:{url}}));
      }
    };
    for(let worker=0;worker<Math.min(MAX_CONCURRENT,members.length);worker++) void load();
    return ()=>{alive=false;};
  },[id,items]);

  if(!items.length)return <p>No records in this category.</p>;
  return <div className="studio-pack-grid" aria-label="Package items grid">
    {items.map((item,index)=>{
      const member=item.path||'';
      const previewable=safeImage(member);
      const image=thumbs[member];
      const title=item.name||item.id||item.packId||member||'Unnamed record';
      const details=<>
        <div className="studio-pack-tile-media" aria-hidden="true">
          {previewable && image?.url
            ? <img src={image.url} alt="" loading="lazy" />
            : <span>{previewable && !image?'Loading artwork…':previewable?'Artwork unavailable':item.kind||'No artwork'}</span>}
        </div>
        <div className="studio-pack-tile-body">
          <strong title={title}>{title}</strong>
          {item.id && item.name && item.id!==item.name && <span className="studio-mono">{item.id}</span>}
          {member && <span className="studio-mono">{member}</span>}
          {item.kind && <Label>{item.kind}</Label>}
          {item.entries!==undefined && <small>{item.entries} entries</small>}
          {item.resources && <small>{item.resources.length} linked resources</small>}
          {item.size!==undefined && <small>{item.size} bytes</small>}
        </div>
      </>;
      return previewable
        ? <button type="button" className="studio-pack-tile studio-pack-tile-action" key={(item.id||member)+index}
            onClick={()=>onPreview(member)} aria-label={'Inspect artwork for '+title}>{details}</button>
        : <div className="studio-pack-tile" key={(item.id||item.packId||member)+index}>{details}</div>;
    })}
  </div>;
}
