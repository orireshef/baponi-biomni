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
[life-sciences marketplace](https://github.com/anthropics/life-sciences) and
enables the no-auth plugins (PubMed, bioRxiv, ClinicalTrials.gov, ChEMBL,
Open Targets, ToolUniverse) plus skills (single-cell-rna-qc, scvi-tools,
nextflow-development, instrument-data-to-allotrope, clinical-trial-protocol,
scientific-problem-selection). Auth-gated plugins (BioRender, Synapse, Wiley,
10x Genomics, Owkin, Medidata) ship disabled — enable via `/plugin` after
configuring credentials.

## Discipline

Non-trivial work follows the **`/sdlc`** skill (`.claude/skills/sdlc/SKILL.md`):
Reflect → Plan → Implement → Review → Learn. TDD when writing code.

Other skills available in `.claude/skills/`:
- `create-prd` — produce a PRD for an epic
- `gemini-cli` — Gemini CLI helper

Agents available in `.claude/agents/`:
- `ai-researcher` — research, experiment design, ML methodology
- `technical-pm` — requirements, API design, PRDs

## Design Documents

Architecture, solution designs, implementation plans, and per-epic specs live under
`docs/` (load on demand) — not in this file.
