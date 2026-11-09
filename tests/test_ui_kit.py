"""Offline UI kit source consistency, exact archive fixture, source-only evidence."""
import json
import pathlib
import tempfile
import unittest

from tools.tavix_package import pack,validate,validate_archive

ROOT=pathlib.Path(__file__).resolve().parents[1]

class UIKitContractTests(unittest.TestCase):
    def test_complete_local_pack_and_schema(self):
        p=ROOT/'examples/ui-kit'
        lock=validate(p)
        self.assertEqual(lock['applicationId'],'example.org.tavi-ui-kit')
        with tempfile.TemporaryDirectory() as tmp:
            out=pathlib.Path(tmp)/'ui-kit.tavix';pack(p,out)
            self.assertEqual(validate_archive(out),lock)
        files={i['path'] for i in lock['files']}
        self.assertIn('ui/kit/icons.js',files)
        self.assertIn('ui/kit/icon-shapes.js',files)
        self.assertIn('ui/kit/ui.css',files)
        self.assertIn('ui/kit/LUCIDE_LICENSE.json',files)
        self.assertIn('ui/icon.svg',files)

    def test_kit_bytes_match_self_contained_reference_and_catalog(self):
        d=json.loads((ROOT/'contracts/tavix-ui-kit-v1.json').read_text())
        self.assertEqual(d['schema'],'tavix.ui-kit/v1')
        self.assertEqual(d['icons']['schema'],'tavix.icons/v1')
        self.assertEqual(len(d['icons']['names']),50)
        self.assertFalse(d['deployment']['requiresNewPermissions'])
        self.assertFalse(d['typography']['fontFilesBundled'])
        for filename in ['icons.js','icon-shapes.js','ui.css','ui.js']:
            self.assertEqual((ROOT/'sdk/ui-kit'/filename).read_bytes(),(ROOT/'examples/ui-kit/ui/kit'/filename).read_bytes(), filename)
        self.assertEqual(json.loads((ROOT/'examples/ui-kit/ui/kit/LUCIDE_LICENSE.json').read_text())['licenseText'],(ROOT/'sdk/ui-kit/LUCIDE_LICENSE.txt').read_text())

    def test_no_cdn_or_embedded_host_privilege(self):
        css=(ROOT/'sdk/ui-kit/ui.css').read_text()
        js=(ROOT/'sdk/ui-kit/icons.js').read_text()
        self.assertIn('Segoe UI',css)
        self.assertIn('Roboto',css)
        self.assertNotIn('@font-face',css)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('localStorage',js)
        self.assertNotIn('window.opener',js)

    def test_reference_sdk_keeps_local_file_import_and_adds_readonly_ui(self):
        s=(ROOT/'sdk/tavix-sdk.mjs').read_text()
        for method in ['workspace.info','ui.info','files.local.pick','files.local.read']:
            self.assertIn("'"+method+"'",s)
        index=json.loads((ROOT/'contracts/tavix-1.0.json').read_text())
        self.assertEqual(index['documentationVersion'],'0.1.15')
        self.assertEqual(index['uiKit']['schema'],'tavix.ui-kit/v1')
