# Contexto — Analisis Barcelona

- Datos crudos en `src/data/raw/` (por temporada: `2024-2025/`, `2025-2026/`, con `Archivos_utilizados/stats_squads_standard_for_*.csv` y `_against_*.csv`).
- **`src/data/clean/`**: generado por el proyecto; `squad_seasons.csv` se construye desde raw (una fila por temporada del Barça: goles/90, xG/90, GA/90, etc.).
- **`src/output/`**: solo gráficos (PNG/PDF). Se rellenan con:
  - **`python -m src.main --plots-only`**: construye `data/clean/squad_seasons.csv` desde raw y genera:
    - `radar.png` y `radar.pdf` — radar mplsoccer comparando dos temporadas (Gls/90, Ast/90, xG/90, xAG/90, xG+xAG/90).
    - `bar_compare_double.png` — barras dobles goles a favor vs goles en contra por 90.
    - `bar_compare.png` — barra simple de una métrica por temporada.
    - `radar_inyigo_vs_Goncalo_Inacio.png` — radar Iñigo Martínez vs Gonçalo Inácio (defensa).
    - `radar_inyigo_vs_Nico_Schlotterbeck.png` — radar Iñigo Martínez vs Nico Schlotterbeck (defensa).
    - `radar_inyigo_vs_defensas_barca.png` — radar Iñigo Martínez (2024-2025) vs promedio Defensas Barça (2025-2026).  
  Los radares vs Gonçalo/Nico usan `data/raw/comparison/Archivos_utilizados/`. El radar vs Defensas usa además `data/raw/2025-2026/Archivos_utilizados/` (stats_defense, stats_standard, stats_passing de jugadores).
- **Módulos**: `core.paths`, `core.squad_seasons` (build_squad_seasons_csv), `core.visualization` (bar_compare, barca_radar_mplsoccer, double_bar_compare, run_all_plots). La extracción desde FBRef está en `core.extraction` (se usa solo en el pipeline completo, no con `--plots-only`).

- **Estilo de gráficos** (réplica de `notebooks/Barca_mi_analisis.ipynb`): paleta BARCA_BLAU (#004D98), BARCA_GRANA (#A50044), BARCA_GRAY (#E5E5E5); fondo figura y ejes #121212; radar con mplsoccer `grid()`, círculos #28252c / #39353f, vértices con borde #6d6c6d; fuentes Roboto Thin y Roboto Slab vía FontManager (mismas URLs que en el notebook).
