import sys
from TaLib import *

#All the TA functions are simple mathematical function. You provides the inputs with an array, 
#and the function simply store the output in a caller provided output array. The TA functions 
#are NOT allocating any space for the caller. The number of data in the output will NEVER exceed 
#the number of elements requested to be calculated (with the startIdx and endIdx explained below).
#
#Here is an example:
#
#We will dissect the TA_MA function allowing to calculate a simple moving average.
#
#TA_RetCode TA_MA( int          startIdx,
#                  int          endIdx,
#                  const double inReal[],
#                  int          optInTimePeriod,
#                  int          optInMAType,
#                  int         *outBegIdx,
#                  int         *outNbElement,
#                  double       outReal[],
#                )
#
#At first it appears that there is a lot of parameters, but do not be discourage, all functions are 
#consistent and share the same parameter structure. The parameters are provided in 4 sections:
#1. The output will be calculated only for the range specified by startIdx to endIdx.
#2. One or more data inputs are then specified. In that example there is only one input. All inputs parameter name starts with "in".
#3. zero or more optional inputs are specified here. In that example there is 2 optional inputs. These parameters allows to fine tune 
#   the function. If you do not care about a particular optIn just specify TA_INTEGER_DEFAULT or TA_REAL_DEFAULT (depending of the type).
#4. One or more output are finally specified. In that example there is only one output which is outReal 
#   (the parameters outBegIdx and outNbElement are always specified once before the list of outputs).
#
#This structure of parameters gives a lot of flexibility to make the function calculate ONLY the portion of required data. 
#It is slightly complex, but it allows demanding user to manage efficiently the memory and the CPU processing.
#
#Lets say you wish to calculate a 30 day moving average using closing prices. The function call could look as follow:
#
#TA_Real    closePrice[400];
#TA_Real    out[400];
#TA_Integer outBeg;
#TA_Integer outNbElement;
#
#/* ... initialize your closing price here... */
#
#retCode = TA_MA( 0, 399, &closePrice[0], 30,TA_MAType_SMA, &outBeg, &outNbElement, &out[0]);
#
#/* The output is displayed here */
#for( i=0; i < outNbElement; i++ )
#   printf( "Day %d = %f\n", outBeg+i, out[i] );
#
#One important aspect of the output are the outBeg and outNbElement. Even if it was requested to calculate for the 
#whole range (from 0 to 399), the moving average is not valid until the 30th day. Consequently, the outBeg will be 
#29 (zero base) and the outNbElement will be 400-29 = 371. Meaning only the first 371 elements of out are valid, 
#and these could be calculated only starting at the 30th element of the input.
#
#As an alternative example, if you would have requested to calculate only in the "125 to 225" range (with startIdx and endIdx), 
#the outBeg will be 125 and outNbElement will be 100. (the "30" minimum required is not an issue because we dispose 
#of 125 closing price before the start of the requested range...). As you may have already understand, the "out" array 
#will be written only for its first 100 elements. The rest will be left untouched.
#
#Here is another example. In that case we want to calculate a 14 bars exponential moving average only for 1 price bar 
#in particular (say the last day of 300 price bar): 
#
#TA_Real    closePrice[300];
#TA_Real    out;
#TA_Integer outBeg;
#TA_Integer outNbElement;
#
#/* ... initialize your closing price here... */
#
#retCode = TA_MA( 299, 299, &closePrice[0], 14, TA_MAType_EMA, &outBeg, &outNbElement, &out );
#
#In that example: outBeg will be 299,  outNbElement will be 1, and only one value gets written into out.
#
#In the case that you do not provide enough data to even being able to calculate at least one value, outNbElement will be 0 
#and outBeg shall  be ignored.
#
#If the input and output of a TA function are of the same type, the caller can re-use the input buffer for storing one of the 
#output of the TA function. The following example will work:
#
##define BUFFER_SIZE 100
#TA_Real buffer[BUFFER_SIZE];
#...
#retCode = TA_MA( 0, BUFFER_SIZE-1, &buffer[0],30, TA_MAType_SMA, &outBeg, &outNbElement, &buffer[0] );
#
#Of course, the input is overwritten, but this capability diminish needs for temporary memory allocation for certain application. 
#You can assume this capability is true for all TA functions.

#3.2 Output Size
#
#It is important that the output array is large enough. Depending of your needs, you might find one of the following method useful 
#to determine the output allocation size. All these methods are consistent and works with all TA functions:

#Input Matching    allocationSize = endIdx + 1;
#Pros: Easy to understand and implement.
#Cons: Memory allocation unnecessary large when specifying small range.

