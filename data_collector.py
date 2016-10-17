from pricehistory import PriceHistoryBuilder
import pandas as pd

dow_tickers = [
    'AAPL','AXP','BA','CAT','CSCO','CVX','KO','DD','XOM','GE','GS','HD','IBM','INTC','JNJ','JPM','MCD','MMM',
    'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UNH','UTX', 'V', 'VZ', 'WMT', 'DIS'
]
indices_etfs = ['DIA', 'QQQ', 'SPY']
s_p_500 = pd.read_csv('../Records/S&P_500_Equities.csv')
s_p_500_tickers = s_p_500.Symbol.tolist()
all_tickers = dow_tickers + indices_etfs + s_p_500_tickers
for ticker in all_tickers:
    ph = PriceHistoryBuilder(ticker)
    ph.BuildHistory()
