"""ADMET prediction demo, mirrors biomni's README hello-world.

Routes biomni's code execution through Baponi sandbox. LLM calls go to a local
LM Studio server (OpenAI-compatible) at http://127.0.0.1:1234/v1.

Usage:
    cp .env.example .env  # set BAPONI_API_KEY (and optionally BAPONI_BASE_URL)
    # Start LM Studio with a chat model loaded at port 1234
    uv run python examples/admet.py
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

from baponi_biomni import make_agent


def main() -> None:
    load_dotenv()
    agent = make_agent(
        path="./data",
        llm=os.environ.get("LLM_MODEL", "qwen3.6-35b-a3b-nvfp4"),
        source="Custom",
        base_url=os.environ.get("LLM_BASE_URL", "http://127.0.0.1:1234/v1"),
        api_key="lm-studio",
        timeout=600,
        expected_data_lake_files=[],  # skip the 12GB+ data lake download for the demo
    )
    agent.go(
        "Predict ADMET properties for the molecule with SMILES "
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O (ibuprofen)."
    )


if __name__ == "__main__":
    main()
