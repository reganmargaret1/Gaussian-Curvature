from dolfin import *


def GC_Problems(prob, N):
    # cutoff = pow(N,2.0);
    cutoff = 0;
    xtol = 1e-18;

    #u(x,y) = x^4 + y^2
    if(prob == 1):
        x0 = -.57; y0 = -.57; x1 = .57; y1 = .57;
        exact = Expression('sqrt(1-pow(x[0],2) - pow(x[1],2))');
        gx = Expression('-x[0]*pow(1-pow(x[0],2) - pow(x[1],2), -1.0/2.0)');
        gy = Expression('-x[1]*pow(1-pow(x[0],2) - pow(x[1],2), -1.0/2.0)');
        K = 1;

        return (x0, y0, x1, y1, exact, gx, gy, K);






