import requests
import pandas as pd

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('Fmp_api_key')

def get_stock_data(ticker):
    # API URL and Key
    api_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}"
      # API key

    # Making a request to the API
    response = requests.get(api_url, params={"apikey": api_key})

    # Checking if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extracting the relevant part of the data
        historical_data = data.get("historical", [])
        Prices = pd.DataFrame(historical_data)
        Prices = Prices.iloc[::-1]
        return Prices
    else:
        print("Failed to retrieve data")
        return pd.DataFrame()
    

def get_company_peers(ticker):
    """Get the Income Statement."""
    URL = 'https://financialmodelingprep.com/api/v4/stock_peers'
    try:
        r = requests.get('{}?symbol={}&apikey={}'.format(URL, ticker, api_key))
        peers = pd.DataFrame.from_dict(r.json()).transpose()
        #Target.columns = Target.loc['symbol']
        return peers.iloc[1,0]
    except requests.exceptions.HTTPError as e:
        print('Requesting Income statement sheet ERROR: ', str(e))


def get_company_multiples(ticker, period='quarter'):
    """Get the Income Statement."""
    URL = 'https://financialmodelingprep.com/api/v3/ratios/'
    try:
        r = requests.get(f'{URL}{ticker}?period={period}&apikey={api_key}')
        r.raise_for_status()  # This will raise an HTTPError if the request returned an unsuccessful status code.
        ratiosPerC = pd.DataFrame.from_dict(r.json()).transpose()
        a = ratiosPerC.iloc[:, :1]  # Selecting the first column in a way that avoids future warnings.
        # Ensure the DataFrame is not empty before setting columns
        if not a.empty:
            first_value = a.iloc[0, 0] if not a.iloc[:, 0].empty else 'Default_Column_Name'
            a.columns = [f'{first_value}']
        return a
    except requests.exceptions.RequestException as e:  # Catches HTTPError, Timeout, etc.
        print('Requesting Income statement sheet ERROR: ', str(e))



def get_peers_multiples(ticker, period='quarter'):
    # Assuming get_company_multiples and get_company_peers are defined elsewhere
    compared_multiple = get_company_multiples(ticker=ticker, period=period)

    peers = get_company_peers(ticker=ticker)
    peer_multiples = [get_company_multiples(ticker=peer, period=period) for peer in peers]

    # Ensure the DataFrames have the same structure or handle discrepancies before concatenating
    # This avoids the problem by ensuring each DataFrame has a compatible structure
    all_multiples = [compared_multiple] + peer_multiples
    result = pd.concat(all_multiples, axis=1)
    result = result.reset_index()  
    
    return result.iloc[4:]


def get_yield(offset, key = api_key):

        today = datetime.now().date().strftime("%Y-%m-%d")
        offset_today = (datetime.now().date() - relativedelta(months=offset)).strftime("%Y-%m-%d")

        """Getting the current quote of the company."""
        URL = 'https://financialmodelingprep.com/api/v4/treasury?'
        try:
            r = requests.get('{}from={}&to={}&apikey={}'.format(URL, offset_today, today,  key))
            quote = pd.DataFrame.from_dict(r.json())
            quote['date'] = pd.to_datetime(quote['date'])
            quote.set_index("date", inplace=True)
            quote.T.columns = pd.to_datetime(quote.T.columns)
            return quote
        except requests.exceptions.HTTPError as e:
            print('Requesting quote estimate ERROR: ', str(e))


#yield_curve1['date'] = pd.to_datetime(yield_curve1['date'])
#yield_curve1.set_index("date", inplace=True)
#yield_curve1
# offset is the amount of last months to get data for
#yield_curve1.T.columns = pd.to_datetime(yield_curve1.T.columns)


def get_indicators (ticker, indicators, periods):
    start_date=datetime.today() - timedelta(days=5000)
    end_date=datetime.today()
    api_key=os.getenv('Fmp_api_key')
    base_url = "https://financialmodelingprep.com/api/v3/technical_indicator/1day"
    df_main = pd.DataFrame()
    close_extracted = False

    # Format start_date and end_date as strings in 'YYYY-MM-DD' format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    for indicator, period in zip(indicators, periods):
        params = {
            "apikey": api_key,
            "type": indicator,
            "period": period,
            "from": start_date_str,
            "to": end_date_str,
        }
        response = requests.get(f"{base_url}/{ticker}", params=params)
        
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df['date'] = pd.to_datetime(df['date'])
            
            if not close_extracted:
                df_main = df[['date', 'close']].copy()
                close_extracted = True
                
            indicator_label = f"{indicator}{period}"  # e.g., "ema10"
            df.rename(columns={indicator: indicator_label}, inplace=True)
            df_main = pd.merge(df_main, df[['date', indicator_label]], on='date', how='left')
        else:
            print(f"Failed to retrieve data for {indicator}{period}")

    if indicators[0] == 'standardDeviation':
      df_main['+2StDev ({})'.format(period)] = df_main['close'] + 2 * df_main['standardDeviation{}'.format(period)]
      df_main['-2StDev ({})'.format(period)] = df_main['close'] - 2 * df_main['standardDeviation{}'.format(period)]
      df_main.drop(columns=['standardDeviation{}'.format(period)], inplace=True)
    else: 
      pass

    return df_main


