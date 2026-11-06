import importlib.util
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "tools/local-client/server.py"
spec = importlib.util.spec_from_file_location("tavix_local_client", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LocalClientTests(unittest.TestCase):
    def test_repository_discovery(self):
        apps = module.discover()
        self.assertTrue(any(a["id"] == "inc.thebigtree.tavi.atrium" and a["version"] == "1.0.5" for a in apps))

    def test_reject_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            version = root / "extensions" / "example" / "1.0.0"
            version.mkdir(parents=True)
            (root / "outside.html").write_text("x")
            (version / "manifest.json").write_text('{"id":"example","version":"1.0.0","entrypoints":{"panel":"../../../outside.html"}}')
            self.assertEqual(module.discover(root), [])
