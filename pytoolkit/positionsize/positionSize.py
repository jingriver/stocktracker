from optparse import OptionParser
import math

"""
Position-Sizing
Knowing how many shares to buy per trade does make a difference to the performance for a trader. 
This is what they call position-sizing.

Percentage Volatility Model:


Position Sizing Calculator
based on the Percentage risk model

Input:     
Account Size: Equity. How much money you currently have in your stock trading account          
Risk Tolerance: % of Account. How much of that money you are prepared to risk on a single stock trade in percentage terms (e.g enter 5 if your risk tolerance is 5%).
Stop Loss Size: how many points you want your stop loss to be for the instrument you are stock trading. For example, on the S&P, if you wanted a 2 point stoploss, enter 2. If you are trading IBM, and want a 1 dollar stoploss, enter 1.          
Unit Cost:  $ number of dollars per point this security moves. The amount in dollars that this security changes for every 1 point of movement. For example, for a stock priced in dollars, you would enter 1. For an S&P emini contract you would enter 50 (because an emini moves 50 dollars per point). For a full size S&P contract you would enter 250.

Output:
Position Size (Shares or contracts), to the nearest whole contract.    
"""

def positionsize(asize, risk, stopsize, unitcost):
    size = int(asize*(risk/100.0)/(stopsize*unitcost))
    return size

def main():
#    usage = "usage: %prog [options]"
#    parser = OptionParser(usage)
#    parser.add_option("-a", "--account size", dest="asize", default="jpg",
#                      help="sufix of the files to be changed")
#    parser.add_option("-p", "--zeropad", dest="pad", default=3,
#                      help="number of zeroes padding the file name", type="int")
#    parser.add_option("-v", "--verbose",
#                      action="store_true", dest="verbose", default=True)
#    parser.add_option("-V", "--version", dest="version",
#                  default=1.0, type="float",)
#        
#    (options, args) = parser.parse_args()    
#    if options.verbose:
#        print "reading %s..." % options.sufix
##    if len(args) != 1:
##        parser.error("incorrect number of arguments")
    
    #emini dow YM
    print positionsize(30000, 5, 50, 5)
    
    #QQQQ
    print positionsize(2822, 5, 1, 1)        
                
if __name__ == "__main__":
    #createTestfiles()
    main()        
    
