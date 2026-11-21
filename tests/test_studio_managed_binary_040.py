"""0.1.40: immutable managed Windows Studio executable, no overwrite/kill."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT/'tools/studio-desktop'
sys.path.insert(0, str(STUDIO))
import studio_binary as binary


def load(name):
    spec=importlib.util.spec_from_file_location('tavix_040_'+name,STUDIO/name)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def source_fixture(root):
    paths = ['package.json', 'src/main.tsx', 'src-tauri/src/lib.rs',
             'src-tauri/src/review.rs', 'src-tauri/src/studio_connection.rs',
             'src-tauri/src/studio_publish.rs', 'studio_pack_catalog.py',
             'src/pack-browser.tsx', 'src/publishing-setup.tsx',
             'src-tauri/tauri.conf.json','src-tauri/Cargo.toml']
    for name in paths:
        p=root/name;p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({'version':'0.1.60','identifier':'inc.thebigtree.tavix.studio'}) if name == 'src-tauri/tauri.conf.json' else (json.dumps({'version':'0.1.60'}) if name.endswith('.json') else 'source fixture'), encoding='utf-8')
    return [root/n for n in paths]


class ManagedBinary040(unittest.TestCase):
    def test_build_output_and_versioned_launch_target_are_separate(self):
        build=load('build_windows.py')
        self.assertEqual(build.BIN, build.BUILD_TARGET/'release/tavix-studio.exe')
        self.assertNotEqual(build.BIN, STUDIO/'src-tauri/target/release/tavix-studio.exe')
        self.assertIn("'CARGO_TARGET_DIR': str(STUDIO / 'src-tauri' / 'target' / 'studio-managed-build')", (STUDIO/'build_windows.py').read_text(encoding='utf-8'))
        self.assertIn('studio_binary import StudioBinaryError, ready_binary', (STUDIO/'run_windows.py').read_text(encoding='utf-8'))
        self.assertIn('No Git push or public release is authorized', (ROOT/'ZIPRUNNER_HANDOFF.md').read_text(encoding='utf-8'))

    def test_content_addressed_launch_preserves_previous_running_copy(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sources=source_fixture(root)
            cargo=root/'src-tauri/target/studio-managed-build/release/tavix-studio.exe'
            cargo.parent.mkdir(parents=True)
            cargo.write_bytes(b'MZ-v1 original compiled executable')
            first=binary.stage_build(root,cargo,'0.1.60')
            self.assertEqual(binary.ready_binary(root,'0.1.60',sources),first)
            self.assertIn('/studio-launch/0.1.60/',first.as_posix())
            self.assertNotEqual(first,cargo)
            with first.open('rb') as old_open:
                cargo.write_bytes(b'MZ-v2 compiled executable bytes')
                second=binary.stage_build(root,cargo,'0.1.60')
                self.assertNotEqual(first,second)
                self.assertTrue(first.is_file())
                self.assertEqual(old_open.read(),b'MZ-v1 original compiled executable')
            self.assertEqual(binary.ready_binary(root,'0.1.60',sources),second)
            self.assertEqual(binary._hash(first),binary._hash(first))

    def test_wrong_version_tampered_hash_and_stale_source_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sources=source_fixture(root)
            cargo=root/'Cargo.exe';cargo.write_bytes(b'MZ - fixture')
            staged=binary.stage_build(root,cargo,'0.1.60')
            with self.assertRaisesRegex(binary.StudioBinaryError, 'current source'):
                binary.ready_binary(root,'0.1.40',sources)
            receipt=binary.runtime_root(root)/'current.json'
            obj=json.loads(receipt.read_text(encoding='utf-8'))
            obj['sha256']='../../evil'
            receipt.write_text(json.dumps(obj))
            with self.assertRaises(binary.StudioBinaryError):
                binary.ready_binary(root,'0.1.60',sources)
            binary.stage_build(root,cargo,'0.1.60')
            # A source overlay after compilation invalidates the receipt.
            newer=receipt.stat().st_mtime+30
            os.utime(sources[0],(newer,newer))
            with self.assertRaisesRegex(binary.StudioBinaryError, 'older than current source'):
                binary.ready_binary(root,'0.1.60',sources)
            self.assertTrue(staged.is_file())

    def test_compiled_copy_tamper_never_launched(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sources=source_fixture(root)
            cargo=root/'Cargo.exe';cargo.write_bytes(b'MZ - fixture')
            staged=binary.stage_build(root,cargo,'0.1.60')
            staged.write_bytes(b'MZ - changed')
            with self.assertRaisesRegex(binary.StudioBinaryError, 'executable bytes'):
                binary.ready_binary(root,'0.1.60',sources)
            with self.assertRaisesRegex(binary.StudioBinaryError, 'has changed'):
                binary.stage_build(root,cargo,'0.1.60')

    def test_managed_launcher_only_spawns_versioned_binary(self):
        launch=load('run_windows.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sources=source_fixture(root)
            cargo=root/'src-tauri/target/studio-managed-build/release/tavix-studio.exe'
            cargo.parent.mkdir(parents=True)
            cargo.write_bytes(b'MZ compiled target fixture')
            staged=binary.stage_build(root,cargo,'0.1.60')
            with mock.patch.object(launch,'STUDIO',root), mock.patch.object(launch,'ROOT',root), mock.patch.object(launch.sys,'platform','win32'), mock.patch.object(launch.subprocess,'call',return_value=0) as call:
                self.assertEqual(launch.main(),0)
                self.assertEqual(call.call_args.args[0],[str(staged)])
                self.assertNotEqual(str(staged),str(cargo))

    def test_builder_never_terminates_processes_and_does_not_rewrite_old_binary(self):
        build=load('build_windows.py')
        launch=(STUDIO/'run_windows.py').read_text(encoding='utf8')
        source=(STUDIO/'build_windows.py').read_text(encoding='utf8')
        for unsafe in ('os.kill(', 'subprocess.run(["taskkill"', 'TerminateProcess(', 'shutil.rmtree(', 'os.remove('):
            self.assertNotIn(unsafe, source+launch)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source_fixture(root)
            (root/'src-tauri/icons').mkdir(parents=True)
            (root/'src-tauri/icons/icon.ico').write_bytes(b'X'*128)
            with mock.patch.object(build,'STUDIO',root),mock.patch.object(build.sys,'platform','win32'),mock.patch.object(build,'command_executable',return_value='npm.cmd'),mock.patch.object(build,'_npm_install_healthy',return_value=True),mock.patch.object(build.subprocess,'run') as run:
                # No fake Cargo output: staged artifacts are not reported built.
                self.assertEqual(build.build_native(),1)
                self.assertEqual(run.call_count,1)
                env=run.call_args.kwargs['env']
                self.assertEqual(env['CARGO_TARGET_DIR'],str(root/'src-tauri/target/studio-managed-build'))
                self.assertNotIn('taskkill',str(run.call_args).lower())


if __name__=='__main__':unittest.main()
