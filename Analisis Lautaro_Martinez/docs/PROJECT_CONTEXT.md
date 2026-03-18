# Project Context: Lautaro Martínez Replacement Analysis

This project analyzes attacking players from the top European leagues to find suitable replacements for **Lautaro Martínez**.

## Data

- Source: pre-aggregated scouting data for Argentinian players (`currentseason_argentinos.xlsx`, `previousseason_argentinos.xlsx`).
- Location: `src/data/raw/`.
- Cleaned / analysis-ready outputs are written to `src/data/clean/`.

## Key Outputs

- `df_lautaro_tableau.xlsx`: aggregated profile for Lautaro and all Argentinian forwards (per 90 + raw totals, similarity scores, ranking flags).
- `df_top10_lautaro.xlsx`: top 10 closest replacement candidates based on playing style and minutes.
- `lautaro_percentile_profile.xlsx`: percentile radar profile for Lautaro vs the Argentinian player pool.

## Notebooks

The main analysis logic lives in `src/1.-argentinos_lautaro_aggregation.ipynb`, which:

1. Loads and merges the last two seasons for Argentinian players.
2. Computes minutes-weighted per-90 metrics.
3. Derives raw totals (goals, shots, xG, xA, etc.).
4. Aggregates similarity and replacement scores.
5. Exports clean tables tailored for Tableau dashboards.
