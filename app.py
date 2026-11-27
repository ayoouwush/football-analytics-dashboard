import streamlit as st

from utils import theme
from utils.data_loader import load_data, missing_columns
from utils.filters import download_button, sidebar_filters
from views import awards, overview, players, positions, teams

st.set_page_config(page_title="Football Analytics", page_icon="⚽", layout="wide")
theme.apply_css()

PAGES = {
    "📊 Overview": overview,
    "🧑‍🎤 Player Analysis": players,
    "🏟️ Team Analysis": teams,
    "🎯 Position Analysis": positions,
    "🏆 Awards": awards,
}

try:
    data = load_data()
except FileNotFoundError as err:
    st.error(str(err))
    st.stop()

missing = missing_columns(data)
if missing:
    st.error(f"The dataset is missing required columns: {', '.join(missing)}")
    st.stop()

st.sidebar.title("⚽ Football Analytics")
page = st.sidebar.radio("Navigate", list(PAGES), label_visibility="collapsed")
st.sidebar.divider()
filtered = sidebar_filters(data)
st.sidebar.caption(f"{len(filtered)} of {len(data)} rows selected")
st.sidebar.divider()
st.sidebar.caption("⚠️ Synthetic data: all players, clubs and stats are randomly generated.")

if filtered.empty:
    st.warning("No data matches the current filters. Select at least one value in every filter.")
    st.stop()

PAGES[page].render(filtered)
if page == "📊 Overview":
    download_button(filtered, key="dl_overview")
