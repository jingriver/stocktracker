import sys
from sets import Set
from math import *

from PyQt4 import QtCore, QtGui
from PyQt4.Qwt5 import *

import resource
from genoptionCalcMainWin import Ui_optionCalcMWIN
from inputWnd import optionInputWnd
from portfolioTableWnd import portfolioTable
from settingWnd import settingWnd, curveType
from scenarioForm import ScenariosForm
     
from options import *
from simplePlot import simpleData, plPlot
from config import *
from xmlutils import *
from traceWindow import StatusDockWindow

optTypeDict={}
optTypeDict['W']='Swaption'
#optTypeDict['S']='Swaption_old'
optTypeDict['F']='Eurodollar Future Option'
optTypeDict['T']='Treasury Bonds Option'

class scenarioWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
	self.vboxlayout = QtGui.QVBoxLayout(self)

        self.tab_Scenario = QtGui.QTabWidget(self)
        self.vboxlayout.addWidget(self.tab_Scenario)

	self.scenario_list = []
	self.max_scenario_id = 0

        self.hboxlayout2 = QtGui.QHBoxLayout()

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)

        self.btn_newScenario = QtGui.QPushButton(self)
        self.hboxlayout2.addWidget(self.btn_newScenario)

        self.btn_deleteScenario = QtGui.QPushButton(self)
        self.hboxlayout2.addWidget(self.btn_deleteScenario)

        self.btn_saveScenario = QtGui.QPushButton(self)
        self.hboxlayout2.addWidget(self.btn_saveScenario)
        self.vboxlayout.addLayout(self.hboxlayout2)

        self.btn_newScenario.setIcon(QtGui.QIcon(":/images/new.png"))
        self.btn_newScenario.setToolTip(self.tr("Create new scenario"))
        self.btn_newScenario.setStatusTip(self.tr("Create new scenario"))
        self.btn_newScenario.setIconSize(QtCore.QSize(25, 25))
        self.btn_deleteScenario.setIcon(QtGui.QIcon(":/images/delete.png"))
        self.btn_deleteScenario.setToolTip(self.tr("Remove current scenario"))
        self.btn_deleteScenario.setStatusTip(self.tr("Remove current scenario"))
        self.btn_deleteScenario.setIconSize(QtCore.QSize(25, 25))
        self.btn_saveScenario.setIcon(QtGui.QIcon(":/images/save.png"))
        self.btn_saveScenario.setToolTip(self.tr("Save scenarios"))
        self.btn_saveScenario.setStatusTip(self.tr("Save scenarios"))
        self.btn_saveScenario.setIconSize(QtCore.QSize(25, 25))

        #self.btn_newScenario.setText("Create New Scenario")
        #self.btn_deleteScenario.setText("Remove Current Scenario")
        #self.btn_saveScenario.setText("Save Scenarios")
	self.btn_saveScenario.setVisible(False)

	self.connect(self.btn_newScenario,QtCore.SIGNAL("clicked()"), self.newScenario)
	self.connect(self.btn_deleteScenario,QtCore.SIGNAL("clicked()"), self.delScenario)
	self.connect(self.tab_Scenario, QtCore.SIGNAL("currentChanged (int)"),self.tabSwitch)

    def tabSwitch(self, index):
	name = self.tab_Scenario.widget(index).name
        self.emit(QtCore.SIGNAL("currentScenarioChanged"),name) 

    def getScenarioNames(self):
	return [x.name for x in self.scenario_list]

    def setTabName(self):
	text = str(self.tab_Scenario.currentWidget().le_scenarioName.text())
	name = self.tab_Scenario.tabText(self.tab_Scenario.currentIndex())
	if text:
	    if text in self.getScenarioNames():
		if text == name: return
		self.tab_Scenario.currentWidget().le_scenarioName.setText(name)
		self.tab_Scenario.currentWidget().errormsg.show()
	    else:
		self.tab_Scenario.setTabText(self.tab_Scenario.currentIndex(), text)
		self.tab_Scenario.currentWidget().name = text
		self.tab_Scenario.currentWidget().errormsg.hide()
	else:self.tab_Scenario.currentWidget().le_scenarioName.undo()
    
    def newScenario(self, xname=None):
	self.scenario_new = ScenariosForm()
	self.scenario_new.label.hide()
	self.scenario_new.le_scenarioName.hide()
	self.max_scenario_id += 1
	index = self.max_scenario_id
	if xname is None: name = "Scenario %d" % index
	else: name=xname
	self.scenario_new.name = name
	self.scenario_list.append(self.scenario_new)
	self.tab_Scenario.addTab(self.scenario_new,name)
	self.scenario_new.le_scenarioName.setText(name)
	self.connect(self.scenario_new.le_scenarioName,QtCore.SIGNAL("editingFinished()"), self.setTabName)
        if xname is None: self.emit(QtCore.SIGNAL("newScenario"),self.scenario_new) 
	return self.scenario_new	
 
    def delScenario(self):
	if self.tab_Scenario.count()==1:
	    print "You cannot remove the default scenario" 
	    return
	idx = self.tab_Scenario.currentIndex()
	widget = self.tab_Scenario.widget(idx)
	self.scenario_list.remove(widget)
	self.tab_Scenario.removeTab(idx)
	name = widget.name	
        self.emit(QtCore.SIGNAL("delScenario"),name)
	del widget
    
    def clear(self):
	self.max_scenario_id = 0
	self.tab_Scenario.clear()
	for widget in self.scenario_list:
	    del widget
 
