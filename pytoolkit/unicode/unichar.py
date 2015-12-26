import string, codecs

CYRILLIC_BASE=0x0400

uList=[]
for c in range(255):
    uList.append(unichr(CYRILLIC_BASE + c))

# Combine the characters into a string - this is
# faster than doing u=u+uniChr(c) in the loop
u=u"" + string.join(uList,"")

f=codecs.open("cyrillic1.ut8", "aw+", "utf-8")
f.write(u)
f.flush()

f=open("cyrillic2.ut8", "aw+")
f.write(u.encode("utf-8"))
f.flush()
