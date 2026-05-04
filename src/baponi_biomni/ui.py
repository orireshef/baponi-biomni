"""Gradio UI launcher for biomni routed through Baponi sandboxes.

Wraps biomni's built-in `agent.launch_gradio_demo()` so the user can run:

    uv run baponi-biomni-ui

Reads from `.env`:
    BAPONI_API_KEY        (required)
    BAPONI_BASE_URL       (optional, default https://api.baponi.ai)
    LLM_BASE_URL          (default http://127.0.0.1:1234/v1, LM Studio)
    LLM_MODEL             (default qwen3.6-35b-a3b-nvfp4)
    LLM_SOURCE            (default Custom; e.g. "Anthropic" for cloud)
    LLM_API_KEY           (default "lm-studio"; required for cloud providers)
"""
from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Launch baponi-biomni Gradio UI")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Server host (passed to gradio's server_name; "
                             "default 127.0.0.1, use 0.0.0.0 to expose on LAN)")
    parser.add_argument("--share", action="store_true",
                        help="Expose a public gradio.live tunnel")
    parser.add_argument("--data-path", default="./data")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Per-call sandbox timeout (seconds)")
    parser.add_argument("--baponi-thread-id", default=None,
                        help="Explicit Baponi sandbox thread id "
                             "(auto-generated otherwise)")
    args = parser.parse_args()

    try:
        import gradio  # noqa: F401
        import gradio.networking
        import gradio_client.utils as _gc_utils
    except ImportError:
        raise SystemExit(
            "gradio is not installed. Run: uv sync --extra ui"
        ) from None

    # Gradio 4.x runs an httpx HEAD against the bound address after launch and
    # raises if it can't reach itself. On macOS that probe sometimes fails
    # spuriously even though the server is up. Skip the check. Accept *args
    # so we don't break if a future gradio version passes timeout=...
    gradio.networking.url_ok = lambda *_a, **_k: True

    # gradio 4.44 + pydantic v2 generates `additionalProperties: True` (a
    # bool) in some langchain tool schemas, which gradio_client's
    # _json_schema_to_python_type can't handle (calls `"const" in schema`).
    # Wrap so non-dict schemas resolve to "any".
    _orig_resolver = _gc_utils._json_schema_to_python_type

    def _safe_resolver(schema, defs):
        if not isinstance(schema, dict):
            return "Any"
        try:
            return _orig_resolver(schema, defs)
        except (TypeError, _gc_utils.APIInfoParseError):
            return "Any"

    _gc_utils._json_schema_to_python_type = _safe_resolver

    from baponi_biomni import make_agent

    # Reasoning-capable local models (qwen3.x, deepseek-r1, ...) burn many
    # tokens on hidden reasoning before the visible answer; biomni's
    # hardcoded 8192 cap truncates them. Override only when source=Custom
    # so we don't 400 cloud APIs that cap at lower model-specific values.
    source = os.environ.get("LLM_SOURCE", "Custom")
    max_tokens = 200_000 if source == "Custom" else None

    agent = make_agent(
        path=args.data_path,
        llm=os.environ.get("LLM_MODEL", "qwen3.6-35b-a3b-nvfp4"),
        source=source,
        base_url=os.environ.get("LLM_BASE_URL", "http://127.0.0.1:1234/v1"),
        api_key=os.environ.get("LLM_API_KEY", "lm-studio"),
        max_tokens=max_tokens,
        thread_id=args.baponi_thread_id,
        timeout=args.timeout,
        expected_data_lake_files=[],
    )

    print(f"\nbaponi-biomni UI")
    print(f"  baponi thread_id: {agent._baponi_executor.thread_id}")
    print(f"  serving on http://{args.host}:7860 (gradio default)\n")

    agent.launch_gradio_demo(server_name=args.host, share=args.share)


if __name__ == "__main__":
    main()
