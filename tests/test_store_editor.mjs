import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {webcrypto} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../examples/store-editor/ui');
const source=fs.readFileSync(path.join(root,'zip.js'),'utf8');
function load(crypto=webcrypto){
  const w={crypto,Blob,File,ReadableStream,DecompressionStream,Response,TextDecoder,TextEncoder,Uint8Array,DataView};
  const env={window:w,Blob,File,ReadableStream,DecompressionStream,Response,TextDecoder,TextEncoder,Uint8Array,DataView,BigInt,Map,Array,Object};
  vm.runInNewContext(source,env,{filename:'zip.js'});
  return w.TaviXZip;
}
const te=new TextEncoder();
const u=s=>te.encode(s);
const manifest={schema:'tavi.extension/v1',id:'example.org.test-editor',version:'0.1.0',name:'Test',summary:'Offline sample',publisher:'example-org',kind:'app',hostApi:{min:'1.0.0',maxExclusive:'2.0.0'},entrypoints:{panel:'ui/index.html'},contributions:[],permissions:['ui.panel'],platforms:['windows','android']};

test('SHA-256 fallback matches known test vector',async()=>{
  const z=load(null);
  assert.equal(await z.sha(u('abc')),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  assert.equal(await z.sha(u('')),'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
});

test('Store editor ZIP export regenerates a verifiable lock and preserves file identity',async()=>{
  const z=load(),files=new Map([['ui/index.html',u('<h1>Tavi</h1>')]]);
  const renamed={...manifest,version:'0.1.1',name:'Updated card game'};
  const locked=await z.relock(files,renamed);
  assert.equal((await z.check(locked)).name,'Updated card game');
  const output=z.build(locked);
  const unpacked=await z.open(new File([output],'test.tavix'));
  assert.equal((await z.check(unpacked)).version,'0.1.1');
  assert.equal(z.txt(unpacked,'ui/index.html'),'<h1>Tavi</h1>');
  const tampered=new Map(unpacked);
  tampered.set('ui/index.html',u('changed'));
  await assert.rejects(z.check(tampered),/integrity check/);
});

test('Rejects traversal, disallowed file extensions, and ZIP size violations',()=>{
  const z=load();
  assert.equal(z.safePath('../secret.json'),false);
  assert.equal(z.safePath('/etc/passwd'),false);
  assert.equal(z.safePath('ui/index.html'),true);
  assert.throws(()=>z.build(new Map([['../secrets.json',u('bad')]])),/Unsafe archive path/);
  assert.throws(()=>z.build(new Map([['ui/test.exe',u('bad')]])),/Unsupported extension/);
  assert.throws(()=>z.build(new Map([['ui/large.png',new Uint8Array(1000001)]])),/exceeds the TaviX/);
});
