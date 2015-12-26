dict_commission = {"fidelity-meng":20,"fidelity-chao":20,
                   "firstrade-meng":7,"firstrade-chao":7,
                   "tradeking":5}
class trade:
    CONS_DATE = 0
    CONS_BS = 1
    CONS_SYMBOL = 2
    CONS_SHARES = 3
    CONS_PRICE = 4
    CONS_ACCOUNT = 5
    
    def __init__(self, record):
        rstr = record.split(",")
        self.rstr = rstr
        self.date = rstr[0]
        self.bs  = rstr[1]
        self.symbol = rstr[2]
        self.shares = rstr[3] 
        self.price = rstr[4]
        self.account = rstr[5]        
    
    def __str__(self):
        return ",".join(self.rstr)

def aggregate(trades, i):
    dict = {}    
    for t in trades:
        dict.setdefault(t.rstr[i], []).append(t)    
    return dict

def calPLPerAccount(trades, commission=0.0):
    pl = 0.0
    shares = 0
    for x in trades:
        s = float(x.shares)
        if x.bs.upper() == 'BUY': s = s  
        elif x.bs.upper() == 'SELL': s = -s
        else: raise "invalid B/S type [%s]" % x.bs
        pl+= float(x.price)*s*(-1)-commission
        shares += s
        
    return (pl, shares)

def calTotalPL(trades):           
    dict_acc = aggregate(trades, trade.CONS_ACCOUNT)
    dict_acc_pl = {}
    dict_acc_hold = {}
    for x in dict_acc:
        dict_acc_hold[x] = {}
        pl_acc = 0.0
        acc = dict_acc[x]        
        dict_sym = aggregate(acc, trade.CONS_SYMBOL)        
        for s in dict_sym:            
            pl, sh = calPLPerAccount(dict_sym[s], dict_commission[x])
            if sh>0: dict_acc_hold[x][s] = (pl, sh)
            else: pl_acc+=pl
        
        dict_acc_pl[x] = pl_acc

    return dict_acc_pl, dict_acc_hold

def outputPL(dict_acc_pl, dict_acc_hold):
    for x in dict_acc_pl:
        print "Account---%s" % x
        print "Total profit: %.2f" % dict_acc_pl[x]
        print "Still holding: %s" % str(dict_acc_hold[x])    
        print "------------------------------"
            
def readfile():
    f = open("trades.csv", "r")
    lines = f.read().split("\n")[1:]
    lines = filter(lambda(x):len(x)>0, lines)
    
    trades = []
    for l in lines:
        trades.append(trade(l))
    
    dict1, dict2 = calTotalPL(trades)
    outputPL(dict1, dict2)
        
if __name__ == "__main__": 
    readfile()   