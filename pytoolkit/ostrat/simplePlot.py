import sys
from math import *
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.Qwt5 import *
import locale
from config import *

class simpleData(QwtData):
    def __init__(self, func, size):
        QwtData.__init__(self)
        self.func = func
        self.dsize = size
        
    def size(self):
        return self.dsize
    
    def x(self, i):
        return 0.1*i
    
    def y(self, i):
        return self.func(self.x(i))
    
    def copy(self):
        return simpleData(self.func, self.dsize)
    
    def xarray(self):
        return map(self.x, range(0,self.dsize+1))
    
    def yarray(self):
        return map(self.y, range(0,self.dsize+1))

class plPlot(QwtPlot):
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)
        self.dateAxis = None
        
        qtitle = QwtText("P/L to Horizon")
        qtitle.setFont(QtGui.QFont("Arial", 14))
        self.setCanvasBackground(QtCore.Qt.white)
        self.setTitle(qtitle)
        
        legend = Qwt.QwtLegend()
        legend.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Sunken)
        #legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        legend.setItemMode(Qwt.QwtLegend.ClickableItem)
        self.insertLegend(legend, QwtPlot.BottomLegend)        
#        self.connect(self,QtCore.SIGNAL('legendChecked(QwtPlotItem*, bool)'), self.showCurve)
        self.connect(self,QtCore.SIGNAL('legendClicked(QwtPlotItem*)'), self.toggleVisibility)
        
        self.setAxisTitle(self.xBottom, "Yield Change (bp)")
        self.setAxisTitle(self.yLeft, "P/L ($) to Horizon")

        scaleDraw = self.axisScaleDraw(QwtPlot.yLeft)
        myscaleDraw = myScaleDraw(scaleDraw)
#        scaleDraw.setMinimumExtent(100)
        self.setAxisScaleDraw(Qwt.QwtPlot.yLeft, myscaleDraw)
        
        #self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        #self.setAxisMaxMinor(QwtPlot.yLeft, 5)
        #self.setAxisScaleEngine(QwtPlot.xBottom, QwtLog10ScaleEngine())

        self.grid = QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.setMajPen(QtGui.QPen(QtCore.Qt.gray, 0, QtCore.Qt.SolidLine))
        self.grid.setMinPen(QtGui.QPen(QtCore.Qt.gray, 0 , QtCore.Qt.DotLine))
        self.grid.attach(self)
                            
#        mark = QwtPlotMarker()
#        #mark.setLabel(QwtText("y = 0"))
#        mark.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
#        mark.setLineStyle(QwtPlotMarker.VLine)
#        mark.setXValue(0)
#        mark.attach(self)
        
        self.canvas().setFocusIndicator(QwtPlotCanvas.ItemFocusIndicator)
        self.canvas().setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.canvas().setLineWidth(1)        
        #self.setMouseTracking(True)
        
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        #self.setAutoReplot(False)        
        
        #self.insertCurve()
#        xMap = QwtScaleMap()
#        yMap = QwtScaleMap()
#        xMap.setScaleInterval(-0.5, 10.5)
#        yMap.setScaleInterval(-2.0, 2.0)

#    def paintEvent(self, event):
#        #painter.fillRect(event.rect(), QtCore.Qt.white)
#        #self.resize(self.parentWidget().size())
#        pass

