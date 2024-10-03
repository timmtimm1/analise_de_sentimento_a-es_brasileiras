import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime

def create_scraper():
    return cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_page_content(url, scraper):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://finviz.com/',
        'DNT': '1',
    }
    response = scraper.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve {url}. Status Code: {response.status_code}")
        return None

def get_tickers_from_page(page_number, scraper):
    url = f"https://finviz.com/screener.ashx?v=111&f=geo_brazil&r={1 + (page_number-1)*20}"
    html_content = get_page_content(url, scraper)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        ticker_cells = soup.select('table.styled-table-new a.tab-link')
        return [cell.text for cell in ticker_cells]
    return []

def get_all_tickers(scraper):
    all_tickers = []
    for page in range(1, 3):  # Pages 1 and 2
        tickers = get_tickers_from_page(page, scraper)
        all_tickers.extend(tickers)
        print(f"Extracted {len(tickers)} tickers from page {page}")
        time.sleep(random.uniform(0.5, 1))  # Random delay between requests
    return all_tickers

def get_company_and_news_links(ticker, scraper):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    html_content = get_page_content(url, scraper)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        company_element = soup.select_one("h2.quote-header_ticker-wrapper_company.text-xl a")
        company = company_element.text.strip() if company_element else "N/A"
        
        news_table = soup.find('table', {'id': 'news-table'})
        if news_table:
            news_data = []
            rows = news_table.find_all('tr')
            for row in rows:
                date_cell = row.find('td', {'align': 'right'})
                link_cell = row.find('a', {'class': 'tab-link-news'})
                if date_cell and link_cell:
                    date = date_cell.text.strip()
                    link = link_cell['href']
                    title = link_cell.text
                    news_data.append({
                        'date': date,
                        'title': title,
                        'link': link
                    })
            return company, news_data
    return "N/A", []

def main():
    scraper = create_scraper()
    all_tickers = get_all_tickers(scraper)
    print(f"Total tickers extracted: {len(all_tickers)}")
    
    all_news = []
    for ticker in all_tickers:
        print(f"Scraping news for {ticker}")
        company, news = get_company_and_news_links(ticker, scraper)
        for item in news:
            all_news.append({
                'company': company,
                'ticker': ticker,
                'date': item['date'],
                'title': item['title'],
                'link': item['link']
            })
        time.sleep(random.uniform(0.5, 1))  # Random delay between requests
    
    today = datetime.today().strftime('%d-%m-%Y')
    df = pd.DataFrame(all_news)
    df.to_csv(f'brazilian_stocks_{today}_news.csv', index=False)
    print(f"Scraped {len(df)} news items. Data saved to brazilian_stocks_{today}_news.csv")

if __name__ == "__main__":
    main()