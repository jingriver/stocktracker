# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/optionCalcMainWin.ui'
#
# Created: Wed Jun 04 15:35:51 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_optionCalcMWIN(object):
    def setupUi(self, optionCalcMWIN):
        optionCalcMWIN.setObjectName("optionCalcMWIN")
        optionCalcMWIN.resize(QtCore.QSize(QtCore.QRect(0,0,767,702).size()).expandedTo(optionCalcMWIN.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(optionCalcMWIN)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setObjectName("vboxlayout")

        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setMargin(9)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.vboxlayout1.addWidget(self.label)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.hboxlayout.addWidget(self.label_6)

        self.dt_tradeDate = QtGui.QDateEdit(self.groupBox)
        self.dt_tradeDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2000,5,1),QtCore.QTime(0,0,0)))
        self.dt_tradeDate.setCalendarPopup(True)
        self.dt_tradeDate.setDate(QtCore.QDate(2000,5,1))
        self.dt_tradeDate.setObjectName("dt_tradeDate")
        self.hboxlayout.addWidget(self.dt_tradeDate)

        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.hboxlayout.addWidget(self.label_8)

        self.dt_horizonDate = QtGui.QDateEdit(self.groupBox)
        self.dt_horizonDate.setCalendarPopup(True)
        self.dt_horizonDate.setObjectName("dt_horizonDate")
        self.hboxlayout.addWidget(self.dt_horizonDate)

        spacerItem = QtGui.QSpacerItem(81,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout)

        self.line = QtGui.QFrame(self.groupBox)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.vboxlayout1.addWidget(self.line)

        self.chartWidget = QtGui.QWidget(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartWidget.sizePolicy().hasHeightForWidth())
        self.chartWidget.setSizePolicy(sizePolicy)
        self.chartWidget.setMinimumSize(QtCore.QSize(500,350))
        self.chartWidget.setObjectName("chartWidget")
        self.vboxlayout1.addWidget(self.chartWidget)
        self.vboxlayout.addWidget(self.groupBox)
        optionCalcMWIN.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(optionCalcMWIN)
        self.menubar.setGeometry(QtCore.QRect(0,0,767,21))
        self.menubar.setObjectName("menubar")

        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")

        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")

        self.menuWindow = QtGui.QMenu(self.menubar)
        self.menuWindow.setObjectName("menuWindow")
        optionCalcMWIN.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(optionCalcMWIN)
        self.statusbar.setObjectName("statusbar")
        optionCalcMWIN.setStatusBar(self.statusbar)

        self.actionAbout = QtGui.QAction(optionCalcMWIN)
        self.actionAbout.setObjectName("actionAbout")

        self.action_New = QtGui.QAction(optionCalcMWIN)
        self.action_New.setObjectName("action_New")

        self.action_Open = QtGui.QAction(optionCalcMWIN)
        self.action_Open.setObjectName("action_Open")

        self.action_Save = QtGui.QAction(optionCalcMWIN)
        self.action_Save.setObjectName("action_Save")

        self.actionExit = QtGui.QAction(optionCalcMWIN)
        self.actionExit.setObjectName("actionExit")

        self.actionAbout_Qt = QtGui.QAction(optionCalcMWIN)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")

        self.actionPrint = QtGui.QAction(optionCalcMWIN)
        self.actionPrint.setObjectName("actionPrint")

        self.actionProperty_Editor = QtGui.QAction(optionCalcMWIN)
        self.actionProperty_Editor.setObjectName("actionProperty_Editor")

        self.actionScenarios = QtGui.QAction(optionCalcMWIN)
        self.actionScenarios.setCheckable(True)
        self.actionScenarios.setChecked(True)
        self.actionScenarios.setObjectName("actionScenarios")

        self.actionContract_Details = QtGui.QAction(optionCalcMWIN)
        self.actionContract_Details.setCheckable(True)
        self.actionContract_Details.setChecked(True)
        self.actionContract_Details.setObjectName("actionContract_Details")

        self.actionPortfolio_Table = QtGui.QAction(optionCalcMWIN)
        self.actionPortfolio_Table.setCheckable(True)
        self.actionPortfolio_Table.setChecked(True)
        self.actionPortfolio_Table.setObjectName("actionPortfolio_Table")

        self.actionTrace_Window = QtGui.QAction(optionCalcMWIN)
        self.actionTrace_Window.setCheckable(True)
        self.actionTrace_Window.setObjectName("actionTrace_Window")

        self.actionScenario_Editor = QtGui.QAction(optionCalcMWIN)
        self.actionScenario_Editor.setCheckable(True)
        self.actionScenario_Editor.setChecked(True)
        self.actionScenario_Editor.setObjectName("actionScenario_Editor")
        self.menu_File.addAction(self.action_New)
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.actionPrint)
        self.menu_File.addAction(self.action_Save)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionExit)
        self.menu_Help.addAction(self.actionAbout)
        self.menu_Help.addAction(self.actionAbout_Qt)
        self.menuWindow.addAction(self.actionScenarios)
        self.menuWindow.addAction(self.actionContract_Details)
        self.menuWindow.addAction(self.actionPortfolio_Table)
        self.menuWindow.addAction(self.actionScenario_Editor)
        self.menuWindow.addAction(self.actionTrace_Window)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(optionCalcMWIN)
        QtCore.QMetaObject.connectSlotsByName(optionCalcMWIN)

    def retranslateUi(self, optionCalcMWIN):
        optionCalcMWIN.setWindowTitle(QtGui.QApplication.translate("optionCalcMWIN", "Option Calculator", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("optionCalcMWIN", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Swaptions/ED options position analysis</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("optionCalcMWIN", "Trade date:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("optionCalcMWIN", "Horizon date:", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("optionCalcMWIN", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("optionCalcMWIN", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuWindow.setTitle(QtGui.QApplication.translate("optionCalcMWIN", "Window", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("optionCalcMWIN", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.action_New.setText(QtGui.QApplication.translate("optionCalcMWIN", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Open.setText(QtGui.QApplication.translate("optionCalcMWIN", "&Open", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save.setText(QtGui.QApplication.translate("optionCalcMWIN", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("optionCalcMWIN", "E&xit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_Qt.setText(QtGui.QApplication.translate("optionCalcMWIN", "About Qt", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrint.setText(QtGui.QApplication.translate("optionCalcMWIN", "&Print", None, QtGui.QApplication.UnicodeUTF8))
        self.actionProperty_Editor.setText(QtGui.QApplication.translate("optionCalcMWIN", "Property Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.actionScenarios.setText(QtGui.QApplication.translate("optionCalcMWIN", "Chart Setting", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContract_Details.setText(QtGui.QApplication.translate("optionCalcMWIN", "Contract Details", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPortfolio_Table.setText(QtGui.QApplication.translate("optionCalcMWIN", "Portfolio Table", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTrace_Window.setText(QtGui.QApplication.translate("optionCalcMWIN", "Trace Window", None, QtGui.QApplication.UnicodeUTF8))
        self.actionScenario_Editor.setText(QtGui.QApplication.translate("optionCalcMWIN", "Scenario Editor", None, QtGui.QApplication.UnicodeUTF8))

