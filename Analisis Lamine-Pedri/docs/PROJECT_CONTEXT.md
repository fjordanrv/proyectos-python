# Contexto del proyecto — Lamine / Pedri

## Estructura (alineada con Analisis_Barcelona / Lautaro)

- `docs/` — documentación
- `requirements.txt` — dependencias
- `src/main.py` — punto de entrada CLI
- `src/core/` — lógica:
  - `paths.py` — rutas bajo `src/data`, `src/output` (solo gráficos), `src/assets`
  - `matches.py` — extracción y limpieza de partidos (FBref + cloudscraper)
  - `lineups.py` — extracción de alineaciones por URL
  - `pedri_lamine_scenarios.py` — minutos, xG, posesión por escenario
  - `scouting.py` — KMeans, reemplazos Pedri (MF) y Lamine (FW)
  - **`radar_heatmap.py`** — radares (mplsoccer `Radar` + `grid`) y mapas de calor (mplsoccer `Pitch` statsbomb), réplica exacta de los notebooks `3.-extraccion_jugadores.ipynb` y `4.-scouting_clustering.ipynb`
  - `visualization.py` — `run_all_plots`: barras de escenarios, clusters 2D, y llamadas a radares/heatmap

## Flujo típico

1. **Datos ya presentes**: `src/data/clean/players_2025.csv`, fixtures, lineups, etc.
2. **`python -m src.main`**: regenera tablas en `src/data/clean/` (replacements, Excel Tableau, CSV de escenarios) y gráficos en `src/output/` (solo PNG).
3. **Actualizar partidos**: `python -m src.main --extract-fixtures --season 2025-2026`
4. **Actualizar alineaciones** (muchas peticiones): `python -m src.main --scrape-lineups --season 2025-2026`
5. **Solo gráficos**: `python -m src.main --plots-only`

## Radares y mapas de calor (`radar_heatmap.py`)

- **Referencia**: Código replicado de los notebooks `src/3.-extraccion_jugadores.ipynb` (heatmap + radares) y `src/4.-scouting_clustering.ipynb`.
- **Radares** (mplsoccer `Radar`, `grid`, `FontManager` Roboto/RobotoSlab):
  - Paleta Blaugrana: `BARCA_BLAU` (#004D98), `BARCA_GRANA` (#A50044), `BARCA_GRAY`, `BARCA_GOLD` (#edbb00). Fondo figura `#121212`; círculos internos `#28252c` / `#39353f`.
  - **Salidas en `src/output/`**: `radar_lamine.png` (Lamine percentil vs FW), `radar_lamine_vs_fw.png` (Lamine vs 1 delantero del cluster), `radar_pedri.png` (Pedri percentil vs MF), `radar_pedri_vs_mf.png` (Pedri vs Maxime Lopez, Azzedine Ounahi, Edu Expósito).
- **Heatmaps** (mplsoccer `Pitch` tipo `statsbomb`):
  - Campo `#22312b`, líneas `#efefef`. Colormap Sofascore (verde → amarillo → naranja → rojo). `pitch.bin_statistic(..., bins=(90, 60))`, `gaussian_filter(sigma=2.8)`, normalización percentiles 5–97.
  - **Salidas**: `heatmap_lamine.png`, `heatmap_pedri.png` si existen `data/clean/lamine_heatmap_points.csv` y `pedri_heatmap_points.csv`.
- **Datos de heatmap**: Una vez con `python -m src.main --fetch-heatmap` (Selenium + CDP Sofascore) se generan los CSV de puntos; luego `--plots-only` genera los PNG.

## Notas

- Los IDs de cluster para Pedri (`2`) y Lamine (`3`) coinciden con el notebook original; si cambian los datos, puede ser necesario ajustarlos en `scouting.py`.
