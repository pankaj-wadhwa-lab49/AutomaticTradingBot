from binance import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("seaborn")

API_KEY = 'SmiueFRK96fmzsl8g96w0oOyAXvNWUkOqFcu44LrMnLaP9Y3iXWruTmqaGTjhpzX'
API_SECRET = 'ulBMKQagTFgRpwhlm9VH1EIWloEW7UNa4ihfBw7bNv0dO37oAzrtrTTmcJZs8kcv'

TEST_API_KEY = '0nvVXH5b91pcVPhO49AmsSuLllofEruVz91KxEgzPek7tBvR9G6KVlyjgyeXkhRJ'
TEST_API_SECRET = 'Kf0sFTslvmdnpGu4x71BbhTV86Y6eDi2xH5RftwC3rYvD4jnAFHzNyEvdzCIyMYJ'

SYMBOL = 'BTCUSDT'
start = '2023-05-20'
end = '2023-05-25'

client = Client(API_KEY, API_SECRET)


def get_minute_data(symbol, interval):
    # frame = pd.DataFrame(client.get_historical_klines(symbol, interval, look_back + ' min ago UTC'))
    frame = pd.DataFrame(client.get_historical_klines(symbol=symbol, interval=interval, start_str=start, end_str=end))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


# df = get_minute_data(symbol=SYMBOL, interval='1h')
# df.Close.dropna().plot(figsize= (12,8), title=SYMBOL, fontsize=12)
# plt.legend(fontsize=13)
# plt.show()


# Momementum and contrarium strategy
# data = df[["Close", "Volume"]].copy()
# data["returns"] = np.log(data.Close.div(data.Close.shift(1)))
# data["creturns"] = data.returns.cumsum().apply(np.exp) # Normalized Prices with Base Value 1

# data["vol_ch"] = np.log(data.Volume.div(data.Volume.shift(1)))

# data.loc[data.vol_ch > 3, "vol_ch"] = np.nan
# data.loc[data.vol_ch < -3, "vol_ch"] = np.nan

# print(data)

# data.vol_ch.plot(kind = "hist", bins = 100, figsize = (12,8))
# plt.show()