#!/usr/bin/env python3
"""Read-only static conformance for the optional TaviX offline UI kit.

This does not test native rendering, permissions or trust; it only checks
package integrity and that locally bundled kit bytes match the reviewed set.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

if __package__:
    from .tavix_package import validate, validate_archive
else:
    from tavix_package import validate, validate_archive

ROOT = Path(__file__).resolve().parents[1]
FILES = ('ui.css', 'ui.js', 'icons.js', 'icon-shapes.js')


def check(package: Path, kit_dir: str = 'ui/kit') -> dict:
    prefix = PurePosixPath(kit_dir)
    if (not kit_dir or prefix.is_absolute() or '..' in prefix.parts
            or not all(x.replace('-', '').replace('_','').isalnum() for x in prefix.parts)):
        raise ValueError('invalid in-package kit directory')
    if package.is_dir():
        lock = validate(package)
        def read(rel: str) -> bytes:
            path = package / rel
            if not path.is_file():
                raise ValueError('UI kit file missing: ' + rel)
            return path.read_bytes()
    elif package.is_file() and package.suffix.lower() == '.tavix':
        lock = validate_archive(package)
        archive = zipfile.ZipFile(package)
        try:
            # Package integrity already verified, read only the known bounded kit paths.
            def read(rel: str) -> bytes:
                try:
                    return archive.read(rel)
                except KeyError:
                    raise ValueError('UI kit file missing: ' + rel) from None
            return _verify(read, lock, prefix)
        finally:
            archive.close()
    else:
        raise ValueError('expected TaviX app directory or .tavix archive')
    return _verify(read, lock, prefix)


def _verify(read, lock: dict, prefix: PurePosixPath) -> dict:
    for filename in FILES:
        actual = read(str(prefix / filename))
        reviewed = (ROOT / 'sdk' / 'ui-kit' / filename).read_bytes()
        if actual != reviewed:
            raise ValueError('UI kit differs from reviewed SDK: ' + filename)
    license_record = json.loads(read(str(prefix / 'LUCIDE_LICENSE.json')))
    if license_record.get('licenseText') != (ROOT / 'sdk/ui-kit/LUCIDE_LICENSE.txt').read_text():
        raise ValueError('UI kit icon license attribution differs from reviewed SDK')
    manifest = json.loads(read('manifest.json'))
    if not manifest.get('icon'):
        raise ValueError('UI kit example must supply an application identity icon')
    return {
        'schema':'tavix.ui-conformance/v1',
        'applicationId':lock['applicationId'],
        'version':lock['version'],
        'uiKit':'tavix.ui-kit/v1',
        'kitDirectory':str(prefix),
        'sourceIntegrity':'passed',
        'offlineKitBytes':'matched',
        'nativeRendering':'not_tested',
        'hostPermissions':'not_tested',
        'operatorAcceptance':'pending'
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--kit-dir', default='ui/kit')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(check(args.package,args.kit_dir),sort_keys=True))
        return 0
    except (ValueError,OSError,KeyError,zipfile.BadZipFile,json.JSONDecodeError) as exc:
        print(f'TaviX UI conformance failed: {exc}',file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
