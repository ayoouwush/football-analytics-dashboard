import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils import kpis, theme
from utils.data_loader import aggregate_players


def render(df):
    st.title("📊 Overview")
    theme.kpi_row([
        ("Players", f"{kpis.total_players(df):,}"),
        ("Goals", f"{kpis.total_goals(df):,}"),
        ("Assists", f"{kpis.total_assists(df):,}"),
        ("Minutes", f"{kpis.total_minutes(df):,}"),
        ("Avg rating", f"{kpis.average_rating(df):.2f}"),
    ])
    tot = aggregate_players(df)

    c1, c2 = st.columns(2)
    with c1:
        top = tot.nlargest(10, "goals").sort_values("goals")
        fig = px.bar(top, x="goals", y="player_name", orientation="h", color="position",
                     color_discrete_map=theme.POS_COLORS, hover_data=["team"], title="Top 10 scorers")
        fig.update_yaxes(title="")
        theme.show_chart(theme.style_fig(fig))
    with c2:
        share = df.groupby("position", as_index=False)["goals"].sum()
        fig = px.pie(share, names="position", values="goals", hole=0.5, color="position",
                     color_discrete_map=theme.POS_COLORS, title="Goals share by position")
        theme.show_chart(theme.style_fig(fig))

    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(df, x="rating", nbins=20, title="Rating distribution",
                           color_discrete_sequence=[theme.PALETTE[0]])
        theme.show_chart(theme.style_fig(fig))
    with c4:
        trend = df.groupby("season", as_index=False).agg(goals=("goals", "sum"), rating=("rating", "mean"))
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=trend["season"], y=trend["goals"], name="Goals",
                             marker_color=theme.PALETTE[0]), secondary_y=False)
        fig.add_trace(go.Scatter(x=trend["season"], y=trend["rating"], name="Avg rating",
                                 mode="lines+markers", line=dict(color=theme.PALETTE[1])), secondary_y=True)
        fig.update_layout(title="Season trend")
        fig.update_yaxes(title_text="Goals", secondary_y=False)
        fig.update_yaxes(title_text="Avg rating", secondary_y=True, showgrid=False)
        theme.show_chart(theme.style_fig(fig))
