# Exporting Reports / Dashboards

This project is designed to feed external reporting tools (e.g. Tableau workbooks) rather than generating PDFs directly.

- Tableau workbook example: `src/output/Lautaro_Martinez_Dashboard..twb`.
- Clean data tables for visualization live in `src/data/clean/`.

To update the dashboard:

1. Re-run `src/1.-argentinos_lautaro_aggregation.ipynb` in your Python environment.
2. Confirm the Excel outputs in `src/data/clean/` have been refreshed.
3. Open the Tableau workbook and refresh the data sources pointing to those Excel files.
