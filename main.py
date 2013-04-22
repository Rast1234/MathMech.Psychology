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
    """
    A main window class
    """

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()  # get layout from 'pyside-uic mainwindow.ui' command
        self.ui.setupUi(self)

        self.config = Config()
        self.beautifyPlyer()
        self.player = PlayerControl(self.ui.vframe, self.config.vlc_args)

        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

        self.populateFiles()

    def beautifyPlyer(self):
        """
        Make player's frame black
        """
        self.palette = self.ui.vframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.ui.vframe.setPalette(self.palette)
        self.ui.vframe.setAutoFillBackground(True)

    def populateFiles(self):
        """
        Fill list widget with items
        """
        for x in self.listFiles():
            item = QtGui.QListWidgetItem(self.ui.fileList)
            item.setText(x)
            item.setFlags(item.flags() or QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)  # play all stuff by default

    def fail(self, title, message):
        """
        Display a warning MessageBox
        """
        reply = QtGui.QMessageBox.critical(self, title, message)

    def listFiles(self):
        """
        Get video files from directory
        """
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

    def on_click(self):
        """
        Start Button click event handler
        """
        files = []
        for x in xrange(self.ui.fileList.count()):
            if self.ui.fileList.item(x).checkState() == QtCore.Qt.Checked:
                files.append(self.ui.fileList.item(x).text().encode('ascii'))
        self.config.files = files
        self.Launch()

    def closeEvent(self, event):
        """
        Overrides default closeEvent
        """
        self.player.Shutdown()
        pass

    def Launch(self):
        """
        Begin work
        """
        try:
            self.player.Open(self.config.files, self.config.repeat)
            #self.player.Play()
        except IndexError:
            self.fail(Messages.title_fail, Messages.no_file)

    def keyPressEvent(self, event):
        """Overrides default keypress"""
        key = event.key()
        if key in self.config.keys['exit']:
            self.close()
        elif key in self.config.keys['fullscreen']:
            self.toggleFullScreen()
        elif key in self.config.keys['speedUp']:
            self.speedInc()
        elif key in self.config.keys['speedDown']:
            self.speedDec()

    def speedInc(self):
            self.player.SetSpeed(10)

    def speedDec(self):
            self.player.SetSpeed(0.5)

    def toggleFullScreen(self):
        if not self.fullscreen:
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.showNormal()
            self.fullscreen = False

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
