# Collect data at any scale available on google finance and either create a new file or append it into a database.
# Minimum resolution is 1 min with 10 days of historical data

import numpy as np
import pandas as pd
import datetime
import os
from pandas.io.data import DataReader
	
class PriceHistoryBuilder:
	
	def _init_(self, symbol, interval, filename):
		self.symbol = symbol
		self.interval = interval
		self.filename = filename
	
	def BuildHistory(self):
	# Prompt for the input of a symbol and the interval to collect data. Use this to input into the google finance site for data output.
	# Using this data produce a csv file that can be added to at the end of each trading day.
	
		print("Enter a symbol:")
		symbol = input()
		symbol = symbol.upper()
		print("You entered: " + symbol)
		print("Enter a time interval in seconds: ")
		interval = input()
	
		data = pd.read_csv(r'http://www.google.com/finance/getprices?i={}&p=10d&f=d,o,h,l,c,v&df=cpct&q={}'.format(interval, symbol), sep=',', engine='python', skiprows=7, header=None, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
		print(data.head())
		# remove extraneous 'a' at beginning of each trading day timestamp, convert the resulting values to integers
		data['Date'] = data['Date'].map(lambda x: int(x[1:]) if x[0] == 'a' else int(x))
		data['Date'] = data['Date'].map(lambda u: u * 60 if u < 400 else u)
		threshold = 24000
		data['Timestamp'] = data[data['Date']>threshold].loc[:, 'Date']
		data['Timestamp'] = data['Timestamp'].fillna(method='ffill')
		data['Date'] = data.apply(lambda x: x.Date + x.Timestamp if x.Date < threshold else x.Date, axis=1)
		data.drop('Timestamp', axis=1, inplace=True)
			
		print("Enter desired filename: ")
		filename = input()
		filename = os.getcwd() + r'\\' + filename + ".csv"
		print(filename)
		
		if os.path.isfile(filename):
			orig_data = pd.read_csv(filename, header=None, index_col=False, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
			print(orig_data.tail())
			last_time = orig_data['Date'].iloc[-1]
			print(last_time)
			data = data[data.Date > last_time]
			print(data.head())
			with open(filename, 'a') as f:
				data.to_csv(f, header=False, index=False)
		
		else:
			with open(filename, 'a') as f:
				data.to_csv(f, header=False, index=False)
	
	
	
if __name__ == "__main__":
			
	ph = PriceHistoryBuilder()
	
	ph.BuildHistory()
	
	
	
