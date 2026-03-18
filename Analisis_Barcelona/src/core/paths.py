"""Rutas del proyecto. Solo gráficos en output/; tablas en data/raw y data/clean."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN_DIR = PROJECT_ROOT / "data" / "clean"
OUTPUT_DIR = PROJECT_ROOT / "output"  # Solo gráficos (PNG/PDF), no tablas
