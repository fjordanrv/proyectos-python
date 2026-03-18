"""Entry point for the Lautaro Martínez replacement analysis project.

Running this module will:

- Cargar los datos crudos de jugadores argentinos (últimas dos temporadas).
- Agregar las métricas por jugador (por 90 minutos y totales sin normalizar).
- Calcular distancias a Lautaro, `replacement_score` y ranking de reemplazos.
- Exportar las tablas limpias a `src/data/clean/` listas para Tableau.
"""

from core import run_full_pipeline


def main() -> None:
    run_full_pipeline()


if __name__ == "__main__":
    main()

