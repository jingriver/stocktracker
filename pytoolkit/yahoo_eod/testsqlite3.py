# visualization) in python? The more computationally intensive stuff will probably be wrapped in C++.
#Pros:
#
#Rapid development (at least initially) 
#Leverage a lot of free prebuilt libraries (graphs, numerics, etc) 
#You can easily integrate a phyton intepreter and have everything scriptable in an easy way. Cool feature. 
#A lot of people have at least heard about phyton
#Cons:
#
#If need to specify that it is a phyton based product that might scare some people away (policy reasons, etc) 
#You might run into scalability problems later on in the development. I'm no expert of phyton, but that is a tendency for these types of languages

from config import *
import sqlite3
from TaLib import *
import re
from threading import Thread

from scipy import stats, polyval, polyfit, sqrt, linspace, fft, concatenate
from pylab import plot, title, show , legend, grid
from numpy import arange, average, sin, cos, zeros

#from testdq import dqzoo
from testHttp import httpConnection
from testyahoo import yahooZoo
from businessday import *

DBDATEFMT = '%Y%m%d'
sql_create = ("""create table prices
            (symbol text, tradedate text, open real, high real, low real, close real, 
             adj_close real, volume real, averagevol real, week52high real, week52low real, 
             updatetime text,
             PRIMARY KEY (symbol, tradedate))""",
         """create table industry_ref
            (industry_id integer primary key AUTOINCREMENT, industry_name text, 
            parent_id integer)""",         
         """create table security
            (symbol text primary key, company_name text, exchange text, 
            industry_id integer, sub_industry_id integer, sp500 integer,
            GICS integer, sector text,
            updatetime text)""",
)

sql_create_mysql = ("""create table prices
            (symbol VARCHAR(10), tradedate VARCHAR(20), open real, high real, low real, close real, 
             adj_close real, volume real, averagevol real, week52high real, week52low real, 
             updatetime datetime ,
             PRIMARY KEY (symbol, tradedate))""",
         """create table industry_ref
            (industry_id integer primary key, industry_name VARCHAR(40), 
            parent_id integer)""",
         """create table security
            (symbol VARCHAR(10) primary key, company_name VARCHAR(50), exchange VARCHAR(40), 
            industry_id integer, sub_industry_id integer, sp500 integer,
            GICS integer, sector VARCHAR(50),
            updatetime datetime )""",
)

sql_del_security = """delete from security where symbol='%s'"""     
sql_check_price = """select * from prices where symbol=? and tradedate=?"""
sql_del_price = """delete from prices where symbol=? and tradedate=?"""
sql_del_one_price = """delete from prices where symbol='%s' and tradedate='%s'"""
sql_del_all_price = """delete from prices where tradedate='%s'"""

def dropAllTbls(dbo):
    cur = dbo.cursor
    cur.execute('drop table prices')
    cur.execute('drop table industry_ref')
    cur.execute('drop table security')

def createTable(dbo, sql):
    cur = dbo.cursor
    # Create table
    try:
        cur.execute(sql)
    except sqlite3.OperationalError:
        print sys.exc_info()[0]
        print sys.exc_info()[1]

def purgeDB(dbo):
    # Drop all tables
    dropAllTbls(dbo)    
    # Create tables
    for s in sql_create:
        createTable(dbo, s)

def purge_security(dbo):
    try:
        cur = dbo.cursor
        cur.execute('drop table security')        
        cur.execute(sql_create[2])
    except sqlite3.OperationalError:
        print sys.exc_info()[0]
        print sys.exc_info()[1]

def purge_industry_ref(dbo):
    try:
        cur = dbo.cursor
        cur.execute('drop table industry_ref')        
        cur.execute(sql_create[1])
    except sqlite3.OperationalError:
        print sys.exc_info()[0]
        print sys.exc_info()[1]

#depreciated
#def readInactiveSymbols():
#    f = open("discontinued_symbols", "r")
#    line = f.read()
#    f.close()
#    mlist = line.split(",")
#    mlist = [str(x).strip() for x in mlist]        
#    return mlist            
#
#depreciated            
#def readSymListToDB(dbo, fname, clearFirst = False):
#    if clearFirst: purge_security(dbo)
#    mlist = readInactiveSymbols()    
#    f = open(fname)
#    lines = f.readlines()    
#    for ln in lines:
#        row = re.split(' {5,}', ln.strip())
#        if len(row)!=2:
#            raise "wrong symbols %s" % row                    
#        if row[0].find('/')>-1:            
#            row = [row[0].split('/')[0], row[1]]
#        sym = row[0]
#        name = row[1]            
#        updateSecurity(dbo, sym, name, 0 if sym in mlist else 1)
#    f.close()

