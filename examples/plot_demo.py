"""Smoke test: BaponiExecutor.python plus plot capture.

Runs without booting the full A1 agent. Verifies:
  1. State persists across calls (cloudpickle round-trip).
  2. Plots saved with plt.savefig surface in biomni._captured_plots.
"""
from __future__ import annotations

from dotenv import load_dotenv

from baponi_biomni import BaponiExecutor


def main() -> None:
    load_dotenv()
    ex = BaponiExecutor(timeout=600)
    print(f"thread_id: {ex.thread_id}")

    print("\n--- step 1: define x ---")
    print(ex.python("x = 42; print('set x =', x)"))

    print("\n--- step 2: read x back ---")
    print(ex.python("print('x is still', x)"))

    print("\n--- step 3: install matplotlib + plot ---")
    print(ex.bash("pip install --quiet matplotlib"))
    out = ex.python(
        "import matplotlib.pyplot as plt\n"
        "plt.plot([1, 2, 3, 2, 1])\n"
        "plt.title('demo')\n"
        "plt.savefig('out.png')\n"
    )
    print(out)

    from biomni.tool import support_tools

    plots = support_tools.get_captured_plots()
    print(f"\ncaptured plots: {len(plots)}")
    if plots:
        print(f"first plot prefix: {plots[0][:60]}...")


if __name__ == "__main__":
    main()
