#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>

double dWT()
{
    int num = 10;
    double dw = ((rand() % (2*num + 1)) - num)/100.0;
    return dw;
}


double GBM(double S, double mu, double iv, double t, int n, int paths)
{
    srand(time(NULL));

    double price = 0;
    double dt = t / (double) n;

    for(int i = 0; i < paths; ++i){
        double S0 = S;
        for(int j = 0; j < n; ++j){
            S0 += mu*S0*dt + iv*S0*dWT();
        }
        price += S0;
    }

    price /= (double) paths;

    return price;
}