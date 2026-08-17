"""Single-company automated pipeline: resolve a company name (or ticker),
scrape its FinViz news, score sentiment with FinBERT, merge with historical
stock returns, and print a summary -- all in one command.

Usage:
    python company_pipeline.py --company "Petrobras"
    python company_pipeline.py --company PBR
    python company_pipeline.py            # interactive prompt
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from common import paths
from scraper.main import create_scraper, get_company_and_news_links
from scraper.resolver import load_or_build_directory, resolve_company
from sentiment_analysis.sentiment import analyze_sentiment_df
from transform import transform


def run_for_company(query: str, save_outputs: bool = True) -> pd.DataFrame:
    scraper = create_scraper()

    print(f"Resolvendo '{query}'...")
    directory = load_or_build_directory(scraper=scraper)
    ticker = resolve_company(query, directory)
    if ticker is None:
        raise SystemExit(
            f"Não foi possível identificar um ticker para '{query}'. "
            f"Esta ferramenta depende de a empresa ter ADR listado nos EUA e "
            f"coberto pelo FinViz."
        )
    print(f"'{query}' -> ticker {ticker}")

    company, news = get_company_and_news_links(ticker, scraper)
    if company == "N/A" and not news:
        raise SystemExit(
            f"'{ticker}' não foi encontrado no FinViz (quote.ashx). "
            f"Verifique o nome/ticker informado -- esta é uma limitação de "
            f"a fonte de notícias ser exclusivamente o FinViz."
        )
    if not news:
        raise SystemExit(f"'{ticker}' ({company}) foi encontrado, mas não há notícias recentes no FinViz.")

    today = paths.today_str()
    news_df = pd.DataFrame([
        {'company': company, 'ticker': ticker, 'date': item['date'], 'title': item['title'], 'link': item['link']}
        for item in news
    ])
    if save_outputs:
        raw_path = paths.raw_news_path(today, ticker)
        news_df.to_csv(raw_path, index=False)
        print(f"Notícias salvas em {raw_path}")

    print(f"Analisando sentimento de {len(news_df)} notícias com FinBERT...")
    sentiment_df = analyze_sentiment_df(news_df)
    if save_outputs:
        processed_path = paths.processed_sentiment_path(today, ticker)
        sentiment_df.to_csv(processed_path, index=False)
        print(f"Sentimento salvo em {processed_path}")

    print(f"Buscando dados de mercado para {ticker}...")
    merged = transform.run(tickers=[ticker], sentiment_df=sentiment_df, date_str=today, save_outputs=save_outputs)

    _print_summary(ticker, company, merged)
    return merged


def _print_summary(ticker: str, company: str, df: pd.DataFrame) -> None:
    print(f"\n=== Resumo: {company} ({ticker}) ===")
    if df.empty:
        print("Nenhuma notícia pôde ser combinada com dados históricos de preço (dados de mercado insuficientes para a data das notícias).")
        return

    print("\nDistribuição de sentimento:")
    print(df['Overall_Sentiment'].value_counts().to_string())

    print("\nScores médios:")
    print(df[['Positive_Score', 'Negative_Score', 'Neutral_Score']].mean().to_string())

    print("\nRetorno médio após a notícia:")
    for days in [1, 3, 7]:
        col = f'{days}d_Return'
        if col in df.columns:
            print(f"  {days}d: {df[col].mean():.4%}")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de sentimento para uma única empresa/ticker.")
    parser.add_argument('--company', '-c', default=None, help="Nome da empresa ou ticker, ex: 'Petrobras' ou 'PBR'")
    parser.add_argument('--no-save', action='store_true', help="Não salvar CSVs intermediários/finais em disco")
    args = parser.parse_args()

    company = args.company or input("Nome da empresa ou ticker: ").strip()
    if not company:
        parser.error("É necessário informar uma empresa.")

    run_for_company(company, save_outputs=not args.no_save)


if __name__ == "__main__":
    main()
