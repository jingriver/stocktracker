from config import *

holidays = {}
oedays = {}

def addBusinessDay(dt, add):
    if add==0: return dt
    res = date(dt.year, dt.month, dt.day)
    dur = abs(add)
    step = int(add/dur)
    while dur>0:
        res = addDays(res, step)
        if isBusinessDay(res): dur-=1
    return res

def isBusinessDay(dt):
    if dt in holidays or calendar.weekday(dt.year, dt.month, dt.day)>4: return False
    else: return True

def getHolidays():
    f = open("../holiday_file/holiday.usd","r")
    line = f.readline()
    while len(line)>0:
        if line[0]!='#': 
                lstr = str(line).split("\t")
                bd = str2date(lstr[0], "%Y%m%d")
                holidays[bd] = lstr[1]
        line = f.readline()    
    
    f.close()

def getOEDays():
    today = date.today()
    year = today.year
    start = 1980
    end = year+1

    for y in range(start, end):
        for m in range(1,13):
            month = calendar.monthcalendar(y, m)        
            if month[0][4]==0: oe = 3
            else: oe = 2
            d = date(y,m,month[oe][4])
            if d in holidays: d =  date(y,m,month[oe][3])            
            oedays[d] = d

def getThisOEDay(y, m):
    month = calendar.monthcalendar(y, m)        
    if month[0][4]==0: oe = 3
    else: oe = 2
    d = date(y,m,month[oe][4])
    if d in holidays: d =  date(y,m,month[oe][3])            
    return d

getHolidays()
getOEDays()


if __name__ == "__main__":        
    #print holidays
    #print oedays
    print addBusinessDay(date.today(), -1)
