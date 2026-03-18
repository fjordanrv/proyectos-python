from pathlib import Path
from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _get_chrome_options(headless: bool = True) -> Options:
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return options


def _get_selected_tables(url: str, headless: bool = True) -> Dict[str, pd.DataFrame]:
    """Descarga una página de FBRef y devuelve las tablas relevantes como DataFrames."""
    options = _get_chrome_options(headless)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table")
        dfs: Dict[str, pd.DataFrame] = {}

        for table in tables:
            table_id = table.get("id")
            if table_id and "table" not in table_id.lower():
                try:
                    df = pd.read_html(StringIO(str(table)))[0]
                    dfs[table_id] = df
                except Exception:
                    # ignorar tablas que fallen al parsear
                    continue

        return dfs

    finally:
        driver.quit()


def build_fbref_league_url(season: str) -> str:
    """Crea la URL de estadísticas de LaLiga en FBRef para una temporada dada."""
    return f"https://fbref.com/en/comps/12/{season}/{season}-La-Liga-Stats"


def build_fbref_barcelona_url(season: str) -> str:
    """URL de estadísticas agregadas del FC Barcelona para una temporada."""
    return f"https://fbref.com/en/squads/206d90db/{season}/Barcelona-Stats"


def scrape_and_save_teams(season: str, headless: bool = True) -> None:
    """Descarga tablas de equipos de LaLiga y las guarda en data/raw/<season>."""
    url = build_fbref_league_url(season)
    tables = _get_selected_tables(url, headless=headless)

    output_dir = DATA_RAW_DIR / season
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_id, df in tables.items():
        df.to_csv(output_dir / f"{table_id}_{season}.csv", index=False)


def scrape_and_save_players(season: str, headless: bool = True) -> Dict[str, pd.DataFrame]:
    """Descarga tablas de jugadores del FC Barcelona y las guarda en data/raw/<season>/players."""
    url = build_fbref_barcelona_url(season)
    tables = _get_selected_tables(url, headless=headless)

    output_dir = DATA_RAW_DIR / season / "players"
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_id, df in tables.items():
        df.to_csv(output_dir / f"{table_id}_{season}.csv", index=False)

    return tables


def scrape_and_save_comparison(url: str, player: str, headless: bool = True) -> Dict[str, pd.DataFrame]:
    """Descarga tablas de comparación para un jugador concreto y las guarda en data/raw/comparison."""
    tables = _get_selected_tables(url, headless=headless)

    output_dir = DATA_RAW_DIR / "comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_id, df in tables.items():
        df.to_csv(output_dir / f"{table_id}_{player}.csv", index=False)

    return tables

