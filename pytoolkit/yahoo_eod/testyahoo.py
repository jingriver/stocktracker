from testHttp import *

class yahooZoo():
    def __init__(self):
        self.conn = httpConnection()
        #history:                
        self.urltemplate = "http://ichart.finance.yahoo.com/table.csv?s=RVBD&a=00&b=2&c=1990&d=09&e=29&f=2007&g=d&ignore=.csv"
        #date-open-high-low-close-adjusted close
        
        #intrday
        self.urlintradaytemp = "http://quote.yahoo.com/d/quotes.csv?s=^DJI&f=sl1vohgd1"
        #intraday: http://quote.yahoo.com/d/quotes.csv?s=USG&f=sl1vohgd1
        #symbol--last price--volumn--open--high-low--date 
        #s--l1--v--o--h--g--d1        
        
    def constructURL(self, symbol, goBackYears, endDate):
        if endDate.upper()=='TODAY':
             today = datetime.today()
             (ed, em, ey) = (today.day, today.month-1, today.year)
             (sd, sm, sy) = (ed, em, ey-goBackYears)
        else:
            sdate = str2datetime(startDate,'%Y%m%d')
            edate = str2datetime(endDate,'%Y%m%d')
            (sd, sm, sy) = (sdate.day, sdate.month-1, sdate.year)
            (ed, em, ey) = (edate.day, edate.month-1, edate.year)                                        
        url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv" % (symbol, sm, sd, sy, em, ed, ey)
        #logging.debug(url)
        return url
        
    def queryHistory(self, sym, goBackYears=1, endDate="TODAY"):
        url = self.constructURL(sym, goBackYears, endDate)
        return self.query(url)
        
    def query(self, url):
        try:
            html = self.conn.getHtml(url)
            #logging.debug(html)
        except:
            return None
        return html
    
    def queryIntraDay(self, sym):
        #intrday
        url = "http://quote.yahoo.com/d/quotes.csv?s=%s&f=sl1vohgd1" % sym
        return self.query(url)
 
if __name__ == '__main__':                            
    yahooZoo().query('BF/B')