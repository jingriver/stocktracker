"""
"""
import time, datetime, os, sys
from matplotlib.numerix import *
from matplotlib import rcParams
from matplotlib.ticker import  IndexLocator, FuncFormatter, NullFormatter, MultipleLocator
from matplotlib.dates import IndexDateFormatter, date2num
from matplotlib.finance import candlestick2, plot_day_summary2, volume_overlay, index_bar
from matplotlib.widgets import Cursor, MultiCursor, SpanSelector

from pylab import *
from TaLib import *

from testsqlite3 import OHLCV
from config import dao

purple = '#660033'
textsize = 8        # size for axes text
rcParams['timezone'] = 'US/Eastern'
rc('grid', color='0.75', linestyle='-', linewidth=0.5)

def load_quotes(fname, fmt='%m/%d/%Y', maxq=None):
    """
    Load quotes from the representative data files vineet sent If any
    of the values are missing I force all missing.  Quotes are sorted
    in increasing time.  Return value is a list of tuples

      (epoch, open, high, low, close, volume )
    """
    quotes = []
    
    for i, line in enumerate(file(fname)):
        if maxq is not None and i>maxq: break
        ts,o,h,l,c,v = line.split(',')
        
        dt = datetime.datetime(*time.strptime(ts.strip('"'), fmt)[:6]) # convert to float days
        d = date2num(dt)

        o,h,l,c,v = [float(val) for val in o,h,l,c,v]

        if o==-1 or h==-1 or l==-1 or c==-1 or v==-1:
            o,h,l,c,v = -1, -1, -1, -1,-1
        quotes.append((d,o,h,l,c,v))

    quotes.sort()  # increasing time
    return quotes

def fill_over(ax, x, y, val, color, over=True):
    """
    Plot filled x,y for all y over val
    if over = False, fill all areas < val
    """
    ybase = asarray(y)-val
    crossings = nonzero(less(ybase[:-1] * ybase[1:],0))
    
    if ybase[0]>=0: fillon = over
    else:           fillon = not over
    
    indLast = 0
    for ind in crossings[0]:        
        if fillon:
            thisX = x[indLast:ind+1]
            thisY = y[indLast:ind+1]
            thisY[0] = val
            thisY[-1] = val
            ax.fill(thisX, thisY, facecolor=color)
        fillon = not fillon
        indLast = ind

def get_valid(x):
    return array([thisx for thisx in x if thisx!=-1])

