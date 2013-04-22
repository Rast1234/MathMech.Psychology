#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from PySide import QtCore, QtGui
from window import *
from os.path import isfile, join
from PlayerControl import PlayerControl
from Config import Config
import Messages


class ControlMainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config = Config()
        self.embedPlayer()
        self.player = PlayerControl(self.ui.vframe)

        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

        self.populateFiles()

    def embedPlayer(self):
        #self.vframe = QtGui.QFrame()
        self.palette = self.ui.vframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.ui.vframe.setPalette(self.palette)
        self.ui.vframe.setAutoFillBackground(True)
        #self.ui.verticalLayout.addWidget(self.vframe)

    def populateFiles(self):
        for x in self.listFiles():
            item = QtGui.QListWidgetItem(self.ui.fileList)
            item.setText(x)
            item.setFlags(item.flags() or QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)  # play all stuff by default

    def fail(self, title, message):
        reply = QtGui.QMessageBox.critical(self, title, message)
        # msgBox.exec_()

    def listFiles(self):
        try:
            os.listdir(self.config.folder)
        except OSError:  # invalid dir
            self.config.folder = self.config.default_folder
        finally:
            listing = os.listdir(self.config.folder)
        files = [x for x in listing if isfile(join(self.config.folder, x))]
        result = []
        if not self.config.extensions:
            result = files
        else:
            for x in files:
                if x.split('.')[-1] in self.config.extensions:
                    result.append(join(self.config.folder, x))
        return result

    @QtCore.Slot()
    def on_click(self):
        print('clicked')

        files = []
        for x in xrange(self.ui.fileList.count()):
            if self.ui.fileList.item(x).checkState() == QtCore.Qt.Checked:
                files.append(self.ui.fileList.item(x).text().encode('ascii'))
        self.config.files = files
        self.ComeOn()

    def closeEvent(self, event):
        """Overrides default closeEvent"""
        self.player.Shutdown()
        pass

    def ComeOn(self):
        try:
            self.player.Open(self.config.files[0])
            self.player.Play()
        except IndexError:
            self.fail(Messages.title_fail, Messages.no_file)

    def keyPressEvent(self, evt):
        """Overrides default keypress"""
        key = evt.key()
        if key == QtCore.Key_Escape:
            self.close()
        elif key == QtCore.Key_F or key == QtCore.Key_F11:
            self.player.FullScreen()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
