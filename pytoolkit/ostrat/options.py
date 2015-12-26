from config import *
from PyQt4 import QtCore,QtGui
import etp
import bawopt

url = "http://snow.ny.jpmorgan.com:5710/etp"
#url_bretton = "http://bretton.ny.jpmorgan.com:8011/etp"
url_bretton = "http://bretton.ny.jpmorgan.com:7812/etp"
ETP_ERR = "<class 'etp.error'>"

class OptionColumn:
    MATURITY = 0
    EXPDATE = 1
    ETYPEDICT = {'E':'European', 'A':'American'}
    
    @classmethod
    def issueDate(cls, type):
        if type == 'S':
            return 4
        else:
            return -1
    
    @classmethod
    def cpsf(cls, type):
        if type == 'W':
            return 4
        elif type == 'S':
            return 6
        elif type in ('F', 'T'):
            return 5

    @classmethod
    def exerciseType(cls, type):
        if type == 'W':
            return 7
        elif type == 'S':
            return 9
        elif type in ('F', 'T'):
            return 8

    @classmethod
    def cpsfVal(cls, type):
        dict = {}
        if type =='W':
            dict['payer'] = 'Payer'
            dict['receiver'] = 'Receiver'
        elif type =='S':
            dict['C'] = 'Payer'
            dict['P'] = 'Receiver'
            dict['S'] = 'Straddle'
        else:
            dict['C'] = 'Call'
            dict['P'] = 'Put'
            dict['S'] = 'Straddle'
            #dict['F'] = 'F'
        return dict
            
class option(QtCore.QObject):
    TableHeader = ['Type', 
                   'Option Expiry', 
                   #'RF Rate', 
                   #'Forward Rate/Future Price',
                   'Strike', 
                   #'Notional', 
                   #'Premium', 
                   'Implied Vol(%)', 
                   'Delta(contracts)', 
                   'Gamma(per pt)', 
                   'Theta($)', 
                   'Vega($)',
		   #'Scenarios 1 beta(bp)',
		   #'Scenarios 1 alpha(bp)',
                   ]
    
    def __init__(self, tradeDate=None, exerciseType='E', 
                 expireDate=None, rfRate=5.0, fwdfut=5.0, strike=5.0, 
                 cpsf='P', premium=0.5, notional=100, 
                 volMatrix=0, matrixPrem=0, 
                 swapMat_contract=None, issueDate=None,
                 horizonDate=None, 
                 priceYield='P',
                 carry=0, yldalpha=0, yldbeta=1):
        
        QtCore.QObject.__init__(self)
        
        self.tradeDate = tradeDate
        self.prev_tradeDate = None
        self.exerciseType = exerciseType
        self.expireDate = expireDate
        self.rfRate=rfRate
        self.fwdfut=fwdfut
        self.strike=strike
        self.cpsf=cpsf
        self.premium=premium
        self.notional=notional
        self.volMatrix=volMatrix
        self.matrixPrem=matrixPrem
        self.swapMat_contract=swapMat_contract
        
        self.priceYield=priceYield
        self.horizonDate=horizonDate
        self.issueDate=issueDate
        
        self.carry=carry
        self.yldalpha=yldalpha
        self.yldbeta=yldbeta
        #self.pointValue = self.getPointValue()
        self.greekMultiply = 1000

        self.impliedVol = 0
        self.delta = 0
        self.gamma = 0
        self.theta = 0
        self.vega = 0
        
        #self.initAdjustableVarialbes()
        
        self.connect(self, QtCore.SIGNAL("CallBackFunc"), self.chkCallBackStatus)
        self.connect(self, QtCore.SIGNAL("OptionPLDone"), self.printAllPL)
                
    def getPointValue(self):
        return self.notional
    
    def __str__(self):
        vl = self.getTableValue()
        vl.append(self.swapMat_contract)
        vl.append(self.tradeDate)
        vl.append(self.horizonDate)
        vl.append(self.exerciseType)
        val = [str(x) for x in vl]
        return str(val)
    
    def toXML(self):
        inden1 = '\t'
        inden2 = '\t\t'        
        xmlStr = "%s<option type=\"%s\">\n" % (inden1, self.type)
        pvals = self.getProperties()
        i = 0
        for p in self.XMLproperties:
            xmlStr += '%s<%s>%s</%s>\n' % (inden2, p, pvals[i], p)
            i += 1
        xmlStr += inden1 + "</option>\n"
        return xmlStr
    
    def setTradeDate(self, tradeDate):
        self.tradeDate = tradeDate
                
    def setHorizonDate(self, horizonDate):
        self.horizonDate = horizonDate
            
    def validateSpreads(self):
        if self.swapMat_contract is None: # or self.notional==0:
            return False
        return True

    def isDataValid(self):
        res = True
        errmsg = ""
        if self.rfRate == 0:            
            errmsg += "--RF rate cannot be zero\n"
            res = False
        if self.strike == 0:
            errmsg += "--strike cannot be zero\n"
            res = False
        if self.premium == 0:
            errmsg += "--premium cannot be zero\n"
            res = False
        #if self.notional == 0:
        #    errmsg += "--notional amount cannot be zero\n"            
        #    res = False
        if self.swapMat_contract is None:
            errmsg += "--swap maturity/contract name cannot be none\n"
            res = False
        
        if not res:
            errmsg = "Invalid data for option [%s]\n %s" % (self.swapMat_contract, errmsg)
        return (res, errmsg)
                
    #entry point for calculate option PL
    def calculate(self, yldList=range(-100,110,10)):
        """calculate intermedia results, run only once
        """        
        if not self.validateSpreads():
            raise Error, "invalid Spreads"

        self.dt = 0.001
        self.volshift=0
                    
        self.yldList = yldList
        self.PLDict = {}
        
        self.calfwdfut()
        
    #called by chkCallBackStatus
    def calGreek(self):
        self.premium_i = IIf(self.cpsf=='F', self.fwdfut_i, self.premium_a)
        self.daysToExpire=getDays(self.tradeDate, self.expireDate)

        #logic here comes from bawoptxl.cpp 
        if self.cpsf in ('C','P','S'):
            self.impliedVol = bawopt.bimp(ord(self.cpsf), ord(self.exerciseType),
                    self.strike_i, 
                    self.daysToExpire/365.0, self.fwdfut_i, 
                    self.rfRate, self.carry,
                    self.premium_i, self.py_basis).prem_volat
            #print "fwdfut, strike, impliedVol [%f][%f][%f]" % (self.fwdfut_i, self.strike_i, self.impliedVol)
            baw = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                    self.strike_i, 
                    self.daysToExpire/365.0, self.fwdfut_i, 
                    self.rfRate, self.carry,
                    self.impliedVol, self.py_basis)
            premium = baw.prem_volat
            delta = baw.delta
                
            gamma_up = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                    self.strike_i, 
                    self.daysToExpire/365.0, self.fwdfut_i+0.01, 
                    self.rfRate, self.carry,
                    self.impliedVol, self.py_basis).delta
        
            gamma_down = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                    self.strike_i, 
                    self.daysToExpire/365.0, self.fwdfut_i-0.01, 
                    self.rfRate, self.carry,
                    self.impliedVol, self.py_basis).delta

            gamma = (gamma_up-gamma_down)*0.5*100.0
        
            prem_later = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                    self.strike_i, 
                    (self.daysToExpire-1.0)/365.0, self.fwdfut_i, 
                    self.rfRate, self.carry,
                    self.impliedVol, self.py_basis).prem_volat

            theta = prem_later - premium

            prem_hi_vol = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                    self.strike_i, 
                    self.daysToExpire/365.0, self.fwdfut_i, 
                    self.rfRate, self.carry,
                    self.impliedVol+1.0, self.py_basis).prem_volat

            vega = prem_hi_vol - premium
 
        elif self.cpsf=='F':
            self.impliedVol=0
            premium, delta, gamma, theta, vega = (0,1,0,0,0)

        self.delta = delta*self.notional
        self.gamma = gamma*self.notional
        self.theta = self.greekMultiply*theta*self.notional
        self.vega = self.greekMultiply*vega*self.notional
                
        self.daysToHorizon = getDays(self.horizonDate, self.expireDate)
