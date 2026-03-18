"""
Entry point para el proyecto de análisis del FC Barcelona.

  # Pipeline de extracción (FBRef → data/raw)
  python -m src.main

  # Solo generar gráficos a output/ (si hay datos en data/clean con columnas tipo 'season')
  python -m src.main --plots-only
"""

import argparse
import sys
from pathlib import Path

# Permite `python -m src.main` desde la raíz del proyecto (core vive bajo src/)
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core.paths import OUTPUT_DIR


def run_full_pipeline() -> None:
    from core.extraction import (
        scrape_and_save_comparison,
        scrape_and_save_players,
        scrape_and_save_teams,
    )
    season = "2024-2025"
    scrape_and_save_teams(season, headless=False)
    scrape_and_save_players(season, headless=False)

    comparison_url = ""
    player_name = "target_player"
    if comparison_url:
        scrape_and_save_comparison(comparison_url, player_name, headless=False)


def run_plots_to_output() -> None:
    """Construye data/clean/squad_seasons.csv desde raw y guarda en output/ radar, barras, etc."""
    import pandas as pd

    from core import visualization
    from core.squad_seasons import SQUAD_SEASONS_CSV, build_squad_seasons_csv

    path = build_squad_seasons_csv()
    if path is None or not path.exists():
        print(
            "No se pudo generar data/clean/squad_seasons.csv.\n"
            "Asegúrate de tener en data/raw/ carpetas por temporada (ej. 2024-2025, 2025-2026)\n"
            "con Archivos_utilizados/stats_squads_standard_for_<season>.csv y _against_."
        )
        return
    df = pd.read_csv(path)
    saved = visualization.run_all_plots(df)
    if saved == 0:
        print("Datos en squad_seasons.csv insuficientes (se necesitan al menos 2 temporadas).")
    else:
        print(f"Gráficos guardados en {OUTPUT_DIR} ({saved} archivos).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots-only", action="store_true", help="Solo generar gráficos en output/")
    args = parser.parse_args()

    if args.plots_only:
        run_plots_to_output()
        return

    run_full_pipeline()


if __name__ == "__main__":
    main()
