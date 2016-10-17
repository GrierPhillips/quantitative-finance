import pandas as pd
import datetime as dt
import os


class PriceHistoryBuilder:
    def __init__(self, symbol=None, interval=61):
        self.symbol = symbol
        self.interval = interval
        self.filename = os.getcwd() + '/' + self.symbol + '.csv'

    def BuildHistory(self):
        '''Prompt for the input of a symbol and the interval to collect data. Use this to input into the google finance site for data output.
        Using this data produce a csv file that can be added to at the end of each trading day.'''
        if self.symbol is None:
            self.symbol = raw_input('Enter a stock symbol: ').upper()
            print('You entered: ' + self.symbol)
            self.interval = int(raw_input('Enter a time interval in seconds (Multiples of 60 accepted 60,120,180,...): ')) + 1
            self.filename = raw_input('Enter desired filename: ')
            self.filename = os.getcwd() + '/' + self.filename + '.csv'
            print('File will be saved as: ', self.filename)
        data = pd.read_csv(r'http://www.google.com/finance/getprices?i={}&p=10d&f=d,o,h,l,c,v&df=cpct&q={}'.format(self.interval, self.symbol), engine='python', skiprows=7, header=None, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
        # data['Date'] = data['Date'].map(lambda x: int(x[1:]))
        # data['Date'] = data['Date'].map(lambda x: int(x[1:]) if x[0] == 'a' else int(x))
        # data['Date'] = data['Date'].map(lambda x: x * 60 if x < 400 else x)
        # threshold = 24000
        # data['Timestamp'] = data[data['Date'] > threshold].loc[:, 'Date']
        # data['Timestamp'] = data['Timestamp'].fillna(method='ffill')
        # data['Date'] = data.apply(lambda x: x.Date + x.Timestamp if x.Date < threshold else x.Date, axis=1)
        # data = data.drop('Timestamp', axis=1)
        data['Date'] = data['Date'].apply(lambda x: dt.datetime.utcfromtimestamp(int(x[1:])))
        if not os.path.exists('../Records'):
            os.mkdir('../Records')
        os.chdir('../Records')
        if os.path.isfile(self.filename):
            orig_data = pd.read_csv(self.filename, parse_dates=['Date'])
            out = pd.concat([orig_data, data], ignore_index=True)
            out = out.drop_duplicates(subset='Date')
            out = out.sort_values(by='Date')
            out.to_csv(self.filename, index=False)
        else:
            data.to_csv(self.filename, index=False)

# TODO: Change storage location to sql db or hdf from csv.
# TODO: Automate time of collection with chron.