#        print "greek [%f] [%f] [%f] [%f] [%f]" % (premium, delta, gamma, theta, vega)
        print "daysToHorizon [%f]" % self.daysToHorizon
            
    #first time to calPL
    #called by chkCallBackStatus
    def calPL(self):
        self.currentYldIdx = 0
        self.currentYld = self.yldList[self.currentYldIdx]
        logging.debug("yld is %f" % self.currentYld)
        self.calBondFut(self.currentYld)

    #continue calculate PL for each yield
    #emit QtCore.SIGNAL("OptionPLDone")
    def calNextPL(self):        
        self.currentYldIdx+=1
        if self.currentYldIdx<len(self.yldList):
            self.currentYld = self.yldList[self.currentYldIdx]
            logging.debug("yld is %f" % self.currentYld)
            #QtCore.QTimer.singleShot(100, self, self.calBondFut(self.currentYld))
            self.calBondFut(self.currentYld)
        else:
            self.emit(QtCore.SIGNAL("OptionPLDone"), (self,))
#            event = QtCore.QEvent(QtCore.QEvent.User)
#            print "send event %s" % str(event.type())
#            QtGui.QApplication.sendEvent(self.pf, event)

    def printAllPL(self, args):
        print "printAllPL " + str(args[0]) + ": " + str(self.PLDict)
        
    #slot func for QtCore.SIGNAL("bonds_finish")
    #last step to calculate PL for options
    #call calNextPL
    def getNetValue(self):
        if self.cpsf=='F':
            netValue = self.bonds
        else:
            #print "Bonds is [%f] for yld [%f]" % (self.bonds, self.currentYld)
            netValue = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                   self.strike_i, max(self.daysToHorizon, self.dt)/365.0, self.bonds, 
                   self.rfRate, self.carry, self.impliedVol+self.volshift, self.py_basis).prem_volat
                   
        #print "PL is [%f] for yld [%f]" % (netValue, self.currentYld)
        self.PLDict[self.currentYld] = netValue
        self.calNextPL()

#    def initAdjustableVarialbes(self):
#        self.adjustableVarialbes ={}
#        self.adjustableVarialbes['strike'] = self.strike
#        self.adjustableVarialbes['premium'] = self.premium
#    
#    def refreshAdjustableVarialbes(self):
#        self.strike = self.adjustableVarialbes['strike']        
#        self.premium = self.adjustableVarialbes['premium']        
#        self.init()
#        
#    def resetParameters(self, pDict):
#        for x in pDict:
#            self.adjustableVarialbes[x]=pDict[x]
#        
#        self.refreshAdjustableVarialbes()

    def setYLDBeta(self, ybeta):
        self.yldbeta = ybeta

    def setYLDAlpha(self, yalpha):
        self.yldalpha = yalpha

    def getTableValue(self):
        return [self.type, 
                self.expireDate, 
                #self.rfRate, 
                #self.fwdfut,
                self.strike, 
                #self.notional, 
                #self.premium, 
                self.impliedVol, 
                self.delta, 
                self.gamma, 
                self.theta, 
                self.vega
                ]

    def getPropIdx(self, rname):
        try:
            return self.properties.index(rname)
        except ValueError:
            return -1

    def getPropertyIdx(self, idx):
        theader = self.TableHeader[idx]
        if theader=='Forward Rate/Future Price':
            theader='Forward Rate'
        if theader in self.properties:
            return self.properties.index(theader)
        else:
            raise "error"
        
    def setTableProperty(self, index, value):        
        self.setProperty(self.getPropertyIdx(index), value)
        
    def setProperty(self, index, value):
        if isinstance(index, tuple):
            for i in range(len(index)):
                self.setProp(index[i], value[i])
        else:
            self.setProp(index, value)
            
        self.emit(QtCore.SIGNAL("OptionChanged"), (self,))
        #logging.debug("emit OptionChanged signal from setProperty")

    def clone(self):
        newOption = optionFactory(self.type)
        newOption.replicate(self)
        return newOption

    def replicate(self, opt):
        assert(isinstance(opt,option))
        self.tradeDate = opt.tradeDate
        self.prev_tradeDate = opt.prev_tradeDate
        self.horizonDate = opt.horizonDate
        self.exerciseType = opt.exerciseType                
        self.swapMat_contract = opt.swapMat_contract
        self.expireDate = opt.expireDate
        self.rfRate = opt.rfRate
        self.fwdfut = opt.fwdfut
        self.issueDate = opt.issueDate
        self.strike = opt.strike
        self.cpsf = opt.cpsf
        self.premium = opt.premium
        self.notional = opt.notional
        self.emit(QtCore.SIGNAL("OptionChanged"), (self,))
        logging.debug("emit OptionChanged signal from replicate")
                
