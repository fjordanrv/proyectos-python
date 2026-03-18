from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mplsoccer import Radar, FontManager, grid

from .defender_radars import (
    DEFENDER_RADAR_LABELS,
    DEFENDER_RADAR_METRICS,
    DEFENSAS_LABEL,
    build_comparison_df,
    build_inyigo_vs_defensas_barca_df,
    INIGO_NAME,
)
from .paths import OUTPUT_DIR

# Paleta y fondo — réplica de notebooks/Barca_mi_analisis.ipynb (cells 23, 27)
BARCA_BLAU = "#004D98"
BARCA_GRANA = "#A50044"
BARCA_GRAY = "#E5E5E5"
BARCA_FIG_BG = "#121212"       # Fondo figura y ejes (estilo notebook)
RADAR_RING_FACE = "#28252c"    # Círculos internos radar
RADAR_RING_EDGE = "#39353f"
RADAR_VERTEX_EDGE = "#6d6c6d"  # Borde de los puntos del polígono

# Fuentes Roboto — mismo setup que el notebook (cells 21)
_URL_ROBOTO_THIN = "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf"
_URL_ROBOTO_BOLD = "https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf"
robotto_thin = FontManager(_URL_ROBOTO_THIN)
robotto_bold = FontManager(_URL_ROBOTO_BOLD)


def bar_compare(
    df: pd.DataFrame,
    column: str,
    ylabel: str,
    title: str,
    save_path: Optional[Path] = None,
) -> None:
    """Barra simple comparando una métrica entre temporadas — estilo notebook (fondo #121212, Roboto)."""
    x = np.array([0, 0.3])
    colores = [BARCA_BLAU, BARCA_GRANA]
    plt.figure(figsize=(5, 5))
    plt.gcf().patch.set_facecolor(BARCA_FIG_BG)
    ax = plt.gca()
    ax.set_facecolor(BARCA_FIG_BG)

    plt.bar(x, df[column].values, color=colores, width=0.2)
    ax.set_xlim(-0.2, 0.5)
    for i, v in enumerate(df[column].values):
        plt.text(x[i], v + v * 0.002, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold", color=BARCA_GRAY)
    plt.ylabel(ylabel, color=BARCA_GRAY)
    plt.xticks(x, df["season"].tolist(), color=BARCA_GRAY)
    plt.tick_params(axis="both", colors=BARCA_GRAY)
    plt.suptitle(title, fontsize=10, fontweight="bold", color=BARCA_GRAY, y=0.95)
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(save_path), facecolor=BARCA_FIG_BG, edgecolor="none")
        plt.close()
    else:
        plt.show()


