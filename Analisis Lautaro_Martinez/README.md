# Analisis de reemplazo: Lautaro Martínez

## Descripción

Proyecto de análisis de datos para identificar posibles **reemplazos de Lautaro Martínez** a partir de datos de jugadores argentinos en las grandes ligas europeas. Se combinan las dos últimas temporadas por jugador, se calculan métricas por 90 minutos, totales sin normalizar y un índice de similitud / `replacement_score`.

## Estructura del proyecto

- `docs/`
  - `PROJECT_CONTEXT.md`: contexto funcional y explicación de las salidas.
  - `INFORMES_PDF_SETUP.md`: cómo conectar los datos limpios con Tableau u otras herramientas de reporting.
- `requirements.txt`: dependencias de Python necesarias para ejecutar el análisis.
- `src/`
  - `main.py`: punto de entrada futuro (actualmente sólo muestra un mensaje).
  - `1.-argentinos_lautaro_aggregation.ipynb`: notebook principal con toda la lógica de agregado y cálculo.
  - `assets/`: recursos estáticos (por ejemplo, imágenes de Lautaro).
  - `data/raw/`: ficheros Excel originales (`currentseason_argentinos.xlsx`, `previousseason_argentinos.xlsx`).
  - `data/clean/`: tablas procesadas listas para Tableau (`df_lautaro_tableau.xlsx`, `df_top10_lautaro.xlsx`, `lautaro_percentile_profile.xlsx`, etc.).
  - `output/`: artefactos de salida, como el workbook de Tableau.

## Instalación

Se recomienda usar un entorno virtual (por ejemplo, `ml-env` que ya tienes creado):

```bash
pip install -r requirements.txt
```

## Ejecución del análisis

1. Abre el entorno de trabajo en tu IDE (por ejemplo, VS Code / Cursor).
2. Activa tu entorno virtual (`ml-env`).
3. Ejecuta el notebook principal:
   - `src/1.-argentinos_lautaro_aggregation.ipynb`
4. Verifica que en `src/data/clean/` se han actualizado:
   - `df_lautaro_tableau.xlsx`
   - `df_top10_lautaro.xlsx`
   - `lautaro_percentile_profile.xlsx`

Esas tablas están preparadas para ser consumidas por Tableau u otra herramienta de visualización.

## Dependencias clave

- Python 3.12
- pandas, numpy, scipy, scikit-learn
- matplotlib, seaborn, plotly
- mplsoccer
- selenium, webdriver-manager, cloudscraper, beautifulsoup4
- openpyxl

## Próximos pasos posibles

- Extraer la lógica del notebook a módulos de Python dentro de `src/`.
- Añadir tests unitarios para las funciones de agregado y cálculo de percentiles.
- Automatizar la regeneración de las tablas limpias con un script o un `makefile`.
