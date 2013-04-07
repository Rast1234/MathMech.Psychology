#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from PySide import QtCore, QtGui
from window import *
from os.path import isfile, join
import vlc

class ControlMainWindow(QtGui.QMainWindow):
    __extList = ['avi', 'mpg', 'mpeg', 'mkv', 'wmv',
                 'flv', 'mov', 'mp4', 'ts', 'dv', ]
    __dir = '' #'video\\'
    __player = '.\\vlc\\vlc.exe' #windows only

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.vframe = QtGui.QFrame()
        self.palette = self.vframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.vframe.setPalette(self.palette)
        self.vframe.setAutoFillBackground(True)
        self.ui.horizontalLayout.addWidget(self.vframe)


        for x in self.listFiles():
            item = QtGui.QListWidgetItem(self.ui.fileList)
            item.setText(x)
            item.setFlags(item.flags() or QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)  #play all stuff by default

        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

    def fail(self, title, message):
        reply = QtGui.QMessageBox.critical(self, title, message)
        # msgBox.exec_()

    def listFiles(self):
        files = [x for x in os.listdir(self.__dir) if isfile(join(self.__dir, x))]
        result = []
        if not self.__extList:
            result = files
        else:
            for x in files:
                if x.split('.')[-1] in self.__extList:
                    result.append(join(self.__dir, x))
        return result

    @QtCore.Slot()
    def on_click(self):
        print('clicked')

        files = []
        for x in xrange(self.ui.fileList.count()):
            if self.ui.fileList.item(x).checkState() == QtCore.Qt.Checked:
                files.append(self.ui.fileList.item(x).text().encode('ascii'))
        config = {'files': files,
                  }
        self.ComeOn(config)

    def closeEvent(self, event):
        """Overrides default closeEvent"""
        #send 'quit' to VLC
        pass

    def Play(self):
        """Play video
        """
        if self.mediaplayer.play() == -1:
            self.fail('Ошибка', 'Не выбрано ни одного файла.')
            return
        self.mediaplayer.play()

    def Pause(self):
        """Pause video
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()

    def Stop(self):
        """Stop video
        """
        self.mediaplayer.stop()

    def ComeOn(self, config):
        try:
            one = config['files'][0]
        except IndexError:
            self.fail('ОШИБКА', 'Не выбрано ни одного файла')
        #create 'media' instance
        self.media = self.instance.media_new(one)
        #put it in the player
        self.mediaplayer.set_media(self.media)
        self.Play()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
