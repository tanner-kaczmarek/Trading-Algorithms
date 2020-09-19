import pandas as pd
import math
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import time

api_key = '1111111111'
period = 60

#gets the closing price for a given stock as well as its SMA
ts = TimeSeries(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format= 'pandas')
data, meta_data = ts.get_intraday(symbol='DIS', interval='1min', outputsize='full')
data_sma, meta_data_sma = ti.get_sma(symbol='DIS', interval='1min', time_period=period, series_type='close')

#df3 is now the percent difference from the SMA to the closing price for a given time.
df1 = data['4. close'].iloc[period-1::]
df2 =data_sma['SMA']
df2.index = df1.index
df3 = df1.subtract(df2, fill_value=0)
df4 = df1.add(df2, fill_value=0)
df5 = df4.divide(2, fill_value=0)
df4 = df3.divide(df5, fill_value=0)
df3 = df4.multiply(100, fill_value=0)

#buy and sell algorithm to test money on previous data
def buy(M, S, P, canI):
    if canI == True:
        temp = M/P
        S = math.floor(temp)
        M = M - (S*P)
        canI = False
    return M, S, canI

def sell(M, S, P, canI):
    if canI == False:
        temp = S * P
        S = 0
        M = M + temp
        canI = True
    return M, S, canI

money = 10000
stocks = 0
BuyTime = True
x = 0

#Logic goes is that that the closing price will return back to its moving average
#If the SMA is greater than -4.5% and if sold last then it should buy.
#If the SMA is greater than 4.5% and if bought last then it should sell.
while(x<len(df3)):
    if(df3[x] < -4.5):
        money, stocks, BuyTime = buy(money, stocks, df1[x], BuyTime)
    if(df3[x] > 4.5):
        money, stocks, BuyTime = sell(money, stocks, df1[x], BuyTime)
    x += 1

#checks to see how much money you made
endMoney = money + (stocks * df1[x-1])
print(endMoney)
print(x)

total_df = pd.concat([df1,df2,df3], axis=1)
print(total_df)
