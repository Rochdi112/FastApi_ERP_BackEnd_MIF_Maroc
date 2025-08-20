import importlib
import pkgutil
import types
import inspect


def test_smoke_import_models_and_schemas_and_basic_instances():
    # Import all app.models.* and app.schemas.* modules
    for pkg_name in ("app.models", "app.schemas"):
        pkg = importlib.import_module(pkg_name)
        for mod in pkgutil.iter_modules(pkg.__path__, pkg_name + "."):
            module = importlib.import_module(mod.name)
            assert isinstance(module, types.ModuleType)

    # Try constructing simple Enums and minimal pydantic schemas where available
    # UserRole Enum
    from app.schemas.user import UserRole, UserCreate
    assert UserRole.admin.value == "admin"

    # Minimal schema instance
    uc = UserCreate(username="u1", full_name="U One", email="u1@example.com", role="client", password="x")
    assert uc.email == "u1@example.com"
