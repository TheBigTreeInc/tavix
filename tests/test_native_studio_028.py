"""0.1.28 read-only Tauri/PatternFly native Studio source boundary checks.

Static source tests cannot substitute for Cargo, npm, WebView2 or operator acceptance.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'tools' / 'studio-desktop'


class NativeStudioContract(unittest.TestCase):
    def test_project_metadata_and_docs(self):
        for name in ('project.zr', 'tavix.zr'):
            self.assertEqual(json.loads((ROOT / name).read_text(encoding='utf-8'))['version'], '0.1.60')
        self.assertEqual(json.loads((ROOT / '.ziprunner-workboard-update.json').read_text(encoding='utf-8'))['version'], '0.1.60')
        self.assertEqual(json.loads((ROOT / 'ziprunner-manifest.json').read_text(encoding='utf-8'))['project']['base_version'], '0.1.58')
        self.assertTrue((ROOT / 'docs/TAVIX_STUDIO_DESKTOP_028.adoc').is_file())
        for source in ('DESIGN.adoc', 'README.md', 'architecture/c4/workspace.dsl', 'architecture/c4/README.adoc'):
            self.assertIn('Studio', (ROOT / source).read_text(encoding='utf-8'))

    def test_ui_uses_patternfly_and_node_is_build_only(self):
        package = json.loads((STUDIO / 'package.json').read_text(encoding='utf-8'))
        self.assertTrue(package['dependencies']['@patternfly/react-core'].startswith('^6.'))
        self.assertTrue(package['dependencies']['@tauri-apps/api'].startswith('^2.'))
        self.assertNotIn('express', package['dependencies'])
        ui = (STUDIO / 'src/main.tsx').read_text(encoding='utf-8')
        for text in ('<Page ', '<PageSidebar ', '<Masthead>', 'Games & apps', 'Assets & objects', 'Official storefront', 'Connections', 'Operations', 'Events', "invoke<Snapshot>('workspace_snapshot')", "invoke<Event[]>('recent_events')"):
            self.assertIn(text, ui)
        self.assertNotIn('localhost:8765', ui)
        self.assertNotIn('localStorage', ui)

    def test_native_permissions_limit_operator_ipc_and_omit_network_plugins(self):
        conf = json.loads((STUDIO / 'src-tauri/tauri.conf.json').read_text(encoding='utf-8'))
        caps = json.loads((STUDIO / 'src-tauri/capabilities/default.json').read_text(encoding='utf-8'))
        self.assertEqual(conf['identifier'], 'inc.thebigtree.tavix.studio')
        self.assertEqual(caps['permissions'], ['core:default'])
        self.assertFalse(conf['bundle']['active'])
        self.assertNotIn('http://127.0.0.1:8765', str(conf))
        cargo = (STUDIO / 'src-tauri/Cargo.toml').read_text(encoding='utf-8')
        self.assertIn('tauri = { version = "2"', cargo)
        self.assertNotIn('tauri-plugin-shell', cargo)
        self.assertNotIn('tauri-plugin-http', cargo)
        self.assertNotIn('tauri-plugin-fs', cargo)
        rust = (STUDIO / 'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        self.assertEqual(rust.count('#[tauri::command]'), 2)
        self.assertIn('generate_handler![workspace_snapshot, recent_events, review::review_blueprints', rust)
        self.assertNotIn('git push', rust)
        self.assertNotIn('shell.execute', rust)
        self.assertNotIn('Command::new("python")', rust)
        self.assertNotIn('std::net::TcpListener', rust)

    def test_inventory_and_events_are_bounded(self):
        rust = (STUDIO / 'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        for marker in ('symlink_metadata()', 'm.len() <= 131072', 'results.len() >= 250', '.take(30)', 'meta.len() > 524288', '"project_key"', '"tavix"'):
            self.assertIn(marker, rust)
        self.assertIn('safe_text(&event, "at", 40)', rust)
        self.assertNotIn('safe_text(&event, "message"', rust)

    def test_old_local_console_remains_available(self):
        for file in ('tools/local-client/server.py', 'tools/local-client/manager.js', 'tools/local-client/index.html'):
            self.assertTrue((ROOT / file).is_file(), file)
        doc = (ROOT / 'docs/TAVIX_STUDIO_DESKTOP_028.adoc').read_text(encoding='utf-8')
        self.assertIn('Existing Python management console', doc)
        self.assertIn('NOT implemented in 0.1.28', doc)


if __name__ == '__main__':
    unittest.main()
