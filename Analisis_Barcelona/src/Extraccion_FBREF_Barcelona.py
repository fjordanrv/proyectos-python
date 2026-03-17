from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os
from pathlib import Path

"""
selenium: controla el navegador (abrir Chrome, cargar páginas, etc.).

ChromeDriverManager: se encarga de descargar y usar el driver correcto de Chrome automáticamente (tú no tienes que bajarlo a mano).

Options: configura cómo se abre Chrome (modo headless, tamaño de ventana, etc.).

WebDriverWait, EC, By: para esperar a que ciertos elementos aparezcan en la página (por ejemplo, que cargue una tabla).

BeautifulSoup: para parsear (leer y navegar) el HTML de la página.

pandas: para convertir tablas HTML en DataFrames.

StringIO: para envolver el HTML en un “falso archivo” y que pd.read_html pueda leerlo.

os: sirve para trabajar con rutas, archivos, etc.
"""
def get_chrome_options(headless=True):
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return options

def get_selected_tables(url, headless=True):
    # Configuración de opciones para Chrome
    options = get_chrome_options(headless)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    """
    ChromeDriverManager().install() descarga (si hace falta) y localiza el ChromeDriver.

    Service(...) le dice a Selenium dónde está ese driver.

    webdriver.Chrome(...) abre una instancia de Chrome lista para usar.
    """
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Esperar a que aparezca al menos una tabla
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        html = driver.page_source
        """
        driver.get(url): abre la página.
        WebDriverWait(driver, 15): crea una espera de hasta 15 segundos.
        wait.until(...): espera a que exista al menos un elemento <table> en la página.
        driver.page_source: obtiene el HTML completo de la página ya cargada.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Buscar todas las tablas cuyo ID no contenga "table"
        tables = soup.find_all("table")
        dfs = {}
        for table in tables:
            table_id = table.get("id")
            if table_id and "table" not in table_id.lower():
                try:
                    df = pd.read_html(StringIO(str(table)))[0]
                    dfs[table_id] = df
                    print(f"Extraída tabla con ID: {table_id}")
                except Exception as e:
                    print(f"Error leyendo tabla {table_id}: {e}")
        
        return dfs

    except Exception as e:
        print(f"Error general: {e}")
        return {}
    finally:
        driver.quit()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def build_fbref_url(season):
    # season = "2024-2025"
    return f"https://fbref.com/en/comps/12/{season}/{season}-La-Liga-Stats"

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""def get_players_stats(url, headless=True):
    # Configuración de opciones para Chrome
    options = get_chrome_options(headless)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Esperar a que aparezca al menos una tabla
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        # Buscar todas las tablas cuyo ID no contenga "table"
        tables = soup.find_all("table")
        dfs = {}
        for table in tables:
            table_id = table.get("id")
            if table_id and "table" not in table_id.lower():
                try:
                    df = pd.read_html(StringIO(str(table)))[0]
                    dfs[table_id] = df
                    print(f"Extraída tabla con ID: {table_id}")
                except Exception as e:
                    print(f"Error leyendo tabla {table_id}: {e}")
        
        return dfs

    except Exception as e:
        print(f"Error general: {e}")
        return {}
    finally:
        driver.quit()"""

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def scrape_and_save_teams(season, headless=True):
    BASE_DIR = Path(__file__).resolve().parents[1]
    url = build_fbref_url(season)

    tables = get_selected_tables(url, headless=headless)
    output_dir = BASE_DIR / "data" / "raw" / season

    output_dir.mkdir(parents=True, exist_ok=True)
    # Guardar CSVs
    for table_id, df in tables.items():
        df.to_csv(output_dir / f"{table_id}_{season}.csv", index=False)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def scrape_and_save_players(season, headless=True):
    BASE_DIR = Path(__file__).resolve().parents[1]
    url = f"https://fbref.com/en/squads/206d90db/{season}/Barcelona-Stats"

    tables = get_selected_tables(url, headless=headless)

    output_dir = BASE_DIR / "data" / "raw" / season / "players"
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_id, df in tables.items():
        df.to_csv(output_dir / f"{table_id}_{season}.csv", index=False)

    return tables

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def scrape_and_save_comparison(url, player, headless=True):
    BASE_DIR = Path(__file__).resolve().parents[1]
    url = url

    tables = get_selected_tables(url, headless=headless)

    output_dir = BASE_DIR / "data" / "raw" / 'comparison'
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_id, df in tables.items():
        df.to_csv(output_dir / f"{table_id}_{player}.csv", index=False)

    return tables
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main():
    season = "2024-2025"
    url = ''
    scrape_and_save_teams(season, headless=False)

    #jugadores
    scrape_and_save_players(season, headless=False)
    
    #comparacion
    scrape_and_save_comparison(url, headless=False)

    
if __name__ == "__main__":
    main()