class PrintFilter(Qwt.QwtPlotPrintFilter):
    def __init__(self):
        QwtPlotPrintFilter.__init__(self)

    # __init___()
    
    def color(self, c, item):
        if not (self.options() & QwtPlotPrintFilter.PrintCanvasBackground):
            if item == QwtPlotPrintFilter.MajorGrid:
                return QtCore.Qt.darkGray
            elif item == QwtPlotPrintFilter.MinorGrid:
                return QtCore.Qt.gray
        if item == QwtPlotPrintFilter.Title:
            return QtCore.Qt.red
        elif item == QwtPlotPrintFilter.AxisScale:
            return QtCore.Qt.green
        elif item == QwtPlotPrintFilter.AxisTitle:
            return QtCore.Qt.blue
        return c

    # color()

    def font(self, f, item):
        result = QtGui.QFont(f)
        result.setPointSize(int(f.pointSize()*1.25))
        return result

    # font()

# class PrintFilter

class OptionDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self,parent)
    
#    def paint(self, painter, option, index):
#        QtGui.QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = QtGui.QComboBox(parent)
            for t in optTypeDict:
                editor.addItem(optTypeDict[t],  QtCore.QVariant(t))
            editor.installEventFilter(self)
            self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
            return editor        
        if index.column() == 1:
            editor = QtGui.QDateEdit(parent)
            editor.setDisplayFormat(QTDATEFMT)
            editor.setCalendarPopup(True)
            expireDate = index.model().data(index, QtCore.Qt.DisplayRole).toString()
            ed = str2datetime(expireDate, fmt=DATEFMT)
            expireDate = QtCore.QDate(ed.year, ed.month, ed.day)
            editor.setDate(expireDate)            
            editor.installEventFilter(self)
            self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
            return editor

        editor = QtGui.QLineEdit(parent)        
        
        #//create a completer with the strings in the column as model.
#        allStrings = QtCore.QStringList()
#        for i in range(0, index.model().rowCount(parent)):
#            strItem = index.model().data(index.sibling(i, index.column()), QtCore.Qt.DisplayRole).toString()
#            if not allStrings.contains(strItem):
#                allStrings.append(strItem)
#                            
#        autoComplete = QtGui.QCompleter(allStrings, parent)
#        editor.setCompleter(autoComplete)
        self.connect(editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
        return editor
        #return QtGui.QItemDelegate.createEditor(self, parent, option, index)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL("commitDate"), (editor,))
        self.emit(QtCore.SIGNAL("closeEditor"), (editor,QtGui.QAbstractItemDelegate.EditNextItem))
        
    def setEditorData(self, editor, index):
        if editor is not None:
            if index.column() == 0:
                s = index.model().data(index, QtCore.Qt.DisplayRole).toString()
                editor.setCurrentIndex(editor.findText(s))
            elif index.column() == 1:
                expireDate = index.model().data(index, QtCore.Qt.DisplayRole).toString()
                expireDate = str2datetime(expireDate, fmt=DATEFMT)
                editor.setDate(expireDate)
            else:
                editor.setText(index.model().data(index, QtCore.Qt.DisplayRole).toString())
                #QtGui.QItemDelegate.setEditorData(self, editor, index)
        
    def setModelData(self, editor, model, index):
        if index.column()== 0:
            value = editor.itemData(editor.currentIndex())
            if value.toString() != model.data(index, QtCore.Qt.DisplayRole).toString():
                model.setData(index, value, QtCore.Qt.UserRole)
        else:
            value = editor.text()
            if value:
                model.setData(index, QtCore.QVariant(value), QtCore.Qt.UserRole)

    def sizeHint(self, option, index):
        if index.column() == 0:
            return QtCore.QSize(150,1)
        if index.column() == 1:
            return QtCore.QSize(100,1)
        return QtGui.QItemDelegate.sizeHint(self, option, index)
        
class OptionModel(QtCore.QAbstractTableModel):
    def __init__(self, options, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.m_opts = options
        self.tblheader = option.TableHeader
        self.numCol = len(self.tblheader)
        for opt in self.m_opts:
            self.connect(opt, QtCore.SIGNAL("OptionChanged"), self, QtCore.SIGNAL("TableModelChanged"))
        
    def rowCount(self, parent):
        return len(self.m_opts)

    def columnCount(self, parent):
        return self.numCol
    
    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if (orientation == QtCore.Qt.Horizontal):
            return QtCore.QVariant(self.tblheader[section])
        if (orientation == QtCore.Qt.Vertical):
            return QtCore.QVariant(section+1)
        return QtCore.QVariant()
    
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        
        opt = self.m_opts[index.row()]
        rowval = opt.getTableValue()
        #rowval[0]=index.row()+1
        
        if role == QtCore.Qt.DisplayRole:
            idx = index.column()
            if rowval[idx] is not None:
                if idx == 0:
                    return QtCore.QVariant(optTypeDict[rowval[idx]])
                else:
                    return QtCore.QVariant(rowval[idx])
            else:
                return QtCore.QVariant()
        elif role == QtCore.Qt.TextColorRole and index.column() == 0:
            return QtCore.QVariant(QtGui.QColor(QtCore.Qt.blue))        
        elif role == QtCore.Qt.BackgroundColorRole:
            return QtCore.QVariant(QtGui.QColor(220,240,240))
#            if rowval[OptionColumn.RFRATE]>3:
#                return QtCore.QVariant(QtGui.QColor(240,220,240))
#            else:
#                return QtCore.QVariant(QtGui.QColor(220,240,240))            
            
        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        
        flags = QtCore.QAbstractTableModel.flags(self, index)

        if index.column()<3:
            if self.m_opts[index.row()].type in ('F','T') and index.column()==1:
                return flags
            else:
                return flags | QtCore.Qt.ItemIsEditable
        else:
            return flags

    def checkView(self):        
        selectModel = self.parent.selectionModel()
        indexes = selectModel.selectedIndexes()
        return indexes
                
    def setData(self, index, value, role):
        if index.column() == 0:
            self.emit(QtCore.SIGNAL("createNewOption"), (value.toString(), index.row()))
            return True
        
        if index.column() > 0:
            for idx in self.checkView():
                self.m_opts[idx.row()].setTableProperty(idx.column(), value.toString())
            return True
        
        return False
        
#    def test(self, args):
#        logging.debug("TableModel slot for OptionChanged" + str(args[0]))
        
class Window(QtGui.QMainWindow):

    def __init__(self, parent = None):

        logging.debug("main beginning at: " + time.strftime('%X %x %Z'))
        t1 = time.time()
    
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_optionCalcMWIN()
        self.ui.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.dt_tradeDate = self.ui.dt_tradeDate
        self.dt_horizonDate = self.ui.dt_horizonDate
        
        self.dt_tradeDate.setDisplayFormat(QTDATEFMT)
        self.dt_horizonDate.setDisplayFormat(QTDATEFMT)
        
        now = date.today()
        self.qtoday = QtCore.QDate(now.year, now.month, now.day)
    
        self.dt_tradeDate.setDate(self.qtoday)
        self.dt_horizonDate.setDate(self.qtoday.addMonths(3))
        
        self.createDockWnd()
        self.createActions()        
        self.createMainTabWidget()
                
        self.curves = []
        self.newPortfolio()
        self.setCurveType((curveType.BETA,0))
        
        #icon = QtGui.QIcon(":/images/optcalc.png")
        icon = QtGui.QIcon(":/images/bigger.png")
        self.setWindowIcon(icon)

        t2 = time.time()
        logging.debug('main took %0.6f s' % (t2-t1))
        logging.debug("main ends at: " + time.strftime('%X %x %Z'))

    def createMainTabWidget(self):
        self.mainTabWidget = QtGui.QTabWidget()
        
        tab1 = QtGui.QWidget()
        self.chart = plPlot()
        
        picker = QwtPlotPicker(QwtPlot.xBottom,
                               QwtPlot.yLeft,
                               QwtPicker.PointSelection,
                               QwtPlotPicker.CrossRubberBand,
                               QwtPicker.AlwaysOn,
                               self.chart.canvas())
        picker.setRubberBandPen(QtGui.QPen(QtCore.Qt.green))

        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom,
                               QwtPlot.yLeft,
                               QwtPicker.DragSelection,
                               QwtPicker.AlwaysOff,
                               self.chart.canvas())
        self.zoomer.setRubberBandPen(QtGui.QPen(QtCore.Qt.green))
        
        chartLayout = QtGui.QVBoxLayout()
        chartLayout.addWidget(self.chart)
        tab1.setLayout(chartLayout)
                        
        tab2 = QtGui.QWidget()
        self.PLTable = QtGui.QTableWidget(1, 1)
        self.PLTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        labels = QtCore.QStringList()
        labels << self.tr("Yield")
        self.PLTable.setHorizontalHeaderLabels(labels)
        self.PLTable.resizeColumnsToContents()
        self.PLTable.resizeRowsToContents()

        copyAct = QtGui.QAction("&Copy", self.PLTable)
        copyAct.setShortcut(self.tr("Ctrl+C"))
        copyAct.setStatusTip(self.tr("Copy the current selection's contents to the clipboard"))
        
        self.connect(copyAct, QtCore.SIGNAL("triggered()"), self.copyPLTable)        
        self.PLTable.addAction(copyAct)
        self.PLTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)        
        
        #shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self.PLTable, self.copyPLTable, None, QtCore.Qt.WidgetShortcut)
        
        tab2hbox = QtGui.QHBoxLayout()
        #tab2hbox.setMargin(5)
        tab2hbox.addWidget(self.PLTable)
        tab2.setLayout(tab2hbox)
    
        self.mainTabWidget.addTab(tab1, self.tr("Chart"))
        self.mainTabWidget.addTab(tab2, self.tr("Data Grid"))

        maintabvbox = QtGui.QVBoxLayout()
        maintabvbox.addWidget(self.mainTabWidget)
        self.ui.chartWidget.setLayout(maintabvbox)

    def createActions(self):
