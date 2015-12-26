#!/usr/bin/python 

import re 
import string 
import sys, time 
import httplib 
import urllib2 
from xml.dom import minidom 

from testHttp import httpConnection

## CGI Version 
#import cgi 
#import cgitb; cgitb.enable() 
#form = cgi.FieldStorage() # holds data from form 
#feedname = form["selection"].value 

## PHP Version 
#feedname = sys.argv[1] 

# feedname = "Spiegel" 
# feedname = "GuardianWorld" 

def listinfo(type): 
    infofile = "feedlist." + type 
    datafile = open(infofile, "r") 
    line = datafile.readline() 

    record = {} 

    while line:         
        if not line.startswith("#"):
            data = string.split(line, ';') 
            feedname = data[0] 
            address = data[1] 
            record[feedname] = address 
        line = datafile.readline() 

    return record 

feedinfo = listinfo("dat") 

class ModelFeed: 

    def __init__(self): 
        self.data = [] 

    def feeddata (self, feedname): 
        feedaddress = feedinfo[feedname]
        return feedaddress 

    def links (self, address): 
        conn = httpConnection()
        file_feed = conn.getHtml(address)
#        file_request = urllib2.Request(address) 
#        file_opener = urllib2.build_opener() 
#        file_feed = file_opener.open(file_request).read() 
        file_xml = minidom.parseString(file_feed) 

        item_node = file_xml.getElementsByTagName("item") 

        linkdata = "" 
        reobj = re.compile("\*")
        for item in item_node: 
            #title = item.childNodes[1] 
            #link = item.childNodes[3] 
            title = item.getElementsByTagName("title")[0]
            link = item.getElementsByTagName("link")[0]
            
            ftitle = title.firstChild.data 
            flink = link.firstChild.data 

            if reobj.search(flink):
                flink = reobj.split(flink)[1]

            linkdata = linkdata + "<a href=\"" + flink + "\" target=\"target\">" + ftitle + "</a><br>\n" 
            #linkdata = linkdata + ftitle + "\n" 
        return linkdata 

    def image (self, feedname): 
        image_address = imginfo[feedname] 
        return image_address 


def inodeValue(doc, nodename): 
    dom = minidom.parseString(doc) 
    node = dom.getElementsByTagName(nodename) 
    norm = node[0].toxml() 
    node_no_xml = re.sub('(<title>)|(<\/title>)|(<link>)|(<\/link>)|(<url>)|(</url>)', '', norm) 
    value = str(node_no_xml) 
    print value 
    return value 


def dnodeValue(doc, nodename): 
    dom = minidom.parseString(doc) 
    node = dom.getElementsByTagName(nodename) 
    norm = node[0].toxml() 
    node_no_xml = re.sub('(<title>)|(<\/title>)|(<link>)|(<\/link>)|(<description>)|(<\/description>)', '', norm) 
    value = str(node_no_xml) 
    print value 
    return value 

def bodyfn(feedname): 
    feed = ModelFeed() 
    feedurl = feed.feeddata(feedname) 
    body = feed.links(feedurl)
    return body 
     
def main(): 
    t1 = time.time()    
    f = open("rss.html","w")
    
    f.write("<html>\n")
    f.write("<head>\n")
    f.write("""<meta http-equiv="Content-Type" content="text/html; charset="utf-8">\n""")
    f.write("</head>\n")
    for feedname in feedinfo:
        #print feedname + "\n"
        f.write(feedname + "<br>\n")
        
        body = bodyfn(feedname) 
        output = body.encode("utf-8") 
        #print output 
        f.write(output + "<br>\n")
    f.write("</html>\n")    
    f.close()
    t2 = time.time()
    print 'rssreader took %0.3f s' % ((t2-t1))

def retest():
    s = "This is \\section 5, not \\Setion 6"
    print s
    p = re.compile(r'\\se(c?)tion\b', re.I)
    m = p.search(s)
    l = p.findall(s)
    if m:
        print m.group(), m.groups(),m.start(),m.end(),m.span()
        print l
    
    #back Backreferences   
    p = re.compile(r'(\b\w+)\s+\1')
    print p.search('Paris in the the spring').group()
    #Named groups 
    p = re.compile(r'(?P<word>\b\w+)\s+(?P=word)')
    m = p.search('Paris in the the spring')
    print m.group()
    print "[%s]" % m.group('word'), m.groups()

    #(?P<name>...) defines a named group, (?P=name) is a backreference to a named group
    #(?:...) defines a non-capturing group
    m = re.match("([abc])+", "abc")
    print m.group(1),m.groups()

    m = re.match("(?:[abc])+", "abc")
    print m.groups()
        
    InternalDate = re.compile(r'INTERNALDATE "'
        r'(?P<day>[ 123][0-9])-(?P<mon>[A-Z][a-z][a-z])-'
        r'(?P<year>[0-9][0-9][0-9][0-9])'
        r' (?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9])'
        r' (?P<zonen>[-+])(?P<zoneh>[0-9][0-9])(?P<zonem>[0-9][0-9])'
        r'"')
    m = InternalDate.match(r'INTERNALDATE "12-Jan-2001 01:21:32 +0223" is now')
    print m.group()
    
    #Positive lookahead assertion (?=...)
    #Negative lookahead assertion (?!...)
    p = re.compile(r'.*[.](?=bat$|exe$).*$')
    print p.search('test.bat').group()
    
    #\W non-alphanumeric characters
    #p = re.compile(r'\W+')
    p = re.compile("\W+")
    print p.split('This is a test, short and sweet, of split().')
    print p.sub('\n', 'This... is a test.')
    print p.subn('\n', 'This... is a test.')
    
    p = re.compile(r'(\W+)')
    print p.split('This... is a test.')    

    p = re.compile('section{([^}]*)}')
    str1 = 'section{First} section{second}'
    print p.sub(r'subsection{\1}',str1)

    p = re.compile('section{ (?P<sname> [^}]* ) }', re.VERBOSE)
    print p.sub(r'subsection{\1}',str1)
    print p.sub(r'subsection{\g<1>}',str1)
    print p.sub(r'subsection{\g<sname>}',str1)
    
    #replacement can also be a function, which gives you even more control. 
    #If replacement is a function, the function is called for every 
    #non-overlapping occurrence of pattern. On each call, the function 
    #is passed a MatchObject argument for the match and can use this information 
    #to compute the desired replacement string and return it. 
    p = re.compile(r'\d+')
    print p.sub(hexrepl, 'Call 65490 for printing, 49152 for user code.')

    #embedded modifiers in the pattern, i.e. (?i)
    print re.sub("(?i)b+", 'c', 'black Blue')

    #Greedy .* versus Non-Greedy (*?, +?, ?? or (m,n))
    #{0,} is the same as *, {1,} is equivalent to +, and {0,1} is the same as ?
    #"." matches anything except a newline character, and there's an alternate mode (re.DOTALL) where it will match even a newline.
    #"." is often used where you want to match ``any character''. 

    s = '<html><head><title>Title</title>'
    print re.match('<.*>', s).span()
    print re.match('<.*>', s).group()
    print re.match('<.*?>', s).group()
        
def hexrepl( match ):
    "Return the hex string for a decimal number"
    value = int( match.group() )
    return hex(value)

if __name__ == "__main__": 
    main()
    retest()