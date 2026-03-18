"""Datos para radares Iñigo Martínez vs Gonçalo Inácio, Nico Schlotterbeck y vs Defensas Barça 2025-2026."""

from pathlib import Path

import pandas as pd

from .cleaning import clean_comparison_stats
from .paths import DATA_RAW_DIR

COMPARISON_DIR = DATA_RAW_DIR / "comparison" / "Archivos_utilizados"
SEASON_2526_DIR = DATA_RAW_DIR / "2025-2026" / "Archivos_utilizados"
INIGO_NAME = "Iñigo Martínez"
DEFENSAS_LABEL = "Defensas 2025-2026"

# Métricas y etiquetas del radar de defensores (notebook cell 64)
DEFENDER_RADAR_METRICS = [
    "Tkl", "TklW", "Int", "Blocks", "Clr",
    "PrgC", "PrgP", "PrgR", "Att", "Cmp%",
]
DEFENDER_RADAR_LABELS = [
    "Tackles", "Tackles Ganados", "Intercepciones", "Bloqueos", "Despejes",
    "Conducciones progresivas", "Pases Progresivos", "Pases Progresivos rec",
    "Pases Intentados", "Pases Completados",
]


def build_comparison_df(suffix: str) -> pd.DataFrame | None:
    """
    Carga defense, standard y passing de comparación para un jugador (suffix 'Gonçalo' o 'Nico'),
    los limpia, fusiona por Player y devuelve un DataFrame de 2 filas: Iñigo Martínez primero,
    luego el otro jugador. Columnas: Player + DEFENDER_RADAR_METRICS.
    """
    base = COMPARISON_DIR / f"defense_stats_{suffix}.csv"
    if not base.exists():
        return None
    try:
        defense = clean_comparison_stats(str(COMPARISON_DIR / f"defense_stats_{suffix}.csv"))
        standard = clean_comparison_stats(str(COMPARISON_DIR / f"standard_stats_{suffix}.csv"))
        passing = clean_comparison_stats(str(COMPARISON_DIR / f"passing_stats_{suffix}.csv"))
    except Exception:
        return None
    merged = defense.merge(standard, on="Player", how="left").merge(passing, on="Player", how="left")
    needed = ["Player"] + [c for c in DEFENDER_RADAR_METRICS if c in merged.columns]
    if len(needed) != len(DEFENDER_RADAR_METRICS) + 1:
        return None
    merged = merged[needed]
    # Asegurar orden: Iñigo primero, el otro segundo
    if INIGO_NAME not in merged["Player"].values:
        return None
    other = merged[merged["Player"] != INIGO_NAME]
    if other.empty:
        return None
    inigo_row = merged[merged["Player"] == INIGO_NAME].iloc[0:1]
    return pd.concat([inigo_row, other.head(1)], ignore_index=True)


def _read_squad_csv(path: Path, header: int = 1) -> pd.DataFrame:
    """Lee CSV de jugadores del equipo (cabecera en fila 1)."""
    return pd.read_csv(path, header=header)


def build_inyigo_vs_defensas_barca_df() -> pd.DataFrame | None:
    """
    Construye un DataFrame de 2 filas: Iñigo Martínez (2024-2025) vs promedio Defensas Barça (2025-2026).
    Usa datos de comparison para Iñigo y de 2025-2026/Archivos_utilizados para defensas.
    """
    inigo_comp = build_comparison_df("Nico")
    if inigo_comp is None or inigo_comp.empty:
        return None
    inigo_row = inigo_comp.iloc[0:1].copy()

    defense_path = SEASON_2526_DIR / "stats_defense_12_2025-2026.csv"
    standard_path = SEASON_2526_DIR / "stats_standard_12_2025-2026.csv"
    passing_path = SEASON_2526_DIR / "stats_passing_12_2025-2026.csv"
    if not defense_path.exists() or not standard_path.exists() or not passing_path.exists():
        return None
    try:
        defense = _read_squad_csv(defense_path)
        standard = _read_squad_csv(standard_path)
        passing = _read_squad_csv(passing_path)
    except Exception:
        return None

    # Filtrar defensas (Pos contiene 'DF')
    for df in (defense, standard, passing):
        if "Pos" not in df.columns:
            return None
    defense = defense[defense["Pos"].astype(str).str.contains("DF", na=False)].copy()
    standard = standard[standard["Pos"].astype(str).str.contains("DF", na=False)].copy()
    passing = passing[passing["Pos"].astype(str).str.contains("DF", na=False)].copy()
    if defense.empty or standard.empty or passing.empty:
        return None

    # Per-90 y promedios
    if "90s" not in defense.columns:
        return None
    for col in ["Tkl", "TklW", "Int", "Blocks", "Clr"]:
        if col in defense.columns:
            defense[col] = pd.to_numeric(defense[col], errors="coerce") / pd.to_numeric(defense["90s"], errors="coerce")
    defense_avg = defense[["Tkl", "TklW", "Int", "Blocks", "Clr"]].mean()

    if "90s" not in standard.columns:
        return None
    for col in ["PrgC", "PrgP", "PrgR"]:
        if col in standard.columns:
            standard[col] = pd.to_numeric(standard[col], errors="coerce") / pd.to_numeric(standard["90s"], errors="coerce")
    standard_avg = standard[["PrgC", "PrgP", "PrgR"]].mean()

    if "90s" not in passing.columns:
        return None
    if "Att" in passing.columns:
        passing["Att"] = pd.to_numeric(passing["Att"], errors="coerce") / pd.to_numeric(passing["90s"], errors="coerce")
    if "Cmp%" in passing.columns:
        passing["Cmp%"] = pd.to_numeric(passing["Cmp%"], errors="coerce")
    passing_avg = passing[["Att", "Cmp%"]].mean()

    row_dict = {"Player": DEFENSAS_LABEL}
    for m in DEFENDER_RADAR_METRICS:
        if m in defense_avg.index:
            row_dict[m] = round(float(defense_avg[m]), 2)
        elif m in standard_avg.index:
            row_dict[m] = round(float(standard_avg[m]), 2)
        elif m in passing_avg.index:
            row_dict[m] = round(float(passing_avg[m]), 2)
    if len(row_dict) != len(DEFENDER_RADAR_METRICS) + 1:
        return None
    defensas_row = pd.DataFrame([row_dict])
    defensas_row = defensas_row[["Player"] + DEFENDER_RADAR_METRICS]
    inigo_row = inigo_row[["Player"] + DEFENDER_RADAR_METRICS]
    return pd.concat([inigo_row, defensas_row], ignore_index=True)