class swaption(option):
    def __init__(self, **args):
        option.__init__(self, **args)
        self.init()
        
    def init(self):
        self.type='S'
        self.py_basis = ord('P')
        
        if self.tradeDate is not None:
            now = str2datetime(self.tradeDate)
            self.qtoday = QtCore.QDate(now.year, now.month, now.day)
                    
            if self.expireDate is None:
                self.expireDate = self.qtoday.addMonths(6).toString(QTDATEFMT)
            if self.issueDate is None:
                self.issueDate = self.qtoday.addMonths(6).toString(QTDATEFMT)
            if self.swapMat_contract is None:
                self.swapMat_contract = self.qtoday.addYears(3).toString(QTDATEFMT)

        self.connect(self, QtCore.SIGNAL("bonds_finish"), self.getNetValue)        

        self.property_names = ['Swap Maturity', 'Option Expiry', 'RF Rate', 'Forward Rate(%)',
                'Issue Date', 'Strike(%)', 'Direction', 'Premium(%)', 'Notional', 'Exercise Type']

        self.properties = ['Swap Maturity', 'Option Expiry', 
                           'RF Rate', 
                           'Forward Rate',
                           'Issue Date', 
                           'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']
        self.XMLproperties = ['SwapMaturity', 'ExpDate', 
                              'RFRate', 
                              'FwdSwap',
                              'IssueDate', 
                              'Strike', 'Direction', 'Premium', 'Notional', 'ExerciseType']
        self.tips = ['Swap Maturity', 'Option Expiry', 
                     'RF Rate', 
                     'Forward Rate',
                     'Issue Date', 
                     'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']
        
        self.cbflag = [False]*2

    def resetCBFlag(self):
        self.cbflag[0] = False
        self.cbflag[1] = False

    #slot func for signal "CallBackFunc", call calGreek and calPL after both callback funcs returned
    def chkCallBackStatus(self):
        logging.debug("chkCallBackStatus %s %s" % (str(self.cbflag[0]),str(self.cbflag[1])))
        if self.cbflag[0] and self.cbflag[1]:
            self.resetCBFlag()
            self.calGreek()
            self.calPL()
        
    #called by calculate func, different implementation for swaption and future options
    #emit two QtCore.SIGNAL("CallBackFunc")
    def calfwdfut(self):
    #    args_fwdfut = ('PRICE', xldstr2num(self.tradeDate), 0, 'WORST', 'US',
    #                          self.strike, xldstr2num(self.swapMat_contract),
    #                          self.fwdfut, 0, xldstr2num(self.issueDate))
        self.premium_a = self.premium
        def cb_fwdyld(*args):
            #logging.debug("callback for fwdyld " + str(args[0]))
            rs = args[0]
            if str(rs) == ETP_ERR:
                self.emit(QtCore.SIGNAL("OptionPLDone"), (self, 0))
            else:
                self.fwdYield = rs
                #print "fwdyld [%f]" % self.fwdYield                    
                self.cbflag[0] = True
                self.emit(QtCore.SIGNAL("CallBackFunc"))
                
        args_fwdfut = ('PRICE', convert2etpdate(self.tradeDate), 0, 'WORST', 'US',
                              self.strike, convert2etpdate(self.swapMat_contract),
                              self.fwdfut, 0, convert2etpdate(self.issueDate))
        
        def cb_fwdfut(*args):
            #print "callback for fwdfut " + str(args[0])
            rs = args[0]
            if str(rs) == ETP_ERR:
                self.emit(QtCore.SIGNAL("OptionPLDone"), (self, 0))
            else:
                self.fwdfut_i = rs            
                #print "fwdfut_i is [%f]" % (self.fwdfut_i)                
                args_fwdyld = ("YIELD", convert2etpdate(self.tradeDate), 0, "WORST", "US",
                                 self.strike, convert2etpdate(self.swapMat_contract),
                                 self.fwdfut_i, 0, convert2etpdate(self.issueDate))
                self.fwdyld_e = etp.query(cb_fwdyld, url, args_fwdyld)
            
        self.fwdfut_e = etp.query(cb_fwdfut, url, args_fwdfut)        
        args_strike = ('PRICE', convert2etpdate(self.expireDate), 0, 'WORST', 'US',
                               self.strike, convert2etpdate(self.swapMat_contract),
                               self.strike, 0, convert2etpdate(self.issueDate))

        def cb_strike(*args):
            #print "callback for strike " + str(args[0])
            rs = args[0]
            if str(rs) == ETP_ERR:
                self.emit(QtCore.SIGNAL("OptionPLDone"), (self, 0))
            else:
                self.strike_i = rs
                #print "strike_i is [%f]" % (self.strike_i)
                self.cbflag[1] = True
                self.emit(QtCore.SIGNAL("CallBackFunc"))

        self.strike_e = etp.query(cb_strike, url, args_strike)
    
    #called in calPL and calNextPL funcs after calculation of PL for each yield is done
    #emit QtCore.SIGNAL("bonds_finish")
    def calBondFut(self, yld):
        def cb_bonds(*args):
            #logging.debug("callback for bonds " + str(args[0]))
            rs = args[0]
            if str(rs) == ETP_ERR:
                self.emit(QtCore.SIGNAL("OptionPLDone"), (self, 0))
            else:
                self.bonds = rs
                self.emit(QtCore.SIGNAL("bonds_finish"))
        
        args_bonds = ("PRICE", convert2etpdate(self.horizonDate), 0, "WORST", "US", 
                    self.strike, convert2etpdate(self.swapMat_contract), 
                    self.fwdYield+(yld*self.yldbeta+self.yldalpha)/100.0, 0, convert2etpdate(self.issueDate))
        
        self.bonds_e = etp.query(cb_bonds, url, args_bonds)
                   
    def getProperties(self):
        return [self.swapMat_contract, self.expireDate, 
                self.rfRate, 
                self.fwdfut,
                self.issueDate, 
                self.strike, self.cpsf, self.premium, self.notional, self.exerciseType]
        
    def setProp(self, index, value):
        value = str(value)
        if value[0:2] in ("++", "--"):
            value = value[1:]
            if index == self.getPropIdx('RF Rate'):
                self.rfRate += float(value)
            elif index == self.getPropIdx('Forward Rate'):
                self.fwdfut += float(value)
            elif index == self.getPropIdx('Strike'):
                self.strike += float(value)
            elif index == self.getPropIdx('Premium'):
                self.premium += float(value)
            elif index == self.getPropIdx('Notional'):
                self.notional += float(value)
            else:
                raise "wrong index for properties [%d]" % index
        else:
            if index == self.getPropIdx('Swap Maturity'):
                self.swapMat_contract = str(value)
		self.getFwdRate()
            elif index == self.getPropIdx('Option Expiry'):
                self.expireDate = str(value)
		self.getFwdRate()
            elif index == self.getPropIdx('RF Rate'):
                self.rfRate = float(value)
            elif index == self.getPropIdx('Forward Rate'):
                self.fwdfut = float(value)
            elif index == self.getPropIdx('Issue Date'):
                self.issueDate = str(value)
            elif index == self.getPropIdx('Strike'):
                self.strike = float(value)
            elif index == self.getPropIdx('Direction'):
                self.cpsf = str(value)
            elif index == self.getPropIdx('Premium'):
                self.premium = float(value)
            elif index == self.getPropIdx('Notional'):
                self.notional = float(value)
            elif index == self.getPropIdx('Exercise Type'):
                self.exerciseType = str(value)
            else:
                raise "wrong index for properties [%d]" % index

