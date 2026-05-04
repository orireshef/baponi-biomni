from __future__ import annotations

from baponi_biomni import BaponiExecutor


_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32  # minimal stub bytes for test


def test_new_plots_appended_to_captured_plots(fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t1")
    fake_baponi.add_file("t1", "_plots/a.png", _PNG_MAGIC)
    fake_baponi.add_file("t1", "_plots/b.png", _PNG_MAGIC + b"diff")

    ex.python("# create plots")

    plots = fake_biomni._captured_plots
    assert len(plots) == 2
    assert all(p.startswith("data:image/png;base64,") for p in plots)


def test_plots_deduped_across_calls(fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t2")
    fake_baponi.add_file("t2", "_plots/a.png", _PNG_MAGIC)
    ex.python("plot 1")
    assert len(fake_biomni._captured_plots) == 1

    # second call: same file present, no new ones
    ex.python("plot 2")
    assert len(fake_biomni._captured_plots) == 1

    # third call: a new file appears
    fake_baponi.add_file("t2", "_plots/b.png", _PNG_MAGIC + b"x")
    ex.python("plot 3")
    assert len(fake_biomni._captured_plots) == 2


def test_non_png_files_ignored(fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t3")
    fake_baponi.add_file("t3", "_plots/notes.txt", b"hi")
    fake_baponi.add_file("t3", "_plots/a.png", _PNG_MAGIC)
    ex.python("x")
    assert len(fake_biomni._captured_plots) == 1
