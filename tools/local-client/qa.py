"""TaviX package boundary QA; never claims multiplayer or real host acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify(root, extension_id, version):
    root = Path(root).resolve()
    directory = root / 'extensions' / extension_id / version
    result = {'schema': 'tavix.exact-package-qa.v1', 'project': 'tavix', 'extension_id': extension_id, 'version': version, 'status': 'failed', 'checks': [], 'capabilities_not_tested': ['Tavi SDK', 'authentication', 'two-client multiplayer', 'game rules', 'native Tavi embedding']}
    def check(name, ok, detail=''):
        result['checks'].append({'name': name, 'passed': bool(ok), 'detail': str(detail)})
    try:
        if not directory.resolve().is_relative_to((root / 'extensions').resolve()):
            raise ValueError('extension path escapes repository')
        manifest_bytes = (directory / 'manifest.json').read_bytes()
        manifest = json.loads(manifest_bytes)
        check('manifest_identity', manifest.get('id') == extension_id and manifest.get('version') == version)
        result['manifest_sha256'] = sha256(manifest_bytes)
        panel = manifest.get('entrypoints', {}).get('panel')
        if not isinstance(panel, str) or not panel or '\\' in panel:
            raise ValueError('invalid panel entrypoint')
        target = (directory / panel).resolve()
        check('panel_containment', target.is_relative_to(directory.resolve()))
        check('panel_exists', target.is_file() and target.is_relative_to(directory.resolve()))
        packages = sorted(directory.glob('*.tavix'))
        check('exactly_one_archive', len(packages) == 1, len(packages))
        if len(packages) == 1:
            archive = packages[0]
            result['archive_sha256'] = sha256(archive.read_bytes())
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                check('archive_member_safety', all(not n.startswith('/') and '\\' not in n and '..' not in Path(n).parts for n in names))
                check('archive_crc', z.testzip() is None)
                check('archive_has_manifest', any(Path(n).name == 'manifest.json' for n in names))
                result['archive_members'] = len(names)
        result['status'] = 'passed' if all(c['passed'] for c in result['checks']) else 'failed'
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        check('verification_error', False, str(exc))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', default='.')
    parser.add_argument('--extension', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output')
    args = parser.parse_args()
    result = verify(args.repository, args.extension, args.version)
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(payload, encoding='utf-8')
    print(payload, end='')
    raise SystemExit(0 if result['status'] == 'passed' else 1)


if __name__ == '__main__':
    main()
