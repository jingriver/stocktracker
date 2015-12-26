from __future__ import nested_scopes
#Coroutines are more generic than subroutines. The lifespan of subroutines is dictated by last in, first out (the last subroutine called is the first to return); in contrast, the lifespan of coroutines is dictated entirely by their use and need.
#
#The start of a subroutine is the only point of entry. Subroutines can return only once; in contrast, coroutines can return (yield) several times. The start of a coroutine is the first point of entry and subsequent points of entry are following yield commands. Practically, yielding returns the result to the calling coroutine and gives it back control, like an usual subroutine. However, the next time the coroutine is called, the execution does not start at the beginning of the coroutine but just after the yield call.
#
#Here's a simple example of how coroutines can be useful. Suppose you have a consumer-producer relationship where one routine creates items and adds them to a queue and another removes items from the queue and uses them. For reasons of efficiency, you want to add and remove several items at once. The code might look like this:
#
#var q := new queue
#
#coroutine produce
#    loop
#        while q is not full
#            create some new items
#            add the items to q
#        yield to consume
#
#coroutine consume
#    loop
#        while q is not empty
#            remove some items from q
#            use the items
#        yield to produce

#Coroutines and generators
#Generators are also a generalisation of subroutines, but with at first sight less expressive power than coroutines; since generators are primarily used to simplify the writing of iterators, the yield statement in a generator does not specify a coroutine to jump to, but rather passes a value back to a parent routine. However, it is still possible to implement coroutines on top of a generator facility, with the aid of a top-level dispatcher routine that passes control explicitly to child generators identified by tokens passed back from the generators:

#var q := new queue
#
#generator produce
#    loop
#        while q is not full
#            create some new items
#            add the items to q
#        yield consume
#
#generator consume
#    loop
#        while q is not empty
#            remove some items from q
#            use the items
#        yield produce
#
#subroutine dispatcher
#    var d := new dictionary<generator ? iterator>
#    d[produce] := start produce
#    d[consume] := start consume
#    var current := produce
#    loop
#        current := next d[current]


#In computer science, a generator is a special routine that can be used to control the iteration behaviour of a loop. A generator is very similar to a function that returns an array, in that a generator has parameters, can be called, and generates a sequence of values. However, instead of building an array containing all the values and returning them all at once, a generator yields the values one at a time, which requires less memory and allows the caller to get started processing the first few values immediately.
#In Python, a generator can be thought of as an iterator that contains a frozen stack frame. Whenever the iterator's next() method is called, Python resumes the frozen frame, which executes normally until the next yield statement is reached. The generator's frame is then frozen again, and the yielded value is returned to the caller.
def countfrom(n):
    while True:
        yield n
        print "insdie countfrom [%d]" % n
        n += 1
 
# Example use: printing out the integers from 10 to 20.
# Note that this iteration terminates normally, despite countfrom() being
# written as an infinite loop. 
for i in countfrom(10):
    if i <= 20:
        print i
    else:
        break
 
# Another generator, which produces prime numbers indefinitely as needed. 
def primes():
    n = 2
    p = []
    while True:
        if not any( [n % f == 0 for f in p] ):
            yield n
            p.append( n )
        n += 1
 
f = primes()
print f
for i in range(10):
    print f.next()
    
def echo(value=None):
    print "Execution starts when 'next()' is called for the first time."
    try:
        while True:
            try:
                value = (yield value)
            except GeneratorExit:
                # never catch GeneratorExit
                raise
            except Exception, e:
                value = e
                print value
    finally:
        print "Don't forget to clean up when 'close()' is called."
        
generator = echo(1)
print generator.next()
print generator.send(2)
generator.throw(TypeError, "spam")
print generator.next()
generator.close()
    