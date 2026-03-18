"""Radares (percentiles) y mapa de calor de jugadores — réplica exacta de los notebooks 3 y 4."""

from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from mplsoccer import Pitch, Radar, FontManager, grid
from scipy.ndimage import gaussian_filter
from scipy.stats import percentileofscore

from .paths import DATA_CLEAN_DIR, OUTPUT_DIR
from .scouting import CLUSTER_COLS, explore_cluster

# Paleta oficial FC Barcelona (notebook 3, cell 29)
BARCA_BLAU = "#004D98"
BARCA_GRANA = "#A50044"
BARCA_GRAY = "#E5E5E5"
BARCA_GOLD = "#edbb00"
# Para comparación: base + 3 comparados (Pedri + Maxime Lopez, Ounahi, Edu Expósito)
PEDRI_COMPARE_NAMES = ["Maxime Lopez", "Azzedine Ounahi", "Edu Expósito"]

# Fuentes Roboto como en el notebook (cell 28)
_URL_ROBOTO_THIN = "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf"
_URL_ROBOTO_BOLD = "https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf"
robotto_thin = FontManager(_URL_ROBOTO_THIN)
robotto_bold = FontManager(_URL_ROBOTO_BOLD)

# Colormap Sofascore para heatmap (notebook 3, cell 3)
SOFASCORE_CMAP = LinearSegmentedColormap.from_list(
    "sofascore",
    [
        "#22312b",  # fondo (verde campo)
        "#2e7d32",  # verde oscuro
        "#66bb6a",  # verde claro
        "#cddc39",  # amarillo verdoso
        "#ffeb3b",  # amarillo
        "#ffb300",  # naranja
        "#f57c00",  # naranja fuerte
        "#e53935",  # rojo
    ],
)

# Heatmaps: URL Sofascore y nombres de archivo por jugador
HEATMAP_PLAYERS = [
    ("Lamine Yamal", "https://www.sofascore.com/es-la/football/player/lamine-yamal/1402912#tab:season", "lamine_heatmap_points.csv", "heatmap_lamine.png"),
    ("Pedri", "https://www.sofascore.com/es-la/football/player/pedri/992587#tab:season", "pedri_heatmap_points.csv", "heatmap_pedri.png"),
]

RADAR_LABELS_FW = [
    "Ventajas creadas",
    "Finalización propia",
    "Impacto ofensivo total",
    "Progresión por pase",
    "Ruptura con balón",
    "Ataque a la profundidad",
]
RADAR_LABELS_MF = [
    "Creatividad estructural",
    "Llegada a zonas de remate",
    "Contribución ofensiva sostenida",
    "Progresión por pase",
    "Conducción funcional",
    "Ocupación de espacios avanzados",
]


def build_percentile_profile(
    df: pd.DataFrame, player_name: str, metrics: List[str]
) -> pd.DataFrame:
    """Una fila: jugador y percentiles (0–100) por métrica respecto al resto del df."""
    row = df[df["Player"] == player_name]
    if row.empty:
        raise ValueError(f"Jugador no encontrado: {player_name}")
    out = {"player": player_name}
    for m in metrics:
        if m not in df.columns:
            continue
        vals = pd.to_numeric(df[m], errors="coerce").dropna()
        if vals.empty:
            continue
        v = row[m].iloc[0]
        out[m] = percentileofscore(vals, float(v))
    return pd.DataFrame([out])


def _draw_radar_single(
    values: np.ndarray,
    labels: List[str],
    player: str,
    pos: str,
    team: str,
    output_path: Path,
) -> None:
    """Radar individual — réplica exacta de radar_jugador (notebook 3, cells 30–32)."""
    low = [0] * len(labels)
    high = [100] * len(labels)
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
        facecolor="#28252c",
        edgecolor="#39353f",
        lw=1.5,
    )
    radar.draw_radar(
        values,
        ax=axs["radar"],
        kwargs_radar={"facecolor": BARCA_GRANA, "alpha": 0.6},
        kwargs_rings={"facecolor": BARCA_BLAU, "alpha": 0.6},
    )
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
        fontproperties=robotto_bold.prop,
    )
    axs["title"].text(
        0.01, 0.65, player,
        fontsize=23,
        fontproperties=robotto_bold.prop,
        ha="left", va="center", color=BARCA_BLAU,
    )
    axs["title"].text(
        0.01, 0.001, team,
        fontsize=20,
        fontproperties=robotto_thin.prop,
        ha="left", va="center", color=BARCA_GRANA,
    )
    axs["title"].text(
        0.99, 0.65, "Radar Chart",
        fontsize=23,
        fontproperties=robotto_bold.prop,
        ha="right", va="center", color=BARCA_BLAU,
    )
    axs["title"].text(
        0.99, 0.001, pos,
        fontsize=20,
        fontproperties=robotto_thin.prop,
        ha="right", va="center", color=BARCA_GRANA,
    )
    fig.set_facecolor("#121212")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), facecolor="#121212", edgecolor="none")
    plt.close()


