from testsqlite3 import OHLCV, getSymList, dailyUpdate
from config import *
import sqlite3
from TaLib import *
from businessday import *
from sector import findSectorFromSymbol
from operator import itemgetter

class Screener:
    def __init__(self, dbo):
        self.dbo = dbo
        self.cursor = dbo.cursor
        self.po_lst = []
        self.sects = findSectorFromSymbol(dbo)

    def getSymbols(self):
        slist, self.wishlist = getSymList(self.dbo)
        slist.extend(self.wishlist)
        return slist
    
    def getindustry(self, symlist):
        for s in symlist:
            try:
                logging.info("%s: %s" % (s, str(self.sects[s])))
            except:
                logging.error("Not industry info for: %s" % s)
            
    def load(self, end=datetime.today(), duration='-1y'):
        endstr = nvldate(end, "%Y%m%d")
        logging.info("Analysis for %s" % endstr)
        slist = self.getSymbols()        
        for sym in slist:
            #print "loading %s" % sym
            po = OHLCV(self.dbo)
            po.queryOHLCV(sym, end, duration)
            if po.dates:
                if po.dates[-1]==endstr:
                    self.po_lst.append(po)
                else:
                    #raise MyError, "Last price for %s is on %s" % (sym, po.dates[-1])
                    logging.error("Last price for %s is on %s" % (sym, po.dates[-1]))                        
            
        self.size = len(self.po_lst) 
    
    def abnormalVol(self):
        threshold = 1.5
        self.abvol = []
        self.abchange = {}
        self.volchange = {}
        for po in self.po_lst:
            tv = list(po.volume)
            try:
                retCode, begIdx20, result20 = TA_MA(0, len(tv)-1, tv, 20, TA_MAType_SMA)
                #assert(retCode, TA_SUCCESS)
                        
                if tv[-1]/result20[-1]>threshold and tv[-1]/tv[-2]>threshold:
                    logging.debug("AbnormalVol: %s: today volume: %f--yesterday volume: %f--EMA(20): %f" % (po.symbol, tv[-1], tv[-2], result20[-1]))
                    change = round(100*(po.close[-1]-po.close[-2])/po.close[-2],2)
                    volchange = round(tv[-1]/result20[-1],2)
                    self.abvol.append(po.symbol)
                    self.abchange[po.symbol]=change 
                    self.volchange[po.symbol]=volchange
                    
                #print "checking abnormalVol for %s" % po.symbol
                
            except:
                logging.error("abnormalVol wrong with %s" % po.symbol)
                logging.error(sys.exc_info()[0])
                logging.error(sys.exc_info()[1])
        self.abchange = sorted(self.abchange.items(), key=itemgetter(1), reverse=True)
        logging.info("Abnormal Volume List [%d]:" % (len(self.abvol)))
        for x, y in self.abchange:
            try:
                logging.info("%s: price change %0.2f%%--volume change %0.2f : %s" % (x, y, self.volchange[x], self.sects[x]))
            except: pass
        
        return self.abvol

    def isCDL(self, cdlfunc, o, h, l, c):
        retCode, begIdx, result = cdlfunc(0, len(c)-1, o, h, l, c)
        assert(retCode, TA_SUCCESS)
        return result[-1]
        
    def candlePattern(self):
        patterns = {TA_CDLMORNINGSTAR:"Morning Star", 
                    TA_CDLPIERCING:"Piercing", 
                    TA_CDLHARAMI:"Harami",
                    TA_CDLEVENINGSTAR:"Evening Star", 
                    TA_CDLSHOOTINGSTAR:"Shotting Star", 
                    TA_CDLDARKCLOUDCOVER:"Dark Cloud Cover"
                    }
        
        bullish = [TA_CDLMORNINGSTAR, TA_CDLPIERCING, TA_CDLHARAMI]
        bearish = [TA_CDLEVENINGSTAR, TA_CDLSHOOTINGSTAR, TA_CDLDARKCLOUDCOVER]
        begidx = -20
        
        results = {}
        for p in patterns:
            results[p] = {}
            
        for po in self.po_lst:            
            try:
                o = po.open[begidx:-1]
                h = po.high[begidx:-1]
                l = po.low[begidx:-1]
                c = po.close[begidx:-1]
                
                for p in patterns:
                    res = self.isCDL(p, o, h, l, c)
                    if res: results[p].setdefault(res,[]).append(po.symbol)                    
            except:
                logging.error("candlePattern wrong with %s" % po.symbol)
                logging.error(sys.exc_info()[0])
                logging.error(sys.exc_info()[1])

        logging.info("Bullish patterns:----------")
        for p in bullish:
            logging.info("%s List (%d): %s" % (patterns[p],len(results[p].get(100,[])),str(results[p])))

        logging.info("Bearish patterns:----------")
        for p in bearish:
            logging.info("%s List (%d): %s" % (patterns[p],len(results[p].get(-100,[])),str(results[p])))

    def newHighLow(self, timeframe = 50*5):
        """New high/New low. timeframe is the number of trading days"""         
        self.newhigh = []
        self.newlow = []
        for po in self.po_lst:
            try:
                tv = po.close[-1*timeframe:]
                tvdt = po.dates[-1*timeframe:]
                val = min(tv)
                valdt = tvdt[tv.index(val)]
                if val==tv[-1]:
                    logging.debug("New low: %s: lowest close: %f on [%s]--today close: %f" % (po.symbol, val, valdt, tv[-1]))
                    self.newlow.append(po.symbol)
                val = max(tv)
                valdt = tvdt[tv.index(val)]
                if val==tv[-1]:
                    logging.debug("New high: %s: highest close: %f on [%s]--today close: %f" % (po.symbol, val, valdt, tv[-1]))
                    self.newhigh.append(po.symbol)                                    
            except:
                logging.error("newHighLow wrong with %s" % po.symbol)
                logging.error(sys.exc_info()[0])
                logging.error(sys.exc_info()[1])
                    
        logging.info("new low List [%d]: %s" % (len(self.newlow), str(self.newlow)))
        self.getindustry(self.newlow)
        logging.info("new high List [%d]: %s" % (len(self.newhigh), str(self.newhigh)))
        self.getindustry(self.newhigh)
        
    def nrd(self):
        """Narrow ranged day"""
        threshold = 0.01
        self.nrdlist = []
        for po in self.po_lst:
            try:
                if abs(po.open[-1]-po.close[-1])/po.close[-1] < threshold:
                    logging.debug("NRD: %s: today open: %f--today close: %f" % (po.symbol, po.open[-1], po.close[-1]))
                    self.nrdlist.append(po.symbol)                
            except:
                logging.error("nrd wrong with %s" % po.symbol)
                logging.error(sys.exc_info()[0])
                logging.error(sys.exc_info()[1])
        logging.info("NRD List: %s" % str(self.nrdlist))
        return self.nrdlist

    def isDown(self, open, close, updown=1):
        threshold = 0.005
        if (open - close)*updown/close > threshold: return True
        else: return False
        
    def tripleDown(self):
        """price down big 3 days in a row"""
        self.tup = []
        self.tdown = []
        for po in self.po_lst:
            try:
                if self.isDown(po.open[-1], po.close[-1]) and self.isDown(po.open[-2], po.close[-2]) and self.isDown(po.open[-3], po.close[-3]):
                    logging.debug("TripleDown: %s: today open: %f--today close: %f" % (po.symbol, po.open[-1], po.close[-1]))
                    logging.debug("                today-1 open: %f--today-1 close: %f" % (po.open[-2], po.close[-2]))
                    logging.debug("                today-2 open: %f--today-2 close: %f" % (po.open[-3], po.close[-3]))
                    self.tdown.append(po.symbol)
                if self.isDown(po.open[-1], po.close[-1],-1) and self.isDown(po.open[-2], po.close[-2],-1) and self.isDown(po.open[-3], po.close[-3],-1):
                    logging.debug("TripleUp: %s: today open: %f--today close: %f" % (po.symbol, po.open[-1], po.close[-1]))
                    logging.debug("                today-1 open: %f--today-1 close: %f" % (po.open[-2], po.close[-2]))
                    logging.debug("                today-2 open: %f--today-2 close: %f" % (po.open[-3], po.close[-3]))
                    self.tup.append(po.symbol)                                                    
            except:
                logging.error("tripleDown wrong with %s" % po.symbol)
                logging.error(sys.exc_info()[0])
                logging.error(sys.exc_info()[1])
        logging.info("TripleDown List: %s" % str(self.tdown))
        logging.info("TripleUp List: %s" % str(self.tup))
        return self.tup, self.tdown 

    def adcheck(self, open, close):
        if open>close: return -1
        elif open<close: return 1
        elif open==close: return 0
        
    def adline(self):
        self.num_advance = 0
        self.num_decline = 0
        self.num_unch = 0
        for po in self.po_lst:
            try:
                if po.symbol in self.wishlist: continue
                #ogging.debug("ADline: %s: today open: %f--today close: %f" % (po.symbol, po.open[-1], po.close[-1]))
                res = self.adcheck(po.open[-1], po.close[-1])
                if res==1: self.num_advance+=1
                elif res==-1: self.num_decline+=1
                elif res==0:  self.num_unch+=1
            except:
                logging.error("adline wrong with %s" % po.symbol)
                logging.error(sys.exc_info()[0])
                logging.error(sys.exc_info()[1])
        tot = self.num_advance+self.num_decline+self.num_unch
        logging.info("Advance: %d, Decline: %d, Unch %d, Total: %d, Size: %d" % (self.num_advance, self.num_decline, self.num_unch, tot, self.size))
        return self.num_advance, self.num_decline, self.num_unch 

    def adlineHistory(self):
        self.adhist = {}
        julian_dates = julian(self.po_lst[0].dates, fmt="%Y%m%d")                            
        for d in range(len(julian_dates)):
            ad=0
            de=0
            unch=0
            for po in self.po_lst:
                try:
                    if po.symbol in self.wishlist: continue
                    res = self.adcheck(po.open[d], po.close[d])
                    if res==1: ad+=1
                    elif res==-1: de+=1
                    elif res==0: unch+=1
                except:
                    pass
            tot = ad+de+unch
            self.adhist[julian_dates[d]] = (ad, de, unch, tot, ad/float(de), (ad-de)/float(tot))            
        dict2CSV("adline_sp500.csv", self.adhist)

