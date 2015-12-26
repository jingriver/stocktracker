def synchronized(meth):
    def new(arg1, arg2):
        print "synchronized"
        return meth(arg1, arg2)
    return new

def logging(meth):
    def new(arg1, arg2):
        print "logging"
        return meth(arg1, arg2)
    return new

@synchronized
@logging
def myfunc(arg1, arg2):
    print arg1, arg2
# decorators are equivalent to ending with:
#    myfunc = synchronized(logging(myfunc))
# Nested in that declaration order

myfunc("arg1", "arg2")

def arg_sayer(what):
    def what_sayer(meth):
        def new(self, *args, **kws):
            print what
            return meth(self, *args, **kws)
        return new
    return what_sayer

def FooMaker(word):
    class Foo(object):
        @arg_sayer(word)
        def say(self): pass
    return Foo()

foo1 = FooMaker('this')
foo2 = FooMaker('that')
print type(foo1),; foo1.say()  # prints: <class '__main__.Foo'> this
print type(foo2),; foo2.say()  # prints: <class '__main__.Foo'> that