class swaption_MQ(swaption):
    def __init__(self, **args):
        option.__init__(self, **args)
        self.init()
        
    def init(self):
        self.type='W'
        self.py_basis = ord('P')
        if self.cpsf == 'C':
            self.cpsf = 'payer'
        elif self.cpsf == 'P':
            self.cpsf = 'receiver'
        
        if self.tradeDate:
            self.setTradeDate(self.tradeDate)
            now = str2datetime(self.tradeDate)
            self.qtoday = QtCore.QDate(now.year, now.month, now.day)
                    
            if self.expireDate is None:
                self.expireDate = self.qtoday.addMonths(6).toString(QTDATEFMT)
            if self.swapMat_contract is None:
                self.swapMat_contract = self.qtoday.addYears(3).toString(QTDATEFMT)
        else:
            #raise "invalid tradeDate [%s]" % str(self.tradeDate)
            pass

        self.property_names = ['Swap Maturity', 'Option Expiry', 'Forward Rate(%)',
                'Strike(%)', 'Direction', 'Premium(%)', 'Notional', 'Exercise Type']
                
        self.properties = ['Swap Maturity', 'Option Expiry', 
                           #'RF Rate', 
                           'Forward Rate',
                           #'Issue Date', 
                           'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']
        self.XMLproperties = ['SwapMaturity', 'ExpDate', 
                              #'RFRate', 
                              'FwdSwap',
                              #'IssueDate', 
                              'Strike', 'Direction', 'Premium', 'Notional', 'ExerciseType']
        self.tips = ['Swap Maturity', 'Option Expiry', 
                     #'RF Rate', 
                     'Forward Rate',
                     #'Issue Date', 
                     'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']
        
        self.greeks = ('yvol', 'delta', 'gamma', 'theta', 'bpvega')

    def setGreeks(self, g, val):
        #print "setGreeks %s %s" % (str(g), str(val))
        if g in ('yvol', 'bpvol'):
            self.impliedVol=val
        elif g == 'delta':
            self.delta=val*self.notional
        elif g == 'gamma':
            self.gamma=val*self.notional
        elif g == 'theta':
            self.theta=val*self.notional
        elif g in ('yvega','bpvega'):
            self.vega=val*self.notional
        else:
            raise "unknown greeks %s" % g
                        
    def getProperties(self):
        return [self.swapMat_contract, self.expireDate, 
                #self.rfRate, 
                self.fwdfut,
                #self.issueDate, 
                self.strike, self.cpsf, self.premium, self.notional, self.exerciseType]

    def setTradeDate(self, tradeDate):
        self.tradeDate = str(tradeDate)
        def cb_prevBusiday(*args):
            rs = args[0]
            if str(rs) == ETP_ERR:
                print "Invalid tradeDate [%s]" % str(tradeDate)
            else:
                self.prev_tradeDate = str(rs[0][1])
                #print "callback setTradeDate " + self.prev_tradeDate
                self.getFwdRate()
	
        args_prev = ('prevbus', self.tradeDate, 'USD')
	print args_prev
        self.prev_e = etp.query(cb_prevBusiday, url_bretton, args_prev)
        
    def getFwdRate(self):
        def cb_fwdrate(*args):
            rs = args[0]
            if str(rs) == ETP_ERR:
                print "Invalid option data"
            else:
                #self.fwdfut = round(rs[0][1],4)
                self.fwdfut = rs[0][1]
                #print "callback getFwdRate " + str(self.fwdfut)
                self.setProperty((self.getPropIdx('Forward Rate'),self.getPropIdx('Strike')), (self.fwdfut,self.fwdfut))

        #mat = getTimeDiffByDays(self.tradeDate, self.swapMat_contract)
        #expiry = getTimeDiffByDays(self.tradeDate, self.expireDate)
        
        #args_fwdrate = ('swaprate', self.prev_tradeDate, (mat,expiry))
        args_fwdrate = ('swaprate', self.prev_tradeDate, (str(self.swapMat_contract),str(self.expireDate)))
	print args_fwdrate
        self.fwdrate_e = etp.query(cb_fwdrate, url_bretton, args_fwdrate)

    def calfwdfut(self):
        self.calAllGreeks()
        self.emit(QtCore.SIGNAL("CallBackFunc"))

    def calAllGreeks(self):
        #self.mat = getTimeDiffByDays(self.tradeDate, self.swapMat_contract)
        #self.expiry = getTimeDiffByDays(self.horizonDate, self.swapMat_contract)
        #print "mat=[%s] and expiry=[%s]" % (self.mat, self.expiry)
        
        self.greeks_e = []
        for g in self.greeks:
            self.calGreek(g)                

    def calGreek(self, greek='delta'):
        #calGreek
        def cb_greeks(*args):
            rs = args[0]
            if str(rs) == ETP_ERR:
                print "Invalid option data"
            else:
                res = rs[0][1]
                self.setGreeks(greek, res)
                #print "callback cb_greeks %s %s " % (greek, str(res))
                self.emit(QtCore.SIGNAL("OptionChanged"), (self,))

        #args_greeks = ('SWAPTION_PROJ', self.prev_tradeDate, self.expiry, self.mat, (0,0,1,1), (('calc',greek),('side',self.cpsf),('strike',self.strike)))
        args_greeks = ('SWAPTION_PROJ', self.prev_tradeDate, self.expireDate, self.swapMat_contract, (0,0,1,1), (('calc',greek),('side',self.cpsf),('strike',self.strike)))
        print args_greeks

        self.greeks_e.append(etp.query(cb_greeks, url_bretton, args_greeks))

    def chkCallBackStatus(self):
        self.getNetValue()
        
    def getNetValue(self):
        def cb_netvalue(*args):
            rs = args[0]
            if str(rs) == ETP_ERR:
                print "Invalid option data"
            else:
                netValue = rs[0]
                print "callback getNetValue " + str(netValue)
                for i in range(len(self.yldList)):
                    #self.PLDict[self.yldList[i]] = netValue[i+1]
                    self.PLDict[self.yldList[i]] = 0 if (netValue[i+1]=="") else netValue[i+1]
                    
                #print self.PLDict
                self.emit(QtCore.SIGNAL("OptionPLDone"), (self,))
        
        #ymin = self.yldList[0]
        #ymax = self.yldList[-1]
        #ystep = self.yldList[1]-self.yldList[0]
	yList = [x*self.yldbeta+self.yldalpha for x in self.yldList] 
        #args_netvalue = ('SWAPTION_PROJ', self.prev_tradeDate, self.expiry, self.mat, (ymin,ymax,ystep,IIf(self.yldbeta==1.0, 0, self.yldbeta)), (('calc','premium'),('side',self.cpsf),('strike',self.strike)))
        args_netvalue = ('SWAPTION_PROJ', self.prev_tradeDate, self.expireDate, self.swapMat_contract, tuple(yList), (('calc','premium'),('side',self.cpsf),('strike',self.strike)))
        print args_netvalue
        self.swaption_e = etp.query(cb_netvalue, url_bretton, args_netvalue)
                        
