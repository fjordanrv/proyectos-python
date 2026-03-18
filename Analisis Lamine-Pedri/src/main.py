"""
Punto de entrada del análisis Lamine / Pedri.

Ejemplos (desde la carpeta del proyecto `Analisis Lamine-Pedri`):

  # Pipeline por defecto: scouting + escenarios (usa datos ya descargados)
  python -m src.main

  # Descargar partidos de una temporada (requiere acceso a FBref)
  python -m src.main --extract-fixtures --season 2025-2026

  # Descargar alineaciones de todos los partidos de esa temporada (muy lento)
  python -m src.main --scrape-lineups --season 2025-2026

  # Solo scouting (reemplazos Pedri/Lamine → data/clean)
  python -m src.main --scouting-only

  # Solo escenarios xG/posesión → src/output/
  python -m src.main --scenarios-only --season 2025-2026

  # Solo generar gráficos (clustering, escenarios, radares y mapa de calor)
  python -m src.main --plots-only --season 2025-2026

  # Obtener datos de heatmap de Lamine y Pedri desde Sofascore (Chrome/Selenium, una vez)
  python -m src.main --fetch-heatmap
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permite `python -m src.main` desde la raíz del proyecto (core vive bajo src/)
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core import run_full_pipeline
from core.lineups import scrape_lineups_for_season
from core.matches import run_extract_and_clean_fixtures
from core.pedri_lamine_scenarios import run_pedri_lamine_scenarios
from core.scouting import run_lamine_replacements_and_tableau, run_pedri_replacements
from core.radar_heatmap import fetch_all_heatmaps
from core.visualization import run_all_plots


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline Lamine-Pedri")
    parser.add_argument(
        "--extract-fixtures",
        action="store_true",
        help="Descargar y limpiar fixtures desde FBref",
    )
    parser.add_argument(
        "--scrape-lineups",
        action="store_true",
        help="Descargar CSV de alineación por partido (lento)",
    )
    parser.add_argument(
        "--season",
        default="2025-2026",
        help="Temporada formato 2025-2026",
    )
    parser.add_argument(
        "--scouting-only",
        action="store_true",
        help="Solo run_pedri_replacements + run_lamine_replacements_and_tableau",
    )
    parser.add_argument(
        "--scenarios-only",
        action="store_true",
        help="Solo escenarios Pedri/Lamine → output/",
    )
    parser.add_argument(
        "--no-scenarios",
        action="store_true",
        help="No calcular escenarios en el pipeline por defecto",
    )
    parser.add_argument(
        "--no-scouting",
        action="store_true",
        help="No ejecutar scouting en el pipeline por defecto",
    )
    parser.add_argument(
        "--plots-only",
        action="store_true",
        help="Solo ejecutar las funciones que crean gráficos (cluster, escenarios, radares, heatmap)",
    )
    parser.add_argument(
        "--fetch-heatmap",
        action="store_true",
        help="Obtener heatmaps de Lamine y Pedri desde Sofascore (Selenium) y guardar CSVs en data/clean",
    )
    args = parser.parse_args()

    if args.fetch_heatmap:
        fetch_all_heatmaps()
        return

    if args.plots_only:
        run_all_plots(season=args.season)
        return

    if args.extract_fixtures:
        run_extract_and_clean_fixtures(args.season)
        return

    if args.scrape_lineups:
        scrape_lineups_for_season(args.season)
        return

    if args.scouting_only:
        run_pedri_replacements()
        run_lamine_replacements_and_tableau()
        return

    if args.scenarios_only:
        run_pedri_lamine_scenarios(args.season)
        return

    run_full_pipeline(
        scouting=not args.no_scouting,
        scenarios_season=None if args.no_scenarios else args.season,
    )


if __name__ == "__main__":
    main()
