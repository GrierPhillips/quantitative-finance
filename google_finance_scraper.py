# This snipped will pull the data from equity DIA at 1 minute intervals

import pandas as pd
import numpy as np
import datetime

bars = pd.read_csv(r'http://www.google.com/finance/getprices?i=60&p=10d&f=d,o,h,l,c,v&df=cpct&q=DIA', skiprows=7, header=None, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
# In the above line the eqity can be changed by changing 'q=%equity%', time scale with 'i=%seconds%', and period with 'p=%period%'
# if you try to exceed the available data period or enter a interval lower than 60 it will default to the last viable resolution.
# i.e. the last viable period or time interval. For 1 minute intervals the max period is 10 days.

bars['Date'] = bars['Date'].map(lambda x: int(x[1:]) if x[0] == 'a' else int(x))
bars['Date'] = bars['Date'].map(lambda u: u * 60 if u < 400 else u)
threshold = 24000
bars['Timestamp'] = bars[bars['Date']>threshold].loc[:, 'Date']
bars['Timestamp'] = bars['Timestamp'].fillna(method='ffill')
bars['Date'] = bars.apply(lambda x: x.Date + x.Timestamp if x.Date < threshold else x.Date, axis=1)
bars.drop('Timestamp', axis=1, inplace=True)
bars['Date'] = bars['Date'].map(lambda v: datetime.datetime.fromtimestamp(v))