#        self.ui.action_New.setShortcut(self.tr("Ctrl+N"))
#        self.ui.action_Open.setShortcut(self.tr("Ctrl+O"))        
#        self.ui.action_Save.setShortcut(self.tr("Ctrl+S"))
#        self.ui.actionPrint.setShortcut(self.tr("Ctrl+P"))        
#        self.ui.actionExit.setShortcut(self.tr("Ctrl+Q"))
 
        self.ui.action_New.setIcon(QtGui.QIcon(":/images/new.png"))
        self.ui.action_Save.setIcon(QtGui.QIcon(":/images/save.png"))
        self.ui.action_Open.setIcon(QtGui.QIcon(":/images/open.png"))
        self.ui.actionPrint.setIcon(QtGui.QIcon(":/images/print.png"))        
        
        self.ui.action_New.setStatusTip(self.tr("Create new portfolio"))
        self.ui.action_Open.setStatusTip(self.tr("Open portfolio"))
        self.ui.action_Save.setStatusTip(self.tr("Save P/L chart"))
        self.ui.actionPrint.setStatusTip(self.tr("Print P/L chart"))

        self.ui.action_New.setToolTip(self.tr("Create new portfolio"))
        self.ui.action_Open.setToolTip(self.tr("Open portfolio"))
        self.ui.action_Save.setToolTip(self.tr("Save P/L chart"))
        self.ui.actionPrint.setToolTip(self.tr("Print P/L chart"))

        self.ui.fileToolBar = self.addToolBar(self.tr("File"))
        self.ui.fileToolBar.addAction(self.ui.action_New)
        #self.ui.fileToolBar.addAction(self.ui.action_Open)
        self.ui.fileToolBar.addAction(self.ui.action_Save)
        self.ui.fileToolBar.addAction(self.ui.actionPrint)
                
        self.connect(self.ui.action_New, QtCore.SIGNAL("triggered()"), self.newPortfolio)
        self.connect(self.ui.action_Open, QtCore.SIGNAL("triggered()"), self.openPortfolio)
        self.connect(self.ui.action_Save, QtCore.SIGNAL("triggered()"), self.saveCharts)
        self.connect(self.ui.actionPrint, QtCore.SIGNAL("triggered()"), self.printPortfolio)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), self, QtCore.SLOT("close()"))
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.about)        
        self.connect(self.ui.actionAbout_Qt, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))

    def createDockWnd(self):
        self.errWindow = StatusDockWindow(self)
        self.errWindow.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.errWindow)
        self.errWindow.hide()
                
        self.dockSetting = QtGui.QDockWidget(self.tr("Chart Setting"), self)
        self.dockSetting.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.settingForm = settingWnd()
        self.dockSetting.setWidget(self.settingForm)
        self.dockSetting.setMinimumHeight(150)
        self.dockSetting.setMinimumWidth(250)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockSetting)

        self.dockPortfolio = QtGui.QDockWidget(self.tr("Portfolio Table"), self)
        #self.dockPortfolio.setAllowedAreas(QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        self.dockPortfolio.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.ptForm = portfolioTable()
        self.dockPortfolio.setWidget(self.ptForm)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockPortfolio)
        self.dockPortfolio.setMinimumHeight(250)
                        
        self.portfolioTable = self.ptForm.portfolioTable
        
        delAct = QtGui.QAction("delete", self.portfolioTable)
        delAct.setShortcut(self.tr("Ctrl+D"))
        delAct.setStatusTip(self.tr("Delete the current selection from portfolio"))
        
        self.connect(delAct, QtCore.SIGNAL("triggered()"), self.delOptionFromPortfolio)
        self.portfolioTable.addAction(delAct)
        self.portfolioTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        self.tbtn_cal = self.ptForm.tbtn_cal
        self.tbtn_new = self.ptForm.tbtn_new
        self.tbtn_open = self.ptForm.tbtn_open
        self.tbtn_save = self.ptForm.tbtn_save

        self.dockOption = QtGui.QDockWidget(self.tr("Contract Details"), self)
        #self.dockOption.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dockOption.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)

        tradeDate = self.dt_tradeDate.date().toString(QTDATEFMT)
        horizonDate = self.dt_horizonDate.date().toString(QTDATEFMT)
        
        #print "In createDockWnd tradeDate=[%s]" % tradeDate
        #print "In createDockWnd horizonDate=[%s]" % horizonDate

        opts = []
        for t in optTypeDict:
	    opts.append(optionFactory(t, tradeDate=tradeDate, horizonDate=horizonDate))
	
	self.optionTab = optionInputWnd(opts)

        self.dockOption.setWidget(self.optionTab)
        self.dockOption.setMinimumHeight(250)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockOption)

	#dock window for scenario settings	
        self.dockScenario = QtGui.QDockWidget(self.tr("Scenario Editor"), self)
        self.dockScenario.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
	self.scenarioTab = scenarioWindow(self)
        self.dockScenario.setWidget(self.scenarioTab)
        self.dockScenario.setMinimumWidth(310)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockScenario)
	self.connect(self.scenarioTab, QtCore.SIGNAL("newScenario"), self.newPortfolioScenario)
	self.connect(self.scenarioTab, QtCore.SIGNAL("delScenario"), self.delPortfolioScenario)
	self.connect(self.scenarioTab, QtCore.SIGNAL("currentScenarioChanged"), self.setCurrentPortfolioScenario)
	self.connect(self.scenarioTab.btn_saveScenario,QtCore.SIGNAL("clicked()"), self.saveScenarios)
		
        self.connect(self.settingForm, QtCore.SIGNAL("curveTypeChanged"), self.setCurveType)
        self.connect(self.portfolioTable, QtCore.SIGNAL("clicked(const QModelIndex &)"), self.editDocWnd)

        self.tbtn_new.setToolTip(self.tr("Add new option into portfolio"))
        self.tbtn_new.setStatusTip(self.tr("Add new option into portfolio"))
        self.tbtn_new.setIcon(QtGui.QIcon(":/images/new.png"))
        self.tbtn_new.setIconSize(QtCore.QSize(25, 25))
        self.tbtn_new.setShortcut(self.tr("Ctrl+N"))
        self.connect(self.tbtn_new, QtCore.SIGNAL("clicked()"), self.copyOption)

        self.tbtn_open.setToolTip(self.tr("Open existing portfolio"))
        self.tbtn_open.setStatusTip(self.tr("Open existing portfolio"))
        self.tbtn_open.setIcon(QtGui.QIcon(":/images/open.png"))
        self.tbtn_open.setIconSize(QtCore.QSize(25, 25))
        self.tbtn_open.setShortcut(self.tr("Ctrl+O"))
        self.connect(self.tbtn_open, QtCore.SIGNAL("clicked()"), self.openPortfolio)

        self.tbtn_save.setToolTip(self.tr("Save current portfolio"))
        self.tbtn_save.setStatusTip(self.tr("Save current portfolio"))
        self.tbtn_save.setIcon(QtGui.QIcon(":/images/save.png"))
        self.tbtn_save.setIconSize(QtCore.QSize(25, 25))
        self.tbtn_save.setShortcut(self.tr("Ctrl+S"))
        self.connect(self.tbtn_save, QtCore.SIGNAL("clicked()"), self.savePortfolio)

        self.tbtn_cal.setToolTip(self.tr("Draw P/L chart"))
        self.tbtn_cal.setStatusTip(self.tr("Draw P/L chart"))
        self.tbtn_cal.setIcon(QtGui.QIcon(":/images/undo.png"))
        self.tbtn_cal.setIconSize(QtCore.QSize(25, 25))
        self.tbtn_cal.setShortcut(self.tr("F9")) 
        self.connect(self.tbtn_cal, QtCore.SIGNAL("clicked()"), self.refreshOptionPlot)        

