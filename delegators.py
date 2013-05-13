# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtCore import *
from PySide.QtGui  import *

class TimeDelegate(QItemDelegate):
    """Time field delegate in rules table
    """

    def createEditor(self, parent, option, index):
        editor = QTimeEdit(parent)
        editor.setDisplayFormat("mm:ss")
        editor.setSelectedSection(QDateTimeEdit.SecondSection)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setTime(QTime.fromString(value, "mm:ss"))

    def setModelData(self, editor, model, index):
        data = editor.time().toString("mm:ss")
        model.setData(index, data, Qt.EditRole)


class SpeedDelegate(QItemDelegate):
    """Speed field delegate in rules table
    """

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setSingleStep(0.5)
        editor.setMaximum(10)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        value = value[:-1]
        editor.setValue(float(value))

    def setModelData(self, editor, model, index):
        data = u"{0}x".format(editor.value())
        model.setData(index, data, Qt.EditRole)

