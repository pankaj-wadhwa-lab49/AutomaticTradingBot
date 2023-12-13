from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta
import config

def main():
    get_most_recent(symbol = symbol, interval= interval, days = historical_days)
    define_macd_ema_strategy()

    buy_sell_list = df['position'].tolist()
    for index, row in enumerate(buy_sell_list):
        execute_trades(index= index)


def get_most_recent(symbol, interval, days):
    global df    
    # now = datetime.utcnow()       
    # past = str(now - timedelta(days = days))
    
    bars = client.futures_historical_klines(symbol = symbol, interval = interval,
                                            start_str = start, end_str = None, limit = 1000) # Adj: futures_historical_klines
    df = pd.DataFrame(bars)
    df["Date"] = pd.to_datetime(df.iloc[:,0], unit = "ms")
    df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume",
                      "Clos Time", "Quote Asset Volume", "Number of Trades",
                      "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore", "Date"]
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    df.set_index("Date", inplace = True)
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors = "coerce")
    df["Complete"] = [True for row in range(len(df)-1)] + [False]
    df.drop(df.tail(1).index,inplace=True)

def define_strategy():
                
    #******************** define your strategy here ************************
    global df
    df["SMA_S"] = df['Close'].ewm(span=sma_s, adjust=False).mean() #ta.trend.ema_indicator(df['Close'], window=sma_s) #df.Close.rolling(window = sma_s).mean()
    df["SMA_M"] = df['Close'].ewm(span=sma_m, adjust=False).mean() #ta.trend.ema_indicator(df['Close'], window=sma_m) #df.Close.rolling(window = sma_m).mean()
    df["SMA_L"] = df['Close'].ewm(span=sma_l, adjust=False).mean() #ta.trend.ema_indicator(df['Close'], window=sma_l) #df.Close.rolling(window = sma_l).mean()
        
    # df.dropna(inplace = True)
                
    cond1 = (df.SMA_S > df.SMA_M) & (df.SMA_M > df.SMA_L)# & (df.Open > df.SMA_S) & (df.Open > df.SMA_M) & (df.Open > df.SMA_L)
    cond2 = (df.SMA_S < df.SMA_M) & (df.SMA_M < df.SMA_L)# & (df.Open < df.SMA_S) & (df.Open < df.SMA_M) & (df.Open < df.SMA_L)
        
    df["position"] = 0
    df.loc[cond1, "position"] = 1
    df.loc[cond2, "position"] = -1
    print(df)
    df.to_csv('hist data.csv')

def define_macd_ema_strategy():
                
    #******************** define your strategy here ************************
    global df
    df["SMA_S"] = df['Close'].ewm(span=sma_s, adjust=False).mean() #ta.ema(df.Close, sma_s) #ta.trend.ema_indicator(df.Close, window=sma_s) #df.Close.rolling(window = sma_s).mean()
    df["SMA_M"] = df['Close'].ewm(span=sma_m, adjust=False).mean() #ta.ema(df.Close, sma_m) #ta.trend.ema_indicator(df.Close, window=sma_m) #df.Close.rolling(window = sma_m).mean()
    df["SMA_L"] = df['Close'].ewm(span=sma_l, adjust=False).mean()

    # calculate MACD  using short and long EMA mostly using close values 
    shortEMA = df['Close'].ewm(span=12, adjust=False).mean()
    longEMA = df['Close'].ewm(span=26, adjust=False).mean()
    
    # Calculate MACD and signal line
    MACD = shortEMA - longEMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    df['MACD'] = MACD
        
                
    cond1 = (df.SMA_S > df.SMA_M) & (df.MACD > 0) & (df.SMA_M > df.SMA_L)  # & (df.Open > df.SMA_S) & (df.Open > df.SMA_M) & (df.Open > df.SMA_L)
    cond2 = (df.SMA_S < df.SMA_M) & (df.MACD < 0) & (df.SMA_M < df.SMA_L) # & (df.Open < df.SMA_S) & (df.Open < df.SMA_M) & (df.Open < df.SMA_L)
        
    df["position"] = 0
    df.loc[cond1, "position"] = 1
    df.loc[cond2, "position"] = -1
    print(df)

def execute_trades(index): # Adj! 
    global df, units
    global BuyPrice, SellPrice, position
    if df["position"][index] == 1: #and df["Open"][index] > df["SMA_S"][index]: # if position is long -> go/stay long
        if position == 0:
            BuyPrice = df["Close"][index]
            outputDF.loc[len(outputDF.index)] = [df.index[index],df["SMA_S"][index], df["SMA_M"][index], df["SMA_L"][index], BuyPrice, 0, leverage, 'Buy Long']
        elif position == -1:
            BuyPrice = df["Close"][index]
            outputDF.loc[len(outputDF.index)] = [df.index[index], df["SMA_S"][index], df["SMA_M"][index], df["SMA_L"][index], BuyPrice, 0, leverage, 'Buy Long from Short']
        position = 1
    elif df["position"][index] == 0: # if position is neutral -> go/stay neutral
        if position == 1:
            SellPrice = df["Close"][index]
            outputDF.loc[len(outputDF.index)] = [df.index[index], df["SMA_S"][index], df["SMA_M"][index], df["SMA_L"][index], 0, SellPrice, leverage, 'Sell Long Neutral']
        elif position == -1:
            BuyPrice = df["Close"][index]
            outputDF.loc[len(outputDF.index)] = [df.index[index], df["SMA_S"][index], df["SMA_M"][index], df["SMA_L"][index], BuyPrice, 0, leverage, 'Buy Short Neutral']
        position = 0
    if df["position"][index] == -1: #and df["Open"][index] < df["SMA_S"][index]: # if position is short -> go/stay short
        if position == 0:
            SellPrice = df["Close"][index]
            outputDF.loc[len(outputDF.index)] = [df.index[index], df["SMA_S"][index], df["SMA_M"][index], df["SMA_L"][index], 0, SellPrice, leverage, 'Sell Short']
        elif position == 1:
            SellPrice = df["Close"][index]
            outputDF.loc[len(outputDF.index)] = [df.index[index], df["SMA_S"][index], df["SMA_M"][index], df["SMA_L"][index], 0, SellPrice, leverage,'Sell Short from Long']
        position = -1
    outputDF.to_csv(f'{symbol} {sma_s} {sma_m} {sma_l} sma profit.csv')

outputDF = pd.DataFrame(columns=['date', 'MA S', 'MA M', 'MA L', 'buy', 'sell', 'leverage', 'position'])
        
if __name__ == "__main__":

    sma_s = 9
    sma_m = 21
    sma_l = 200

    # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    symbol = 'APTUSDT' 
    interval = "5m"
    start = '2023-06-17'
    leverage = 1
    historical_days = 18/24
    position = 0
    units = 1
   

    api_key = config.API_KEY
    api_secret = config.API_SECRET

    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "Complete"])
    # twm = ThreadedWebsocketManager(api_key=api_key, api_secret= api_secret)

    client = Client(api_key, api_secret, testnet=False)
    # client.futures_change_leverage(symbol = symbol, leverage = leverage)
    print("Using Binance Server")
    
    main()

# Use this with the icho cloud & heikin ashi candles to help take better trades