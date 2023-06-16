
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


api_key = config.API_KEY #os.environ.get('BINANCE_TESTNET_KEY')
    # secret (saved in bashrc for linux)
api_secret = config.API_SECRET #os.environ.get('BINANCE_TESTNET_PASSWORD')

client = Client(api_key, api_secret, testnet=False)

def get_data_frame():
    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    # request historical candle (or klines) data using timestamp from above, interval either every min, hr, day or month
    # starttime = '30 minutes ago UTC' for last 30 mins time
    # e.g. client.get_historical_klines(symbol='ETHUSDTUSDT', '1m', starttime)
    # starttime = '1 Dec, 2017', '1 Jan, 2018'  for last month of 2017
    # e.g. client.get_historical_klines(symbol='BTCUSDT', '1h', "1 Dec, 2017", "1 Jan, 2018")

    starttime = '2 days ago UTC'
    interval = '5m'
    symbol = 'SOLUSDT'
    bars = client.futures_historical_klines(symbol, interval, starttime)
    for line in bars:        # Keep only first 5 columns, "date" "open" "high" "low" "close"
        del line[5:]
    df = pd.DataFrame(bars, columns=['Date', 'Open', 'High', 'Low', 'Close']) #  2 dimensional tabular data
    df.set_index('Date', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms')
    df.to_csv(f'{symbol}_hist.csv')


get_data_frame()