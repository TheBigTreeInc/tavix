"""Regression for the Windows 0.1.33 PatternFly 6 TS2322 compiler failure.

Source assertion complements (does not replace) actual Windows tsc --noEmit,
Vite and Tauri build. A source test must never claim compiled-binary proof.
"""
import json
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools'/'studio-desktop'
TITLE_TAG=re.compile(r'<Title\b[^>]*>', re.MULTILINE)
SIZE_ATTR=re.compile(r'\bsize="([^"]+)"')
ALLOWED={'md','lg','xl','2xl','3xl','4xl'}

class PatternFlyTitleBuild034(unittest.TestCase):
    def test_all_patternfly_title_sizes_are_supported(self):
        src=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        sizes=[]
        for title in TITLE_TAG.findall(src):
            m=SIZE_ATTR.search(title)
            if m:
                sizes.append(m.group(1))
                self.assertIn(m.group(1),ALLOWED,title)
        self.assertTrue(sizes or '<h1 className="studio-header-title">' in src,
                        'No validated PatternFly Title or semantic masthead h1')
        blueprint_src=(STUDIO/'src/blueprint-library.tsx').read_text(encoding='utf-8')
        for title in TITLE_TAG.findall(blueprint_src):
            m=SIZE_ATTR.search(title)
            if m: self.assertIn(m.group(1),ALLOWED,title)
        self.assertIn('<Title headingLevel="h3" size="md">Designer checklist</Title>',blueprint_src)
        self.assertNotIn('<Title headingLevel="h3" size="sm">Designer checklist</Title>',src)

    def test_native_build_preserves_typescript_check(self):
        pkg=json.loads((STUDIO/'package.json').read_text(encoding='utf-8'))
        self.assertEqual(pkg['scripts']['build'],'tsc --noEmit && vite build')
        native=(STUDIO/'build_windows.py').read_text(encoding='utf-8')
        self.assertIn("'build', '--no-bundle'",native)
        self.assertIn("'npm'",native)

    def test_version_stamp_and_no_publishing(self):
        manifest=json.loads((ROOT/'ziprunner-manifest.json').read_text(encoding='utf-8'))
        stamp=json.loads((ROOT/'.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        workboard=json.loads((ROOT/'.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        self.assertEqual((manifest['project']['version'],manifest['project']['base_version']),('0.1.60','0.1.58'))
        self.assertEqual(stamp['version'], '0.1.60')
        self.assertLessEqual(len(stamp['tests']),20)
        self.assertEqual(workboard['version'],'0.1.60')
        self.assertIn('No Git push or public release is authorized',(ROOT/'ZIPRUNNER_HANDOFF.md').read_text(encoding='utf-8'))
        src=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn('<Button isDisabled>Publish to official store — integration pending</Button>',src)

if __name__=='__main__': unittest.main()
