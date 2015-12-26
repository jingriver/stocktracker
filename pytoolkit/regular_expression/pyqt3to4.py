import re, sys, os
from subprocess import *

QT_IMPORT = {re.compile(r"\bfrom qt import\b"):"from PyQt4.Qt import",
     re.compile(r"\bfrom qttable import\b"):"#from qttable import",
     re.compile(r"\bfrom qtcanvas import\b"):"#from qtcanvas import"}

QT_CLS = {re.compile(r"\bQCanvasText\b"):"QGraphicsSimpleTextItem", 
	  re.compile(r"\bQTable\b"):"QTableWidget",
      re.compile(r"\bQDragObject\b"):"QMimeData",
      re.compile(r"\bQIconDrag\b"):"QListWidget",
      re.compile(r"\bQIconView\b"):"QListWidget",
      re.compile(r"\bQTableItem\b"):"QTableWidgetItem",
      re.compile(r"\bQListViewItem\b"):"QListWidgetItem",
      re.compile(r"\bQCanvas\b"):"QGraphicsScene",
      re.compile(r"\bQCanvasView\b"):"QGraphicsView",
      re.compile(r"\bQCanvasEllipse\b"):"QGraphicsEllipseItem",
      re.compile(r"\bQCanvasRectangle\b"):"QGraphicsRectItem",
      re.compile(r"\bQDockWindow\b"):"QDockWidget",
      re.compile(r"\bexec_loop\b"):"exec_",
      re.compile(r"\bQPopupMenu\b"):"QMenu",
      re.compile(r"\bsetNumCols\b"):"setColumnCount",
      re.compile(r"\bPYSIGNAL\b"):"SIGNAL",
      re.compile(r"\bsetOn\b"):"setChecked",
      re.compile(r"\bsetCaption\b"):"setWindowTitle",
      #re.compile(r"\binsertItem\b"):"addItem",
      #re.compile(r"\bsetCurrentItem\b"):"setCurrentIndex",
      re.compile(r"""\bnumRows\(\)"""):"rowCount()",
      re.compile(r"""\bnumCols\(\)"""):"columnCount()",
            
      }

#setWindowIcon(QtGui.QPixmap("image0"))
#setWindowIcon(QtGui.QIcon(QtGui.QPixmap("image0")))

def replace_emit(matchstr):
    newstr = matchstr
    rawstr = r"""emit\s*\(\s*SIGNAL\s*\([\s,\w,\",\']+\)\s*,\s*(\([\w,\,\s,\",\',\.]*\))"""
    compile_obj = re.compile(rawstr)
    match_obj = compile_obj.search(newstr)    
    while match_obj: 
        all_groups = match_obj.groups()
        
        # Retrieve group(s) by index
        group_1 = match_obj.group(1)       
        if group_1[0]=="(" and group_1[0]=="(":    
            repl=group_1[1:-1]
            group_1 = "\(" + repl + "\)"
            repl = repl.strip()
            if repl=="":
                group_1 = "\s*,\s*\(" + repl + "\)"
            elif repl[-1]==",":            
                repl = repl[:-1]    
        print "[%s]----[%s]" % (group_1, repl)                    
        # Replace string
        newstr = re.sub(group_1,repl, newstr)
        match_obj = compile_obj.search(newstr)        
    return newstr        
    
def replace_gen_class(s):
    #s = ' from genchartitemarroweditor import genChartItemArrowEditor'
    #p = re.compile(r'from (?P<fname>\b\w+) import')
    p = re.compile(r'from \bgen(\w+) \bimport \bgen(\w+)')
    ms = p.findall(s)
    clsnames = []
    for m in ms:
        cname = 'gen'+m[1]
        clsnames.append(cname)

    newstr  = p.sub(r'from gen\1 import Ui_gen\2', s)    
    for c in clsnames:
        rawstr = r"""(\b%s.__init__(.*))""" % c
        p = re.compile(rawstr)
        m = p.search(newstr)
        if m:
            print m.groups()
            newstr = p.sub(r'\1;self.setupUi(self)', newstr)        
    for c in clsnames:
        newstr = re.sub(r'\b(%s)\b' % c, 'Ui_'+c,newstr)
    return newstr

def replace_name(s, d):
    newstr = s
    for p in d:
        newstr = p.sub(d[p], newstr)
    return newstr
    
def replace(fname):    
    f = open(fname)
    s = f.read()    
    f.close()    
    #res = replace_gen_class(s)
    #res = replace_name(res, QT_IMPORT)
    #res = replace_name(res, QT_CLS)
    res = replace_emit(s)
    if s!=res:
        print "processing " + os.path.split(fname)[1]
	try:
	    save(fname+".bak", s)
	    save(fname, res)
	except:
	    pass
    
def save(fname, content):
    f = open(fname, 'w')
    f.write(content)
    f.close()    

def dirpy(dirname):
    try:
	fnames = os.listdir(dirname)
	fnames = filter(lambda x: str(x).lower().endswith('py'), fnames)
	if 'pyqt3to4.py' in fnames: fnames.remove('pyqt3to4.py')
	#fnames = filter(lambda x: str(x)!='pyqt3to4.py', fnames)
	fnames = map(lambda x:os.path.join(dirname,x), fnames)
    except:
	fnames = [dirname]
    map(replace, fnames) 
        
if __name__=='__main__':
    dirpy(sys.argv[1])
    #f = sys.argv[1]
    #print f
    #f = 'chartitem.py'
    #replace(f)