#        self.tbtn_del.setToolTip(self.tr("Delete selected option..."))
#        self.tbtn_del.setIcon(QtGui.QIcon(":/images/delete.png"))
#        self.tbtn_del.setIconSize(QtCore.QSize(25, 25))
#        self.connect(self.tbtn_del, QtCore.SIGNAL("clicked()"), self.delOptionFromPortfolio) 
	
	self.connect(self.ui.actionScenarios,QtCore.SIGNAL("toggled(bool)"),self.dockSetting.setVisible)       
	self.connect(self.ui.actionContract_Details,QtCore.SIGNAL("toggled(bool)"),self.dockOption.setVisible)       
	self.connect(self.ui.actionPortfolio_Table,QtCore.SIGNAL("toggled(bool)"),self.dockPortfolio.setVisible)       
	self.connect(self.ui.actionScenario_Editor,QtCore.SIGNAL("toggled(bool)"),self.dockScenario.setVisible)       
	self.connect(self.ui.actionTrace_Window,QtCore.SIGNAL("toggled(bool)"),self.errWindow.setVisible) 

	self.connect(self.dockSetting,QtCore.SIGNAL("visibilityChanged(bool)"),self.checkDockSettingStatus)
	self.connect(self.dockOption,QtCore.SIGNAL("visibilityChanged(bool)"),self.checkDockOptionStatus)
	self.connect(self.dockPortfolio,QtCore.SIGNAL("visibilityChanged(bool)"),self.checkDockPortfolioStatus)
	self.connect(self.dockScenario,QtCore.SIGNAL("visibilityChanged(bool)"),self.checkDockScenarioStatus)
	self.connect(self.errWindow,QtCore.SIGNAL("visibilityChanged(bool)"),self.checkTraceWindowStatus)

	self.portfolioTable.installEventFilter(self)

    def checkDockSettingStatus(self, show):
        if not self.isMinimized():
	    self.ui.actionScenarios.setChecked(show)

    def checkDockOptionStatus(self, show):
        if not self.isMinimized():
	    self.ui.actionContract_Details.setChecked(show)

    def checkDockPortfolioStatus(self, show):
        if not self.isMinimized():
	    self.ui.actionPortfolio_Table.setChecked(show)

    def checkDockScenarioStatus(self, show):
        if not self.isMinimized():
	    self.ui.actionScenario_Editor.setChecked(show)

    def checkTraceWindowStatus(self, show):
        if not self.isMinimized():
	    self.ui.actionTrace_Window.setChecked(show)

    def eventFilter(self, obj, event):
	if obj==self.portfolioTable:
	    if event.type()==QtCore.QEvent.KeyPress and event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
		self.newOption()
		return True
	return QtGui.QMainWindow.eventFilter(self,obj,event)
		
    def setModel(self):
        logging.debug(",".join([str(x) for x in self.portfolio.options]))
        self.model = OptionModel(self.portfolio.options, self.portfolioTable)
        self.portfolioTable.setModel(self.model)
                
        self.delegate = OptionDelegate(self.portfolioTable)
        self.portfolioTable.setItemDelegate(self.delegate)
        
        self.portfolioTable.resizeColumnsToContents()
        self.portfolioTable.resizeRowsToContents()

        self.connect(self.model, QtCore.SIGNAL("TableModelChanged"), self.ptForm.updateTableByModel)
        self.connect(self.model, QtCore.SIGNAL("createNewOption"), self.newOption)
        
