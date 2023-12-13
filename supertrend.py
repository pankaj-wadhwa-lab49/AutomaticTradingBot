from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import time
import config
import math
from common import Send_Telegram_Message
import pandas_ta as ta

BuyPrice = 0
SellPrice = 0
LastBuyDF = pd.DataFrame(columns=['time', 'buyPrice', 'sellPrice', 'position'])
stopLoss_takeProfit_triggered = False

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
        execute_trades()

def checkStopLossAndTakeProfit(close):
    global stopLoss_takeProfit_triggered, position
    if len(LastBuyDF) == 0:
        return

    positionPrice = LastBuyDF.iloc[-1]['buyPrice'] if position == 1 else (LastBuyDF.iloc[-1]['sellPrice'] if position == -1 else '0')
    positionPrice = float(positionPrice)
    if position == 1:
        stopLossPrice = positionPrice - (stopLossPercentage/100)*positionPrice
        takeProfitPrice = positionPrice + (takeProfitPercentage/100)*positionPrice
        if close < stopLossPrice or close > takeProfitPrice:
            print('long ',positionPrice)
            createOrder(symbol = symbol, side = "SELL", type = "MARKET", quantity = units, positionMessage = "GOING NEUTRAL")
            position = 0
            stopLoss_takeProfit_triggered = True
    elif position == -1:
        stopLossPrice = positionPrice + (stopLossPercentage/100)*positionPrice
        takeProfitPrice = positionPrice - (takeProfitPercentage/100)*positionPrice
        if close > stopLossPrice  or close < takeProfitPrice:
            print('short ',positionPrice)
            createOrder(symbol = symbol, side = "BUY", type = "MARKET", quantity = units, positionMessage = "GOING NEUTRAL")
            position = 0
            stopLoss_takeProfit_triggered = True
        


def define_strategy():   
    #******************** define your strategy here ************************
    global df
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=14, multiplier=3)
    df["position"] = sti['SUPERTd_14_3.0']
    df.to_csv('df.csv')
    # sti.to_csv('sti.csv')
    # print(df)

def execute_trades(): # Adj! 
    global df, units
    global BuyPrice, SellPrice, position
    global stopLoss_takeProfit_triggered

    if checkIfOpenPosition() == False and position != 0:
        position = 0

    if df["position"].iloc[-1] == 1: # if position is long -> go/stay long
        if position == 0:
            createOrder(symbol = symbol, side = "BUY", type = "MARKET", quantity = units, positionMessage= "GOING LONG")
        elif position == -1:
            createOrder(symbol = symbol, side = "BUY", type = "MARKET", quantity = 2 * units, positionMessage = "GOING LONG")
        position = 1
    if df["position"].iloc[-1] == -1: # if position is short -> go/stay short
        if position == 0:
            createOrder(symbol = symbol, side = "SELL", type = "MARKET", quantity = units, positionMessage="GOING SHORT")
        elif position == 1:
            createOrder(symbol = symbol, side = "SELL", type = "MARKET", quantity = 2 * units, positionMessage = "GOING SHORT")
        position = -1
    # outputDF.to_csv(f'{symbol} {sma_s} {sma_m} {sma_l} sma profit.csv')

def createOrder(symbol, side, type, quantity, positionMessage):
    global LastBuyDF
    if testNet == False:
        order = client.futures_create_order(symbol = symbol, side = side, type = type, quantity = quantity)
        print(order)
        orderDetail = client.futures_get_order(symbol = symbol, orderId = order["orderId"])
        print(orderDetail)
        str1 = "Quantity = {} | Price = {} | Position = {} \n".format(quantity, orderDetail['avgPrice'], positionMessage)
        Send_Telegram_Message(message=str1)
        createTrailingStopLossOrder(
            symbol=symbol,
            side=side
        )
        if orderDetail['status'] == 'FILLED':
            if df["position"].iloc[-1] == 1 and position == 0:
                LastBuyDF.loc[len(LastBuyDF.index)] = [orderDetail['time'], orderDetail['avgPrice'], '0', df["position"].iloc[-1]]
            elif df["position"].iloc[-1] == -1 and position == 0:
                LastBuyDF.loc[len(LastBuyDF.index)] = [orderDetail['time'], '0', orderDetail['avgPrice'], df["position"].iloc[-1]]
            # LastBuyDF.to_csv('LastBuyList.csv')
        report_trade(order, positionMessage)

def createTrailingStopLossOrder(symbol, side):
    global callbackRatePercent
    newSide = 'SELL' if side == 'BUY' else 'BUY'
    if testNet == False and position != 0:
        order = client.futures_create_order(symbol = symbol, side = newSide, type = 'TRAILING_STOP_MARKET', quantity = units, callbackRate = callbackRatePercent)
        print('trailing stop loss order', order)

def checkIfOpenPosition():
    positions = client.futures_position_information(symbol = symbol) 
    return len(positions) > 0

    
def report_trade(order, going): # Adj!
        global cum_profits
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
        # outputDF.to_csv(f'{symbol} profit.csv')
        # print trade report
        print(2 * "\n" + 100* "-")
        str1 = "{} | {}\n".format(order_time, going)
        str2 = "Base_Units = {} | Quote_Units = {} | Price = {} \n".format(base_units, quote_units, price)
        str3 = "Profit = {} | CumProfits = {} ".format(real_profit, cum_profits)
        print(str1) 
        print(str2)
        print(str3)
        Send_Telegram_Message(message= str3)
        print(100 * "-" + "\n")

outputDF = pd.DataFrame(columns=['order time', 'base_units', 'quote_units', 'price', 'real_profit', 'cum_profits'])

def Quantity():
    balances = client.futures_account_balance()
    for check_balance in balances:
        if check_balance["asset"] == "USDT":
            usdt_balance = float(check_balance["balance"])
            currentPrice = float(client.futures_symbol_ticker(symbol=symbol)['price'])
            quantity = math.floor(usdt_balance/currentPrice)
            return quantity
    return 0
        
if __name__ == "__main__":

    # Triple Moving Averages
    sma_s = 9
    sma_m = 21
    sma_l = 100

    # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    start = '2023-06-27'
    symbol = 'APTUSDT' 
    interval = "5m"
    leverage = 2
    historical_days = 18/24
    position = 0 # position has to be 0 by default
    callbackRatePercent = 1 # for trailing stop loss
    
    cum_profits = 0
    
    # Stop Loss and Take Profit percetage
    stopLossPercentage = 1
    takeProfitPercentage = 1.35

    # Testnet configuration
    testNet = False

    # Binance API Keys
    api_key = config.API_KEY
    api_secret = config.API_SECRET

    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "Complete"])
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret= api_secret)

    client = Client(api_key, api_secret, testnet=False)
    client.futures_change_leverage(symbol = symbol, leverage = leverage)
    units = Quantity() * leverage

    print("Using Binance Server")
    print("units", units)
    main()

# Use this with the icho cloud & heikin ashi candles to help take better trades


