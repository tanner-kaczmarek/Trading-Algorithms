import pandas as pd
import math
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import time

api_key = '11111111111'
periodS = 20
periodL = 120

#getting the last week closing times, the shorter period moving average calculated using PeriodS values and the longer period moving average calculated using Period L values
ts = TimeSeries(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format= 'pandas')
data, meta_data = ts.get_intraday(symbol='AAPL', interval='1min', outputsize='full')
data_sma, meta_data_sma = ti.get_sma(symbol='AAPL', interval='1min', time_period=periodS, series_type='close')
data_lma, meta_data_lma = ti.get_sma(symbol='AAPL', interval='1min', time_period=periodL, series_type='close')

#lining up the values so they have the same timestamps and are easiest to compare
df1 = data['4. close'].iloc[periodL-1::]
df2 =data_sma['SMA'].iloc[periodL-periodS::]
df3 = data_lma['SMA']
df1.index = df2.index = df3.index


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
Uptrend = False
Cross = False
x = 10

#buys if there is an uptrend, if the sma and the lma cross, and if there was a sell last.
#sells if there is a cross, and there was a buy last.
while(x<len(df3)):
    if(df1[x-10] < df1[x]):
        Uptrend = True
    else:
        Uptrend = False
    if(df2[x-1] < df3[x-1] and df2[x] > df3[x]):
        Cross = True
    elif(df2[x-1] > df3[x-1] and df2[x] < df3[x]):
        Cross = True
    if(Uptrend and Cross and BuyTime):
        money, stocks = buy(money, stocks, df1[x])
        BuyTime = False
    elif(not Cross and not BuyTime):
        money, stocks = sell(money, stocks, df1[x])
        BuyTime = True
    Cross = False
    x += 1

#checks to see how much money you made
endMoney = money + (stocks * df1[x-1])
print(endMoney)
print(x)


total_df = pd.concat([df1,df2,df3], axis=1)
print(total_df)