#        topLeft = self.model.index(0, 0, QtCore.QModelIndex())
#        bottomRight = self.model.index(0, 2, QtCore.QModelIndex())                
#        for row in range(model.rowCount(QtCore.QModelIndex())):
#            self.portfolioTable.resizeRowToContents(row)
#        for column in range(model.columnCount(QtCore.QModelIndex())):
#            self.portfolioTable.resizeColumnToContents(column)
    
    def delOptionFromPortfolio(self):
        selectModel = self.portfolioTable.selectionModel()
        indexes = selectModel.selectedIndexes()
        rows = Set([x.row() for x in indexes])
        if len(rows)>0:
            delOpt = []
            for idx in rows:
                delOpt.append(self.portfolio.options[idx])
            
	    self.saveScenarios()
            for opt in delOpt:
                self.portfolio.delOption(opt)
            
            if len(self.portfolio.options)>0:
                self.setModel()
                self.portfolioTable.emit(QtCore.SIGNAL("clicked(const QModelIndex &)"), self.model.createIndex(0,0))
		self.updateAllScenarioTables()
                #self.refreshOptionPlot()
            else:
                self.newOption()
        else:
            logging.error("Nothing to be deleted!")
    
    #edit option in docwindow            
    def editDocWnd(self, index):
        if index.isValid():            
            opt = self.portfolio.options[index.row()]
            self.optionTab.updateTab(opt)
        else:
            logging.error("invalid index in editDocWnd")
            
    def copyOption(self):
        selectModel = self.portfolioTable.selectionModel()
        indexes = selectModel.selectedIndexes()
        if len(indexes)>0:
            row = indexes[0].row()
            baseOpt = self.portfolio.options[row]
            opt = baseOpt.clone()
	    self.saveScenarios()
            self.portfolio.updateOption(opt, -1)
            self.setModel()
            self.optionTab.updateTab(opt)
	    self.updateAllScenarioTables()
            #self.refreshOptionPlot()
        else:
            self.newOption()
        
    def newOption(self, args=None):
        if args is None:
            type = 'W'
            index = -1
        elif isinstance(args, tuple):
            type = args[0]
            index = args[1]
        else:
            raise "newOption error"
                        
        tradeDate = self.dt_tradeDate.date().toString(QTDATEFMT)
        horizonDate = self.dt_horizonDate.date().toString(QTDATEFMT)
        
        opt = optionFactory(type, tradeDate=tradeDate, horizonDate=horizonDate, savedopt=True)
