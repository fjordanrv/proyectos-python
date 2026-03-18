"""Rutas del proyecto (equivalente a `src` como raíz de datos)."""

from pathlib import Path

# Directorio `src/`
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN_DIR = PROJECT_ROOT / "data" / "clean"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"

SCORE_FIXTURES_RAW = DATA_RAW_DIR / "score_fixtures"
LINEUPS_RAW = DATA_RAW_DIR / "lineups"
