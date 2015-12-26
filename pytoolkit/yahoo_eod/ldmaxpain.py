from businessday import *
from testHttp import *
from TableParse import *
from config import *
from testsqlite3 import OHLCV
        
#before Jul, 2004, include Jul, 2004
"http://www.iqauto.com/cgi-bin/viewarc.pl?cd=a/aapl/0010/001020"
#Begin from Aug, 2004
"http://www.iqauto.com/cgi-bin/hist.pl?cd=a/aapl/0010/001020"

urltemplate1 = "http://www.iqauto.com/cgi-bin/viewarc.pl?cd=%s/%s/%02d%02d/%s"
urltemplate2 = "http://www.iqauto.com/cgi-bin/hist.pl?cd=%s/%s/%02d%02d/%s"    

class MaxPainLoader:
    
    def __init__(self):
        self.conn = httpConnection()
        dbo = dao()
        self.po = OHLCV(dbo)        
    
    def loadMP(self, symbol="aapl", startyear=2000):        
        self.maxpain={}
        self.getPrices(symbol, startyear)
                    
        for y in range(0,4):
            for m in range(1,13):
                oe = getThisOEDay(y+startyear, m)
                self.loadThisMP(symbol, y, m, oe, 1)
                
        for m in range(1,8):
            oe = getThisOEDay(2004, m)
            self.loadThisMP(symbol, 4, m, oe, 1)
    
        for m in range(8,13):
            oe = getThisOEDay(2004, m)
            self.loadThisMP(symbol, 4, m, oe, 2)
    
        for y in range(5,9):
            for m in range(1,13):
                oe = getThisOEDay(y+startyear, m)
                self.loadThisMP(symbol, y, m, oe, 2)
        
        dict2CSV("maxpain/%s_maxpain.csv" % symbol, self.maxpain)                
        logging.info(self.maxpain) 
        return self.maxpain

    def getPrices(self, symbol, startyear):
        end = date.today()
        ey = end.year
        duration = ey-startyear+1
        self.po.queryClosePrice(symbol, end, "-%dy" % duration)
        self.closePrices = dict(zip(self.po.dates, self.po.close))
                
    def loadThisMP(self, symbol, oy, om, thisday, template=1):
        symbol = symbol.lower()
        urltemplate = urltemplate1 if template==1 else urltemplate2
        url = urltemplate % (symbol[0], symbol, oy, om, nvldate(thisday, "%y%m%d"))
        thismp = self.parseTable(url)
        if thismp is not None and thismp>0:
            p = self.closePrices.get(nvldate(thisday, "%Y%m%d"), None)                            
            self.maxpain[thisday] = (thismp, p)
    
    def parseTable(self, url):
        logging.debug(url)
        try:    
            html = self.conn.getHtml(url)
        except urllib2.URLError:
            return None
        table = parse(html)
        for t in table:        
            if len(t)>0 and t[0]=='Maximum Pain Point:':
                logging.debug(t[1])
                return t[1]
        return None
    
if __name__ == '__main__':                
    m = MaxPainLoader()
    slist = ('QQQQ', 'SPY', 'IWM', 'AAPL', 'JPM')
    for s in slist:
        m.loadMP(s)
    #m.loadMP("C")
        

