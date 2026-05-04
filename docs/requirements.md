# baponi-biomni — Requirements

## Problem

[snap-stanford/biomni](https://github.com/snap-stanford/biomni) is a biomedical
agent that executes LLM-generated Python, R, and bash on the host with **full
system privileges**. The exec functions live in `biomni/tool/support_tools.py`
(`run_python_repl`) and `biomni/utils.py` (`run_r_code`, `run_bash_script`,
`run_cli_command`). Running an agent that downloads packages, writes files, and
shells out at the LLM's discretion is a non-starter for any environment that
isn't already a throwaway VM.

## Goal

Run biomni unchanged with all LLM-generated code transparently routed through
[baponi.ai](https://baponi.ai) sandboxes. No fork of biomni. Drop-in API:

```python
from baponi_biomni import make_agent
agent = make_agent(llm="claude-sonnet-4-20250514")
agent.go("Predict ADMET properties of ibuprofen.")
```

## Functional requirements

### FR-1 — Transparent execution rerouting
All four biomni exec functions (`run_python_repl`, `run_r_code`,
`run_bash_script`, `run_cli_command`) must route through baponi without
requiring the user to modify their biomni code.

### FR-2 — Single-session statefulness
A single agent session must use one Baponi `thread_id`, giving:
- File persistence under `/home/baponi` across calls
- Pip-installed packages persist (cached in `~/.local`)
- One concurrent execution per thread (Baponi constraint)

### FR-3 — Python REPL state semantics
Variables defined in one `run_python_repl` call must survive into the next call
(matching biomni's local in-memory namespace behavior). Picklable globals only;
non-picklable values (lambdas, file handles) are silently dropped.

### FR-4 — Plot capture
Matplotlib figures generated inside the sandbox must surface back to biomni's
host-side `_captured_plots` global as `data:image/png;base64,...` URIs, so the
existing `get_captured_plots()` / multimodal feedback path keeps working.

### FR-5 — LLM provider flexibility
`make_agent` must accept `source`, `base_url`, and `api_key` kwargs so the
agent can use any biomni-supported LLM provider (Anthropic, OpenAI, OpenAI-
compatible local servers like LM Studio, etc.).

### FR-6 — Configurable sandbox endpoint
`BAPONI_BASE_URL` env var must override the default `https://api.baponi.ai`
(needed for staging or self-hosted Baponi deployments).

### FR-7 — R unsupported (v1)
`run_r_code` raises `RNotSupportedError` (Baponi's default OCI image has no
Rscript). Documented as v1.1 follow-up via custom OCI image.

## Non-functional requirements

### NFR-1 — Test coverage without network
Full unit test suite must run with no Baponi API key, no network, no
pre-installed biomni. Use a `FakeBaponi` in-memory client.

### NFR-2 — Real-biomni integration check
At least one test verifies our patch targets line up with the symbols actually
exposed by the installed biomni version.

### NFR-3 — Minimal divergence from biomni's contract
Tool return-value shape must match what biomni's agent loop expects (string
stdout, error prefix `Error: `, captured plots in the global). No agent-loop
changes required upstream.

### NFR-4 — uv-managed
`uv sync` brings up a working dev environment. No Conda, no system-level
package management.

## Acceptance criteria

- [x] AC-1: `uv run pytest` → all tests pass with no env vars set
- [x] AC-2: `examples/plot_demo.py` runs end-to-end with only `BAPONI_API_KEY`
  set, demonstrates state persistence and at least one captured plot
- [x] AC-3: `examples/admet.py` runs end-to-end with `BAPONI_API_KEY` and an
  LLM endpoint (LM Studio or cloud), produces an ADMET solution block
- [x] AC-4: No host-side `subprocess.run` / local `exec` is invoked for tool
  calls (verified by the agent loop completing entirely against the sandbox)
- [x] AC-5: `BAPONI_BASE_URL` env var overrides the default endpoint

## Out of scope (v1)

- R execution (deferred, requires custom OCI image)
- Custom biomedical Python libraries preinstalled in the sandbox image (rely
  on per-thread `pip install` warm-up)
- Multi-agent / concurrent thread management
- Streaming output (`client.execute_stream`) — current impl uses synchronous
  `client.execute`
