from __future__ import annotations

import base64
import os
import re
from uuid import uuid4

import httpx
from baponi import Baponi

from .errors import RNotSupportedError
from .prologue import wrap

_FENCE_RE = re.compile(r"^\s*```(?:python|py|bash|sh)?\s*\n?|\n?```\s*$", re.MULTILINE)


def _strip_fences(code: str) -> str:
    return _FENCE_RE.sub("", code).strip()


def _make_thread_id(prefix: str = "biomni") -> str:
    return f"{prefix}-{uuid4().hex[:16]}"


class BaponiExecutor:
    """Routes biomni's 4 exec functions through a Baponi sandbox tied to one thread_id."""

    def __init__(
        self,
        *,
        thread_id: str | None = None,
        timeout: int = 60,
        env_vars: dict[str, str] | None = None,
        client: Baponi | None = None,
        base_url: str | None = None,
    ) -> None:
        if client is None:
            kwargs: dict = {}
            url = base_url or os.environ.get("BAPONI_BASE_URL")
            if url:
                kwargs["base_url"] = url
            client = Baponi(**kwargs)
        self.client = client
        self.thread_id = thread_id or _make_thread_id()
        self.timeout = timeout
        self.env_vars = {k.upper(): v for k, v in (env_vars or {}).items()}
        self._seen_plots: set[str] = set()

    def python(self, command: str) -> str:
        code = _strip_fences(command)
        wrapped = wrap(code)
        result = self.client.execute(
            wrapped,
            language="python",
            timeout=self.timeout,
            thread_id=self.thread_id,
            env_vars=self.env_vars or None,
        )
        self._sync_plots()
        if not result.success:
            return f"Error: {result.stderr.strip() or result.error or 'unknown'}"
        return result.stdout

    def bash(self, script: str) -> str:
        result = self.client.execute(
            script,
            language="bash",
            timeout=self.timeout,
            thread_id=self.thread_id,
            env_vars=self.env_vars or None,
        )
        if not result.success:
            return f"Error (exit {result.exit_code}): {result.stderr.strip() or result.error or ''}"
        return result.stdout

    def cli(self, command: str) -> str:
        return self.bash(command)

    def r(self, code: str) -> str:
        raise RNotSupportedError()

    _PLOTS_DIR = "_plots"

    def _sync_plots(self) -> None:
        """Pull new PNGs from /home/baponi/_plots into biomni's _captured_plots.

        Note: list_files returns paths RELATIVE to the `path` argument (just
        the filename here), but download_url needs the FULL path from the
        /home/baponi root. We compose the full path before downloading.
        """
        try:
            files = self.client.list_files(
                source="thread", id=self.thread_id, path=self._PLOTS_DIR
            )
        except Exception as e:
            print(f"[baponi-biomni] list_files failed: {e}")
            return

        new = [
            f for f in files
            if f.path.endswith(".png") and f.path not in self._seen_plots
        ]
        if not new:
            return

        try:
            from biomni.tool import support_tools
        except ImportError:
            support_tools = None

        for f in new:
            full_path = f"{self._PLOTS_DIR}/{f.path}"
            try:
                signed = self.client.download_url(
                    path=full_path, source="thread", id=self.thread_id
                )
                headers = {h.name: h.value for h in signed.headers}
                resp = httpx.get(signed.url, headers=headers, timeout=30)
                resp.raise_for_status()
                data_uri = (
                    "data:image/png;base64,"
                    + base64.b64encode(resp.content).decode("utf-8")
                )
                if support_tools is not None:
                    if data_uri not in support_tools._captured_plots:
                        support_tools._captured_plots.append(data_uri)
                self._seen_plots.add(f.path)
            except Exception as e:
                print(f"[baponi-biomni] plot fetch failed for {full_path}: {e}")
