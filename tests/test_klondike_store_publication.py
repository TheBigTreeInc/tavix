"""Exact-package Klondike catalog staging contract; does not grant publication approval."""
import hashlib
import json
from pathlib import Path
import unittest
from tools.tavix_package import validate_archive
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from repository import build_index, validate_release

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.1'
APP='inc.thebigtree.tavi.klondike'
RELEASE=ROOT/'extensions'/APP/VERSION
EXPECTED='da4ecd43299c0f05e49beebc5a51fed7146325be8b54b663ac2327103025be92'

class KlondikePublicStoreCandidateTests(unittest.TestCase):
    def test_archive_is_exact_reviewed_compiled_build(self):
        archive=RELEASE/f'{APP}-{VERSION}.tavix'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),EXPECTED)
        lock=validate_archive(archive)
        self.assertEqual(lock['applicationId'],APP)
        self.assertEqual(lock['version'],VERSION)
        manifest,info,actual_archive=validate_release(RELEASE)
        self.assertEqual(actual_archive,archive)
        self.assertEqual(manifest['classification'],{'type':'game','categories':['cards','solitaire']})
        self.assertEqual(set(manifest['platforms']),{'android','windows','web'})
        self.assertEqual(manifest['publisher'],'thebigtreeinc')
        self.assertNotIn('assetDependencies', manifest)
        self.assertNotIn('assets.read', manifest['permissions'])
        self.assertEqual(info['license'],'NOASSERTION')
        self.assertEqual(info['source'],'https://github.com/TheBigTreeInc/tavix')

    def test_icon_store_art_and_offline_permissions(self):
        manifest=json.loads((RELEASE/'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['icon'],'ui/icon.png')
        self.assertTrue((RELEASE/manifest['icon']).is_file())
        self.assertGreater((RELEASE/manifest['icon']).stat().st_size,30000)
        for name in ('store/cover.webp','store/screenshot-android-portrait.webp','store/screenshot-android-landscape.webp','store/screenshot-desktop.webp'):
            self.assertTrue((RELEASE/name).is_file())
        self.assertEqual(set(manifest['permissions']),{'ui.panel','storage.private'})
        self.assertEqual(manifest['entrypoints']['panel'],'ui/index.html')

    def test_public_catalog_candidate_is_canonical_and_two_original_apps_retained(self):
        self.assertFalse((ROOT/'extensions/example.org.klondike/0.1.1').exists(),
                         'Unapproved legacy draft remains; run guarded Klondike archive preflight')
        raw=build_index(ROOT)
        self.assertEqual((ROOT/'tavi.repository.json').read_bytes(),raw)
        data=json.loads(raw)
        entries={e['manifest']['id']:e for e in data['extensions']}
        self.assertEqual(set(entries),{'inc.thebigtree.tavi.atrium','org.tavi.community.companion',APP})
        e=entries[APP]
        self.assertTrue(e['entrypoint'].startswith('https://thebigtreeinc.github.io/tavix/extensions/'))
        self.assertEqual(e['release']['revision'],EXPECTED)
        self.assertIn('android',e['manifest']['platforms'])
        self.assertEqual(e['manifest']['classification']['type'],'game')

    def test_publisher_permission_and_publication_gates_are_documented(self):
        doc=(ROOT/'docs/KLONDIKE_STORE_DISCOVERY_0120.adoc').read_text(encoding='utf-8')
        self.assertIn('operator explicitly confirmed',doc)
        self.assertIn('NOASSERTION',doc)
        self.assertIn('before installing Klondike',doc)
        self.assertIn('No Git push or public release is authorized', (ROOT/'ZIPRUNNER_HANDOFF.md').read_text(encoding='utf-8'))