def _draw_radar_compare_two(
    df: pd.DataFrame,
    player_left: str,
    player_right: str,
    metrics: List[str],
    labels: List[str],
    output_path: Path,
) -> None:
    """Comparación de 2 jugadores — réplica de radar_jugadores (notebook 3, cell 33)."""
    rows = df[df["Player"].isin([player_left, player_right])]
    if len(rows) < 2:
        return
    val_0 = rows[rows["Player"] == player_left][metrics].iloc[0].astype(float).to_numpy()
    val_1 = rows[rows["Player"] == player_right][metrics].iloc[0].astype(float).to_numpy()

    low = [0] * len(metrics)
    high = [100] * len(metrics)
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
        facecolor="#28252c",
        edgecolor="#39353f",
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
        fontproperties=robotto_bold.prop,
    )
    axs["radar"].scatter(
        vertices1[:, 0], vertices1[:, 1],
        c=BARCA_GRANA, edgecolors="#6d6c6d", marker="o", s=150, zorder=2,
    )
    axs["radar"].scatter(
        vertices2[:, 0], vertices2[:, 1],
        c=BARCA_BLAU, edgecolors="#6d6c6d", marker="o", s=150, zorder=2,
    )
    axs["title"].text(
        0.01, 0.65, player_left,
        fontsize=20, fontproperties=robotto_bold.prop,
        ha="left", va="center", color=BARCA_GRANA,
    )
    axs["title"].text(
        0.01, 0.00, "2025-2026",
        fontsize=15, fontproperties=robotto_thin.prop,
        ha="left", va="center", color="#FFFFFF",
    )
    axs["title"].text(
        0.99, 0.65, player_right,
        fontsize=20, fontproperties=robotto_bold.prop,
        ha="right", va="center", color=BARCA_BLAU,
    )
    axs["title"].text(
        0.99, 0.00, "2025-2026",
        fontsize=15, fontproperties=robotto_thin.prop,
        ha="right", va="center", color="#FFFFFF",
    )
    fig.set_facecolor("#121212")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), facecolor="#121212", edgecolor="none")
    plt.close()


def _draw_radar_compare(
    df: pd.DataFrame,
    player_base: str,
    players_compare: List[str],
    metrics: List[str],
    labels: List[str],
    output_path: Path,
) -> None:
    """Pedri vs 3 mediocampistas — réplica exacta de radar__mas_jugadores (notebook 3, cell 36)."""
    base_row = df[df["Player"] == player_base]
    if base_row.empty:
        return
    base_vals = base_row[metrics].iloc[0].astype(float).to_numpy()
    compare_vals = []
    for p in players_compare:
        r = df[df["Player"] == p]
        if not r.empty:
            compare_vals.append(r[metrics].iloc[0].astype(float).to_numpy())
    if not compare_vals:
        return

    compare_colors = [BARCA_BLAU, BARCA_GOLD, BARCA_GRAY]

    low = [0] * len(metrics)
    high = [100] * len(metrics)
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
        grid_height=0.90,
        title_height=0.08,
        endnote_height=0.02,
        title_space=0,
        endnote_space=0,
        grid_key="radar",
        axis=False,
    )
    radar.setup_axis(ax=axs["radar"], facecolor="None")
    radar.draw_circles(
        ax=axs["radar"],
        facecolor=BARCA_GRAY,
        alpha=0.06,
        edgecolor=BARCA_GRAY,
        lw=1.4,
    )
    radar.draw_radar(
        base_vals,
        ax=axs["radar"],
        kwargs_radar={"facecolor": BARCA_GRANA, "alpha": 0.35},
        kwargs_rings={"facecolor": "none"},
    )
    for vals, color in zip(compare_vals, compare_colors):
        radar.draw_radar(
            vals,
            ax=axs["radar"],
            kwargs_radar={
                "fill": False,
                "edgecolor": color,
                "lw": 2.4,
                "alpha": 0.95,
            },
            kwargs_rings={"facecolor": "none"},
        )
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
    y = 0.62
    axs["title"].text(
        0.04, 0.61, player_base,
        fontsize=18, fontproperties=robotto_thin.prop,
        color=BARCA_GRANA, ha="left", va="center",
    )
    if len(players_compare) > 0:
        axs["title"].text(
            0.16, y, players_compare[0],
            fontsize=18, fontproperties=robotto_thin.prop,
            color=BARCA_BLAU, ha="left", va="center",
        )
    if len(players_compare) > 1:
        axs["title"].text(
            0.44, y, players_compare[1],
            fontsize=18, fontproperties=robotto_thin.prop,
            color=BARCA_GOLD, ha="left", va="center",
        )
    if len(players_compare) > 2:
        axs["title"].text(
            0.75, y, players_compare[2],
            fontsize=18, fontproperties=robotto_thin.prop,
            color=BARCA_GRAY, ha="left", va="center",
        )
    fig.set_facecolor("#121212")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), facecolor="#121212", edgecolor="none")
    plt.close()


