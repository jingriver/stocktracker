import os
from os.path import join, getsize

def fcount(fname):
    cnt = 0
    f = open(fname, 'r')
    text = f.read().split('\n')
    f.close()
    for line in text:
        line = line.strip()
        #if len(line)>0 and not line.startswith("#"): cnt+=1
        if len(line)>0: cnt+=1
    print fname, cnt
    return cnt
    
def dcount(rootdir="."):
    total_count = 0
    file_count = 0
    for root, dirs, files in os.walk(rootdir):
#        print root, "consumes",
#        print sum(getsize(join(root, name)) for name in files),
#        print "bytes in", len(files), "non-directory files"
        
        pyfiles = filter(lambda(x):x.endswith("py"), files)
        for name in pyfiles:
             fname = os.path.join(root, name)
             total_count += fcount(fname)
             file_count += 1
        
    return total_count, file_count

print dcount("C:/dqpython/unite/main/package")                 