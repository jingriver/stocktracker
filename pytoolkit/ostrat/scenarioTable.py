from PyQt4 import QtCore, QtGui

class ScenariosForm(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #self.setObjectName("scenario1")

        self.hboxlayout = QtGui.QHBoxLayout(self.scenario1)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.label = QtGui.QLabel(self.scenario1)
        self.label.setObjectName("label")
        self.hboxlayout1.addWidget(self.label)

        self.le_scenarioName = QtGui.QLineEdit(self.scenario1)
        self.le_scenarioName.setObjectName("le_scenarioName")
        self.hboxlayout1.addWidget(self.le_scenarioName)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.scenarioTable = QtGui.QTableWidget(self.scenario1)
        self.scenarioTable.setObjectName("scenarioTable")
        self.vboxlayout1.addWidget(self.scenarioTable)
        self.hboxlayout.addLayout(self.vboxlayout1)        
