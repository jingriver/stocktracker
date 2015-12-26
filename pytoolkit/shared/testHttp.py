import urllib2
from config import *

class httpConnection:
    #proxy='http://webproxy.ny.jpmorgan.com:8000/'
    def __init__(self, proxy='http://approxy.jpmchase.net:8080/'):
        self.proxy = proxy
        self.setProxy()
        
    def setProxy(self):
        proxy_handler = urllib2.ProxyHandler({'http': self.proxy, 'https': self.proxy})
        #proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
        #proxy_auth_handler.add_password('realm', 'host', 'username', 'password')        
        self.opener = urllib2.build_opener(proxy_handler)
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(self.opener)

    def setAuthen(self, user='jingriver', pwd='ycxm0531'):      
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
            None, 'https://api.del.icio.us/', user, pwd
        )        
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        #opener = urllib2.build_opener(auth_handler, proxy_handler)
        self.opener.add_handler(auth_handler)
        urllib2.install_opener(self.opener)
        
        url = 'https://api.del.icio.us/v1/posts/recent'        
        xml = urllib2.urlopen(url).read()
        print xml
    
    def getHtml(self, url="http://quote.yahoo.com/d/quotes.csv?s=RVBD+USG&f=nl1vhgd1rm4kjx"):
#        req = urllib2.Request(url)
#        req.add_header('Referer', 'http://www.python.org/')
        f = urllib2.urlopen(url)
#        print f.geturl()
#        print f.info()
        html = f.read()
        f.close()
        return html
    
    def getRawdata(self, url):
        return urllib2.urlopen(url)

from formatter import AbstractFormatter, NullWriter
from htmllib import HTMLParser
import string

class myWriter(NullWriter):
    def __init__ ( self ):
        NullWriter.__init__(self)
        self._bodyText = []
        
    def send_flowing_data(self, str1):
        self._bodyText.append(str(str1))

    @property
    def bodyText(self):
        return "\n".join(self._bodyText)
    
class myHTMLParser(HTMLParser):
    def do_meta(self, attrs):
        self.metas = attrs

#    def handle_starttag(self, tag, attrs):
#        print "Encountered the beginning of a %s tag" % tag
#
#    def handle_endtag(self, tag):
#        print "Encountered the end of a %s tag" % tag

def main():
    conn = httpConnection()
    #conn.setAuthen()
    charset = 'utf-8'
    #intrday
    #http://quote.yahoo.com/d/quotes.csv?s=^DJI&f=sl1d1t1c1ohgve
    #http://download.finance.yahoo.com/d/quotes.csv?s=^DJI&f=sl1d1t1c1ohgve
    #http://finance.yahoo.com/d/quotes.csv?s=XOM+BBDb.TO+JNJ+MSFT&f=snd1l1yr
    #http://finance.yahoo.com/q/hp?s=IBM&a=00&b=2&c=1962&d=09&e=29&f=2007&g=d&z=66&y=11484
    #http://ichart.finance.yahoo.com/table.csv?s=IBM&a=00&b=2&c=1962&d=09&e=29&f=2007&g=d&ignore=.csv
    #http://ichart.finance.yahoo.com/table.csv?s=RVBD&a=0&b=2&c=1990&d=9&e=29&f=2007&g=d&ignore=.csv
    #1962/01/02:2007/10/29
    #http://www.gummy-stuff.org/Yahoo-data.htm
    url = "http://finance.google.com/finance?q=NYSE:CEO"
    url = "http://dataquery.ny.jpmorgan.com/rdi/XMLMenu"
    html = conn.getHtml(url)    
    print html
    return        
    #html=unicode(html, charset)    
    print html.encode(charset)
    mywriter = myWriter()
    abstractformatter = AbstractFormatter(mywriter)
    parser = myHTMLParser(abstractformatter)
    parser.feed(html)
    print parser.title
    print parser.metas
    #print parser.formatter.writer.bodyText

def readUnicodeFile(fname):
    import codecs
    fileObj = codecs.open(fname, "rb", "utf-8" )
    u = fileObj.read() # Returns a Unicode string from the UTF-8 bytes in the file
    print u.encode('utf-8')
    return u

def readFile(fname):
    f = open(fname)
    s = f.read()
    print s
    u=unicode(s, 'utf-8')
    print u.encode('utf-8')
    return u

def getRawHttp(host='localhost', filename='/index.html'):
    # import sys for handling command line argument 
    # import socket for network communications 
    import sys, socket 
    
    # hard-wire the port number for safety's sake 
    # then take the names of the host and file from the command line 
    port = 80 
    
    # create a socket object called 'c' 
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    # connect to the socket 
    c.connect((host, port))
    
    # create a file-like object to read 
    fileobj = c.makefile('r', 0) 
    
    # Ask the server for the file 
    fileobj.write("GET "+filename+" HTTP/1.0\n\n") 
    
    # read the lines of the file object into a buffer, buff 
    buff = fileobj.readlines() 
    
    # step through the buffer, printing each line 
    for line in buff: 
         print line 

def testHttplibGet():
    import httplib
    conn = httplib.HTTPConnection("www.python.org")
    conn.request("GET", "/index.html")
    r1 = conn.getresponse()
    print r1.status, r1.reason
    data1 = r1.read()
    print data1
    
    conn.request("GET", "/parrot.spam")
    r2 = conn.getresponse()
    print r2.status, r2.reason
    data2 = r2.read()
    print data2
    conn.close()

def testHttplibPost():
    import httplib, urllib
    params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
    headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"}
    conn = httplib.HTTPConnection("musi-cal.mojam.com:80")
    conn.request("POST", "/cgi-bin/query", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print data
    conn.close()

def testhttp2():
    import httplib2
    import socks
    
    httplib2.debuglevel=4
    h = httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 'http://webproxy.ny.jpmorgan.com', 8000))
    r,c = h.request("http://www.google.com/")
    
if __name__ == '__main__':
    main()
    #testHttplibGet()
    #getRawHttp()
    #testhttp2()    
