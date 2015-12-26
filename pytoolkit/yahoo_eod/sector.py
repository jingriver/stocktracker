from config import *
from testHttp import *
from TableParse import *
import re
import sqlite3
from testsqlite3 import purge_industry_ref, getSymList, downloadSymListToDB

"""Sector: Technology >  Industry: Semiconductors
url = http://finance.google.com/finance?q=WFR&hl=en

Sector summary
Sector     Change     % down / up
Basic Materials     -1.94%     
Capital Goods     -1.34%     
Conglomerates     +0.19%     
Cons. Cyclical     +1.11%     
Cons. Non-Cyclical     -0.45%     
Energy     -1.02%     
Financial     +0.30%     
Healthcare     -0.14%     
Services     -0.20%     
Technology     -1.64%     
Transportation     -0.66%     
Utilities     -1.32%

Subcategories
<div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=57851646">Communications Equipment</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=64708745">Computer Hardware</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=62334177">Computer Networks</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=52540027">Computer Peripherals</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=55018533">Computer Services</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=51836946">Computer Storage Devices</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=59573548">Electronic Instr. & Controls</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=62382400">Office Equipment</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=60142938">Scientific & Technical Instr.</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=55119621">Semiconductors</a></div><div style="float:left;width:15em;padding:2px 6px 2px 2px;overflow:hidden;white-space:nowrap;"><a href="?catid=54399928">Software & Programming</a></div>

Symbol
<div class=item>Sector:&nbsp;<a id=sector href=?catid=66529330 >Technology</a>&nbsp;&gt;&nbsp;
Industry:&nbsp;<a href=?catid=55119621 >Semiconductors</a>
</div>     
"""
        
url = "http://finance.google.com/finance"
url_google = "http://finance.google.com"
url_symbol = "http://finance.google.com/finance?q="

sector_begin = "Sector summary"
sector_end = "Trends"
subsector_begin = "Subcategories"
subsector_end = "Companies"
symbol_begin = "Sector:"
symbol_end = "div"
ahref = re.compile(r"""<a.* href=(.*)>(.+)</a>""")
hlink = re.compile(r"""<a.+>.+</a>""")

conn = httpConnection()
htmlparser = LinksExtractor()
                                
def getMainSectorFromWeb(url):
    try:    
        html = conn.getHtml(url)
    except urllib2.URLError:
        return None
    begin = html.find(sector_begin)
    end = html.find(sector_end, begin)    
    sector = html[begin:end]
    #print begin, end, sector
    table = parse_but_href(sector)
    hrefs = ""        
    for t in table:
        if len(t)>0 and t[0]!="" and href_tag.search(t[0]):
            hrefs += t[0]        
                        
    htmlparser.feed(hrefs)
    htmlparser.close()
    return htmlparser.get_links()

def getSubSectorFromWeb(sectors):
    names = {}
    for x in sectors:
        name = x[0].strip()
        url = url_google+x[1] 
        html = conn.getHtml(url)        
        names[name] = parseSubSector(name, html)
    logging.info(names) 
    return names
        
def parseSubSector(name, html):
    begin = html.find(subsector_begin)
    end = html.find(subsector_end, begin)    
    sector = html[begin:end]
    table = parseDiv(sector)
    tname = [parseHref(x)[1].strip() for x in table]    
    return tname

def parseHref(s):
    m = ahref.search(s)
    return m.groups()

def update_industry_ref(dbo):
    s = getMainSectorFromWeb(url)
    names = getSubSectorFromWeb(s)
        
    conn = dbo.conn
    cur = dbo.cursor
    purge_industry_ref(dbo)
    try:
        for x in names.keys():            
            cur.execute("""insert into industry_ref(industry_name, parent_id)            
                  values (?, ?)""", (x, 0,))
            conn.commit()
        cur.execute("select * from industry_ref")
        sectors = {}
        for x in cur:
            sectors[str(x[1])] = x[0]
        
        for x in sectors:
            subsectors = names[x]
            for ss in subsectors:
                cur.execute("""insert into industry_ref(industry_name, parent_id)            
                  values (?, ?)""", (ss, sectors[x],))
                conn.commit()
            
    except sqlite3.IntegrityError:
        #print "Already existed"
        pass    

