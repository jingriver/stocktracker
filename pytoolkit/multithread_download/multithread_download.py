import sys, re
import urllib, urllib2
from threading import Thread

class downloadThread(Thread):
    def __init__(self, url, fname):
        Thread.__init__(self)
        self.url = url
        self.fname = fname
        
    def run(self):
        try:
            print "downloading " + self.url
            #urllib.urlretrieve(self.url, self.fname)
        except:
            print "cannot download file: " + url
            print sys.exc_info()
        print "download %s finished" % self.fname

def getHtml(url):
    f = urllib2.urlopen(url)
    html = f.read()
    f.close()
    return html

def readfile(fname):
    f = open(fname, "r")
    lines = f.read()
    f.close()
    return lines    
    
rawstr = r"""(http://[a-zA-Z0-9~_:\.\/\-]*mp3)"""
m = re.compile(rawstr)
rawstr = r"""([a-zA-Z0-9]*\.mp3)"""
mf = re.compile(rawstr)

#text = readfile("d:/mp3/1.txt")
text = getHtml("http://web.wenxuecity.com/BBSView.php?SubID=tv&MsgID=382850")
lines = text.split("\n") 
dir = "d:/mp3/tv/" 
for line in lines:
    mo = m.search(line)
    if mo:       
        url = mo.group(1)        
        mfo = mf.search(url)
        if mfo:
            fname = mfo.group(1)            
            t = downloadThread(url, dir + fname)
            t.start()
        else: print "bad url %s" % url           