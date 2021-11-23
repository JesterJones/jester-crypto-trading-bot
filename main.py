from binance import Client
import pandas as pd
import keys

client = Client(keys.key,keys.secret, tld='us')

def getdata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback+' ago CST'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time','Open','High','Low','Close','Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

test = getdata('ETHUSDT', '8h', '30 day')

#buy if asset fell by more than 0.2% within the last 30 min
#sell if asset rises by more than 0.15% or falls further by 0.15% 

def strategytest(symbol, qty, entried=False):
    df = getdata(symbol,'1m','30 min')
    cumulret = (df.Open.pct_change() + 1).cumprod() - 1
    if not entried:
        if cumulret[-1] > -0.002:
            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            print(order)
            entried=True
        else:
            print('No Trade has been executed')
    if entried:
        while True:
            df = getdata(symbol,'1m','30 min')
            sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'], unit = 'ms')]
            if len(sincebuy) > 0:
                sincebuyret = (sincebuy.Open.pct_change() + 1).cumprod() - 1
                if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < - 0.0015:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    print(order)
                    break

strategytest('ETHUSDT', 0.0025)