"""0.1.30 regression: native Studio Windows launch uses a real icon and managed path."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'tools' / 'studio-desktop'


def load_file(path):
    spec = importlib.util.spec_from_file_location('test_native_studio_runner', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StudioBootContract(unittest.TestCase):
    def test_windows_icon_is_valid_and_named_in_tauri_config(self):
        icons = STUDIO / 'src-tauri' / 'icons'
        ico = (icons / 'icon.ico').read_bytes()
        reserved, file_type, count = struct.unpack_from('<HHH', ico)
        self.assertEqual((reserved, file_type), (0, 1))
        self.assertGreaterEqual(count, 3)
        self.assertGreater(len(ico), 300)
        conf = json.loads((STUDIO / 'src-tauri' / 'tauri.conf.json').read_text(encoding='utf-8'))
        for item in conf['bundle']['icon']:
            self.assertTrue((STUDIO / 'src-tauri' / item).is_file())
        self.assertEqual(conf['version'], '0.1.60')
        self.assertEqual(json.loads((STUDIO / 'package.json').read_text(encoding='utf-8'))['version'], '0.1.60')
        self.assertIn('version = "0.1.60"', (STUDIO / 'src-tauri' / 'Cargo.toml').read_text(encoding='utf-8'))

    def test_ziprunner_build_and_managed_start_are_native(self):
        for filename in ('project.zr', 'tavix.zr'):
            config = json.loads((ROOT / filename).read_text(encoding='utf-8'))
            self.assertEqual(config['version'], '0.1.60')
            self.assertIn('python tools/studio-desktop/build_windows.py', config['build'])
            self.assertEqual(config['start'], ['python tools/studio-desktop/run_windows.py'])
            self.assertEqual(config['mechanisms_require_build_success'], True)
        self.assertNotIn('local-client/server.py', str(config['start']))
        self.assertIn('run_windows.py', (STUDIO / 'launch-windows.cmd').read_text(encoding='utf-8'))
        self.assertEqual(json.loads((ROOT / 'ziprunner-manifest.json').read_text(encoding='utf-8'))['project']['base_version'], '0.1.58')

    def test_no_duplicate_privileged_app_or_preview_ipc(self):
        rust = (STUDIO / 'src-tauri' / 'src/lib.rs').read_text(encoding='utf-8')
        self.assertEqual(rust.count('#[tauri::command]'), 2)
        # Other historical/independent tools may exist in an operator checkout;
        # this source must launch exactly one native Studio, not delete them.
        start = json.loads((ROOT / 'project.zr').read_text(encoding='utf-8'))['start']
        self.assertEqual(len(start), 1)
        self.assertNotIn('local-client', start[0])
        config = json.loads((STUDIO / 'src-tauri' / 'capabilities/default.json').read_text(encoding='utf-8'))
        self.assertEqual(config['permissions'], ['core:default'])
        for filename in ('tools/local-client/server.py', 'tools/local_client/manager.py'):
            self.assertTrue((ROOT / filename).exists())

    def test_missing_icon_fails_before_native_build(self):
        build = load_file(STUDIO / 'build_windows.py')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'src-tauri/icons').mkdir(parents=True)
            with mock.patch.object(build, 'STUDIO', root), mock.patch.object(build.sys, 'platform', 'win32'), mock.patch.object(build.subprocess, 'run') as run:
                self.assertEqual(build.build_native(), 2)
                run.assert_not_called()

    def test_launch_missing_binary_fails_without_spawning(self):
        launch = load_file(STUDIO / 'run_windows.py')
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(launch, 'EXE', Path(temp) / 'tavix-studio.exe'), mock.patch.object(launch.sys, 'platform', 'win32'), mock.patch.object(launch.subprocess, 'call') as call:
                self.assertEqual(launch.main(), 2)
                call.assert_not_called()

    def test_windows_build_uses_bounded_commands_and_local_binary(self):
        build = load_file(STUDIO / 'build_windows.py')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'src-tauri/icons').mkdir(parents=True)
            (root / 'src-tauri/icons/icon.ico').write_bytes(b'X'*200)
            (root / 'src-tauri/tauri.conf.json').write_text(json.dumps({'identifier': 'inc.thebigtree.tavix.studio'}))
            (root / 'package-lock.json').write_text('{}')
            (root / 'package.json').write_text(json.dumps({'version':'0.1.60'}))
            (root / 'src-tauri/tauri.conf.json').write_text(json.dumps({'identifier':'inc.thebigtree.tavix.studio','version':'0.1.60'}))
            exe = root / 'src-tauri/target/studio-managed-build/release/tavix-studio.exe'
            exe.parent.mkdir(parents=True);exe.write_bytes(b'MZTEST')
            with mock.patch.object(build, 'STUDIO', root), mock.patch.object(build, 'BIN', exe), mock.patch.object(build.sys, 'platform', 'win32'), mock.patch.object(build, 'command_executable', return_value='npm.cmd'), mock.patch.object(build, '_npm_install_healthy', side_effect=[False, True]), mock.patch.object(build.subprocess, 'run') as run:
                self.assertEqual(build.build_native(), 0)
                self.assertEqual(run.call_count, 2)
                self.assertEqual(run.call_args_list[0].args[0][:2], ['npm.cmd', 'ci'])
                self.assertEqual(run.call_args_list[1].args[0][1:], ['run','tauri','--','build','--no-bundle'])

    def test_stamp_still_at_20_entries_and_native_tests_covered(self):
        stamp = json.loads((ROOT / '.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        self.assertEqual(stamp['version'], '0.1.60')
        self.assertLessEqual(len(stamp['tests']), 20)
        commands = ' '.join(t['command'] for t in stamp['tests'])
        self.assertIn('test_native_studio_028.py', commands)
        self.assertIn('test_native_studio_boot_030.py', commands)
        self.assertIn('test_tavia_resource_diagnostics_027.py', commands)


if __name__ == '__main__':
    unittest.main()