g_sectors = {}
g_sector_dict = {}
g_mainsector = {}
g_mainsectorname = {}

class catagory():
    def __init__(self, s):
        self.id = s[0]
        self.name = str(s[1])
        self.parent = s[2]
    
    def __str__(self):
        return "%d---%s---%d" % (self.id, self.name, self.parent)  
    
def getglobalSectorsFromDB(dbo):
    cur = dbo.cursor
    cur.execute("select industry_id, industry_name, parent_id from industry_ref")
    for x in cur:
        g_sectors[x[0]] = catagory(x)
        
    for g in g_sectors.values():
        if g.parent==0:
            g_mainsector[g.id] = g
            g_mainsectorname[g.name] = g.id 
            g_sector_dict[g.id] = {}
        else: g_sector_dict.setdefault(g.parent, {})[g.name] = g.id

    #"Consumer/Non-Cyclical"  "Cons. Non-Cyclical" "Consumer Cyclical"    
    g_mainsectorname["Consumer/Non-Cyclical"] = g_mainsectorname["Cons. Non-Cyclical"]
    g_mainsectorname["Consumer Cyclical"] = g_mainsectorname["Cons. Cyclical"]    
#    for id in g_sector_dict:   
#        print g_mainsector[id]
#        print [str(x) for x in g_sector_dict[id]]
    
def updateSymbolSector(dbo):
    dbconn = dbo.conn    
    cur = dbo.cursor
    slist, wishlist = getSymList(dbo, showActiveOnly = False)
    for sym in slist:
        cur.execute("select industry_id from security where symbol='%s'" % sym)
        res= cur.fetchone()
        if res and res[0]: continue
        logging.info("updating industry info for %s" % sym)
        html = conn.getHtml(url_symbol+sym)
        begin = html.find(symbol_begin)
        end = html.find(symbol_end, begin)    
        sector = html[begin:end]
        match_obj = hlink.findall(sector)
        tname = [parseHref(x)[1].strip() for x in match_obj]
        #logging.info("%s %s" % (sym, tname))
        try:
            tid = g_mainsectorname[tname[0]]
            tsub_id = g_sector_dict[tid][tname[1]]            
            cur.execute("update security set industry_id=?, sub_industry_id=? where symbol=?", (tid, tsub_id, sym))
            dbconn.commit()            
            logging.info("%s %d %d" % (sym, tid, tsub_id))
        except KeyError:
            logging.error("No such sectors: %s %s" % (sym, tname))
        except IndexError:            
            cur.execute("delete from security where symbol='%s'" % sym)
            cur.execute("delete from prices where symbol='%s'" % sym)
            dbconn.commit()
            logging.error("Its' not a stock: %s %s" % (sym, tname))

def updateSecurityTable(dbo):
    downloadSymListToDB(dbo, clearFirst = False)
    getglobalSectorsFromDB(dbo)
    updateSymbolSector(dbo)
                            
def syncPriceTable(dbo):
    from sets import Set
    dbconn = dbo.conn    
    cur = dbo.cursor    
    cur.execute("select symbol from security")
    s1 = cur.fetchall()
    s1 = Set([x[0] for x in s1])
    print len(s1)

    cur.execute("select distinct symbol from prices")
    s2 = cur.fetchall()
    s2 = Set([x[0] for x in s2])
    print len(s2)
    
    s3 = s2.difference(s1)
    print s3
            
def findSectorFromSymbol(dbo):
    getglobalSectorsFromDB(dbo)
    res = {}
    compose = {}
    cur = dbo.cursor
    cur.execute("select symbol, industry_id, sub_industry_id from security where sp500=1")
    
    cnt = 0
    for x in cur:
        cnt+=1
        res[str(x[0])] = (g_sectors[x[1]].name,g_sectors[x[2]].name)
        compose.setdefault(g_sectors[x[1]].name,[]).append(str(x[0]))
        #logging.debug("%s %s" % (str(x[0]), str(res[str(x[0])])))
#    for s in compose:
#        logging.info("%s %0.2f%%" % (s, len(compose[s])*100.0/cnt))        
    return res

if __name__ == '__main__':
    dbo = dao()                
    #update_industry_ref(dbo, names)    
    #findSectorFromSymbol(dbo)
    updateSecurityTable(dbo)
    #syncPriceTable(dbo)