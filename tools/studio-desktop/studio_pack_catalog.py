"""Bounded, read-only catalogue and safe artwork preview of retained TaviX/TAVIA ZIPs.

Never imports the submitted extension or treats preview as canonical validation.
No native host paths are emitted: all references are ZIP-relative and whitelisted.
"""
from __future__ import annotations
import base64
import hashlib
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile

SAFE_MEMBER = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.\-/]{0,180}$')
SVG_ELEMENTS = {'svg','g','rect','circle','ellipse','path','line','polyline','polygon','text'}
SVG_ATTRIBUTES = {'viewBox','width','height','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','d','fill','stroke','stroke-width','opacity','points','transform','font-size','font-family','text-anchor','id'}
MEDIA = {'.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg'}
MAX_PREVIEW = 96 * 1024


def safe_name(name):
    return (isinstance(name,str) and SAFE_MEMBER.fullmatch(name) is not None and
            name and not name.startswith('/') and not any(x in ('','.','..') for x in name.split('/')))


def summary(manifest, kind, members):
    deps = manifest.get('assetDependencies', []) if kind == 'tavix' else []
    classification = manifest.get('classification',{})
    if not isinstance(classification,dict):classification={}
    return {
        'kind':kind,'type':str(manifest.get('type','') if kind=='tavia' else classification.get('type','app'))[:64],
        'id':str(manifest.get('id',''))[:127], 'version':str(manifest.get('version',''))[:32],
        'counts':{'files':len(members),'resources':len(manifest.get('resources',{})) if isinstance(manifest.get('resources'),dict) else 0,
                  'objects':len(manifest.get('objects',{})) if isinstance(manifest.get('objects'),dict) else 0,
                  'collections':len(manifest.get('collections',{})) if isinstance(manifest.get('collections'),dict) else 0,
                  'dependencies':len(deps) if isinstance(deps,list) else 0},
        'dependencies':[{'packId':str(d.get('packId',''))[:127],'optional':not bool(d.get('required',False))}
                        for d in deps[:24] if isinstance(d,dict)] if isinstance(deps,list) else [],
    }


def catalog(source: Path, kind: str, section: str, offset: int, limit: int):
    if section not in ('summary','resources','objects','collections','files','dependencies'):
        raise ValueError('Unsupported catalog section')
    if not 0 <= offset <= 5000 or not 1 <= limit <= 80:
        raise ValueError('Catalog pagination out of range')
    # Caller performs full archive preflight. Still reject malformed ZIP metadata
    # rather than interpret anything outside the fixed manifest entry.
    with zipfile.ZipFile(source) as z:
        names=z.namelist()
        if len(names)>1024 or len(names)!=len(set(names)) or 'manifest.json' not in names or any(not safe_name(n) for n in names):
            raise ValueError('Unsafe package catalog')
        if z.getinfo('manifest.json').file_size > 262144:
            raise ValueError('Manifest too large')
        import json
        manifest=json.loads(z.read('manifest.json'))
        if not isinstance(manifest,dict):raise ValueError('Invalid package manifest')
        overview=summary(manifest,kind,names)
        if section=='summary':return {'section':section,'total':1,'items':[overview]}
        rows=[]
        if section=='files':
            rows=[{'id':name[:180],'path':name[:180], 'size':z.getinfo(name).file_size,
                   'kind':PurePosixPath(name).suffix.lower().removeprefix('.') or 'file'} for name in names]
        elif section=='resources':
            resources=manifest.get('resources',{})
            if isinstance(resources,dict):
                rows=[{'id':str(key)[:127], 'path':str(val.get('default',''))[:180],
                       'kind':'resource','variants':len(val.get('variants',{})) if isinstance(val.get('variants'),dict) else 0}
                      for key,val in resources.items() if isinstance(val,dict)]
        elif section=='objects':
            objects=manifest.get('objects',{})
            if isinstance(objects,dict):
                rows=[{'id':str(key)[:127],'name':str(value.get('name',''))[:160],
                       'kind':str(value.get('kind',''))[:64],
                       'resources':[str(x)[:127] for x in value.get('resources',[])[:32]] if isinstance(value.get('resources'),list) else []}
                      for key,value in objects.items() if isinstance(value,dict)]
        elif section=='collections':
            col=manifest.get('collections',{})
            if isinstance(col,dict):
                rows=[{'id':str(key)[:127],'name':str(value.get('name',''))[:160],
                       'kind':str(value.get('kind',''))[:64],
                       'entries':len(value.get('entries',[])) if isinstance(value.get('entries'),list) else 0}
                      for key,value in col.items() if isinstance(value,dict)]
        elif section=='dependencies':
            rows=overview['dependencies']
    return {'section':section,'total':len(rows),'offset':offset,'items':rows[offset:offset+limit], 'summary':overview}


def _safe_svg(data: bytes) -> bool:
    if len(data)>MAX_PREVIEW or b'<!' in data or b'<?' in data or b'&' in data:
        return False
    try:
        tree=ET.fromstring(data)
    except ET.ParseError:
        return False
    if len(list(tree.iter()))>750:
        return False
    for node in tree.iter():
        if not isinstance(node.tag,str):return False
        name=node.tag.rsplit('}',1)[-1]
        if name not in SVG_ELEMENTS:return False
        if node.tag.startswith('{') and not node.tag.startswith('{http://www.w3.org/2000/svg}'):
            return False
        for attr,val in node.attrib.items():
            key=attr.rsplit('}',1)[-1]
            if (attr.startswith('{') or key not in SVG_ATTRIBUTES or
                    any(s in val.lower() for s in ('url(', 'javascript:', 'data:', '<!', '<script'))):
                return False
    return tree.tag.rsplit('}',1)[-1]=='svg'


def preview(source: Path, kind: str, member: str):
    if not safe_name(member) or Path(member).suffix.lower() not in MEDIA:
        raise ValueError('Preview type unavailable')
    with zipfile.ZipFile(source) as z:
        if member not in z.namelist():raise ValueError('Preview member unavailable')
        if z.getinfo(member).file_size > MAX_PREVIEW:raise ValueError('Artwork too large for inline preview')
        import json
        if z.getinfo('manifest.json').file_size > 262144:raise ValueError('Manifest too large')
        manifest=json.loads(z.read('manifest.json'))
        if kind=='tavia':
            digest=manifest.get('files',{}).get(member) if isinstance(manifest.get('files'),dict) else None
            if not isinstance(digest,str):raise ValueError('Artwork not declared by pack')
        else:
            lock=json.loads(z.read('tavix.lock.json'))
            matches=[v for v in lock.get('files',[]) if isinstance(v,dict) and v.get('path')==member]
            if len(matches)!=1:raise ValueError('Artwork not declared in lock')
            digest=matches[0].get('sha256')
        data=z.read(member)
        if not isinstance(digest,str) or hashlib.sha256(data).hexdigest()!=digest:
            raise ValueError('Artwork integrity mismatch')
        suffix=Path(member).suffix.lower()
        if suffix=='.svg' and not _safe_svg(data):raise ValueError('SVG is not safe for preview')
        if suffix=='.png' and not data.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Invalid PNG')
        if suffix in ('.jpg','.jpeg') and not data.startswith(b'\xff\xd8\xff'):raise ValueError('Invalid JPEG')
        if suffix=='.webp' and not(data.startswith(b'RIFF') and data[8:12]==b'WEBP'):raise ValueError('Invalid WebP')
        return {'member':member, 'mime':MEDIA[suffix],
                'dataUrl':f'data:{MEDIA[suffix]};base64,{base64.b64encode(data).decode("ascii")}'}
