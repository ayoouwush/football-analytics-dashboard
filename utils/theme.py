import plotly.graph_objects as go
import streamlit as st

PALETTE = ["#1DB954", "#F5C542", "#4FC3F7", "#FF7043", "#BA68C8", "#26A69A", "#EF5350", "#9CCC65"]
POS_COLORS = {"GK": "#F5C542", "DEF": "#4FC3F7", "MID": "#1DB954", "FWD": "#FF7043"}
POS_ORDER = ["GK", "DEF", "MID", "FWD"]

CSS = """
<style>
.block-container {padding-top: 2rem;}
h1, h2, h3 {color: #E8F5E9;}
.kpi {background: linear-gradient(135deg, #12301F, #0F2A1A); border: 1px solid #1DB95455;
      border-radius: 14px; padding: 16px 18px; text-align: center;}
.kpi .label {font-size: 0.8rem; color: #9CCFAE; text-transform: uppercase; letter-spacing: .08em;}
.kpi .value {font-size: 1.9rem; font-weight: 700; color: #1DB954;}
.award {background: linear-gradient(135deg, #12301F, #0B1F14); border: 1px solid #F5C54299;
        border-radius: 16px; padding: 18px; height: 100%;}
.award .title {font-size: .8rem; color: #F5C542; text-transform: uppercase; letter-spacing: .1em;}
.award .name {font-size: 1.35rem; font-weight: 700; margin: 6px 0 2px;}
.award .meta {color: #9CCFAE; font-size: .9rem;}
.award .stat {margin-top: 10px; font-size: 1.1rem; color: #1DB954; font-weight: 600;}
</style>
"""


def apply_css():
    st.markdown(CSS, unsafe_allow_html=True)


def pretty(col: str) -> str:
    return col.replace("_", " ").title()


def style_fig(fig, height=420):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8F5E9"), colorway=PALETTE, height=height,
        margin=dict(l=10, r=10, t=50, b=10), legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#1f4a31")
    fig.update_yaxes(gridcolor="#1f4a31")
    return fig


def show_chart(fig):
    """Works on old and new Streamlit (use_container_width was replaced by width='stretch')."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def show_table(df, **kwargs):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


def kpi_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.markdown(f'<div class="kpi"><div class="label">{label}</div>'
                     f'<div class="value">{value}</div></div>', unsafe_allow_html=True)
    st.write("")


def radar_chart(rows, label_col, metrics, ref, title=""):
    """Radar of `rows`, each metric scaled 0-100 against the max in `ref`."""
    mx = ref[metrics].max().replace(0, 1)
    theta = [pretty(m) for m in metrics]
    fig = go.Figure()
    for i, (_, r) in enumerate(rows.iterrows()):
        vals = [float(r[m] / mx[m] * 100) for m in metrics]
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=theta + theta[:1], fill="toself", name=str(r[label_col]),
            opacity=0.55, line=dict(color=PALETTE[i % len(PALETTE)])))
    fig.update_layout(title=title, polar=dict(
        bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 100], gridcolor="#2a5a3a", showticklabels=False),
        angularaxis=dict(gridcolor="#2a5a3a")))
    return style_fig(fig, 480)
