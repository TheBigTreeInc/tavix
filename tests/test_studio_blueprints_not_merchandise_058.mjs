import test from 'node:test';
import assert from 'node:assert/strict';
import {publicationRows} from '../tools/studio-desktop/src/catalog-rows.mjs';
const good={sha256:'f'.repeat(64),kind:'tavia',packageId:'org.tavi.cards',version:'1.0.0',title:'Cards',status:'review_approved',canonicalValid:true,storeReady:true};

test('blueprints never become merchandise rows even when mixed with valid pack data',()=>{
 const fakeBlueprint={id:'redlink-icons',version:'1.0.0',title:'Network icons',kind:'tavib'};
 const rows=publicationRows([good,fakeBlueprint],[],[],false);
 assert.equal(rows.length,1);
 assert.equal(rows[0].kind,'tavia');
 assert.equal(rows.some(row=>row.kind==='tavib'||row.key?.startsWith('blueprint:')),false);
});
test('application submissions and remote asset packs remain visible',()=>{
 const app={...good,sha256:'a'.repeat(64),kind:'tavix',packageId:'org.tavi.game'};
 const rows=publicationRows([good,app],[{packId:'org.tavi.other',version:'2.0.0',status:'published'}],[],true);
 assert.equal(rows.length,3);
 assert.equal(rows.filter(x=>x.kind==='tavix').length,1);
 assert.equal(rows.filter(x=>x.kind==='tavia').length,2);
 assert.equal(rows.find(x=>x.id==='org.tavi.other').editable,false);
});
