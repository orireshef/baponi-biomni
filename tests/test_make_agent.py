"""Tests for the make_agent forwarding layer.

A1 is mocked so these tests never touch real biomni state and don't
need an LLM provider configured.
"""
from __future__ import annotations

from typing import Any


class _FakeLLM:
    def __init__(self, *, max_tokens: int | None = 8192) -> None:
        self.max_tokens = max_tokens


class _FakeA1:
    last_kwargs: dict[str, Any] = {}

    def __init__(self, *, path: str, llm: str, **kwargs: Any) -> None:
        type(self).last_kwargs = {"path": path, "llm": llm, **kwargs}
        self.llm = _FakeLLM()


def _patch_biomni(monkeypatch):
    """Stub the bits of biomni that make_agent + apply_patches touch."""
    import sys
    import types

    utils = types.ModuleType("biomni.utils")
    utils.run_r_code = lambda c: f"r:{c}"
    utils.run_bash_script = lambda s: f"b:{s}"
    utils.run_cli_command = lambda c: f"cli:{c}"

    biomni_agent = types.ModuleType("biomni.agent")
    biomni_agent.A1 = _FakeA1
    biomni_a1 = types.ModuleType("biomni.agent.a1")
    biomni_agent.a1 = biomni_a1

    # biomni.tool.support_tools is supplied by the fake_biomni fixture; we
    # need the rest of the package tree wired up.
    monkeypatch.setitem(sys.modules, "biomni.utils", utils)
    monkeypatch.setitem(sys.modules, "biomni.agent", biomni_agent)
    monkeypatch.setitem(sys.modules, "biomni.agent.a1", biomni_a1)
    _FakeA1.last_kwargs = {}


def test_make_agent_default_does_not_override_max_tokens(fake_baponi, fake_biomni, monkeypatch):
    _patch_biomni(monkeypatch)
    from baponi_biomni import make_agent

    agent = make_agent(llm="claude-sonnet-4-20250514")
    # Default is None -> biomni's existing max_tokens stays
    assert agent.llm.max_tokens == 8192


def test_make_agent_explicit_max_tokens_applied(fake_baponi, fake_biomni, monkeypatch):
    _patch_biomni(monkeypatch)
    from baponi_biomni import make_agent

    agent = make_agent(llm="qwen3", max_tokens=200_000)
    assert agent.llm.max_tokens == 200_000


def test_make_agent_forwards_host_plots_dir(tmp_path, fake_baponi, fake_biomni, monkeypatch):
    _patch_biomni(monkeypatch)
    from baponi_biomni import make_agent

    agent = make_agent(llm="claude", host_plots_dir=tmp_path / "myplots")
    assert agent._baponi_executor.host_plots_dir == tmp_path / "myplots"


def test_make_agent_forwards_python_bin(fake_baponi, fake_biomni, monkeypatch):
    _patch_biomni(monkeypatch)
    from baponi_biomni import make_agent

    agent = make_agent(llm="claude", python_bin="/opt/conda/envs/biomni/bin/python")
    assert agent._baponi_executor.python_bin == "/opt/conda/envs/biomni/bin/python"


def test_make_agent_forwards_source_base_url_api_key(fake_baponi, fake_biomni, monkeypatch):
    _patch_biomni(monkeypatch)
    from baponi_biomni import make_agent

    make_agent(
        llm="qwen3",
        source="Custom",
        base_url="http://127.0.0.1:1234/v1",
        api_key="lm-studio",
    )
    assert _FakeA1.last_kwargs["source"] == "Custom"
    assert _FakeA1.last_kwargs["base_url"] == "http://127.0.0.1:1234/v1"
    assert _FakeA1.last_kwargs["api_key"] == "lm-studio"
