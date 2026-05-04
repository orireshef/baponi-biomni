"""Integration test: verify apply_patches against the actually-installed biomni.

Does NOT make any API calls — uses fake_baponi for the Baponi client.
Confirms our rebind targets match upstream biomni's module layout.
"""
from __future__ import annotations


def test_real_biomni_modules_have_expected_targets():
    """Sanity-check: upstream biomni still exposes the symbols we patch."""
    import biomni.tool.support_tools as st
    import biomni.utils as bu
    import biomni.agent.a1 as a1m

    assert hasattr(st, "run_python_repl")
    assert hasattr(st, "_captured_plots")
    assert hasattr(bu, "run_r_code")
    assert hasattr(bu, "run_bash_script")
    assert hasattr(bu, "run_cli_command")
    # a1 re-imports a subset
    assert hasattr(a1m, "run_python_repl")
    assert hasattr(a1m, "run_bash_script")


def test_apply_patches_against_real_biomni(fake_baponi):
    from baponi_biomni import BaponiExecutor, apply_patches

    ex = BaponiExecutor()
    apply_patches(ex)

    import biomni.tool.support_tools as st
    import biomni.utils as bu
    import biomni.agent.a1 as a1m

    # Calling the patched function should hit FakeBaponi
    st.run_python_repl("print('hi')")
    assert any(c["language"] == "python" for c in fake_baponi.calls)

    fake_baponi.calls.clear()
    bu.run_bash_script("ls /tmp")
    assert any(c["language"] == "bash" for c in fake_baponi.calls)

    fake_baponi.calls.clear()
    a1m.run_python_repl("print('via a1')")
    assert any(c["language"] == "python" for c in fake_baponi.calls)