def abnormalVolHistory(end=date.today()):
    dbo = dao()    
    
    po = OHLCV(dbo)    
    po.queryClosePrice('^GSPC', end, duration='-1y')
    
    avhist = []     
    
    f = open("abnormalvolHistory.csv", "w")
    for i, d in enumerate(po.dates):        
        s = Screener(dbo)
        s.load(end=str2datetime(d, "%Y%m%d"))
        av = len(s.abnormalVol())
        avhist.append(av)
        print "%s,%s,%d\n" % (tranformDateFormat(d), str(po.close[i]), av)
        f.write("%s,%s,%d\n" % (tranformDateFormat(d), str(po.close[i]), av))
        
    f.close()            

def main():
    dbo = dao()
    #abnormalVolHistory()
    
    dailyUpdate(dbo)
    
    s = Screener(dbo)
    #s.load(end=str2datetime("20080808", "%Y%m%d"))
    s.load(addBusinessDay(date.today(), 0))    
    av = s.abnormalVol()
    #s.getindustry(av)
    nrd = s.nrd()
    tu, td = s.tripleDown()    
    print "abnormal volume: %d, NRD: %d, TripleDown: %d" % (len(av), len(nrd), len(td))
    print "abnormal volume : NRD -- %s" % str(multi_intersect(av, nrd))
    print "NRD : TripleDown -- %s" % str(multi_intersect(nrd, td))
    print "abnormal volume : TripleDown -- %s" % str(multi_intersect(av, td))
    print "abnormal volume : TripleUp -- %s" % str(multi_intersect(av, tu))
    print "All together -- %s" % str(multi_intersect(av, nrd, td))
    
    s.adline()
    s.adlineHistory()
    s.newHighLow()    
    s.candlePattern()        
    dbo.close()        
    
if __name__ == "__main__":
    logging.info("program starts at: " + time.strftime('%X %x %Z'))
    t1 = time.time()    
    main()
    t2 = time.time()    
    logging.info('program took %0.3f s' % ((t2-t1)))
    logging.info("program ends at: " + time.strftime('%X %x %Z'))