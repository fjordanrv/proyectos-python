from .matches import clean_matchs, extract_matchs, run_extract_and_clean_fixtures
from .pedri_lamine_scenarios import run_pedri_lamine_scenarios
from .scouting import (
    explore_cluster,
    run_lamine_replacements_and_tableau,
    run_pedri_replacements,
)

__all__ = [
    "extract_matchs",
    "clean_matchs",
    "run_extract_and_clean_fixtures",
    "run_pedri_lamine_scenarios",
    "explore_cluster",
    "run_pedri_replacements",
    "run_lamine_replacements_and_tableau",
    "run_full_pipeline",
]


def run_full_pipeline(
    *,
    scouting: bool = True,
    scenarios_season: str | None = "2025-2026",
) -> None:
    """
    Por defecto: scouting (CSV/Excel en data/clean) + escenarios (CSV en data/clean; gráficos en output/).
    La extracción web (partidos/alineaciones) no se ejecuta aquí; usa main.py con flags.
    """
    if scouting:
        run_pedri_replacements()
        run_lamine_replacements_and_tableau()
    if scenarios_season:
        run_pedri_lamine_scenarios(scenarios_season)
