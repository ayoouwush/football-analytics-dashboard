from pathlib import Path
import pandas as pd
import streamlit as st

CSV_PATH = Path(__file__).resolve().parent.parent / "football_players.csv"
REQUIRED_COLUMNS = [
    "player_id", "player_name", "team", "position", "season", "nationality", "age",
    "matches_played", "minutes_played", "goals", "assists", "shots", "shots_on_target",
    "key_passes", "pass_accuracy", "tackles", "interceptions", "saves", "clean_sheets",
    "yellow_cards", "red_cards", "rating",
]


@st.cache_data
def load_data() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError("football_players.csv not found. Run `python data_generator.py` first.")
    return pd.read_csv(CSV_PATH)


def missing_columns(df: pd.DataFrame) -> list:
    return [c for c in REQUIRED_COLUMNS if c not in df.columns]


def aggregate_players(df: pd.DataFrame) -> pd.DataFrame:
    """One row per player across whatever seasons are in df."""
    return (df.groupby(["player_id", "player_name", "team", "position"], as_index=False)
            .agg(seasons=("season", "nunique"), matches_played=("matches_played", "sum"),
                 minutes_played=("minutes_played", "sum"), goals=("goals", "sum"),
                 assists=("assists", "sum"), shots=("shots", "sum"),
                 shots_on_target=("shots_on_target", "sum"), key_passes=("key_passes", "sum"),
                 tackles=("tackles", "sum"), interceptions=("interceptions", "sum"),
                 saves=("saves", "sum"), clean_sheets=("clean_sheets", "sum"),
                 yellow_cards=("yellow_cards", "sum"), red_cards=("red_cards", "sum"),
                 pass_accuracy=("pass_accuracy", "mean"), rating=("rating", "mean"))
            .round({"pass_accuracy": 1, "rating": 2}))
