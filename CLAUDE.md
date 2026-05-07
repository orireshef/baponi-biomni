# baponi-biomni

Wrapper that runs [snap-stanford/biomni](https://github.com/snap-stanford/biomni) with all
LLM-generated code routed through [baponi.ai](https://baponi.ai/) sandboxes. Monkey-patches
biomni's 4 exec functions (`run_python_repl`, `run_bash_script`, `run_cli_command`,
`run_r_code`) to call Baponi's `/v1/sandbox/execute` instead of running on the host.

See `README.md` for usage.

## Communication

- Use `/caveman full` mode by default. Terse, compressed responses.

## Package Management

- **uv** for everything (`uv add`, `uv sync`, `uv run pytest`). Never `pip` directly.

## Commits

- Conventional Commits: `<type>(<scope>): <description>`.
- No `Co-Authored-By` trailers.
- Commit eagerly; one logical change per commit.

## Life-sciences plugins

`.claude/settings.json` registers Anthropic's
[life-sciences marketplace](https://github.com/anthropics/life-sciences).

**Enabled MCPs**: PubMed, ToolUniverse.

**Enabled skills** (no MCP): single-cell-rna-qc, scvi-tools, nextflow-development,
instrument-data-to-allotrope, clinical-trial-protocol, scientific-problem-selection.

**Disabled MCPs** — kept here for future re-enable:
- `biorxiv@`, `clinical-trials@`, `chembl@` — upstream `mcp.deepsense.ai` host is
  NXDOMAIN (vendor took it down or never published). Re-enable when DNS is
  restored or replace with a sandbox-backed skill.
- `open-targets@` — upstream MCP rejects the protocol versions Claude Code
  negotiates. Replaced by the local **`open-targets`** skill
  (`.claude/skills/open-targets/SKILL.md`) which queries the Open Targets
  parquet release mounted at `/data/open-targets-public/<release>/output/`
  inside the Baponi sandbox via DuckDB. Faster, no network round-trips, and the
  parquet release is the canonical artefact.

Auth-gated plugins (BioRender, Synapse, Wiley, 10x Genomics, Owkin, Medidata)
ship disabled — enable via `/plugin` after configuring credentials.

The claude.ai-managed Google Drive / Gmail / Google Calendar connectors are
disabled at the account level via the claude.ai web settings (not local config).

## Discipline

Non-trivial work follows the **`/sdlc`** skill (`.claude/skills/sdlc/SKILL.md`):
Reflect → Plan → Implement → Review → Learn. TDD when writing code.

Other skills available in `.claude/skills/`:
- `create-prd` — produce a PRD for an epic
- `gemini-cli` — Gemini CLI helper
- `open-targets` — query OT Platform parquet release via Baponi sandbox + DuckDB

Agents available in `.claude/agents/`:
- `ai-researcher` — research, experiment design, ML methodology
- `technical-pm` — requirements, API design, PRDs

## Design Documents

Architecture, solution designs, implementation plans, and per-epic specs live under
`docs/` (load on demand) — not in this file.
