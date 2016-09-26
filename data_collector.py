from pricehistory import PriceHistoryBuilder

dow_stocks = [
    'AAPL','AXP','BA','CAT','CSCO','CVX','KO','DD','XOM','GE','GS','HD','IBM','INTC','JNJ','JPM','MCD','MMM',
    'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UNH','UTX', 'V', 'VZ', 'WMT', 'DIS'
]
for stock in dow_stocks:
    ph = PriceHistoryBuilder(stock)
    ph.BuildHistory()
