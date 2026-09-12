"""
Streamlit Lab — interactive research UI for the factory simulator.

Pages: Home, Configure, Run, Results, Compare, Gallery
Entry: factory-lab
"""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "examples" / "runs"


def main(argv: Optional[List[str]] = None) -> int:
    """Launch the Streamlit lab UI."""
    app_path = Path(__file__).resolve()
    try:
        from streamlit.web import cli as stcli
    except Exception:
        print(
            "Streamlit is required for factory-lab.\n"
            'Install with: pip install -e ".[ui]"',
            file=sys.stderr,
        )
        return 1
    sys.argv = ["streamlit", "run", str(app_path), *(argv or [])]
    stcli.main()
    return 0


def _ensure_streamlit():
    import streamlit as st
    return st


def _load_plotly():
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        return go, make_subplots
    except Exception:
        return None, None


def run_app() -> None:
    st = _ensure_streamlit()
    st.set_page_config(
        page_title="Factory Research Lab",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans', sans-serif;
        }
        .stApp {
            background:
                radial-gradient(1200px 600px at 10% -10%, #d9ece8 0%, transparent 55%),
                radial-gradient(900px 500px at 100% 0%, #e8e2d4 0%, transparent 50%),
                linear-gradient(180deg, #f7f5f0 0%, #eef2f1 100%);
        }
        h1, h2, h3 { font-family: 'IBM Plex Sans', sans-serif; letter-spacing: -0.02em; }
        code, pre { font-family: 'IBM Plex Mono', monospace; }
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1f2a2e 0%, #24353a 100%);
        }
        div[data-testid="stSidebar"] * { color: #e8efec !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "run_log_path" not in st.session_state:
        st.session_state.run_log_path = str(ROOT / "factory_simulation_log.json")
    if "run_progress" not in st.session_state:
        st.session_state.run_progress = None
    if "run_error" not in st.session_state:
        st.session_state.run_error = None
    if "run_thread" not in st.session_state:
        st.session_state.run_thread = None

    pages = ["Home", "Configure", "Run", "Results", "Compare", "Gallery"]
    with st.sidebar:
        st.markdown("### Factory Research Lab")
        st.caption("One engine. Honest bottlenecks.")
        choice = st.radio("Navigate", pages, index=pages.index(st.session_state.page))
        st.session_state.page = choice

    page = st.session_state.page
    if page == "Home":
        _page_home(st)
    elif page == "Configure":
        _page_configure(st)
    elif page == "Run":
        _page_run(st)
    elif page == "Results":
        _page_results(st)
    elif page == "Compare":
        _page_compare(st)
    else:
        _page_gallery(st)


def _page_home(st) -> None:
    st.title("Factory Research Lab")
    st.markdown(
        "What does it really take for a **solar-powered factory** to copy itself "
        "from raw materials?"
    )
    st.markdown(
        "This toolkit runs one replication engine with specs for energy, transport, "
        "software, quality, and maintenance constraints. Counts today: ~138 resources "
        "and ~14 module types in the built-in model (not “250+ / production-ready modular”)."
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Run 5-minute minimal demo", type="primary"):
            st.session_state.config = {
                "spec": "specs/minimal.json",
                "profile": None,
                "max_hours": 200,
                "modular": False,
                "overrides": {},
            }
            st.session_state.page = "Run"
            st.rerun()
    with col2:
        if st.button("Configure a scenario"):
            st.session_state.page = "Configure"
            st.rerun()
    st.markdown("---")
    st.markdown(
        "CLI path: `pip install -e \".[ui]\"` then "
        "`factory-sim --spec specs/minimal.json --max-hours 200` or `factory-lab`."
    )


def _page_configure(st) -> None:
    from factory_simulator.api import list_specs

    st.header("Configure")
    st.caption("Pick a spec, profile, and a few knobs — then run.")

    specs = list_specs()
    labels = [f"{s['name']}  ({Path(s['path']).name})" for s in specs] or ["minimal"]
    paths = [s["path"] for s in specs] or ["specs/minimal.json"]
    idx = 0
    for i, p in enumerate(paths):
        if "minimal" in p:
            idx = i
            break
    choice = st.selectbox("Spec", labels, index=idx)
    spec_path = paths[labels.index(choice)] if choice in labels else "specs/minimal.json"

    profile = st.text_input("Profile (optional)", value="")
    max_hours = st.number_input("Max hours", min_value=10, max_value=20000, value=200, step=10)
    modular = st.checkbox("Hybrid modular plugins (--modular)", value=False)

    st.subheader("Key knobs")
    solar = st.number_input("Initial solar capacity (kW)", min_value=10.0, value=100.0, step=10.0)
    parallel = st.number_input("Parallel processing limit", min_value=1, value=10, step=1)
    enable_degradation = st.checkbox("Enable degradation", value=True)
    enable_weather = st.checkbox("Enable weather", value=True)

    if st.button("Save & go to Run", type="primary"):
        st.session_state.config = {
            "spec": spec_path,
            "profile": profile or None,
            "max_hours": int(max_hours),
            "modular": bool(modular),
            "overrides": {
                "initial_solar_capacity_kw": float(solar),
                "parallel_processing_limit": int(parallel),
                "enable_degradation": bool(enable_degradation),
                "enable_weather": bool(enable_weather),
            },
        }
        st.session_state.page = "Run"
        st.rerun()


def _page_run(st) -> None:
    from factory_simulator.api import run_scenario, summarize_run

    st.header("Run")
    cfg = st.session_state.get("config") or {
        "spec": "specs/minimal.json",
        "profile": None,
        "max_hours": 200,
        "modular": False,
        "overrides": {},
    }
    st.write(
        f"Spec: `{cfg['spec']}` · max_hours={cfg['max_hours']} · "
        f"modular={cfg['modular']}"
    )

    out_path = st.text_input("Output JSON", value=st.session_state.run_log_path)
    st.session_state.run_log_path = out_path

    progress_box = st.empty()
    if st.session_state.run_progress:
        progress_box.json(st.session_state.run_progress)
    if st.session_state.run_error:
        st.error(st.session_state.run_error)

    def _start():
        st.session_state.run_error = None
        st.session_state.run_progress = {"phase": "queued"}

        def worker():
            try:
                def cb(info):
                    st.session_state.run_progress = info

                result = run_scenario(
                    spec=cfg["spec"],
                    profile=cfg.get("profile"),
                    max_hours=cfg["max_hours"],
                    modular=cfg.get("modular", False),
                    output=out_path,
                    progress_cb=cb,
                    config_overrides=cfg.get("overrides") or None,
                    max_wall_time_seconds=min(1800, max(120, cfg["max_hours"] * 2)),
                )
                st.session_state.last_result = result
                st.session_state.run_progress = {
                    "phase": "complete",
                    **summarize_run(result),
                }
            except Exception as exc:
                st.session_state.run_error = str(exc)
                st.session_state.run_progress = {"phase": "error"}

        t = threading.Thread(target=worker, daemon=True)
        st.session_state.run_thread = t
        t.start()

    cols = st.columns(3)
    with cols[0]:
        if st.button("Start run", type="primary"):
            _start()
            st.rerun()
    with cols[1]:
        if st.button("Refresh status"):
            st.rerun()
    with cols[2]:
        if st.button("Open Results"):
            st.session_state.page = "Results"
            st.rerun()

    thread = st.session_state.run_thread
    if thread is not None and thread.is_alive():
        st.info("Run in progress… click Refresh status.")
        time.sleep(0.5)
        st.rerun()


def _metrics_figures(data: Dict[str, Any]):
    go, make_subplots = _load_plotly()
    if go is None:
        return None
    metrics = data.get("metrics") or {}
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Battery (kWh)", "Tasks completed", "Waste", "Transport jobs"),
    )
    battery = metrics.get("battery_charge") or []
    completed = metrics.get("completed_tasks") or []
    waste = metrics.get("waste_generated") or []
    transport = metrics.get("transport_jobs") or []
    if battery:
        fig.add_trace(go.Scatter(y=battery, name="battery", line=dict(color="#2f6f6a")), row=1, col=1)
    if completed:
        fig.add_trace(go.Scatter(y=completed, name="completed", line=dict(color="#8a5a2b")), row=1, col=2)
    if waste:
        fig.add_trace(go.Scatter(y=waste, name="waste", line=dict(color="#5c6b73")), row=2, col=1)
    if transport:
        fig.add_trace(go.Scatter(y=transport, name="transport", line=dict(color="#3d5a80")), row=2, col=2)
    fig.update_layout(height=520, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def _page_results(st) -> None:
    from factory_simulator.api import summarize_run

    st.header("Results")
    path = st.text_input("Result JSON path", value=st.session_state.run_log_path)
    data = st.session_state.last_result
    if data is None and Path(path).exists():
        with open(path) as f:
            data = json.load(f)
            st.session_state.last_result = data
    if not data:
        st.warning("No results yet. Run a scenario first or load a JSON log.")
        return

    summary = summarize_run(data)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", summary["status"])
    c2.metric("Days", f"{summary['time_days']:.1f}")
    c3.metric("Completed tasks", summary["completed_tasks"])
    c4.metric("Blocked tasks", summary["blocked_tasks"])

    st.subheader("Top blockers")
    if summary["top_blockers"]:
        st.table(summary["top_blockers"])
    else:
        st.write("No blocker events recorded in the log tail.")

    fig = _metrics_figures(data)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Install plotly (`pip install -e \".[ui]\"`) for interactive charts.")

    st.download_button(
        "Download JSON",
        data=json.dumps(data, default=str),
        file_name="factory_run.json",
        mime="application/json",
    )


def _page_compare(st) -> None:
    from factory_simulator.api import compare_runs

    st.header("Compare")
    st.caption("Two saved runs side-by-side.")
    a = st.text_input("Run A path", value=str(EXAMPLES_DIR / "minimal_short.json"))
    b = st.text_input("Run B path", value=st.session_state.run_log_path)
    if st.button("Compare", type="primary"):
        if not Path(a).exists() or not Path(b).exists():
            st.error("Both run files must exist.")
            return
        result = compare_runs(a, b)
        left, right = st.columns(2)
        with left:
            st.subheader("A")
            st.json(result["a"])
        with right:
            st.subheader("B")
            st.json(result["b"])
        st.subheader("Deltas (B − A)")
        st.json(result["deltas"])
        st.write(f"Faster: **{result['faster']}**")
        if result.get("blocker_delta"):
            st.subheader("Blocker mix delta")
            st.json(result["blocker_delta"])


def _page_gallery(st) -> None:
    from factory_simulator.api import summarize_run

    st.header("Gallery")
    st.caption("Curated example runs — load and inspect.")
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(EXAMPLES_DIR.glob("*.json"))
    if not files:
        st.warning(
            "No curated examples yet. After demos-docs lands, expect "
            "`minimal_short.json` and a bottleneck sample here."
        )
        return
    labels = [f.name for f in files]
    choice = st.selectbox("Example", labels)
    path = EXAMPLES_DIR / choice
    with open(path) as f:
        data = json.load(f)
    st.json(summarize_run(data))
    if st.button("Load into Results"):
        st.session_state.last_result = data
        st.session_state.run_log_path = str(path)
        st.session_state.page = "Results"
        st.rerun()


# Streamlit executes the script top-to-bottom when run via `streamlit run`.
# The console entry point `factory-lab` calls main() which launches Streamlit.


def _should_render() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if _should_render():
    run_app()
elif __name__ == "__main__":
    raise SystemExit(main())
