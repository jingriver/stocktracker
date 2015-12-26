from PyQt4 import QtCore, QtGui
from options import *
from config import *
#import weakref

class optionInputWnd(QtGui.QFrame):
    def __init__(self, opts, parent = None):
        QtGui.QFrame.__init__(self, parent)
        
        vboxlayout = QtGui.QVBoxLayout(self)
        vboxlayout.setMargin(9)
        vboxlayout.setSpacing(6)

        self.stackedWidget = QtGui.QStackedWidget(self)
        self.optDlg = []
        for opt in opts:
            dlg = inputDialog(opt)            
            self.optDlg.append(dlg)
            self.stackedWidget.addWidget(dlg)
            self.connect(dlg.model, QtCore.SIGNAL("ModelChanged"), self.updateTabByModel)
            
        vboxlayout.addWidget(self.stackedWidget)
        
    def updateTabByModel(self, args):
        #logging.debug("updateTabByModel")
        opt = args[0]
        self.setUpdatesEnabled(False)
        self.setUpdatesEnabled(True)        
        
    def updateTab(self, opt):
        self.setUpdatesEnabled(False)
        flag = False
        for dlg in self.optDlg:
            if dlg.option.type==opt.type:
                dlg.updateOption(opt)
                self.stackedWidget.setCurrentIndex(self.optDlg.index(dlg))
                flag = True
                break
            
        if not flag:
            logging.error("unknown option type")
            
        self.setUpdatesEnabled(True)

class inputDialog(QtGui.QWidget):
    def __init__(self, option, parent = None, edit=-1):
        QtGui.QWidget.__init__(self, parent)
        self.option = option
        self.edit = edit
        
        self.tradeDate = option.tradeDate
        self.exerciseType = option.exerciseType
        self.horizonDate = option.horizonDate
        
        vboxlayout = QtGui.QVBoxLayout(self)
        vboxlayout.setMargin(9)
        vboxlayout.setSpacing(6)

        self.tableView = QtGui.QTableView(self)
        
        vboxlayout.addWidget(self.tableView)
        
        self.model = PropertyModel(self.option, self)
        self.tableView.setModel(self.model)
        self.tableView.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        
        self.delegate = PropertyDelegate(self.option, self.tableView)
        self.tableView.setItemDelegate(self.delegate)

        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
                
    def updateOption(self, opt):
        assert (isinstance(opt, option))
        #self.option = weakref.ref(opt)
        #logging.debug("dialog update option")
        self.model.updateOption(opt)
        self.delegate.setOptionDates(opt)

