import plotly.express as px
import streamlit as st

from utils import theme

RADAR = ["goals", "assists", "key_passes", "tackles", "interceptions", "pass_accuracy"]


def team_table(df):
    return (df.groupby("team", as_index=False)
            .agg(players=("player_id", "nunique"), goals=("goals", "sum"), assists=("assists", "sum"),
                 key_passes=("key_passes", "sum"), tackles=("tackles", "sum"),
                 interceptions=("interceptions", "sum"), clean_sheets=("clean_sheets", "sum"),
                 minutes_played=("minutes_played", "sum"), pass_accuracy=("pass_accuracy", "mean"),
                 avg_rating=("rating", "mean")).round({"pass_accuracy": 1, "avg_rating": 2}))


def render(df):
    st.title("🏟️ Team Analysis")
    t = team_table(df)

    c1, c2 = st.columns(2)
    with c1:
        m = t.melt(id_vars="team", value_vars=["goals", "assists"], var_name="stat", value_name="total")
        fig = px.bar(m.sort_values("total", ascending=False), x="team", y="total", color="stat",
                     barmode="group", title="Goals and assists per team")
        theme.show_chart(theme.style_fig(fig))
    with c2:
        comp = df.groupby(["team", "position"])["player_id"].nunique().reset_index(name="players")
        fig = px.bar(comp, x="team", y="players", color="position", color_discrete_map=theme.POS_COLORS,
                     category_orders={"position": theme.POS_ORDER}, title="Squad composition")
        theme.show_chart(theme.style_fig(fig))

    fig = px.scatter(t, x="players", y="avg_rating", size="goals", text="team", title="Squad size vs average rating",
                     color_discrete_sequence=[theme.PALETTE[0]])
    fig.update_traces(textposition="top center")
    theme.show_chart(theme.style_fig(fig))

    st.subheader("Team radar comparison")
    teams = t["team"].tolist()
    picked = st.multiselect("Pick 2 to 6 teams", teams, default=teams[:3], max_selections=6)
    if len(picked) < 2:
        st.info("Select at least 2 teams to compare.")
    else:
        theme.show_chart(theme.radar_chart(t[t["team"].isin(picked)], "team", RADAR, t))

    st.subheader("Summary table")
    theme.show_table(t.sort_values("avg_rating", ascending=False))
