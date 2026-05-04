from __future__ import annotations

from baponi_biomni import BaponiExecutor


_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32  # minimal stub bytes for test


def test_new_plots_appended_to_captured_plots(tmp_path, fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t1", host_plots_dir=tmp_path)
    fake_baponi.add_file("t1", "_plots/a.png", _PNG_MAGIC)
    fake_baponi.add_file("t1", "_plots/b.png", _PNG_MAGIC + b"diff")

    ex.python("# create plots")

    plots = fake_biomni._captured_plots
    assert len(plots) == 2
    assert all(p.startswith("data:image/png;base64,") for p in plots)


def test_plots_deduped_across_calls(tmp_path, fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t2", host_plots_dir=tmp_path)
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


def test_non_png_files_ignored(tmp_path, fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t3", host_plots_dir=tmp_path)
    fake_baponi.add_file("t3", "_plots/notes.txt", b"hi")
    fake_baponi.add_file("t3", "_plots/a.png", _PNG_MAGIC)
    ex.python("x")
    assert len(fake_biomni._captured_plots) == 1


def test_plots_written_to_host_dir_and_appended_to_stdout(
    tmp_path, fake_baponi, fake_httpx, fake_biomni
):
    """New PNGs land on host disk and a 'Plot saved to: <abs>' line is
    appended so biomni's gradio path-scanner picks them up."""
    ex = BaponiExecutor(thread_id="t4", host_plots_dir=tmp_path)
    fake_baponi.add_file("t4", "_plots/x.png", _PNG_MAGIC)
    fake_baponi.add_handler(
        lambda c, l, t: ("user-stdout", "", 0) if l == "python" else None
    )

    out = ex.python("plt.savefig('foo')")

    written = list(tmp_path.iterdir())
    assert len(written) == 1
    assert written[0].name == "x.png"
    assert written[0].read_bytes() == _PNG_MAGIC

    assert "user-stdout" in out
    assert f"Plot saved to: {written[0].resolve()}" in out


def test_no_plots_no_stdout_change(tmp_path, fake_baponi, fake_httpx, fake_biomni):
    ex = BaponiExecutor(thread_id="t5", host_plots_dir=tmp_path)
    fake_baponi.add_handler(
        lambda c, l, t: ("just stdout", "", 0) if l == "python" else None
    )

    out = ex.python("nothing visual")

    assert out == "just stdout"
    assert not tmp_path.exists() or list(tmp_path.iterdir()) == []