class PropertyModel(QtCore.QAbstractTableModel):
    def __init__(self, option, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.tblheader = [self.tr('Properties'),self.tr('Values')]
        self.numCol = len(self.tblheader)
        self.rnames = option.property_names
        self.option = None
        self.updateOption(option)

    def updateOption(self, opt):
        assert (isinstance(opt, option))
        #logging.debug("model update option %s" % str(opt))
        if self.option != opt:
            self.option = opt
            self.connect(self.option, QtCore.SIGNAL("OptionChanged"), self, QtCore.SIGNAL("ModelChanged"))
            self.option.emit(QtCore.SIGNAL("OptionChanged"), (self.option,))
        
    def rowCount(self, parent):
        return len(self.rnames)

    def columnCount(self, parent):
        return self.numCol
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
	    if (orientation == QtCore.Qt.Horizontal):
		return QtCore.QVariant(self.tblheader[section])
        return QtCore.QVariant()
    
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        rtips = self.option.tips
        rvalues = self.option.getProperties()
        if role == QtCore.Qt.DisplayRole:
            cidx = index.column()
            idx = index.row()
            if cidx == 0:                
                if self.rnames[idx] is not None:
                    return QtCore.QVariant(self.rnames[idx])
                else:
                    return QtCore.QVariant()
            elif cidx == 1:
                if rvalues[idx] is not None:
                    if idx == OptionColumn.cpsf(self.option.type):
                        dictmp = OptionColumn.cpsfVal(self.option.type)
                        return QtCore.QVariant(dictmp[rvalues[idx]])
                    elif idx == OptionColumn.exerciseType(self.option.type):
                        return QtCore.QVariant(OptionColumn.ETYPEDICT[rvalues[idx]])
                    else:
                        return QtCore.QVariant(rvalues[idx])
                else:
                    return QtCore.QVariant()
        elif role == QtCore.Qt.ToolTipRole:
            #return index.model().data(index, QtCore.Qt.DisplayRole)
            return QtCore.QVariant(rtips[index.row()])
#        elif role == QtCore.Qt.TextColorRole and index.column() == 1:
#            return QtCore.QVariant(QtGui.QColor(QtCore.Qt.blue))
#        
#        elif role == QtCore.Qt.BackgroundColorRole:
#            if rowval[OptionColumn.RFRATE]>3:
#                return QtCore.QVariant(QtGui.QColor(240,220,240))
#            else:
#                return QtCore.QVariant(QtGui.QColor(220,240,240))
            
        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        
        flags = QtCore.QAbstractTableModel.flags(self, index)
        if index.column() == 0: return flags
        if index.column() == 1:
            if self.option.type in ('F','T') and index.row()==1:
                return flags
            elif self.option.type in ('W') and index.row()==2:
                return flags
            else:
                return flags | QtCore.Qt.ItemIsEditable        
        return flags

    def setData(self, index, value, role):
        """
            whenever the properties of an option object are been changed, 
            option.setProperty will emit "optionChange" signal which will trigger the 
            model's dataChanged signal
        """
        if index.column() == 1:
            self.option.setProperty(index.row(), value.toString())
            return True
        
        return False
        
class PropertyDelegate(QtGui.QItemDelegate):
    def __init__(self, option, parent=None):
        QtGui.QItemDelegate.__init__(self,parent)
        self.setOptionDates(option)

    def sizeHint(self, option, index):
        if index.column() == 1:
            return QtCore.QSize(100,1)
        return QtGui.QItemDelegate.sizeHint(self, option, index)
        
    def setOptionDates(self, opt):
        assert(isinstance(opt, option))
        self.optionType = opt.type
        tradeDate = str2datetime(opt.tradeDate, fmt=DATEFMT)
        self.qtoday = QtCore.QDate(tradeDate.year, tradeDate.month, tradeDate.day)
        
        if opt.expireDate is not None:
	    expireDate = str2datetime(opt.expireDate, fmt=DATEFMT)
	    self.qexpireDate = QtCore.QDate(expireDate.year, expireDate.month, expireDate.day)

        if self.optionType=='W':
            swapMat_contract = str2datetime(opt.swapMat_contract, fmt=DATEFMT)
            self.qswapMat_contract = QtCore.QDate(swapMat_contract.year, swapMat_contract.month, swapMat_contract.day)        
        elif self.optionType=='S':
            swapMat_contract = str2datetime(opt.swapMat_contract, fmt=DATEFMT)
            self.qswapMat_contract = QtCore.QDate(swapMat_contract.year, swapMat_contract.month, swapMat_contract.day)
            
            issueDate = str2datetime(opt.issueDate, fmt=DATEFMT)
            self.qissueDate = QtCore.QDate(issueDate.year, issueDate.month, issueDate.day)
            
#    def paint(self, painter, option, index):            
#        QtGui.QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        if index.row() == OptionColumn.cpsf(self.optionType):
            editor = QtGui.QComboBox(parent)
            dictmp = OptionColumn.cpsfVal(self.optionType)
            for t in dictmp:
                editor.addItem(dictmp[t],  QtCore.QVariant(t))
            editor.installEventFilter(self)
            self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
            return editor        

        if index.row() == OptionColumn.exerciseType(self.optionType):
            editor = QtGui.QComboBox(parent)
            dictmp = OptionColumn.ETYPEDICT
            for t in dictmp:
                editor.addItem(dictmp[t],  QtCore.QVariant(t))
            editor.installEventFilter(self)
            self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
            return editor        
        
        if (index.row() == OptionColumn.EXPDATE or 
            (self.optionType in ('W','S') and index.row() in (OptionColumn.MATURITY, OptionColumn.issueDate(self.optionType)))):
            editor = QtGui.QDateEdit(parent)
            editor.setDisplayFormat(QTDATEFMT)
            editor.setCalendarPopup(True)
            editor.setDate(self.qtoday)
            editor.installEventFilter(self)
            self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
            return editor        
        
        editor = QtGui.QItemDelegate.createEditor(self, parent, option, index)
        editor.setText(index.model().data(index, QtCore.Qt.DisplayRole).toString())
        self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
        return editor        

    def setEditorData(self, editor, index):
        if editor is not None:
            if index.row() == OptionColumn.cpsf(self.optionType):
                s = index.model().data(index, QtCore.Qt.DisplayRole).toString()
                editor.setCurrentIndex(editor.findText(s))
            elif index.row() == OptionColumn.exerciseType(self.optionType):
                s = index.model().data(index, QtCore.Qt.DisplayRole).toString()
                editor.setCurrentIndex(editor.findText(s))
            elif index.row() == OptionColumn.EXPDATE:
                editor.setDate(self.qexpireDate)
            elif self.optionType in ('S','W'):
                if index.row() == OptionColumn.MATURITY:
                    editor.setDate(self.qswapMat_contract)
                elif index.row() == OptionColumn.issueDate(self.optionType):
                    editor.setDate(self.qissueDate)
            else:
                QtGui.QItemDelegate.setEditorData(self, editor, index)
    
    def setModelData(self, editor, model, index):
#        if not editor.isModified():
#            return        
        if index.row()==OptionColumn.cpsf(self.optionType):
            value = editor.itemData(editor.currentIndex())
            if value.toString() != model.data(index, QtCore.Qt.DisplayRole).toString():
                model.setData(index, value, QtCore.Qt.UserRole)            
            
        elif index.row()==OptionColumn.exerciseType(self.optionType):            
            value = editor.itemData(editor.currentIndex())
            if value.toString() != model.data(index, QtCore.Qt.DisplayRole).toString():
                model.setData(index, value, QtCore.Qt.UserRole)            
        else:
            value = editor.text()
            if value:
                model.setData(index, QtCore.QVariant(value), QtCore.Qt.UserRole)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL("commitDate"), (editor,))
        self.emit(QtCore.SIGNAL("closeEditor"), (editor,QtGui.QAbstractItemDelegate.EditNextItem))
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    s = swaption(tradeDate='1/1/2007', exerciseType='E', horizonDate='1/1/2007')    
    f = futuresOption(tradeDate='2/1/2007', exerciseType='E', horizonDate='1/1/2007')    
    t = treasureOption(tradeDate='2/1/2007', exerciseType='E', horizonDate='1/1/2007')    
    view = optionInputWnd(s, f, t)
    view.show()
    sys.exit(app.exec_())
            
