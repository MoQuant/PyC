#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

double Z()
{
    return ((rand() % 201) - 100)/100;
}

double StockPrice(double S, double r, double v, double t, double mu, int n, int paths)
{
    srand(time(NULL));

    double dt = t / (double) n;
    
    double price = 0;
    for(int i = 0; i < paths; ++i){
        double S0 = S;
        for(int j = 0; j < n; ++j){
            S0 += mu*S0*dt + v*S0*Z();
        }
        price += S0;
    }

    double stock_price = exp(-r*t)*(price/(double) paths);

    return stock_price;
}