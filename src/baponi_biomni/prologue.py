"""Code injected into every sandbox python execution.

Each Baponi exec is a fresh process; persistence comes from /home/baponi (thread-scoped).
- PROLOGUE_STATE: rehydrate globals() from cloudpickle dump
- PROLOGUE_PLOTS: patch matplotlib so figures mirror to /home/baponi/_plots/
- EPILOGUE_STATE: dump picklable globals back to disk

All injected names are underscore-prefixed so the cloudpickle filter skips them.
"""

PROLOGUE_STATE = '''\
import os as _os, pickle as _pk
_NS_PATH = "/home/baponi/_biomni_ns.pkl"
if _os.path.exists(_NS_PATH):
    try:
        with open(_NS_PATH, "rb") as _f:
            globals().update(_pk.load(_f))
    except Exception as _e:
        print(f"[baponi-biomni] state restore failed: {_e}")
'''

PROLOGUE_PLOTS = '''\
import os as _os, uuid as _uuid
_PLOTS_DIR = "/home/baponi/_plots"
_os.makedirs(_PLOTS_DIR, exist_ok=True)
try:
    import matplotlib as _mpl
    _mpl.use("Agg")
    import matplotlib.pyplot as _plt
    _orig_show = _plt.show
    _orig_savefig = _plt.savefig
    def _mirror_active_figures():
        for _n in _plt.get_fignums():
            _plt.figure(_n).savefig(
                f"{_PLOTS_DIR}/{_uuid.uuid4().hex}.png",
                dpi=150, bbox_inches="tight",
            )
    def _show(*a, **k):
        _mirror_active_figures()
        print("Plot generated and displayed")
        return _orig_show(*a, **k)
    def _savefig(*a, **k):
        _r = _orig_savefig(*a, **k)
        _fname = a[0] if a else k.get("fname", "unknown")
        if not str(_fname).startswith(_PLOTS_DIR):
            _mirror_active_figures()
        print(f"Plot saved to: {_fname}")
        return _r
    _plt.show = _show
    _plt.savefig = _savefig
except ImportError:
    pass
'''

EPILOGUE_STATE = '''\
try:
    import pickle as _pk
    _SKIP = {"In", "Out", "exit", "quit", "get_ipython"}
    _dump = {}
    for _k, _v in list(globals().items()):
        if _k.startswith("_") or _k in _SKIP:
            continue
        try:
            _pk.dumps(_v)
            _dump[_k] = _v
        except Exception:
            pass
    with open("/home/baponi/_biomni_ns.pkl", "wb") as _f:
        _pk.dump(_dump, _f)
except Exception as _e:
    print(f"[baponi-biomni] state dump failed: {_e}")
'''


def wrap(user_code: str) -> str:
    """Wrap user code with state + plot prologue and state epilogue."""
    return (
        PROLOGUE_STATE
        + PROLOGUE_PLOTS
        + "\n# --- user code ---\n"
        + user_code
        + "\n# --- end user code ---\n"
        + EPILOGUE_STATE
    )
