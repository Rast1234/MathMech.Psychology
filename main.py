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
        self.player = PlayerControl(self)
        self.embedPlayer(self.player)

        for x in self.listFiles():
            item = QtGui.QListWidgetItem(self.ui.fileList)
            item.setText(x)
            item.setFlags(item.flags() or QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)  # play all stuff by default

        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

    def embedPlayer(self, player):
        self.vframe = QtGui.QFrame()
        self.palette = self.vframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.vframe.setPalette(self.palette)
        self.vframe.setAutoFillBackground(True)
        self.ui.horizontalLayout.addWidget(self.vframe)

    def fail(self, title, message):
        reply = QtGui.QMessageBox.critical(self, title, message)
        # msgBox.exec_()

    def listFiles(self):
        files = [x for x in os.listdir(self.config.folder) if isfile(join(self.config.folder, x))]
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
        #send 'quit' to VLC
        pass

    def ComeOn(self):
        try:
            one = self.config.files[0]
            self.player.Open(one)
            self.player.Play()
        except IndexError:
            self.fail(Messages.title_fail, Messages.no_file)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
