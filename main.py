#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import os
import signal
from os.path import isfile, join

import PySide
from PySide.QtCore import *
from PySide.QtGui import *

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
        self.taskTimer = QTimer(self)
        self.taskTimer.setInterval(1000)
        self.connect(self.taskTimer, SIGNAL("timeout()"), self.refresh)
        self.stage = 0

        self.config = Config()
        self.beautifyPlyer()

        self.player = PlayerControl(self.ui.vframe, self.config.vlc_args)
        self.fullscreen = False
        self.__hideOnFullscreen = [
            self.ui.fileGroup,
            self.ui.settingsGroup,
            self.ui.menubar,
            self.ui.frame,
        ]

        self.keys = {
            'fullscreen': (QtCore.Qt.Key_F, QtCore.Qt.Key_F11),
            'exit': (QtCore.Qt.Key_Escape, ),
            'pause': (QtCore.Qt.Key_Space, ),
            'speedUp': (QtCore.Qt.Key_Equal, ),
            'speedDown': (QtCore.Qt.Key_Minus, ),
        }

        self.finalUI()

    def finalUI(self):
        """Set up custom parts of UI
        """

        #initialize cool widget and push it on top of layout
        self.ui.rulesTable = RulesTableWidget(self.ui.settingsGroup)
        self.ui.verticalLayout_2.insertWidget(1, self.ui.rulesTable)

        self.ui.exeButton.clicked.connect(self.on_exe)
        self.ui.stopButton.clicked.connect(self.on_stop_click)
        self.ui.launchButton.clicked.connect(self.on_click)
        self.ui.launchButton.setFocus()

        self.ui.fileList.itemClicked.connect(self.on_item_click)
        self.ui.automaticRunCheckBox.clicked.connect(self.on_auto_click)

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

    def on_auto_click(self):
        status = self.ui.automaticRunCheckBox.isChecked()
        self.config.auto_run = status

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
        if self.config.folder != '':
            try:
                listing = os.listdir(self.config.folder)
            except OSError:  # invalid dir
                self.fail(Messages.title_fail, Messages.no_dir)
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
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def refresh(self):
        """Monster function to manage stages and update UI elements
        """
        ui = self.ui
        ui.speedIndicator.display(self.player.GetSpeed())
        ela = self._time_to_seconds(ui.elapsedTime.time())
        rem = self._time_to_seconds(ui.remainTime.time())
        if rem == 0:
            self.taskTimer.stop()
            self.player.Stop()
            self.guiStop()
            self.showNormal()
        else:
            ela += 1
            rem -= 1
            ui.elapsedTime.setTime(self._seconds_to_time(ela))
            ui.remainTime.setTime(self._seconds_to_time(rem))
        self.stage -= 1
        if self.stage == 0:
            rule = ui.currentRule.value()  # actually, this is next rule
            if rule < len(self.config.rules):
                self.player.SetSpeed(self.config.rules[rule][1])
                self.stage = self.config.rules[rule][0]
                ui.currentRule.setValue(rule + 1)
                if self.config.auto_run:
                    #self.togglePause(True) - won't work from another thread
                    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.KeyboardModifiers())
                    QCoreApplication.postEvent(self, evt)
                    self.on_exe()

            #otherwise, total countdown is over, and everything is stopped already.
        ui.currentStage.setValue(self.stage)

    def on_click(self):
        """Start Button click event handler
        """
        self.grabDataToConfig()
        files = []
        for x in self.config.files:
            files.append(join(self.config.folder, x))
        if not files:
            self.fail(Messages.title_fail, Messages.no_file)
            return
        if not self.config.rules:
            self.fail(Messages.title_fail, Messages.no_rules)
            return
        sum = 0
        for x in self.config.rules:
            sum += x[0]
        raw = self.ui.timeInput.time()
        total = self._time_to_seconds(raw)
        th = raw.hour()
        tm = raw.minute()
        ts = raw.second()
        sh = sum / 3600
        sm = sum / 60 % 60
        ss = sum % 60
        if sum != total:
            details = u'''
Заданное время: {0:d}ч : {1:d}м : {2:d}с
Cуммарное время этапов: {3:d}ч : {4:d}м : {5:d}с'''.format(th,tm,ts, sh,sm,ss)
            self.fail(Messages.title_fail, Messages.invalid_time + details)
            return


        self.player.Open(files)  # player will start playing automatically
        # self.player.Play()
        self.player.SetSpeed(self.config.rules[0][1])
        self.guiPlay()
        self.showFullScreen()
        self.stage = self.config.rules[0][0]
        self.ui.currentStage.setValue(self.stage)
        self.taskTimer.start()

    def on_stop_click(self):
        """Stop button click event handler
        """
        self.player.Stop()
        self.stage = 0
        self.ui.currentStage.setValue(self.stage)
        self.guiStop()

    def on_exe(self):
        """Open external program
        """
        try:
            os.startfile(self.config.exe)  # it works under Windows
        except WindowsError:
            self.fail(Messages.title_fail, Messages.exe_fail + self.config.exe)

    def closeEvent(self, event):
        """Overrides default closeEvent
        """
        self.player.Shutdown()

    def keyPressEvent(self, event):
        """Overrides default keypress
        """
        key = event.key()
        if key in self.keys['exit']:
            self.close()
        elif key in self.keys['fullscreen']:
            if self.player.IsPlaying():
                self.toggleFullScreen()
        elif key in self.keys['pause']:
            self.togglePause()
        elif key in self.keys['speedUp']:
            if self.player.IsPlaying():
                self.player.SpeedChange(0.1)
                self.ui.speedIndicator.display(self.player.GetSpeed())
        elif key in self.keys['speedDown']:
            if self.player.IsPlaying():
                self.player.SpeedChange(-0.1)
                self.ui.speedIndicator.display(self.player.GetSpeed())

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
            filter=u"Файлы настройки (*.{})".format(self.config.ext),
        )
        # PySide returns tuple (filename, filter) while QT returns only filename
        conf_file = choice[0]
        if conf_file != '':
            if conf_file.split('.')[-1] != self.config.ext:  # filename w/o extension
                if conf_file[-1] == '.':
                    conf_file += self.config.ext
                else:
                    conf_file += '.' + self.config.ext
            self.grabDataToConfig()
            try:
                self.config.save(conf_file)
            except:
                self.fail(Messages.title_fail, Messages.save_fail)

    def load(self):
        '''Load config'''
        choice = QFileDialog.getOpenFileName(
            caption=Messages.load_dialog,
            filter=u"Файлы настройки (*.{})".format(self.config.ext),
        )
        # PySide returns tuple (filename, filter) while QT returns only filename
        conf_file = choice[0]
        if conf_file != '':
            try:
                self.config.load(conf_file)
                self.updateUIFromConfig()
            except:
                self.fail(Messages.title_fail, Messages.load_fail)

    def showHelp(self):
        '''Open help doc'''
        try:
            os.startfile(self.config.help)  # it works under Windows
        except WindowsError:
            self.fail(Messages.title_fail, Messages.help_fail + self.config.help)

    def showInfo(self):
        '''Show authors'''
        versions = u"""

Используемые библиотеки:

    * Python {}
    * Qt {}
    * PySide {}
    * libvlc {}
Собрано для Windows с помощью cxFreeze
""".format(sys.version, QtCore.qVersion(), PySide.__version__, self.player.version)
        QMessageBox.about(self, Messages.about, Messages.authors + versions)

    def reset(self):
        '''Load empty config'''
        self.config.reset()
        self.updateUIFromConfig()

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

        cfg.totaltime = self._time_to_seconds(ui.timeInput.time())

        status = ui.automaticRunCheckBox.isChecked()
        cfg.auto_run = status
        cfg.files = self.listSelectedFiles()
        cfg.reverseUpdate()

    def _time_to_seconds(self, raw_time):
        return raw_time.hour() * 60 * 60 + \
                        raw_time.minute() * 60 + \
                        raw_time.second()

    def _seconds_to_time(selfself, sec):
        h = sec / 3600
        m = sec / 60 % 60
        s = sec % 60
        return QTime(h, m, s)

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

    def guiPlay(self):
        """Initialize playback mode
        """
        ui = self.ui
        ui.stopButton.setEnabled(True)
        ui.launchButton.setEnabled(False)
        ui.remainTime.setTime(ui.timeInput.time())
        ui.elapsedTime.setTime(QTime(0, 0, 0))
        ui.currentRule.setValue(1)  # will always start from first rule

    def guiStop(self):
        """Initialize default (stopped) mode
        """
        ui = self.ui
        ui.stopButton.setEnabled(False)
        ui.launchButton.setEnabled(True)
        ui.remainTime.setTime(ui.timeInput.time())
        ui.elapsedTime.setTime(QTime(0, 0, 0))
        ui.currentRule.setValue(1)  # will always start from first rule

    def togglePause(self, pause=False):
        if self.player.IsPlaying() or pause:
            self.player.Pause()
            self.taskTimer.stop()
            self.showNormal()
        else:
            self.showFullScreen()
            self.player.Play()
            self.taskTimer.start()

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
