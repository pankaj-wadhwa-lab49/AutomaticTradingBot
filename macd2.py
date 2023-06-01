from datetime import time

from binance import Client
import config
import pandas as pd
import ta

client = Client(config.API_KEY, config.API_SECRET)
SYMBOL = 'BTCUSDT'
quantity = 1
start = '2023-04-01'
end = '2023-05-25'

def get_minute_data(symbol, interval):
    # frame = pd.DataFrame(client.get_historical_klines(symbol, interval, look_back + ' min ago UTC'))
    frame = pd.DataFrame(client.get_historical_klines(symbol=symbol, interval=interval, start_str=start, end_str=end))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def apply_technical_indicators(df):

    df['macd'] = ta.trend.macd(df.Close)
    df['macd_signal'] = ta.trend.macd_signal(df.Close)
    df['ma_200'] = ta.trend.ema_indicator(df.Close, window=200)
    # Calculate MACD histogram
    df['macd_histogram'] = df['macd'] - df['macd_signal']

# Example usage
# Assuming you have historical price data in a Pandas DataFrame named 'data'
# with 'timestamp', 'open', 'high', 'low', 'close' columns

def tradingStrategy(pair, qty, open_position=False):
    while True:
        df = get_minute_data(pair, '1m')
        apply_technical_indicators(df)
        
        if not open_position:
            if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] and df['macd_histogram'].iloc[-1] < 0 and df['Close'].iloc[-1] > df['ma_200'].iloc[-1]:
                # order = client.create_order(symbol=pair, side='BUY', type='Market', quantity=qty)
                # buy_price = float(order['fills'][0]['price'])
                print("Buy")
                open_position= True
                break

    if open_position:
        while True:
            df = get_minute_data(pair, '1m')
            apply_technical_indicators(df)
            if df['macd'].iloc[-1] < df['macd_signal'].iloc[-1] and df['macd_histogram'].iloc[-1] > 0 and df['Close'].iloc[-1] < df['ma_200'].iloc[-1]:
                # order = client.create_order(symbol=pair, side='SELL', type='Market', quantity=qty)
                # buy_price = float(order['fills'][0]['price'])
                print("sell")
                open_position = False




while True:
    tradingStrategy(SYMBOL, quantity)
    time.sleep(0.5)
