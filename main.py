#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import sys
import signal
from os.path import isfile, join

from PySide.QtCore import *
from PySide.QtGui  import *

from window import *
from PlayerControl import PlayerControl
from Config import Config
from RulesTableWidget import RulesTableWidget
import Messages


class ControlMainWindow(QMainWindow):
    """A main window class
    """

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()  # get layout from 'pyside-uic mainwindow.ui' command
        self.ui.setupUi(self)

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, SIGNAL("timeout()"), self.refresh)

        self.config = Config()
        self.beautifyPlyer()
        self.player = PlayerControl(self.ui.vframe, self.config.vlc_args)

        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

        self.ui.rulesTable = RulesTableWidget(self.ui.rulesTableFrame)
        self.ui.rulesTable.fromRulesList( self.config.config['rules'] )
        
        add_rule_callback = lambda: self.ui.rulesTable.addRule("00:00", "0.00x")
        remove_rule_callback = lambda: self.ui.rulesTable.removeRule()
        self.ui.addRuleButton.clicked.connect(add_rule_callback)
        self.ui.removeRuleButton.clicked.connect(remove_rule_callback)

        self.fullscreen = False

        self.populateFiles()


    def beautifyPlyer(self):
        """Make player's frame black
        """
        self.palette = self.ui.vframe.palette()
        self.palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.ui.vframe.setPalette(self.palette)
        self.ui.vframe.setAutoFillBackground(True)


    def populateFiles(self):
        """Fill list widget with items
        """
        for x in self.listFiles():
            item = QListWidgetItem(self.ui.fileList)
            item.setText(x)
            item.setFlags(item.flags() or Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # play all stuff by default


    def fail(self, title, message):
        """Display a warning MessageBox
        """
        reply = QMessageBox.critical(self, title, message)


    def listFiles(self):
        """Get video files from directory
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


    def refresh(self):
        """Update active UI elements: time, speed
        """
        if not self.player.IsPlaying():
            self.timer.stop()
            self.fail("timer","timer stopped from refresh()")
            pass
        self.ui.speedIndicator.display(self.player.GetSpeed())
        self.ui.speedIndicator.raise_()


    def on_click(self):
        """Start Button click event handler
        """

        self.config.config['rules'] = self.ui.rulesTable.toRulesList()

        files = []
        for x in xrange(self.ui.fileList.count()):
            if self.ui.fileList.item(x).checkState() == Qt.Checked:
                files.append(self.ui.fileList.item(x).text().encode('ascii'))
        self.config.files = files
        self.Launch()


    def closeEvent(self, event):
        """Overrides default closeEvent
        """
        self.player.Shutdown()
        pass


    def Launch(self):
        """Begin work
        """
        try:
            self.player.Open(self.config.files, self.config.repeat)
            #self.player.Play()
            self.timer.start()
        except IndexError:
            self.fail(Messages.title_fail, Messages.no_file)


    def keyPressEvent(self, event):
        """Overrides default keypress
        """
        key = event.key()
        if key in self.config.keys['exit']:
            self.close()
        elif key in self.config.keys['fullscreen']:
            self.toggleFullScreen()
        elif key in self.config.keys['speedUp']:
            self.player.SpeedChange(0.5)
        elif key in self.config.keys['speedDown']:
            self.player.SpeedChange(-0.5)


    def toggleFullScreen(self):
        if not self.fullscreen:
            self.ui.vframe.showFullScreen()
            self.fullscreen = True
        else:
            self.ui.vframe.showNormal()
            self.fullscreen = False


    def openFolder(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        dialog.exec_()


def main():
    """Program enter
    """

    # Ctrl+C in linux terminal
    if sys.platform == "linux2":
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

