import alibom
import alib
from datetime import date

def alib_fwd_date(fwd):
  today = date.today().strftime("%m-%d-%Y")
  start_date = alibom.date(today)
  end_date = alib.date_fwd_adj2(start_date, fwd + ",B","/apps/cheetah/alib/holidays/1.2.0.3/data/holiday.usd")
  return str(end_date)

def alib_bussiness_day():
  today = date.today().strftime("%m-%d-%Y")
  today = '01-15-2007'
  start_date = alibom.date(today)      
  return alib.is_business_day(start_date, "/apps/cheetah/alib/holidays/1.2.0.3/data/holiday.usd")

def alib_ols_regression(ax, ay, base):
    out = alib.linear_regression(ax, ay, None, base)
    print dir(out)

def alib_interpolation(ax, ay, x):    
    return alib.interp_lf1(ax, ay, x)

def alib_check():
    print "ALIB Version: "+alib.version()
    print "Security Path: "+alib.security_get_path()
    print "Security expiration: "+str(alib.security_get_expiration())
#        System.out.println("ALIB Version: "+alibFuncs.ALIB_VERSION());
#        System.out.println("Security Path: "+alibFuncs.ALIB_SECURITY_GET_PATH());
#        System.out.println("Security Path: "+alibFuncs.ALIB_SECURITY_GET_EXPIRATION());
                      
def main():
    alib_check()
    print alib_bussiness_day()
    print alib_fwd_date('-1D')
    x = [2, 3, 5.05, 6.75, 8.01]
    y = [7.96, -5.93, 1.65, 26.5, 30]
    x0 = 2.5
    print alib_interpolation(x, y, x0)
    alib_ols_regression(x, y, 'ols')
    h = {}
    if not h.has_key(1):
        print 'not'
        h[1]=[]
    h[1].append('a1')
    h[1].append('a2')
    h[1].append('a3')
    print h
            
    d1 = {1:'one',2:'two',3:'three'}
    d2 = {1:'yi',3:'san', 4:'si'}
    d1.update(d2)
    print d1
    print d2
    
    h1 = [1,2,3]
    print h1
    
    while len(h1)>0:
        h1.remove(h1[-1])
        print h1    
        
main()