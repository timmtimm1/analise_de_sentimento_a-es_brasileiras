import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import time
import random
from scipy import stats

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    try:
        data = {
            'Ticker': ticker,
            'Company Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'Current Price': info.get('currentPrice', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Average Volume': info.get('averageVolume', 'N/A'),
            'Beta': info.get('beta', 'N/A')
        }
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None

def get_historical_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start="2005-01-01", end=date.today().strftime("%Y-%m-%d"))
        hist.reset_index(inplace=True)
        hist['Ticker'] = ticker
        return hist
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {str(e)}")
        return None

def calculate_cumulative_return(df, ticker, date, n_days):
    future_prices = df[(df['Ticker'] == ticker) & 
                       (df['Date'] > date) & 
                       (df['Date'] <= date + timedelta(days=n_days))]
    
    if len(future_prices) > 0:
        return (future_prices['Close'].iloc[-1] / df[df['Date'] == date]['Close'].iloc[0]) - 1
    else:
        return np.nan

def parse_sentiment_date(date_str):
    if pd.isna(date_str):
        return pd.NaT
    
    try:
        dt = pd.to_datetime(date_str, format='%b-%d-%y %I:%M%p')
        if dt.year > datetime.now().year:
            dt = dt.replace(year=dt.year-100)
        return dt.date()
    except ValueError:
        try:
            time = pd.to_datetime(date_str, format='%I:%M%p').time()
            return datetime.now().date()
        except ValueError:
            return pd.NaT

def main():
    tickers = ['ABEV', 'AFYA', 'ASAI', 'ATLX', 'AZUL', 'BAK', 'BBD', 'BRFS', 'BSBR', 'CIG', 
               'CINT', 'CSAN', 'EBR', 'ELP', 'ELPC', 'ERJ', 'GGB', 'INTR', 'ITUB', 'LND', 
               'LVRO', 'NVNI', 'PAGS', 'PBR', 'PBR-A', 'SBS', 'SGML', 'SID', 'SUZ', 'TIMB', 
               'UGP', 'VALE', 'VINP', 'VIV', 'VSTA', 'XP', 'ZENV']

    all_data = []
    all_historical_data = []

    for ticker in tickers:
        print(f"Fetching data for {ticker}")
        stock_data = get_stock_data(ticker)
        if stock_data:
            all_data.append(stock_data)
        
        print(f"Fetching historical data for {ticker}")
        hist_data = get_historical_data(ticker)
        if hist_data is not None and not hist_data.empty:
            all_historical_data.append(hist_data)
        
        time.sleep(random.uniform(0.5, 1))  # Random delay to avoid rate limiting

    df = pd.DataFrame(all_data)
    df_hist = pd.concat(all_historical_data, ignore_index=True)
    
    today = datetime.today().strftime('%d-%m-%Y')
    current_data_filename = f'brazilian_stocks_current_data_{today}.csv'
    historical_data_filename = f'brazilian_stocks_historical_data_{today}.csv'
    
    df.to_csv(current_data_filename, index=False)
    df_hist.to_csv(historical_data_filename, index=False, date_format='%Y-%m-%d')
    
    print(f"Current data saved to {current_data_filename}")
    print(f"Historical data saved to {historical_data_filename}")

    # Load sentiment data
    sentiment_df = pd.read_csv(f'brazilian_stocks_news_with_finbert_sentiment_{today}.csv')
    sentiment_df['date'] = sentiment_df['date'].apply(parse_sentiment_date)
    sentiment_df = sentiment_df.dropna(subset=['date'])

    # Prepare historical data
    df_hist['Date'] = pd.to_datetime(df_hist['Date']).dt.date

    # Merge sentiment and historical data
    latest_historical_date = df_hist['Date'].max()
    sentiment_df = sentiment_df[sentiment_df['date'] <= latest_historical_date]
    merged_df = pd.merge(sentiment_df, df_hist, left_on=['ticker', 'date'], right_on=['Ticker', 'Date'], how='inner')

    # Calculate returns
    for days in [1, 3, 7]:
        merged_df[f'{days}d_Return'] = merged_df.apply(
            lambda row: calculate_cumulative_return(df_hist, row['Ticker'], row['Date'], days), 
            axis=1
        )

    # Clean up and format the final dataframe
    merged_df = merged_df.dropna(subset=[f'{days}d_Return' for days in [1, 3, 7]], how='all')
    merged_df = merged_df.drop(columns=['Date', 'Ticker'])
    merged_df = merged_df.rename(columns={
        'company': 'Company',
        'ticker': 'Ticker',
        'date': 'Date',
        'title': 'Title',
        'link': 'Link',
        'positive_score': 'Positive_Score',
        'negative_score': 'Negative_Score',
        'neutral_score': 'Neutral_Score',
        'overall_sentiment': 'Overall_Sentiment'
    })
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])

    # Save the final merged dataframe
    final_filename = f"brazilian_stocks_with_sentiment_and_historical_data_{today}.csv"
    merged_df.to_csv(final_filename, index=False)
    print(f"Final merged data saved to {final_filename}")

if __name__ == "__main__":
    main()