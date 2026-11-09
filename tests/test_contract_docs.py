"""Source-backed reference checks; not Tavi runtime/Structurizr acceptance."""
import json
import pathlib
import re
import tempfile
import unittest

from tools.tavix_package import pack, validate, validate_archive

ROOT = pathlib.Path(__file__).resolve().parents[1]
SDK = ROOT / "extensions/inc.thebigtree.tavi.atrium/1.0.5/ui/tavix-sdk.mjs"
CONTRACT = ROOT / "contracts/tavix-1.0.json"


class DocumentationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_contract_index_schema_and_versions(self):
        j = self.index
        self.assertEqual(j['schema'], 'tavix.documentation-contract/v1')
        self.assertEqual(j['documentationVersion'], '0.1.15')
        self.assertEqual(j['standard'], 'tavix/1.0')
        self.assertEqual(j['package']['manifestSchema'], 'tavi.extension/v1')
        self.assertEqual(j['package']['lockSchema'], 'tavix.package/v1')
        self.assertEqual(j['repository']['catalogSchema'], 'tavi.repository/v1')
        self.assertEqual(j['hostWire']['channel'], 'tavi.extension/v1')
        self.assertFalse(j['hostWire']['productionHostInLocalClient'])

    def test_paths_and_readme_are_discoverable(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        index = (ROOT / 'docs/INDEX.adoc').read_text(encoding='utf-8')
        for path in self.index['references'].values():
            self.assertTrue((ROOT / path).exists(), f'Missing referenced document: {path}')
        for name in ('docs/INDEX.adoc','docs/TAVIX_CONTRACT.adoc',
                     'docs/TAVIX_PACKAGE_FORMAT.adoc','docs/DEVELOPER_GUIDE.adoc',
                     'contracts/tavix-1.0.json','docs/TAVIX_CLASSIFICATION.adoc',
                     'contracts/tavix-classification-v1.schema.json',
                     'contracts/tavix-installed-games-v1.json'):
            self.assertIn(name, readme)
            self.assertIn(name, agents)
        self.assertIn('raw.githubusercontent.com/TheBigTreeInc/tavix/main/', index)
        self.assertIn('source locations', index)

    def test_sdk_wire_constants_and_exact_method_inventory(self):
        sdk = SDK.read_text(encoding='utf-8')
        self.assertIn("TAVIX_STANDARD='tavix/1.0'", sdk)
        self.assertIn("TAVIX_CHANNEL='tavi.extension/v1'", sdk)
        self.assertIn("TAVIX_HOST_API='1.0.0'", sdk)
        methods = set(re.findall(r"(?:request|call)\('([^']+)'", sdk))
        self.assertEqual(methods, set(self.index['hostWire']['observedSdkMethods']),
                         'SDK wrapper changes require updating the developer contract')
        missing = set(self.index['hostWire']['neverAssumeAvailable']) - methods
        self.assertFalse(missing)

    def test_package_rules_match_python_source(self):
        from tools import tavix_package as package
        from tools.local_client import local_packages
        from tools import repository
        j = self.index
        self.assertEqual(package.STANDARD, j['standard'])
        self.assertEqual(package.LOCK_SCHEMA, j['package']['lockSchema'])
        self.assertEqual(set(package.ALLOWED_EXT), set(j['package']['allowedArchiveFileExtensions']))
        self.assertEqual(local_packages.MAX_ARCHIVE, j['package']['maxLocalUploadBytes'])
        self.assertEqual(local_packages.MAX_TOTAL, j['package']['maxLocalExtractionBytes'])
        self.assertEqual(repository.INDEX, j['repository']['catalogFile'])
        self.assertEqual(package.validate.__name__, 'validate')
        # Intentional guard: the 1 MiB/file policy is source-level, not exposed as a constant.
        self.assertIn('size>1_000_000', pathlib.Path(package.__file__).read_text())
        self.assertEqual(j['package']['maxFileSizeBytes'], 1_000_000)

    def test_example_is_valid_complete_and_packable(self):
        source = ROOT / 'examples/hello-tavix'
        lock = validate(source)
        self.assertEqual(lock['applicationId'], 'example.org.hello')
        self.assertEqual(lock['version'], '0.1.0')
        self.assertEqual({f['path'] for f in lock['files']},
                         {'manifest.json','ui/index.html','ui/style.css','ui/main.js'})
        with tempfile.TemporaryDirectory() as tmp:
            archive = pathlib.Path(tmp) / 'hello.tavix'
            pack(source, archive)
            self.assertEqual(validate_archive(archive), lock)

    def test_html_asset_links_exist(self):
        html = (ROOT / 'examples/hello-tavix/ui/index.html').read_text()
        self.assertIn('href="style.css"', html)
        self.assertIn('src="main.js"', html)
        self.assertTrue((ROOT / 'examples/hello-tavix/ui/style.css').is_file())
        self.assertTrue((ROOT / 'examples/hello-tavix/ui/main.js').is_file())

    def test_version_metadata_and_approval_gates(self):
        for f in ('project.zr','tavix.zr','.ziprunner-post-update-tests.json',
                  '.ziprunner-workboard-update.json'):
            self.assertEqual(json.loads((ROOT / f).read_text())['version'], '0.1.15', f)
        z=json.loads((ROOT / 'project.zr').read_text())
        self.assertIn('ziprunner.config.json', z['protected_paths'])
        self.assertEqual(z['post_build_mechanisms'], [])
        self.assertFalse(z['delete_missing'])


if __name__ == '__main__':
    unittest.main()
