import enchant
d = enchant.Dict("en_US")
print d.check("Hello")
print d.check("Helo")
print d.suggest("Helo")

