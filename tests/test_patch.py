"""Verify apply_patches rebinds biomni's exec functions on stub modules."""
from __future__ import annotations

import sys
import types

import pytest


@pytest.fixture
def stub_biomni(monkeypatch):
    """Construct a fake biomni package tree with the 4 exec functions."""
    biomni = types.ModuleType("biomni")
    tool = types.ModuleType("biomni.tool")
    support = types.ModuleType("biomni.tool.support_tools")
    utils = types.ModuleType("biomni.utils")
    agent = types.ModuleType("biomni.agent")
    agent_a1 = types.ModuleType("biomni.agent.a1")

    def _orig_python(c): return f"orig-py:{c}"
    def _orig_r(c): return f"orig-r:{c}"
    def _orig_bash(c): return f"orig-bash:{c}"
    def _orig_cli(c): return f"orig-cli:{c}"

    support.run_python_repl = _orig_python
    support._captured_plots = []
    utils.run_r_code = _orig_r
    utils.run_bash_script = _orig_bash
    utils.run_cli_command = _orig_cli
    # simulate star-import re-export
    agent_a1.run_python_repl = _orig_python
    agent_a1.run_r_code = _orig_r
    agent_a1.run_bash_script = _orig_bash
    agent_a1.run_cli_command = _orig_cli

    biomni.tool = tool
    tool.support_tools = support
    biomni.utils = utils
    biomni.agent = agent
    agent.a1 = agent_a1

    for name, mod in {
        "biomni": biomni,
        "biomni.tool": tool,
        "biomni.tool.support_tools": support,
        "biomni.utils": utils,
        "biomni.agent": agent,
        "biomni.agent.a1": agent_a1,
    }.items():
        monkeypatch.setitem(sys.modules, name, mod)
    return {"support": support, "utils": utils, "a1": agent_a1}


def test_apply_patches_rebinds_all_targets(stub_biomni, fake_baponi):
    from baponi_biomni import BaponiExecutor, apply_patches

    ex = BaponiExecutor()
    apply_patches(ex)

    st = stub_biomni["support"]
    bu = stub_biomni["utils"]
    a1 = stub_biomni["a1"]

    assert st.run_python_repl("x") != "orig-py:x"
    assert bu.run_bash_script("ls") != "orig-bash:ls"
    assert bu.run_cli_command("ls") != "orig-cli:ls"
    # a1 re-exports rebinded
    assert a1.run_python_repl("y") != "orig-py:y"
    assert a1.run_bash_script("ls") != "orig-bash:ls"


def test_apply_patches_routes_python_to_executor(stub_biomni, fake_baponi):
    from baponi_biomni import BaponiExecutor, apply_patches

    ex = BaponiExecutor()
    apply_patches(ex)

    import biomni.tool.support_tools as st
    st.run_python_repl("print('hello')")
    assert len(fake_baponi.calls) == 1
    assert fake_baponi.calls[0]["language"] == "python"
