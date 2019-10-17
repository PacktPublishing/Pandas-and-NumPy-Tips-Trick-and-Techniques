import numpy as np
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import datetime as dt

class Analyze:
    # sets default to 1 year lookback plus 1-month + 2 days days to account for trimming
    default_date = dt.date.isoformat(dt.date.today() - dt.timedelta(397))
    
    def get_data(symbol,date=default_date):
        data = pdr.get_data_yahoo(symbol, start=date)
        return data

    # adds volatility related columns to df
    def calc_vol(df, n=21):
        """
        calculate rolling window volatility
        (STD), and add related columns. Default is 21 day.
        """
        df['Return'] = np.log(df.Close).diff()
        df['Volatility'] = df['Return'].rolling(n).std()
        df['Change'] = df['Close'].diff()
        df['Exp_Change'] = (df['Volatility'] * df['Close']).shift(1)
        df['Magnitude'] = df['Change'] / df['Exp_Change']
        df['Abs_Magnitude'] = np.abs(df.Magnitude)
        
        return df.iloc[n+1:]
    
    # adds 2 user specifed moving average lengths        
    def moving_avg(df, fast=21, slow=63):
        df[str(fast) +'_day'] = df.Close.rolling(fast).mean()
        df[str(slow) + '_day'] = df.Close.rolling(slow).mean()
        
    # adds column that measurements intraday volatility
    def high_low(df):
        df['High_Low_Spread'] = (df['High'] - df['Low']) /df['Close']
    
    # returns subset of data from options expiration Fridays
    def exp_friday(df):
        mask = np.where((df.index.day > 14) & 
                        (df.index.day < 22) & 
                        (df.index.dayofweek == 4), True, False)
        return df[mask]
    # keeps running count of last + 2 sd move
    def low_vol_duration(df):
        pd.set_option('mode.chained_assignment', None)
        df['Days<2sd'] = 0
        count = 0
        for row in range(len(df)):
           
            if df['Magnitude'].iloc[row] < 2:
                count += 1
                df['Days<2sd'].iloc[row] = count
            else:    
                df['Days<2sd'].iloc[row] = count
                count = 0
        return df[df.Magnitude >=2]
    
    # visualize analysis
    def plot_magnitude(df):
        plt.scatter(df['Return'], df['Abs_Magnitude'], alpha=0.6)
        plt.grid(True)
        
    def plot_MA(df):
        plt.plot(df['Close'])
        plt.plot(df.filter(regex='day'))
        plt.grid(True)
        
    def mag_hist(df):
        plt.hist(df['Magnitude'], bins=20, color='g', edgecolor='w')
        
         
        
