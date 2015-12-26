import weakref
class Object:
    pass

o = Object()
r = weakref.ref(o)
o2 = r()
print o is o2
