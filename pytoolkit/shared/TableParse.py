import re

def tag_maker(tag, close_tag=None):
    "Make regexes that match HTML tags"
    if not close_tag: close_tag = tag
    return re.compile(r"<%s[^>]*>(.*?)</%s[^>]*>" % (tag, close_tag), 
                      re.I | re.M | re.S)

def ent_maker(ent):
    "Make regexes that match entities"
    return re.compile("&%s;?" % ent, re.I)

tbl = tag_maker('table')
hdr = tag_maker('th', 't(?:r|h|able)')
row = tag_maker('tr', 't(?:r|able)')
cel = tag_maker('td', 't(?:d|r|able)')
tag = re.compile(r"<[^>]*>", re.M | re.S)
div = tag_maker('div')

ent = {}

for (old, new) in (('amp', '&'), ('lt', '<'), ('gt', '>'), ('nbsp', ' ')):
    ent[ent_maker(old)] = new

def clean(str):
    'Removes tags and surrounding whitespace' 
    t = tag.sub('', str)
    for pat, repl in ent.items():
        t = re.sub(pat, repl, t)
    return t.strip()

def parse(str, head=None, cleaner=clean):
    """Parse a string, given optionally a list of header entries:

    parse('<HTML>...(snip)...</HTML>', ['first name', 'last name'])
    
    A function to cleanup the HTML may be specified if you don't like
    the behavior of the original one.  It will return a list of lists."""
    newtbl = []
    tbls = tbl.findall(str)
    for t in tbls:
        header = [cleaner(h) for h in hdr.findall(t)]
        if head and head != header: continue
        else:
            newtbl.append(header)
            rows = row.findall(str)
            for r in rows:
                newrow = []
                cells = cel.findall(r)
                for c in cells: newrow.append(cleaner(c))
                newtbl.append(newrow)
            return newtbl
    else: return None 

def parseDiv(str):
    """Parse a string, given optionally a list of header entries:

    parse('<div>...(snip)...</div>', ['first name', 'last name'])
    
    A function to cleanup the HTML may be specified if you don't like
    the behavior of the original one.  It will return a list of lists."""
    newtbl = []
    tbls = div.findall(str)
    for t in tbls:
        newtbl.append(t)
    return newtbl 
    
href_tag = re.compile("<a href*")

def clean_but_href(str):
    'Removes tags and surrounding whitespace'
    if href_tag.search(str):
        t = str
    else: 
        t = tag.sub('', str)
    for pat, repl in ent.items():
        t = re.sub(pat, repl, t)
    return t.strip()

def parse_but_href(str, head=None, cleaner=clean_but_href):
    return parse(str, head, cleaner)

import htmllib, formatter
class LinksExtractor(htmllib.HTMLParser): # derive new HTML parser
    def __init__(self, formatter = formatter.NullFormatter()):        # class constructor
        htmllib.HTMLParser.__init__(self, formatter)  # base class constructor
        self.links = []        # create an empty list for storing hyperlinks
        self.descripts = []

    def start_a(self, attrs):  # override handler of <A ...>...</A> tags
        # process the attributes
        if len(attrs) > 0:
            for attr in attrs:
                if attr[0]=="href" :         # ignore all non HREF attributes                    
                    self.links.append(attr[1]) # save the link info in the list

    def handle_data(self, data):
        "Handle the textual 'data'."
        self.descripts.append(data.strip())
        
    def get_links(self):        
        return zip(self.descripts, self.links)

if __name__ == '__main__':
    print parse_but_href       