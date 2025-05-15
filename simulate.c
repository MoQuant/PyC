#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>

// Generate dWT as being a number being between -10% to 10%
double dWT()
{
    int num = 10;
    double dw = ((rand() % (2*num + 1)) - num)/100.0;
    return dw;
}

// Simulation of Geometric Brownian Motion
double GBM(double S, double mu, double iv, double t, int n, int paths)
{
    // Makes sure random values are not consistent
    srand(time(NULL));

    double price = 0;
    double dt = t / (double) n;

    // Runs all possible paths
    for(int i = 0; i < paths; ++i){
        double S0 = S;
        for(int j = 0; j < n; ++j){
            S0 += mu*S0*dt + iv*S0*dWT();
        }
        price += S0;
    }

    // Computes average price of simulation
    price /= (double) paths;

    return price;
}
