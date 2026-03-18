from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from numpy.linalg import norm
from scipy.stats import percentileofscore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "src" / "data" / "raw"
DATA_CLEAN_DIR = PROJECT_ROOT / "src" / "data" / "clean"


METRICS_PER90 = [
    "Goals per 90",
    "xG per 90",
    "xA per 90",
    "Shots per 90",
    "Dribbles per 90",
    "Touches in box per 90",
    "Progressive passes per 90",
]


def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load current and previous season Argentinian players data."""
    DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    cur = pd.read_excel(
        DATA_RAW_DIR / "currentseason_argentinos.xlsx"
    ).assign(Season="Current")
    prev = pd.read_excel(
        DATA_RAW_DIR / "previousseason_argentinos.xlsx"
    ).assign(Season="Previous")

    all_seasons = pd.concat([cur, prev], ignore_index=True)
    all_seasons["Minutes played"] = all_seasons["Minutes played"].astype(float)

    for m in METRICS_PER90:
        if m in all_seasons.columns:
            all_seasons[m] = all_seasons[m].astype(float)

    return cur, prev, all_seasons


def build_player_aggregation(
    cur: pd.DataFrame, prev: pd.DataFrame, all_seasons: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate two seasons per player (per 90 and raw totals)."""
    minutes_col = "Minutes played"

    rows = []
    for player, g in all_seasons.groupby("Player"):
        mins = g[minutes_col].sum()
        data = {"Player": player, minutes_col: mins}

        for m in METRICS_PER90:
            if m not in g.columns:
                continue
            value_per90 = (
                (g[m] * g[minutes_col]).sum() / mins if mins > 0 else np.nan
            )
            data[m] = value_per90

        if "Goals" in g.columns:
            data["Goals"] = g["Goals"].sum()
        if "Shots" in g.columns:
            data["Shots"] = g["Shots"].sum()
        if "xG" in g.columns:
            data["xG"] = g["xG"].sum()
        if "xA" in g.columns:
            data["xA"] = g["xA"].sum()

        if "Touches in box per 90" in g.columns:
            data["Touches in box"] = (
                (g["Touches in box per 90"] * g[minutes_col]).sum() / 90
                if mins > 0
                else np.nan
            )
        if "Progressive passes per 90" in g.columns:
            data["Progressive passes"] = (
                (g["Progressive passes per 90"] * g[minutes_col]).sum() / 90
                if mins > 0
                else np.nan
            )

        if "xG" in g.columns and "xA" in g.columns:
            total_xg = g["xG"].sum()
            total_xa = g["xA"].sum()
            total_xgxa = total_xg + total_xa
            per90_xgxa = total_xgxa * 90 / mins if mins > 0 else np.nan
            data["xG+xA"] = total_xgxa
            data["xG+xA per 90"] = per90_xgxa

        rows.append(data)

    agg = pd.DataFrame(rows)

    for col in ("Goals", "Shots"):
        if col in agg.columns:
            agg[col] = agg[col].round().astype("Int64")

    for col in ("xG", "xA", "xG+xA", "Touches in box", "Progressive passes"):
        if col in agg.columns:
            agg[col] = agg[col].round(2)

    team_current = cur.set_index("Player")["Team"]
    team_any = all_seasons.set_index("Player")["Team"]
    agg["Team"] = agg["Player"].map(lambda p: team_current.get(p, team_any.get(p)))

    per90_cols = [
        m for m in METRICS_PER90 + ["xG+xA per 90"] if m in agg.columns
    ]
    raw_cols = [
        c
        for c in [
            "Goals",
            "xG",
            "xA",
            "Shots",
            "Dribbles",
            "Touches in box",
            "Progressive passes",
            "xG+xA",
        ]
        if c in agg.columns
    ]
    cols = ["Player", "Team", minutes_col] + per90_cols + raw_cols
    agg = agg[cols]

    arg_debug_path = DATA_CLEAN_DIR / "argentinian_agg_debug.xlsx"
    agg.to_excel(arg_debug_path, index=False)

    return agg


