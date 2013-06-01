# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtCore import *
from PySide.QtGui import *
from PlayerControl import minSpeed, maxSpeed


class TimeDelegate(QItemDelegate):
    """Time field delegate in rules table
    """

    __timeFormat = "HH:mm:ss"

    def createEditor(self, parent, option, index):
        editor = QTimeEdit(parent)
        editor.setDisplayFormat(self.__timeFormat)
        editor.setSelectedSection(QDateTimeEdit.SecondSection)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setTime(QTime.fromString(value, self.__timeFormat))

    def setModelData(self, editor, model, index):
        data = editor.time().toString(self.__timeFormat)
        model.setData(index, data, Qt.EditRole)


class SpeedDelegate(QItemDelegate):
    """Speed field delegate in rules table
    """

    __suffix = "x"
    __displayFormat = u"{0}" + __suffix


    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setSingleStep(0.1)
        editor.setMaximum(maxSpeed)
        editor.setMinimum(minSpeed)
        editor.setDecimals(1)
        editor.setSuffix(self.__suffix)
        editor.setValue(1.0)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        value = value[:-1]
        editor.setValue(float(value))

    def setModelData(self, editor, model, index):
        data = self.__displayFormat.format(editor.value())
        model.setData(index, data, Qt.EditRole)
