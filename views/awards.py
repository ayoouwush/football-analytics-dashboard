import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import theme
from utils.data_loader import aggregate_players

# 4-3-3 coordinates on a 100 x 100 pitch (x across, y up)
FORMATION = {
    "GK": [(50, 8)],
    "DEF": [(15, 28), (38, 26), (62, 26), (85, 28)],
    "MID": [(25, 52), (50, 48), (75, 52)],
    "FWD": [(20, 78), (50, 84), (80, 78)],
}


def card(title, row, stat):
    st.markdown(f'<div class="award"><div class="title">{title}</div>'
                f'<div class="name">{row["player_name"]}</div>'
                f'<div class="meta">{row["team"]} · {row["position"]}</div>'
                f'<div class="stat">{stat}</div></div>', unsafe_allow_html=True)


def pitch_figure(xi):
    fig = go.Figure()
    line = dict(color="rgba(255,255,255,0.7)", width=2)
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=line, fillcolor="#1B6B3A", layer="below")
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=line)
    fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60, line=line)
    for y0, y1 in [(0, 16), (84, 100)]:
        fig.add_shape(type="rect", x0=20, y0=y0, x1=80, y1=y1, line=line)
    for pos in theme.POS_ORDER:
        sub = xi[xi["position"] == pos]
        coords = FORMATION[pos][:len(sub)]
        fig.add_trace(go.Scatter(
            x=[c[0] for c in coords], y=[c[1] for c in coords], mode="markers+text", name=pos,
            marker=dict(size=34, color=theme.POS_COLORS[pos], line=dict(color="white", width=2)),
            text=[f"{r:.1f}" for r in sub["rating"]], textfont=dict(color="black", size=12),
            customdata=sub[["player_name", "team"]].values,
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<br>Rating %{text}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=[c[0] for c in coords], y=[c[1] - 6 for c in coords], mode="text", showlegend=False,
            text=[n.split(" ")[-1] for n in sub["player_name"]], textfont=dict(color="white", size=13),
            hoverinfo="skip"))
    fig.update_xaxes(visible=False, range=[-3, 103], fixedrange=True)
    fig.update_yaxes(visible=False, range=[-3, 103], scaleanchor="x", fixedrange=True)
    return theme.style_fig(fig, 640)


def render(df):
    st.title("🏆 Awards")
    seasons = sorted(df["season"].unique())
    scope = st.selectbox("Season", ["All selected seasons"] + seasons)
    d = df if scope == "All selected seasons" else df[df["season"] == scope]
    tot = aggregate_players(d)
    if tot.empty:
        st.warning("No data for awards.")
        return

    st.subheader("Player of the Season")
    a, b, c, e = st.columns(4)
    with a:
        r = tot.nlargest(1, "rating").iloc[0]
        card("Player of the Season", r, f"Rating {r['rating']:.2f}")
    with b:
        r = tot.nlargest(1, "goals").iloc[0]
        card("Golden Boot", r, f"{int(r['goals'])} goals")
    with c:
        r = tot.nlargest(1, "assists").iloc[0]
        card("Playmaker", r, f"{int(r['assists'])} assists")
    with e:
        gks = tot[tot["position"] == "GK"]
        if gks.empty:
            st.info("No goalkeepers in the current filter.")
        else:
            r = gks.nlargest(1, "saves").iloc[0]
            card("Golden Glove", r, f"{int(r['saves'])} saves")

    st.subheader("Best XI (4-3-3)")
    need = {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3}
    xi = pd.concat([tot[tot["position"] == p].nlargest(n, "rating") for p, n in need.items()])
    short = [p for p, n in need.items() if len(xi[xi["position"] == p]) < n]
    if short:
        st.warning("Not enough players to fill: " + ", ".join(short) + ". Widen your filters for a full XI.")
    if xi.empty:
        return
    theme.show_chart(pitch_figure(xi))
