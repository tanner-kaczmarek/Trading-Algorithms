import pandas as pd
import math
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import time

api_key = '111111111111'
Tickers = ['AAPL', 'TWTR', 'TSLA', 'NFLX', 'FB', 'MSFT', 'DIS', 'GPRO', 'SBUX', 'F', 'BABA', 'BAC', 'FIT', 'GE', 'HOME', 'MGM', 'SPXS']
FinalMoneyMA = []  #Array that carries the final information for MA in format [endMoney, PeriodS, PeriodL, Ticker]
FinalMoneyRSI = [] #Array that carries the final information for RSI in format[endMoney, Period, Ticker]
CountMA = 0
CountRSI = 0
maxMA = []         #Array that has the maxMAs for a given stock
maxRSI = []        #Array that has the maxRSI's for a given stock

ts = TimeSeries(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format= 'pandas')

#buy and sell algorithm to test money on previous data
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

#a loop to test all the tickers, with an array of different SMA and LMA periods to find the best time period to use
for y in range(len(Tickers)):
    data, meta_data = ts.get_intraday(symbol=Tickers[y], interval='1min', outputsize='full')
    for periodS in range(5, 50, 5):
        for periodL in range(50, 200, 10):

            data_sma, meta_data_sma = ti.get_sma(symbol=Tickers[y], interval='1min', time_period=periodS, series_type='close')
            data_lma, meta_data_lma = ti.get_sma(symbol=Tickers[y], interval='1min', time_period=periodL, series_type='close')
            df1 = data['4. close'].iloc[periodL-1::]
            df2 =data_sma['SMA'].iloc[periodL-periodS::]
            df3 = data_lma['SMA']

            #only needs to run the RSI for one period so only when its the first run for the for loop for periodL
            if(periodL == 50):
                period = periodS + 25  #range is 30-75 testing for RSI
                data_rsi, meta_data_rsi = ti.get_rsi(symbol=Tickers[y], interval='1min', time_period=period, series_type='close')
                df4 =data_rsi['RSI'].iloc[periodL-period-1::]
                if(len(df4) == len(df3)):  #bug where sometimes they are not the same length so this is verifying they are
                    df1.index = df2.index = df3.index = df4.index
            else:
                if(len(df1) == len(df2) and len(df2) == len(df3)): #bug where sometimes they are not the same length so this is verifying they are
                    df1.index = df2.index = df3.index 
                else:
                    continue


            moneyMA = 10000
            stocksMA = 0    
            tempMA = [] 
            maxTempMA = 0 

            moneyRSI = 10000
            stocksRSI = 0
            tempRSI = []
            maxTempRSI = 0 

            #buys if there is an uptrend, if the sma and the lma cross, and if there was a sell last.
            #sells if there is a cross, and there was a buy last.
            def ma(i, BT, money, stocks):
                Cross = False
                if(df1[i-10] < df1[i]):
                    Uptrend = True
                else:
                    Uptrend = False
                if(df2[i-1] < df3[i-1] and df2[i] > df3[i]):
                    Cross = True
                elif(df2[i-1] > df3[i-1] and df2[i] < df3[i]):
                    Cross = True
                if(Uptrend and Cross and BT):
                    money, stocks = buy(money, stocks, df1[i])
                    BT = False
                elif(not Cross and not BT):
                    money, stocks = sell(money, stocks, df1[i])
                    BT = True
                return BT, money, stocks  

            #Buys if the RSI calculated value is less than 30 and if sold last
            #Sells if the RSI calculated value is greater than 70 and if bought last
            def rsi(i, BT, money, stocks):
                if(df4[i] <= 30  and BT):
                    money, stocks = buy(money, stocks, df1[x])
                    BT = False
                elif(df4[i] >= 70  and not BT):
                    money, stocks = sell(money, stocks, df1[x])
                    BT = True
                return BT, money, stocks

            BuyTimeMA = True
            BuyTimeRSI = True
            x = 10

            while(x<len(df3)):
                BuyTimeMA, moneyMA, stocksMA = ma(x, BuyTimeMA, moneyMA, stocksMA)
                if(periodL == 50 and len(df4) == len(df3)):
                    BuyTimeRSI, moneyRSI, stocksRSI = rsi(x, BuyTimeRSI, moneyRSI, stocksRSI)
                x += 1
            
            #calculating the final money and putting it in the final array for MA
            #Also adding the maxMA for a given ticker
            endMoneyMA = moneyMA + (stocksMA * df1[x-1]) 
            tempMA.append(endMoneyMA)
            tempMA.append(periodS)
            tempMA.append(periodL)
            tempMA.append(y)
            FinalMoneyMA.append(tempMA)
            if(FinalMoneyMA[maxTempMA][0] < endMoneyMA and FinalMoneyMA[maxTempMA][3] == y):
                maxTempMA = CountMA
            print(FinalMoneyMA[CountMA])
            CountMA +=1

            #calculating the final money and putting it in the final array for RSI
            #Also adding the maxRSI for a given ticker
            if(periodL == 50):
                endMoneyRSI = moneyRSI + (stocksRSI * df1[x-1])
                tempRSI.append(endMoneyRSI)
                tempRSI.append(period)
                tempRSI.append(y)
                FinalMoneyRSI.append(tempRSI)
                if(FinalMoneyRSI[maxTempRSI][0] < endMoneyRSI and FinalMoneyRSI[maxTempRSI][2]==y):
                    maxTempRSI = CountRSI
                print(FinalMoneyRSI[CountRSI])
                CountRSI += 1

            #needs to sleep as I only get 5 API calls every five minutes
            if(periodS == 5 and periodL == 50):
                time.sleep(55)
            else:
                time.sleep(30)
    
    maxMA.append(maxTempMA)
    maxRSI.append(maxTempRSI)

#Running through and printing max values for RSI and MA for a given ticker
while x < len(maxMA):
    print('MA Stock: ', Tickers[FinalMoneyMA[maxMA[x]][3]], ' Price:  ', FinalMoneyMA[maxMA[x]][0], ' Short period: ', FinalMoneyMA[maxMA[x]][1], ' Long period: ', FinalMoneyMA[maxMA[x]][2] )
    print('RSI Stock: ', Tickers[FinalMoneyRSI[maxRSI[x]][2]], ' Price: ', FinalMoneyRSI[maxRSI[x]][0], ' Period: ', FinalMoneyRSI[maxRSI[x]][1])
