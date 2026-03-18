"""Análisis de minutos Pedri / Lamine y escenarios (xG, posesión)."""

import glob
from pathlib import Path
from typing import Dict, List

import pandas as pd

from .paths import DATA_CLEAN_DIR, LINEUPS_RAW, OUTPUT_DIR

SCENARIO_ORDER = [
    "pedri_on",
    "pedri_off",
    "lamine_on",
    "lamine_off",
    "both_on",
]
LABEL_MAP = {
    "pedri_on": "Pedri ON",
    "pedri_off": "Pedri OFF",
    "lamine_on": "Lamine ON",
    "lamine_off": "Lamine OFF",
    "both_on": "Ambos ON",
}


def get_player_minutes(folder_path: Path, players_target: List[str]) -> pd.DataFrame:
    csv_files = glob.glob(str(folder_path / "*.csv"))
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.lower()
        required = {"match_id", "player", "min"}
        if not required.issubset(df.columns):
            continue
        match_id = df["match_id"].iloc[0]
        df_filtered = df.loc[
            df["player"].isin(players_target), ["match_id", "player", "min"]
        ]
        base_df = pd.DataFrame(
            {"match_id": match_id, "player": players_target, "min": 0}
        )
        df_final = base_df.merge(
            df_filtered, on=["match_id", "player"], how="left", suffixes=("", "_real")
        )
        df_final["min"] = df_final["min_real"].fillna(df_final["min"])
        df_final = df_final[["match_id", "player", "min"]]
        dfs.append(df_final)

    if not dfs:
        return pd.DataFrame(columns=["match_id", "player", "min"])

    out = pd.concat(dfs, ignore_index=True)
    out["min"] = pd.to_numeric(out["min"], errors="coerce")
    return out


def unpivot_player_minutes(df: pd.DataFrame) -> pd.DataFrame:
    df = (
        df.pivot_table(
            index="match_id", columns="player", values="min", aggfunc="sum", fill_value=0
        )
        .reset_index()
    )
    df.columns = (
        df.columns.astype(str).str.strip().str.replace("\xa0", "", regex=False)
    )
    df = df.rename(columns={"Pedri": "pedri_min", "Lamine Yamal": "lamine_min"})
    df.columns.name = None
    return df


def merge_fixtures_with_minutes(
    fixtures_path: Path, minutes_wide: pd.DataFrame
) -> pd.DataFrame:
    df = pd.read_csv(fixtures_path)
    df.columns = df.columns.str.lower()
    minutes_wide = minutes_wide.copy()
    minutes_wide.columns = minutes_wide.columns.str.lower()
    df = df[df["match_id"].notna() & (df["match_id"] != "")]
    df["match_id"] = df["match_id"].astype(str)
    minutes_wide["match_id"] = minutes_wide["match_id"].astype(str)
    df_final = df.merge(minutes_wide, on="match_id", how="left")[
        ["match_id", "xg_for", "posesion", "lamine_min", "pedri_min"]
    ]
    df_final[["lamine_min", "pedri_min", "xg_for"]] = df_final[
        ["lamine_min", "pedri_min", "xg_for"]
    ].fillna(0)
    return df_final


def add_scenario_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["lamine_played"] = (df["lamine_min"] > 0).astype(int)
    df["pedri_played"] = (df["pedri_min"] > 0).astype(int)
    df["lamine_60"] = (df["lamine_min"] >= 60).astype(int)
    df["pedri_60"] = (df["pedri_min"] >= 60).astype(int)
    df = df[df["xg_for"] != 0]
    return df


def build_scenario_df(
    df: pd.DataFrame,
    scenarios: Dict[str, pd.Series],
    metrics: Dict[str, str] | None = None,
) -> pd.DataFrame:
    if metrics is None:
        metrics = {"xg_for_media": "xg_for", "posesion_for_media": "posesion"}
    rows = []
    for name, mask in scenarios.items():
        sub = df.loc[mask]
        row = {"scenario": name, "partidos": len(sub)}
        for out_col, src_col in metrics.items():
            row[out_col] = sub[src_col].mean() if len(sub) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def prepare_scenario_plot_df(
    df: pd.DataFrame,
    order: List[str],
    label_map: Dict[str, str],
    scenario_col: str = "scenario",
) -> pd.DataFrame:
    df_plot = df.set_index(scenario_col).loc[order].reset_index()
    df_plot["label"] = df_plot[scenario_col].map(label_map)
    return df_plot


def run_pedri_lamine_scenarios(
    season: str,
    players_target: List[str] | None = None,
) -> pd.DataFrame:
    """
    Agrega minutos desde lineups/<season>/, cruza con fixtures clean y devuelve scenario_df.
    Guarda CSV de escenarios en data/clean/ (solo datos; los gráficos van a output/).
    """
    if players_target is None:
        players_target = ["Pedri", "Lamine Yamal"]

    folder = LINEUPS_RAW / season
    fixtures_path = DATA_CLEAN_DIR / f"score_fixtures_clean_{season}.csv"
    if not folder.is_dir():
        raise FileNotFoundError(f"No existe carpeta de alineaciones: {folder}")
    if not fixtures_path.exists():
        raise FileNotFoundError(f"Falta {fixtures_path}")

    long_min = get_player_minutes(folder, players_target)
    wide = unpivot_player_minutes(long_min)
    merged = merge_fixtures_with_minutes(fixtures_path, wide)
    merged = add_scenario_flags(merged)

    scenarios = {
        "pedri_on": merged["pedri_60"] == 1,
        "pedri_off": merged["pedri_60"] == 0,
        "lamine_on": merged["lamine_60"] == 1,
        "lamine_off": merged["lamine_60"] == 0,
        "both_on": (merged["pedri_60"] == 1) & (merged["lamine_60"] == 1),
    }
    scenario_df = build_scenario_df(merged, scenarios)
    DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    scenario_df.to_csv(
        DATA_CLEAN_DIR / f"pedri_lamine_scenarios_{season}.csv", index=False
    )
    plot_df = prepare_scenario_plot_df(
        scenario_df, order=SCENARIO_ORDER, label_map=LABEL_MAP
    )
    plot_df.to_csv(
        DATA_CLEAN_DIR / f"pedri_lamine_scenarios_plot_{season}.csv", index=False
    )
    return scenario_df
