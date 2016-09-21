# Collect data at any scale available on google finance and either create a new file or append it into a database.
# Minimum resolution is 1 min with 10 days of historical data

import pandas as pd
import datetime
import os


class PriceHistoryBuilder:
	def _init_(self, symbol, interval, filename):
		self.symbol = symbol
		self.interval = interval
		self.filename = filename

	def BuildHistory(self):
		'''Prompt for the input of a symbol and the interval to collect data. Use this to input into the google finance site for data output.
		Using this data produce a csv file that can be added to at the end of each trading day.'''

		print("Enter a symbol:")
		symbol = raw_input()
		symbol = symbol.upper()
		print("You entered: " + symbol)
		print("Enter a time interval in seconds: ")
		interval = raw_input()

		data = pd.read_csv(r'http://www.google.com/finance/getprices?i={}&p=10d&f=d,o,h,l,c,v&df=cpct&q={}'.format(interval, symbol), sep=',', engine='python', skiprows=7, header=None, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
		print(data.head())
		# remove extraneous 'a' at beginning of each trading day timestamp, convert the resulting values to integers, then to timestamp
		data['Date'] = data['Date'].map(lambda x: int(x[1:]) if x[0] == 'a' else int(x))
		data['Date'] = data['Date'].map(lambda x: x * 60 if x < 400 else x)
		threshold = 24000
		data['Timestamp'] = data[data['Date'] > threshold].loc[:, 'Date']
		data['Timestamp'] = data['Timestamp'].fillna(method='ffill')
		data['Date'] = data.apply(lambda x: x.Date + x.Timestamp if x.Date < threshold else x.Date, axis=1)
		data.drop('Timestamp', axis=1, inplace=True)
		data['Date'] = data['Date'].apply(datetime.datetime.utcfromtimestamp)

		# Get filename and construct path for saving file
		print("Enter desired filename: ")
		filename = raw_input()
		filename = os.getcwd() + '/' + filename + ".csv"
		print('File will be saved as: ', filename)

		if os.path.isfile(filename):
			orig_data = pd.read_csv(filename, parse_dates=['Date'])
			out = pd.concat([orig_data, data], ignore_index=True)
			out = out.drop_duplicates(subset='Date')
			out = out.sort_values(by='Date')
			out.to_csv(filename, index=False)

		else:
			data.to_csv(filename, index=False)

if __name__ == "__main__":

	ph = PriceHistoryBuilder()
	ph.BuildHistory()