def recompute_replacement_scores(agg: pd.DataFrame) -> pd.DataFrame:
    """Compute distance_to_lautaro, replacement_score, flags and rank."""
    minutes_col = "Minutes played"
    metrics = [m for m in METRICS_PER90 if m in agg.columns]

    df = agg.copy()
    df["Is_Target"] = df["Player"].eq("L. Martínez")

    vals = df[metrics].astype(float)
    lautaro_vec = (
        df.loc[df["Player"] == "L. Martínez", metrics].iloc[0].astype(float)
    )

    vals_norm = (vals - vals.mean()) / vals.std(ddof=0)
    lautaro_norm = (lautaro_vec - vals.mean()) / vals.std(ddof=0)

    dists = norm(vals_norm.values - lautaro_norm.values, axis=1)
    df["distance_to_lautaro"] = dists

    minutes_vals = df[minutes_col].astype(float)
    minutes_norm = (minutes_vals.max() - minutes_vals) / (
        minutes_vals.max() - minutes_vals.min() + 1e-9
    )

    dist_norm = (df["distance_to_lautaro"] - df["distance_to_lautaro"].min()) / (
        df["distance_to_lautaro"].max() - df["distance_to_lautaro"].max() + 1e-9
    )

    df["replacement_score"] = 0.7 * dist_norm + 0.3 * minutes_norm

    df["Is_Replacement_candidate"] = ~df["Is_Target"]

    df["Replacement Rank"] = pd.NA
    candidates = df["Is_Replacement_candidate"] & df["replacement_score"].notna()
    df.loc[candidates, "Replacement Rank"] = (
        df.loc[candidates, "replacement_score"]
        .rank(method="first", ascending=True)
        .astype("Int64")
    )

    for col in ("Is_Target", "Is_Replacement_candidate"):
        df[col] = df[col].astype(str).str.upper()

    return df


def _compute_lautaro_percentile_profile(agg: pd.DataFrame) -> pd.DataFrame:
    """Compute percentile profile (per 90) for Lautaro."""
    metrics_map = {
        "Goals / 90": "Goals per 90",
        "xG / 90": "xG per 90",
        "xA / 90": "xA per 90",
        "Shots / 90": "Shots per 90",
        "Dribbles / 90": "Dribbles per 90",
        "Touches in box / 90": "Touches in box per 90",
        "Progressive passes / 90": "Progressive passes per 90",
    }

    lautaro = agg[agg["Player"] == "L. Martínez"].iloc[0]

    rows = []
    for label, col in metrics_map.items():
        if col not in agg.columns:
            continue
        series = agg[col].astype(float)
        val = float(lautaro[col])
        pct = percentileofscore(series, val, kind="rank")
        rows.append({"player": lautaro["Player"], "Metric": label, "Percentile": pct})

    return pd.DataFrame(rows)


def run_full_pipeline() -> None:
    """Run the end‑to‑end aggregation and export all clean tables."""
    cur, prev, all_seasons = load_raw_data()
    agg = build_player_aggregation(cur, prev, all_seasons)
    agg_with_scores = recompute_replacement_scores(agg)

    df_tableau_path = DATA_CLEAN_DIR / "df_lautaro_tableau.xlsx"
    agg_with_scores.to_excel(df_tableau_path, index=False)

    metrics = [m for m in METRICS_PER90 if m in agg.columns]
    players_num = agg.copy()
    vals = players_num[metrics].astype(float)
    lautaro_vec = (
        players_num.loc[players_num["Player"] == "L. Martínez", metrics]
        .iloc[0]
        .astype(float)
    )
    vals_norm = (vals - vals.mean()) / vals.std(ddof=0)
    lautaro_norm = (lautaro_vec - vals.mean()) / vals.std(ddof=0)
    dists = norm(vals_norm.values - lautaro_norm.values, axis=1)
    players_num["distance_to_lautaro"] = dists

    minutes_vals = players_num["Minutes played"].astype(float)
    minutes_norm = (minutes_vals.max() - minutes_vals) / (
        minutes_vals.max() - minutes_vals.min() + 1e-9
    )
    dist_norm = (players_num["distance_to_lautaro"] - players_num["distance_to_lautaro"].min()) / (
        players_num["distance_to_lautaro"].max()
        - players_num["distance_to_lautaro"].min()
        + 1e-9
    )
    players_num["replacement_score"] = 0.7 * dist_norm + 0.3 * minutes_norm

    candidates = players_num[players_num["Player"] != "L. Martínez"]
    cols_top10 = [
        "Player",
        "Team",
        "Minutes played",
        "distance_to_lautaro",
        "replacement_score",
    ]
    df_top10 = (
        candidates.sort_values("replacement_score", ascending=True)[cols_top10]
        .head(10)
        .reset_index(drop=True)
    )
    df_top10.insert(0, "Rank", df_top10.index + 1)
    df_top10.to_excel(DATA_CLEAN_DIR / "df_top10_lautaro.xlsx", index=False)

    profile = _compute_lautaro_percentile_profile(agg)
    profile.to_excel(DATA_CLEAN_DIR / "lautaro_percentile_profile.xlsx", index=False)

