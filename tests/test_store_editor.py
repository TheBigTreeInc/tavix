"""Store Editor is a private package example, not a public publishing authority."""
import pathlib
import tempfile
import unittest
from tools.tavix_package import validate, pack, validate_archive
ROOT=pathlib.Path(__file__).resolve().parents[1]

class StoreEditorTests(unittest.TestCase):
    def test_complete_pack_and_archive(self):
        example=ROOT/'examples/store-editor'
        lock=validate(example)
        self.assertEqual(lock['applicationId'],'example.org.tavix-store-editor')
        self.assertEqual(lock['version'],'0.1.1')
        paths={item['path'] for item in lock['files']}
        for name in ['ui/index.html','ui/editor.js','ui/zip.js','ui/style.css','ui/icon.svg','ui/sample-icon.png','ui/sample-cover.webp']:
            self.assertIn(name,paths)
        with tempfile.TemporaryDirectory() as folder:
            out=pathlib.Path(folder)/'store-editor.tavix'
            pack(example,out)
            self.assertEqual(validate_archive(out),lock)

    def test_preview_and_publisher_boundary(self):
        example=ROOT/'examples/store-editor/ui'
        html=(example/'index.html').read_text(encoding='utf-8')
        js=(example/'editor.js').read_text(encoding='utf-8')
        zip_source=(example/'zip.js').read_text(encoding='utf-8')
        self.assertIn('Current Store',html)
        self.assertIn('Rich concept',html)
        self.assertIn('readonly',html)
        self.assertIn('not editable',html.lower())
        self.assertIn('draft_only_not_published',js)
        self.assertIn('newerVersion(values.version,state.importedVersion)',js)
        self.assertIn('TaviXZip.check',js)
        self.assertIn("'tavix.package/v1'",zip_source)
        for source in (js,zip_source):
            for bad in ('fetch(', 'XMLHttpRequest', 'localStorage.setItem(', 'window.opener', 'eval('):
                self.assertNotIn(bad,source)

    def test_utf8_source_reads_are_platform_independent(self):
        """Windows uses CP1252 by default; always specify UTF-8 for source files."""
        import ast
        tree=ast.parse(pathlib.Path(__file__).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr=='read_text':
                self.assertTrue(
                    any(k.arg=='encoding' for k in node.keywords) or bool(node.args),
                    f'Implicit platform encoding at line {node.lineno}'
                )

    def test_docs_and_no_host_api_change(self):
        doc=(ROOT/'docs/TAVIX_STORE_EDITOR_001.adoc').read_text(encoding='utf-8')
        self.assertIn('preview-only',doc)
        self.assertIn('publisher',doc.lower())
        self.assertIn('Gold',doc)
        self.assertIn('examples/store-editor', (ROOT/'README.md').read_text(encoding='utf-8'))
