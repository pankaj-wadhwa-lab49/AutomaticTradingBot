from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import config

def main():
    get_most_recent(symbol = symbol, interval= interval, days = historical_days)
    twm.start()
    twm.start_kline_socket(callback=handle_kline_message,
                           symbol=symbol, interval=interval)
    twm.join()


def get_most_recent(symbol, interval, days):
    global df    
    now = datetime.utcnow()       
    past = str(now - timedelta(days = days))
    
    bars = client.futures_historical_klines(symbol = symbol, interval = interval,
                                            start_str = past, end_str = None, limit = 1000) # Adj: futures_historical_klines
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
    print(df)

        
def handle_kline_message(msg):
    print(".", end = "", flush = True)
    global df
    # extract the required items from msg
    event_time = pd.to_datetime(msg["E"], unit = "ms")
    start_time = pd.to_datetime(msg["k"]["t"], unit = "ms")
    open   = float(msg["k"]["o"])
    high    = float(msg["k"]["h"])
    low     = float(msg["k"]["l"])
    close   = float(msg["k"]["c"])
    volume  = float(msg["k"]["v"])
    complete = msg["k"]["x"]

    if complete == True:
        # feed df (add new bar / update latest bar)
        print("completed")
        # print('complete df', df)

        # df.append()
        new_row_dict = {'Date': [start_time],'Open': [open], 'High': [high], 'Low': [low], "Close": [close], "Volume": [volume], "Complete": [complete]}
        newDf = pd.DataFrame(new_row_dict)
        newDf["Date"] = pd.to_datetime(newDf.iloc[:,0], unit = "ms")
        newDf.set_index('Date', inplace = True)
        # df.loc[start_time] = [open, high, low, close, volume, complete]
        df = pd.concat([df, newDf])
        # df = df.append(new_row, ignore_index=False)
        define_strategy()

def define_strategy():
                
    #******************** define your strategy here ************************
    global df
    df["SMA_S"] = df.Close.rolling(window = sma_s).mean()
    df["SMA_M"] = df.Close.rolling(window = sma_m).mean()
    df["SMA_L"] = df.Close.rolling(window = sma_l).mean()
        
    # df.dropna(inplace = True)
                
    cond1 = (df.SMA_S > df.SMA_M) & (df.SMA_M > df.SMA_L) & (df.Open > df.SMA_S) & (df.Open > df.SMA_M) & (df.Open > df.SMA_L)
    cond2 = (df.SMA_S < df.SMA_M) & (df.SMA_M < df.SMA_L) & (df.Open < df.SMA_S) & (df.Open < df.SMA_M) & (df.Open < df.SMA_L)
        
    df["position"] = 0
    df.loc[cond1, "position"] = 1
    df.loc[cond2, "position"] = -1
    print(df)


def execute_trades(self): # Adj! 
    global df, units
    global BuyPrice, SellPrice, position
    if df["position"].iloc[-1] == 1: # if position is long -> go/stay long
        if self.position == 0:
            order = client.futures_create_order(symbol = self.symbol, side = "BUY", type = "MARKET", quantity = units)
            # BuyPrice = float(client.futures_symbol_ticker(symbol= symbol)['price'])
            report_trade(order, "GOING LONG")  
        elif self.position == -1:
            # SellPrice = float(client.futures_symbol_ticker(symbol= symbol)['price'])
            order = client.futures_create_order(symbol = self.symbol, side = "BUY", type = "MARKET", quantity = 2 * units)
            report_trade(order, "GOING LONG")
        position = 1
    elif df["position"].iloc[-1] == 0: # if position is neutral -> go/stay neutral
        if self.position == 1:
            # SellPrice = float(client.futures_symbol_ticker(symbol= symbol)['price'])
            order = client.futures_create_order(symbol = self.symbol, side = "SELL", type = "MARKET", quantity = units)
            report_trade(order, "GOING NEUTRAL") 
        elif self.position == -1:
            # BuyPrice = float(client.futures_symbol_ticker(symbol= symbol)['price'])
            order = client.futures_create_order(symbol = self.symbol, side = "BUY", type = "MARKET", quantity = units)
            report_trade(order, "GOING NEUTRAL")
        position = 0
    if df["position"].iloc[-1] == -1: # if position is short -> go/stay short
        if self.position == 0:
            # BuyPrice = float(client.futures_symbol_ticker(symbol= symbol)['price'])
            order = client.futures_create_order(symbol = self.symbol, side = "SELL", type = "MARKET", quantity = units)
            report_trade(order, "GOING SHORT") 
        elif self.position == 1:
            # SellPrice = float(client.futures_symbol_ticker(symbol= symbol)['price'])
            order = client.futures_create_order(symbol = self.symbol, side = "SELL", type = "MARKET", quantity = 2 * units)
            report_trade(order, "GOING SHORT")
        position = -1
    
def report_trade(order, going): # Adj!
        
        time.sleep(0.1)
        order_time = order["updateTime"]
        trades = client.futures_account_trades(symbol = symbol, startTime = order_time)
        order_time = pd.to_datetime(order_time, unit = "ms")
        
        # extract data from trades object
        dff= pd.DataFrame(trades)
        columns = ["qty", "quoteQty", "commission","realizedPnl"]
        for column in columns:
            dff[column] = pd.to_numeric(dff[column], errors = "coerce")
        base_units = round(dff.qty.sum(), 5)
        quote_units = round(dff.quoteQty.sum(), 5)
        commission = -round(dff.commission.sum(), 5)
        real_profit = round(dff.realizedPnl.sum(), 5)
        price = round(quote_units / base_units, 5)
        
        # calculate cumulative trading profits
        cum_profits += round((commission + real_profit), 5)
        
        outputDF.loc[len(outputDF.index)] = [order_time, base_units, quote_units, price, real_profit, cum_profits]
        outputDF.to_csv(f'{symbol} profit.csv')
        # print trade report
        print(2 * "\n" + 100* "-")
        print("{} | {}".format(order_time, going)) 
        print("{} | Base_Units = {} | Quote_Units = {} | Price = {} ".format(order_time, base_units, quote_units, price))
        print("{} | Profit = {} | CumProfits = {} ".format(order_time, real_profit, cum_profits))
        print(100 * "-" + "\n")

outputDF = pd.DataFrame(columns=['buy', 'sell', 'trade_profit', 'fees', 'leverage', 'position_type', 'total_profit'])
        
if __name__ == "__main__":

    sma_s = 9
    sma_m = 21
    sma_l = 200

    # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    symbol = 'SOLUSDT' 
    interval = "1m"
    leverage = 1
    historical_days = 15/24
    position = 0
    units = 20

    api_key = config.API_KEY
    api_secret = config.API_SECRET

    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "Complete"])
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret= api_secret)

    client = Client(api_key, api_secret, testnet=False)
    client.futures_change_leverage(symbol = symbol, leverage = leverage)
    print("Using Binance TestNet Server")
    
    main()

# Use this with the icho cloud & heikin ashi candles to help take better trades