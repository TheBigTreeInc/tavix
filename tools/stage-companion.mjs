/** Companion producer post-build adapter.
 * Call after successful `npm run build` in the companion source checkout.
 * Does not build or alter companion itself; never runs Git.
 */
import {existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
const producer=path.resolve(process.cwd());
const repository=path.resolve(process.env.TAVIX_REPOSITORY_DIR||path.join(producer,'..','tavix'));
const input=path.join(producer,'dist','tavi-extension-bundle');
const tool=path.join(repository,'tools','repository.py');
if(!existsSync(tool)||!existsSync(path.join(repository,'project.zr'))){
 if(process.env.TAVIX_STAGE_REQUIRED==='1')throw Error('Companion: missing TaviX checkout: '+repository);
 console.log('TAVIX_STAGE_SKIPPED: optional TaviX repository checkout absent');
}else{
 if(!existsSync(path.join(input,'manifest.json')))throw Error('Companion compiled bundle missing: run npm run build first');
 const proc=spawnSync(process.env.TAVIX_PYTHON||(process.platform==='win32'?'python':'python3'),[tool,'stage','--repository',repository,'--input',input,'--source-url','https://github.com/TheBigTreeInc/tavix','--license','NOASSERTION'],{stdio:'inherit',windowsHide:true,cwd:producer});
 if(proc.error)throw proc.error;
 if(proc.status!==0)throw Error(`Companion TaviX stage failed: ${proc.status}`);
 console.log('TAVIX_STAGE_READY: review in the tavix ZipRunner Git project; nothing was pushed');
}
