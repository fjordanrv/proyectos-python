"""Generación de gráficos (clustering, escenarios, radares y mapa de calor)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .paths import DATA_CLEAN_DIR, OUTPUT_DIR
from .radar_heatmap import run_heatmap_plot, run_radar_plots
from .scouting import CLUSTER_COLS, explore_cluster


def run_cluster_plots(
    min_minutes: int = 300,
) -> None:
    """
    Genera y guarda en src/output/ los gráficos de clustering:
    - cluster_MF_2d.png (mediocampistas)
    - cluster_FW_2d.png (delanteros)
    """
    path = DATA_CLEAN_DIR / "players_2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Falta {path}; ejecuta antes el scouting o asegura tener el CSV.")

    df = pd.read_csv(path)
    df = df[df["Playing Time_Min"] >= min_minutes]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    explore_cluster(
        df, 4, CLUSTER_COLS, pos="MF", show_plots=True, plot_output_basename="cluster_MF"
    )
    explore_cluster(
        df, 4, CLUSTER_COLS, pos="FW", show_plots=True, plot_output_basename="cluster_FW"
    )


def run_scenario_plots(season: str) -> bool:
    """
    Lee el CSV de escenarios en output/ y genera gráficos de barras (xG y posesión).
    Guarda en src/output/: impacto_xg_escenarios.png, impacto_posesion_escenarios.png
    Devuelve True si se generaron, False si no existía el CSV.
    """
    csv_path = DATA_CLEAN_DIR / f"pedri_lamine_scenarios_plot_{season}.csv"
    if not csv_path.exists():
        return False

    df = pd.read_csv(csv_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Paleta igual que en los .ipynb (escenarios)
    colors = ["#2E86AB", "#9FC9E3", "#F2C94C", "#F7D774", "#1B3B6F"]
    if "xg_for_media" in df.columns:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df["label"], df["xg_for_media"], color=colors[: len(df)])
        ax.set_ylabel("xG for (media)")
        ax.set_title(f"xG for por escenario — {season}")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(str(OUTPUT_DIR / "impacto_xg_escenarios.png"))
        plt.close()

    if "posesion_for_media" in df.columns:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df["label"], df["posesion_for_media"], color=colors[: len(df)])
        ax.set_ylabel("Posesión (media %)")
        ax.set_title(f"Posesión por escenario — {season}")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(str(OUTPUT_DIR / "impacto_posesion_escenarios.png"))
        plt.close()
    return True


def run_all_plots(
    season: str = "2025-2026",
    cluster_plots: bool = True,
    scenario_plots: bool = True,
    radar_plots: bool = True,
    heatmap_plot: bool = True,
) -> None:
    """
    Ejecuta solo las funciones que crean gráficos.
    - cluster_plots: clustering MF/FW en output/
    - scenario_plots: xG y posesión por escenario (requiere CSV en data/clean)
    - radar_plots: radares Lamine y Pedri vs cluster (radar_lamine.png, radar_lamine_vs_fw.png, radar_pedri_vs_mf.png)
    - heatmap_plot: mapa de calor si existe data/clean/lamine_heatmap_points.csv
    """
    if cluster_plots:
        run_cluster_plots()
    if scenario_plots:
        if not run_scenario_plots(season):
            print(
                f"Aviso: no existe CSV de escenarios para {season}. "
                f"Ejecuta antes: python -m src.main --scenarios-only --season {season}"
            )
    if radar_plots:
        if not run_radar_plots():
            print("Aviso: no se pudieron generar radares (revisa players_2025.csv y filtro MF/FW).")
    if heatmap_plot:
        if not run_heatmap_plot():
            print(
                "Aviso: no se generaron mapas de calor. "
                "Para Lamine y Pedri ejecuta una vez: python -m src.main --fetch-heatmap"
            )
