"""Extracción y limpieza de partidos (fixtures) del Barça desde FBref."""

from io import StringIO

import pandas as pd

from .paths import DATA_CLEAN_DIR, SCORE_FIXTURES_RAW


def extract_matchs(season: str) -> pd.DataFrame:
    """Descarga la tabla de partidos all_comps y guarda CSV en data/raw/score_fixtures/."""
    import cloudscraper
    from bs4 import BeautifulSoup

    url = (
        f"https://fbref.com/en/squads/206d90db/{season}/"
        f"all_comps/Barcelona-Stats-All-Competitions"
    )
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    r = scraper.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table", {"id": "matchlogs_for"})
    if table is None:
        raise ValueError(f"No se encontró matchlogs_for para temporada {season}")

    df = pd.read_html(StringIO(str(table)))[0]
    rows = table.find("tbody").find_all("tr")
    match_urls = []
    for row in rows:
        cell = row.find("td", {"data-stat": "match_report"})
        if cell is None:
            match_urls.append(None)
            continue
        a = cell.find("a")
        if a and "href" in a.attrs:
            match_urls.append("https://fbref.com" + a["href"])
        else:
            match_urls.append(None)

    df["match_report_url"] = match_urls
    SCORE_FIXTURES_RAW.mkdir(parents=True, exist_ok=True)
    out = SCORE_FIXTURES_RAW / f"score_fixtures_{season}.csv"
    df.to_csv(out, index=False)
    return df


def clean_matchs(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Normaliza columnas y guarda en data/clean/score_fixtures_clean_<season>.csv."""
    df = df.copy()
    df = df[
        [
            "match_report_url",
            "Date",
            "Comp",
            "Venue",
            "Opponent",
            "GF",
            "GA",
            "xG",
            "xGA",
            "Poss",
        ]
    ]
    df["match_id"] = df["match_report_url"].str.extract(r"/matches/([^/]+)/")
    df["season"] = season
    df = df[
        [
            "match_id",
            "match_report_url",
            "Date",
            "season",
            "Comp",
            "Opponent",
            "Venue",
            "GF",
            "GA",
            "xG",
            "xGA",
            "Poss",
        ]
    ]
    df.rename(
        columns={
            "match_report_url": "match_url",
            "Date": "date",
            "Comp": "competition",
            "Opponent": "opponent",
            "Venue": "home_away",
            "GF": "goals_for",
            "GA": "goals_against",
            "xG": "xG_for",
            "xGA": "xG_against",
            "Poss": "posesion",
        },
        inplace=True,
    )
    DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_CLEAN_DIR / f"score_fixtures_clean_{season}.csv"
    df.to_csv(out, index=False)
    return df


def run_extract_and_clean_fixtures(season: str) -> pd.DataFrame:
    """Pipeline: descarga + limpia una temporada."""
    raw = extract_matchs(season)
    return clean_matchs(raw, season)