class mychart:
    def __init__(self):
        self.run()
        
    def load(self, ticker):
        fname='jpm_prices.csv'
        quotes = load_quotes(fname)

        times, opens, highs, lows, closes, volumes = zip(*quotes)                
        #valid opens, etc
    #    vopens   = get_valid(opens)
    #    vcloses  = get_valid(closes)
    #    vlows    = get_valid(lows)
    #    vhighs   = get_valid(highs)
    #    vvolumes = get_valid(volumes)
        vind = array([i for i, o in enumerate(opens) if o!=-1])
    
    #    assert(len(vopens)==len(vcloses)==len(vlows)==len(vhighs)==len(vvolumes))    
    #    N = len(vopens)        
        return times, opens, closes, highs, lows, volumes, vind

    def loadFromDB(self, ticker, duration='-3m'):
        po = OHLCV(dao())        
        times, opens, highs, lows, closes, volumes = po.queryOHLCV(ticker, duration=duration)
        numtimes = []
        for ts in times:
            dt = datetime.datetime(*time.strptime(ts.strip('"'), "%Y%m%d")[:6]) # convert to float days
            numtimes.append(date2num(dt))
         
        vind = array([i for i, o in enumerate(opens) if o!=-1])
        return numtimes, opens, closes, highs, lows, volumes, vind
        
    def get_locator(self):
        """
        the axes cannot share the same locator, so this is a helper
        function to generate locators that have identical functionality
        """    
        return IndexLocator(10, 1)
    
    def fmt_vol(self, x,pos):
        if pos>3: return ''  # only label the first 3 ticks
        return '%dM' % int(x/1e-6)
    
    def drawTicker(self, ticker):
        self.ticker = ticker
        self.updateChart()
        show()
        
    def updateChart(self, duration="3m"):      
        axUpper, axMiddle, axMiddleVol, axLower, axADX = self.allAxes        
        for ax in self.allAxes:
            ax.cla()

        t = self.allAxes[0].set_title('%s' % self.ticker, fontsize=12)
        t.set_y(1.05)  # move it up a bit higher than the default
        t.set_x(0)  # align the title left, axes coords
        t.set_horizontalalignment('left')  # align the title left, axes coords
                    
        times, opens, closes, highs, lows, volumes, vind = self.loadFromDB(self.ticker, "-"+duration)
        formatter =  IndexDateFormatter(times, '%b %d %y')                
        self.allAxes[-1].xaxis.set_major_formatter( formatter )
        
        self.panel_oscillator(axUpper, vind, TA_RSI, (closes, 14), "RSI(14)")
        self.panel_candlestick(axMiddle, axMiddleVol, opens, closes, highs, lows, volumes, vind)        
        self.panel_macd(axLower, closes, vind)
        #self.panel_adx(axADX, highs, lows, closes, vind)
        self.panel_oscillator(axADX, vind, TA_MFI, (highs, lows, closes, volumes, 20),  "MFI(20)")
        #self.panel_oscillator(axADX, vind, TA_ATR, (highs, lows, closes, 14),  "ATR(14)", False)
        #self.panel_stoch(axADX, highs, lows, closes, vind)                
        
        # force all the axes to have the same x data limits    
        xlim = 0, len(closes)
        for a in self.allAxes:
            #a.dataLim.intervalx = xlim
            a.set_xlim(xlim)
        
        for ax in axUpper, axMiddle:
            for ticklabel in ax.get_xticklabels():
                ticklabel.set_visible(False)

        # make sure everyone has the same axes limits    
        setp(self.allAxes[-1].get_xticklabels(), 'rotation', 45,
            'horizontalalignment', 'right', fontsize=8)
                
        #cursor = Cursor(axUpper, useblit=True, color='red', linewidth=2 )
        #cursor.horizOn=False
        multi = MultiCursor(axUpper.figure.canvas, self.allAxes, color='r', lw=1)
        
        #draw()
        
    def run(self):
        figBG   = 'w'        # the figure background color
        axesBG  = '#f6f6f6'  # the axies background color
                
        # the demo data are intc from (2003, 9, 1) to (2004, 4, 12 ) with
        # dates as epoch; I saved these to a file for ease of debugginh
            
        figure(1, facecolor=figBG)        

        nullfmt   = NullFormatter()         # no labels    
        volumeFmt = FuncFormatter(self.fmt_vol)
    
        left, width = 0.1, 0.8
        num_panel = 4
        height = 1.0/(num_panel+2)
        rect = []
        rect.append([left, 0.1, width, height])
        for i in range(num_panel):
            if i==1:
                rect.append([left, rect[-1][1]+rect[-1][3], width, height*2])
            else:
                rect.append([left, rect[-1][1]+rect[-1][3], width, height])
        
        axUpper      = axes(rect[3], axisbg=axesBG)  #left, bottom, width, height        
        axMiddle     = axes(rect[2], axisbg=axesBG, sharex=axUpper)
        axMiddleVol  = axes(rect[2], axisbg=axesBG, frameon=False, sharex=axUpper)  # the volume overlay                
        axLower      = axes(rect[1], axisbg=axesBG, sharex=axUpper)
        axADX      = axes(rect[0], axisbg=axesBG, sharex=axUpper)
        self.allAxes = (axUpper, axMiddle, axMiddleVol, axLower, axADX)    
            
        axUpper.xaxis.set_major_locator( self.get_locator() )
        axUpper.xaxis.set_major_formatter(nullfmt)
        axUpper.grid(True)
        
        # set up two scales on middle axes with left and right ticks        
        axMiddle.xaxis.set_major_locator( self.get_locator() )
        axMiddle.yaxis.set_major_locator( MultipleLocator(5) )
        axMiddle.xaxis.set_major_formatter(nullfmt)
        axMiddle.grid(True)
                    
        axMiddleVol.xaxis.set_major_locator( self.get_locator() )
        axMiddleVol.xaxis.set_major_formatter(nullfmt)
        axMiddleVol.yaxis.set_major_formatter(volumeFmt)            

        axLower.xaxis.set_major_locator( self.get_locator() )
        axLower.grid(True)

        axADX.xaxis.set_major_locator( self.get_locator() )
        axADX.grid(True)
        
        tframe = ['1m', '3m', '6m', '1y', '2y', '5y']
        left = 0.6
        bottom = 0.02
        width = 0.04
        height = 0.02
        lstep = 0.05

        def btn_callback(event):
            self.updateChart(event.label_text)
        
        for i, tf in enumerate(tframe):
            axbutton = axes([left+lstep*i, bottom, width, height])
            bnext = Button(axbutton, tf)            
            bnext.on_clicked(btn_callback)