class futuresOption(option):
    def __init__(self, **args):
        option.__init__(self, **args)
        self.init()
        
    def init(self):
        self.type='F'
        self.py_basis = ord('Y')
        self.greekMultiply = 2500
        #self.pointValue = self.getPointValue()
        
        if self.swapMat_contract is None:
            self.swapMat_contract = 'ed08z'

        self.property_names = ['Contract', 'Option Expiry', 'RF Rate', 'Future Price(0.32)',
                'Strike(0.00)', 'Direction', 'Premium(0.64)', 'Notional', 'Exercise Type']
        self.properties = ['Contract', 'Option Expiry', 'RF Rate', 'Future Price',
                'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']
        self.XMLproperties = ['Contract', 'ExpDate', 'RFRate', 'FuturePrice',
                'Strike', 'Direction', 'Premium', 'Notional', 'ExerciseType']
        self.tips = ['Contract', 'Option Expiry', 'RF Rate', 'Future Price',
                'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']

    def getPointValue(self):
        return self.notional*2.5
                        
    def getPropertyIdx(self, idx):
        theader = self.TableHeader[idx]
        if theader=='Forward Rate/Future Price':
            theader = 'Future Price'
        if theader in self.properties:
            return self.properties.index(theader)
        else:
            raise "error"

    def getProperties(self):
        return [self.swapMat_contract, self.expireDate, self.rfRate, self.fwdfut,
                self.strike, self.cpsf, self.premium, self.notional, self.exerciseType]

    def setProp(self, index, value):
        value = str(value)
        if value[0:2] in ("++", "--"):
            value = value[1:]
            if index == self.getPropIdx('RF Rate'):
                self.rfRate += float(value)
            elif index == self.getPropIdx('Future Price'):
                self.fwdfut += float(value)
            elif index == self.getPropIdx('Strike'):
                self.strike += float(value)
            elif index == self.getPropIdx('Premium'):
                self.premium += float(value)
            elif index == self.getPropIdx('Notional'):
                self.notional += float(value)
            else:
                raise "wrong index for properties [%d]" % index
        else:
            if index == self.getPropIdx('Contract'):
                self.swapMat_contract_bak = self.swapMat_contract
                self.swapMat_contract = str(value)
                self.getExpDate(False)
            elif index == self.getPropIdx('Option Expiry'):
                self.expireDate = str(value)
            elif index == self.getPropIdx('RF Rate'):
                self.rfRate = float(value)
            elif index == self.getPropIdx('Future Price'):
                self.fwdfut = float(value)
            elif index == self.getPropIdx('Issue Date'):
                self.issueDate = str(value)
            elif index == self.getPropIdx('Strike'):
                self.strike = float(value)
            elif index == self.getPropIdx('Direction'):
                self.cpsf = str(value)
            elif index == self.getPropIdx('Premium'):
                self.premium = float(value)
            elif index == self.getPropIdx('Notional'):
                self.notional = float(value)
            elif index == self.getPropIdx('Exercise Type'):
                self.exerciseType = str(value)
            else:
                raise "wrong index for properties [%d]" % index

    def chkCallBackStatus(self):
        #logging.debug("chkCallBackStatus")
        self.calGreek()
        self.calPL()
    
    #called by calfwdfut <- calculate
    #emit QtCore.SIGNAL("CallBackFunc") if we need calculate PL at the time
    def getExpDate(self, emitFlag=True):
        def cb_optexp(*args):
            rs = args[0]
            if str(rs) == ETP_ERR:
                if emitFlag:
                    self.emit(QtCore.SIGNAL("OptionPLDone"), (self, 0))
                else:
                    w = QtGui.QWidget()
                    QtGui.QMessageBox.warning(w, self.tr("Invalid option data"),
                                              self.tr("Invalid contract name, please try agian"))
                    self.swapMat_contract = self.swapMat_contract_bak
                    self.emit(QtCore.SIGNAL("OptionChanged"), (self,))
            else:
                self.expireDate = xldnum2dstr(rs)
                print "callback " + str(self.expireDate)
                self.setProperty(1, self.expireDate)
                if emitFlag:
                    self.emit(QtCore.SIGNAL("CallBackFunc"))

        args_optexp = ('optexp', self.swapMat_contract)
        self.optexp_e = etp.query(cb_optexp, url, args_optexp)
        
    def calfwdfut(self):
        self.fwdfut_i = self.fwdfut
        self.strike_i = self.strike
        self.premium_a = self.premium
        
        self.getExpDate()

    def calBondFut(self, yld):
        spot = 100.0-self.fwdfut
        self.bonds = 100.0-(spot+(yld*self.yldbeta+self.yldalpha)/100.0)
        #print "FO bonds [%f]" % self.bonds

    def calPL(self):
        for yld in self.yldList:
            #logging.debug("yld is %f" % yld)            
            self.calBondFut(yld)
            netValue = self.getNetValue()
            #print "PL is [%f] for yld [%f]" % (netValue, yld)
            self.PLDict[yld] = netValue
        
        #print "FO calPL [%s]" % str(self)
        #print self.PLDict
        self.emit(QtCore.SIGNAL("OptionPLDone"), (self,))

    def getNetValue(self):
        if self.cpsf=='F':
            netValue = self.bonds
        else:
            netValue = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                   self.strike_i, max(self.daysToHorizon, self.dt)/365.0, 
                   self.bonds, self.rfRate, self.carry, 
                   self.impliedVol+self.volshift, 
                   self.py_basis).prem_volat
        return netValue

