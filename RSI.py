import pandas as pd
import math
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import time

api_key = '1111111111'
period = 30

#get the closing time periods for a given stock as well as its RSI value calculated with a period of 30
ts = TimeSeries(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format= 'pandas')
data, meta_data = ts.get_intraday(symbol='AAPL', interval='1min', outputsize='full')
data_rsi, meta_data_rsi = ti.get_rsi(symbol='AAPL', interval='1min', time_period=period, series_type='close')

df1 = data['4. close'].iloc[period::]
df2 =data_rsi['RSI']
df1.index = df2.index 


#a buy and sell algorithm to test money on previous data
def buy(M, S, P):
    temp = M/P
    S = math.floor(temp)
    M = M - (S*P)
    return M, S

def sell(M, S, P):
    temp = S * P
    S = 0
    M = M + temp
    return M, S

money = 10000
stocks = 0
BuyTime = True
Count = 0
x = 0

#Buys if the RSI calculated value is less than 30 and if sold last
#Sells if the RSI calculated value is greater than 70 and if bought last
while(x<len(df2)):
    if(df2[x] <= 30  and BuyTime):
        money, stocks = buy(money, stocks, df1[x])
        BuyTime = False
        Count += 1
    elif(df2[x] >= 70  and not BuyTime):
        money, stocks = sell(money, stocks, df1[x])
        BuyTime = True
    x += 1

#checks to see how much money you made
endMoney = money + (stocks * df1[x-1])
print(endMoney)
print(x)
print (Count)


total_df = pd.concat([df1,df2], axis=1)
print(total_df)
