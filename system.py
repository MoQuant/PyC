import ctypes
import random as rd
import numpy as np
import time

def CountIt(f):
    def Handle(*a, **b):
        t0 = int(time.time())
        z = f(*a, **b)
        t1 = int(time.time())
        print(f.__name__, ' took ', t1 - t0,' seconds to run')
        return z
    return Handle

S = 100
r = 0.05
v = 0.25
t = 22.0/252.0
mu = 0.15
N = 5000
paths = 2000

@CountIt
def C():

    lib = ctypes.CDLL('./monte_carlo.so')


    lib.StockPrice.argtypes = (ctypes.c_double, 
                               ctypes.c_double,
                               ctypes.c_double,
                               ctypes.c_double,
                               ctypes.c_double,
                               ctypes.c_int,
                               ctypes.c_int)
    
    lib.StockPrice.restype = ctypes.c_double

    # Call the C function
    result = lib.StockPrice(100, 0.05, 0.25, 22.0/252.0, 0.15, 1000, 100)
    return result

@CountIt
def Python():
    Z = lambda: rd.randint(-100, 100)/100
    price = 0
    dt = t / N
    for i in range(paths):
        S0 = S
        for j in range(N):
            S0 += mu*S0*dt + v*S0*Z()
        price += S0
    
    stock_price = np.exp(-r*t)*(price/paths)
    return stock_price


c_price = C()
py_price = Python()
print(f'C Price: {c_price} | Python Price: {py_price}')