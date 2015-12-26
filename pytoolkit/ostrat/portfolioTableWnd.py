from PyQt4 import QtCore, QtGui
from options import *
from config import *

class portfolioTable(QtGui.QFrame):
    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent)
        
        vboxlayout = QtGui.QVBoxLayout(self)
        vboxlayout.setMargin(9)
        vboxlayout.setSpacing(6)

        self.portfolioTable = QtGui.QTableView(self)
        vboxlayout.addWidget(self.portfolioTable)

        hboxlayout = QtGui.QHBoxLayout()
        hboxlayout.setMargin(0)
        hboxlayout.setSpacing(6)

        spacerItem = QtGui.QSpacerItem(281,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        hboxlayout.addItem(spacerItem)

        self.tbtn_new = QtGui.QToolButton(self)
        hboxlayout.addWidget(self.tbtn_new)

        self.tbtn_open = QtGui.QToolButton(self)
        hboxlayout.addWidget(self.tbtn_open)

        self.tbtn_save = QtGui.QToolButton(self)
        hboxlayout.addWidget(self.tbtn_save)

        self.tbtn_cal = QtGui.QToolButton(self)
        hboxlayout.addWidget(self.tbtn_cal)
        
        vboxlayout.addItem(hboxlayout)

        self.tbtn_new.setText(QtGui.QApplication.translate("PortfolioTable", "New Portfolio", None, QtGui.QApplication.UnicodeUTF8))
        self.tbtn_open.setText(QtGui.QApplication.translate("PortfolioTable", "Open Portfolio", None, QtGui.QApplication.UnicodeUTF8))
        self.tbtn_save.setText(QtGui.QApplication.translate("PortfolioTable", "Save Portfolio", None, QtGui.QApplication.UnicodeUTF8))
        self.tbtn_cal.setText(QtGui.QApplication.translate("PortfolioTable", "Calculate P&L", None, QtGui.QApplication.UnicodeUTF8))

    def updateTableByModel(self, args):
        #logging.debug("updateTableByModel" + str(args[0]))
        self.portfolioTable.setUpdatesEnabled(False)
        self.portfolioTable.setUpdatesEnabled(True)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    view = portfolioTable()
    view.show()
    sys.exit(app.exec_())
