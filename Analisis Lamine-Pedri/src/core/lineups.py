"""Extracción de alineaciones por partido desde FBref."""

import re
import time
from io import StringIO
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from .paths import DATA_CLEAN_DIR, LINEUPS_RAW


def create_scraper() -> Any:
    import cloudscraper

    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )


def extract_lineups(url: str, scraper: Any, season_folder: str) -> Optional[pd.DataFrame]:
    """
    Descarga lineup de un partido y guarda en data/raw/lineups/<season_folder>/lineups_<slug>.csv.
    """
    from bs4 import BeautifulSoup

    r = scraper.get(url)
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {url}")
        return None

    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table", {"id": "stats_206d90db_summary"})
    if table is None:
        print(f"No lineup table: {url}")
        return None

    df = pd.read_html(StringIO(str(table)))[0]
    df.columns = [
        col[1] if str(col[0]).startswith("Unnamed") else f"{col[0]}_{col[1]}"
        for col in df.columns
    ]

    m_id = re.search(r"/matches/([^/]+)/", url)
    if not m_id:
        return None
    df["match_id"] = m_id.group(1)

    m = re.search(r"/matches/[^/]+/([^/]+)$", url)
    if not m:
        print(f"Invalid URL: {url}")
        return None
    slug = m.group(1)

    out_dir = LINEUPS_RAW / season_folder
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"lineups_{slug}.csv"
    df.to_csv(out_path, index=False)
    return df


def scrape_lineups_for_season(
    season: str,
    scraper: Optional[Any] = None,
    sleep_seconds: float = 10.0,
) -> None:
    """
    Lee score_fixtures_clean_<season>.csv y descarga lineup de cada match_url.
    Puede tardar mucho (sleep entre peticiones para no saturar FBref).
    """
    clean_path = DATA_CLEAN_DIR / f"score_fixtures_clean_{season}.csv"
    if not clean_path.exists():
        raise FileNotFoundError(f"Falta {clean_path}; ejecuta antes extracción de partidos.")

    fixtures = pd.read_csv(clean_path)
    if scraper is None:
        scraper = create_scraper()

    for url in fixtures["match_url"].dropna():
        extract_lineups(str(url), scraper, season_folder=season)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
