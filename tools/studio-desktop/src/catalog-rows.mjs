/** Commerce-only rows: .tavib blueprints are compatibility metadata, never merchandise. */
const kinds = Object.freeze({tavia:'TAVIA · asset pack',tavix:'TAVIX · application'});
const reviewText = Object.freeze({review_approved:'Locally approved',changes_requested:'Changes requested',draft:'Awaiting review'});
export function publicationRows(reviews=[],published=[],inspected=[],registryChecked=false) {
  const byKey = new Map();
  const status = new Map();
  // Inspect is richer than the published-only catalog, but both are live reads.
  for (const entry of published) {
    if (!entry || typeof entry.packId!=='string' || typeof entry.version!=='string')continue;
    status.set(`${entry.packId}@${entry.version}`,'published');
  }
  for (const entry of inspected) {
    if (!entry || typeof entry.packId!=='string' || typeof entry.version!=='string')continue;
    status.set(`${entry.packId}@${entry.version}`,entry.status);
  }
  for (const item of reviews) {
    if (!item || !/^[a-f0-9]{64}$/.test(item.sha256||'') || !kinds[item.kind]) continue;
    const live=item.kind==='tavia'?(status.get(`${item.packageId}@${item.version}`)|| (registryChecked?'Not returned':'Not checked')):'GitHub separate';
    byKey.set(`submission:${item.sha256}`,{
      key:`submission:${item.sha256}`,name:item.title||item.packageId,id:item.packageId,
      version:item.version,type:kinds[item.kind],kind:item.kind,source:'Local submission',
      review:reviewText[item.status]||'Unreviewed',live,editable:true,
      eligible:Boolean(item.canonicalValid && item.storeReady && item.status==='review_approved')
    });
  }
  for (const [identity,live] of status) {
    const lastAt=identity.lastIndexOf('@');
    const id=identity.slice(0,lastAt),version=identity.slice(lastAt+1);
    const duplicate=[...byKey.values()].some(row=>row.kind==='tavia'&&row.id===id&&row.version===version);
    if(duplicate)continue;
    const key=`remote:${identity}`;
    byKey.set(key,{key,name:id,id,version,type:'TAVIA · asset pack',kind:'tavia',source:'LoopRD registry',
      review:'Not imported locally',live,editable:false,eligible:false});
  }
  return [...byKey.values()].sort((a,b)=>a.name.localeCompare(b.name)||a.version.localeCompare(b.version));
}
export function cleanDraft(draft) {
  return {
    priceGold:Number.isInteger(draft?.priceGold)&&draft.priceGold>=0&&draft.priceGold<=1000000?draft.priceGold:null,
    listed:draft?.listed===true,
    testing:draft?.testing===true,
    summary:typeof draft?.summary==='string'?draft.summary.slice(0,240):''
  };
}
export function draftEquals(a,b) {
  return JSON.stringify(cleanDraft(a))===JSON.stringify(cleanDraft(b));
}