def run_radar_plots(min_minutes: int = 300) -> bool:
    """
    Genera radares en output/:
    - radar_lamine.png (perfil percentil Lamine vs FW)
    - radar_lamine_vs_fw.png (Lamine vs otros FW del cluster)
    - radar_pedri_vs_mf.png (Pedri vs otros MF del cluster)
    """
    path = DATA_CLEAN_DIR / "players_2025.csv"
    if not path.exists():
        return False

    df = pd.read_csv(path)
    df = df[df["Playing Time_Min"] >= min_minutes]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = [c for c in CLUSTER_COLS if c in df.columns]
    if len(metrics) != 6:
        return False

    labels_fw = RADAR_LABELS_FW[: len(metrics)]
    labels_mf = RADAR_LABELS_MF[: len(metrics)]

    # Radar individual Lamine (notebook: radar_jugador)
    df_fw = df[df["Pos"].astype(str).str.contains("FW", na=False)]
    if not df_fw.empty and "Lamine Yamal" in df_fw["Player"].values:
        try:
            profile = build_percentile_profile(df_fw, "Lamine Yamal", metrics)
            vals = profile[metrics].iloc[0].astype(float).values
            _draw_radar_single(
                vals,
                labels_fw,
                player="Lamine Yamal",
                pos="Delantero",
                team="FC Barcelona",
                output_path=OUTPUT_DIR / "radar_lamine.png",
            )
        except Exception:
            pass

    # Lamine vs 1 delantero del cluster (notebook: radar_jugadores)
    try:
        _, df_final_fw = explore_cluster(df, 4, metrics, "FW", show_plots=False)
        df_cluster = df_final_fw[df_final_fw["cluster"] == "3"].reset_index(drop=True)
        others = df_cluster[df_cluster["Player"] != "Lamine Yamal"]["Player"].head(1).tolist()
        if others and "Lamine Yamal" in df_cluster["Player"].values:
            _draw_radar_compare_two(
                df_cluster,
                player_left="Lamine Yamal",
                player_right=others[0],
                metrics=metrics,
                labels=labels_fw,
                output_path=OUTPUT_DIR / "radar_lamine_vs_fw.png",
            )
    except Exception:
        pass

    # Radar individual Pedri (notebook: radar_jugador)
    df_mf = df[df["Pos"].astype(str).str.contains("MF", na=False)]
    if not df_mf.empty and "Pedri" in df_mf["Player"].values:
        try:
            profile = build_percentile_profile(df_mf, "Pedri", metrics)
            vals = profile[metrics].iloc[0].astype(float).values
            _draw_radar_single(
                vals,
                labels_mf,
                player="Pedri",
                pos="Mediocampista",
                team="FC Barcelona",
                output_path=OUTPUT_DIR / "radar_pedri.png",
            )
        except Exception:
            pass

    # Pedri vs 3 mediocampistas (notebook: radar__mas_jugadores)
    try:
        _, df_final_mf = explore_cluster(df, 4, metrics, "MF", show_plots=False)
        wanted = ["Pedri"] + PEDRI_COMPARE_NAMES
        df_compare = df_final_mf[df_final_mf["Player"].isin(wanted)].drop_duplicates(subset=["Player"])
        compare_list = [p for p in PEDRI_COMPARE_NAMES if p in df_compare["Player"].values]
        if not df_compare[df_compare["Player"] == "Pedri"].empty and compare_list:
            _draw_radar_compare(
                df_compare,
                "Pedri",
                compare_list,
                metrics,
                labels_mf,
                OUTPUT_DIR / "radar_pedri_vs_mf.png",
            )
    except Exception:
        pass

    return True


