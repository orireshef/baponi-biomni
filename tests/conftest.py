from __future__ import annotations

import sys
import types
from typing import Any

import pytest


class _FakeFileEntry:
    def __init__(self, path: str, size: int = 0, modified: str | None = None) -> None:
        self.path = path
        self.size = size
        self.modified = modified


class _FakeSignedUrl:
    def __init__(self, url: str) -> None:
        self.url = url
        self.method = "GET"
        self.headers: list[Any] = []
        self.expires_at = "2099-01-01T00:00:00Z"


class _FakeSandboxResult:
    def __init__(
        self,
        *,
        success: bool = True,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        error: str | None = None,
    ) -> None:
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.error = error


class FakeBaponi:
    """In-memory baponi client for tests. Stateful per thread_id."""

    def __init__(self, *_a, **_k) -> None:
        self.calls: list[dict[str, Any]] = []
        self._files: dict[str, dict[str, bytes]] = {}
        self._handlers: list = []

    def add_handler(self, fn) -> None:
        """fn(code, language, thread_id) -> (stdout, stderr, exit_code) or None to fall through."""
        self._handlers.append(fn)

    def execute(self, code, *, language="python", timeout=30, thread_id=None,
                metadata=None, sub_paths=None, env_vars=None) -> _FakeSandboxResult:
        self.calls.append({
            "code": code, "language": language, "thread_id": thread_id,
            "env_vars": env_vars,
        })
        for h in self._handlers:
            r = h(code, language, thread_id)
            if r is not None:
                stdout, stderr, exit_code = r
                return _FakeSandboxResult(
                    success=exit_code == 0,
                    stdout=stdout, stderr=stderr, exit_code=exit_code,
                )
        return _FakeSandboxResult(stdout="", stderr="", exit_code=0)

    def add_file(self, thread_id: str, path: str, content: bytes) -> None:
        self._files.setdefault(thread_id, {})[path] = content

    def list_files(self, *, source="thread", id, path=None):
        """Mirrors real baponi: returns paths RELATIVE to the `path` arg."""
        files = self._files.get(id, {})
        prefix = (path or "").lstrip("/").rstrip("/")
        out = []
        for full in files:
            if not prefix:
                out.append(_FakeFileEntry(path=full, size=len(files[full])))
            elif full == prefix:
                continue
            elif full.startswith(prefix + "/"):
                rel = full[len(prefix) + 1:]
                out.append(_FakeFileEntry(path=rel, size=len(files[full])))
        return out

    def download_url(self, *, path, source="thread", id):
        return _FakeSignedUrl(url=f"http://fake-storage/{id}/{path}")


@pytest.fixture(autouse=True)
def _clear_baponi_env(monkeypatch):
    """Tests should not inherit BAPONI_* env vars from the developer's
    shell or .env file. Each test gets a clean slate; opt-in via
    `monkeypatch.setenv` when a test exercises an env-driven code path."""
    for var in ("BAPONI_PYTHON_BIN", "BAPONI_BASE_URL", "BAPONI_API_KEY"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def fake_baponi(monkeypatch):
    fake = FakeBaponi()
    import baponi_biomni.executor as ex_mod
    monkeypatch.setattr(ex_mod, "Baponi", lambda *a, **k: fake)
    return fake


@pytest.fixture
def fake_httpx(monkeypatch, fake_baponi):
    """Route httpx.get to FakeBaponi's _files store."""
    class _Resp:
        def __init__(self, content: bytes) -> None:
            self.content = content
        def raise_for_status(self) -> None:
            pass

    def _get(url, headers=None, timeout=None):
        # url format: http://fake-storage/<thread>/<path>
        _, _, _, thread, *rest = url.split("/", 4)
        path = rest[0] if rest else ""
        content = fake_baponi._files.get(thread, {}).get(path, b"")
        return _Resp(content)

    import baponi_biomni.executor as ex_mod
    monkeypatch.setattr(ex_mod.httpx, "get", _get)
    return _get


@pytest.fixture
def fake_biomni(monkeypatch):
    """Inject a stub biomni.tool.support_tools so executor._sync_plots can write plots."""
    biomni_pkg = types.ModuleType("biomni")
    tool_pkg = types.ModuleType("biomni.tool")
    support = types.ModuleType("biomni.tool.support_tools")
    support._captured_plots = []
    support._persistent_namespace = {}
    biomni_pkg.tool = tool_pkg
    tool_pkg.support_tools = support
    monkeypatch.setitem(sys.modules, "biomni", biomni_pkg)
    monkeypatch.setitem(sys.modules, "biomni.tool", tool_pkg)
    monkeypatch.setitem(sys.modules, "biomni.tool.support_tools", support)
    return support
