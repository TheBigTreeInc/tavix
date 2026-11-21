#!/usr/bin/env python3
"""Trusted, offline TaviX Studio submission inspection and feedback exporter.

Native Rust chooses the path; renderer cannot provide arbitrary filesystem paths.
Uses the canonical TaviX and Tavi Assets validators. Does not execute packages,
authorize a publisher, grant entitlements, or publish to a remote store.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import zipfile
# -I is used by the Rust process. This fixed source directory is trusted,
# while no user-supplied archive directory is ever added to Python's import path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from studio_diagnostics import health as studio_health, record as record_diagnostic
from studio_pack_catalog import catalog as pack_catalog, preview as pack_preview
from studio_blueprint_library import load as library_load, local_entries, import_blueprint, local_readme
from studio_publisher_probe import probe as publisher_probe
from studio_tavib import discover as discover_tavib, import_selected as import_tavib, inspect_member as inspect_tavib_member
from studio_release_gateway import releases as github_releases, draft as github_draft, publish as github_publish, receipt as github_receipt, connection as github_connection
from studio_looprd_adapter import connection as looprd_connection, catalog as looprd_catalog, inspect as looprd_inspect, stage as looprd_stage, publish as looprd_publish
from studio_github_catalog import sync as github_catalog_sync, preview as github_catalog_preview, prepare as github_catalog_prepare, login as github_login

MAX_ARCHIVE = 48 * 1024 * 1024
MAX_EXPANDED = 160 * 1024 * 1024
MAX_ENTRIES = 1024
MAX_MANIFEST = 262144
MAX_OUTPUT = 64 * 1024 * 1024
ASSET_MEDIA_SUFFIXES = {'.svg','.png','.webp','.jpg','.jpeg','.ogg','.wav','.mp3','.json'}
SAFE_MEMBER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-/]{0,180}$")
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,126}$")


def issue(code: str, severity: str, message: str, resource: str = "") -> dict:
    return {"code": code, "severity": severity, "message": message[:360], "resource": resource[:128]}


def _safe_name(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return bool(name and SAFE_MEMBER.fullmatch(name) and not name.startswith('/') and
                not any(part in ('', '.', '..') for part in parts) and '\\' not in name)


def _open_manifest(source: Path) -> dict:
    if not source.is_file() or source.is_symlink() or source.stat().st_size > MAX_ARCHIVE:
        raise ValueError('Package missing, linked or exceeds Studio 48 MiB review limit')
    with zipfile.ZipFile(source) as z:
        infos = z.infolist()
        if not infos or len(infos) > MAX_ENTRIES:
            raise ValueError('Unsupported archive entry count')
        seen = set()
        total = 0
        for item in infos:
            name = item.filename
            if not _safe_name(name) or item.is_dir() or item.flag_bits & 1 or item.file_size < 0:
                raise ValueError('Unsafe or unsupported archive member')
            if item.external_attr >> 16 & 0o170000 == 0o120000:
                raise ValueError('Archive symlink is forbidden')
            if name.casefold() in seen:
                raise ValueError('Duplicate archive member')
            seen.add(name.casefold())
            total += item.file_size
            if item.file_size > 20 * 1024 * 1024 or total > MAX_EXPANDED:
                raise ValueError('Archive expansion limit exceeded')
        if 'manifest.json' not in z.namelist():
            raise ValueError('Root manifest.json is missing')
        info = z.getinfo('manifest.json')
        if info.file_size > MAX_MANIFEST:
            raise ValueError('Manifest exceeds size limit')
        data = z.read(info)
        try:
            manifest = json.loads(data)
        except (ValueError, UnicodeError):
            raise ValueError('Manifest JSON is invalid') from None
        if not isinstance(manifest, dict):
            raise ValueError('Manifest must be an object')
        return manifest



def _tavia_resource_hint(source: Path) -> str:
    """Only ZIP-relative safe names. Never return arbitrary archive text or OS paths."""
    try:
        with zipfile.ZipFile(source) as z:
            invalid = [i.filename for i in z.infolist() if i.filename != 'manifest.json'
                       and PurePosixPath(i.filename).suffix.lower() not in ASSET_MEDIA_SUFFIXES]
            if invalid:
                first = invalid[0]
                if not _safe_name(first) or any(token in first.lower() for token in
                    ('token','secret','password','credential','bearer','key=','auth','ghp_','github_pat_')):
                    first = '[unsafe archive name withheld]'
                return f'Unsupported resource member {first}; {len(invalid)} unsupported file(s). Use approved image/audio/JSON resources and keep design documents in the outer feedback ZIP.'
    except (ValueError, OSError, zipfile.BadZipFile):
        pass
    return ''

def _canonical_validation(source: Path, kind: str, repo: Path, assets: Path | None):
    if kind == 'tavix':
        sys.path.insert(0, str(repo / 'tools'))
        try:
            from tavix_package import validate_archive
            validate_archive(source)
            return True, '', ''
        except (ImportError, OSError, RuntimeError, ValueError, KeyError, zipfile.BadZipFile) as exc:
            # An unavailable canonical implementation is not a successful validation.
            return False, 'TAVIX_CANONICAL_REJECTED' if not isinstance(exc, ImportError) else 'TAVIX_VALIDATOR_MISSING', ''
        finally:
            sys.path.pop(0)
    if not assets or not (assets / 'src/tavi_assets/tavia.py').is_file():
        return False, 'TAVIA_VALIDATOR_MISSING', 'Connect the canonical Tavi Assets source checkout in Studio Connections'
    # Reuse the existing reviewed management adapter. It validates through an
    # isolated, fixed Python CLI and already limits canonical AssetError reasons.
    # This avoids interpreter module collisions and never runs submitted content.
    try:
        import importlib.util
        manager_source = repo / 'tools/local_client/manager_assets.py'
        spec = importlib.util.spec_from_file_location('studio_canonical_assets_adapter', manager_source)
        if spec is None or spec.loader is None:
            return False, 'TAVIA_VALIDATOR_UNAVAILABLE', 'Canonical Assets inspection adapter unavailable'
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        adapter.inspect_tavia(source.read_bytes(), assets)
        return True, '', ''
    except Exception as exc:
        # Only the trusted adapter's fixed, bounded public message may cross IPC.
        # Unanticipated Python exceptions may carry full paths or untrusted data.
        if 'adapter' in locals() and isinstance(exc, adapter.AssetImportError):
            category = {
                'TAVIA_VALIDATION_REJECTED': 'TAVIA_CANONICAL_REJECTED',
                'TAVIA_ARCHIVE_INVALID': 'TAVIA_ARCHIVE_REJECTED',
                'TAVIA_ARCHIVE_LIMIT': 'TAVIA_ARCHIVE_REJECTED',
                'TAVIA_TOO_LARGE': 'TAVIA_TOO_LARGE',
                'TAVIA_VALIDATOR_FAILED': 'TAVIA_VALIDATOR_FAILED',
                'TAVIA_VALIDATOR_TIMEOUT': 'TAVIA_VALIDATOR_TIMEOUT',
                'TAVIA_VALIDATOR_PROTOCOL': 'TAVIA_VALIDATOR_PROTOCOL',
                'TAVIA_VALIDATOR_MISSING': 'TAVIA_VALIDATOR_MISSING',
                'TAVIA_SOURCE_MISSING': 'TAVIA_VALIDATOR_MISSING',
                'TAVIA_SOURCE_INVALID': 'TAVIA_SOURCE_INVALID',
                'TAVIA_EMPTY': 'TAVIA_ARCHIVE_REJECTED',
            }
            code = category.get(exc.code, 'TAVIA_VALIDATOR_UNAVAILABLE')
            reason = exc.public_message[:320]
            if 'unsupported TAVIA resource type' in reason:
                reason += ' Keep designer documents in the outer feedback ZIP.'
            return False, code, reason[:360]
        return False, 'TAVIA_VALIDATOR_UNEXPECTED', 'The trusted inspection adapter failed unexpectedly. Validation was not completed; export Studio diagnostics'


def _load_blueprint(root: Path, selected: str) -> tuple[dict, str | None]:
    return library_load(root, selected)


def available_blueprints(repo: Path):
    items=[]
    for path in sorted((repo / 'tools/studio-desktop/blueprints').glob('*.json')):
        data, _ = _load_blueprint(repo, path.stem)
        items.append({"id":data['id'],"title":data['title'],"description":data.get('description',''),
                      "applicablePackTypes":data['applicablePackTypes'],
                      "requiredCount":len(data['requiredResources'])+sum(data.get('requiredPrefixes',{}).values()),
                      "designerChecklist":data['designerChecklist'],"origin":"bundled"})
    for data,digest in local_entries():
        items.append({"id":data['id'],"title":data['title'],"description":data.get('description',''),
                      "applicablePackTypes":data['applicablePackTypes'],
                      "requiredCount":len(data['requiredResources'])+sum(data.get('requiredPrefixes',{}).values()),
                      "designerChecklist":data['designerChecklist'],"origin":"operator",
                      "digestPrefix":digest})
    return items


def inspect(source: Path, repo: Path, assets: Path | None, blueprint_id: str) -> dict:
    kind = source.suffix.lower().removeprefix('.')
    if kind not in ('tavia', 'tavix'):
        raise ValueError('Only .tavia and .tavix archives can be submitted')
    digest = hashlib.sha256(source.read_bytes()).hexdigest() if source.stat().st_size <= MAX_ARCHIVE else ''
    notes = []
    try:
        manifest = _open_manifest(source)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        manifest = {}
        notes.append(issue('ARCHIVE_REJECTED', 'blocking', str(exc)))
    identity = manifest.get('id','')
    version = manifest.get('version','')
    if not isinstance(identity, str) or not SAFE_ID.fullmatch(identity):
        identity = ''
        notes.append(issue('IDENTITY_INVALID', 'blocking', 'Package ID missing or invalid'))
    if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+',version):
        version = ''
        notes.append(issue('VERSION_INVALID', 'blocking', 'Package version missing or invalid'))
    display = manifest.get('display')
    title = manifest.get('name') if kind == 'tavix' else (display.get('name') if isinstance(display, dict) else '')
    title = title if isinstance(title,str) else ''
    canonical_valid = False
    if manifest:
        canonical_valid, error_code, hint = _canonical_validation(source, kind, repo, assets)
        if not canonical_valid:
            notes.append(issue(error_code, 'blocking',
                               hint or 'Canonical package validation failed; use TaviX or Tavi Assets validation diagnostics before publication'))
    blueprint = None
    present_count = 0
    required_count = 0
    if kind == 'tavia' and blueprint_id:
        data, _ = _load_blueprint(repo, blueprint_id)
        pack_type = manifest.get('type')
        matches_type = pack_type in data.get('applicablePackTypes', [])
        if not matches_type:
            notes.append(issue('BLUEPRINT_TYPE_MISMATCH', 'blocking',
                               'Selected blueprint does not apply to this asset pack type. Choose a matching blueprint or review without a preset'))
        resources = manifest.get('resources',{})
        if not isinstance(resources, dict): resources = {}
        required = data.get('requiredResources',[])
        prefixes = data.get('requiredPrefixes',{})
        required_count = len(required) + sum(prefixes.values())
        if matches_type:
            for item in required:
                if item in resources:
                    present_count += 1
                else:
                    notes.append(issue('BLUEPRINT_MISSING_RESOURCE','blocking',f'Missing required resource: {item}',item))
            for prefix, minimum in prefixes.items():
                found = sum(1 for key in resources if key.startswith(prefix))
                present_count += min(found, minimum)
                if found < minimum:
                    notes.append(issue('BLUEPRINT_MISSING_GROUP','blocking',
                                       f'Expected at least {minimum} resource(s) with prefix {prefix}; found {found}',prefix))
        blueprint = {'id': data['id'], 'title': data['title'],
                     'origin':'operator' if blueprint_id.startswith('local-') else 'bundled',
                     'sourceDigest':hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=True).encode('utf-8')).hexdigest(),
                     'present': present_count, 'required': required_count,
                     'designerChecklist': data.get('designerChecklist',[])}
    elif kind == 'tavia' and not blueprint_id:
        notes.append(issue('BLUEPRINT_NOT_SELECTED','review',
                           'Choose a designer blueprint to check pack completeness before store review'))
    if kind == 'tavix':
        deps = manifest.get('assetDependencies',[])
        if deps:
            notes.append(issue('ASSET_DEPENDENCIES_EXTERNAL','review',
                               f'{len(deps)} asset dependency declaration(s) require installed-pack compatibility review'))
    if not isinstance(manifest.get('schema'), str) or manifest['schema'] not in ('tavi.assets.pack/v1','tavi.extension/v1'):
        notes.append(issue('MANIFEST_SCHEMA_INVALID','blocking','Unsupported or missing package manifest schema'))
    return {'kind':kind,'sha256':digest,'packageId':identity,'version':version,'title':title[:160],
            'canonicalValid':canonical_valid, 'blueprint':blueprint, 'issues':notes,
            'assetDependencies':len(manifest.get('assetDependencies',[])) if isinstance(manifest.get('assetDependencies',[]),list) else 0,
            'storeReady':canonical_valid and bool(identity and version) and not any(i['severity']=='blocking' for i in notes) and (kind=='tavix' or blueprint is not None)}


def _clean(value: str, limit: int = 500) -> str:
    return ''.join(ch if ch >= ' ' and ch not in '\r\n' else ' ' for ch in value)[:limit]


def export(original: Path, report_path: Path, destination: Path, repo: Path, mode: str):
    if mode not in ('feedback','preview','approval'):
        raise ValueError('Unknown export mode')
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if original.stat().st_size > MAX_ARCHIVE:
        raise ValueError('Source package too large')
    source = original.read_bytes()
    if hashlib.sha256(source).hexdigest() != report['sha256']:
        raise ValueError('Source package has changed since inspection')
    if mode in ('preview','approval') and not report.get('canonicalValid'):
        raise ValueError('Invalid packages cannot be exported as previews or approvals')
    if mode == 'approval' and report.get('status') != 'review_approved':
        raise ValueError('Package has no local operator review approval')
    if destination.exists():
        raise ValueError('Refusing to overwrite an existing feedback bundle')
    if not destination.parent.is_dir():
        raise ValueError('Export parent does not exist')
    kind = report['kind']
    safe_id = report.get('packageId') or 'unidentified'
    source_name = f'{safe_id}-{report.get("version") or "unknown"}.{kind}'
    header = ('Developer preview — not an official store release' if mode=='preview' else
              'Local review approval — NOT publication authority' if mode=='approval' else
              'Designer and developer feedback — changes requested or inspection report')
    lines = [f'= {_clean(header)}','',f'Package: `{_clean(safe_id)}`',
             f'Version: `{_clean(report.get("version", ""))}`',
             f'SHA-256: `{report["sha256"]}`',f'Format: `{kind}`',
             f'Canonical validator: {"passed" if report.get("canonicalValid") else "failed or unavailable"}',
             f'Local review status: `{report.get("status", "draft")}`','',
             '== Findings']
    issues=report.get('issues', [])[:400]
    if issues:
        for i in issues:
            lines.append(f'* [{_clean(i.get("severity",""))}] {_clean(i.get("code",""))}: {_clean(i.get("message",""))}')
    else:
        lines.append('* No machine-detected findings. Designer checklist and operator acceptance still apply.')
    lines.extend(['','== Reviewer notes','* '+(_clean(report.get('reviewerNote',''), 2000) or 'None provided'),'',
                  '== Boundaries','This ZIP is a review handoff, not a .tavia or .tavix installable package.',
                  'No Git push, publisher signature, LoopRD entitlement, Wallet payment or store publication is implied.'])
    metadata = json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False).encode('utf-8') + b'\n'
    # Resolve and pin the exact blueprint BEFORE opening an output ZIP, so a
    # modified operator-local profile cannot produce a partial handoff file.
    bp_id=(report.get('blueprint') or {}).get('id')
    bp=None
    adoc=None
    if bp_id:
        bp,adoc=_load_blueprint(repo,bp_id)
        current_digest=hashlib.sha256(json.dumps(bp,sort_keys=True,ensure_ascii=True).encode('utf-8')).hexdigest()
        expected_digest=(report.get('blueprint') or {}).get('sourceDigest')
        if bp_id.startswith('local-') and expected_digest!=current_digest:
            raise ValueError('Local blueprint changed since review; recheck this exact submission before exporting')
    # The original source package stays byte-for-byte unchanged in the OUTER review ZIP.
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('submission/'+source_name,source)
        z.writestr('feedback/REVIEW.adoc','\n'.join(lines)+'\n')
        z.writestr('feedback/review.json',metadata)
        if bp_id and bp:
            z.writestr('blueprint/'+bp_id+'.json',json.dumps(bp,indent=2).encode('utf-8'))
            z.writestr('blueprint/'+bp_id+'.adoc',Path(adoc).read_bytes() if adoc else local_readme(bp_id).encode('utf-8'))
    if destination.stat().st_size > MAX_OUTPUT:
        destination.unlink(missing_ok=True)
        raise ValueError('Export exceeds size limit')
    return {'filename':destination.name, 'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'mode':mode}


def main(args):
    if len(args)<3:
        raise ValueError('usage: inspect|blueprints|export ROOT [ARGS]')
    action = args[1]
    root=Path(args[2]).resolve()
    if not (root/'project.zr').is_file() or json.loads((root/'project.zr').read_text(encoding='utf-8')).get('project_key') != 'tavix':
        raise ValueError('Expected trusted TaviX checkout')
    if action=='blueprints': return available_blueprints(root)
    if action=='tavib_discover':
        if len(args)!=4: raise ValueError('TAVIB_SELECTION_INVALID')
        return discover_tavib(Path(args[3]),root)
    if action=='tavib_detail':
        if len(args)!=6:raise ValueError('TAVIB_SELECTION_INVALID')
        return inspect_tavib_member(Path(args[3]),root,args[4],args[5])
    if action=='tavib_import':
        if len(args)!=6: raise ValueError('TAVIB_SELECTION_INVALID')
        return import_tavib(Path(args[3]),root,args[4],json.loads(args[5]))
    if action=='looprd_connect':
        if len(args)!=6:raise ValueError('LOOPRD_ENDPOINT_INVALID')
        return looprd_connection(args[3],args[4],args[5])
    if action=='looprd_catalog':
        if len(args)!=5:raise ValueError('LOOPRD_ENDPOINT_INVALID')
        return looprd_catalog(args[3],args[4])
    if action=='looprd_inspect':
        if len(args)!=5:raise ValueError('LOOPRD_ENDPOINT_INVALID')
        return looprd_inspect(args[3],args[4])
    if action=='looprd_stage':
        if len(args)!=10:raise ValueError('LOOPRD_EXACT_APPROVAL_REQUIRED')
        return looprd_stage(*args[3:10])
    if action=='looprd_publish':
        if len(args)!=9:raise ValueError('LOOPRD_EXACT_APPROVAL_REQUIRED')
        return looprd_publish(*args[3:9])
    if action=='publisher_releases':
        if len(args)!=4: raise ValueError('PUBLISH_DESTINATION_INVALID')
        return github_releases(args[3])
    if action=='publisher_auth':
        if len(args)!=3: raise ValueError('PUBLISH_DESTINATION_INVALID')
        return github_connection()
    if action in ('publisher_draft','publisher_publish','publisher_receipt'):
        if len(args)!=7: raise ValueError('RELEASE_IDENTITY_INVALID')
        if action=='publisher_draft':return github_draft(args[3],args[4],args[5],args[6])
        if action=='publisher_publish':return github_publish(args[3],args[5],args[6])
        return github_receipt(args[6],args[5])
    if action=='github_login':
        if len(args)!=3:raise ValueError('GITHUB_CATALOG_REQUEST_INVALID')
        return github_login()
    if action=='github_catalog_sync':
        if len(args)!=4:raise ValueError('GITHUB_CATALOG_REQUEST_INVALID')
        return github_catalog_sync(args[3])
    if action=='github_catalog_preview':
        if len(args)!=8:raise ValueError('GITHUB_CATALOG_REQUEST_INVALID')
        return github_catalog_preview(*args[3:8])
    if action=='github_catalog_prepare':
        if len(args)!=9:raise ValueError('GITHUB_CATALOG_REQUEST_INVALID')
        return github_catalog_prepare(*args[3:9])
    if action=='publisher_probe':
        if len(args)!=5: raise ValueError('Invalid publisher probe arguments')
        return publisher_probe(args[3],args[4])
    if action=='blueprint_import':
        if len(args)!=4: raise ValueError('Invalid blueprint import arguments')
        return import_blueprint(Path(args[3]))
    if action=='health':
        if len(args) != 5: raise ValueError('health requires fixed native source selection')
        return studio_health(root, Path(args[3]) if args[3] != '-' else None, args[4])
    if action=='inspect':
        if len(args)!=6: raise ValueError('inspect ROOT SOURCE ASSETS BLUEPRINT')
        report = inspect(Path(args[3]),root,Path(args[4]) if args[4]!='-' else None,args[5] if args[5]!='-' else '')
        record_diagnostic('inspect', [item['code'] for item in report.get('issues', [])] or ['INSPECT_OK'], report['kind'], report['sha256'])
        return report
    if action in ('catalog','preview'):
        if (action=='catalog' and len(args)!=8) or (action=='preview' and len(args)!=6):
            raise ValueError('Invalid fixed catalog argument count')
        source=Path(args[3]); digest=args[4]
        if not re.fullmatch(r'[a-f0-9]{64}',digest) or not source.is_file() or source.stat().st_size>MAX_ARCHIVE:
            raise ValueError('Stored archive unavailable')
        if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
            raise ValueError('Stored archive digest mismatch')
        _open_manifest(source)  # Full preflight before displaying untrusted metadata.
        kind=source.suffix.lower().removeprefix('.')
        if kind not in ('tavia','tavix'):raise ValueError('Invalid package type')
        if action=='catalog':return pack_catalog(source,kind,args[5],int(args[6]),int(args[7]))
        return pack_preview(source,kind,args[5])
    if action=='export':
        if len(args)!=7: raise ValueError('export ROOT SOURCE REPORT DEST MODE')
        return export(Path(args[3]), Path(args[4]), Path(args[5]),root,args[6])
    raise ValueError('Unsupported review action')


def protocol_response(argv):
    """Produce exactly one fixed-schema JSON envelope, even on unexpected faults.

    Trusted validators may print diagnostics; stdout is reserved for the native
    IPC response, never the validator's console output or archive content.
    """
    from contextlib import redirect_stdout
    try:
        with redirect_stdout(io.StringIO()):
            result = main(argv)
        return {'ok': True, 'result': result}
    except (ValueError, OSError, zipfile.BadZipFile, KeyError) as exc:
        exact = {'Invalid blueprint ID':'BLUEPRINT_INVALID', 'Blueprint unavailable':'BLUEPRINT_UNAVAILABLE',
                 'Unsupported blueprint contract':'BLUEPRINT_UNSUPPORTED',
                 'BLUEPRINT_FILE_INVALID':'BLUEPRINT_FILE_INVALID',
                 'BLUEPRINT_ALREADY_IMPORTED':'BLUEPRINT_ALREADY_IMPORTED',
                 'BLUEPRINT_JSON_INVALID':'BLUEPRINT_JSON_INVALID',
                 'Package missing, linked or exceeds Studio 48 MiB review limit':'PACKAGE_UNAVAILABLE'}
        raw=str(exc)
        code = exact.get(raw, raw if raw in {
            'TAVIB_ALREADY_IMPORTED','TAVIB_SOURCE_CHANGED','TAVIB_SELECTION_INVALID',
            'RELEASE_APPROVAL_REQUIRED','GITHUB_CLI_MISSING','GITHUB_AUTH_REQUIRED',
            'GITHUB_COMMAND_FAILED','RELEASE_ALREADY_PREPARED','RELEASE_DRAFT_REQUIRED',
            'GITHUB_CATALOG_DESTINATION_INVALID','GITHUB_ASSETS_REPOSITORY_REQUIRED',
            'GITHUB_CATALOG_API_FAILED','GITHUB_CATALOG_TOO_LARGE',
            'GITHUB_CATALOG_RESPONSE_INVALID','GITHUB_CATALOG_READ_FAILED',
            'GITHUB_CATALOG_SCHEMA_UNSUPPORTED','GITHUB_CATALOG_SOURCE_INDEX_MISMATCH',
            'GITHUB_CATALOG_STALE_REVISION','GITHUB_CATALOG_ENTRY_EXISTS',
            'GITHUB_CATALOG_CONFIRMATION_REQUIRED','GITHUB_CATALOG_SOURCE_CHANGED',
            'GITHUB_CATALOG_REVIEW_REQUIRED','GITHUB_CATALOG_PR_UNVERIFIED',
            'GITHUB_LOGIN_TERMINAL_REQUIRED','GITHUB_LOGIN_LAUNCH_FAILED',
            'GITHUB_CATALOG_REQUEST_INVALID', 
            'LOOPRD_ENDPOINT_INVALID','LOOPRD_REQUEST_TOO_LARGE','LOOPRD_RESPONSE_TOO_LARGE',
            'LOOPRD_SCOPED_TOKEN_REQUIRED','LOOPRD_SCOPE_REJECTED','LOOPRD_HTTP_ERROR',
            'LOOPRD_UNREACHABLE','LOOPRD_RESPONSE_INVALID','LOOPRD_OPERATION_REJECTED',
            'LOOPRD_SOURCE_INVALID','LOOPRD_SOURCE_CHANGED','LOOPRD_REVIEW_REQUIRED',
            'LOOPRD_RECEIPT_REQUIRED','LOOPRD_RECEIPT_INVALID','LOOPRD_CANONICAL_ASSETS_REQUIRED',
            'LOOPRD_STAGE_UNVERIFIED','LOOPRD_NOT_STAGED','LOOPRD_PUBLISH_UNVERIFIED'
        } else 'REVIEW_OPERATION_REJECTED')
        hints = {'BLUEPRINT_INVALID':'Invalid designer blueprint identifier',
                 'BLUEPRINT_UNAVAILABLE':'Selected designer blueprint is missing from the TaviX source',
                 'BLUEPRINT_UNSUPPORTED':'Designer blueprint is not compatible with this Studio',
                 'BLUEPRINT_FILE_INVALID':'Blueprint must be a safe JSON file smaller than 32 KiB',
                 'BLUEPRINT_ALREADY_IMPORTED':'This local blueprint ID is already imported; use a new ID and version to preserve review identity',
                 'BLUEPRINT_JSON_INVALID':'Invalid blueprint JSON or unsupported blueprint schema or fields',
                 'PACKAGE_UNAVAILABLE':'Selected package cannot be read or exceeds the 48 MiB review limit',
                 'TAVIB_ALREADY_IMPORTED':'Blueprint from this exact application and version is already imported',
                 'TAVIB_SOURCE_CHANGED':'Application package changed after discovery; choose it again',
                 'TAVIB_SELECTION_INVALID':'Choose a valid discovered blueprint',
                 'RELEASE_APPROVAL_REQUIRED':'Local review approval and canonical validation are required',
                 'GITHUB_CLI_MISSING':'GitHub CLI (gh) is not installed',
                 'GITHUB_AUTH_REQUIRED':'Authenticate with gh auth login outside Studio',
                 'GITHUB_COMMAND_FAILED':'GitHub release request failed; inspect your account permissions and GitHub CLI outside Studio',
                 'RELEASE_ALREADY_PREPARED':'A GitHub release draft receipt already exists for this artifact',
                 'RELEASE_DRAFT_REQUIRED':'Create an approved GitHub release draft before public publication',
                 'LOOPRD_ENDPOINT_INVALID':'Use the approved HTTPS hostname and exact /admin and /catalog DAPI paths',
                 'LOOPRD_SCOPED_TOKEN_REQUIRED':'A short-lived scoped LoopRD service credential was not supplied to Studio',
                 'LOOPRD_SCOPE_REJECTED':'LoopRD rejected this service credential or required scope',
                 'LOOPRD_HTTP_ERROR':'LoopRD returned a non-success HTTP status',
                 'LOOPRD_UNREACHABLE':'LoopRD HTTPS service is unreachable with trusted TLS',
                 'LOOPRD_RESPONSE_INVALID':'LoopRD did not return a valid registry response',
                 'LOOPRD_RESPONSE_TOO_LARGE':'LoopRD response exceeded Studio safe size',
                 'LOOPRD_REQUEST_TOO_LARGE':'Registry request exceeded the safe request bound',
                 'LOOPRD_OPERATION_REJECTED':'LoopRD refused this operation; check service authorization, component status and audit',
                 'LOOPRD_SOURCE_INVALID':'The approved source is not a valid TAVIA review',
                 'LOOPRD_SOURCE_CHANGED':'The exact reviewed TAVIA archive was changed',
                 'LOOPRD_REVIEW_REQUIRED':'Canonical validation, store readiness and local approval are required',
                 'LOOPRD_RECEIPT_REQUIRED':'Choose the separate approval receipt for this action and exact artifact',
                 'LOOPRD_RECEIPT_INVALID':'Approval receipt does not match the exact action, endpoint and pack digest',
                 'LOOPRD_CANONICAL_ASSETS_REQUIRED':'Connect a valid local tavi-assets checkout to stage using canonical validation',
                 'LOOPRD_STAGE_UNVERIFIED':'Staging did not return the ready state',
                 'LOOPRD_NOT_STAGED':'The exact pack/version is not ready for promotion on LoopRD',
                 'LOOPRD_PUBLISH_UNVERIFIED':'The server did not confirm published status',
                 'REVIEW_OPERATION_REJECTED':'Review operation rejected; inspect Studio Connections and diagnostics'}
    except Exception:
        # Never send traceback, exception text or submitted archive contents to WebView.
        code = 'REVIEW_INTERNAL_FAILURE'
        hints = {'REVIEW_INTERNAL_FAILURE':'The trusted Studio review process failed unexpectedly. No package was approved; copy the diagnostic report'}
    record_diagnostic('cli', [code])
    return {'ok': False, 'code': code, 'reason': hints[code]}


if __name__ == '__main__':
    response = protocol_response(sys.argv)
    # Rust requires UTF-8. On Windows, redirected stdout may use a legacy ANSI code page.
    # Force 7-bit JSON escapes for every untrusted Unicode title/message, even with python -I.
    print(json.dumps(response, separators=(',', ':'), ensure_ascii=True))
    raise SystemExit(0 if response['ok'] else 1)
