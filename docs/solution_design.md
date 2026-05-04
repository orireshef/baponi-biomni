# baponi-biomni — Solution Design

## Overview

`baponi-biomni` is a thin wrapper layer that monkey-patches biomni's four
execution entry points before `biomni.agent.A1` is constructed, so all
LLM-generated code runs inside a Baponi sandbox instead of on the host. The
agent loop, tool registry, retriever, prompt formatting, and LLM client are
all biomni-native — only the leaves of the call graph (the `run_*` functions)
are intercepted.

```
   ┌─────────────────────────────────────────────┐
   │ Host process (your machine)                 │
   │                                             │
   │   biomni.agent.A1                           │
   │       │                                     │
   │       │ self.llm.invoke(...)                │
   │       │                                     │
   │       └──> ChatAnthropic / ChatOpenAI / …   │  ── HTTPS ──> LLM provider
   │           (Anthropic, OpenAI, LM Studio)    │              (local or cloud)
   │       │                                     │
   │       │ tool call: run_python_repl(code)    │
   │       ▼                                     │
   │   ┌─────────────────────────────────────┐   │
   │   │ baponi_biomni.patch                 │   │
   │   │   run_python_repl  ──▶ executor.py  │   │
   │   │   run_r_code       ──▶ raise        │   │
   │   │   run_bash_script  ──▶ executor.py  │   │
   │   │   run_cli_command  ──▶ executor.py  │   │
   │   └─────────────────────────────────────┘   │
   │       │                                     │
   │       │ BaponiExecutor.python(code)         │
   │       │   wraps with prologue + epilogue    │
   │       ▼                                     │
   │   baponi.Baponi.execute(code, thread_id)    │  ── HTTPS ──>  Baponi API
   │                                             │
   │       ◀──── stdout, stderr, exit_code ──────┤
   │                                             │
   │   _sync_plots():                            │
   │     Baponi.list_files(path="_plots")        │  ── HTTPS ──>  Baponi API
   │     Baponi.download_url(path=...)           │
   │     httpx.get(presigned_url)                │  ── HTTPS ──>  Cloud Storage
   │     biomni._captured_plots.append(...)      │
   └─────────────────────────────────────────────┘
```

## Components

### `BaponiExecutor` (`src/baponi_biomni/executor.py`)

Owns one `baponi.Baponi` client + one `thread_id`. Methods:

| Method | Routes to | Notes |
|---|---|---|
| `python(code)` | `client.execute(language="python", thread_id, env_vars)` | Wraps with `prologue.wrap()` to add state + plot interception |
| `bash(script)` | `client.execute(language="bash", thread_id, env_vars)` | Direct passthrough |
| `cli(command)` | `bash(command)` | Baponi handles tokenization |
| `r(code)` | raises `RNotSupportedError` | No Rscript in default image |
| `_sync_plots()` | `list_files` + `download_url` + `httpx.get` | Pulls new PNGs into `biomni.tool.support_tools._captured_plots` |

### `prologue.py` — code injected into every `python` exec

Each Baponi exec is a fresh process. Persistence comes only from `/home/baponi`
(thread-scoped filesystem). To preserve biomni's REPL semantics we inject:

1. **`PROLOGUE_STATE`** — at the top: deserialize `/home/baponi/_biomni_ns.pkl`
   into `globals()` if it exists. Stdlib `pickle` (chosen over cloudpickle to
   avoid bootstrap install dance).
2. **`PROLOGUE_PLOTS`** — patches `plt.show` and `plt.savefig` to mirror every
   active figure to `/home/baponi/_plots/<uuid>.png`. Mirrors biomni's local
   matplotlib monkey-patch behavior. Idempotent (each call is a new process).
3. **(user code in the middle)**
4. **`EPILOGUE_STATE`** — at the bottom: serialize all picklable globals back
   to `/home/baponi/_biomni_ns.pkl`. Underscore-prefixed names skipped to keep
   prologue helpers out of the dump.

### `patch.py` — `apply_patches(executor)`

Rebinds biomni symbols to executor methods. Targets verified via
`test_real_biomni_patch.py`:

- `biomni.tool.support_tools.run_python_repl`
- `biomni.utils.run_r_code` / `run_bash_script` / `run_cli_command`
- `biomni.agent.a1.run_python_repl` / `run_r_code` / `run_bash_script` (these
  are star-imports captured at module load and must be rebound at the import
  site too)

Must be called **before** `biomni.agent.A1` is constructed if A1's `__init__`
captures references to these functions; `make_agent` enforces this ordering.

### `make_agent` (`src/baponi_biomni/__init__.py`)

Public entrypoint. Creates a `BaponiExecutor`, calls `apply_patches`, then
imports and constructs `A1`. Forwards LLM-related kwargs (`source`, `base_url`,
`api_key`) so the same wrapper supports Anthropic, OpenAI, Custom (LM Studio),
Ollama, etc.

## Plot capture flow (the important detail)