#        def onselect(xmin, xmax):
#            indmin, indmax = npy.searchsorted(x, (xmin, xmax))
#            indmax = min(len(x)-1, indmax)
#        
#            thisx = x[indmin:indmax]
#            thisy = y[indmin:indmax]
#            ax2.set_xlim(thisx[0], thisx[-1])
#            ax2.set_ylim(thisy.min(), thisy.max())
#            draw()
#        
#        # set useblit True on gtkagg for enhanced performance
#        span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
#                            rectprops=dict(alpha=0.5, facecolor='red') )
                
    def panel_oscillator(self, ax, vind, tafunc, params, name, drawhirizon=True, lowbound=20, upbound=80):
        retCode, begIdx, s = tafunc(0, len(vind)-1, *params)
        assert(retCode, TA_SUCCESS)
        ax.plot(vind[begIdx:], s, color=purple)
        if drawhirizon:
            N = len(vind)
            # upper horiz line
            ax.plot( (0, N), [lowbound, lowbound], color=purple, linewidth=2)
            # lower horiz line
            ax.plot( (0, N), [upbound, upbound], color=purple, linewidth=2)  
            # center line
            ax.plot( (0, N), [50, 50], color=purple, linewidth=2)  
        
            # fill above threshold
            fill_over(ax, vind[begIdx:], s, lowbound,  purple,  over=False)
            fill_over(ax, vind[begIdx:], s,  upbound,  purple, over=True)
            
        ax.yaxis.set_major_locator( MultipleLocator(20) )    
        # now add some text
        left, height, top = 0.025, 0.06, 0.85
        t = ax.text(left, top, name, fontsize=textsize, transform=ax.transAxes)                
                
    def panel_candlestick(self, axMiddle, axMiddleVol, opens, closes, highs, lows, volumes, vind):
        ############### Middle axes #################
        axMiddle.yaxis.tick_left()
        axMiddleVol.yaxis.tick_right()        
        #plot_day_summary2(axMiddle, opens, closes, highs, lows)
        candlestick2(axMiddle, opens, closes, highs, lows, width=0.9)
    
        # specify the text in axes (0,1) coords.  0,0 is lower left and 1,1 is
        # upper right
    
        left, height, top = 0.025, 0.06, 0.9
        t1 = axMiddle.text(left, top, '%s daily'%self.ticker, fontsize=textsize,
                           transform=axMiddle.transAxes)
        t2 = axMiddle.text(left, top-height, 'MA(5)', color='b', fontsize=textsize,
                           transform=axMiddle.transAxes)
        t3 = axMiddle.text(left, top-2*height, 'MA(20)', color='r', fontsize=textsize,
                           transform=axMiddle.transAxes)
    
        s = '%s O:%1.2f H:%1.2f L:%1.2f C:%1.2f, V:%1.1fM Chg:%+1.2f' %(
            time.strftime('%d-%b-%Y'),
            opens[-1], highs[-1],
            lows[-1], closes[-1],
            volumes[-1]*1e-6,
            closes[-1]-opens[-1])
        t4 = axMiddle.text(0.4, top, s, fontsize=textsize,
                           transform=axMiddle.transAxes)
        
        # now do the moviing average.  I'll use a convolution to simulate a
        # real moving average    
        try:
            for x in [5, 20]:
                retCode, begIdx5, ma5 = TA_MA(0, len(closes)-1, closes, x)
                assert(retCode, TA_SUCCESS)
                axMiddle.plot(vind[begIdx5:], ma5, 'b', linewidth=1)            
        except:
            pass
        #axMiddle.set_ylim((20, 32))
        #axMiddle.set_yticks((25,30))
    
        # Now do the volume overlay        
        bars = volume_overlay(axMiddleVol, opens, closes, volumes, width=1, alpha=0.5)
        axMiddleVol.add_collection(bars)
        axMiddleVol.set_ylim((0, 3*max(volumes)))  # use only a third of the viewlim
        
    def panel_macd(self, axLower, closes, vind):
        ############### Lower axes #################
    
        # make up two signals; I don't know what the signals are in real life
        # so I'll just illustrate the plotting stuff
        try:
        #    s1 = random_signal(len(vind), 10)
        #    s2 = random_signal(len(vind), 20)
            retCode, begIdx, s1, s2, s3 = TA_MACD(0, len(closes)-1, closes, 12, 26, 9)
            assert(retCode, TA_SUCCESS)
            
            axLower.plot(vind[begIdx:], s1, color=purple)
            axLower.plot(vind[begIdx:], s2, color='k', linewidth=1.0)
            
            #axLower.plot(vind[begIdx20:], s3, color='#cccc99')  # wheat
            s4 = [-1]*begIdx
            s4.extend(s3)
            bars = index_bar(axLower, s4, width=2, alpha=0.5, facecolor='#3087c7', edgecolor='#cccc99')
            axLower.yaxis.set_major_locator(MultipleLocator(5))
        except:
            pass
        # now add some text
        left, height, top = 0.025, 0.06, 0.85    
        t = axLower.text(left, top, 'MACD(12,26,9) -0.26', fontsize=textsize,
                         transform=axLower.transAxes)
        
    def panel_adx(self, axADX, highs, lows, closes, vind):
        ############### Lower axes #################
        retCode, begIdx1, adx = TA_ADX(0, len(closes)-1, highs, lows, closes, 20)
        assert(retCode, TA_SUCCESS)
    
        retCode, begIdx2, minus_di = TA_MINUS_DI(0, len(closes)-1, highs, lows, closes, 20)
        assert(retCode, TA_SUCCESS)
    
        retCode, begIdx3, plus_di = TA_PLUS_DI(0, len(closes)-1, highs, lows, closes, 20)
        assert(retCode, TA_SUCCESS)
        
        axADX.plot(vind[begIdx1:], adx, color=purple)
        axADX.plot(vind[begIdx2:], minus_di, color='k', linewidth=1.0)
        axADX.plot(vind[begIdx3:], plus_di, color='b', linewidth=1.0)
        axADX.yaxis.set_major_locator(MultipleLocator(5))

        left, height, top = 0.025, 0.06, 0.85    
        t = axADX.text(left, top, 'ADX(20), +DI, -DI', fontsize=textsize,
                         transform=axADX.transAxes)

    def panel_stoch(self, ax, highs, lows, closes, vind):
        retCode, begIdx, slowk, slowd = TA_STOCH(0, len(closes)-1, highs, lows, closes)
        assert(retCode, TA_SUCCESS)
        
        ax.plot(vind[begIdx:], slowk, color=purple)
        ax.plot(vind[begIdx:], slowd, color='k', linewidth=1.0)
        ax.yaxis.set_major_locator(MultipleLocator(20))

        left, height, top = 0.025, 0.06, 0.85    
        t = ax.text(left, top, 'Slow Stochastic', fontsize=textsize, transform=ax.transAxes)
        