#Range Matching    allocationSize = endIdx - startIdx + 1;
#Pros: Easy to implement.
#Cons: Allocation slightly larger than needed. Example: for a 30 period SMA, you will get 29 elements wasted because of the lookback.

#Exact Allocation    lookback = TA_XXXX_Lookback( ... ) ;
#temp = max( lookback, startIdx );
#if( temp > endIdx )
#   allocationSize = 0; // No output
#else
#   allocationSize = endIdx - temp + 1;
#Pros: Optimal allocation algorithm.
#Cons: Slightly more complex
#
#A function TA_XXXX_Lookback is provided for each TA function. Example: For TA_SMA, there is a TA_SMA_Lookback.
#The lookback function indicates how many inputs are consume before the first output can be calculated. 
#Example: A simple moving average (SMA) of period 10 will have a lookback of 9.

# series from "daily" data of TA_SIMULATOR
series = [ 91.500, 94.815, 94.375, 95.095, 93.780, 94.625, 92.530, 92.750, 90.315, 92.470, 96.125, 97.250, 98.500, 89.875, 91.000, 92.815, 89.155, 89.345, 91.625, 89.875, 88.375, 87.625, 84.780, 83.000, 83.500, 81.375, 84.440, 89.250, 86.375, 86.250, 85.250, 87.125, 85.815, 88.970, 88.470, 86.875, 86.815, 84.875, 84.190, 83.875, 83.375, 85.500, 89.190, 89.440, 91.095, 90.750, 91.440, 89.000, 91.000, 90.500, 89.030, 88.815, 84.280, 83.500, 82.690, 84.750, 85.655, 86.190, 88.940, 89.280, 88.625, 88.500, 91.970, 91.500, 93.250, 93.500, 93.155, 91.720, 90.000, 89.690, 88.875, 85.190, 83.375, 84.875, 85.940, 97.250, 99.875, 104.940, 106.000, 102.500, 102.405, 104.595, 106.125, 106.000, 106.065, 104.625, 108.625, 109.315, 110.500, 112.750, 123.000, 119.625, 118.750, 119.250, 117.940, 116.440, 115.190, 111.875, 110.595, 118.125, 116.000, 116.000, 112.000, 113.750, 112.940, 116.000, 120.500, 116.620, 117.000, 115.250, 114.310, 115.500, 115.870, 120.690, 120.190, 120.750, 124.750, 123.370, 122.940, 122.560, 123.120, 122.560, 124.620, 129.250, 131.000, 132.250, 131.000, 132.810, 134.000, 137.380, 137.810, 137.880, 137.250, 136.310, 136.250, 134.630, 128.250, 129.000, 123.870, 124.810, 123.000, 126.250, 128.380, 125.370, 125.690, 122.250, 119.370, 118.500, 123.190, 123.500, 122.190, 119.310, 123.310, 121.120, 123.370, 127.370, 128.500, 123.870, 122.940, 121.750, 124.440, 122.000, 122.370, 122.940, 124.000, 123.190, 124.560, 127.250, 125.870, 128.860, 132.000, 130.750, 134.750, 135.000, 132.380, 133.310, 131.940, 130.000, 125.370, 130.130, 127.120, 125.190, 122.000, 125.000, 123.000, 123.500, 120.060, 121.000, 117.750, 119.870, 122.000, 119.190, 116.370, 113.500, 114.250, 110.000, 105.060, 107.000, 107.870, 107.000, 107.120, 107.000, 91.000, 93.940, 93.870, 95.500, 93.000, 94.940, 98.250, 96.750, 94.810, 94.370, 91.560, 90.250, 93.940, 93.620, 97.000, 95.000, 95.870, 94.060, 94.620, 93.750, 98.000, 103.940, 107.870, 106.060, 104.500, 105.000, 104.190, 103.060, 103.420, 105.270, 111.870, 116.000, 116.620, 118.280, 113.370, 109.000, 109.700, 109.250, 107.000, 109.190, 110.000, 109.200, 110.120, 108.000, 108.620, 109.750, 109.810, 109.000, 108.750, 107.870 ]
print "length of series is: %s" % len(series)
def test_TA_MAX():
    retCode, begIdx, result = TA_MAX( 0, len(series)-1, series, 4 )
    assert(retCode, TA_SUCCESS)
    print begIdx, len(result)      

def test_TA_DEMA():
    retCode, begIdx, result = TA_MA(0, len(series)-1, series, 30, TA_MAType_SMA ) # default optInTimePeriod
    assert(retCode, TA_SUCCESS)
    print begIdx, len(result)

if __name__ == '__main__':
    print "TA-Lib ", TA_GetVersionString()
    test_TA_MAX()
    test_TA_DEMA()
    