def barca_radar_mplsoccer(
    df: pd.DataFrame,
    metrics: list[str],
    labels: list[str],
    title: str,
    save_path: Optional[Path] = None,
) -> None:
    """Radar comparando dos temporadas — réplica de Barca_mi_analisis (grid, círculos #28252c, Roboto)."""
    df_sorted = df.sort_values("season").reset_index(drop=True)
    seasons = df_sorted["season"].tolist()
    vals_0 = df_sorted.loc[0, metrics].astype(float).values
    vals_1 = df_sorted.loc[1, metrics].astype(float).values

    max_vals = np.maximum(vals_0, vals_1) * 1.1
    low = [0] * len(metrics)
    high = max_vals.tolist()

    radar = Radar(
        labels,
        low,
        high,
        num_rings=4,
        ring_width=1,
        center_circle_radius=1,
    )
    fig, axs = grid(
        figheight=7,
        grid_height=0.915,
        title_height=0.06,
        endnote_height=0.025,
        title_space=0,
        endnote_space=0,
        grid_key="radar",
        axis=False,
    )
    radar.setup_axis(ax=axs["radar"], facecolor="None")
    radar.draw_circles(
        ax=axs["radar"],
        facecolor=RADAR_RING_FACE,
        edgecolor=RADAR_RING_EDGE,
        lw=1.5,
    )
    radar_output = radar.draw_radar_compare(
        vals_0,
        vals_1,
        ax=axs["radar"],
        kwargs_radar={"facecolor": BARCA_BLAU, "alpha": 0.6},
        kwargs_compare={"facecolor": BARCA_GRANA, "alpha": 0.6},
    )
    radar_poly, radar_poly2, vertices1, vertices2 = radar_output
    radar.draw_range_labels(
        ax=axs["radar"],
        fontsize=10,
        color=BARCA_GRAY,
        fontproperties=robotto_thin.prop,
    )
    radar.draw_param_labels(
        ax=axs["radar"],
        fontsize=15,
        color=BARCA_GRAY,
        fontproperties=robotto_thin.prop,
    )
    axs["radar"].scatter(
        vertices1[:, 0], vertices1[:, 1],
        c=BARCA_BLAU, edgecolors=RADAR_VERTEX_EDGE, marker="o", s=150, zorder=2,
    )
    axs["radar"].scatter(
        vertices2[:, 0], vertices2[:, 1],
        c=BARCA_GRANA, edgecolors=RADAR_VERTEX_EDGE, marker="o", s=150, zorder=2,
    )
    axs["title"].text(
        0.01, 0.65, seasons[0],
        fontsize=19, color=BARCA_BLAU,
        fontproperties=robotto_bold.prop, ha="left", va="center",
    )
    axs["title"].text(
        0.99, 0.65, seasons[1],
        fontsize=19, color=BARCA_GRANA,
        fontproperties=robotto_bold.prop, ha="right", va="center",
    )
    fig.set_facecolor(BARCA_FIG_BG)
    plt.tight_layout()
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(save_path), facecolor=BARCA_FIG_BG, edgecolor="none")
        plt.close()
    else:
        plt.show()


def double_bar_compare(
    df: pd.DataFrame,
    col_left: str,
    col_right: str,
    label_left: str,
    label_right: str,
    ylabel: str,
    title: str,
    save_path: Optional[Path] = None,
) -> None:
    """Barras dobles por temporada — estilo notebook (fondo #121212, BARCA_GRAY)."""
    plt.figure(figsize=(7, 5))
    plt.gcf().patch.set_facecolor(BARCA_FIG_BG)
    ax = plt.gca()
    ax.set_facecolor(BARCA_FIG_BG)

    bar_width = 0.35
    seasons = df["season"].tolist()
    x = np.arange(len(seasons))
    bars_left = plt.bar(
        x - bar_width / 2,
        df[col_left],
        width=bar_width,
        label=label_left,
        color=BARCA_BLAU,
    )
    bars_right = plt.bar(
        x + bar_width / 2,
        df[col_right],
        width=bar_width,
        label=label_right,
        color=BARCA_GRANA,
    )
    max_height = max(df[col_left].max(), df[col_right].max())
    plt.ylim(0, max_height + 0.4)
    plt.xticks(x, seasons, color=BARCA_GRAY)
    plt.ylabel(ylabel, color=BARCA_GRAY)
    plt.title(title, color=BARCA_GRAY)
    plt.tick_params(axis="both", colors=BARCA_GRAY)
    leg = plt.legend(loc="upper left", bbox_to_anchor=(1.02, 0.5), labelcolor=BARCA_GRAY)
    if hasattr(leg, "get_frame"):
        leg.get_frame().set_facecolor(BARCA_FIG_BG)
    for bar in bars_left:
        h = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.02 * h,
            f"{h:.2f}",
            ha="center", va="bottom", fontsize=11, color=BARCA_GRAY,
        )
    for bar in bars_right:
        h = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.02 * h,
            f"{h:.2f}",
            ha="center", va="bottom", fontsize=11, color=BARCA_GRAY,
        )
    plt.tight_layout()
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(save_path), facecolor=BARCA_FIG_BG, edgecolor="none")
        plt.close()
    else:
        plt.show()


