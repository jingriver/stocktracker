from PyQt4 import QtCore, QtGui
from options import *
from config import *
from gensettings import Ui_SettingForm

class curveType:
    YLDBETA = 0
    HORIZON = 1
    BETA    = 2
    
class settingWnd(Ui_SettingForm, QtGui.QFrame):
    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent)

        self.setupUi(self)
        self.tabWidget.setCurrentIndex(0)
                
        self.dsb_start.setDecimals(1)
        self.dsb_end.setDecimals(1)
        self.dsb_step.setDecimals(1)
        
        self.dsb_start.setValue(-100.0)
        self.dsb_end.setValue(100)
        self.dsb_step.setValue(10)
        self.dsb_start.setSingleStep(self.dsb_step.value())
        self.dsb_end.setSingleStep(self.dsb_step.value())

        self.connect(self.dsb_start, QtCore.SIGNAL("valueChanged(double)"), self.yieldRange)
        self.connect(self.dsb_end, QtCore.SIGNAL("valueChanged(double)"), self.yieldRange)
        self.connect(self.dsb_step, QtCore.SIGNAL("valueChanged(double)"), self.yieldRange)
        
        self.btnGroup = QtGui.QButtonGroup(self.groupBox)
        self.btnGroup.addButton(self.rb_beta)
        self.btnGroup.addButton(self.rb_horizon)
        
        self.cvtype = curveType.YLDBETA

        self.rb_beta.setChecked(True)
        self.le_horizonStep.setText("3m")
        self.dsb_betaStep.setValue(10)
        self.dsb_betaStep.setDecimals(1)

        self.betaStep = self.dsb_betaStep.value()
        self.horizonStep = str(self.le_horizonStep.text())
        self.valChanged = False
        
        #self.connect(self.btnGroup, QtCore.SIGNAL("buttonClicked(QAbstractButton *)"), self.curveType)
        self.connect(self.btnGroup, QtCore.SIGNAL("buttonClicked(int)"), self.setCurveType)
#        self.connect(self.dsb_betaStep, QtCore.SIGNAL("editingFinished()"), self.setBetaStep)        
#        self.connect(self.le_horizonStep, QtCore.SIGNAL("textChanged(const QString &)"), self.setHorizonStep)
        #self.connect(self.dsb_betaStep, QtCore.SIGNAL("valueChanged(double)"), self.setBetaStep)
        self.connect(self.dsb_betaStep, QtCore.SIGNAL("editingFinished()"), self.setBetaStep)
        self.connect(self.le_horizonStep, QtCore.SIGNAL("editingFinished()"), self.setHorizonStep)


	self.label_5.hide()
	self.dsb_betaStep.hide()
        
    def setBetaStep(self):
        val = self.dsb_betaStep.value()
        if self.betaStep != val:
            self.betaStep = val
            self.valChanged = True
            self.rb_beta.click()
        
    def setHorizonStep(self):
        val = str(self.le_horizonStep.text())
        if self.horizonStep != val:
            self.horizonStep = val
            self.valChanged = True       
            self.rb_horizon.click()
        
    def setCurveType(self, args):
        cval = IIf(self.btnGroup.checkedButton()==self.rb_beta, curveType.BETA, curveType.HORIZON)
        if self.cvtype != cval or self.valChanged:
            self.cvtype = cval
            self.valChanged = False
            if self.btnGroup.checkedButton()==self.rb_beta:
                val = self.dsb_betaStep.value()
                self.emit(QtCore.SIGNAL("curveTypeChanged"), (curveType.BETA, val))
            elif self.btnGroup.checkedButton()==self.rb_horizon:
                val = str(self.le_horizonStep.text()).strip()
                self.emit(QtCore.SIGNAL("curveTypeChanged"), (curveType.HORIZON, val))
            else:
                logging.error("unknown checkedButtion")

    def yieldRange(self, args):
        step = self.dsb_step.value()
        self.dsb_start.setSingleStep(step)
        self.dsb_end.setSingleStep(step)            
        val = (self.dsb_start.value(), self.dsb_end.value(), step)        
        self.emit(QtCore.SIGNAL("yldRangeChanged"), val)
                
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    view = settingWnd()
    view.show()
    sys.exit(app.exec_())
