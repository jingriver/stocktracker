import new

def curry(*args, **kwargs):
    function, args = args[0], args[1:]
    if args and kwargs:
        def result(*rest, **kwrest):
            combined = kwargs.copy()
            combined.update(kwrest)
            return function(*args + rest, **combined)
    elif args:
        if len(args) > 1:
            def result(*rest, **kwrest):
                return function(*args + rest, **kwrest)
        else:
            # Special magic: make a bound object method on the arg
            return new.instancemethod(function, args[0], object)
    elif kwargs:
        def result(*rest, **kwrest):
            if kwrest:
                combined = kwargs.copy()
                combined.update(kwrest)
            else:
                combined = kwargs
            return function(*rest, **combined)
    else:
        return function
    return result

def cheeseshop(kind, *arguments, **keywords):
    print "-- Do you have any", kind, '?'
    print "-- I'm sorry, we're all out of", kind
    for arg in arguments: print arg
    print '-'*40
    keys = keywords.keys()
    keys.sort()
    for kw in keys: print kw, ':', keywords[kw]
    
cheeseshop('wood')    