class treasureOption(futuresOption):
    def __init__(self, **args):
        option.__init__(self, **args)
        self.init()

    def init(self):
        self.type='T'
        self.py_basis = ord('P')
        if self.swapMat_contract is None:
            self.swapMat_contract = 'ty08u'
        
        self.property_names = ['Contract', 'Option Expiry', 'RF Rate', 'Future Price(0.32)',
                'Strike(0.00)', 'Direction', 'Premium(0.64)', 'Notional', 'Exercise Type']
        self.properties = ['Contract', 'Option Expiry', 'RF Rate', 'Future Price',
                'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']
        self.XMLproperties = ['Contract', 'ExpDate', 'RFRate', 'FuturePrice',
                'Strike', 'Direction', 'Premium', 'Notional', 'ExerciseType']
        self.tips = ['Contract', 'Option Expiry', 'RF Rate', 'Future Price',
                'Strike', 'Direction', 'Premium', 'Notional', 'Exercise Type']

    def getPointValue(self):
        return self.notional
                        
    def calfwdfut(self):
        self.fwdfut_i = 3.125*self.fwdfut-2.125*int(self.fwdfut)
        self.strike_i = self.strike
        self.premium_a = 1.5625*self.premium - 0.5625*int(self.premium)
        
        self.getExpDate()

    def calBondFut(self, yldshifts):
        def cb_bonds(*args):
            #logging.debug("callback for bonds " + str(args[0]))
            rs = args[0]
            if str(rs) == ETP_ERR:
                self.emit(QtCore.SIGNAL("OptionPLDone"), (self, 0))
            else:
                self.bonds = rs                
                self.getNetValue()
        
        args_bonds = ("FPROJ_SIMPLE", str(self.tradeDate), str(self.horizonDate),  
                    self.swapMat_contract, self.fwdfut_i, yldshifts,
                    'spotYld')
        
        print args_bonds
        self.bonds_e = etp.query(cb_bonds, url, args_bonds)

    def calPL(self):
        yldshifts = []
        for yld in self.yldList:
            #logging.debug("yld is %f" % yld)
            yldshifts.append(yld*self.yldbeta+self.yldalpha)
        
        yldshifts = tuple(yldshifts)
        self.calBondFut(yldshifts)
        
    def getNetValue(self):
        print self.bonds
        if self.cpsf=='F':
            for i in range(0, len(self.yldList)):
                netValue = self.bonds[i][0]
                self.PLDict[self.yldList[i]] = netValue
        else:
            for i in range(0, len(self.yldList)):
                netValue = bawopt.bopt(ord(self.cpsf), ord(self.exerciseType),
                       self.strike_i, max(self.daysToHorizon, self.dt)/365.0, self.bonds[i][0], 
                       self.rfRate, self.carry, self.impliedVol+self.volshift, self.py_basis).prem_volat
                                              
                self.PLDict[self.yldList[i]] = netValue

        #print self.PLDict
        self.emit(QtCore.SIGNAL("OptionPLDone"), (self,))
            
