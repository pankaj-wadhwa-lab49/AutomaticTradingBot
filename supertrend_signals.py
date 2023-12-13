from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import config
from common import Send_Telegram_Message
import pandas_ta as ta

lastRunningSignal = 0

def main():
    get_most_recent(symbol = symbol, interval= interval, days = historical_days)
    twm.start()
    twm.start_kline_socket(callback=handle_kline_message,
                           symbol=symbol, interval=interval)
    twm.join()


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
    define_strategy()
    # checkStopLossAndTakeProfit(close=close)

    if complete == True:
        # feed df (add new bar / update latest bar)
        print("completed")
        new_row_dict = {'Date': [start_time],'Open': [open], 'High': [high], 'Low': [low], "Close": [close], "Volume": [volume], "Complete": [complete]}
        newDf = pd.DataFrame(new_row_dict)
        newDf["Date"] = pd.to_datetime(newDf.iloc[:,0], unit = "ms")
        newDf.set_index('Date', inplace = True)
        df = pd.concat([df, newDf])
        define_strategy()
        sendSignal()

    
def define_strategy():   
    #******************** define your strategy here ************************
    global df
    atrPeriod = 9
    multiplier = 3.9 # keep precision 1 always
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=atrPeriod, multiplier=multiplier)
    positionName = f'SUPERTd_{atrPeriod}_{multiplier}' #sample SUPERTd_7_3.0
    df["position"] = sti[positionName]
    df.to_csv('df.csv')
    # sti.to_csv('sti.csv')
    # print(df)

def sendSignal(): # Adj! 
    global lastRunningSignal

    if lastRunningSignal != df["position"].iloc[-1]:
        lastRunningSignal = df["position"].iloc[-1]
        signal = 'BUY Signal' if df["position"].iloc[-1] == 1 else 'SELL Signal'
        msg = symbol + ": " + signal
        Send_Telegram_Message(msg)

        
if __name__ == "__main__":

    # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    start = '2023-06-29'
    symbol = 'APTUSDT' 
    interval = "5m"
    leverage = 2
    historical_days = 18/24
    position = 0 # position has to be 0 by default

    # Binance API Keys
    api_key = config.API_KEY
    api_secret = config.API_SECRET

    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "Complete"])
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret= api_secret)

    client = Client(api_key, api_secret, testnet=False)
    client.futures_change_leverage(symbol = symbol, leverage = leverage)

    print("Using Binance Server")
    main()

# Use this with the icho cloud & heikin ashi candles to help take better trades


