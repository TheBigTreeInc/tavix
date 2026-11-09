"""Local-only .tavix installer; never publishes packages or grants publisher trust."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

from tools.tavix_package import validate_archive, validate
from tools.tavix_classification import resolve_classification
from tools.tavix_asset_dependencies import validate_asset_dependencies
from tools.tavix_registry_admin import validate_registry_admin_request
from tools.tavix_local_file_import import validate_local_file_import

ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')
MAX_ARCHIVE = 32 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024


def install(data: bytes, storage: Path):
    if not data or len(data) > MAX_ARCHIVE:
        raise ValueError('Archive is empty or exceeds 32 MiB')
    storage = storage.resolve()
    storage.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tavix-verify-') as tmp:
        tmp = Path(tmp)
        archive = tmp / 'upload.tavix'
        archive.write_bytes(data)
        lock = validate_archive(archive)
        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            if len(infos) > 1024 or sum(x.file_size for x in infos) > MAX_TOTAL:
                raise ValueError('Archive exceeds extraction limits')
            for info in infos:
                if info.is_dir() or (info.external_attr >> 16) & 0o170000 not in (0, 0o100000):
                    raise ValueError('Only regular files are allowed')
                if info.flag_bits & 1:
                    raise ValueError('Encrypted entries are forbidden')
            extracted = tmp / 'content'
            extracted.mkdir()
            for info in infos:
                target = (extracted / info.filename).resolve()
                if not target.is_relative_to(extracted.resolve()):
                    raise ValueError('Unsafe archive member')
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as source, target.open('wb') as dest:
                    shutil.copyfileobj(source, dest)
        manifest = json.loads((extracted / 'manifest.json').read_text(encoding='utf-8'))
        app_id, version = manifest.get('id'), manifest.get('version')
        if not isinstance(app_id, str) or not ID.fullmatch(app_id) or not isinstance(version, str) or not ID.fullmatch(version):
            raise ValueError('Unsafe package identity or version')
        if lock.get('applicationId') != app_id or lock.get('version') != version:
            raise ValueError('Manifest and lock identity mismatch')
        validate(extracted)
        classification = resolve_classification(manifest)
        dependencies = validate_asset_dependencies(manifest)
        admin_requested = validate_registry_admin_request(manifest)
        file_imports = validate_local_file_import(manifest)
        panel = manifest['entrypoints']['panel']
        target = storage / app_id / version
        if target.exists():
            raise ValueError('This exact package version is already installed; remove it before replacement')
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.stage-', dir=storage))
        try:
            for file in extracted.rglob('*'):
                if file.is_file():
                    dest = stage / file.relative_to(extracted)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(file, dest)
            os.replace(stage, target)
        finally:
            if stage.exists(): shutil.rmtree(stage)
        return {'id': app_id, 'version': version, 'name': manifest.get('name', app_id), 'classification': classification, 'assetDependencies': dependencies, 'registryAdminRequested': admin_requested, 'fileImports': file_imports, 'sha256': hashlib.sha256(data).hexdigest(), 'panel': '/__local_packages/' + app_id + '/' + version + '/' + panel, 'permissions': manifest.get('permissions', []), 'publisher_trust': 'unverified', 'scope': 'local-only'}


def installed(storage: Path):
    result = []
    for manifest_path in sorted(storage.glob('*/*/manifest.json')):
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            app_id, version = manifest_path.parent.parent.name, manifest_path.parent.name
            if manifest['id'] != app_id or manifest['version'] != version: continue
            classification = resolve_classification(manifest)
            dependencies = validate_asset_dependencies(manifest)
            admin_requested = validate_registry_admin_request(manifest)
            file_imports = validate_local_file_import(manifest)
            panel = manifest['entrypoints']['panel']
            if not (manifest_path.parent / panel).resolve().is_relative_to(manifest_path.parent.resolve()): continue
            if not (manifest_path.parent / panel).is_file(): continue
            result.append({'id': app_id, 'version': version, 'name': manifest.get('name', app_id), 'classification': classification, 'assetDependencies': dependencies, 'registryAdminRequested': admin_requested, 'fileImports': file_imports, 'panel': '/__local_packages/' + app_id + '/' + version + '/' + panel, 'permissions': manifest.get('permissions', []), 'scope': 'local-only', 'publisher_trust': 'unverified'})
        except (ValueError, KeyError, TypeError, OSError): pass
    return result


def remove(storage: Path, app_id: str, version: str):
    if not ID.fullmatch(app_id) or not ID.fullmatch(version): raise ValueError('Invalid identity')
    target = storage.resolve() / app_id / version
    if not target.is_dir(): raise ValueError('Not installed')
    shutil.rmtree(target)
    if not target.parent.iterdir(): target.parent.rmdir()
