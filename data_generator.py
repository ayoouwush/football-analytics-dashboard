"""Builds football_players.csv: 120 synthetic players x 3 seasons = 360 rows (seed 42).
Everything is randomly generated. No real players, clubs or results."""
import numpy as np
import pandas as pd

SEED = 42
SEASONS = ["2022/23", "2023/24", "2024/25"]
TEAMS = ["Riverside FC", "Northgate United", "Harbor City", "Crestwood Rovers",
         "Ironvale Athletic", "Sunhill Town", "Redstone FC", "Bluewater Albion",
         "Oakfield Wanderers", "Stormbridge FC", "Goldcoast City", "Highpeak Rangers"]
POS_COUNTS = {"GK": 12, "DEF": 40, "MID": 40, "FWD": 28}
FIRST = ["Alex", "Marco", "Liam", "Noah", "Ethan", "Lucas", "Mateo", "Omar", "Kai", "Leo",
         "Diego", "Ivan", "Felix", "Hugo", "Samir", "Tariq", "Jonas", "Rafael", "Yusuf", "Dario",
         "Nico", "Pavel", "Andre", "Luka", "Tomas", "Elias", "Bruno", "Kofi", "Ravi", "Sven"]
LAST = ["Silva", "Novak", "Okafor", "Moreau", "Haddad", "Larsen", "Costa", "Petrov", "Reyes",
        "Tanaka", "Bauer", "Rossi", "Khan", "Duarte", "Lindqvist", "Mensah", "Varga", "Ortega",
        "Fischer", "Nakamura", "Bianchi", "Kowalski", "Diallo", "Santos", "Jensen"]
NATIONS = ["Spain", "Brazil", "France", "Germany", "Nigeria", "Argentina", "Portugal",
           "Netherlands", "Italy", "England", "Japan", "Morocco", "Croatia", "Sweden", "Ghana"]

# per-match rates by position
RATES = {
    "goals":   {"GK": 0.0,  "DEF": 0.04, "MID": 0.10, "FWD": 0.35},
    "assists": {"GK": 0.0,  "DEF": 0.06, "MID": 0.16, "FWD": 0.15},
    "shots":   {"GK": 0.0,  "DEF": 0.5,  "MID": 1.2,  "FWD": 2.5},
    "key":     {"GK": 0.05, "DEF": 0.4,  "MID": 1.3,  "FWD": 0.9},
    "tackles": {"GK": 0.05, "DEF": 2.2,  "MID": 1.8,  "FWD": 0.6},
    "inter":   {"GK": 0.1,  "DEF": 1.8,  "MID": 1.0,  "FWD": 0.3},
}
PASS_BASE = {"GK": 70, "DEF": 84, "MID": 86, "FWD": 79}


def build() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    positions = [p for p, n in POS_COUNTS.items() for _ in range(n)]
    names, used = [], set()
    while len(names) < len(positions):
        n = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        if n not in used:
            used.add(n)
            names.append(n)

    rows = []
    for i, pos in enumerate(positions):
        pid = i + 1
        team = TEAMS[i % len(TEAMS)]
        nation = rng.choice(NATIONS)
        age0 = int(rng.integers(18, 34))
        ability = rng.normal(0, 1)
        for s, season in enumerate(SEASONS):
            form = np.exp(0.35 * (ability + rng.normal(0, 0.4)))
            m = int(rng.integers(16, 39))
            mins = int(min(m * 90, m * rng.uniform(55, 90)))
            g = int(rng.poisson(m * RATES["goals"][pos] * form))
            a = int(rng.poisson(m * RATES["assists"][pos] * form))
            shots = max(g, int(rng.poisson(m * RATES["shots"][pos] * form)))
            sot = g + int(rng.binomial(shots - g, 0.4))
            rows.append(dict(
                player_id=pid, player_name=names[i], team=team, position=pos, season=season,
                nationality=nation, age=age0 + s, matches_played=m, minutes_played=mins,
                goals=g, assists=a, shots=shots, shots_on_target=sot,
                key_passes=int(rng.poisson(m * RATES["key"][pos] * form)),
                pass_accuracy=round(float(np.clip(rng.normal(PASS_BASE[pos] + 2 * ability, 3), 55, 97)), 1),
                tackles=int(rng.poisson(m * RATES["tackles"][pos] * form)),
                interceptions=int(rng.poisson(m * RATES["inter"][pos] * form)),
                saves=int(rng.poisson(m * 2.8 * form)) if pos == "GK" else 0,
                clean_sheets=int(rng.binomial(m, 0.30 if pos == "GK" else 0.25)) if pos in ("GK", "DEF") else 0,
                yellow_cards=int(rng.poisson(m * 0.12)),
                red_cards=int(rng.poisson(m * 0.008)),
            ))
    df = pd.DataFrame(rows)

    def norm(x):
        return (x - x.min()) / (x.max() - x.min())

    defensive = df["tackles"] + df["interceptions"] + df["saves"]
    raw = (0.30 * norm(df["goals"]) + 0.20 * norm(df["assists"]) + 0.20 * norm(df["pass_accuracy"])
           + 0.15 * norm(defensive) + 0.15 * norm(df["minutes_played"]))
    df["rating"] = (5.0 + 4.5 * norm(raw)).round(2)
    return df


if __name__ == "__main__":
    data = build()
    data.to_csv("football_players.csv", index=False)
    print(f"Saved football_players.csv: {data.shape[0]} rows x {data.shape[1]} columns")
