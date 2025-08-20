import importlib
import builtins
from unittest import mock


def test_main_import_error_branch():
    # Simule une ImportError pour un sous-module lors du rechargement de app.main
    import app.main as main
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "app.api.v1" and fromlist and "auth" in fromlist:
            # Provoque l'échec sur 'from app.api.v1 import auth, ...'
            raise ImportError("boom")
        return orig_import(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=fake_import):
        importlib.reload(main)
        assert hasattr(main, "app")
