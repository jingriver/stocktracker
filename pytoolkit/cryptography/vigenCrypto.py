#Encryption algorithms transform their input data, or plaintext, in some way that 
#is dependent on a variable key, producing ciphertext. This transformation can 
#easily be reversed, if (and, hopefully, only if) one knows the key. 
#The key can be varied by the user or application and chosen from some very large space of possible keys. 

STARTNUM = 97
ALPHALEN = 26
ASCIIOFFSET = 10
from types import *

def generateAlphabets():
    res = []
    for i in range(STARTNUM,STARTNUM+ALPHALEN):
        res.append(chr(i))     
    return res

def shiftAlphabets(alphalist, offset):
    if type(offset) is not IntType:
        raise "Offset [%s] must be a integer" % str(offset) 
    res = alphalist[offset:]
    res.extend(alphalist[0:offset])    
    return res

class vigenCrypto():
    def __init__(self, key="king"):
        self.setkey(key)
        self.alphabets = generateAlphabets()
        self.table=[self.alphabets]
        for i in range(1,ALPHALEN+1):
            self.table.append(shiftAlphabets(self.alphabets,i))
        
    def __str__(self):
        res = ""
        for x in self.table:
            res += " ".join(x) + "\n"        
        return res

    def setkey(self, key):
        self.key = key
        self.keyoffset = [ord(x)-STARTNUM for x in key] 
        
    def encode(self, text):
        res = ""
        text = text.lower()
        cnt = 0
        for x in text:
            if cnt==len(self.key):cnt = 0
            i = ord(x)-STARTNUM
            if i<0 or i>ALPHALEN:
                y = x
            else:                
                y = self.table[self.keyoffset[cnt]][i]
                #print "%s-%s-%s" % (self.key[cnt], x, y)         
                cnt+=1
            res +=chr(ord(y)+ASCIIOFFSET)
        return res

    def decode(self, text):
        res = ""
        cnt = 0
        for x in text:
            x = chr(ord(x)-ASCIIOFFSET)
            if cnt==len(self.key):cnt = 0
            i = ord(x)-STARTNUM
            if i<0 or i>ALPHALEN:
                y = x
            else:
                y = self.alphabets[self.table[self.keyoffset[cnt]].index(x)]
                #print "%s-%s-%s" % (self.key[cnt], x, y)         
                cnt+=1
            res +=y
        return res
 
if __name__ == '__main__':
    c = vigenCrypto("kingofsoccer")
    #print c
    plaintext = "The Sun and the Man in the Moon"
    ciphertext = c.encode(plaintext)
    print ciphertext
    print c.decode(ciphertext)
    f = open("string_tran.py")
    plaintext = f.read()
    f.close()
    ciphertext = c.encode(plaintext)
    f = open("ctext.txt", 'w')
    f.write(ciphertext)
    f.close
    #print ciphertext
    f = open("ctext.txt", 'r')
    ciphertext = f.read()
    f.close()
    print c.decode(ciphertext)
    