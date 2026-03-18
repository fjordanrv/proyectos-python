# ⚽ Análisis de Lamine Yamal | Dashboard en Tableau

Proyecto de analítica deportiva centrado en el análisis del perfil estadístico de **Lamine Yamal**, comparándolo con jugadores de las 5 grandes ligas europeas durante la temporada **2025–26**.

El resultado final es un **cuadro de mando interactivo en Tableau**, diseñado para explorar el rendimiento del jugador desde diferentes perspectivas.

---

## 📊 Objetivo del proyecto

El objetivo principal es construir una solución completa de análisis de datos que permita:

- Evaluar el rendimiento de Lamine Yamal en contexto competitivo
- Comparar su perfil con jugadores de élite en Europa
- Visualizar métricas clave de forma interactiva
- Facilitar la interpretación de datos para scouting y análisis deportivo

---

## 🧱 Metodología

El proyecto sigue un flujo típico de análisis de datos:

1. **📥 Recopilación de datos**  
   Obtención de datos desde plataformas Open Data (ej. FBref u otras fuentes públicas)

2. **🧹 Preparación de datos**  
   Limpieza, transformación y estructuración del dataset

3. **📊 Análisis exploratorio**  
   Cálculo de métricas relevantes y generación de variables comparativas

4. **📈 Visualización**  
   Diseño de un dashboard interactivo en Tableau

---

## 📊 Dashboard

El resultado final del proyecto es un dashboard en Tableau que permite:

- Comparar percentiles del jugador
- Analizar métricas ofensivas y de creación
- Evaluar impacto en el juego
- Explorar datos de forma interactiva

🔗 **Ver dashboard en Tableau Public**  
*(añadir enlace cuando lo publiques)*

---

## 📂 Estructura del proyecto

```
Analisis Lamine-Pedri/
├── docs/
│   ├── INFORMES_PDF_SETUP.md
│   └── PROJECT_CONTEXT.md
├── README.md
├── requirements.txt
└── src/
    ├── main.py              # CLI: pipeline por defecto y flags
    ├── assets/              # Figuras estáticas
    ├── core/
    │   ├── paths.py
    │   ├── matches.py       # Extracción/limpieza partidos (FBref)
    │   ├── lineups.py       # Extracción alineaciones
    │   ├── pedri_lamine_scenarios.py
    │   └── scouting.py      # Clustering y reemplazos
    ├── data/
    │   ├── raw/
    │   └── clean/
    └── output/              # CSV escenarios Pedri/Lamine
```

### Ejecución

Desde la carpeta del proyecto (con el venv activado y `pip install -r requirements.txt`):

```bash
python -m src.main                    # scouting + escenarios (temporada por defecto 2025-2026)
python -m src.main --scouting-only   # solo replacements + Excel Tableau
python -m src.main --extract-fixtures --season 2025-2026
python -m src.main --scrape-lineups --season 2025-2026   # lento
```

---

## 🛠️ Tecnologías utilizadas

- **Python** (Pandas, scikit-learn, cloudscraper, Selenium según uso)
- **Tableau** (visualización)
- **Open Data (FBref u otros)**

---

## 🎯 Resultados

- Dataset estructurado listo para análisis
- Comparación estadística del jugador frente a ligas top
- Dashboard interactivo para exploración de rendimiento

---

## 🚀 Posibles mejoras

- Incorporar más temporadas
- Añadir métricas avanzadas (xG, xA, progresión)
- Automatizar la extracción de datos
- Integrar el dashboard en una app (Streamlit)

---

## 👤 Autor

Franco Jordan  
Data Analyst | Sports Analytics  

🔗 [LinkedIn](https://www.linkedin.com/in/fjordanrv)
