import string

def Translator(frm='', to='', delete='', keep=None):
    allchars = string.maketrans('','')
    if len(to) == 1:
        to = to * len(frm)
    trans = string.maketrans(frm, to)
    if keep is not None:
        delete = allchars.translate(allchars, keep.translate(allchars, delete))
    def callable(s):
        return s.translate(trans, delete)
    return callable

trans = Translator(delete='abcd', keep='cdef')
print trans('abcdef')

allChar = string.uppercase + string.lowercase

def shiftAsciiValue(originStr, offset):
    allChar = string.uppercase + string.lowercase
    res = ""     
    for ch in allChar:
        res += chr(ord(ch)+offset)
    #table = string.maketrans(string.lowercase, string.lowercase[2:] + string.lowercase[:2])
    table = string.maketrans(allChar, res)
    return originStr.translate(table)

def shiftBackAsciiValue(originStr, offset):
    allChar = string.uppercase + string.lowercase
    res = ""     
    for ch in allChar:
        res += chr(ord(ch)+offset)
    #table = string.maketrans(string.lowercase, string.lowercase[2:] + string.lowercase[:2])
    table = string.maketrans(res, allChar)
    return originStr.translate(table)

ASCIIOFFSET = 20
originStr = "allChar = string.uppercase + string.lowercase"
encodes = shiftAsciiValue(originStr, ASCIIOFFSET)
print shiftBackAsciiValue(encodes, ASCIIOFFSET)