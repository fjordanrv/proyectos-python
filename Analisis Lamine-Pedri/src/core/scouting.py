"""Clustering y reemplazos tipo Pedri / Lamine (jugadores Big 5)."""

from typing import Any, Optional, Tuple

import matplotlib

matplotlib.use("Agg")  # evitar necesidad de display en servidor/CI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from .paths import DATA_CLEAN_DIR, OUTPUT_DIR

CLUSTER_COLS = [
    "Per 90 Minutes_xAG",
    "Per 90 Minutes_xG",
    "Per 90 Minutes_xG+xAG",
    "Progression_PrgP",
    "Progression_PrgC",
    "Progression_PrgR",
]


def explore_cluster(
    df: pd.DataFrame,
    n_cluster: int,
    cols: list,
    pos: Optional[str] = None,
    scale: bool = True,
    show_plots: bool = False,
    plot_output_basename: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    if pos is not None:
        df = df[df["Pos"].astype(str).str.contains(pos, na=False)]
    df = df.reset_index(drop=True)
    X = df[cols]
    if scale:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X.values

    cluster = KMeans(n_clusters=n_cluster, random_state=1, n_init=10)
    labels = cluster.fit_predict(X_scaled)
    df["cluster"] = labels.astype(str)
    df_group = df.groupby("cluster")[cols].mean()

    if show_plots:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        base = plot_output_basename or "cluster_explore"
        sns.set_theme()
        if len(cols) == 1:
            plt.figure(figsize=(12, 8))
            sns.boxplot(data=df, x="cluster", y=cols[0])
            plt.savefig(str(OUTPUT_DIR / f"{base}_1d.png"))
            plt.close()
        elif len(cols) >= 2:
            plt.figure(figsize=(12, 8))
            sns.scatterplot(data=df, x=cols[0], y=cols[1], hue="cluster")
            plt.savefig(str(OUTPUT_DIR / f"{base}_2d.png"))
            plt.close()

    return df_group, df


def run_pedri_replacements(
    min_minutes: int = 300,
    pedri_cluster_id: str = "2",
) -> pd.DataFrame:
    """Replica notebook: MF, cluster de Pedri, export replacements_tableau.csv."""
    path = DATA_CLEAN_DIR / "players_2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Falta {path}")

    df = pd.read_csv(path)
    df = df[df["Playing Time_Min"] >= min_minutes]
    _, df_final = explore_cluster(df, 4, CLUSTER_COLS, "MF", show_plots=False)
    df_cluster = df_final[df_final["cluster"] == pedri_cluster_id].reset_index(drop=True)
    if df_cluster.empty:
        raise ValueError(
            f"No hay jugadores en cluster MF '{pedri_cluster_id}'. "
            "Ajusta pedri_cluster_id tras revisar clusters."
        )

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster[CLUSTER_COLS])
    idx_pedri = df_cluster[df_cluster["Player"] == "Pedri"].index[0]
    pedri_vector = X_scaled[idx_pedri].reshape(1, -1)
    distances = euclidean_distances(X_scaled, pedri_vector).flatten()
    df_cluster = df_cluster.copy()
    df_cluster["distance_to_pedri"] = distances

    df_replacements = df_cluster[df_cluster["Player"] != "Pedri"].copy()
    scaler_m = MinMaxScaler()
    df_replacements["distance_norm"] = scaler_m.fit_transform(
        df_replacements[["distance_to_pedri"]]
    )
    df_replacements["minutes_penalty"] = np.log1p(df_replacements["Playing Time_Min"])
    df_replacements["minutes_penalty_norm"] = MinMaxScaler().fit_transform(
        df_replacements[["minutes_penalty"]]
    )
    df_replacements["replacement_score"] = (
        0.6 * df_replacements["distance_norm"]
        + 0.4 * df_replacements["minutes_penalty_norm"]
    )
    df_replacements = df_replacements.sort_values("replacement_score")

    out = DATA_CLEAN_DIR / "replacements_tableau.csv"
    df_replacements.to_csv(
        out, index=False, sep=";", encoding="utf-8-sig"
    )
    return df_replacements


def run_lamine_replacements_and_tableau(
    min_minutes: int = 300,
    lamine_cluster_id: str = "3",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """FW cluster Lamine: replacements, df_lamine_tableau.xlsx, df_top10.xlsx."""
    path = DATA_CLEAN_DIR / "players_2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Falta {path}")

    df = pd.read_csv(path)
    df = df[df["Playing Time_Min"] >= min_minutes]
    _, df_final_fw = explore_cluster(df, 4, CLUSTER_COLS, "FW", show_plots=False)
    df_cluster = df_final_fw[df_final_fw["cluster"] == lamine_cluster_id].reset_index(
        drop=True
    )
    if df_cluster.empty:
        raise ValueError(
            f"No hay jugadores en cluster FW '{lamine_cluster_id}'. "
            "Ajusta lamine_cluster_id."
        )

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster[CLUSTER_COLS])
    lamine_rows = df_cluster[df_cluster["Player"] == "Lamine Yamal"]
    if lamine_rows.empty:
        raise ValueError("No está 'Lamine Yamal' en el cluster seleccionado.")
    idx_lamine = lamine_rows.index[0]
    lamine_vector = X_scaled[idx_lamine].reshape(1, -1)
    distances = euclidean_distances(X_scaled, lamine_vector).flatten()
    df_cluster = df_cluster.copy()
    df_cluster["distance_to_lamine"] = distances

    df_replacements = df_cluster[df_cluster["Player"] != "Lamine Yamal"].copy()
    scaler_m = MinMaxScaler()
    df_replacements["distance_norm"] = scaler_m.fit_transform(
        df_replacements[["distance_to_lamine"]]
    )
    df_replacements["minutes_penalty"] = np.log1p(df_replacements["Playing Time_Min"])
    df_replacements["minutes_penalty_norm"] = MinMaxScaler().fit_transform(
        df_replacements[["minutes_penalty"]]
    )
    df_replacements["replacement_score"] = (
        0.99 * df_replacements["distance_norm"]
        + 0.01 * df_replacements["minutes_penalty_norm"]
    )
    df_replacements = df_replacements.sort_values("replacement_score")

    df_final = df_cluster.copy()
    df_final["is_target"] = df_final["Player"].eq("Lamine Yamal")
    df_final = df_final.merge(
        df_replacements[["Player", "replacement_score"]], on="Player", how="left"
    )
    df_final["is_replacement_candidate"] = df_final["replacement_score"].notna()
    df_final = df_final.sort_values("replacement_score", na_position="last")
    df_final["replacement_rank"] = range(1, len(df_final) + 1)
    df_final.loc[df_final["is_target"], "replacement_rank"] = np.nan

    DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df_final.to_excel(DATA_CLEAN_DIR / "df_lamine_tableau.xlsx", index=False)

    df_top10 = (
        df_replacements[
            [
                "Player",
                "Squad",
                "Playing Time_Min",
                "distance_to_lamine",
                "replacement_score",
            ]
        ]
        .head(10)
        .reset_index(drop=True)
    )
    df_top10["Rank"] = df_top10.index + 1
    df_top10 = df_top10[
        [
            "Rank",
            "Player",
            "Squad",
            "Playing Time_Min",
            "distance_to_lamine",
            "replacement_score",
        ]
    ]
    df_top10.to_excel(DATA_CLEAN_DIR / "df_top10.xlsx", index=False)

    return df_replacements, df_final
