from __future__ import annotations

from .errors import RNotSupportedError
from .executor import BaponiExecutor
from .patch import apply_patches

__all__ = ["make_agent", "apply_patches", "BaponiExecutor", "RNotSupportedError"]


import os as _os


def make_agent(
    *,
    path: str = "./data",
    llm: str = "claude-sonnet-4-20250514",
    source: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    max_tokens: int | None = None,
    thread_id: str | None = None,
    env_vars: dict[str, str] | None = None,
    timeout: int = 600,
    python_bin: str | None = None,
    host_plots_dir: str | _os.PathLike[str] | None = None,
    **a1_kwargs,
):
    """Build a biomni A1 agent that runs all code through baponi sandbox.

    Args:
        path: biomni data dir (downloaded tool descriptions, etc.).
        llm: model id passed to A1.
        source: LLM provider: "OpenAI", "Anthropic", "Custom", etc. If None,
            biomni auto-detects from the model name or `base_url`.
        base_url: OpenAI-compatible endpoint URL for `source="Custom"`
            (e.g. "http://127.0.0.1:1234/v1" for LM Studio).
        api_key: LLM API key. For local servers like LM Studio, any non-empty
            string works.
        max_tokens: override the LLM's `max_tokens`. Biomni hardcodes 8192
            for `source="Custom"` (`biomni.llm.get_llm`), which truncates
            reasoning models like qwen3.6 that spend many tokens on hidden
            reasoning before the visible answer. Set to e.g. 200_000 for
            those. Default `None` leaves whatever biomni configured in
            place (Anthropic / OpenAI cloud models cap below 200k and a
            blanket override would 400 the API).
        thread_id: baponi thread id (auto-generated UUID if None). Files and
            installed packages persist under /home/baponi for this thread.
        env_vars: environment variables injected into the sandbox per call.
            Keys uppercased automatically; PATH/HOME/etc. are blocked by baponi.
        timeout: per-call sandbox timeout in seconds. Free tier caps at 60;
            Pro/Enterprise allow up to 3600. Default 600 leaves headroom for
            heavy ML model loads.
        python_bin: explicit python interpreter inside the sandbox image.
            Forwarded to BaponiExecutor; see its docstring.
        host_plots_dir: where pulled-down PNGs land on the host. Forwarded
            to BaponiExecutor.
        **a1_kwargs: forwarded to biomni.agent.A1.
    """
    executor = BaponiExecutor(
        thread_id=thread_id,
        timeout=timeout,
        env_vars=env_vars,
        python_bin=python_bin,
        host_plots_dir=host_plots_dir,
    )
    apply_patches(executor)
    from biomni.agent import A1

    a1_extra = {}
    if source is not None:
        a1_extra["source"] = source
    if base_url is not None:
        a1_extra["base_url"] = base_url
    if api_key is not None:
        a1_extra["api_key"] = api_key

    agent = A1(path=path, llm=llm, **a1_extra, **a1_kwargs)
    agent._baponi_executor = executor

    if max_tokens is not None and hasattr(agent.llm, "max_tokens"):
        try:
            agent.llm.max_tokens = max_tokens
        except Exception as e:
            print(f"[baponi-biomni] could not set max_tokens={max_tokens}: {e}")
    return agent
