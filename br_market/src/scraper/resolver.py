"""Company-name -> FinViz-scrapeable-ticker resolution.

Builds on top of scraper.main without modifying it: reuses get_all_tickers()
and get_company_and_news_links() (their selectors are already proven against
FinViz's live markup by the rest of this codebase) to build a small local
ticker<->company-name directory for the BR-geo screener, then resolves
free-text company names (or raw tickers) against it. Falls back to Yahoo
Finance's public search endpoint for companies outside that directory.
"""

import time
from datetime import datetime, timedelta
from difflib import get_close_matches
from pathlib import Path

import pandas as pd
import requests

from common.paths import CACHE_DIR
from scraper.main import get_all_tickers, get_company_and_news_links

DIRECTORY_CACHE_PATH = CACHE_DIR / "br_ticker_directory.csv"
CACHE_TTL = timedelta(days=7)


def get_tickers_and_companies(scraper) -> list[dict]:
    """Scrapes the BR-geo screener's tickers, then fetches each ticker's
    company name via the existing, already-verified get_company_and_news_links
    selector. Skips tickers FinViz has no quote page for (company == "N/A").
    """
    tickers = get_all_tickers(scraper)
    directory = []
    for ticker in tickers:
        company, _news = get_company_and_news_links(ticker, scraper)
        if company != "N/A":
            directory.append({"ticker": ticker, "company": company})
        time.sleep(0.2)
    return directory


def _cache_is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age < CACHE_TTL


def load_or_build_directory(scraper=None, force_refresh: bool = False) -> pd.DataFrame:
    if not force_refresh and _cache_is_fresh(DIRECTORY_CACHE_PATH):
        return pd.read_csv(DIRECTORY_CACHE_PATH)

    if scraper is None:
        from scraper.main import create_scraper

        scraper = create_scraper()

    rows = get_tickers_and_companies(scraper)
    df = pd.DataFrame(rows, columns=["ticker", "company"])
    df.to_csv(DIRECTORY_CACHE_PATH, index=False)
    return df


def _yahoo_search_fallback(query: str) -> str | None:
    """Resolves a company name to a ticker via Yahoo Finance's public
    (unauthenticated) search endpoint, for companies outside the cached BR
    directory. Best-effort: returns the first EQUITY match, if any.
    """
    try:
        response = requests.get(
            "https://query1.finance.yahoo.com/v1/finance/search",
            params={"q": query, "quotesCount": 5, "newsCount": 0},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        response.raise_for_status()
        quotes = response.json().get("quotes", [])
        for quote in quotes:
            if quote.get("quoteType") == "EQUITY" and quote.get("symbol"):
                return quote["symbol"]
    except (requests.RequestException, ValueError):
        pass
    return None


def resolve_company(query: str, directory: pd.DataFrame | None = None) -> str | None:
    """Resolves free-text company name or a raw ticker to a best-guess
    ticker symbol. Tries, in order:
      1. exact case-insensitive match against directory['ticker']
      2. case-insensitive substring match of query inside a cached company name
      3. difflib.get_close_matches against cached company names
      4. Yahoo Finance search fallback

    Returns None if nothing matches.
    """
    query_norm = query.strip()
    if not query_norm:
        return None

    if directory is None or directory.empty:
        return _yahoo_search_fallback(query_norm)

    query_lower = query_norm.lower()

    exact_ticker = directory[directory["ticker"].str.lower() == query_lower]
    if not exact_ticker.empty:
        return exact_ticker.iloc[0]["ticker"]

    substring_match = directory[directory["company"].str.lower().str.contains(query_lower, regex=False)]
    if not substring_match.empty:
        return substring_match.iloc[0]["ticker"]

    companies = directory["company"].tolist()
    close = get_close_matches(query_norm, companies, n=1, cutoff=0.5)
    if close:
        match_row = directory[directory["company"] == close[0]]
        return match_row.iloc[0]["ticker"]

    return _yahoo_search_fallback(query_norm)
