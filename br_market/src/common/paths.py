"""Centralized filesystem paths for the pipeline.

Resolves everything relative to the repo root instead of the process's CWD,
so scripts behave the same whether run from `br_market/src/scraper/`,
`br_market/src/`, or anywhere else.
"""

from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BR_MARKET_DIR = REPO_ROOT / "br_market"
DATA_DIR = BR_MARKET_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FINAL_DIR = DATA_DIR / "final"
CACHE_DIR = DATA_DIR / "cache"

for _dir in (RAW_DIR, PROCESSED_DIR, FINAL_DIR, CACHE_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


def today_str() -> str:
    return datetime.today().strftime("%d-%m-%Y")


def raw_news_path(date_str: str, ticker: str | None = None) -> Path:
    if ticker:
        return RAW_DIR / f"{ticker}_{date_str}_news.csv"
    return RAW_DIR / f"brazilian_stocks_{date_str}_news.csv"


def processed_sentiment_path(date_str: str, ticker: str | None = None) -> Path:
    if ticker:
        return PROCESSED_DIR / f"{ticker}_{date_str}_news_with_finbert_sentiment.csv"
    return PROCESSED_DIR / f"brazilian_stocks_news_with_finbert_sentiment_{date_str}.csv"


def final_path(date_str: str, ticker: str | None = None) -> Path:
    if ticker:
        return FINAL_DIR / f"{ticker}_{date_str}_with_sentiment_and_historical_data.csv"
    return FINAL_DIR / f"brazilian_stocks_with_sentiment_and_historical_data_{date_str}.csv"


def current_data_path(date_str: str, ticker: str | None = None) -> Path:
    if ticker:
        return RAW_DIR / f"{ticker}_{date_str}_current_data.csv"
    return RAW_DIR / f"brazilian_stocks_current_data_{date_str}.csv"


def historical_data_path(date_str: str, ticker: str | None = None) -> Path:
    if ticker:
        return RAW_DIR / f"{ticker}_{date_str}_historical_data.csv"
    return RAW_DIR / f"brazilian_stocks_historical_data_{date_str}.csv"
