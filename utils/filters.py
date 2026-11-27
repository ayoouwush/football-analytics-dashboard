import streamlit as st


def sidebar_filters(df):
    """Cascading filters: season -> team -> position -> player. Returns the filtered frame."""
    st.sidebar.subheader("🎛️ Filters")
    seasons = sorted(df["season"].unique())
    sel_seasons = st.sidebar.multiselect("Season", seasons, default=seasons)
    d = df[df["season"].isin(sel_seasons)]

    teams = sorted(d["team"].unique())
    sel_teams = st.sidebar.multiselect("Team", teams, default=teams)
    d = d[d["team"].isin(sel_teams)]

    positions = [p for p in ["GK", "DEF", "MID", "FWD"] if p in d["position"].unique()]
    sel_pos = st.sidebar.multiselect("Position", positions, default=positions)
    d = d[d["position"].isin(sel_pos)]

    players = sorted(d["player_name"].unique())
    sel_players = st.sidebar.multiselect("Player", players, default=players)
    d = d[d["player_name"].isin(sel_players)]
    return d


def download_button(df, label="⬇️ Download filtered CSV", filename="football_filtered.csv", key=None):
    st.download_button(label, df.to_csv(index=False).encode("utf-8"), filename, "text/csv", key=key)