def downloadSymListToDB(dbo, clearFirst = False):
    #"http://www2.standardandpoors.com/servlet/Satellite?pagename=spcom/page/download&sectorid=%20%3E%20%2700%27&itemname=%3E=%20%271%27&dt=10-SEP-2008&indexcode=500"
    if clearFirst: 
        purge_security(dbo)
    else:
        conn = dbo.conn
        cur = dbo.cursor
        cur.execute("update security set sp500=0")
        conn.commit()
        
    yesterday = nvldate(addBusinessDay(date.today(), -1), "%d-%b-%Y")
    url = "http://www2.standardandpoors.com/servlet/Satellite?pagename=spcom/page/download&sectorid=%20%3E%20%2700%27&itemname=%3E=%20%271%27&dt=" + yesterday + "&indexcode=500"  
    httpconn = httpConnection()
   
    html = httpconn.getHtml(url)
    lines = html.split("\n")[1:]
    lines = filter(lambda x:len(x)>0, lines)            
    for ln in lines:
        row = ln.split(",")
        row = [str(x).strip() for x in row]
        sym = row[0]
        name = row[1]
        gics = row[3]
        sector = row[4]
        if sym.find('.')>-1:     
            sym = sym.replace('.', '-')        
        updateSecurity(dbo, sym, name, gics, sector)        

def updateSecurity(dbo, sym, name, gics, sector, sp=1):
    conn = dbo.conn
    cur = dbo.cursor
    try:
        print sym
        cur.execute("select * from security where symbol='%s'" % sym)
        if cur.fetchone():
            cur.execute("""update security set company_name=?,  
                        GICS=?, sector=?, sp500=?,
                        updatetime=? where symbol=?""", 
                        (name, gics, sector, sp, datetime.now(), sym))                        
        else:
            cur.execute("""insert into security(symbol, company_name, GICS, sector, sp500, updatetime)            
                  values (?, ?, ?, ?, ?, ?)""", 
                  (sym, name, gics, sector, sp, datetime.now(),))
        conn.commit()
        #print "Saved successfully"
    except sqlite3.IntegrityError:
        print "Already existed"
        pass    
        
def updatePricesFromDQ(dbo, sym):
    conn = dbo.conn
    cur = dbo.cursor
    
    ## Insert a row of data
    #cur.execute("""insert into prices(tradedate, symbol, close, updatetime)   
    #          values ('2006-01-05', 'RHAT', 35.14, ?)""", (datetime.now(),))
     
    # Larger example
    updtime = datetime.now()
    #for t in (('2006-03-28', 'IBM', 45.00, updtime),
    #          ('2006-04-05', 'MSOFT', 72.00, updtime),
    #          ('2006-04-06', 'IBM', 53.00, updtime),):
    #    cur.execute('insert into prices(tradedate, symbol, close, updatetime) values (?,?,?,?)', t)
    dq = dqzoo()
    res = dq.queryHistory(sym, "TODAY-20Y", "TODAY")
    for row in res:
        if row[4] is not None:
            try:
                cur.execute("""insert into prices(tradedate, symbol, 
                      open, high, low, close, volume, updatetime)   
                      values (?, ?, ?, ?, ?, ?, ?, ?)""", 
                      (row[0], row[1], row[2], row[3],  
                       row[4], row[5], row[6],
                       datetime.now(),))
                #print "Saved successfully"
            except sqlite3.IntegrityError:
                #print "Already existed"
                pass
    conn.commit()

