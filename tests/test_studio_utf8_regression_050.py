"""Windows UTF-8 regression and bounded historical source-read debt.

0.1.49: CP1252 decoding of the UTF-8 Studio renderer failed.
0.1.50: global no-implicit-read assertion failed on 25 pre-existing sites in
seven legacy Python test files not included in the Studio incremental overlay.
Keep Studio hard-gated and track the exact older debt without overwriting user
checkout files with stale GitHub versions or silently accepting new violations.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Exact seven existing legacy files and call counts seen in Windows 0.1.50 QA.
# These are allowed ceilings, not permissions for new use in other files.
# Remove a baseline entry once its entire legacy file has been migrated.
LEGACY_READ_TEXT_DEBT = {
    'test_asset_dependencies.py': 6,
    'test_c4_architecture.py': 1,
    'test_game_completion_contract.py': 2,
    'test_local_file_import.py': 4,
    'test_registry_admin.py': 3,
    'test_repository.py': 2,
    'test_ui_kit.py': 7,
}


def unqualified_reads(text, filename):
    """Return source line numbers of read_text() calls without encoding."""
    tree = ast.parse(text, filename=filename)
    return sorted(node.lineno for node in ast.walk(tree)
                  if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Attribute)
                  and node.func.attr == 'read_text'
                  and not any(k.arg == 'encoding' for k in node.keywords))


def violating_files(file_to_text):
    """Fail any new file or increase past a known legacy call-count ceiling."""
    bad = []
    for filename, text in sorted(file_to_text.items()):
        read_lines = unqualified_reads(text, filename)
        allowance = LEGACY_READ_TEXT_DEBT.get(filename, 0)
        if len(read_lines) > allowance:
            bad.append((filename, read_lines, allowance))
    return bad


class WindowsSourceEncoding050(unittest.TestCase):
    def test_actual_studio_source_reproduces_cp1252_failure_and_reads_utf8(self):
        raw = (ROOT / 'tools/studio-desktop/src/main.tsx').read_bytes()
        with self.assertRaises(UnicodeDecodeError):
            raw.decode('cp1252')
        ui = raw.decode('utf-8')
        self.assertIn("invoke<Snapshot>('workspace_snapshot')", ui)
        self.assertIn("const STUDIO_UI_VERSION = '0.1.60'", ui)

    def test_no_new_unqualified_source_read_text_in_python_tests(self):
        contents = {p.name: p.read_text(encoding='utf-8')
                    for p in (ROOT / 'tests').glob('test_*.py')}
        violations = violating_files(contents)
        self.assertEqual(violations, [],
                         'new implicit code-page source reads: ' + repr(violations))

    def test_legacy_allowances_are_exact_bounded_and_studio_is_unexempt(self):
        self.assertEqual(sum(LEGACY_READ_TEXT_DEBT.values()), 25)
        self.assertNotIn('test_native_studio_028.py', LEGACY_READ_TEXT_DEBT)
        self.assertFalse(any('studio' in p for p in LEGACY_READ_TEXT_DEBT))
        for name in LEGACY_READ_TEXT_DEBT:
            self.assertTrue(name.startswith('test_') and name.endswith('.py'))
        # A new file and an extra call in an existing legacy file both fail.
        self.assertTrue(violating_files({'test_new.py': 'x.read_text()'}))
        existing='\n'.join('x.read_text()' for _ in range(6))
        self.assertEqual(violating_files({'test_asset_dependencies.py': existing}), [])
        self.assertTrue(violating_files({'test_asset_dependencies.py': existing+'\nx.read_text()'}))
        self.assertTrue(violating_files({'test_native_studio_028.py': 'x.read_text()'}))

    def test_explicit_utf8_is_not_counted(self):
        text='x.read_text(encoding="utf-8")\nx.read_text(encoding="utf-8")'
        self.assertEqual(unqualified_reads(text, 'test_fixture.py'), [])


if __name__ == '__main__':
    unittest.main()
