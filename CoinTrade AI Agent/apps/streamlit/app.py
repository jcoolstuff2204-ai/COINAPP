from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for relative in [
    "apps/api",
    "packages/schemas",
    "services/persistence",
    "services/market_ingestion",
    "services/feature_engine",
    "services/risk_engine",
    "services/signal_engine",
    "services/paper_execution",
    "services/ai_explanation",
    "apps/streamlit",
]:
    sys.path.insert(0, str(ROOT / relative))

import streamlit as st

from quantrade_streamlit.adapter import load_dashboard_data


st.set_page_config(
    page_title="QuanTrade AI Agent",
    page_icon="QT",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def dashboard_data() -> dict[str, object]:
    return load_dashboard_data("fixture")


def badge(text: str) -> None:
    st.markdown(f"`{text}`")


data = dashboard_data()
scanner_signal = data["scanner"]["signals"][0]
explanation = scanner_signal["explanation"]
portfolio = data["portfolio"]["portfolio"]
health = data["data_health"]["items"][0]
book = data["replay"]["book"]

st.sidebar.title("QuanTrade")
st.sidebar.caption("Smarter signals. Calmer trading.")
st.sidebar.warning("DEMO DATA")
st.sidebar.success("Paper mode only")
st.sidebar.info("Live trading unavailable")
if st.sidebar.button("Replay fixture"):
    st.cache_data.clear()
    st.rerun()

st.title("QuanTrade AI Agent")
st.caption("Temporary Streamlit test harness for deterministic fixture mode.")

top_a, top_b, top_c, top_d = st.columns(4)
top_a.metric("Portfolio equity", f"${portfolio['equity']:,.2f}")
top_b.metric("Open risk", f"${portfolio['open_risk']:,.2f}")
top_c.metric("Best opportunity", f"{scanner_signal['opportunity_score']:.2f}")
top_d.metric("Feed status", health["status"].title())

tabs = st.tabs(["Command Center", "Scanner", "Signal Detail", "Replay & Health", "Paper Portfolio"])

with tabs[0]:
    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Best Opportunity")
        st.write(f"**{scanner_signal['symbol']}** · {scanner_signal['behavioral_state'].replace('_', ' ')}")
        st.progress(min(scanner_signal["opportunity_score"] / 100, 1.0), text="Opportunity score")
        st.write(explanation["summary"])
        st.write("**Thesis**")
        st.write(explanation["thesis"])
        st.write("**Counter-thesis**")
        st.write(explanation["counter_thesis"])
    with right:
        st.subheader("Risk Controls")
        st.metric("Risk score", f"{scanner_signal['risk_score']:.2f}")
        st.metric("Manipulation score", f"{scanner_signal['manipulation_score']:.2f}")
        st.write("Status")
        badge(scanner_signal["status"])
        st.write("Warnings")
        for warning in scanner_signal["warnings"]:
            st.warning(warning)

with tabs[1]:
    st.subheader("Market Scanner")
    rows = [
        {
            "Rank": 1,
            "Symbol": scanner_signal["symbol"],
            "Strategy": scanner_signal["strategy"],
            "State": scanner_signal["behavioral_state"],
            "Opportunity": scanner_signal["opportunity_score"],
            "Risk": scanner_signal["risk_score"],
            "Manipulation": scanner_signal["manipulation_score"],
            "Status": scanner_signal["status"],
        }
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("Fixture scanner output is deterministic and labeled as demo data.")

with tabs[2]:
    st.subheader("Signal Detail")
    plan_a, plan_b, plan_c = st.columns(3)
    plan_a.metric("Entry low", f"${scanner_signal['entry_zone'][0]:,.2f}")
    plan_b.metric("Entry high", f"${scanner_signal['entry_zone'][1]:,.2f}")
    plan_c.metric("Invalidation", f"${scanner_signal['invalidation_price']:,.2f}")
    st.write("Component Contributions")
    st.dataframe(scanner_signal["components"], use_container_width=True, hide_index=True)
    st.write("Timeline")
    st.dataframe(data["signal_detail"]["timeline"], use_container_width=True, hide_index=True)
    st.write("Execution guidance")
    st.info(explanation["execution_guidance"])

with tabs[3]:
    st.subheader("Replay & Data Health")
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Events processed", data["replay"]["events_processed"])
    h2.metric("Order book valid", str(book["valid"]))
    h3.metric("Checksum", book["checksum_status"])
    h4.metric("Spread", f"{book['spread_bps']} bps")
    st.write("Top of Book")
    col_bid, col_ask = st.columns(2)
    col_bid.dataframe(book["bids"], use_container_width=True, hide_index=True, column_config={"0": "Bid", "1": "Quantity"})
    col_ask.dataframe(book["asks"], use_container_width=True, hide_index=True, column_config={"0": "Ask", "1": "Quantity"})
    st.write("Health")
    st.json(health)

with tabs[4]:
    st.subheader("Paper Portfolio")
    st.write("Latest paper order")
    st.json(data["paper_order"]["order"])
    st.write("Open positions")
    st.dataframe(data["positions"]["positions"], use_container_width=True, hide_index=True)
    st.write("Journal")
    st.json(data["journal"]["entries"][0])
    st.write("Performance")
    st.json(data["performance"]["performance"])

