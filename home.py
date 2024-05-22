import ctypes
import time
import requests
import json
import numpy as np
import asyncio
import aiohttp
import pandas as pd
import time
import datetime

def CT(idate):
    tx = int(time.time())
    tv = time.mktime(datetime.datetime.strptime(idate, '%m-%d-%Y').timetuple())
    return (tv - tx)/(60*60*24*365)

def OptionsChain():
    
    def FixName(u):
        s = u.split('-')
        strike = s[-2]
        the_date = s[1]
        reference = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
        year = '20' + str(the_date[-2:])
        month = the_date[-5:-2]
        month = reference[month]
        day = the_date[:-5]
        if len(day) < 2:
            day = '0' + str(day)
        the_date = f'{month}-{day}-{year}'
        return the_date
    
    msg = {
        "jsonrpc" : "2.0",
        "id" : 9290,
        "method" : "public/get_last_trades_by_currency",
        "params" : {
            "currency" : "BTC",
            "count" : 500,
            "kind": 'option'
        }
    }

    async def call_api(msg):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.ws_connect('wss://test.deribit.com/ws/api/v2') as conn:
                await conn.send_str(msg)
                response = await conn.receive()
                resp = json.loads(response.data)
                resp = resp['result']['trades']
                df = []
                for i in resp:
                    df.append([FixName(i['instrument_name']), i['price'], i['iv']/100])
                return pd.DataFrame(df, columns=['Date', 'Price', 'IV'])

    return asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))

def CryptoData(ticker='BTC-USD'):
    url = 'https://api.exchange.coinbase.com/products/{}/candles?granularity=60'
    r = requests.get(url.format(ticker)).json()
    close = np.array(r).T[4]
    current_price = close[0]
    ror = close[:-1]/close[1:] - 1
    drift = np.prod([(1 + r) for r in ror]) - 1
    return current_price, drift

lib = ctypes.CDLL("./simulate.so")

lib.GBM.argtypes = (ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int,
                    ctypes.c_int)

lib.GBM.restype = ctypes.c_double

# S, drift, v, t, n=, paths=

n = 10500
paths = 1000

input_date = '05-31-2024'
S, drift = CryptoData()
T = CT(input_date)

df = OptionsChain()

data = df[(df['Date'] == input_date)]

total_price = data['Price'].sum()
weights = data['Price']/total_price

iv = weights.T.dot(data['IV'])

simulated_price = lib.GBM(S, drift, iv, T, n, paths)

if S < simulated_price:
    print(S, drift, iv, T, simulated_price)
    print("Buy Bitcoin")

if S >= simulated_price:
    print(S, drift, iv, T, simulated_price)
    print("Sell Bitcoin")
