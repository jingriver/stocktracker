from numpy import r_, sin
from scipy.signal import cspline1d, cspline1d_eval

x = r_[0:10]
dx = x[1]-x[0]
newx = r_[-3:13:0.1]  # notice outside the original domain 
y = sin(x)
cj = cspline1d(y)
newy = cspline1d_eval(cj, newx, dx=dx,x0=x[0])
from pylab import plot, show
plot(newx, newy, x, y, 'o')
show()
