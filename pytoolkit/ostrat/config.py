import os, sys
import logging
import logging.config
from datetime import datetime, date, timedelta
import time
import xldate

osname = os.name.lower()
#if osname=='posix':
#    logging.config.fileConfig("/apps/cheetah/cheetah_apps/python/JuliPrice/juliprice_logging.conf")
#elif osname=='nt':
#    logging.config.fileConfig("juliprice_logging.conf")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    
QTEXCEPTION = 'QT Error'
DATEFMT = "%Y/%m/%d"
QTDATEFMT = 'yyyy/MM/dd'
#QTDATEFMT = 'MM/dd/yyyy'
DATEFMT_ETP = "%m/%d/%Y"

def str2datetime(strdate, fmt=DATEFMT):
#    try:
#        dtuple = time.strptime(strdate, fmt)
#    except ValueError:
#        dtuple = time.strptime(strdate, DATEFMT_ETP)
#    return datetime(dtuple[0], dtuple[1], dtuple[2], dtuple[3], dtuple[4], dtuple[5])
    dtuple = time.strptime(strdate, fmt)
    return datetime(dtuple[0], dtuple[1], dtuple[2], dtuple[3], dtuple[4], dtuple[5])

def convert2etpdate(strdate, fmtfrom=DATEFMT, fmtto=DATEFMT_ETP):
    dt = str2datetime(strdate, fmtfrom)
    return nvldate(dt, fmtto)

def getDays(t1, t2, fmt=DATEFMT):
    days = (str2datetime(t2, fmt)-str2datetime(t1, fmt)).days
    if days < 0:
        print "negative days between [%s] to [%s]" % (t1, t2)
        return 0
    return days

def getTimeDiffByDays(tstart, tend, fmt=DATEFMT):
    days = getDays(tstart, tend, fmt)
    if days < 30:
        return "%dd" % days
    if days < 365:
        dm = int(round(days/30.0))
        return "%dm" % dm
    dy = int(days/365.0)
    daysleft = days%365.0
    if daysleft<30:
        return "%dy" % dy
    monthleft = int(round(daysleft/30.0))
    return "%dy%dm" % (dy,monthleft)
        
def getTimeDiff(tstart, tend, fmt=DATEFMT):
    t1 = str2datetime(tstart, fmt)
    t2 = str2datetime(tend, fmt)
    if t1>t2:
        t = t1
        t1 = t2
        t2 = t
                            
    dy = t2.year-t1.year
    if dy>0:
        return "%dy" % dy    
    dm = t2.month-t1.month
    if dm>0:
        return "%dm" % dm    
    dd = t2.day-t1.day
    if dd>=0:
        return "%dd" % dd
    return None

def IIf(bCondition, uTrue, uFalse):
    """Simulating the ternary(?:condition) operator in Python"""
    return ( uTrue, uFalse )[ not bCondition ]    

def getlastDay(dt):
    if dt is None:
        return False
    
    import calendar
    (weekday, days) = calendar.monthrange(dt.year, dt.month)
    if days == dt.day:
        return True
    else:
        return False

def xldstr2num(strdate, datemode=0, fmt=DATEFMT):
    dt = str2datetime(strdate, fmt)
    return xldate.xldate_from_date_tuple((dt.year, dt.month, dt.day),datemode) 
        
def xldnum2dstr(num, datemode=0, fmt=DATEFMT):
    dtuple = xldate.xldate_as_tuple(num,datemode)
    return datetime(dtuple[0],dtuple[1],dtuple[2]).strftime(fmt)
        
def nvldate(d, fmt=DATEFMT):
    if d is None:
        t_datedDate = 0
    else:
        t_datedDate= d.strftime(fmt)
    return t_datedDate

def addDays(dt, days):
    d = timedelta(days=days)
    dt += d
    return dt
    
def addYears(dt, years):
    return datetime(dt.year+years, dt.month, dt.day)

def addMonth(dt, month):
    d = timedelta(days=month*30)
    dt += d
    return dt

def pythondatetime():
#    now = date.today()
#    now1 = datetime.today()
#    today = now.strftime( "%Y%m%d" )
#    today1 = now1.strftime( "%Y%m%d" )
#    #print now, now1
#    print addDays(now, 31)
#    
#    dtuple = time.strptime("20070131", "%Y%m%d")
#    d = datetime(dtuple[0], dtuple[1], dtuple[2], dtuple[3], dtuple[4], dtuple[5])
#    s = d.strftime("%Y%m%d")
#    logging.debug(d)
#    print datetime.utcnow()
#    print time.time()
#    print str2datetime("20070131", "%Y%m%d")
    
    t1 = "20051231"
    t2 = "20080521"
    print t1, t2
    print getDays(t1,t2,"%Y%m%d")
    print getTimeDiff(t1, t2, "%Y%m%d")
    print getTimeDiffByDays(t1, t2, "%Y%m%d")
    
def sortDictbyKey(dict):
    keys = dict.keys()
    keys.sort()
    sortedField = ([(x, dict[x]) for x in keys])
    return sortedField
            
if __name__ == "__main__":
    pythondatetime()
