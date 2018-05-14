# -*- coding: utf-8 -*-
"""
Created on Mon May  7 00:22:57 2018

@author: cos
"""

import sys, csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import ndimage
from matplotlib.widgets import RectangleSelector
import cv2
import numpy as np

form_class = uic.loadUiType("ver10.2.ui")[0]



class MdiSub(QMainWindow):
    def __init__(self):
        super(MdiSub, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.fig = plt.Figure(tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QHBoxLayout())
        
        self.widget.layout().addWidget(self.canvas)
        
        self.ax = self.fig.add_subplot(111)
        
        def line_select_callback(eclick, erelease):
            self.x1, self.y1 = eclick.xdata, eclick.ydata
            self.x2, self.y2 = erelease.xdata, erelease.ydata
            
        self.RS= RectangleSelector(self.ax, line_select_callback, drawtype='box', useblit=True, button=[1, 3], minspanx=1, minspany=1, spancoords='pixels', interactive=True)

        self.cid = self.canvas.mpl_connect('key_press_event', self.RS)
        
        self.M=[]
        global dot
        dot=[]
        
    def loadImage(self, fileName):
        im = plt.imread(fileName)
        self.im = np.flipud(im)
        self.ax.imshow(self.im, origin='lower')
        self.setWindowTitle(fileName)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.canvas.draw()
        QApplication.restoreOverrideCursor()

        return True
    
    def loadVideo(self, image, cnt):
        b, g, r = cv2.split(image)
        im = cv2.merge([r,g,b])
        self.im = np.flipud(im)
        self.setWindowTitle(str(int(cnt)))
        self.ax.imshow(self.im, origin='lower')
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.canvas.draw()
        QApplication.restoreOverrideCursor()

        return True
    
    def rotate(self):
        angle, ok = QInputDialog.getDouble(self, '이미지 회전', '이미지 회전각을 입력하세요.')
        if ok:
            self.im = ndimage.rotate(self.im, angle)
        self.ax.clear()
        self.ax.imshow(self.im)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.canvas.draw()
        QApplication.restoreOverrideCursor()
        
    def select(self):
        self.im = self.im[int(self.y1):int(self.y2), int(self.x1):int(self.x2)]
        self.ax.clear()
        self.ax.imshow(self.im)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.canvas.draw()
        QApplication.restoreOverrideCursor()
            
    def onclick2(self, event):
        if event.xdata and event.ydata:
            self.M.append((event.xdata, event.ydata))
        if len(self.M)%2==0:
            line = self.ax.plot([self.M[-2][0], self.M[-1][0]], [self.M[-2][1], self.M[-1][1]])
            self.canvas.draw()
        if len(self.M)==4:
            slope1 = (self.M[-2][0] - self.M[-1][0]) / (self.M[-2][1] - self.M[-1][1])
            slope2 = (self.M[-4][0] - self.M[-3][0]) / (self.M[-4][1] - self.M[-3][1])
            an = abs(np.degrees(np.arctan(slope1)) - np.degrees(np.arctan(slope2)))
            self.statusBar().showMessage(str(an)+' or '+str(180-an))
            self.canvas.draw()
            self.M=[]
            win.actionAngle.setChecked(False)
        
        
    def angle(self):
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick2)
        while(self.ax.lines): self.ax.lines.pop(0)
        self.canvas.draw()
            
    def onclick(self, event):
        if event.xdata and event.ydata:
            win.put(len(dot), event.xdata, event.ydata)
            #win.table.setItem(len(dot), 1, QTableWidgetItem(str(event.ydata)))
            dot.append(self.ax.scatter(event.xdata, event.ydata))
            self.canvas.draw()
            self.statusBar().showMessage(str(event.xdata)+', '+str(event.ydata))
        #win.actionPoint.setChecked(False)
            

    def point(self):
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick)
        while (self.ax.collections):
            self.ax.collections.pop()
        self.canvas.draw()
        
    def dis(self):
        self.canvas.mpl_disconnect(self.cid)
        
    def graph(self):
        img = cv2.cvtColor(self.im, cv2.COLOR_RGB2GRAY)
        self.ax.clear()
        y, ok = QInputDialog.getDouble(self, '그래프', 'y좌표를 입력하세요.')
        if ok:
            self.ax.plot(img[int(y), 0:len(self.im[0])])
        self.canvas.draw()
        
    def onclick3(self, event):
        if event.xdata and event.ydata:
            self.M.append((event.xdata, event.ydata))
        if len(self.M)==2:
            line = self.ax.plot([self.M[-2][0], self.M[-1][0]], [self.M[-2][1], self.M[-1][1]])
            llen = np.sqrt((self.M[-2][0] - self.M[-1][0])**2 + (self.M[-2][1] - self.M[-1][1])**2)
            self.canvas.draw()
            self.statusBar().showMessage(str(llen))
            self.M=[]
            win.actionLength.setChecked(False)
        
        
    def length(self):
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick3)
        while(self.ax.lines): self.ax.lines.pop(0)
        self.canvas.draw()
        
    def onclick4(self, event):
        if event.xdata and event.ydata:
            print(self.im[int(event.xdata), int(event.ydata)])
            win.actionColor.setChecked(False)
            #self.canvas.mpl_disconnect(self.cid)
        
    def color(self):
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick4)
    
        
class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Image Analyzer ver.10.3.3")
        self.mdiArea = QMdiArea()
        self.setCentralWidget(self.mdiArea)
        self.createDockWindows()
        '''
        subWindow = QMdiSubWindow(self)
        subWindow.setWidget(QWidget())
        self.mdiArea.addSubWindow(subWindow)
        '''
        self.actionOpen.triggered.connect(self.openData)
        self.actionRotate.triggered.connect(self.rotateData)
        self.actionCrop.triggered.connect(self.cropData)
        self.actionAngle.toggled.connect(self.angle)
        self.actionPoint.triggered.connect(self.point)
        self.actionSaveTable.triggered.connect(self.saveTable)
        self.actionGraph.triggered.connect(self.graph)
        self.actionDelete.triggered.connect(self.delete)
        self.actionLength.triggered.connect(self.length)
        self.actionColor.toggled.connect(self.color)
        
        
    def createDockWindows(self):
        dock = QDockWidget("Table", self)
        #dock.setBaseSize(10, 600)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.table = QTableWidget(dock)
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(['x', 'y','x Diff.', 'y Diff', 'length'])
        #self.table.resizeColumnsToContents()
        dock.setWidget(self.table)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        dock = QDockWidget("Graph", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.mat = QWidget(dock)
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.mat.setLayout(QHBoxLayout())
        self.mat.layout().addWidget(self.canvas)
        self.axe = self.fig.add_subplot(111)
        #self.axe.plot([1,2,3])
        dock.setWidget(self.mat)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        
    def put(self, x, y, z):
        self.table.setRowCount(self.table.rowCount()+1)
        self.table.setItem(x,0,QTableWidgetItem('%.2f' %y))
        self.table.setItem(x,1,QTableWidgetItem('%.2f' %z))
        self.table.resizeColumnsToContents()
        self.axe.scatter(y, z)
        self.canvas.draw()
        
        
    def saveTable(self):
        path = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
    #if not path.isEmpty():
        with open(path[0], 'w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, delimiter=',')
            for row in range(self.table.rowCount()):
                rowdata = []
                for column in range(self.table.columnCount()):
                    item = self.table.item(row, column)
                    if item is not None:
                        rowdata.append(item.text())
                    else:
                        rowdata.append('')
                writer.writerow(rowdata)
        
    def openData(self):
        fileName, _ = QFileDialog.getOpenFileName(self)
        if fileName[-3:] == ('avi' or 'mp4'):
            vidcap = cv2.VideoCapture(fileName)
            success = True
            cnt=0
            while success:
                vidcap.set(cv2.CAP_PROP_POS_MSEC, cnt)
                success,image = vidcap.read()
                cnt+=1000
                Sub = self.createMdiSub()
                if success and Sub.loadVideo(image, cnt/1000):
                    Sub.show()
                else:
                    Sub.close()
                
            self.statusBar().showMessage("File loaded", 2000)
        elif fileName:
            Sub = self.createMdiSub()
            if Sub.loadImage(fileName):
                self.statusBar().showMessage("File loaded", 2000)
                Sub.show()
            else:
                Sub.close()
                
    def rotateData(self):
        if self.activeMdiSub():
            self.activeMdiSub().rotate()
            
    def cropData(self):
        if self.activeMdiSub():
            self.activeMdiSub().select()
            
    def angle(self):
        if self.activeMdiSub() and self.actionAngle.isChecked():
            self.activeMdiSub().angle()
            
        elif self.activeMdiSub() and not self.actionAngle.isChecked():
            self.activeMdiSub().dis()
            
    def point(self):
        if self.activeMdiSub() and self.actionPoint.isChecked():
            self.activeMdiSub().point()
        elif self.activeMdiSub() and not self.actionPoint.isChecked():
            self.activeMdiSub().dis()
            
    def graph(self):
        if self.activeMdiSub():
            self.activeMdiSub().graph()
            
    def delete(self):
        self.table.clearContents()
        global dot
        dot=[]
        '''
        while(self.activeMdiSub().ax.collections):
            self.activeMdiSub().ax.collections.pop()
        self.activeMdiSub().canvas.draw()
        '''
        while(self.axe.collections):
            self.axe.collections.pop()
        self.canvas.draw()
        while self.table.rowCount():
            self.table.removeRow(self.table.rowCount())
            self.table.setRowCount(self.table.rowCount()-1)
            
    def length(self):
        if self.activeMdiSub() and self.actionLength.isChecked():
            self.activeMdiSub().length()
            
        elif self.activeMdiSub() and not self.actionLength.isChecked():
            self.activeMdiSub().dis()
            
    def color(self):
        if self.activeMdiSub() and self.actionColor.isChecked():
            c = self.activeMdiSub().color()
        elif self.activeMdiSub() and not self.actionColor.isChecked():
            self.activeMdiSub().dis()
                
    def createMdiSub(self):
        Sub = MdiSub()
        self.mdiArea.addSubWindow(Sub)
        return Sub
    
    def activeMdiSub(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()