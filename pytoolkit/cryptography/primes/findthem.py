#!/usr/local/bin/python
import os, time
from Crypto.Util import *
    
def findthem(max = 1000000):
    start = 5
    primes = [2,3]    

#    filename = "primes.txt"   
#    # check if primes.txt exists
#    if os.path.isfile(filename):            
#        # read in all previous primes
#        # convert to numbers
#        f = open(filename,'r')
#        snums = f.readlines()
#        f.close()
#    else:
#        print "no such file %s" % filename
#        return    
#    if snums:
#        using_file = 1        
#        for sn in snums:
#            primes.append(int(sn))
#        
#        start = primes[len(primes)-1]+1    
#    else:
#        # seed list with first two primes
#        using_file = 0
#        primes = [2,3]
#        start = 5
#        
#    # print out intial 
#    if using_file:
#        pass
#    else:
#        for p in primes:
#            print "",p
    
    #f = open(filename,'w')
    # range of numbers searching for primes
    for num in range(start, max, 2):
        #intialize not-a-prime as false
        nap = True
    
        # cycle through list of known primes
        for prime in primes:    
            # check if a previous prime divides evenly
            # into the current number -- if so the number
            # we are checking (num) is not a prime
            if (num % prime) == 0:
                nap = False
                break
            # if prime squared is bigger than the number 
            # than we don't need to check any more
            if prime*prime > num:
               break
    
        # did we determine it's not a prime
        # if not, then we found a prime
        if nap:
            # add prime to list of known primes
            primes.append(num)            
            #f.write(str(num) + '\n')             
    #f.close()
    return primes

def findprimes(n = 1000000): 
    if n==2: return [2]
    elif n<2: return []
    s=range(3,n+1,2)
    mroot = n ** 0.5
    half=(n+1)/2-1
    i=0
    m=3
    while m <= mroot:
        if s[i]:
            j=(m*m-3)/2
            s[j]=0
            while j<half:
                s[j]=0
                j+=m
        i=i+1
        m=2*i+3
    return [2]+[x for x in s if x]

def findprimeCryptolib(n=2048):
    randfunc = os.urandom
    return number.getPrime(n, randfunc)    

def Denary2Binary(n):
    '''convert denary integer n to binary string bStr'''
    bStr = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr

def int2bin(n, count=24):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

if __name__ == "__main__":
    print("program starts at: " + time.strftime('%X %x %Z'))
    t1 = time.time()    
    print len(findthem())
    t2 = time.time()
    print('program took %0.3f s' % ((t2-t1)))
    t1=t2
    res = findprimes(10**8)    
    print len(res), res[-1],res[-2],res[-1]*res[-2]

    print Denary2Binary(255)
    
    res = findprimeCryptolib(1024)
    print res
    print hex(res)
    print long(hex(res),16)
    t2 = time.time()
    print('program took %0.3f s' % ((t2-t1)))    
    print("program ends at: " + time.strftime('%X %x %Z'))         