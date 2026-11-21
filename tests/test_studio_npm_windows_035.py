"""Windows native Studio npm recovery contract; no npm commands are actually executed."""
import importlib.util
import json
import tempfile
from pathlib import Path
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/studio-desktop/build_windows.py'

def module():
    spec=importlib.util.spec_from_file_location('studio_build_windows_035', SCRIPT)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

class NodeDependencyRecovery(unittest.TestCase):
    def setup_root(self, root):
        (root/'src-tauri/icons').mkdir(parents=True)
        (root/'src-tauri/icons/icon.ico').write_bytes(b'Z'*128)
        (root/'src-tauri/tauri.conf.json').write_text(json.dumps({'identifier':'inc.thebigtree.tavix.studio','version':'0.1.60'}))
        (root/'package.json').write_text(json.dumps({'version':'0.1.60'}))
        exe=root/'src-tauri/target/studio-managed-build/release/tavix-studio.exe'
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b'MZTEST')
        return exe

    def test_incomplete_populated_install_repairs_incrementally_not_npm_ci(self):
        build=module()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);exe=self.setup_root(root)
            (root/'node_modules').mkdir()
            (root/'package-lock.json').write_text('{}')
            with mock.patch.object(build,'STUDIO',root), mock.patch.object(build,'BIN',exe),mock.patch.object(build.sys,'platform','win32'),mock.patch.object(build,'command_executable',return_value='npm.cmd'),mock.patch.object(build,'_npm_install_healthy',side_effect=[False,True]),mock.patch.object(build.subprocess,'run') as run:
                self.assertEqual(build.build_native(),0)
                self.assertEqual(run.call_count,2)
                self.assertEqual(run.call_args_list[0].args[0][:2],['npm.cmd','install'])
                self.assertEqual(run.call_args_list[1].args[0][1:],['run','tauri','--','build','--no-bundle'])

    def test_healthy_install_is_not_reinstalled(self):
        build=module()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);exe=self.setup_root(root)
            with mock.patch.object(build,'STUDIO',root),mock.patch.object(build,'BIN',exe),mock.patch.object(build.sys,'platform','win32'),mock.patch.object(build,'command_executable',return_value='npm.cmd'),mock.patch.object(build,'_npm_install_healthy',return_value=True),mock.patch.object(build.subprocess,'run') as run:
                self.assertEqual(build.build_native(),0)
                self.assertEqual(run.call_count,1)
                self.assertEqual(run.call_args.args[0][1:3],['run','tauri'])

    def test_clean_tree_with_lock_uses_ci_once(self):
        build=module()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);exe=self.setup_root(root)
            (root/'package-lock.json').write_text('{}')
            with mock.patch.object(build,'STUDIO',root),mock.patch.object(build,'BIN',exe),mock.patch.object(build.sys,'platform','win32'),mock.patch.object(build,'command_executable',return_value='npm.cmd'),mock.patch.object(build,'_npm_install_healthy',side_effect=[False,True]),mock.patch.object(build.subprocess,'run') as run:
                self.assertEqual(build.build_native(),0)
                self.assertEqual(run.call_args_list[0].args[0][:2],['npm.cmd','ci'])

    def test_partial_install_that_cannot_recover_never_starts_tauri(self):
        build=module()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);exe=self.setup_root(root)
            (root/'node_modules').mkdir()
            with mock.patch.object(build,'STUDIO',root),mock.patch.object(build,'BIN',exe),mock.patch.object(build.sys,'platform','win32'),mock.patch.object(build,'command_executable',return_value='npm.cmd'),mock.patch.object(build,'_npm_install_healthy',return_value=False),mock.patch.object(build.subprocess,'run') as run:
                self.assertEqual(build.build_native(),1)
                self.assertEqual(run.call_count,1)

    def test_shims_and_local_npm_ls_required(self):
        build=module()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);shims=root/'node_modules/.bin';shims.mkdir(parents=True)
            with mock.patch.object(build,'STUDIO',root),mock.patch.object(build.subprocess,'run') as run:
                self.assertFalse(build._npm_install_healthy('npm.cmd'))
                run.assert_not_called()
                for tool in build.TOOLS:(shims/(tool+'.cmd')).write_text('stub')
                run.return_value.returncode=0
                self.assertTrue(build._npm_install_healthy('npm.cmd'))
                self.assertEqual(run.call_args.args[0],['npm.cmd','ls','--depth=0','--offline'])

    def test_mismatched_frontend_and_tauri_version_rejected_before_npm(self):
        build=module()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);exe=self.setup_root(root)
            (root/'package.json').write_text(json.dumps({'version':'0.1.36'}))
            with mock.patch.object(build,'STUDIO',root),mock.patch.object(build,'BIN',exe),mock.patch.object(build.sys,'platform','win32'),mock.patch.object(build,'command_executable',return_value='npm.cmd'),mock.patch.object(build.subprocess,'run') as run:
                self.assertEqual(build.build_native(),2)
                run.assert_not_called()

if __name__=='__main__': unittest.main()
