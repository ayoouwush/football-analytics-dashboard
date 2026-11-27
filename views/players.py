import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import theme
from utils.data_loader import aggregate_players
from utils.filters import download_button

RADAR = ["goals", "assists", "key_passes", "pass_accuracy", "tackles", "interceptions"]


def render(df):
    st.title("🧑‍🎤 Player Analysis")
    tot = aggregate_players(df)

    st.subheader("Radar comparison")
    names = sorted(tot["player_name"])
    default = tot.nlargest(3, "rating")["player_name"].tolist()
    picked = st.multiselect("Pick 2 to 6 players", names, default=default, max_selections=6)
    if len(picked) < 2:
        st.info("Select at least 2 players to compare.")
    else:
        rows = tot[tot["player_name"].isin(picked)]
        theme.show_chart(theme.radar_chart(rows, "player_name", RADAR, tot))

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(tot, x="assists", y="goals", color="position", size="minutes_played",
                         color_discrete_map=theme.POS_COLORS, hover_name="player_name",
                         hover_data=["team"], title="Goals vs assists")
        theme.show_chart(theme.style_fig(fig))
    with c2:
        fig = px.scatter(tot, x="shots_on_target", y="goals", color="position",
                         color_discrete_map=theme.POS_COLORS, hover_name="player_name",
                         title="Shots on target vs goals")
        if len(tot) > 2 and tot["shots_on_target"].nunique() > 1:
            slope, intercept = np.polyfit(tot["shots_on_target"], tot["goals"], 1)
            xs = np.array([tot["shots_on_target"].min(), tot["shots_on_target"].max()])
            fig.add_trace(go.Scatter(x=xs, y=slope * xs + intercept, mode="lines", name="Trend",
                                     line=dict(color="#FFFFFF", dash="dash")))
        theme.show_chart(theme.style_fig(fig))

    st.subheader("Stats table")
    q = st.text_input("🔍 Search player or team", "").strip()
    table = tot
    if q:
        mask = tot["player_name"].str.contains(q, case=False) | tot["team"].str.contains(q, case=False)
        table = tot[mask]
    if table.empty:
        st.warning(f"No players match “{q}”.")
    else:
        theme.show_table(table.drop(columns=["player_id"]).sort_values("rating", ascending=False))
        download_button(table, filename="player_stats.csv", key="dl_players")