def updatePricesFromYahoo(dbo, sym):
    sym = sym.upper()
    conn = dbo.conn
    cur = dbo.cursor
    
    updtime = datetime.now()
    dq = yahooZoo()    
    res = dq.queryHistory(sym, 1, "TODAY")
    if res is None:
        print "no price for [%s]" % sym 
        return 
    res = res.split("\n")
    res = [x.strip() for x in res]
    for row in res[1:]:
        row = row.split(',') 
        try:
            tdate = nvldate(str2datetime(row[0], '%Y-%m-%d'), DBDATEFMT)
        except:
            continue
        if row[4] is not None:
            cur.execute(sql_check_price, (sym, tdate))
            if cur.fetchone() is not None:
                cur.execute(sql_del_price, (sym, tdate))            
            cur.execute("""insert into prices(tradedate, symbol, 
                  open, high, low, close, volume, adj_close, updatetime)   
                  values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (tdate, sym, row[1], row[2], row[3],  
                   row[4], row[5], row[6], 
                   datetime.now(),))
            
#            try:
#                cur.execute("""insert into prices(tradedate, symbol, 
#                      open, high, low, close, volume, adj_close, updatetime)   
#                      values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
#                      (tdate, sym, row[1], row[2], row[3],  
#                       row[4], row[5], row[6], 
#                       datetime.now(),))
#                #print "Saved successfully"
#            except sqlite3.IntegrityError:
#                #print "Already existed"
#                pass

    conn.commit()
    print "finish loading %s" % sym

def updateIntradayPricesFromYahoo(dbo, sym):
    sym = sym.upper()
    conn = dbo.conn
    cur = dbo.cursor
    
    updtime = datetime.now()
    dq = yahooZoo()
    res = dq.queryIntraDay(sym)
    if res is None:
        print "no intraday price for [%s] today" % sym 
        return
    res = res.split("\n")
    res = [x.strip() for x in res]
    for row in res:
        if len(row)==0: continue
        row = row.split(',')
        tdate = nvldate(date.today(), DBDATEFMT)
        
        if row[3]=='N/A' or float(row[1]) == 0.0:
            logging.error("No intraday price for %s: %s" % (sym, res))  
            return
                        
        cur.execute(sql_check_price, (sym, tdate))
        if cur.fetchone() is not None:
            cur.execute(sql_del_price, (sym, tdate))            
        cur.execute("""insert into prices(tradedate, symbol, 
              open, high, low, close, volume, adj_close, updatetime)   
              values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
              (tdate, sym, row[3], row[4], row[5],  
               row[1], row[2], 0, 
               datetime.now(),))
    conn.commit()
    print "finish loading intraday %s" % sym

def getSymListFromFile(fname):
    try:
        f = open(fname, 'r')
    except IOError:
        print sys.exc_info()[0]
        print sys.exc_info()[1]
        return None             
    lines = f.read()
    f.close()
    slist = lines.split(",")
    return [s.strip() for s in slist]        

def getSymListFromDB(dbo, showActiveOnly=True):
    cur = dbo.cursor
    if showActiveOnly:    
        cur.execute('select symbol from security where sp500=1 order by symbol')
    else:
        cur.execute('select symbol from security order by symbol')
    rows = cur.fetchall()
    slist = []
    for r in rows:
        slist.append(str(r[0]))        
    return slist

def getSymList(dbo, showActiveOnly=True):
    slist = getSymListFromDB(dbo, showActiveOnly)
    
    wishlist = file('wishlist.txt').read().split(",")
    wishlist = [str(x).strip() for x in wishlist]
    #slist.extend(wishlist)
    logging.info("total symbols to be processed is: [%s]" % str(len(slist)+len(wishlist)))        
    return slist, wishlist
    
def dumpOHLCVtoCSV(fname, dbo, symbol, end=datetime.today(), duration='-1y'):
    symbol = symbol.upper()
    cur = dbo.cursor    
    begin = nvldate(addTime(end,duration),"%Y%m%d")
    endstr = nvldate(end,"%Y%m%d")
    f = open(fname, 'w')
    f.write("History prices for %s\n" % symbol)
    f.write("tradedate, open, high, low, close, volume\n")
    cur.execute("""select tradedate, open, high, low, close, volume 
                from prices where symbol=? and tradedate>=? and tradedate<=? order by tradedate""", (symbol, begin, endstr))
    rows = cur.fetchall()
    #logging.info("total records for [%s] are [%s]" % (symbol, str(len(rows))))
    for r in rows:
        r = list(r)
        r[0] = convert2etpdate(r[0],DBDATEFMT,'%m/%d/%Y')
        rstr = map(str, r)
        f.write(",".join(rstr))
        f.write('\n')
    f.close()

def runsql(dbo, sql):
    conn = dbo.conn
    cur = dbo.cursor    
    cur.execute(sql)
    conn.commit()

def queryTable(dbo, tname, where=""):
    cur = dbo.cursor
    ## Do this instead
    #symbol = ('IBM',)
    #cur.execute('select * from prices where symbol=?', symbol)
    #print cur.fetchone()
    #print "--------"
        
    cur.execute('select * from %s' % tname + where)
    rows = cur.fetchall()
    logging.info("total records in [%s] are [%s]" % (tname, str(len(rows))))
    l1 = []
    for r in rows:
        logging.debug(str(r))
        l1.append(r[0])
    list2CSV("queryRes.csv", l1)

def dailyUpdate(dbo):
    f = open("records", 'a+')
    lines = f.readlines()
    lines  = [str(x)[:-1] for x in lines]
    lines = filter(lambda x:len(x)>0, lines)
    last = lines[-1] if len(lines)>0 else None
    today = nvldate(datetime.today())
    print "Last date in record: [%s] -- today: [%s]" % (last, today)
    slist, wishlist = getSymList(dbo)         
    slist.extend(wishlist)        
    if last!=today:
        updatePrices(dbo, slist, "EOD")
        #assignThreads(slist, "EOD")         
        f.write(today + "\n")
    f.close()
    if isBusinessDay(datetime.today()):
        updatePrices(dbo, slist, "INTRADAY")
        #assignThreads(slist, "INTRADAY")

def updatePrices(dbo, slist, type):
    if type=='EOD':
        func = updatePricesFromYahoo
    elif type=='INTRADAY':
        func = updateIntradayPricesFromYahoo
    else:
        raise "invalid price type %s" % type
    
    for sym in slist:
        func(dbo, sym)
        
def assignThreads(slist, type):
    numThreads = 3
    bsize = len(slist)
    symPerThreads = int(bsize/numThreads)
    
    threadlist=[]
    for i in range(numThreads):
        if i < numThreads-1:
            mpThread = slist[i*symPerThreads:(i+1)*symPerThreads]
        else:
            mpThread = slist[i*symPerThreads:]
            
        logging.debug("number of symbol: [%d] in thread [%d]" % (len(mpThread),i))
                    
        t = updatePriceThread(mpThread,i,type)
        t.start()
        threadlist.append(t)
    
    for x in threadlist:
        x.join()
    
class updatePriceThread(Thread):
    def __init__(self, mps, numThread, type):
        Thread.__init__(self)        
        self.mps=mps
        self.numThread=numThread
        self.type = type
    
    def run(self):
        self.dbo=dao()
        logging.debug("starting updatePriceThread Thread [%d]" % (self.numThread))
        cnt=0            
        if self.type=='EOD':
            for sym in self.mps:
                cnt+=1
                updatePricesFromYahoo(self.dbo, sym)
                #logging.debug("Thread [%d] is processing [%s], [%d] symbols have been processed" % (self.numThread, sym, cnt))
        elif self.type=='INTRADAY':
            for sym in self.mps:
                cnt+=1
                updateIntradayPricesFromYahoo(self.dbo, sym)
                #logging.debug("Thread [%d] is processing [%s], [%d] symbols have been processed" % (self.numThread, sym, cnt))            
        else:
            logging.error('unknow type for updatePriceThread [%s]' % str(self.type))
            
        logging.debug("finish updatePriceThread at Thread [%d]" % (self.numThread))
        try:
            self.dbo.close()
        except:
            pass
                
class OHLCV:
    def __init__(self, dbo):
        self.cursor = dbo.cursor
        self.clear()            

    def clear(self):
        self.dates = []
        self.open = []
        self.high = []
        self.low = []
        self.close = []
        self.volume = []

    def getclose(self):
        return (self.dates, self.close)

    def getOHLCV(self):
        return (self.dates, self.open, self.high, self.low, self.close, self.volume)
    
    def queryOHLCV(self, symbol, end=datetime.today(), duration='-1y'):
        symbol = symbol.upper()
        self.clear()
        self.symbol = symbol
        begin = nvldate(addTime(end,duration),"%Y%m%d")
        endstr = nvldate(end,"%Y%m%d")
        self.cursor.execute('select tradedate, open, high, low, close, volume from prices where symbol=? and tradedate>=? and tradedate<=? order by tradedate', (symbol, begin, endstr))
        rows = self.cursor.fetchall()
        #logging.info("total records for [%s] between [%s] -- {%s] are [%s]" % (symbol, begin, endstr, str(len(rows))))
        for r in rows:
            #logging.debug(str(r))
            r = list(r)
            self.dates.append(r[0])
            self.open.append(r[1])
            self.high.append(r[2])
            self.low.append(r[3])
            self.close.append(r[4])
            self.volume.append(r[5])            
        return (self.dates, self.open, self.high, self.low, self.close, self.volume)
    
    def queryClosePrice(self, symbol, end=datetime.today(), duration='-1y'):
        symbol = symbol.upper()
        self.clear()
        self.symbol = symbol
        begin = nvldate(addTime(end,duration),"%Y%m%d")
        endstr = nvldate(end,"%Y%m%d")
        self.cursor.execute('select tradedate, close from prices where symbol=? and tradedate>=? and tradedate<=? order by tradedate', (symbol, begin, endstr))
        rows = self.cursor.fetchall()
        #logging.info("total records for [%s] between [%s] -- {%s] are [%s]" % (symbol, begin, endstr, str(len(rows))))
        for r in rows:
            #logging.debug(str(r))
            r = list(r)
            self.dates.append(r[0])
            self.close.append(r[1])            
        #return (self.dates, self.close)

    def queryThisClosePrice(self, symbol, today):
        symbol = symbol.upper()
        todaystr = nvldate(today,"%Y%m%d")
        self.cursor.execute('select tradedate, close from prices where symbol=? and tradedate=?', (symbol, todaystr))
        row = self.cursor.fetchone()
        if row is not None and len(row)>0:
            return row[1]
        return None

def test_fft():
    length = 100
    l1 = arange(-1*length,length,1)    
    #l2 = sin(l1)+sin(2*l1)
    l2 = l1**2
    #l2 = zeros(2*length);  l2[:length]=1
    b = fft(l2)    
        
    title('FFT example')
    grid(True)
    plot(l1,abs(concatenate((b[length:],b[:length]))))
    show()
        
def price_fft(po):    
    d1, l1 = po.getclose()
    length = len(l1)
    if length % 2 == 1:
        l1 = l1[1:]
        length -= 1
            
    l2 = l1 - average(l1)
    #list2CSV("1.csv", l2)
        
    b = fft(l2)        
    length = int(length/2)    
    f=arange(-length,length,1)
    
    title('FFT for %s' % po.symbol)
    grid(True)
    plot(f,abs(concatenate((b[length:],b[:length]))))
    show()
    
def dailychange(po):
    d1, l1 = po.getclose()
    l2 = []
    length = len(l1)
        
    for i in range(1, length):
        l2.append((l1[i]-l1[i-1])*100.0/l1[i-1])

    #d2 = linspace(1,length-1,length-1)
    d2 = julian(d1[1:])
    
#    for i in range(1, length-1): 
#        print d1[i], d2[i]

    l3 = []
    for i in range(1, length-1):
        if l2[i-1]==0:
            l3.append(l3[-1])
        else:
            l3.append((l2[i]-l2[i-1])/l2[i-1])
    d3 = d2[1:]
    
    f = open("daily-change.csv", "w")
    for i in range(len(d3)):
        f.write("%s,%f,%f,%f\n" %(tranformDateFormat(d1[i+2]), l1[i+2], l2[i+1], l3[i]))
    f.close()

    title('Percentage daily change for %s' % po.symbol)    
    plot(d2,l2,'g.-')
    plot(d3,l3,'r.-')
    legend(['change',])    
    show()
        
    return l2

def calATR(po, optInTimePeriod = 14):    
    (d1, o, h, l, c, v) = po.getOHLCV()
    retCode, begIdx, result = TA_ATR(0, len(c)-1, h, l, c, optInTimePeriod)
    assert(retCode, TA_SUCCESS)
    #print len(c), begIdx, len(result)
#    fresult = [result[0]]*begIdx
#    fresult.extend(result)

    c = c[begIdx:]
    d1 = d1[begIdx:]
    print len(c), begIdx, len(result)
    
    d2 = julian(d1, fmt="%Y%m%d")
    title('ATR Example for %s' % po.symbol)
    #plot(d2,c,'g.-')
    plot(d2,result,'r.-')    
    legend([po.symbol, 'ATR 14'])    
    show()

def calMA(po):    
    d1, c = po.getclose()
    retCode, begIdx20, result20 = TA_MA(0, len(c)-1, c, 20, TA_MAType_SMA)
    assert(retCode, TA_SUCCESS)

    retCode, begIdx200, result200 = TA_MA(0, len(c)-1, c, 200, TA_MAType_SMA)
    assert(retCode, TA_SUCCESS)

    c = c[begIdx200:]
    d1 = d1[begIdx200:]
    result20 = result20[begIdx200-begIdx20:]
    
    #print len(c), len(d1), len(result20), len(result200)
    
    d2 = julian(d1, fmt="%Y%m%d")
    title('MA Example for %s' % po.symbol)
    plot(d2,c,'g.-')
    plot(d2,result20,'r.-')    
    plot(d2,result200,'b.-')
    legend([po.symbol, 'MA 20', 'MA 200'])    
    show()

def calCandle(po):
    (d1, o, h, l, c, v) = po.getOHLCV()
    # TA_CDLDOJI   
    retCode, begIdx, result = TA_CDLHARAMI(0, len(c)-1, o, h, l, c)
    assert(retCode, TA_SUCCESS)
    for d, p in zip(d1, result):
        if p!=0: print d, p
                                                    
def regression(l1, l2):
    size = min(len(l1), len(l2))
    x = l1[:size]
    y = l2[:size]
    (a_s,b_s,r,tt,stderr)=stats.linregress(x,y)
    #print a_s, b_s,r,tt,stderr    
    return r
    
#    (ar,br)=polyfit(x,y,1)
#    xr=polyval([ar,br],x)
#    #compute the mean square error
#    err=sqrt(sum((xr-y)**2)/size)
#    print ar, br, err
#
#    #(ar,br,cr)=polyfit(x,y,2)
#    #xr=polyval([ar,br,cr],x)
#    coefs=polyfit(x,y,5)
#    xr=polyval(coefs,x)
#    #compute the mean square error
#    err=sqrt(sum((xr-y)**2)/size)
#    print coefs, err    

def correlation(po_target, po_ref):
    cutoff_r = 0.9    
    
    d1, l1 = po_target.getclose()
    d2, l2 = po_ref.getclose()
    final = {}
    rmax = 0
    len1 = len(l1)
    len2 = len(l2)
    lend = len2
    interval = 1
    count = 20
    
    while lend-len1>0:
        lend = len2-count
        r = regression(l1, l2[lend-len1:lend])
        end = d2[lend-1]
        print end, r
        if r > rmax: 
            rmax = r
            endmax = end
            lendmax = lend
        if r>cutoff_r: final[end] = r
        count+=interval
    
    print endmax, rmax
    print final
    drawRegression(l1, l2[lendmax-len1:lendmax])

def drawRegression(x, y):
    (a_s,b_s,r,tt,stderr)=stats.linregress(x,y)
    #print a_s, b_s,r,tt,stderr
    yr = [elem*a_s + b_s for elem in x]

    #matplotlib ploting
    title('Regression Example')
    plot(x,y,'g.')
    plot(x,yr,'r.')    
    legend(['original', 'regression'])    
    show()

def runcorrelation(dbo, sym1, sym2, end=datetime.today(), duration='-3m', cutoff = '-10y'):
    po_target = OHLCV(dbo)
    po_target.queryClosePrice(sym1, end=end, duration=duration)    
    po_ref = OHLCV(dbo)
    po_ref.queryClosePrice(sym2, end=end, duration=cutoff)    
    correlation(po_target, po_ref)
    
def main():
    dbo = dao()    
    #runsql(dbo, sql_del_security % 'BF/B')
    #runsql(dbo, sql_del_one_price % ('TEK', '20080812'))

    #purgeDB(dbo)    
    #readSymListToDB(dbo, 'SP500.txt', True)
    #queryTable(dbo, 'security')
    #queryTable(dbo, 'prices', " where tradedate='20080724'")    
    #queryTable(dbo, 'prices', " where symbol='TEK' and tradedate='20080812'")
    
    #dailyUpdate(dbo)
    #updateIntradayPricesFromYahoo(dbo, "C")
    #getSymList(dbo)
    #sym = "^RUT"
    #dumpOHLCVtoCSV("%s_prices.csv" % sym, dbo, sym)

    po = OHLCV(dbo)
    po.queryClosePrice('^GSPC', end=datetime.today(), duration='-1y')
    po.queryOHLCV('SPY', end=datetime.today(), duration='-1y')        
    dailychange(po)
    #price_fft(po)
    #calATR(po)
    #calMA(po)
    #calCandle(po)
    
    #runcorrelation(dbo, '^GSPC', '^GSPC')    
    dbo.close()  
    
if __name__ == "__main__":
    logging.info("program starts at: " + time.strftime('%X %x %Z'))
    t1 = time.time()    
    main()
    t2 = time.time()    
    logging.info('program took %0.3f s' % ((t2-t1)))
    logging.info("program ends at: " + time.strftime('%X %x %Z'))