#    def panel_rsi(self, axUpper, closes, vind):
#        ############### Upper axes #################
#    
#        # make up a pseudo signal    
#        retCode, begIdx, s = TA_RSI(0, len(closes)-1, closes, 14)
#        assert(retCode, TA_SUCCESS)
#        thresh1 = 20
#        thresh2 = 80
#        axUpper.plot(vind[begIdx:], s, color=purple)
#    
#        N = len(closes)
#        # upper horiz line
#        axUpper.plot( (0, N), [thresh1, thresh1], color=purple, linewidth=2)
#        # lower horiz line
#        axUpper.plot( (0, N), [thresh2, thresh2], color=purple, linewidth=2)  
#    
#        # fill above threshold
#        fill_over(axUpper, vind[begIdx:], s,  thresh2,  purple, over=True)
#        fill_over(axUpper, vind[begIdx:], s, thresh1,  purple,  over=False)
#    
#        t = axUpper.set_title('%s' % self.ticker, fontsize=12)
#        t.set_y(1.05)  # move it up a bit higher than the default
#        t.set_x(0)  # align the title left, axes coords
#        t.set_horizontalalignment('left')  # align the title left, axes coords
#        axUpper.yaxis.set_major_locator( MultipleLocator(5) )
#    
#        # now add some text
#        left, height, top = 0.025, 0.06, 0.85
#        t = axUpper.text(left, top, 'RSI(14)', fontsize=textsize,
#                         transform=axUpper.transAxes)                
#
#    def panel_MFI(self, axMFI, highs, lows, closes, volumes, vind):
#        ############### Lower axes #################
#        retCode, begIdx, mfi = TA_MFI(0, len(closes)-1, highs, lows, closes, volumes, 20)
#        assert(retCode, TA_SUCCESS)
#
#        thresh1 = 20
#        thresh2 = 80
#
#        N = len(closes)
#        # upper horiz line
#        axMFI.plot( (0, N), [thresh1, thresh1], color=purple, linewidth=2)
#        # lower horiz line
#        axMFI.plot( (0, N), [thresh2, thresh2], color=purple, linewidth=2)  
#    
#        # fill above threshold
#        fill_over(axMFI, vind[begIdx:], mfi,  thresh2,  purple, over=True)
#        fill_over(axMFI, vind[begIdx:], mfi, thresh1,  purple,  over=False)
#            
#        axMFI.plot(vind[begIdx:], mfi, color=purple)
#
#        left, height, top = 0.025, 0.06, 0.85    
#        t = axMFI.text(left, top, 'MFI(20)', fontsize=textsize,
#                         transform=axMFI.transAxes)

if __name__== "__main__":
    m = mychart()
    m.drawTicker("GOOG")