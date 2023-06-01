from binance.client import Client
from binance import ThreadedWebsocketManager
import pprint
from time import sleep
import config
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import ta
from enum import Enum
 
class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

############ Variables ###############
TEST_NET = True

kline_closed_values = []
opens, closes, highs,lows, dates, date, time= [],[],[],[],[],[],[]
OrderStatus= OrderSide.BUY
Profit = 0
BuyPrice = 0
outputDF = pd.DataFrame(columns=['buy', 'sell', 'trade_profit', 'total_profit'])

def main():
    twm.start()
    twm.start_kline_socket(callback=handle_kline_message,
                           symbol=symbol, interval='1m')
    twm.join()

def handle_kline_message(candle_msg):
    print('Candle received')
    # pprint.pprint(f"kline message type: {candle_msg['e']}")
    # pprint.pprint(candle_msg)
    kline = candle_msg['k']   # access the key 'k'
    is_kline_closed = kline['x']   # if true, then its end of current kline
    kline_close_value = kline['c']  # last or closing ETH value
    if is_kline_closed:
        # print("kline closed at: {}".format(kline_close_value))
        kline_closed_values.append(float(kline_close_value))
        # print(kline_closed_values)

        df = createDataFrame(kline)

        ## MACD calculations
        macd_trade_logic(df)
        
def createDataFrame(data):
    global closes, opens, highs, lows, date,time
    open_ = data['o']
    close = data['c']
    high = data['h']
    low = data['l']
    date = data['T']

    closes.append(float(close))
    opens.append(float(open_))
    highs.append(float(high))
    lows.append(float(low))
    dates.append(date)

    df = pd.DataFrame(opens,columns=['open'])
    df['close'] = closes
    df['high'] = highs
    df['low'] = lows
    df['date'] = dates

    df= df[['date', 'open', 'close', 'high', 'low']]
        # To print in human readable date and time (from timestamp)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms') # index set to first column = date_and_time
    return df

def macd_trade_logic(symbol_df):
    # calculate short and long EMA mostly using close values
    shortEMA = symbol_df['close'].ewm(span=12, adjust=False).mean()
    longEMA = symbol_df['close'].ewm(span=26, adjust=False).mean()
    
    # Calculate MACD and signal line
    MACD = shortEMA - longEMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    symbol_df['MACD'] = MACD
    symbol_df['signal'] = signal
    symbol_df['MACD_Diff'] = MACD - signal
    # symbol_df['ma_200'] = ta.trend.ema_indicator(symbol_df.Close, window=200)

    symbol_df['Trigger'] = np.where((symbol_df['MACD'] > symbol_df['signal']), 1, 0) # (symbol_df['MACD_Diff'] > 0)
    symbol_df['Position'] = symbol_df['Trigger'].diff()
    
    # Add buy and sell columns
    symbol_df['Buy'] = np.where(symbol_df['Position'] == 1,symbol_df['close'], np.NaN )
    symbol_df['Sell'] = np.where(symbol_df['Position'] == -1,symbol_df['close'], np.NaN )
    print(symbol_df)
    with open('output.txt', 'w') as f:
        f.write(symbol_df.to_string())
    
    # get the column=Position as a list of items.
    buy_sell_list = symbol_df['Position'].tolist()
    buy_or_sell(symbol_df, buy_sell_list)


def buy_or_sell(df, buy_sell_list):
    print('pankaj buy_or_sell')
    global outputDF, OrderStatus, Profit, BuyPrice
    current_price = float(client.get_symbol_ticker(symbol =symbol)['price'])
    
    index = len(buy_sell_list) - 1
    last_element = buy_sell_list[-1]
    if OrderStatus == OrderSide.BUY:
        print('buy current price', current_price)
        if last_element == 1.0:
            print("buy buy buy.... price", current_price)
            BuyPrice = current_price
            OrderStatus = OrderSide.SELL
        else:
             print("looking to buy but nothing to do...")
    elif OrderStatus == OrderSide.SELL:
        print('sell current price', current_price)
        if last_element == -1.0:
            print("sell sell sell.... price", current_price)
            Profit += (current_price - BuyPrice)

            outputDF.loc[len(outputDF.index)] = [BuyPrice, current_price, current_price - BuyPrice, Profit]
            outputDF.to_csv('profit.csv')
            OrderStatus = OrderSide.BUY
        else:
             print("looking to sell but nothing to do...")


if __name__ == "__main__":
    # passkey (saved in bashrc for linux)
    api_key = config.TEST_API_KEY #os.environ.get('BINANCE_TESTNET_KEY')
    # secret (saved in bashrc for linux)
    api_secret = config.TEST_API_SECRET #os.environ.get('BINANCE_TESTNET_PASSWORD')

    twm = ThreadedWebsocketManager()

    client = Client(api_key, api_secret, testnet=True)
    print("Using Binance TestNet Server")
    # pprint.pprint(client.get_account())

    # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    symbol = 'ETHUSDT' 
    main()

