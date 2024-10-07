import numpy as np
import pandas as pd


def RSI(close):
    up = sum([i - j for i, j in zip(close[1:], close[:-1]) if i - j >= 0])
    down = sum([abs(i - j) for i, j in zip(close[1:], close[:-1]) if i - j < 0])
    rsi = 100 - 100/(1 + up/down)
    return rsi

def RSIWindow(dataset, tickers, window=50):
    result = {}
    n = len(dataset[tickers[0]])
    for tick in tickers:
        result[tick] = []
        for i in range(window, n):
            hold = dataset[tick][i-window:i]
            rsi = RSI(hold)
            result[tick].append(rsi)
    return result    
        

tickers = ['AAPL','AMD','AMZN','BLK','CSCO','GOOGL','JPM','MSFT','NFLX','NVDA','ORCL','QCOM','TSLA']

data = {tick:pd.read_csv(f'{tick}.csv')[::-1]['adjClose'].values for tick in tickers}

window = 50

rsiData = RSIWindow(data, tickers, window=window)

balance = 100000
tx_fee = 0.005
weight_per_stock = 0.05

interest_rate = 0.03

volume = {tick:0 for tick in tickers}

rate_of_return = 0

positions = {tick:'neutral' for tick in tickers}
prices = {tick:None for tick in tickers}

N = len(data[tickers[0]])

cRor = 1

for t in range(window, N):
    for tick in tickers:
        the_rsi = rsiData[tick][t-window]

        # CLOSE SHORT
        if the_rsi < 33 and positions[tick] == 'short':
            positions[tick] = 'neutral'
            oldbalance = balance
            balance = balance + prices[tick]*(1 - tx_fee)*(1 - interest_rate)*volume[tick] - data[tick][t]*volume[tick]*(1 + tx_fee)
            rate_of_return = (prices[tick]*(1-tx_fee))/(data[tick][t]*(1+tx_fee)) - 1.0
            cRor *= (1 + rate_of_return)
            print(f"Short Trade | Ticker = {tick} | RateOfReturn = {rate_of_return}") 


        # ENTER SHORT
        if the_rsi > 66 and positions[tick] == 'neutral':
            positions[tick] = 'short'
            prices[tick] = data[tick][t]
            volume[tick] = (balance * weight_per_stock)/prices[tick]

        # CLOSE LONG
        if the_rsi > 66 and positions[tick] == 'long':
            positions[tick] = 'neutral'
            oldbalance = balance
            balance = balance + (data[tick][t]*volume[tick])*(1 - tx_fee) - prices[tick]*(1 + tx_fee)*volume[tick]

            rate_of_return = (data[tick][t]*(1-tx_fee))/(prices[tick]*(1+tx_fee)) - 1.0
            cRor *= (1 + rate_of_return)
            print(f"Long Trade | Ticker = {tick} | RateOfReturn = {rate_of_return}") 

        # GO LONG
        if the_rsi < 33 and positions[tick] == 'neutral':
            positions[tick] = 'long'
            prices[tick] = data[tick][t]
            
            volume[tick] = (balance * weight_per_stock)/prices[tick]

        
print("Final Balance: ", balance)
print("Final Return: ", cRor - 1)


            
