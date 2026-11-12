/* Offline, bounded TaviX ZIP reader/writer. No remote services or third-party code. */
(function (global) {
  'use strict';
  const encoder = new TextEncoder();
  const decoder = new TextDecoder('utf-8', {fatal: true});
  const MAX_ARCHIVE = 25 * 1024 * 1024;
  const MAX_FILES = 300;
  const MAX_TOTAL = 32 * 1024 * 1024;
  const MAX_FILE = 1_000_000;
  const SAFE = /^[A-Za-z0-9_.\-/]+$/;
  const VERSION = /^\d+\.\d+\.\d+$/;
  const crcTable = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let i = 0; i < 8; i++) c = c & 1 ? (c >>> 1) ^ 0xedb88320 : c >>> 1;
    crcTable[n] = c >>> 0;
  }
  function crc32(bytes) {
    let value = 0xffffffff;
    for (const byte of bytes) value = (value >>> 8) ^ crcTable[(value ^ byte) & 255];
    return (value ^ 0xffffffff) >>> 0;
  }
  function safePath(path) {
    return SAFE.test(path) && !path.startsWith('/') && !path.split('/').some(p => p === '..' || p === '.' || p === '' || p === '__pycache__' || p === 'node_modules' || p === '.git' || p.startsWith('.env'));
  }
  function checkFile(name, bytes) {
    if (!safePath(name)) throw new Error('Unsafe archive path: ' + name);
    if (!(bytes instanceof Uint8Array)) throw new Error('Invalid ZIP entry ' + name);
    if (bytes.byteLength > MAX_FILE) throw new Error('File exceeds the TaviX 1 MB limit: ' + name);
    if (!/\.(html|css|js|mjs|png|svg|webp|json)$/.test(name)) throw new Error('Unsupported extension: ' + name);
  }
  function readU16(v, i) { return v.getUint16(i, true); }
  function readU32(v, i) { return v.getUint32(i, true); }
  async function rawInflate(bytes) {
    if (!('DecompressionStream' in global)) throw new Error('This browser does not support ZIP decompression. Use a recent Chromium, Edge or Android WebView.');
    const reader = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader();
    const chunks=[];let total=0;
    try {
      while(true){
        const part=await reader.read();
        if(part.done)break;
        total+=part.value.byteLength;
        if(total>MAX_FILE){await reader.cancel('Archive expansion exceeds file limit');throw new Error('ZIP entry expands beyond the 1 MB per-file limit.');}
        chunks.push(part.value);
      }
    } finally { reader.releaseLock(); }
    const result=new Uint8Array(total);let offset=0;
    for(const chunk of chunks){result.set(chunk,offset);offset+=chunk.length;}
    return result;
  }
  async function open(file) {
    if (file.size > MAX_ARCHIVE) throw new Error('Package exceeds the editor’s 25 MB import limit.');
    const bin = new Uint8Array(await file.arrayBuffer());
    const view = new DataView(bin.buffer, bin.byteOffset, bin.byteLength);
    let eocd = -1;
    for (let pos = bin.length - 22; pos >= Math.max(0, bin.length - 65557); pos--) {
      if (readU32(view,pos) === 0x06054b50 && pos + 22 + readU16(view,pos + 20) === bin.length) { eocd = pos; break; }
    }
    if (eocd < 0) throw new Error('Not a ZIP/.tavix archive.');
    if (readU16(view,eocd+4) || readU16(view,eocd+6) || readU16(view,eocd+8) !== readU16(view,eocd+10)) throw new Error('Multi-disk ZIPs are unsupported.');
    const count = readU16(view,eocd + 10);
    if (!count || count > MAX_FILES) throw new Error('Unsupported entry count.');
    let pos = readU32(view,eocd+16);
    const cdSize = readU32(view,eocd+12);
    if (pos + cdSize > eocd) throw new Error('Invalid ZIP central directory.');
    const entries = new Map();
    let total = 0;
    for (let i = 0; i < count; i++) {
      if (pos + 46 > bin.length || readU32(view,pos) !== 0x02014b50) throw new Error('Broken central directory.');
      const flags = readU16(view,pos+8), method = readU16(view,pos+10);
      const crc = readU32(view,pos+16), compressed = readU32(view,pos+20), size = readU32(view,pos+24);
      const nameLen = readU16(view,pos+28), extraLen = readU16(view,pos+30), commentLen = readU16(view,pos+32), local = readU32(view,pos+42);
      if (flags & 1 || flags & 0x40 || flags & 8 || ![0,8].includes(method)) throw new Error('Encrypted, streamed or unsupported ZIP entry.');
      if (size > MAX_FILE || compressed > MAX_ARCHIVE) throw new Error('Oversized archive entry.');
      if (pos+46+nameLen+extraLen+commentLen > bin.length) throw new Error('Truncated ZIP metadata.');
      const name = decoder.decode(bin.subarray(pos+46,pos+46+nameLen));
      if (entries.has(name)) throw new Error('Duplicate ZIP entry: ' + name);
      if (name.endsWith('/')) throw new Error('Directory entries are not supported in TaviX archives.');
      if (!safePath(name)) throw new Error('Unsafe ZIP entry: ' + name);
      if (local+30 > bin.length || readU32(view,local) !== 0x04034b50) throw new Error('Broken local ZIP header.');
      const start = local+30+readU16(view,local+26)+readU16(view,local+28);
      if (start + compressed > bin.length) throw new Error('Truncated ZIP file.');
      const packed = bin.subarray(start,start+compressed);
      const raw = method === 0 ? new Uint8Array(packed) : await rawInflate(packed);
      if (raw.length !== size || crc32(raw) !== crc) throw new Error('Corrupt ZIP file: ' + name);
      checkFile(name,raw);
      total += raw.length;
      if (total > MAX_TOTAL) throw new Error('Uncompressed archive exceeds limit.');
      entries.set(name,raw);
      pos += 46+nameLen+extraLen+commentLen;
    }
    return entries;
  }
  function txt(entries, name) {
    const item=entries.get(name);
    if (!item) throw new Error('Missing ' + name);
    return decoder.decode(item);
  }
  // WebCrypto where available; portable audited-against-Python fallback for offline preview contexts.
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  function rotr(x,n){return (x>>>n)|(x<<(32-n));}
  function shaFallback(bytes){
    const length=bytes.length, size=(length+9+63)&~63, msg=new Uint8Array(size);
    msg.set(bytes);msg[length]=128;
    const bits=BigInt(length)*8n;
    const view=new DataView(msg.buffer);view.setUint32(size-8,Number(bits>>32n),false);view.setUint32(size-4,Number(bits&0xffffffffn),false);
    const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const words=new Uint32Array(64);
    for(let offset=0;offset<size;offset+=64){
      for(let j=0;j<16;j++)words[j]=view.getUint32(offset+j*4,false);
      for(let j=16;j<64;j++){
        const a=words[j-15],b=words[j-2];
        words[j]=(words[j-16]+(rotr(a,7)^rotr(a,18)^(a>>>3))+words[j-7]+(rotr(b,17)^rotr(b,19)^(b>>>10)))>>>0;
      }
      let [a,b,c,d,e,f,g,q]=h;
      for(let j=0;j<64;j++){
        const t1=(q+(rotr(e,6)^rotr(e,11)^rotr(e,25))+((e&f)^(~e&g))+K[j]+words[j])>>>0;
        const t2=((rotr(a,2)^rotr(a,13)^rotr(a,22))+((a&b)^(a&c)^(b&c)))>>>0;
        q=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
      }
      for(const [j,v] of [a,b,c,d,e,f,g,q].entries())h[j]=(h[j]+v)>>>0;
    }
    return h.map(n=>n.toString(16).padStart(8,'0')).join('');
  }
  async function sha(bytes) {
    if (global.crypto?.subtle){
      const data=await global.crypto.subtle.digest('SHA-256',bytes);
      return Array.from(new Uint8Array(data),b=>b.toString(16).padStart(2,'0')).join('');
    }
    return shaFallback(bytes);
  }
  async function check(entries) {
    const manifest = JSON.parse(txt(entries,'manifest.json'));
    const lock = JSON.parse(txt(entries,'tavix.lock.json'));
    if (manifest.schema !== 'tavi.extension/v1' || !VERSION.test(manifest.version||'')) throw new Error('Invalid manifest identity or version.');
    if (manifest.kind !== 'app') throw new Error('TaviX 1.0 requires kind: app.');
    if (lock.schema !== 'tavix.package/v1' || lock.standard !== 'tavix/1.0' || lock.applicationId !== manifest.id || lock.version !== manifest.version) throw new Error('Manifest/lock mismatch.');
    if (!entries.has(manifest.entrypoints?.panel)) throw new Error('Missing application entrypoint.');
    if (manifest.icon && !entries.has(manifest.icon)) throw new Error('Missing application icon.');
    if (!Array.isArray(lock.files) || lock.files.length !== entries.size - 1) throw new Error('Lockfile lists the wrong number of files.');
    const checked = new Set();
    for (const item of lock.files) {
      if (!item || typeof item.path !== 'string' || checked.has(item.path) || item.path === 'tavix.lock.json') throw new Error('Invalid lockfile member.');
      checked.add(item.path);
      const data = entries.get(item.path);
      if (!data || data.length !== item.size || await sha(data) !== item.sha256) throw new Error('Lockfile integrity check failed: ' + item.path);
    }
    for(const path of entries.keys()) if(path !== 'tavix.lock.json' && !checked.has(path)) throw new Error('Unlisted archive content: '+path);
    return manifest;
  }
  function u16(v,pos,n) { v.setUint16(pos,n,true); }
  function u32(v,pos,n) { v.setUint32(pos,n>>>0,true); }
  function build(entries) {
    if (!entries.size || entries.size>MAX_FILES) throw new Error('Invalid archive entry count.');
    const content=[],directory=[];
    let offset=0,total=0;
    for(const [path,raw] of [...entries.entries()].sort(([a],[b])=>a.localeCompare(b,'en'))) {
      checkFile(path,raw); total+=raw.length;
      if(total>MAX_TOTAL)throw new Error('Archive too large.');
      const name=encoder.encode(path), crc=crc32(raw);
      const local=new Uint8Array(30+name.length),lv=new DataView(local.buffer);
      u32(lv,0,0x04034b50);u16(lv,4,20);u16(lv,6,0x800);u16(lv,8,0);u16(lv,10,0);u16(lv,12,0);
      u32(lv,14,crc);u32(lv,18,raw.length);u32(lv,22,raw.length);u16(lv,26,name.length);local.set(name,30);
      content.push(local,raw);
      const record=new Uint8Array(46+name.length),rv=new DataView(record.buffer);
      u32(rv,0,0x02014b50);u16(rv,4,0x0314);u16(rv,6,20);u16(rv,8,0x800);u16(rv,10,0);u16(rv,12,0);u16(rv,14,0);
      u32(rv,16,crc);u32(rv,20,raw.length);u32(rv,24,raw.length);u16(rv,28,name.length);u32(rv,38,0o100644 << 16);u32(rv,42,offset);record.set(name,46);
      directory.push(record);offset+=local.length+raw.length;
    }
    const dirLen=directory.reduce((x,y)=>x+y.length,0),end=new Uint8Array(22),ev=new DataView(end.buffer);
    u32(ev,0,0x06054b50);u16(ev,8,entries.size);u16(ev,10,entries.size);u32(ev,12,dirLen);u32(ev,16,offset);
    return new Blob([...content,...directory,end],{type:'application/zip'});
  }
  async function relock(entries,manifest) {
    const output = new Map(entries);
    output.set('manifest.json',encoder.encode(JSON.stringify(manifest,null,2)+'\n'));
    output.delete('tavix.lock.json');
    const files = [];
    for(const [path,bytes] of [...output.entries()].sort(([a],[b])=>a.localeCompare(b,'en'))) {
      checkFile(path,bytes);
      files.push({path,sha256:await sha(bytes),size:bytes.length});
    }
    const lock={applicationId:manifest.id,files,schema:'tavix.package/v1',standard:'tavix/1.0',version:manifest.version};
    output.set('tavix.lock.json',encoder.encode(JSON.stringify(lock)+'\n'));
    return output;
  }
  global.TaviXZip = Object.freeze({open,check,build,relock,sha,txt,crc32,safePath});
})(window);
