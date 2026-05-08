# baponi-biomni

Run [snap-stanford/biomni](https://github.com/snap-stanford/biomni) with all
LLM-generated code routed through [baponi.ai](https://baponi.ai/) sandboxes.
Biomni out of the box runs Python/R/bash on the host with full privileges; this
wrapper monkey-patches its 4 execution functions to call Baponi's `/v1/sandbox/execute`
instead. One Baponi `thread_id` per agent session gives `/home/baponi`
filesystem persistence (pip packages + files) across tool calls. Variables are
preserved between calls via a cloudpickle round-trip. Matplotlib figures are
mirrored to `/home/baponi/_plots/` and pulled back via the Files API into
biomni's `_captured_plots` global.

## Setup

```bash
cp .env.example .env
# edit .env to set BAPONI_API_KEY (sk-us-...) and ANTHROPIC_API_KEY (sk-ant-...)
uv sync
```

## Hello world

```python
from dotenv import load_dotenv
from baponi_biomni import make_agent

load_dotenv()
agent = make_agent(llm="claude-sonnet-4-20250514")
agent.go("Predict ADMET properties of ibuprofen.")
```

`make_agent` is a drop-in replacement for `biomni.agent.A1(...)`. It applies the
patches before importing `A1`, so any of biomni's tools that shell out to
`run_python_repl` / `run_bash_script` / `run_cli_command` go through Baponi.

## Web UI

Launch biomni's built-in Gradio UI with all execution sandboxed:

```bash
uv sync --extra ui
uv run baponi-biomni-ui --host 127.0.0.1
# open http://127.0.0.1:7860
```

By default the UI uses LM Studio at `http://127.0.0.1:1234/v1` for the LLM.
Override via `LLM_BASE_URL`, `LLM_MODEL`, `LLM_SOURCE`, `LLM_API_KEY` in `.env`.

Plots render inline: PNGs created in the sandbox are pulled to
`data/plots/<thread_id>/` on the host so biomni's chat UI can display them.

## Usage as a library

```python
from baponi_biomni import BaponiExecutor

ex = BaponiExecutor(thread_id="my-session", timeout=60)
ex.python("x = 42")
print(ex.python("print(x)"))    # "42\n"
print(ex.bash("ls /home/baponi"))
```

## Claude Code life-sciences plugins

`.claude/settings.json` registers Anthropic's
[life-sciences marketplace](https://github.com/anthropics/life-sciences) and
pre-enables the no-auth plugins so anyone running Claude Code in this repo gets
literature search (PubMed, bioRxiv), drug/target data (ChEMBL, Open Targets,
ClinicalTrials.gov), and skills for single-cell QC, scvi-tools, nf-core
pipelines, Allotrope conversion, clinical-trial protocols, and scientific
problem selection — alongside biomni's 150+ tools.

Auth-gated plugins (BioRender, Synapse, Wiley Scholar Gateway, 10x Genomics
Cloud, Owkin, Medidata) are available in the marketplace but disabled by
default — enable + configure them via `/plugin` when needed.

## Limitations

- **R is not supported.** `run_r_code` raises `RNotSupportedError`. Baponi's
  default OCI image ships Python 3.14 + Node 25 + bash, no `Rscript`. Adding R
  requires pushing a custom OCI image via the Baponi admin console (one image
  per API key).
- **Free tier: 60s sandbox timeout.** Biomedical workloads commonly exceed
  this; bump to Pro tier or split into smaller steps.
- **Cold start cost.** The first `pip install` per `thread_id` takes a few
  seconds. Reuse the thread between calls (default behavior) to amortize it.
- **Cloudpickle round-trip.** Variables that aren't picklable (open file
  handles, db connections, lambdas pointing into user namespace) are silently
  dropped between calls; only picklable globals survive.
- **No concurrent calls per thread.** Baponi rejects with `ThreadBusyError`
  (HTTP 409). Biomni doesn't appear to invoke tools concurrently within one
  agent loop, so this should not surface, but is worth knowing if you build on
  top of `BaponiExecutor` directly.

## Tests

```bash
uv run pytest
```

Tests use a `FakeBaponi` in-memory client (`tests/conftest.py`) — no network or
API key needed.

## Project layout

```
src/baponi_biomni/
  __init__.py     # make_agent(), public API
  executor.py     # BaponiExecutor: 4 exec methods + plot sync via Files API
  patch.py        # apply_patches(): rebind biomni's exec symbols
  prologue.py     # injected pre/post code for state + plot capture
  errors.py       # RNotSupportedError
examples/
  admet.py        # full A1 agent demo (needs API keys)
  plot_demo.py    # BaponiExecutor-only smoke test
tests/            # unit tests with FakeBaponi
```