#    def mouseMoveEvent(self, event):
#        print event.pos().x(), event.pos().y()
#        x1 = event.pos().x()
#        y1 = event.pos().y()
#        QtGui.QCursor.setPos(event.pos())
#        QwtPlot.mouseMoveEvent(self, event)

    def toggleVisibility(self, plotItem):
        """Toggle the visibility of a plot item
        """
        plotItem.setVisible(not plotItem.isVisible())
        self.replot()

    def showCurve(self, item, on):
        item.setVisible(on)
        widget = self.legend().find(item)
        if isinstance(widget, QwtLegendItem):
            widget.setChecked(on)
        self.replot()

    def printPlot(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setColorMode(QtGui.QPrinter.Color)
        printDialog = QtGui.QPrintDialog(printer)
        if printDialog.exec_():
            self.__plot.print_(printer)

    def insertCurve(self):
        d1=self.newCurveData(sin)
        c1 = self.newCurve("y = sin(x)", (d1.xarray(), d1.yarray()))
        c1.attach(self)
        
    def newCurveData(self, func, nPoints=100):
#        dx = range(nPoints)
#        dx = map(lambda x: x/10.0, dx)
#        dy = map(lambda x: sin(x), dx)
#        dz = map(lambda x: cos(x), dx)

#        csin.setData(dx, dy)
#        ccos.setData(dx, dz)

        s1 = simpleData(func, nPoints)
        return s1
            
    def newCurve(self, cname, cdata, curveCol=QtCore.Qt.red, symbolCol=QtCore.Qt.black, symbolStyle=QwtSymbol.Ellipse):
        csin = QwtPlotCurve(cname)
        csin.setRenderHint(QwtPlotItem.RenderAntialiased)
        csin.setPen(curveCol)
        #csin.setStyle(QwtPlotCurve.Sticks)
        #csin.setCurveType(QwtPlotCurve.Xfy)
        #csin.setCurveAttribute(QwtPlotCurve.Fitted)
        #csin.attach(self)

        sym = QwtSymbol()
        sym.setStyle(symbolStyle)
        #sym.setPen(symbolCol)
        sym.setPen(curveCol)
        sym.setSize(7)
        csin.setSymbol(sym)
                        
        csin.setData(cdata[0], cdata[1])
        #csin.setData(cdata)
        return csin

    def newTimeSeries(self, cname, cdata):
        self.dateAxis = DateArray(cdata)
        cdata = (self.dateAxis.intArray, cdata[1])
        #print cdata
        
        qtitle = QwtText("Data Query TimeSeries")
        qtitle.setFont(QtGui.QFont("Arial", 14))
        self.setCanvasBackground(QtCore.Qt.white)
        self.setTitle(qtitle)

        self.setAxisTitle(self.yLeft, cname)
                        
        self.setAxisTitle(QwtPlot.xBottom, "time [y:m:d]")
        self.setAxisScaleDraw(QwtPlot.xBottom, TimeScaleDraw(self.dateAxis))
        
        self.setAxisLabelRotation(QwtPlot.xBottom, -50.0)
        self.setAxisLabelAlignment(
            QwtPlot.xBottom, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

#        self.mark = QwtPlotMarker()
#        #self.mark.setLabel(QwtText("y = 0"))
#        self.mark.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
#        self.mark.setLineStyle(QwtPlotMarker.VLine)        
#        self.mark.attach(self)
#        self.mark.setXValue(10)
        
        return self.newCurve(cname, cdata)

    def preTimeSeries(self, cname, cdata):
        self.enableAxis(Qwt.QwtPlot.yRight)        
        self.dateAxis = DateArray(cdata)
        cdata = (self.dateAxis.intArray, cdata[1])

        self.setAxisTitle(self.yRight, cname)
        return self.newCurve(cname, cdata, curveCol=QtCore.Qt.blue, symbolCol=QtCore.Qt.green, symbolStyle=QwtSymbol.Rect)

    def replotWithZoomer(self):
        """Auto scale and clear the zoom stack
        """

        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        self.replot()

class DateArray:
    def __init__(self, data):
        dtArray, dataArray = data
        self.dtArray = dtArray
        self.startDate = min(dtArray)
        self.endDate = max(dtArray)
        self.intArray = [int((x-self.startDate).days) for x in self.dtArray]
        self.dateDict = {}
        for i in range(len(self.dtArray)):
            self.dateDict[self.intArray[i]] = dataArray[i]

    def getDateStr(self, days):
        dt = addDays(self.startDate, days)
        return nvldate(dt,"%Y-%m-%d")

class myScaleDraw(QwtScaleDraw):
    def __init__(self, *args):
        QwtScaleDraw.__init__(self, *args)
        locale.setlocale(locale.LC_ALL, "")
        
    def label(self, val):
        valstr = locale.format("%8.2f", val, True)
        #return QwtText(QtCore.QString.number(val, 'f', 2))
        return QwtText(QtCore.QString(valstr))
            
class TimeScaleDraw(QwtScaleDraw):
    def __init__(self, dateAxis, *args):
        QwtScaleDraw.__init__(self, *args)
        self.dateAxis = dateAxis
 
    def label(self, value):        
        return QwtText(self.dateAxis.getDateStr(int(value)))

class CursorPicker(QwtPlotPicker):
    def __init__(self, *args):
        QwtPlotPicker.__init__(self, *args)
        self.cursor = self.canvas().cursor()
        #self.connect(self, QtCore.SIGNAL("moved(const QwtDoublePoint &)"), self.test)
        #self.connect(self, QtCore.SIGNAL("selected(const QwtDoublePoint &)"), self.test)
    
    def test(self, args):
        print args.x(), args.y()
        #self.cursor.setPos(args.x(), args.y()-100)        
        
    def trackerText(self, pos):
        plotpos = self.invTransform(pos)
        return QwtText("%f -- %f" % (plotpos.x(),plotpos.y()))

class DQPicker(QwtPlotPicker):
    def __init__(self, dateAxis, *args):
        QwtPlotPicker.__init__(self, *args)
        self.dateAxis = dateAxis
        self.cursor = self.canvas().cursor()

    def setDateAxis(self, dateAxis):
        self.dateAxis = dateAxis
        
    def trackerText(self, pos):
        if self.dateAxis:
    #        print "***"
    #        print pos.x(), pos.y()
    #        print "$$$"
    #        print self.cursor.pos().x(), self.cursor.pos().y()
            plotpos = self.invTransform(pos)
    #        print "---"
    #        print plotpos.x(), plotpos.y()
            xval = int(plotpos.x())
                        
            if xval in self.dateAxis.dateDict:
                return QwtText("(%s, %f)" % (self.dateAxis.getDateStr(xval),self.dateAxis.dateDict[xval]))
            else:
                return QwtText("(%s, %f)" % (self.dateAxis.getDateStr(xval),plotpos.y()))
        else:
            return QwtPlotPicker.trackerText(self, pos)
        
def main(args):
    app = QtGui.QApplication(args)
    demo = plPlot()
    demo.insertCurve()
    demo.resize(600,400)
    print QtCore.QString.number(25082899.2121,'f', 0)
    demo.show()
    #demo.printPlot()
#    zoomer = QwtPlotZoomer(QwtPlot.xBottom,
#                           QwtPlot.yLeft,
#                           QwtPicker.DragSelection,
#                           QwtPicker.AlwaysOff,
#                           demo.canvas())
#    zoomer.setRubberBandPen(QtGui.QPen(QtCore.Qt.green))
    picker = DQPicker(QwtPlot.xBottom,
                           QwtPlot.yLeft,
                           QwtPicker.PointSelection,
                           QwtPlotPicker.CrossRubberBand,
                           QwtPicker.AlwaysOn,
                           demo.canvas())
    
    picker.setRubberBandPen(QtGui.QPen(QtCore.Qt.green))
        
    sys.exit(app.exec_())

# main()

if __name__ == '__main__':
    main(sys.argv)    
        
        
