# SDLC Experience Log

## v0.1.0 — baponi-biomni initial integration (2026-05-04)

### What Went Well

- **Plan-mode discipline up front.** The /sdlc plan template
  (`.claude/plans/i-want-to-set-frolicking-milner.md`) anchored the design.
  Every later code decision traced back to a verified fact in the SDK probe
  or biomni source dive, not to assumptions.
- **FakeBaponi from the start.** Building a fake client in `tests/conftest.py`
  before writing any executor code meant tests ran offline and caught the
  Files API path-relativity bug after the fix landed.
- **Real-biomni integration test.** `test_real_biomni_patch.py` runs against
  the installed biomni and confirms our patch targets line up with upstream's
  star-import re-exports in `biomni.agent.a1`. Catches a class of regression
  the stub-based tests cannot.
- **Iterative SDK probing.** Probing PyPI metadata, then `inspect.getmembers`
  on the installed `Baponi` client, surfaced first-class file methods
  (`list_files`, `download_url`) the docs hadn't mentioned. Saved us from
  writing a raw httpx client.

### What Went Wrong

- **Eager-commits skipped during initial build.** Whole feature shipped as
  one uncommitted diff. Discovered when `/sdlc` was invoked retroactively.
  Lesson: commit per logical unit during build, not at the end.
- **Files API path semantics surprise.** Assumed `list_files(path="_plots")`
  returns full paths from `/home/baponi`. It returns paths *relative to the
  `path` argument*. Caught only by live probing against staging — unit tests
  with the FakeBaponi that mimicked the wrong semantics would have hidden it.
  Updated FakeBaponi to match real behavior so tests now guard against
  regression in either direction.
- **cloudpickle bootstrap detour.** Initial design specified cloudpickle for
  state round-trip. The sandbox doesn't have it preinstalled; `pip install
  --user --quiet cloudpickle` followed by import in the same process failed
  because user-site wasn't on `sys.path`. Reverted to stdlib `pickle`. Less
  faithful but no install dance, and good enough for biomni's typical
  variable-reuse patterns.
- **Biomni's incomplete `Requires-Dist`.** biomni 0.0.8 declares only
  `pydantic`, `langchain`, `python-dotenv`. Actual imports include pandas,
  langchain-openai, langchain-anthropic, langchain-text-splitters, requests,
  tqdm. Had to add these to our pyproject. If biomni publishes a new version
  with proper deps, we should drop the duplicates.
- **DNS / staging URL.** SDK default `https://api.baponi.ai` doesn't resolve
  on the test machine. User pointed us at staging; added `BAPONI_BASE_URL`
  env-var passthrough. Should have made this configurable from day one.

### Lessons Learned

- **When integrating with a third-party SDK, probe the live client, not just
  the docs.** Docs are aspirational; the SDK is reality. `inspect.getmembers`
  + `inspect.signature` surfaces the truth.
- **Make fake clients mirror real semantics, not assumed semantics.**
  Whenever you hit a "hm that's weird" against a real API, immediately update
  the fake to match. The fake is your regression net.
- **Default to stdlib for sandbox-side dependencies.** Anything you ship into
  the sandbox process has bootstrap cost. Use the stdlib unless the limit
  actually bites.
- **Make endpoint URLs env-overridable from the first commit.** Saves a
  retrofit when staging / self-hosted setups appear.
- **Commit eagerly even when shipping fast.** The diff doesn't get smaller
  by waiting; it just gets harder to split into atomic commits later.

### Metrics

- Tests: 18 written, 18 passing (no skips, no flakes)
- Commits: 6 (all retroactive — see Lessons Learned)
- Review rounds: 1 (lead-only self-review; no agent team spawned for v0.1)
- Live verifications:
  - `BaponiExecutor` smoke test: state persistence + plot capture against
    staging Baponi → green
  - Full A1 agent ADMET run with LM Studio (`qwen3.5-35b-a3b@8bit`) →
    produced solution block in ~60s wall, ~10 sandbox calls
- Files: 5 source modules, 6 test modules, 2 examples, 3 design docs

### Open follow-ups

- **R support (v1.1)**: build OCI image with r-base, push to Baponi admin
  console, route `run_r_code` through bash with `Rscript -e`.
- **cloudpickle bootstrap**: handle `--user` install + `site.addsitedir` +
  `importlib.invalidate_caches` so users who define REPL classes get them
  preserved across calls.
- **Streaming output**: surface long-running sandbox progress via
  `client.execute_stream` — currently the host blocks until exec completes.
- **Sandbox scientific stack**: bake numpy, pandas, scipy, scanpy, biopython,
  rdkit into a custom OCI image so cold-start `pip install` is unnecessary.
