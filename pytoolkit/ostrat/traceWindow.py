###########################################################################
# FILE: StatusWindow.py
#
# $Header$
###########################################################################

import sys

from PyQt4 import QtCore, QtGui

class StdoutProxy(QtCore.QObject):
    def __init__(self):
    	QtCore.QObject.__init__(self)
    	sys.stdout = self
        
    def write(self, str1):
        self.emit(QtCore.SIGNAL("textAdded"), str1)
				     
class StderrProxy(QtCore.QObject):
    def __init__(self):
    	QtCore.QObject.__init__(self)
    	sys.stderr = self
        
    def write(self, str1):
    	self.emit(QtCore.SIGNAL("textAdded"), str1)

class StatusWidget(QtGui.QTextEdit):
    def __init__ (self, parent=None):
    	QtGui.QTextEdit.__init__(self, parent)
    	self.setReadOnly(True)
    	self.stdout = StdoutProxy()
    	self.stderr = StderrProxy()
    	self.connect(self.stdout, QtCore.SIGNAL("textAdded"), self.stdoutHandler)
        self.connect(self.stderr, QtCore.SIGNAL("textAdded"), self.stderrHandler)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        clearAct = menu.addAction(self.tr("Clear"))
        clearAct.setShortcut(self.tr("Ctrl+D"))
        self.connect (clearAct, QtCore.SIGNAL("triggered()"), self.clear)        
        menu.exec_(event.globalPos())  
      
    def stdoutHandler(self, str1):
    	self.setTextColor(QtCore.Qt.blue)
    	self.append(str(str1))
        
    def stderrHandler(self, str1):
    	self.setTextColor(QtCore.Qt.red)
    	self.setFontWeight(QtGui.QFont.Bold)
    	self.append(str(str1))
        self.setFontWeight(QtGui.QFont.Normal)

class StatusDockWindow(QtGui.QDockWidget):
    def __init__(self, parent):
    	QtGui.QDockWidget.__init__(self, parent)
        self.setWindowTitle(self.tr("Trace Window"))
        self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.statusWidget = StatusWidget(self)
        self.setWidget(self.statusWidget)
#        self.setMinimumHeight(150)
        self.setMinimumWidth(250)

class Window(QtGui.QMainWindow):
    def __init__(self, parent = None):    
        QtGui.QMainWindow.__init__(self)
        self.labQuery = QtGui.QPushButton('DateQuery String')
        self.setCentralWidget(self.labQuery)
        self.errWindow = StatusDockWindow(self)
        #self.addDockWidget(Qt.NoDockWidgetArea, self.errWindow)
        self.resize(600,400)
        print sys.version
        
        self.connect(self.labQuery, QtCore.SIGNAL("clicked()"), self.errTest)
        
    def errTest(self):
        print "errTest"
        haha()
        
def run():
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()    
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()

