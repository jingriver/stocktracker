import os, sys 
from datetime import datetime, date, timedelta
import time, calendar
import xldate
from sets import Set
from dbutil import dao

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

import logging, logging.config
#osname = os.name.lower()
#if osname=='posix':
#    logging.config.fileConfig("/apps/cheetah/cheetah_apps/python/JuliPrice/juliprice_logging.conf")
#elif osname=='nt':
#    logging.config.fileConfig("juliprice_logging.conf")

#logging.basicConfig(level=logging.DEBUG, 
#                    format='%(asctime)s %(levelname)s %(message)s', 
#                    filename = 'dq.log',
#                    filemode = 'w')

currentDate = date.today().strftime('%Y%m%d')
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s', 
                    filename = "dq." + str(currentDate) + ".log",
                    filemode = 'w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-2s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
    
QTEXCEPTION = 'QT Error'
DATEFMT = "%Y/%m/%d"
QTDATEFMT = 'yyyy/MM/dd'
DATEFMT_ETP = "%m/%d/%Y"

def str2datetime(strdate, fmt=DATEFMT):
    dtuple = time.strptime(strdate, fmt)
    return datetime(dtuple[0], dtuple[1], dtuple[2], dtuple[3], dtuple[4], dtuple[5])

def str2date(strdate, fmt=DATEFMT):
    dtuple = time.strptime(strdate, fmt)
    return date(dtuple[0], dtuple[1], dtuple[2])

def tranformDateFormat(strdate, fmtFrom="%Y%m%d", fmtTo="%m/%d/%y"):
    return nvldate(str2date(strdate, fmtFrom), fmtTo)
        
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

def addYears(dt, years):    
    try:
        d = datetime(dt.year+years, dt.month, dt.day)
    except ValueError: #leap year
        d = datetime(dt.year+years, dt.month, dt.day-1)
    return d

def addMonth(dt, month):
    d = timedelta(days=month*30)
    dt += d
    return dt

def addDays(dt, days):
    d = timedelta(days=days)
    dt += d
    return dt

def addTime(dt, duration):
    duration = str(duration).strip().lower()
    number = int(duration[:-1])
    if duration.endswith("y"):
        return addYears(dt, number)
    elif duration.endswith("m"):
        return addMonth(dt, number)
    elif duration.endswith("d"):
        return addDays(dt, number)
    else:
        raise "wrong format for duration [%s]" % duration

def julian(dt, fmt="%Y%m%d"):
    d2 = []
    for x in dt:
        d2.append(xldstr2num(x, 0, fmt))        
    return d2

def multi_intersect(first, *params):
    s = Set(first)
    for x in params:
        s.intersection_update(x)
    return list(s)

def multi_union(first, *params):
    s = Set(first)
    for x in params:
        s.union(x)
    return list(s)
                
def sortDictbyKey(dict):
    keys = dict.keys()
    keys.sort()
    sortedField = ([(x, dict[x]) for x in keys])
    return sortedField

def multi_blast2 (query, program, database, *more_queries):
    """A function can take additional optional arguments by 
        prefixing the last parameter with an *  (asterix). 
        Optional arguments are then available in the tuple 
        referenced by this parameter.
        call example:
        multi_blast2 ('seq.fasta', 'blastp', 'database', 'seq2.fasta', 'seq3.fasta')        
    """
    command = "blastall -p %s -d %s -i %s" % (program, database, query)
    for q in more_queries:
        command += " -i '%s'" % (q)
    return command
        
def blast2(query, program='blastp', database='swissprot', **params):
    """Optional variables can also by passed as keywords, 
        if the last parameter is preceded by **. In this case, 
        the optional variables are placed in a dictionary.        
        call example:
        blast2('seq.fasta', m=8, e=1.0, F='S 10 1.0 1.5')
    """
    command = "blastall -p %s -d %s -i %s" % (program, database, query)
    if params:
        for para,value in params.items():
            command += " -%s '%s'" % (para, value)
    return command

def dict2CSV(fname, dict):
    if len(dict)==0: return
    f = open(fname, 'w')
    ks = dict.keys()
    ks.sort()    
    
    if isinstance(dict.values()[0], (list, tuple,)):
        for x in ks:
            val = map(str, dict[x])
            f.write(str(x) + "," + ",".join(val)+"\n")
    else:
        for x in ks:
            val = dict[x]
            f.write(str(x) + str(val)+"\n")
    f.close()
        
def list2CSV(fname, l1):
    if len(l1)==0: return
    f = open(fname, 'w')
    if isinstance(l1[0], (int, float, long, )):
        fmtstr = "%f\n"
    #elif isinstance(obj, basestring): 
    else:
        fmtstr = "%s\n"
    for x in l1:
        f.write(fmtstr % x)
    f.close()    

#testing function
def testpythondatetime():
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
            
if __name__ == "__main__":
    #print __debug__
    #f = open("residual.csv")
    print multi_blast2 ('seq.fasta', 'blastp', 'database', 'seq2.fasta', 'seq3.fasta')
    print blast2('seq.fasta', m=8, e=1.0, F='S 10 1.0 1.5')
    
    #testpythondatetime()
