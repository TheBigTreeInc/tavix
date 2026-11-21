"""Operator-only credentials; never write plaintext tokens or place them in TaviX packages.

Windows: DPAPI CurrentUser encryption, saved outside repository. Other systems:
use the OS keyring if installed; otherwise memory-only with an explicit persistence flag.
"""
import base64
import ctypes
import json
import os
from pathlib import Path


class SecretStore:
    def __init__(self, directory=None):
        self.directory = Path(directory or (Path.home() / '.tavix-suite'))
        self._memory = {}
        self._keyring = None
        if os.name != 'nt':
            try:
                import keyring
                # Do not persist through insecure/plaintext fallback keyring backends.
                backend = keyring.get_keyring()
                if not any(flag in type(backend).__module__.lower() for flag in ('plaintext', 'file', 'fail')) and 'fail' not in type(backend).__name__.lower():
                    self._keyring = keyring
            except (ImportError, RuntimeError):
                pass

    @property
    def persistent(self):
        return os.name == 'nt' or self._keyring is not None

    def put(self, name, value):
        if name not in ('github', 'looprd_read', 'looprd_ingest', 'looprd_publish'):
            raise ValueError('Unsupported secret name')
        if not isinstance(value, str) or len(value) < 16 or len(value) > 8192 or '\n' in value or '\r' in value:
            raise ValueError('Invalid credential format')
        if os.name == 'nt':
            saved = self._load_dpapi()
            saved[name] = value
            self._save_dpapi(saved)
        elif self._keyring:
            self._keyring.set_password('TaviX Management Suite', name, value)
        self._memory[name] = value

    def get(self, name):
        if name in self._memory:
            return self._memory[name]
        if os.name == 'nt':
            return self._load_dpapi().get(name)
        if self._keyring:
            return self._keyring.get_password('TaviX Management Suite', name)
        return None

    def forget(self, name):
        self._memory.pop(name, None)
        if os.name == 'nt':
            saved = self._load_dpapi()
            saved.pop(name, None)
            self._save_dpapi(saved)
        elif self._keyring:
            try:
                self._keyring.delete_password('TaviX Management Suite', name)
            except Exception:
                pass

    @staticmethod
    def _crypt(data, decrypt=False):
        import ctypes.wintypes
        class Blob(ctypes.Structure):
            _fields_ = [('cbData', ctypes.wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_ubyte))]
        buf = ctypes.create_string_buffer(data)
        incoming = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
        output = Blob()
        crypt = ctypes.windll.crypt32
        fn = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
        fn.restype = ctypes.wintypes.BOOL
        # CRYPTPROTECT_UI_FORBIDDEN: never allow untrusted WebView UI to prompt.
        if decrypt:
            ok = fn(ctypes.byref(incoming), None, None, None, None, 1, ctypes.byref(output))
        else:
            ok = fn(ctypes.byref(incoming), None, None, None, None, 1, ctypes.byref(output))
        if not ok:
            raise OSError('OS credential encryption failed')
        try:
            return ctypes.string_at(output.pbData, output.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(output.pbData)

    def _load_dpapi(self):
        file = self.directory / 'secrets.dpapi'
        if not file.exists():
            return {}
        return json.loads(self._crypt(base64.b64decode(file.read_bytes()), decrypt=True).decode('utf-8'))

    def _save_dpapi(self, values):
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        content = self._crypt(json.dumps(values, separators=(',', ':')).encode('utf-8'))
        file = self.directory / 'secrets.dpapi'
        tmp = self.directory / 'secrets.dpapi.tmp'
        tmp.write_bytes(base64.b64encode(content))
        os.chmod(tmp, 0o600)
        os.replace(tmp, file)
