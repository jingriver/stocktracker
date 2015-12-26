# -*- coding: utf-8 -*-

import os, re
from optparse import OptionParser

from os.path import join, getsize
    
def changename(old, new, rootdir=".", sufix="jpg", pad = 3):
    fmt = "%s%0" + str(pad) + "d." + sufix    
    reobj = re.compile(old)
    for root, dirs, files in os.walk(rootdir):
        file_count = 0
        filter_files = filter(lambda(x):x.endswith(sufix), files)
        for name in filter_files:
            if old in ("*", ""):
                dst = os.path.join(root, fmt % (new, file_count))
            else:
                dst = os.path.join(root, reobj.sub(new, name))
            fname = os.path.join(root, name)
            os.rename(fname, dst)
            print dst
            file_count += 1
        
    return file_count

def createTestfiles():
    prefix = "DCS"
    newdir = os.path.join(os.getcwd(), "testcd")
    if not os.path.exists(newdir):  os.mkdir(newdir)
    fmt = "%s%0" + str(3) + "d.txt"   
    for i in range(5):
        fname = fmt % (prefix, i)        
        fullname = os.path.join(newdir, fname)
        f = open(fullname, 'w')
        f.close()


def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-s", "--sufix", dest="sufix", default="txt",
                      help="sufix of the files to be changed")
    parser.add_option("-p", "--zeropad", dest="pad", default=3,
                      help="number of zeroes padding the file name", type="int")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=True)
    parser.add_option("-V", "--version", dest="version",
                  default=1.0, type="float",)
        
    (options, args) = parser.parse_args()    
    if options.verbose:
        print "reading %s..." % options.sufix
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    
    dirname = os.path.join(os.getcwd(), args[0])
    if not os.path.exists(dirname): 
        parser.error("directory %s does not exist")      
    changename("DCS", "TCS", dirname, options.sufix, options.pad)        
    
if __name__ == "__main__":
    #createTestfiles()
    main()        
    
             