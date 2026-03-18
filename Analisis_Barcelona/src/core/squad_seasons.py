"""Construye data/clean/squad_seasons.csv a partir de datos raw (FBRef squad stats por temporada)."""

from pathlib import Path

import pandas as pd

from .paths import DATA_CLEAN_DIR, DATA_RAW_DIR

SQUAD_SEASONS_CSV = DATA_CLEAN_DIR / "squad_seasons.csv"

# Métricas por temporada para radar y barras (nombres en CSV con cabecera doble "Per 90 Minutes" / nombre)
RADAR_METRICS = ["Gls", "Ast", "G+A", "xG", "xAG", "xG+xAG"]
RADAR_LABELS = [
    "Goles/90",
    "Asistencias/90",
    "G+A/90",
    "xG/90",
    "xAG/90",
    "xG+xAG/90",
]


def _read_squad_standard(path: Path, header: list[int] = [0, 1]) -> pd.DataFrame:
    """Lee CSV de estadísticas de equipos (cabecera doble) y devuelve columnas numéricas útiles."""
    df = pd.read_csv(path, header=header)
    if not isinstance(df.columns, pd.MultiIndex):
        return df
    new_cols = []
    for c in df.columns:
        if c[0] == "Per 90 Minutes":
            new_cols.append(f"{c[1]}_per90")
        elif c[1] == "Squad":
            new_cols.append("Squad")
        else:
            new_cols.append(f"{c[1]}" if c[1] else str(c[0]))
    df.columns = new_cols
    return df


def _extract_barcelona_row(df: pd.DataFrame, squad_value: str = "Barcelona") -> pd.Series | None:
    """Obtiene la fila del Barcelona (o 'vs Barcelona' en tablas against)."""
    if "Squad" not in df.columns:
        return None
    row = df.loc[df["Squad"].astype(str).str.strip() == squad_value]
    if row.empty:
        return None
    return row.iloc[0]


def build_squad_seasons_csv() -> Path | None:
    """
    Recorre data/raw/<season>/ y genera squad_seasons.csv en data/clean/ con una fila por temporada
    (Barcelona: goles a favor y en contra por 90, xG, etc.).
    """
    DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for season_dir in sorted(DATA_RAW_DIR.iterdir()):
        if not season_dir.is_dir():
            continue
        season = season_dir.name
        # Archivos_utilizados tiene prioridad; si no existe, buscar en Otros
        for sub in ("Archivos_utilizados", "Otros"):
            for_dir = season_dir / sub
            path_for = for_dir / f"stats_squads_standard_for_{season}.csv"
            path_against = for_dir / f"stats_squads_standard_against_{season}.csv"
            if not path_for.exists():
                continue

            try:
                df_for = _read_squad_standard(path_for)
                ser = _extract_barcelona_row(df_for, "Barcelona")
                if ser is None:
                    continue
                out = {"season": season}
                for m in RADAR_METRICS:
                    col = f"{m}_per90"
                    if col in ser.index:
                        try:
                            out[col] = float(ser[col])
                        except (TypeError, ValueError):
                            pass
                # Goles en contra (GA): del archivo "against", fila "vs Barcelona" -> Gls son los que nos metieron
                if path_against.exists():
                    df_against = _read_squad_standard(path_against)
                    ser_against = _extract_barcelona_row(df_against, "vs Barcelona")
                    if ser_against is not None and "Gls_per90" in ser_against.index:
                        try:
                            out["GA_per90"] = float(ser_against["Gls_per90"])
                        except (TypeError, ValueError):
                            pass
                rows.append(out)
            except Exception:
                continue
            break

    if not rows:
        return None
    result = pd.DataFrame(rows)
    result.to_csv(SQUAD_SEASONS_CSV, index=False)
    return SQUAD_SEASONS_CSV
