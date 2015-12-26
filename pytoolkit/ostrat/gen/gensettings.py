# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings.ui'
#
# Created: Mon May 19 10:36:17 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SettingForm(object):
    def setupUi(self, SettingForm):
        SettingForm.setObjectName("SettingForm")
        SettingForm.resize(QtCore.QSize(QtCore.QRect(0,0,379,214).size()).expandedTo(SettingForm.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(SettingForm)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.tabWidget = QtGui.QTabWidget(SettingForm)
        self.tabWidget.setObjectName("tabWidget")

        self.tab_yld = QtGui.QWidget()
        self.tab_yld.setObjectName("tab_yld")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.tab_yld)
        self.vboxlayout1.setMargin(9)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.label_2 = QtGui.QLabel(self.tab_yld)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,0,1,1,1)

        self.dsb_start = QtGui.QDoubleSpinBox(self.tab_yld)
        self.dsb_start.setMinimumSize(QtCore.QSize(70,0))
        self.dsb_start.setMaximum(1000.0)
        self.dsb_start.setMinimum(-1000.0)
        self.dsb_start.setObjectName("dsb_start")
        self.gridlayout.addWidget(self.dsb_start,1,0,1,1)

        self.label_3 = QtGui.QLabel(self.tab_yld)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,0,2,1,1)

        self.dsb_step = QtGui.QDoubleSpinBox(self.tab_yld)
        self.dsb_step.setMinimumSize(QtCore.QSize(70,0))
        self.dsb_step.setObjectName("dsb_step")
        self.gridlayout.addWidget(self.dsb_step,1,2,1,1)

        self.dsb_end = QtGui.QDoubleSpinBox(self.tab_yld)
        self.dsb_end.setMinimumSize(QtCore.QSize(70,0))
        self.dsb_end.setObjectName("dsb_end")
        self.gridlayout.addWidget(self.dsb_end,1,1,1,1)

        self.label = QtGui.QLabel(self.tab_yld)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)
        self.hboxlayout.addLayout(self.gridlayout)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout)

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab_yld,"")

        self.tab_curve = QtGui.QWidget()
        self.tab_curve.setObjectName("tab_curve")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.tab_curve)
        self.vboxlayout2.setMargin(9)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.groupBox = QtGui.QGroupBox(self.tab_curve)
        self.groupBox.setObjectName("groupBox")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout3.setMargin(9)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.rb_beta = QtGui.QRadioButton(self.groupBox)
        self.rb_beta.setObjectName("rb_beta")
        self.hboxlayout2.addWidget(self.rb_beta)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem2)
        self.vboxlayout3.addLayout(self.hboxlayout2)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        spacerItem3 = QtGui.QSpacerItem(21,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem3)

        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.hboxlayout3.addWidget(self.label_5)

        self.dsb_betaStep = QtGui.QDoubleSpinBox(self.groupBox)
        self.dsb_betaStep.setObjectName("dsb_betaStep")
        self.hboxlayout3.addWidget(self.dsb_betaStep)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.rb_horizon = QtGui.QRadioButton(self.groupBox)
        self.rb_horizon.setObjectName("rb_horizon")
        self.hboxlayout4.addWidget(self.rb_horizon)

        spacerItem4 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem4)
        self.vboxlayout3.addLayout(self.hboxlayout4)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        spacerItem5 = QtGui.QSpacerItem(21,22,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem5)

        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.hboxlayout5.addWidget(self.label_6)

        self.le_horizonStep = QtGui.QLineEdit(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.le_horizonStep.sizePolicy().hasHeightForWidth())
        self.le_horizonStep.setSizePolicy(sizePolicy)
        self.le_horizonStep.setObjectName("le_horizonStep")
        self.hboxlayout5.addWidget(self.le_horizonStep)
        self.vboxlayout3.addLayout(self.hboxlayout5)
        self.hboxlayout1.addWidget(self.groupBox)

        spacerItem6 = QtGui.QSpacerItem(131,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem6)
        self.vboxlayout2.addLayout(self.hboxlayout1)

        spacerItem7 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout2.addItem(spacerItem7)
        self.tabWidget.addTab(self.tab_curve,"")
        self.vboxlayout.addWidget(self.tabWidget)

        self.retranslateUi(SettingForm)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(SettingForm)

    def retranslateUi(self, SettingForm):
        SettingForm.setWindowTitle(QtGui.QApplication.translate("SettingForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SettingForm", "End Point", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("SettingForm", "Step", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SettingForm", "Start Point", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_yld), QtGui.QApplication.translate("SettingForm", "Yield Change", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("SettingForm", "Curve Type", None, QtGui.QApplication.UnicodeUTF8))
        self.rb_beta.setText(QtGui.QApplication.translate("SettingForm", "Yield beta (bp)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("SettingForm", "Yield beta change step    ", None, QtGui.QApplication.UnicodeUTF8))
        self.rb_horizon.setText(QtGui.QApplication.translate("SettingForm", "Horizon Date", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("SettingForm", "Horizon Date change step", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_curve), QtGui.QApplication.translate("SettingForm", "Curve Settings", None, QtGui.QApplication.UnicodeUTF8))

