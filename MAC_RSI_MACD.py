
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import matplotlib.dates as md
import matplotlib.ticker as mt
import matplotlib.finance as mf
import matplotlib.widgets as mw
from pandas.io.data import DataReader
from pandas import ExcelWriter
from backtest import Strategy, Portfolio, Analysis

class TechnicalAnalysis(Analysis):
	def __init__(self, symbol, bars, short_window, long_window, rsi_per=100, macd_per=50):
		self.symbol = symbol
		self.bars = bars
		self.short_window = short_window
		self.long_window = long_window
		self.rsi_per = rsi_per
		self.macd_per = macd_per
		self.ema = self.EMA()
		
	# Define moving averages (using ema)
	def EMA(self):
		mavgs = pd.DataFrame(index=self.bars.index)
		mavgs['short_mavg'] =  pd.ewma(bars['Close'], span=self.short_window, min_periods=1)
		mavgs['long_mavg'] = pd.ewma(bars['Close'], span=self.long_window, min_periods=1)
		
		return mavgs
	
	#	Define Relative Strength Index(RSI)
	def RSI(self):
		'''Wilder's RSI is calculated by the following formula:
			RSI = 100 - (100 / (1 + rs)) where rs = average gain / average loss and
			average gain = (previous average gain * (period - 1) + current gain) / period
			average loss = (previous average loss * (period - 1) + current loss) / period
		'''	

		# Calculate Wilders RSI
		deltas = bars.Close.diff()
		seed = deltas[:self.rsi_per + 1]
		up = seed[seed >= 0].sum()/self.rsi_per
		down = -seed[seed <= 0].sum()/self.rsi_per
		rs = up/down
		rsi = np.zeros_like(bars.Close)
		rsi[:self.rsi_per] = 100. - 100./(1. + rs)
		for i in range(self.rsi_per, len(bars.Close)):
			delta = deltas[i-1]
			if delta > 0:
				upval = delta
				downval = 0.
			else:
				upval = 0.
				downval = -delta
			up = (up*(self.rsi_per-1)+upval)/self.rsi_per
			down = (down*(self.rsi_per-1)+downval)/self.rsi_per
			rs = up/down
			rsi[i]=100. - 100./(1.+rs)
			
		return rsi
		
	def MACD(self):
	  # Moving Average Convergence Divergence is a signal produced from the difference of two moving averages
	  # The signal oscillates above and below 0.0 as the moving averages converge and diverge
		macd = pd.DataFrame(index=bars.index)
		mavgs = self.ema
		macd['macd'] = mavgs.short_mavg - mavgs.long_mavg
		macd['signal'] = pd.ewma(macd.macd, span=self.macd_per)
		
		return macd
		
	def generate_analysis(self):
		ema = self.EMA()
		rsi = self.RSI()
		macd = self.MACD()
		
		return ema, rsi, macd
		
class MovingCrossRSIMACD(Strategy):
	"""
	Requires:
	symbol - A stock symbol on which to form a strategy on.
	bars - A DataFrame of bars for the above symbol.
	short_window - Lookback period for short moving average.
	long_window - Lookback period for long moving average."""
	
	def __init__(self, symbol, bars, short_window, long_window, ema, rsi, macd):
		self.symbol = symbol
		self.bars = bars
		self.short_window = short_window
		self.long_window = long_window
		self.ema = ema
		self.rsi = rsi
		self.macd = macd
	
	def generate_signals(self):
		''Returns the DataFrame of symbols containing the signals
		to go long, short or hold (1, -1 or 0).''
	
		signals = pd.DataFrame(index=self.bars.index)
		signals['signal'] = 0.0 
		signals['mavg_signal'] = 0.0
		signals['rsi_signal'] = 0.0
		signals['macd_signal'] = 0.0
		signals['positions'] = 0.0
		
		# Create a 'signal' (invested or not invested) when the short moving average crosses the long, 
		# rsi is above or below 70,30 and macd signal crosses 0
		signals.mavg_signal[self.short_window:] = np.where(self.ema.short_mavg[self.short_window:] > self.ema.long_mavg[self.short_window:], 1.0, -1.0)
		signals.rsi_signal[self.rsi > 70] = -1.0
		signals.rsi_signal[self.rsi < 30] = 1.0
		signals.macd_signal[self.macd.signal < 0] = -1.0
		signals.macd_signal[self.macd.signal > 0] = 1.0
		
		# Process Buy signals and closing of open long positions
		signals.signal[(signals.mavg_signal > 0) & (signals.rsi_signal > 0)] =  1.0
		signals.positions = signals.signal.cumsum()
		signals.signal[(signals.positions > 1.0) & (signals.mavg_signal > 0) & (signals.rsi_signal > 0)] = 0.0
		signals.positions = signals.signal.cumsum()
		signals.signal[(signals.positions > 0) & (signals.macd_signal.diff() == -2.0)] = -1.0
		signals.positions = signals.signal.cumsum()
		
		#Process Sell signals ans closing of open short positions
		signals.signal[(signals.mavg_signal < 0) & (signals.rsi_signal < 0)] = -1.0
		signals.positions = signals.signal.cumsum()
		signals.signal[(signals.positions < -1.0) & (signals.mavg_signal < 0) & (signals.rsi_signal < 0)] = 0.0
		signals.positions = signals.signal.cumsum()
		signals.signal[(signals.positions < 0) & (signals.macd_signal.diff() == 2.0)] = 1.0	
		signals.positions = signals.signal.cumsum()

		return signals

