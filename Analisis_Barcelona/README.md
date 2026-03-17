# ⚽ Impacto estructural de la salida de Iñigo Martínez | FC Barcelona

Análisis de cómo la salida de **Iñigo Martínez** afecta el modelo de juego del FC Barcelona, evaluando cambios estructurales en el rendimiento del equipo y explorando posibles reemplazos mediante un enfoque basado en datos.

---

## 📊 Contexto

La salida de Iñigo Martínez supone la pérdida de un perfil clave dentro del sistema del FC Barcelona:

- Central zurdo con capacidad de **organización en salida de balón**
- Alto impacto en la **progresión desde línea defensiva**
- Rol estructural en la estabilidad del modelo de juego

Aunque el equipo mantiene buenos resultados en la temporada **2025/26**, surge la necesidad de evaluar si el modelo ha cambiado internamente.

---

## ❓ Pregunta clave

> ¿Puede el Barça reemplazar a Iñigo Martínez sin alterar su modelo de juego?

---

## 🎯 Objetivos

- Analizar el impacto de la salida de Iñigo Martínez  
- Comparar el rendimiento estructural del equipo entre las temporadas **2024/25 vs 2025/26**  
- Identificar cambios en el modelo de juego  
- Evaluar posibles reemplazos en el mercado  
- Desarrollar un **algoritmo de similitud de perfiles** basado en:
  - rol táctico  
  - progresión de balón  
  - peso estructural en la salida  

---

## 🧠 Metodología

### 1. 📥 Datos

- Fuente: **FBref (Open Data)**
- Tipo: datos agregados de eventos
- Temporadas:
  - 2024/25
  - 2025/26

---

### 2. 🧹 Procesamiento

- Limpieza y estructuración del dataset
- Creación de métricas de progresión y participación
- Normalización de variables

---

### 3. 📊 Análisis

- Comparación inter-temporada del equipo
- Evaluación de:
  - progresión desde defensa  
  - volumen de pases progresivos  
  - comportamiento defensivo (proactivo vs reactivo)

---

### 4. 🤖 Modelado

Desarrollo de un sistema de similitud para identificar reemplazos potenciales:

- Definición de variables clave del rol
- Construcción de perfiles de jugador
- Comparación mediante métricas de distancia/similitud

---

## 📈 Resultados principales

El análisis muestra cambios estructurales relevantes en el equipo:

- 🔻 **Menor progresión desde zonas defensivas**
- 🔻 Reducción en la influencia de centrales en la construcción
- 🔺 Mayor tendencia a una **defensa reactiva**
- 🔺 Incremento de la dependencia del rendimiento ofensivo

Estos resultados sugieren una alteración del modelo, más allá de los resultados deportivos.

---

## 📂 Estructura del proyecto

```
analisis-barcelona/
│
├── data/
│   └── raw/          # Datos originales de FBref
│
├── notebooks/        # Análisis exploratorio
├── src/              # Scripts de extracción y procesamiento
├── output/           # Resultados (ej. radar, gráficos)
└── README.md
```

---

## 🛠️ Tecnologías utilizadas

- Python  
- Pandas  
- Jupyter Notebook  
- Web Scraping (FBref)  

---

## 🚀 Aplicaciones del proyecto

- Scouting y análisis de perfiles defensivos  
- Evaluación de impacto estructural en equipos  
- Identificación de reemplazos basados en datos  
- Apoyo a decisiones de mercado  

---

## 🔮 Líneas futuras

- Incorporar métricas avanzadas (xG buildup, progresiones por zona)  
- Ampliar análisis a más equipos  
- Integrar visualizaciones interactivas  
- Conectar con herramientas como Streamlit o Tableau  

---

## 👤 Autor

Franco Jordan  
Data Analyst | Sports Analytics  

🔗 [LinkedIn](https://www.linkedin.com/in/fjordanrv)