#        hdate = str2datetime(opt.horizonDate)
#        self.dt_horizonDate.setDate(hdate)
        
	self.saveScenarios()
        self.portfolio.updateOption(opt, index, needConnect=True)
        
        self.setModel()
        self.optionTab.updateTab(opt)
	self.updateAllScenarioTables()

    def newPortfolio(self):
	self.clearChartAndTable()
        self.portfolio = portfolio()
	self.scenarioTab.clear()
        self.connect(self.portfolio, QtCore.SIGNAL("PortfolioPLDone"), self.redrawOptionPlot)
        self.connect(self.settingForm, QtCore.SIGNAL("yldRangeChanged"), self.portfolio.setyldRange)
        self.connect(self.dt_tradeDate, QtCore.SIGNAL("dateChanged(const QDate &)"), self.portfolio.setTradeDate)
        self.connect(self.dt_horizonDate, QtCore.SIGNAL("dateChanged(const QDate &)"), self.portfolio.setHorizonDate)
        #self.connect(self.cb_exerciseType, QtCore.SIGNAL("currentIndexChanged(const QString &)"), self.portfolio.setExerciseType)
        
        self.newOption()
	self.scenarioTab.newScenario()
	
    def creatAllScenarioWidgets(self):
	if len(self.portfolio.scenarios)>0:
	    for s in self.portfolio.scenarios:
		widget = self.scenarioTab.newScenario(s)
		self.updateScenarioTable(widget)
	else:
	    widget = self.scenarioTab.newScenario()

    def marshPortfolio(self, doc):
        tradeDate = str(doc.node.getAttribute("tradeDate"))
        horizonDate = str(doc.node.getAttribute("horizonDate"))

        p = portfolio()
                
        for x in doc.node.childNodes:
            if str(x.name) == 'option':
                type = x.getAttribute("type")
                issueDate = None
                expireDate = None
                rfRate = 0
                for y in x.childNodes:
                    if y.name in ('SwapMaturity', 'Contract'):
                        swapMat_contract = str(y.text)
                    elif y.name == 'ExpDate':
                        expireDate = str(y.text)
                    elif y.name == 'RFRate':
                        rfRate = float(y.text)
                    elif y.name in ('FwdSwap', 'FuturePrice'):
                        fwdfut = float(y.text)
                    elif y.name == 'Strike':
                        strike = float(y.text)
                    elif y.name == 'Direction':
                        cpsf = str(y.text)
                    elif y.name == 'Premium':
                        premium = float(y.text)
                    elif y.name == 'Notional':
                        notional = float(y.text)
                    elif y.name == 'ExerciseType':
                        exerciseType = str(y.text)
                    elif y.name == 'IssueDate':
                        issueDate = str(y.text)
                
                opt = optionFactory(type, tradeDate=tradeDate, exerciseType=exerciseType, 
                                 expireDate=expireDate, rfRate=rfRate, fwdfut=fwdfut, strike=strike, 
                                 cpsf=cpsf, premium=premium, notional=notional,  
                                 swapMat_contract=swapMat_contract, horizonDate=horizonDate,
                                 issueDate=issueDate)
                p.updateOption(opt, -1)
	
        for x in doc.node.childNodes:
            if str(x.name) == 'scenario':
		name = x.getAttribute("name")
		tweak = [0]*len(p.options)
                for y in x.childNodes:
		    if str(y.name) == 'option':
			tweak[int(y.getAttribute("id"))]=(float(y.getAttribute("alpha")), float(y.getAttribute("beta")))
		print "name %s tweak %s" % (name, str(tweak))
		p.newScenario(name, tweak)
			
        return p

    def clearChartAndTable(self):
        for c in self.curves:
            c.detach()        
        self.chart.replot()
        self.curves = []
        self.pfPL = []
	self.PLTable.clear()
	                
    def openPortfolio(self):
        filter  = "XML (*.xml)"
        caption = "Choose a filename to save the portfolio"
        cpath = QtCore.QDir.currentPath()
        if str(cpath[-3:]).upper()=='BIN':
            fileName = str(QtGui.QFileDialog.getOpenFileName(self, self.tr(caption),
                                                         '../package/ostrat',
                                                         self.tr(filter), 'xml'))            
        else:
            fileName = str(QtGui.QFileDialog.getOpenFileName(self, self.tr(caption),
                                                         QtCore.QDir.currentPath(),
                                                         self.tr(filter), 'xml'))
            
        if not fileName:
            return
        
	self.clearChartAndTable()
        
        file = open(fileName, "r")
        doc  = Document(xmlFile = file)
        file.close()

        self.portfolio = self.marshPortfolio(doc)
	self.scenarioTab.clear()
	self.creatAllScenarioWidgets()
        
        for x in self.portfolio.options:
            if x.type in ('F', 'T'):
                x.getExpDate(False)
            
        hdate = str2datetime(self.portfolio.options[0].horizonDate, DATEFMT)
        hqdate = QtCore.QDate(hdate.year, hdate.month, hdate.day)
        self.dt_horizonDate.setDate(hqdate)        
        self.portfolioTable.emit(QtCore.SIGNAL("clicked(const QModelIndex &)"), self.model.createIndex(0,0))
        
        self.connect(self.portfolio, QtCore.SIGNAL("PortfolioPLDone"), self.redrawOptionPlot)
        self.connect(self.settingForm, QtCore.SIGNAL("yldRangeChanged"), self.portfolio.setyldRange)
        self.connect(self.dt_horizonDate, QtCore.SIGNAL("dateChanged(const QDate &)"), self.portfolio.setHorizonDate)
        #self.connect(self.cb_exerciseType, QtCore.SIGNAL("currentIndexChanged(const QString &)"), self.portfolio.setExerciseType)
        self.setModel()
        #self.refreshOptionPlot()

    def validateOptData(self):
        res = True
        errmsg = ""
        for x in self.portfolio.options:
            r, emsg = x.isDataValid()
            if not r:
                errmsg += emsg + "\n"
                res = False
        if not res:
