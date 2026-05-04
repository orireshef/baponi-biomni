"""Sanity tests on the injected code as a string and via real exec()."""
from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from baponi_biomni.prologue import (
    EPILOGUE_STATE,
    PROLOGUE_PLOTS,
    PROLOGUE_STATE,
    wrap,
)


def test_wrap_includes_user_code():
    out = wrap("z = 1")
    assert "z = 1" in out
    assert PROLOGUE_STATE in out
    assert PROLOGUE_PLOTS in out
    assert EPILOGUE_STATE in out


def test_state_roundtrip_via_real_exec(tmp_path, monkeypatch):
    """Run prologue+user+epilogue twice with /home/baponi redirected to tmp_path.

    Verifies the pickle round-trip mechanism end-to-end without baponi.
    """
    fake_home = tmp_path / "home" / "baponi"
    fake_home.mkdir(parents=True)

    # patch the hardcoded path
    state_pro = PROLOGUE_STATE.replace("/home/baponi", str(fake_home))
    plots_pro = PROLOGUE_PLOTS.replace("/home/baponi", str(fake_home))
    state_epi = EPILOGUE_STATE.replace("/home/baponi", str(fake_home))

    # call 1: define x = 42
    code1 = state_pro + plots_pro + "\nx = 42\n" + state_epi
    ns1: dict = {}
    exec(code1, ns1)
    assert (fake_home / "_biomni_ns.pkl").exists()

    # call 2: read x and store result
    code2 = state_pro + "\nresult = x * 2\n" + state_epi
    ns2: dict = {}
    exec(code2, ns2)
    assert ns2["result"] == 84
