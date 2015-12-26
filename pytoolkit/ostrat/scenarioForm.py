from PyQt4 import QtCore, QtGui

class ScenariosForm(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.name = "Scenario 1"

        self.hboxlayout = QtGui.QHBoxLayout(self)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.label = QtGui.QLabel(self)
        self.label.setObjectName("label")
        self.label.setText(self.tr("Scenario Name"))
        self.hboxlayout1.addWidget(self.label)

        self.le_scenarioName = QtGui.QLineEdit(self)
        self.le_scenarioName.setObjectName("le_scenarioName")
        self.hboxlayout1.addWidget(self.le_scenarioName)

        self.errormsg = QtGui.QLabel(self)
        self.errormsg.setText(self.tr("The name already exists!"))
        #self.errormsg.setForegroundRole(QtGui.QPalette.BrightText)
        self.hboxlayout1.addWidget(self.errormsg)
        self.errormsg.hide()

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.scenarioTable = QtGui.QTableWidget(self)
        self.scenarioTable.setObjectName("scenarioTable")
        self.vboxlayout1.addWidget(self.scenarioTable)
        self.hboxlayout.addLayout(self.vboxlayout1)        
        
        self.scenarioTable.clear()
        self.scenarioTable.setColumnCount(3)
        self.scenarioTable.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(self.tr("Option ID"))
        self.scenarioTable.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(self.tr("Yield Alpha(bp)"))
        self.scenarioTable.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(self.tr("Yield Beta(bp)"))
        self.scenarioTable.setHorizontalHeaderItem(2,headerItem2)
