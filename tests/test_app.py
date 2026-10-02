# -*- coding: utf-8 -*-
"""Smoke test: every view of the Streamlit app renders without errors.

Streamlit only executes the code path for what is currently on screen, so a
missing dependency or broken chart behind a non-default radio/selectbox choice
goes unnoticed until a visitor clicks there. This test clicks everywhere:
it runs the app headlessly (streamlit.testing AppTest), then re-runs it once
per option of every radio and selectbox.

  - Exceptions and st.error() messages fail the test.
  - st.warning() messages are surfaced as pytest warnings, not failures,
    because some are expected (e.g. optional data unavailable).

Run from the project root:  python -m pytest tests/ -v
Run it in a clean venv built from requirements.txt to mirror Streamlit Cloud.
"""
import warnings
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
TIMEOUT = 180  # seconds per run; first run includes data loading


def _problems(at, label):
    """Collect failures and surface warnings for one app run."""
    for w in at.warning:
        warnings.warn(f"[{label}] st.warning: {w.value}", stacklevel=2)
    return [f"[{label}] exception: {e.value}" for e in at.exception] + [
        f"[{label}] st.error: {e.value}" for e in at.error
    ]


def _fresh(monkeypatch):
    monkeypatch.chdir(ROOT)  # apps read outputs/ etc. via relative paths
    at = AppTest.from_file(str(APP), default_timeout=TIMEOUT)
    at.run()
    return at


def test_every_view_renders(monkeypatch):
    at = _fresh(monkeypatch)
    problems = _problems(at, "default view")

    # Discover every radio/selectbox choice from the default run, then
    # exercise each non-default option in its own fresh session.
    for kind in ("radio", "selectbox"):
        for i, widget in enumerate(getattr(at, kind)):
            for j, option in enumerate(widget.options):
                if j == (widget.index or 0):
                    continue  # already covered by the default run
                run = _fresh(monkeypatch)
                w = getattr(run, kind)[i]
                (w.select_index(j) if kind == "selectbox" else w.set_value(option)).run()
                problems += _problems(run, f"{kind} '{widget.label}' = {option}")

    assert not problems, "\n".join(problems)


def test_date_labels_are_not_open_ended(monkeypatch):
    """The app shows a fixed snapshot, so no label may claim data runs to 'Present'.

    Date ranges should be derived from the data (see get_coverage in app.py).
    """
    import re

    at = _fresh(monkeypatch)
    texts = [e.value for kind in ("title", "subheader", "markdown", "caption", "info")
             for e in getattr(at, kind)]
    texts += [chart.proto.spec for chart in at.get("plotly_chart")]  # figure JSON incl. titles
    hits = [t[:120] for t in texts if re.search(r"\bpresent\b", t, re.IGNORECASE)]
    assert not hits, "Open-ended date label(s) found:\n" + "\n".join(hits)
