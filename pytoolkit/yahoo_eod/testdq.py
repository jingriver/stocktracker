import sys
from dataquery.DQPy import DQTimeSeries, DQContext, DQPy
from config import *

class dqzoo:
    def __init__(self, sid="O066144", dqserver="dataquery-dev.ny.jpmorgan.com:6555"):
        self.conn = DQPy(sid, dqserver)
         
    def getExpressList(self, symbol):
        return ['DB(QA,%s,PRICE,OPEN)' % symbol,
                    'DB(QA,%s,PRICE,HIGH)' % symbol,
                    'DB(QA,%s,PRICE,LOW)' % symbol,
                    'DB(QA,%s,PRICE,CLOSE)' % symbol,
                    'DB(QA,%s,PRICE,VOLUME)' % symbol,]
    
    def setContext(self, startDate="TODAY-5BD", endDate="TODAY"):
#        calendar = 'CAL_WEEKDAYS'
#        frequency = 'FREQ_DAY'
#        naCode = 'NA_NOTHING'
#        freqConv = 'CONV_LASTBUS_ABS'
        self.dqcon = DQContext(startDate, endDate, "FREQ_DAY", "CONV_LASTBUS_ABS", "NA_NOTHING", "CAL_WEEKDAYS")
    
    def queryHistory(self, sym, startDate="TODAY-5BD", endDate="TODAY"):
        self.setContext(startDate, endDate)
        exprList = self.getExpressList(sym)
        ts = self.conn.getTimeSeries(exprList, self.dqcon)
        logging.info(str(ts.InfoMessage))
        ts.NAtoNone()
        return self.parseTS(sym, exprList,ts)

    def parseTS(self, sym, exprList, ts):
        res = []
        i = 0
        for dt in ts.dates:            
            j = 0
            rtmp = [dt, sym]
            for exp in exprList:
                rtmp.append(ts.values[j][i])
                j += 1
            i += 1
            res.append(rtmp)
        return res
        
if __name__ == "__main__":
    dq = dqzoo()
    slist = ['VIA', 'VIA/B']        
    for sym in slist:
        logging.debug(str(dq.queryHistory(sym, "TODAY-5BD")))