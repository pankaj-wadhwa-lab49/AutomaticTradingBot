import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
plt.style.use("seaborn")

start = '2022-01-01'
end = '2023-05-25'

symbol = 'BTC-USD'
df = yf.download(symbol, start, end)
print(df)
df.Close.dropna().plot(figsize= (15,8), fontsize=13)
plt.legend(fontsize=13)
plt.show()
# df.to_csv("example.csv")

# Returns
p0 = 100
p1 = 110
levarage = 2
margin = p0/2

#Simple Returns
unlev_return = (p1 - p0)/p0

lev_return = (p1 - p0)/margin

# lev_return == unlev_return * levarage
# Above is true for simple returns