import plotly.express as px
import streamlit as st

from utils import theme
from utils.data_loader import aggregate_players

DEEP = {  # position -> (stats to rank by, extra columns)
    "GK": ["saves", "clean_sheets"],
    "DEF": ["tackles", "interceptions", "clean_sheets"],
    "MID": ["assists", "key_passes", "pass_accuracy"],
    "FWD": ["goals", "shots_on_target", "assists"],
}


def render(df):
    st.title("🎯 Position Analysis")
    order = {"position": theme.POS_ORDER}

    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(df, x="position", y="rating", color="position", color_discrete_map=theme.POS_COLORS,
                     category_orders=order, title="Rating by position")
        theme.show_chart(theme.style_fig(fig))
    with c2:
        metrics = ["goals", "assists", "key_passes", "tackles", "interceptions"]
        avg = df.groupby("position")[metrics].mean().reset_index().melt(
            id_vars="position", var_name="stat", value_name="average")
        fig = px.bar(avg, x="stat", y="average", color="position", barmode="group",
                     color_discrete_map=theme.POS_COLORS, category_orders=order,
                     title="Average stats per player-season")
        theme.show_chart(theme.style_fig(fig))

    fig = px.scatter(df, x="pass_accuracy", y="rating", color="position", color_discrete_map=theme.POS_COLORS,
                     hover_name="player_name", category_orders=order, title="Pass accuracy vs rating")
    theme.show_chart(theme.style_fig(fig))

    st.subheader("Deep dive")
    tot = aggregate_players(df)
    tabs = st.tabs(["🧤 GK", "🛡️ DEF", "🎼 MID", "⚡ FWD"])
    for tab, pos in zip(tabs, theme.POS_ORDER):
        with tab:
            sub = tot[tot["position"] == pos]
            if sub.empty:
                st.info(f"No {pos} players in the current filter.")
                continue
            stats = DEEP[pos]
            choice = st.selectbox("Rank by", stats, key=f"rank_{pos}", format_func=theme.pretty)
            top = sub.nlargest(10, choice).sort_values(choice)
            fig = px.bar(top, x=choice, y="player_name", orientation="h", hover_data=["team"],
                         color_discrete_sequence=[theme.POS_COLORS[pos]], title=f"Top {pos} by {theme.pretty(choice)}")
            fig.update_yaxes(title="")
            theme.show_chart(theme.style_fig(fig, 380))
            theme.show_table(sub[["player_name", "team"] + stats + ["rating"]].sort_values(choice, ascending=False))
