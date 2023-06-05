from binance.client import Client
import pandas as pd 
import numpy as np
import config
import pprint

client = Client(config.TEST_FUTURES_API_KEY, config.TEST_FUTURES_API_SECRET, testnet=True)
pprint.pprint(client.futures_account_balance())
client.futures_position_information(symbol = 'BTCUSDT')
client.futures_change_leverage(symbol = 'BTCUSDT', leverage = 2)
client.futures_change_margin_type(symbol = 'BTCUSDT', marginType = 'ISOLATED')
client.futures_change_margin_type(symbol = 'BTCUSDT', marginType = 'CROSSED')

#Position mode
client.futures_get_position_mode()
client.futures_change_position_mode(dualSidePoition = True)


leverage = 10
size = 0.01

client.futures_change_leverage(symbol = "BTCUSDT", leverage = leverage)


#Long Orders
order_open = client.futures_create_order(symbol = "BTCUSDT", side = "BUY",
                                         type = "MARKET", quantity = size)
order_open
client.futures_get_order(symbol = "BTCUSDT", orderId = order_open["orderId"]) # check order status


order_close = client.futures_create_order(symbol = "BTCUSDT", side = "SELL",
                                          type = "MARKET", quantity = size, reduce_Only = True)
order_close

#Go Short
order_open = client.futures_create_order(symbol = "BTCUSDT", side = "SELL",
                                         type = "MARKET", quantity = size)
order_open

order_close = client.futures_create_order(symbol = "BTCUSDT", side = "BUY",
                                          type = "MARKET", quantity = size, reduceOnly = True)
order_close