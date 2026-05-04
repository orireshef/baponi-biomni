from __future__ import annotations

import importlib

from .executor import BaponiExecutor

_REBIND_TARGETS = (
    "biomni.agent.a1",
    "biomni.agent",
)


def apply_patches(executor: BaponiExecutor) -> None:
    """Rebind biomni's 4 exec functions to route through the given executor.

    Must be called BEFORE biomni.agent.A1 is constructed if A1's __init__
    captures references to these functions. Re-binding both the definition
    sites and any star-import re-exports.
    """
    import biomni.tool.support_tools as st
    import biomni.utils as bu

    py = lambda c: executor.python(c)  # noqa: E731
    rr = lambda c: executor.r(c)  # noqa: E731
    bs = lambda s: executor.bash(s)  # noqa: E731
    cli = lambda c: executor.cli(c)  # noqa: E731

    st.run_python_repl = py
    if hasattr(bu, "run_python_repl"):
        bu.run_python_repl = py
    bu.run_r_code = rr
    bu.run_bash_script = bs
    bu.run_cli_command = cli

    binds = {
        "run_python_repl": py,
        "run_r_code": rr,
        "run_bash_script": bs,
        "run_cli_command": cli,
    }
    for mod_name in _REBIND_TARGETS:
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            continue
        for fn_name, fn in binds.items():
            if hasattr(mod, fn_name):
                setattr(mod, fn_name, fn)
