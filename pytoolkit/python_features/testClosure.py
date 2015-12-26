#UnboundLocalError: local variable 'totalSquares' referenced before assignment
#def totalSquares(numlist):
#    totalSquares = 0
#
#    def addSqrToTotal(x): totalSquares=totalSquares+square(x)
#    map(addSqrToTotal,numlist)
#
#    return totalSquares
#
#totalSquares([1,2,3])

def make_power_operator(n): return lambda x: x**n
square = make_power_operator(2)
print square(3)

class testClosure:
    def totalSquares(self, numlist):
        self.totalSquares = 0
    
        def addSqrToTotal(x): self.totalSquares=self.totalSquares+x*x
        map(addSqrToTotal,numlist)
    
        return self.totalSquares
    
    def filterOdds(self, numlist):
        def is_even(n): return n%2==0
        return filter(is_even, numlist)

t = testClosure()
print t.totalSquares([1,2,3])
print t.filterOdds([1,2,3])

    