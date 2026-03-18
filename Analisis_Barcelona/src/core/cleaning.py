from pathlib import Path
from typing import List

import pandas as pd
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN_DIR = PROJECT_ROOT / "data" / "clean"


def clean_comparison_stats(path: str) -> pd.DataFrame:
    """Limpia un CSV de comparación de jugadores descargado de FBRef."""
    df = pd.read_csv(path, header=1)
    df = df.copy()

    if re.search(r"passing", path):
        df = df[["Player", "90s", "Att", "Cmp%"]]
        for col in df.columns:
            if col != "90s" and col == "Att":
                df[col] = round(pd.to_numeric(df[col]) / pd.to_numeric(df["90s"]), 2)

    elif re.search(r"standard", path):
        df = df[["Player", "90s", "PrgC", "PrgP", "PrgR"]]
        for col in df.columns:
            if col not in ("90s", "Player"):
                df[col] = round(pd.to_numeric(df[col]) / pd.to_numeric(df["90s"]), 2)

    elif re.search("defense", path):
        df = df[["Player", "90s", "Tkl", "TklW", "Int", "Blocks", "Clr"]]
        for col in df.columns:
            if col not in ("90s", "Player"):
                df[col] = round(df[col] / df["90s"], 2)

    df = df.drop(columns=["90s"])
    return df


def load_and_clean_comparisons(filepaths: List[str]) -> pd.DataFrame:
    """Carga varios CSV de comparación, los limpia y concatena en un único DataFrame."""
    frames = []
    for path in filepaths:
        frames.append(clean_comparison_stats(path))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)