#            errmsgDlg = QtGui.QErrorMessage(self)
#            errmsgDlg.showMessage()
            errmsg += "Please correct the above error first"
            QtGui.QMessageBox.warning(self, self.tr("Invalid option data"),
                                       self.tr(str(errmsg)))
        return res

    def updateAllScenarioTables(self):
	for i in range(self.scenarioTab.tab_Scenario.count()):
	    widget = self.scenarioTab.tab_Scenario.widget(i)
	    self.updateScenarioTable(widget)

    def updateScenarioTable(self, widget):
	widget.scenarioTable.clearContents()
	cs = self.portfolio.scenarios[widget.name]
	idx = 0
	widget.scenarioTable.setRowCount(len(self.portfolio.options))
	for x in self.portfolio.options:
	    try: ab = cs[x]
	    except KeyError:
		ab = (x.yldalpha, x.yldbeta)
		pass 
	    widget.scenarioTable.setItem(idx, 0, QtGui.QTableWidgetItem("$"+str(idx+1)))
	    widget.scenarioTable.setItem(idx, 1, QtGui.QTableWidgetItem(str(float(ab[0]))))
	    widget.scenarioTable.setItem(idx, 2, QtGui.QTableWidgetItem(str(float(ab[1]))))
	    idx +=1
	
	widget.scenarioTable.resizeColumnsToContents()
	widget.scenarioTable.resizeRowsToContents()
		
    def delPortfolioScenario(self, name):
	self.portfolio.delScenario(name)	

    def newPortfolioScenario(self, widget):
	self.portfolio.newScenario(widget.name)		
	self.updateScenarioTable(widget)
    
    def setCurrentPortfolioScenario(self, name):
	self.portfolio.defaultScenarioName = name

    def saveScenarios(self):
	num = self.scenarioTab.tab_Scenario.count()
	for i in range(num):
	    widget = self.scenarioTab.tab_Scenario.widget(i)
	    name = widget.name
	    table = widget.scenarioTable
	    tweaks = []
	    for row in range(table.rowCount()):
		alpha = str(table.item(row,1).text())
		beta = str(table.item(row,2).text())
		tweaks.append((float(alpha), float(beta)))
	    self.portfolio.editScenario(name, tweaks)
    
    def setCurveType(self, args):
        (ctype, step) = args
        if ctype == curveType.YLDBETA:
            self.ctype = ctype
            self.curveList = (1.0*step, 1.0, 1.0/step)
            self.curveNames = ("Steepen %s" % str(step), "Parallel Shift", "Flatten %s" % str(step))
        elif ctype == curveType.HORIZON:
            self.ctype = ctype
            self.curveList = ("-%s" % step, 0, "+%s" % step)
            self.curveNames = ("-%s" % step, "horizon date", "+%s" % step)
	elif ctype == curveType.BETA:
            self.ctype = ctype
            self.curveList = self.portfolio.getScenarioNames()
            self.curveNames = self.portfolio.getScenarioNames()
        else:
            logging.error("wrong curve type [%s]" % str(ctype))
        
    #slot function for click redraw button    
    def refreshOptionPlot(self):
        self.setFocus()
	if self.ctype==curveType.BETA: 
	    self.saveScenarios()
	    self.setCurveType((curveType.BETA,0))
        if len(self.portfolio.options) > 0:
	    self.clearChartAndTable()
            self.redrawCnt = 0
            if self.validateOptData():
		print "self.curveList " + str(self.curveList)
                self.portfolio.queryPortfolioPL(self.curveList[self.redrawCnt], self.ctype)
                #QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
		self.progressBar = QtGui.QProgressDialog("Calculating...", "&Cancel",0,len(self.curveList),self)
		self.connect(self.progressBar, QtCore.SIGNAL("canceled()"), self.cancelProgressBar)
		self.progressBar.setWindowTitle("Option Calculator")
		self.progressBar.setValue(0)
		self.progressBar.forceShow () 

    def cancelProgressBar(self):
	print "cancelProgressBar"
	self.redrawCnt = len(self.curveList)+1
	self.redrawOptionPlot()

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        self.progressBar.setValue(curVal + 1)

    def getColorList(self, i, size):
        green  = 120
        blue   = 240
        red    = 360
        value  = 255
        minSat = 120
        maxSat = 255        
        hue = green + (red-green) * i / size
        color = QtGui.QColor()
        color.setHsv(hue,maxSat,value)
        return color
    
    def getSymStyle(self, style):        
        symStyle = {0:QwtSymbol.Ellipse,1:QwtSymbol.Rect,2:QwtSymbol.Diamond, 3:QwtSymbol.Triangle}
        i = style % len(symStyle)
        return symStyle[i]
        
    def redrawOptionPlot(self):
	if self.redrawCnt>len(self.curveList):
	    print "user cancelled the calculation"
	    self.finishRedraw(False)
	    return 

        self.redrawCnt+=1
        print "redrawOptionPlot %d" % self.redrawCnt
        self.pfPL.append(self.portfolio.pfPL)
        
        color = self.getColorList(self.redrawCnt, len(self.curveList))
        symStyle = self.getSymStyle(self.redrawCnt)
        c1 = self.chart.newCurve(self.curveNames[self.redrawCnt-1], self.pfPL[-1], curveCol = color, symbolStyle=symStyle)
        
        c1.attach(self.chart)
        self.curves.append(c1)
        #self.chart.showCurve(c1, True)
        #self.chart.replot()
        self.chart.replotWithZoomer()
	self.advanceProgressBar()
        
        if self.redrawCnt < len(self.curveList):
	    #print self.portfolio
            self.portfolio.queryPortfolioPL(self.curveList[self.redrawCnt], self.ctype)
        else: self.finishRedraw()

    def finishRedraw(self, success=True):
	if success:
	    #QtGui.QApplication.restoreOverrideCursor()
	    self.zoomer.setZoomBase()
	    self.refreshPLTable()
	    self.portfolioTable.resizeColumnsToContents()
	    print self.portfolio
	    print "--------calculation is done!---------"
	#self.progressBar.close()
            
    def refreshPLTable(self):
        self.PLTable.setUpdatesEnabled(False)
        self.PLTable.setSortingEnabled(False)
        self.PLTable.setRowCount(0)
        
        #print self.pfPL
        ylds = self.pfPL[0][0]
        numRow = len(ylds)
        numCol = len(self.pfPL)
        self.PLTable.setRowCount(numRow)
        self.PLTable.setColumnCount(numCol+1)
        
        labels = QtCore.QStringList()
        labels << self.tr("Yield")
        for x in self.curveNames:
            labels << self.tr(str(x))
        self.PLTable.setHorizontalHeaderLabels(labels)
                
        for row in range(numRow):
            newItem = QtGui.QTableWidgetItem()
            newItem.setData(QtCore.Qt.DisplayRole, QtCore.QVariant(ylds[row]))
            self.PLTable.setItem(row, 0, newItem)
	    for col in range(numCol):
		if self.pfPL[col][1]:
		    newItem = QtGui.QTableWidgetItem()
		    newItem.setData(QtCore.Qt.DisplayRole, QtCore.QVariant(round(self.pfPL[col][1][row],2)))
		    self.PLTable.setItem(row, col+1, newItem)

        self.PLTable.resizeColumnsToContents()
        self.PLTable.resizeRowsToContents()
        self.PLTable.setColumnWidth(0,50)
        self.PLTable.setUpdatesEnabled(True)
        self.PLTable.setSortingEnabled(True)

    def copyPLTable(self):
        selectModel = self.PLTable.selectionModel()
        rangeSelection = selectModel.selection()[0]
        
        topleft = rangeSelection.topLeft()
        bottomRight = rangeSelection.bottomRight()
        
        row0 = topleft.row()
        col0 = topleft.column()
        row1 = bottomRight.row()
        col1 = bottomRight.column()
        
        if row0-row1==0:
            return
        
        res = ""
        for col in range(col0, col1+1):
            res += self.PLTable.horizontalHeaderItem(col).text() + "\t"
        res += "\n"
        
        for row in range(row0,row1+1):
            for col in range(col0, col1+1):
                res += self.PLTable.item(row,col).text() + "\t"
            res += "\n"
        
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(res)        

    def printPortfolio(self):
        pixmap = QtGui.QPixmap.grabWidget(self.chart)
        #pixmap = QtGui.QPixmap.grabWidget(self.ui.chartWidget)
	image = pixmap.toImage()
        clipboard = QtGui.QApplication.clipboard()
        #clipboard.setPixmap(pixmap)
	clipboard.setImage(image)
        
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

