#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import os
import signal
from os.path import isfile, join
from pprint import pprint

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

        # update layout during work
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, SIGNAL("timeout()"), self.refresh)

        self.config = Config()
        self.beautifyPlyer()

        self.player = PlayerControl(self.ui.vframe, self.config.vlc_args)
        self.fullscreen = False
        self.__hideOnFullscreen = [
            self.ui.fileGroup,
            self.ui.settingsGroup,
            self.ui.menubar,
            self.ui.speedIndicator
        ]

        self.finalUI()

    def finalUI(self):
        """Set up custom parts of UI
        """

        #initialize cool widget and push it on top of layout
        self.ui.rulesTable = RulesTableWidget(self.ui.settingsGroup)
        self.ui.verticalLayout_2.insertWidget(1, self.ui.rulesTable)

        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

        self.ui.fileList.itemClicked.connect(self.on_item_click)

        add_rule_callback = lambda: self.ui.rulesTable.addRule("00:00:00", "1.0x")
        remove_rule_callback = lambda: self.ui.rulesTable.removeRule()
        self.ui.addRuleButton.clicked.connect(add_rule_callback)
        self.ui.removeRuleButton.clicked.connect(remove_rule_callback)

        self.ui.action_open_folder.triggered.connect(self.openFolder)
        self.ui.action_open.triggered.connect(self.openExe)
        self.ui.action_save.triggered.connect(self.save)
        self.ui.action_load.triggered.connect(self.load)
        self.ui.action_show_help.triggered.connect(self.showHelp)
        self.ui.action_show_info.triggered.connect(self.showInfo)
        self.ui.action_reset.triggered.connect(self.reset)

        #initial set up from hard-coded defaults
        self.updateUIFromConfig()

    def on_item_click(self, item):
        """File click handler"""
        state = item.checkState()
        if state == Qt.Checked:
            state = Qt.Unchecked
        else:
            state = Qt.Checked
        item.setCheckState(state)

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
        self.ui.fileList.clear()
        for x in self.listDirFiles():
            item = QListWidgetItem(self.ui.fileList)
            item.setText(x)
            item.setFlags(item.flags() or Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # play all stuff by default

    def fail(self, title, message):
        """Display a warning MessageBox
        """
        reply = QMessageBox.critical(self, title, message)

    def listDirFiles(self):
        """Get video files from directory
        """
        listing = [u'(пусто)']
        try:
            listing = os.listdir(self.config.folder)
        except OSError:  # invalid dir
            self.fail(Messages.title_fail, Messages.no_dir)
            self.config.folder = self.config.default_folder
        #print "LISTING =", listing
        files = [x for x in listing if isfile(join(self.config.folder, x))]
        result = []
        if not self.config.extensions:
            result = files
        else:
            for x in files:
                if x.split('.')[-1].lower() in self.config.extensions:
                    result.append(x)
        return result

    def listSelectedFiles(self):
        """Get selected items from list
        """
        files = []
        for x in xrange(self.ui.fileList.count()):
            if self.ui.fileList.item(x).checkState() == Qt.Checked:
                files.append(self.ui.fileList.item(x).text())
        return files

    def setSelectedFiles(self, selectedFiles):
        """Try set checked/unchecked files
        in panel according to supplied list.
        Ignore missing, uncheck extra files.
        """
        for x in xrange(self.ui.fileList.count()):
            item = self.ui.fileList.item(x)
            if item.text() in selectedFiles:
                item.setCheckState(True)
            else:
                item.setCheckState(False)

    def refresh(self):
        """Update active UI elements: speed
        """
        if not self.player.IsPlaying():
            self.timer.stop()
            self.fail("timer", "timer stopped from refresh()")
        self.ui.speedIndicator.display(self.player.GetSpeed())

    def on_click(self):
        """Start Button click event handler
        """
        self.grabDataToConfig()
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
            files = []
            for x in self.config.files:
                files.append(join(self.config.folder, x))
            self.player.Open(files)
            # self.player.Play()
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
        elif key in self.config.keys['pause']:
            if self.isFullScreen():
                self.showNormal()
                if self.player.IsPlaying():
                    self.player.Pause()
            else:
                self.showFullScreen()
                self.player.Play()
        elif key in self.config.keys['speedUp']:
            self.player.SpeedChange(0.5)
        elif key in self.config.keys['speedDown']:
            self.player.SpeedChange(-0.5)

    def toggleFullScreen(self):
        """Toggles full screen view
        """
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    def showFullScreen(self):
        """Overrides default full screen:
        hides extra panels and menu
        """
        for x in self.__hideOnFullscreen:
                x.hide()
        super(ControlMainWindow, self).showFullScreen()

        self.ui.centralwidget.setFocus()

    def showNormal(self, *args, **kwargs):
        """Overrides default un-fullscreen:
        shows panels and menu hidden on showFullScreen
        """
        super(ControlMainWindow, self).showNormal()
        for x in self.__hideOnFullscreen:
            x.show()

    def openFolder(self):
        choice = QFileDialog.getExistingDirectory(
            caption=Messages.folder_dialog,
            dir=self.config.folder
        )
        if choice != '':  # dialog cancelled
            self.config.folder = choice
            self.ui.folderLabel.setText(choice)
            self.populateFiles()

    def openExe(self):
        choice = QFileDialog.getOpenFileName(
            caption=Messages.file_dialog,
            options=QFileDialog.HideNameFilterDetails,  # hide "(*.exe)" part
            filter=u"Программы (*.exe)",
        )
        # PySide returns tuple (filename, filter) while QT returns only filename
        exe = choice[0]
        if exe != '':
            self.config.exe = choice[0]
            self.ui.exeLabel.setText(choice[0])

    def save(self):
        '''Save config'''
        choice = QFileDialog.getSaveFileName(
            caption=Messages.save_dialog,
            options=QFileDialog.HideNameFilterDetails,  # hide "(*.exe)" part
            filter=u"Файлы настройки (*.testcfg)",
        )
        # PySide returns tuple (filename, filter) while QT returns only filename
        conf_file = choice[0]
        if conf_file != '':
            self.grabDataToConfig()
            self.config.save(conf_file)

    def load(self):
        '''Load config'''
        choice = QFileDialog.getOpenFileName(
            caption=Messages.load_dialog,
            options=QFileDialog.HideNameFilterDetails,  # hide "(*.exe)" part
            filter=u"Файлы настройки (*.testcfg)",
        )
        # PySide returns tuple (filename, filter) while QT returns only filename
        conf_file = choice[0]
        if conf_file != '':
            self.config.load(conf_file)
            self.updateUIFromConfig()

    def showHelp(self):
        '''Open help doc'''
        os.startfile(self.config.help)

    def showInfo(self):
        '''Show authors'''
        QMessageBox.about(self, Messages.about, Messages.authors)

    def reset(self):
        '''Load empty config'''
        pass

    def grabDataToConfig(self):
        """Collect all input fields into config
        Is this needed?
        """
        ui = self.ui
        cfg = self.config
        cfg.folder = ui.folderLabel.text()
        cfg.exe = ui.exeLabel.text()
        cfg.rules = ui.rulesTable.toRulesList() #this is called only here
        cfg.files = self.listSelectedFiles()

        raw_time = ui.timeInput.time()

        cfg.totaltime = raw_time.hour() * 60 * 60 + \
                                raw_time.minute() * 60 + \
                                raw_time.second()

        status = ui.automaticRunCheckBox.isChecked()
        cfg.auto_run = status
        cfg.files = self.listSelectedFiles()
        cfg.reverseUpdate()

    def updateUIFromConfig(self):
        """Update file list, labels etc. from config
        Functions changing config should always call
        this routine in order to sync ui<->config
        """
        ui = self.ui
        cfg = self.config

        # Setings group
        ui.rulesTable.fromRulesList(cfg.rules)

        raw_time = cfg.totaltime
        hours = raw_time / 60 / 60
        minutes = raw_time / 60
        seconds = raw_time % 60
        ui.timeInput.setTime(QTime(hours, minutes, seconds))
        ui.automaticRunCheckBox.setChecked(cfg.auto_run)
        ui.exeLabel.setText(cfg.exe)

        # File group
        ui.folderLabel.setText(cfg.folder)
        self.setSelectedFiles(cfg.files)
        self.populateFiles()
        cfg.reverseUpdate()


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