def radar_inyigo_vs(
    df: pd.DataFrame,
    player1_name: str,
    save_path: Optional[Path] = None,
    subtitle_left: str = "2024-2025",
    subtitle_right: str = "2024-2025",
) -> None:
    """
    Radar Iñigo Martínez vs otro defensa — réplica de radar_jugadores (notebook cell 64).
    df debe tener 2 filas (Iñigo primero) y columnas DEFENDER_RADAR_METRICS.
    subtitle_left/subtitle_right: texto bajo los nombres (ej. temporada).
    """
    metrics = [c for c in DEFENDER_RADAR_METRICS if c in df.columns]
    labels = [DEFENDER_RADAR_LABELS[DEFENDER_RADAR_METRICS.index(c)] for c in metrics]
    if len(metrics) != len(DEFENDER_RADAR_METRICS) or len(df) < 2:
        return
    val_0 = df.loc[0, metrics].astype(float).values
    val_1 = df.loc[1, metrics].astype(float).values
    max_vals = np.maximum(val_0, val_1) * 1.1
    low = [0] * len(metrics)
    high = max_vals.tolist()

    radar = Radar(
        labels,
        low,
        high,
        num_rings=4,
        ring_width=1,
        center_circle_radius=1,
    )
    fig, axs = grid(
        figheight=7,
        grid_height=0.915,
        title_height=0.06,
        endnote_height=0.025,
        title_space=0,
        endnote_space=0,
        grid_key="radar",
        axis=False,
    )
    radar.setup_axis(ax=axs["radar"], facecolor="None")
    radar.draw_circles(
        ax=axs["radar"],
        facecolor=RADAR_RING_FACE,
        edgecolor=RADAR_RING_EDGE,
        lw=1.5,
    )
    radar_output = radar.draw_radar_compare(
        val_0,
        val_1,
        ax=axs["radar"],
        kwargs_radar={"facecolor": BARCA_GRANA, "alpha": 0.6},
        kwargs_compare={"facecolor": BARCA_BLAU, "alpha": 0.6},
    )
    radar_poly, radar_poly2, vertices1, vertices2 = radar_output
    radar.draw_range_labels(
        ax=axs["radar"],
        fontsize=10,
        color=BARCA_GRAY,
        fontproperties=robotto_thin.prop,
    )
    radar.draw_param_labels(
        ax=axs["radar"],
        fontsize=12,
        color=BARCA_GRAY,
        fontproperties=robotto_thin.prop,
    )
    axs["radar"].scatter(
        vertices1[:, 0], vertices1[:, 1],
        c=BARCA_GRANA, edgecolors=RADAR_VERTEX_EDGE, marker="o", s=150, zorder=2,
    )
    axs["radar"].scatter(
        vertices2[:, 0], vertices2[:, 1],
        c=BARCA_BLAU, edgecolors=RADAR_VERTEX_EDGE, marker="o", s=150, zorder=2,
    )
    axs["title"].text(
        0.01, 0.65, INIGO_NAME,
        fontsize=20, fontproperties=robotto_bold.prop,
        ha="left", va="center", color=BARCA_GRANA,
    )
    axs["title"].text(
        0.01, 0.00, subtitle_left,
        fontsize=15, fontproperties=robotto_thin.prop,
        ha="left", va="center", color="#FFFFFF",
    )
    axs["title"].text(
        0.99, 0.65, player1_name,
        fontsize=20, fontproperties=robotto_bold.prop,
        ha="right", va="center", color=BARCA_BLAU,
    )
    axs["title"].text(
        0.99, 0.00, subtitle_right,
        fontsize=15, fontproperties=robotto_thin.prop,
        ha="right", va="center", color="#FFFFFF",
    )
    fig.set_facecolor(BARCA_FIG_BG)
    plt.tight_layout()
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(save_path), facecolor=BARCA_FIG_BG, edgecolor="none")
        plt.close()
    else:
        plt.show()