#        printer.setOutputFileName('bode-example-%s.ps' % Qt.qVersion())
        
        printer.setDocName('Option Calculator-%s.ps' % QtCore.qVersion())
        #printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setCreator("Option Calculator")
        printer.setOrientation(QtGui.QPrinter.Landscape)
        printer.setColorMode(QtGui.QPrinter.GrayScale)        
    
        dialog = QtGui.QPrintDialog(printer)
        if dialog.exec_():
            filter = PrintFilter()
            if (QtGui.QPrinter.GrayScale == printer.colorMode()):
                filter.setOptions(
                    QwtPlotPrintFilter.PrintAll
                    & ~QwtPlotPrintFilter.PrintCanvasBackground)
            self.chart.print_(printer, filter)

    # print_()
    def saveCharts(self):
        #filter  = "Images (*.svg *.bmp *.png *.jpg *.jpeg)"
        filter  = "Images (*.svg *.bmp *.png)"
        caption = "Choose a filename to save the regression residual image"
        fileName = str(QtGui.QFileDialog.getSaveFileName(self, self.tr(caption),
                                                     QtCore.QDir.currentPath(),
                                                     self.tr(filter), 'svg'))

        if not fileName:
            return
                
        filter = PrintFilter()
        rect = self.chart.contentsRect()
        print rect.width(),rect.height()
        #xMap = self.chart.canvasMap(self.chart.xAxis())
        format = fileName[fileName.rfind(".")+1:].upper()
        
        if format == 'SVG':
            picture = QtGui.QPicture()
            painter = QtGui.QPainter(picture)
            #self.chart.drawCanvas(painter)
            self.chart.print_(painter,rect,filter)
            painter.end()
            picture.save(fileName)
        elif format in ['BMP', 'PNG', 'JPG', 'JPEG']:
            pixmap = QtGui.QPixmap.grabWidget(self.chart)
            pixmap.save(fileName, format)
                            
    def savePortfolio(self):
        #logging.debug("save")        
        filter  = "XML (*.xml)"
        caption = "Choose a filename to save the portfolio"
        fileName = str(QtGui.QFileDialog.getSaveFileName(self, self.tr(caption),
                                                     QtCore.QDir.currentPath(),
                                                     self.tr(filter), 'xml'))

        if not fileName:
            return
	self.saveScenarios() 
        xmlStr = self.portfolio.toXML()
        f = open(fileName,'w')
        f.write(xmlStr)
        f.close()
            
    def about(self):
       QtGui.QMessageBox.about(self, self.tr("About Option Calculator"), self.tr(
                               "The aim of this project was to build an option pricing "
                               "application that enables one to evaluate a portfolio "
                               "consisting of a variety of options and futures on fixed "
                               "income securities in a consistent fashion. In particular, "
                               "the portfolio could consist of treasury futures/options, "
                               "eurodollar futures/options and swaptions."
                               ))

class myQApplication(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
    
    def notify(self, receiver, event):
        try:
            QtGui.QApplication.notify(self, receiver, event)
        except:            
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            pass
        
def run():
    app = QtGui.QApplication(sys.argv)
    #app.setStyle(QtGui.QMacStyle())
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