def draw_heatmap_from_points(
    points_df: pd.DataFrame,
    output_path: Path,
    title: str = "Mapa de calor",
) -> None:
    """
    Mapa de calor sobre campo StatsBomb — réplica exacta del notebook 3 (cell 4).
    points_df con columnas 'x' e 'y' (Sofascore: 0–100); se convierten a coordenadas StatsBomb 120x80.
    """
    df = points_df.copy()
    df.columns = df.columns.str.strip().str.lower()
    if "x" not in df.columns or "y" not in df.columns:
        raise ValueError("points_df debe tener columnas 'x' e 'y' (o 'X'/'Y')")

    x = df["x"].astype(float).values
    y = df["y"].astype(float).values
    # Sofascore devuelve 0–100; StatsBomb es 120 (largo) x 80 (ancho)
    if x.max() <= 1.5 and y.max() <= 1.5:
        x, y = x * 100, y * 100
    pitch_x = x * 120 / 100.0
    pitch_y = y * 80 / 100.0

    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#22312b",
        line_color="#efefef",
        line_zorder=2,
    )
    fig, ax = pitch.draw(figsize=(6.6, 4.125))
    fig.set_facecolor("#22312b")

    bin_statistic = pitch.bin_statistic(
        pitch_x,
        pitch_y,
        statistic="count",
        bins=(90, 60),
    )
    bin_statistic["statistic"] = gaussian_filter(
        bin_statistic["statistic"],
        sigma=2.8,
    )

    values = bin_statistic["statistic"]
    values = values[values > 0]
    norm = Normalize(
        vmin=np.percentile(values, 5),
        vmax=np.percentile(values, 97),
    )

    pitch.heatmap(
        bin_statistic,
        ax=ax,
        cmap=SOFASCORE_CMAP,
        norm=norm,
        alpha=0.97,
        edgecolors="none",
    )
    ax.invert_yaxis()
    ax.set_title(title, fontsize=14, fontweight="bold", color="#efefef")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), facecolor="#22312b", edgecolor="none")
    plt.close()


def run_heatmap_plot(
    try_fetch_if_missing: bool = False,
) -> bool:
    """
    Genera heatmap_lamine.png y heatmap_pedri.png en output/ cuando existan los CSV
    (lamine_heatmap_points.csv, pedri_heatmap_points.csv).
    Acepta columnas 'x'/'y' o 'X'/'Y'. Si try_fetch_if_missing=True, intenta obtener
    los datos desde Sofascore para los que falten (requiere Selenium y Chrome).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    any_ok = False
    for label, url, csv_name, png_name in HEATMAP_PLAYERS:
        csv_path = DATA_CLEAN_DIR / csv_name
        if not csv_path.exists():
            if try_fetch_if_missing:
                try:
                    fetch_heatmap_data_sofascore(url=url, save_path=csv_path)
                except Exception:
                    continue
            else:
                continue
        try:
            df = pd.read_csv(csv_path)
            draw_heatmap_from_points(
                df,
                OUTPUT_DIR / png_name,
                title=f"{label} — mapa de calor",
            )
            any_ok = True
        except Exception:
            continue
    return any_ok


def fetch_heatmap_data_sofascore(
    url: str,
    save_path: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Obtiene los puntos del mapa de calor desde la API de Sofascore (Selenium + CDP).
    save_path debe ser data/clean/lamine_heatmap_points.csv o pedri_heatmap_points.csv.
    Requiere Chrome y selenium/webdriver-manager.
    """
    import json
    import time

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_page_load_timeout(15)
    try:
        driver.get(url)
    except Exception:
        pass
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
    heatmap_data = None
    for x in logs:
        path = x.get("params", {}).get("headers", {}).get(":path", "")
        if "heatmap" in path and "player" in path:
            try:
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": x["params"]["requestId"]},
                )
                heatmap_data = json.loads(body["body"])
                break
            except Exception:
                continue
    driver.quit()
    if not heatmap_data or "points" not in heatmap_data:
        raise ValueError("No se pudo obtener el heatmap desde Sofascore (API o red).")
    points = heatmap_data["points"]
    df = pd.DataFrame([{"x": p["x"], "y": p["y"]} for p in points])
    if save_path is None:
        save_path = DATA_CLEAN_DIR / "lamine_heatmap_points.csv"
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)
    return df


def fetch_all_heatmaps() -> None:
    """
    Descarga los datos de heatmap de Lamine y Pedri desde Sofascore y guarda
    lamine_heatmap_points.csv y pedri_heatmap_points.csv en data/clean/.
    Requiere Chrome y Selenium. Ejecutar una vez; luego --plots-only generará ambos PNG.
    """
    for label, url, csv_name, _ in HEATMAP_PLAYERS:
        save_path = DATA_CLEAN_DIR / csv_name
        try:
            fetch_heatmap_data_sofascore(url=url, save_path=save_path)
            print(f"Heatmap de {label} guardado en {save_path}")
        except Exception as e:
            print(f"No se pudo obtener heatmap de {label}: {e}")