class MarketOnClosePortfolio(Portfolio):
	'''A portfolio of positions based
	on a set of signals as provided by a Strategy.
	
	Requires:
	symbol - A stock symbol which forms the basis of the portfolio.
	bars - A DataFrame of bars for a symbol set.
	signals - A DataFrame of signals (1, 0, -1) for each symbol.
	initial_capital - The amount in cash at the start of the portfolio."""
	
	''' __init__(self, symbol, bars, signals, initial_capital=10000.0):
		self.symbol = symbol
		self.bars = bars
		self.signals = signals
		self.initial_capital = float(initial_capital)
		self.positions = self.generate_positions()'''
		
	def generate_positions(self):
		positions = pd.DataFrame(index=signals.index).fillna(0.0)
		positions[self.symbol] = self.signals.positions*50
		
		return positions        
		
	def backtest_portfolio(self):
		portfolio = self.positions.mul(self.bars.Close, axis=0)
		pos_diff = self.positions.diff()
		portfolio['holdings'] = self.positions.mul(bars.Close, axis=0)
		portfolio['cash'] = self.initial_capital - pos_diff.mul(self.bars.Close, axis=0).sum(axis=1).cumsum()
		portfolio['total'] = portfolio.cash + portfolio.holdings
		portfolio['returns'] = portfolio.total.pct_change()
		        
		return portfolio
		
if __name__ == "__main__":
	# Prompt for the input of a symbol and the short and long windows
	print("Enter a filename:")
	filename = input()
	print("Enter a symbol:")
	symbol = input()
	symbol.upper()
	print("You entered: " + symbol)
	print("Enter the period for the short window: ")
	short_window = input()
	short_window = int(short_window)
	print("Enter the period for the long window: ")
	long_window = input()
	long_window = int(long_window)
	
	# Obtain bars of symbol from the saved file
	bars = pd.read_csv(filename, header=None, index_col=False, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
	bars['Date'] = bars['Date'].map(lambda v: datetime.datetime.fromtimestamp(v) if v < 25000 else datetime.datetime.fromtimestamp(v))
	#Convert date from numpy Datetime64 format to float days format and then to a list of labels for the x axis
	Dates = [md.date2num(t) for t in bars.Date]
	bars['Dates'] = Dates
	days = np.unique(np.floor(bars['Dates']), return_index=True)
	iso_days= []
	for n in np.arange(len(days[0])):
		iso_days.append(datetime.date.isoformat(md.num2date(days[0][n])))
		
	# Calculate technical analyses of symbol
	technicals = TechnicalAnalysis(symbol, bars, short_window, long_window)
	ema, rsi, macd = technicals.generate_analysis()

	# Create a Strategy instance from technicals and input windows
	mac = MovingCrossRSIMACD(symbol, bars, short_window, long_window, ema, rsi, macd)
	signals = mac.generate_signals()
	
	# Create a portfolio of symbol, with $10,000 initial capital. 
	portfolio = MarketOnClosePortfolio(symbol, bars, signals)
	returns = portfolio.backtest_portfolio()
	
	# Create and initial format subplots. 
	fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True)
	fig.patch.set_facecolor('white')
	for i, ax in enumerate(fig.axes):
		ax.grid(True)
		ax.yaxis.set_major_locator(mt.MaxNLocator(5, prune='both'))
	ax1.set_ylabel('Price in $')
	ax1.set_xticks(days[1])
	
	# Plot minute price data with moving averages
	ax1.plot(bars.index, bars.Close, color='r', lw=2.) #line graph of bars.Close
	sma_line, = ax1.plot(bars.index, ema.short_mavg, 'b', lw=2.)
	lma_line, = ax1.plot(bars.index, ema.long_mavg, 'g', lw=2.)
	
	# Plot the buy and sell trades against symbol
	buy_signals, = ax1.plot(signals.ix[signals.signal == 1.0].index, bars.Close[signals.signal == 1.0], '^', markersize=10, color='m')
	sell_signals, = ax1.plot(signals.ix[signals.signal == -1.0].index, bars.Close[signals.signal == -1.0], 'v', markersize=10, color='b')

	# Plot the RSI
	rsi_line, = ax2.plot(bars.index, rsi, color='y')
	ax2.set_ylim(0, 100)
	ax2.set_ylabel('RSI')
	ax2.set_yticks([40, 60])
	ax2.axhline(70, color='black')
	ax2.axhline(30, color='black')
	
	# Plot the MACD for the short and long window
	macd_line, = ax3.plot(bars.index, macd.macd, 'b', lw=2.)
	macd_signal, = ax3.plot(bars.index, macd.signal, 'r', lw=2.)
	ax3.fill_between(bars.index, 0, macd.macd - macd.signal, facecolor='green')
	ax3.set_ylabel('MACD')
	
	# Plot the equity curve in dollars
	ax4.set_ylabel('Portfolio value in $')
	returns_line, = ax4.plot(bars.index, returns.total, lw=2.)
	ax4.set_xticklabels(iso_days, rotation=45, horizontalalignment='right')
	
	# Plot the "buy" and "sell" trades against the equity curve
	buy_returns, = ax4.plot(returns.ix[signals.signal == 1.0].index, returns.total[signals.signal == 1.0], '^', markersize=10, color='m')
	sell_returns, = ax4.plot(returns.ix[signals.signal == -1.0].index, returns.total[signals.signal == -1.0], 'v', markersize=10, color='b')
	#ax4.plot(returns.ix[signals.positions == 2.0].index, returns.total[signals.positions == 2.0], '^', markersize=10, color='m')
	#ax4.plot(returns.ix[signals.positions == -2.0].index, returns.total[signals.positions == -2.0], 'v', markersize=10, color='b')'''
	
	# Create sliders
	slider_color = 'lightgoldenrodyellow'
	axsma = plt.axes([0.2, 0.13, 0.6, 0.03], axisbg=slider_color)
	axlma = plt.axes([0.2, 0.1, 0.6, 0.03], axisbg=slider_color)
	axrsi = plt.axes([0.2, 0.07, 0.6, 0.03], axisbg=slider_color)
	axmacd = plt.axes([0.2, 0.04, 0.6, 0.03], axisbg=slider_color)
	
	ssma = mw.Slider(axsma, 'Short Moving Average Period', 1, 390, valinit=short_window)
	slma = mw.Slider(axlma, 'Long Moving Average Period', 1, 390, valinit=long_window)
	srsi = mw.Slider(axrsi, 'RSI Period', 1, 390, valinit=100)
	smacd = mw.Slider(axmacd, 'MACD Signal Period', 1, 390, valinit=50)
	
	def update(val):
		sma_val = int(round(ssma.val))
		lma_val = int(round(slma.val))
		rsi_val = int(round(srsi.val))
		macd_val = int(round(smacd.val))
		technicals.short_window = sma_val
		technicals.long_window = lma_val
		technicals.rsi_per = rsi_val
		technicals.macd_per = macd_val
		new_ema, new_rsi, new_macd = technicals.generate_analysis()
		sma_line.set_ydata(new_ema.short_mavg)
		lma_line.set_ydata(new_ema.long_mavg)
		rsi_line.set_ydata(new_rsi)
		mac.rsi = new_rsi
		mac.macd = new_macd
		signals = mac.generate_signals()
		new_portfolio = MarketOnClosePortfolio(symbol, bars, signals)
		print(new_portfolio.generate_positions()[740:760])
		new_returns = new_portfolio.backtest_portfolio()
		for coll in (ax3.collections):
			ax3.collections.remove(coll)
		ax3.fill_between(bars.index, 0, new_macd.macd - new_macd.signal, facecolor='green')	
		macd_signal.set_ydata(new_macd.signal)
		returns_line.set_ydata(new_returns.total)
		buy_signals.set_data(signals.ix[signals.signal == 1.0].index, bars.Close[signals.signal == 1.0])
		sell_signals.set_data(signals.ix[signals.signal == -1.0].index, bars.Close[signals.signal == -1.0])
		buy_returns.set_data(new_returns.ix[signals.signal == 1.0].index, new_returns.total[signals.signal == 1.0])
		sell_returns.set_data(new_returns.ix[signals.signal == -1.0].index, new_returns.total[signals.signal == -1.0])
		plt.draw()
	
	ssma.on_changed(update)
	slma.on_changed(update)	
	srsi.on_changed(update)
	smacd.on_changed(update)
	
	# Plot the figure
	fig.subplots_adjust(hspace=0, bottom=0.25)
	plt.show()
	fig.savefig(r"C:/users/gph/desktop/tradingalgorithm/{}_{}EMA_cross_{}ewmaRSI_backtest.png".format(short_window, long_window, technicals.rsi_per))
	
	# Calculate final dataframe values based on slider locations
	ema, rsi, macd = technicals.generate_analysis()
	signals = mac.generate_signals()
	portfolio = MarketOnClosePortfolio(symbol, bars, signals)
	returns = portfolio.backtest_portfolio()
	
	#Save dataframes to excel file for backchecking and debugging.
	writer = ExcelWriter("complex_model.xlsx")
	returns.to_excel(writer, 'Sheet1')
	signals.to_excel(writer, 'Sheet2')
	bars.to_excel(writer, 'Sheet3')
	writer.save()
