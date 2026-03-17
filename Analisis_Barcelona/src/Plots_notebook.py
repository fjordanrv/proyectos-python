import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from mplsoccer import Radar, FontManager, grid
import seaborn as sns

# ============================
# PALETA OFICIAL FC BARCELONA
# ============================
BARCA_BLAU = "#004D98"
BARCA_GRANA = "#A50044"
BARCA_GOLD = "#EDBB00"
BARCA_DARK = "#0D1B2A"
BARCA_GRAY = "#E5E5E5"

from matplotlib import rcParams

def set_barca_style():
    """
    Aplica un tema global estilo FC Barcelona a matplotlib.
    Debe llamarse una vez al inicio del notebook.
    """

    # Partimos del estilo por defecto para no acumular basuras
    plt.style.use("default")

    # Fondo de figura y ejes
    rcParams["figure.facecolor"] = "white"
    rcParams["axes.facecolor"] = "white"

    # Bordes y ejes
    rcParams["axes.edgecolor"] = BARCA_DARK
    rcParams["axes.labelcolor"] = BARCA_DARK
    rcParams["axes.titleweight"] = "bold"
    rcParams["axes.titlesize"] = 14
    rcParams["axes.labelsize"] = 12

    # Líneas y colores por defecto (ciclo de colores)
    rcParams["axes.prop_cycle"] = plt.cycler(
        color=[BARCA_BLAU, BARCA_GRANA, BARCA_GOLD, BARCA_DARK]
    )

    # Ticks
    rcParams["xtick.color"] = BARCA_DARK
    rcParams["ytick.color"] = BARCA_DARK
    rcParams["xtick.labelsize"] = 11
    rcParams["ytick.labelsize"] = 11

    # Grid
    rcParams["axes.grid"] = True
    rcParams["grid.linestyle"] = "--"
    rcParams["grid.alpha"] = 0.3
    rcParams["grid.color"] = BARCA_GRAY

    # Leyenda
    rcParams["legend.frameon"] = False
    rcParams["legend.fontsize"] = 11

    # Fuente general
    rcParams["font.size"] = 11

    # Líneas
    rcParams["lines.linewidth"] = 2

    # Márgenes
    rcParams["figure.autolayout"] = True


def bar_compare(df, column, ylabel, title):
    plt.figure(figsize=(7,5))
    colors = [BARCA_BLAU, BARCA_GRANA]  # azul vs rojo

    plt.bar(df["season"], df[column], color=colors, width=0.5)

    # Etiquetas sobre la barra
    for i, v in enumerate(df[column]):
        plt.text(i, v + v*0.02, f"{v:.2f}", ha="center", fontsize=12)

    plt.title(title, fontsize=14)
    plt.ylabel(ylabel)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.show()

def barca_radar_mplsoccer(df, metrics, labels, title):
    """
    Radar tipo StatsBomb con mplsoccer para comparar dos temporadas del Barça.
    Usa Radar.draw_radar_compare.
    """

    # 1) Ordenar por temporada (por si acaso)
    df_sorted = df.sort_values("season").reset_index(drop=True)
    seasons = df_sorted["season"].tolist()

    # 2) Extraer valores
    vals_0 = df_sorted.loc[0, metrics].astype(float).values
    vals_1 = df_sorted.loc[1, metrics].astype(float).values

    # 3) Rangos por métrica
    max_vals = np.maximum(vals_0, vals_1) * 1.1
    low = [0] * len(metrics)
    high = max_vals.tolist()

    # 4) Crear radar
    radar = Radar(
        params=labels,
        min_range=low,
        max_range=high,
        num_rings=5,
        ring_width=1,
        center_circle_radius=0,
    )

    # 5) Set up eje
    fig, ax = radar.setup_axis(figsize=(7, 7))
    ax.set_facecolor("#f5f5f5")

    # Anillos de fondo
    radar.draw_circles(ax=ax, facecolor="#e6e6e6", edgecolor="white")

    # 6) Dibujar comparación de las dos temporadas
    radar_output = radar.draw_radar_compare(
        vals_0,
        vals_1,
        ax=ax,
        kwargs_radar={"facecolor": BARCA_BLAU, "alpha": 0.55},
        kwargs_compare={"facecolor": BARCA_GRANA, "alpha": 0.55},
    )
    radar_poly_0, radar_poly_1, verts_0, verts_1 = radar_output

    # 7) Labels
    radar.draw_range_labels(ax=ax, fontsize=10, color="#777777")
    radar.draw_param_labels(ax=ax, fontsize=12, color="#333333")

    # 8) Título + leyenda
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    ax.legend(
        [seasons[0], seasons[1]],
        loc="upper left",
        bbox_to_anchor=(1.05, 1.05),
        frameon=False,
        fontsize=12,
    )

    plt.tight_layout()
    plt.show()

def double_bar_compare(df, col_left, col_right, label_left, label_right, ylabel, title):
    plt.figure(figsize=(7,5))

    bar_width = 0.35
    seasons = df["season"]
    x = np.arange(len(seasons))

    bars_left = plt.bar(
        x - bar_width/2,
        df[col_left],
        width=bar_width,
        label=label_left,
        color=BARCA_BLAU
    )

    bars_right = plt.bar(
        x + bar_width/2,
        df[col_right],
        width=bar_width,
        label=label_right,
        color=BARCA_GRANA
    )

    # Ajustar dinámicamente el límite del eje Y
    max_height = max(df["Gls_per90"].max(), df["GA_per90"].max())
    plt.ylim(0, max_height + 0.4)


    plt.xticks(x, seasons)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 0.5))
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    offset = 0.08
    for bar in bars_left:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 0.02*h, f"{h:.2f}",
                 ha="center", va="bottom", fontsize=11)

    for bar in bars_right:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 0.02*h, f"{h:.2f}",
                 ha="center", va="bottom", fontsize=11)

    plt.tight_layout()
    plt.show()