Baponi's `list_files(path="_plots")` returns paths **relative to `_plots`**
(just `aa.png`), but `download_url(path=...)` requires the **full path from
`/home/baponi`** (`_plots/aa.png`). The executor composes the full path before
downloading. The fake client in tests mirrors this semantics so tests would
catch a regression.

State of plots is tracked per-executor via `self._seen_plots: set[str]`.
Diffed against each `list_files` response so only newly created PNGs round-
trip back.

Each new PNG is delivered three ways so all downstream consumers in biomni
keep working:

1. **Written to disk** at `self.host_plots_dir / <filename>.png`
   (default `data/plots/<thread_id>/`). This is what makes biomni's gradio
   UI render plots inline — its rendering loop scans tool stdout for
   `*.png` paths and renders any that resolve on host (`a1.py:2713`).
2. **Appended to `support_tools._captured_plots`** as a `data:image/png;base64,…`
   URI. This is what biomni's markdown export (`_add_execution_plots`) uses.
3. **Announced in stdout** via a `Plot saved to: <abs-host-path>` line so
   the gradio scanner finds path 1 above.

## State persistence flow

```
Call 1: python("x = 42")
  prologue:  pkl missing → no-op
  user:      x = 42
  epilogue:  pickle.dumps(x=42) → /home/baponi/_biomni_ns.pkl

Call 2: python("print(x)")
  prologue:  pkl exists → globals().update({"x": 42})
  user:      print(x)  → "42\n"
  epilogue:  pickle.dumps(x=42) → /home/baponi/_biomni_ns.pkl
```

Limitation: stdlib pickle can't serialize lambdas, locally-defined classes,
generators, file handles. Per-variable try/except in the epilogue silently
drops these. Acceptable for biomni's typical "compute, store, reuse" patterns;
not acceptable for users who define classes in the REPL and expect them to
survive (would need cloudpickle bootstrap).

## Configuration

### Environment variables
- `BAPONI_API_KEY` — required (read by Baponi SDK)
- `BAPONI_BASE_URL` — optional override (default `https://api.baponi.ai`)
- `LLM_BASE_URL`, `LLM_MODEL` — used by `examples/admet.py`

### `make_agent` kwargs
- `path`: biomni data dir
- `llm`, `source`, `base_url`, `api_key`: forwarded to A1's LLM construction
- `thread_id`: explicit Baponi thread id (auto-generated UUID otherwise)
- `env_vars`: passed to every `client.execute` call (uppercased automatically;
  PATH/HOME/etc. blocked by Baponi)
- `timeout`: per-call sandbox timeout (free tier max 60s; Pro max 3600s)
- `**a1_kwargs`: passes through (e.g. `expected_data_lake_files=[]` to skip
  the 12GB+ data lake download)

## Test architecture

### `FakeBaponi` (`tests/conftest.py`)
In-memory implementation of the subset of the Baponi client we use:
- `execute(code, language, thread_id, env_vars)` — records call args, returns
  configurable `SandboxResult`
- `list_files(source, id, path)` — mirrors real semantics (returns paths
  RELATIVE to the `path` argument)
- `download_url(path, source, id)` — returns a fake URL routed back through
  `fake_httpx` to retrieve content from the in-memory file store

### Test fixtures
- `fake_baponi` — patches `baponi_biomni.executor.Baponi` to return a
  `FakeBaponi` instance
- `fake_httpx` — patches `httpx.get` to read from the fake file store
- `fake_biomni` — injects a stub `biomni.tool.support_tools` module so plot
  sync has a place to write
- `stub_biomni` (in `test_patch.py`) — full fake biomni package tree to test
  patch rebinding without the real install

### Coverage
- `test_executor.py` — wrapping, fence-stripping, error handling, thread_id
  stability, env_var case-coercion (9 tests)
- `test_patch.py` — rebinding correctness (2 tests)
- `test_plot_capture.py` — Files API integration, dedup, non-PNG filtering
  (3 tests)
- `test_prologue.py` — wrap helper + real `exec()` round-trip with
  `/home/baponi` redirected to a tmpdir (2 tests)
- `test_real_biomni_patch.py` — verifies our rebind targets exist on the
  installed biomni and that calling them routes through the executor (2 tests)

## Known design limits

| Limit | Mitigation | Path forward |
|---|---|---|
| No R support | Raises typed exception | Custom OCI image with r-base via Baponi admin console (v1.1) |
| stdlib pickle drops lambdas/local classes | Silent drop with per-var try/except | Bootstrap cloudpickle on first call (needs `--user` install + sys.path refresh) |
| 60s free-tier timeout | Document; bump to Pro tier | None on our side |
| Cold start: pip install per thread | Thread reuse amortizes | Custom OCI image with biomedical scientific stack preinstalled |
| One concurrent exec per thread | Biomni doesn't appear to invoke tools concurrently | Multi-thread executor pool if needed |

## Why monkey-patch and not fork

- Biomni is actively developed; a fork would diverge.
- The exec functions are the only sandboxing-relevant surface — patching them
  at the leaf preserves all other biomni behavior.
- `apply_patches` is testable against a stub biomni AND the real install, so
  upstream symbol relocations are caught early.
