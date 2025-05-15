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

# Converts options expiration date to days/365
def CT(idate):
    tx = int(time.time())
    tv = time.mktime(datetime.datetime.strptime(idate, '%m-%d-%Y').timetuple())
    return (tv - tx)/(60*60*24*365)

# Options Chain Function
def OptionsChain():

    # Extracts the options contracts date from initial instrument name
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

    # Message to fetch last 500 trades from the options
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

    # Connects to Deribit's API to extract options chian data
    async def call_api(msg):
        # Bypass SSL if certificate is not available
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.ws_connect('wss://test.deribit.com/ws/api/v2') as conn:
                await conn.send_str(msg)
                response = await conn.receive()
                resp = json.loads(response.data)
                resp = resp['result']['trades']
                df = []
                # Build a pandas dataframe out of the instrument, price, and implied volatility
                for i in resp:
                    df.append([FixName(i['instrument_name']), i['price'], i['iv']/100])
                return pd.DataFrame(df, columns=['Date', 'Price', 'IV'])

    return asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))

# Fetches candlesticks from Coinbase to calculate the current price and drift, which in this case is the cumulative rate of return
def CryptoData(ticker='BTC-USD'):
    url = 'https://api.exchange.coinbase.com/products/{}/candles?granularity=60'
    r = requests.get(url.format(ticker)).json()
    close = np.array(r).T[4]
    current_price = close[0]
    ror = close[:-1]/close[1:] - 1
    drift = np.prod([(1 + r) for r in ror]) - 1
    return current_price, drift

# Load the Geometric Brownian Motion C function into Python
lib = ctypes.CDLL("./simulate.so")

# Assign datatypes to GBM C function
lib.GBM.argtypes = (ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int,
                    ctypes.c_int)

# Assign result datatype
lib.GBM.restype = ctypes.c_double

# S, drift, v, t, n=, paths=

# Set paths and steps
n = 10500
paths = 1000

# Fetches stock price and drift
input_date = '05-31-2024'
S, drift = CryptoData()
T = CT(input_date)

# Fetches options chain data
df = OptionsChain()

# Makes sure options are fetched based on the input date
data = df[(df['Date'] == input_date)]

# Takes a sum of the price to calculate the weight of each option
total_price = data['Price'].sum()
weights = data['Price']/total_price

# Aggregate implied volatility is computed by doing a dot product on the weights and iv vectors
iv = weights.T.dot(data['IV'])

# Fetches the simulated price from the GBM C function
simulated_price = lib.GBM(S, drift, iv, T, n, paths)

# If the Bitcoin's price is less than the simulated price the algorithm recommends to buy Bitcoin, else it recommends to sell Bitcoin
if S < simulated_price:
    print(S, drift, iv, T, simulated_price)
    print("Buy Bitcoin")

if S >= simulated_price:
    print(S, drift, iv, T, simulated_price)
    print("Sell Bitcoin")
