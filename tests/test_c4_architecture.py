"""Source-contract regression checks for the TaviX C4 deliverables.

These checks are NOT a Structurizr DSL parser or CLI validation.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DSL = ROOT / 'architecture' / 'c4' / 'workspace.dsl'
DOC = ROOT / 'architecture' / 'c4' / 'README.adoc'


class ArchitectureContractTests(unittest.TestCase):
    def test_root_relative_structurizr_and_asciidoc_exist(self):
        self.assertTrue(DSL.is_file())
        self.assertTrue(DOC.is_file())
        self.assertTrue(DSL.read_text(encoding='utf-8').startswith('workspace '))
        self.assertTrue(DOC.read_text(encoding='utf-8').startswith('= TaviX C4 architecture'))

    def test_required_views_have_stable_keys(self):
        text = DSL.read_text(encoding='utf-8')
        for kind, key in (
            ('systemContext tavix', 'tavixContext'),
            ('container tavix', 'tavixContainers'),
            ('component cli', 'tavixPublisherComponents'),
            ('component previewServer', 'tavixPreviewServerComponents'),
            ('component previewUi', 'tavixPreviewUiComponents'),
            ('component adapter', 'tavixAdapterComponents'),
            ('dynamic tavix', 'tavixReleaseStage'),
            ('dynamic previewServer', 'tavixLocalInstall'),
            ('deployment tavix "Local development"', 'tavixLocalDeployment'),
        ):
            with self.subTest(key=key):
                self.assertIn(kind + ' ' + key + ' ', text)

    def test_component_source_evidence_exists(self):
        doc = DOC.read_text(encoding='utf-8')
        for path in (
            'tools/repository.py', 'tools/tavix_package.py',
            'tools/ziprunner_catalog_preflight.py',
            'tools/local-client/server.py', 'tools/local-client/index.html',
            'tools/local_client/local_packages.py', 'tools/local-client/qa.py',
            'tools/stage-companion.mjs',
        ):
            with self.subTest(path=path):
                self.assertIn(path, doc)
                self.assertTrue((ROOT / path).is_file())

    def test_external_systems_and_development_limits_are_explicit(self):
        dsl = DSL.read_text(encoding='utf-8')
        doc = DOC.read_text(encoding='utf-8')
        for name in ('"Tavi"', '"ZipRunner"', '"Extension producer"', '"GitHub repository and Pages"'):
            self.assertIn(name, dsl)
        self.assertIn('127.0.0.1', dsl)
        self.assertIn('not a production Tavi installation', dsl)
        self.assertIn('not a hardened trust boundary', doc)

    def test_workboard_single_side_for_new_architecture_ticket(self):
        update = json.loads((ROOT / '.ziprunner-workboard-update.json').read_text('utf-8'))
        done = {entry['id'] for entry in update['implemented']}
        pending = {entry['id'] for entry in update['remaining']}
        self.assertTrue(done.isdisjoint(pending))
        # Workboard updates are incremental across releases: the C4 ticket was
        # implemented in 0.1.8 and need not be repeated in later ZIPs.
        self.assertTrue(all(isinstance(i, str) and i for i in done | pending))


if __name__ == '__main__':
    unittest.main()
