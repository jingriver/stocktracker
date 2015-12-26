from scipy import stats, linspace
from scipy import interpolate
from scipy import array

#x must be sorted
x = [2, 3, 5.05, 6.75, 8.01]
y = [7.96, -5.93, 1.65, 26.5, 30]

ax = linspace(2.5,8,50)
#linear interpolation
mint = interpolate.interp1d( x, y, kind='linear' )
ay = mint(ax)

#cubic spline interpolation
tck = interpolate.splrep(x,y,s=0)
az = interpolate.splev(ax,tck,der=0)

#linear regression
(a_s,b_s,r,tt,stderr)=stats.linregress(x,y)
newx = linspace(0,10,50)
newy = newx*a_s+b_s

y0 = x[0]*a_s+b_s
y1 = x[-1]*a_s+b_s
#x.insert(0,x[0])
#y.insert(0,y0)
#x.append(x[-1])
#y.append(y1)

extrax = [2.5, 4, 6]
x.extend(extrax)
#y.extend(interpolate.splev(extrax,tck,der=0).tolist())
y.extend(mint(extrax).tolist())

(a_s,b_s,r,tt,stderr)=stats.linregress(x,y)
newx = linspace(0,10,50)
newy = newx*a_s+b_s

#s = map(upper, [str(x) for x in newx])
#print s
#s = '1209:YSEN'
#print s.find(':Y')

bm='US987434AM99'
bm=bm[2:-1]
print bm
print len(bm)
from pylab import plot, show
plot(ax, az, x, y, 'ro')
#plot(newx, newy,x, y, 'o')
show()

#foodict = None
#food = None
#def snafu():
#    global foodict
#    foodict = {"foobar": "huh?"}
#    print foodict
#    food = "rice"
#
#def s():
#    print foodict
#    print food
#
#snafu()
#s()