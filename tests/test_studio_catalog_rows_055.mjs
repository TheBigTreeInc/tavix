import test from 'node:test';
import assert from 'node:assert/strict';
import {publicationRows,cleanDraft,draftEquals} from '../tools/studio-desktop/src/catalog-rows.mjs';
const review={sha256:'a'.repeat(64),kind:'tavia',packageId:'org.tavi.cards',version:'1.2.3',title:'Cards',status:'review_approved',canonicalValid:true,storeReady:true};
test('one row per sellable package and remote-only asset; blueprints stay out',()=>{
 const rows=publicationRows([review],
  [{packId:'org.tavi.cards',version:'1.2.3',status:'published'},{packId:'org.tavi.other',version:'1.0.0',status:'published'}], [],true);
 assert.equal(rows.length,2);
 const cards=rows.find(row=>row.id==='org.tavi.cards');
 assert.equal(cards.live,'published');assert.equal(cards.type,'TAVIA · asset pack');assert.equal(cards.eligible,true);
 assert.equal(rows.some(row=>row.kind==='tavib'),false);
 assert.equal(rows.find(row=>row.id==='org.tavi.other').editable,false);
});
test('unverified remote state does not pretend listing or pricing is live',()=>{
 const rows=publicationRows([review],[],[],false);
 assert.equal(rows[0].live,'Not checked');
 assert.equal(rows[0].eligible,true);
});
test('TAVIX source stays separate from the LoopRD assets catalog',()=>{
 const app={...review,sha256:'b'.repeat(64),kind:'tavix',packageId:'org.tavi.game'};
 const rows=publicationRows([app],[{packId:'org.tavi.game',version:'1.2.3'}],[],true);
 assert.equal(rows.find(r=>r.kind==='tavix').live,'GitHub separate');
 assert.equal(rows.length,2);
});
test('draft fields include zero/free and distinguish unsupplied prices',()=>{
 assert.equal(cleanDraft({priceGold:0,listed:true,testing:true,summary:'Test'}).priceGold,0);
 assert.equal(cleanDraft({priceGold:null}).priceGold,null);
 assert.equal(cleanDraft({priceGold:-1}).priceGold,null);
 assert.equal(cleanDraft({priceGold:1_000_001}).priceGold,null);
 assert.equal(draftEquals({priceGold:0},{priceGold:null}),false);
});
test('malformed local IDs are not admitted into the catalog model',()=>{
 const result=publicationRows([{...review,sha256:'../invalid'}],[],[],false);
 assert.equal(result.length,0);
});
