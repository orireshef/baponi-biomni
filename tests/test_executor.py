from __future__ import annotations

from baponi_biomni import BaponiExecutor
from baponi_biomni.errors import RNotSupportedError

import pytest


def test_python_wraps_user_code(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    ex.python("print('hi')")
    assert len(fake_baponi.calls) == 1
    code = fake_baponi.calls[0]["code"]
    assert "_biomni_ns.pkl" in code
    assert "matplotlib" in code
    assert "print('hi')" in code
    assert fake_baponi.calls[0]["language"] == "python"


def test_python_strips_fences(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    ex.python("```python\nprint('a')\n```")
    code = fake_baponi.calls[0]["code"]
    assert "```" not in code
    assert "print('a')" in code


def test_bash_passthrough(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    fake_baponi.add_handler(lambda c, l, t: ("done", "", 0) if l == "bash" else None)
    out = ex.bash("ls /tmp")
    assert out == "done"
    assert fake_baponi.calls[0]["language"] == "bash"
    assert fake_baponi.calls[0]["code"] == "ls /tmp"


def test_cli_routes_through_bash(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    ex.cli("echo hi")
    assert fake_baponi.calls[0]["language"] == "bash"


def test_r_raises(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    with pytest.raises(RNotSupportedError):
        ex.r("x <- 1")


def test_failure_returns_error_string(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    fake_baponi.add_handler(lambda c, l, t: ("", "boom", 1))
    out = ex.python("raise RuntimeError('x')")
    assert out.startswith("Error")
    assert "boom" in out


def test_thread_id_stable_across_calls(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    ex.python("a = 1")
    ex.python("b = 2")
    tids = {c["thread_id"] for c in fake_baponi.calls}
    assert len(tids) == 1
    assert next(iter(tids)).startswith("biomni-")


def test_explicit_thread_id_used(fake_baponi, fake_biomni):
    ex = BaponiExecutor(thread_id="my-session")
    ex.python("x = 1")
    assert fake_baponi.calls[0]["thread_id"] == "my-session"


def test_env_vars_uppercased_and_passed(fake_baponi, fake_biomni):
    ex = BaponiExecutor(env_vars={"foo": "bar", "Baz": "qux"})
    ex.python("import os")
    env = fake_baponi.calls[0]["env_vars"]
    assert env == {"FOO": "bar", "BAZ": "qux"}


def test_python_bin_routes_through_bash(fake_baponi, fake_biomni):
    ex = BaponiExecutor(python_bin="/opt/conda/envs/biomni/bin/python")
    ex.python("print('hi')")
    assert len(fake_baponi.calls) == 1
    call = fake_baponi.calls[0]
    assert call["language"] == "bash"
    code = call["code"]
    # Heredoc preserves the wrapped python source
    assert "print('hi')" in code
    assert "_biomni_ns.pkl" in code
    # Bash invokes the explicit interpreter
    assert "/opt/conda/envs/biomni/bin/python" in code


def test_python_bin_from_env(fake_baponi, fake_biomni, monkeypatch):
    monkeypatch.setenv("BAPONI_PYTHON_BIN", "/opt/conda/envs/biomni/bin/python")
    ex = BaponiExecutor()
    ex.python("x = 1")
    assert fake_baponi.calls[0]["language"] == "bash"
    assert "/opt/conda/envs/biomni/bin/python" in fake_baponi.calls[0]["code"]


def test_python_bin_unset_uses_python_language(fake_baponi, fake_biomni):
    ex = BaponiExecutor()
    ex.python("x = 1")
    assert fake_baponi.calls[0]["language"] == "python"