# Métricas y etiquetas para radar por temporada (alineadas con squad_seasons)
RADAR_METRIC_COLS = [f"{m}_per90" for m in ["Gls", "Ast", "G+A", "xG", "xAG", "xG+xAG"]]
RADAR_LABELS = [
    "Goles/90",
    "Asistencias/90",
    "G+A/90",
    "xG/90",
    "xAG/90",
    "xG+xAG/90",
]


def run_all_plots(df_squad_seasons: pd.DataFrame) -> int:
    """
    Genera todos los gráficos posibles a partir del DataFrame de temporadas del Barça.
    df_squad_seasons debe tener columna 'season' y columnas numéricas (_per90, GA_per90, etc.).
    Devuelve el número de gráficos guardados en output/.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    df = df_squad_seasons.sort_values("season").reset_index(drop=True)
    if len(df) < 2:
        return 0

    # Radar comparando dos temporadas
    metrics = [c for c in RADAR_METRIC_COLS if c in df.columns]
    labels = [RADAR_LABELS[RADAR_METRIC_COLS.index(c)] for c in metrics]
    if len(metrics) >= 2 and len(labels) == len(metrics):
        try:
            barca_radar_mplsoccer(
                df.head(2),
                metrics,
                labels,
                "FC Barcelona — comparativa por temporada",
                save_path=OUTPUT_DIR / "radar.png",
            )
            saved += 1
            barca_radar_mplsoccer(
                df.head(2),
                metrics,
                labels,
                "FC Barcelona — comparativa por temporada",
                save_path=OUTPUT_DIR / "radar.pdf",
            )
        except Exception:
            pass

    # Barras dobles: Goles a favor vs en contra por 90
    if "Gls_per90" in df.columns and "GA_per90" in df.columns:
        try:
            double_bar_compare(
                df.head(2),
                "Gls_per90",
                "GA_per90",
                "Goles/90",
                "Goles en contra/90",
                "Por 90 min",
                "FC Barcelona — Goles a favor y en contra",
                save_path=OUTPUT_DIR / "bar_compare_double.png",
            )
            saved += 1
        except Exception:
            pass

    # Barra simple (una métrica por temporada)
    first_numeric = next(
        (c for c in df.columns if c != "season" and df[c].dtype in ("float64", "int64")),
        None,
    )
    if first_numeric:
        try:
            bar_compare(
                df.head(2),
                first_numeric,
                first_numeric.replace("_", " "),
                "FC Barcelona — " + first_numeric.replace("_per90", ""),
                save_path=OUTPUT_DIR / "bar_compare.png",
            )
            saved += 1
        except Exception:
            pass

    # Radares Iñigo Martínez vs Gonçalo Inácio y vs Nico Schlotterbeck (notebook Barca_mi_analisis)
    for suffix, player1_name in [("Gonçalo", "Gonçalo Inácio"), ("Nico", "Nico Schlotterbeck")]:
        try:
            comp_df = build_comparison_df(suffix)
            if comp_df is not None and len(comp_df) >= 2:
                safe_name = player1_name.replace(" ", "_").replace("ç", "c").replace("á", "a")
                radar_inyigo_vs(
                    comp_df,
                    player1_name,
                    save_path=OUTPUT_DIR / f"radar_inyigo_vs_{safe_name}.png",
                )
                saved += 1
        except Exception:
            pass

    # Radar Iñigo Martínez vs Defensas Barça 2025-2026 (promedio defensas del equipo)
    try:
        inyigo_vs_def = build_inyigo_vs_defensas_barca_df()
        if inyigo_vs_def is not None and len(inyigo_vs_def) >= 2:
            radar_inyigo_vs(
                inyigo_vs_def,
                DEFENSAS_LABEL,
                save_path=OUTPUT_DIR / "radar_inyigo_vs_defensas_barca.png",
                subtitle_left="2024-2025",
                subtitle_right="2025-2026",
            )
            saved += 1
    except Exception:
        pass

    return saved