class portfolio(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.options = []
        self.setyldRange()
        self.horizonDate = None
        self.default_yldBeta = 1.0
	self.scenarios = {}
	self.defaultScenarioName = None

    def delScenario(self, name):
	if name in self.scenarios:
	    del self.scenarios[name]		

    def syncPortfolioWithScenario(self, name):
	cs =  self.scenarios[name]
	for opt in self.options:
	    if opt in cs:
		opt.setYLDAlpha(cs[opt][0])
		opt.setYLDBeta(cs[opt][1])
	
    def syncOptionWithScenario(self, name, opt):
	cs =  self.scenarios[name]
        opt.setYLDAlpha(cs[opt][0])
        opt.setYLDBeta(cs[opt][1])
	
    def newScenario(self, name=None, tweaks=None):
	self.curScenario = {}
	if tweaks is None:
	    for opt in self.options:
		#self.curScenario[opt] = (opt.yldalpha, opt.yldbeta)
		self.curScenario[opt] = (0.0, 1.0)
	else:
	    idx = 0
	    for opt in self.options:
		self.curScenario[opt] = tweaks[idx]
		idx += 1
			
	if name is None:
	    id = len(self.scenarios)+1
	    name = "Scenarios %d" % id
	self.scenarios[name] = self.curScenario
	self.defaultScenarioName = name

    def editScenario(self, name, tweaks):
	self.curScenario =  self.scenarios[name]
	i = 0
	for opt in self.options:
	    self.curScenario[opt] = tweaks[i]
	    i+=1

    def getScenarioNames(self):
	return self.scenarios.keys()
    
    def __str__(self):
        pstr = ""
        for opt in self.options:
            pstr += str(opt) + "\n"
        return pstr
   
    def scenarioToXML(self):
	inden1 = '\t'
	inden2 = '\t\t'
	xmlStr = ""
	for s in self.scenarios:
	    xmlStr += "%s<scenario name=\"%s\">\n" % (inden1, s)
	    cs = self.scenarios[s]
	    i = 0
	    for opt in self.options:
		xmlStr += '%s<%s id=\"%d\" alpha=\"%s\" beta=\"%s\"/>\n' % (inden2, "option", i, cs[opt][0], cs[opt][1])
		i+=1
	    xmlStr += "%s</scenario>\n" % (inden1)
	return xmlStr			
	    	    
 
    def toXML(self):
        xmlStr = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
        xmlStr += "<portfolio tradeDate=\"%s\" horizonDate=\"%s\">\n" % (self.options[0].tradeDate, self.options[0].horizonDate)
        for x in self.options:
            xmlStr += x.toXML()
	xmlStr+=self.scenarioToXML()
        xmlStr += "</portfolio>"
        return xmlStr
    
    def updateOption(self, opt, idx=-1, needConnect=False):
        if idx==-1 or len(self.options)==0:
            self.connect(opt, QtCore.SIGNAL("OptionPLDone"), self.chkCalStatus)
            self.options.append(opt)
        else:
            self.options[idx]=opt
            if needConnect:
                self.connect(opt, QtCore.SIGNAL("OptionPLDone"), self.chkCalStatus)            
        now = str2datetime(opt.horizonDate)
        self.horizonDate = QtCore.QDate(now.year, now.month, now.day)

    def delOption(self, opt):
        self.disconnect(opt, QtCore.SIGNAL("OptionPLDone"), self.chkCalStatus)
        self.options.remove(opt)
        
    def setyldRange(self, args = (-100,100,10)):
        #print "setyldRange [%d] [%d] [%d]" % (args[0],args[1],args[2])
	val = args[0]
	self.yldList = [val]
	while val<args[1]:
	    val+=args[2]
	    self.yldList.append(val) 

    def setTradeDate(self, tradeDate):
	assert(isinstance(tradeDate, QtCore.QDate))
        tdate = str(tradeDate.toString(QTDATEFMT))
        for x in self.options:
            x.setTradeDate(tdate)
    
    def setHorizonDate(self, horizonDate):
	assert(isinstance(horizonDate, QtCore.QDate))
	self.horizonDate = QtCore.QDate(horizonDate.year(), horizonDate.month(), horizonDate.day())
	self.setOptsHorizonDate(str(horizonDate.toString(QTDATEFMT)))
    
    def setOptsHorizonDate(self, hdate):
        for x in self.options:
            x.setHorizonDate(hdate)
	
    def getHorizonDate(self, add):
        if add == 0:
            hdate = self.horizonDate
        elif len(add)>1:
            num = int(add[:-1])
            unit = str(add[-1])

            if unit.upper() == 'Y':
                hdate = self.horizonDate.addYears(num)
            elif unit.upper() == 'M':
                hdate = self.horizonDate.addMonths(num)
            elif unit.upper() == 'D':
                hdate = self.horizonDate.addDays(num)
	    else:
		raise "invalid parameter for getHorizonDate: [%s]" % str(add)
	else:
	    raise "invalid parameter for getHorizonDate: [%s]" % str(add)
        return str(hdate.toString(QTDATEFMT))

    #@cvtype: curve type. yield change/horizon date
    #@cvparm: curve parameter. yield beta/time delta
    def queryPortfolioPL(self, cvparam=1.0, cvtype=0):
        print "queryPortfolioPL %d %s" % (len(self.options), str(cvparam))
        self.flag_calOpt={}
        self.cvtype = cvtype
        if cvtype == 0:
            for x in self.options:
                x.setYLDBeta(cvparam)
                if x.isDataValid():
                    self.flag_calOpt[x]=False
                    x.calculate(self.yldList)
                else:
                    self.flag_calOpt[x]=True
                    print "queryPortfolioPL: please check your option data [%s]" % str(x)
        elif cvtype == 1:
            hdate = self.getHorizonDate(cvparam)
            self.setOptsHorizonDate(hdate)
	    self.syncPortfolioWithScenario(self.defaultScenarioName)
            for x in self.options:
                if x.isDataValid():
                    self.flag_calOpt[x]=False
                    x.calculate(self.yldList)
                    #print x
                else:
                    self.flag_calOpt[x]=True
                    print "queryPortfolioPL: please check your option data [%s]" % str(x)
        if cvtype == 2:
            for x in self.options:
		ab = self.scenarios[cvparam][x]
		print "(alpha, beta) = " + str(ab)
                x.setYLDAlpha(ab[0])
                x.setYLDBeta(ab[1])
                if x.isDataValid():
                    self.flag_calOpt[x]=False
                    x.calculate(self.yldList)
                else:
                    self.flag_calOpt[x]=True
                    print "queryPortfolioPL: please check your option data [%s]" % str(x)
                    
    def chkCalStatus(self, args):
        #print "chkCalStatus" + str(args)
        opt = args[0]
        if len(args)>1:
            opt.calSuccess = args[1]
        else:
            opt.calSuccess = 1
            
        self.flag_calOpt[opt]=True
        for x in self.flag_calOpt:
            if not self.flag_calOpt[x]:
                return
            
        self.calPortfolioPL()
                
    def calPortfolioPL(self):
        yldList = self.options[0].PLDict.keys()
        yldList.sort()
                
        totalPLList = []        
        successOpt = []
	#recover the oringinal horizonData for all options in portfolio
        if self.cvtype == 1:
            self.setOptsHorizonDate(str(self.horizonDate.toString(QTDATEFMT)))
	#recover the oringinal yield beta for all options in portfolio
        for x in self.options:
            x.setYLDBeta(self.default_yldBeta)
            if x.calSuccess > 0:                
                successOpt.append(x)
            else:
                print "calPortfolioPL: etp error for option [%s]" % str(x)
            
        for yld in yldList:
            totalPL = 0
            for x in successOpt:
                if x.type == 'T':
		    #print "initial cost " + str(x.premium_a) + " " + str(x.getPointValue())
                    totalPL += (x.PLDict[yld]+x.carry-x.premium_a)*x.getPointValue()
                else:
                    totalPL += (x.PLDict[yld]+x.carry-x.premium)*x.getPointValue()
            #totalPLList.append(round(totalPL,2))
            totalPLList.append(totalPL)
        
#        print yldList
#        print totalPLList
        
        self.pfPL = (yldList, totalPLList)
        print "PortfolioPLDone"
        self.emit(QtCore.SIGNAL("PortfolioPLDone"))
        
#    def event(self, e):
#        #logging.debug("receive event %s" % str(e.type()))
#        print "receive event %s" % str(e.type())
#        if e.type() == QtCore.QEvent.User:
#            return True
#        return Qt.QObject.event(e)
        
class myQApplication(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
    
    def notify(self, receiver, event):
        try:
            QtGui.QApplication.notify(self, receiver, event)
        except: 
            print sys.exc_info()[0]
            print sys.exc_info()[1]

def optionFactory(type='S',tradeDate=None, exerciseType='E', 
                 expireDate=None, rfRate=5.0, fwdfut=5.0, strike=5.0, 
                 cpsf='P', premium=0.5, notional=100, 
                 volMatrix=0, matrixPrem=0, 
                 swapMat_contract=None, issueDate=None,
                 horizonDate=None, 
                 priceYield='P',
                 carry=0, yldalpha=0, yldbeta=1, savedopt=False):
    if savedopt:#default option
	if horizonDate is None: horizonDate=nvldate(str2datetime('3/20/2009','%m/%d/%Y'))
        swapMat_contract=nvldate(addYears(str2datetime(horizonDate),1))
        expireDate=nvldate(addMonth(str2datetime(horizonDate),6))
        #now = str2datetime(self.tradeDate)
        #self.qtoday = QtCore.QDate(now.year, now.month, now.day)
        #if self.expireDate is None:
	#    self.expireDate = self.qtoday.addMonths(6).toString(QTDATEFMT)
        #if self.swapMat_contract is None:
	#    self.swapMat_contract = self.qtoday.addYears(3).toString(QTDATEFMT)
        if type == 'S':
            opt = swaption(tradeDate=tradeDate, exerciseType='E', 
                         expireDate=expireDate, rfRate=5.25, fwdfut=4.79, strike=4.74, 
                         cpsf='P', premium=0.59, notional=100,  
                         swapMat_contract=swapMat_contract, horizonDate=horizonDate,
                         issueDate=expireDate)
        elif type == 'W':
            opt = swaption_MQ(tradeDate=tradeDate, exerciseType='E', 
                         expireDate=expireDate, fwdfut=4.79, strike=4.74, 
                         cpsf='P', premium=0.59, notional=100,
                         swapMat_contract=swapMat_contract, horizonDate=horizonDate)
        elif type == 'F':
            opt = futuresOption(tradeDate=tradeDate, exerciseType='E',
                             rfRate=5.25, fwdfut=95.205, strike=95.250, 
                             cpsf='P', premium=0.305, notional=1000, 
                             swapMat_contract='ed08z', horizonDate=horizonDate)
        elif type == 'T':
            opt = treasureOption(tradeDate=tradeDate, exerciseType='A',
                         rfRate=5.40, fwdfut=104.22, strike=103.0, 
                         cpsf='P', premium=0.36, notional=1000,  
                         swapMat_contract='ty08u', horizonDate=horizonDate)
    else:
        if type == 'S':
            opt = swaption(tradeDate=tradeDate, exerciseType=exerciseType, 
                         expireDate=expireDate, rfRate=rfRate, fwdfut=fwdfut, strike=strike, 
                         cpsf=cpsf, premium=premium, notional=notional,
                         swapMat_contract=swapMat_contract, horizonDate=horizonDate,
                         issueDate=issueDate)
        elif type == 'W':
            opt = swaption_MQ(tradeDate=tradeDate, exerciseType=exerciseType, 
                         expireDate=expireDate, fwdfut=fwdfut, strike=strike, 
                         cpsf=cpsf, premium=premium, notional=notional,  
                         swapMat_contract=swapMat_contract, horizonDate=horizonDate)
        elif type == 'F':
            opt = futuresOption(tradeDate=tradeDate, exerciseType=exerciseType,
                         rfRate=rfRate, fwdfut=fwdfut, strike=strike, 
                         cpsf=cpsf, premium=premium, notional=notional,  
                         swapMat_contract=swapMat_contract, horizonDate=horizonDate)    
        elif type == 'T':
            opt = treasureOption(tradeDate=tradeDate, exerciseType=exerciseType,
                         rfRate=rfRate, fwdfut=fwdfut, strike=strike, 
                         cpsf=cpsf, premium=premium, notional=notional,  
                         swapMat_contract=swapMat_contract, horizonDate=horizonDate)
    return opt
    
def main():
    now = date.today()
    tradeDate = now.strftime(DATEFMT)
    p = portfolio()

    s = swaption(tradeDate=tradeDate, exerciseType='E', 
                 expireDate='3/17/2008', rfRate=5.25, fwdfut=4.79, strike=4.74, 
                 cpsf='P', premium=0.59, notional=100,  
                 swapMat_contract='3/19/2010', horizonDate='7/20/2007',
                 issueDate='3/17/2008')
    #s.resetParameters({"strike":50})
    #s.calculate()
    p.updateOption(s)
    
    f = futuresOption(tradeDate=tradeDate, exerciseType='E',
                     rfRate=5.25, fwdfut=95.205, strike=95.250, 
                     cpsf='P', premium=0.305, notional=1000, 
                     swapMat_contract='ed08z', horizonDate='7/20/2007')
    #f.resetParameters({"premium":50})
    #f.calculate()
    p.updateOption(f)
    #p.delOption(s)
    return p

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)    

    f = QtGui.QFrame()
    f.resize(100, 30)
    c = QtGui.QPushButton("Calculate", f) 
    p = main()
    QtCore.QObject.connect(c, QtCore.SIGNAL("clicked()"), p.queryPortfolioPL)
    f.show()
    sys.exit(app.exec_())
