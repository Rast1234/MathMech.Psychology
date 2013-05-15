# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtCore import *
from PySide.QtGui  import *

from QTableWidgetDragRow import *
from delegators import TimeDelegate, SpeedDelegate

class RulesTableWidget( QTableWidgetDragRow ):
    """Table widget class which give metods to input / output
    rules in list format and validate input fields
    """

    def __init__(self, parent=None):
        """Initial rules table. Set 2 columns, headers and delegates
        """
        super(RulesTableWidget, self).__init__(parent)

        self.setColumnCount(2)
        self.setItemDelegateForColumn(0, TimeDelegate(self))
        self.setItemDelegateForColumn(1, SpeedDelegate(self))

        self.setHorizontalHeaderLabels((u"Время", u"Скорость"))
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)


    def addRule(self, time, speed):
        """Add row to rules table
        """
        row = self.rowCount()
        self.insertRow(row)

        timeItem  = QTableWidgetItem()
        speedItem = QTableWidgetItem()

        timeItem.setText(time)
        speedItem.setText(speed)

        self.setItem(row, 0, timeItem)
        self.setItem(row, 1, speedItem)

        ranges = self.selectedRanges()
        if len(ranges):
            self.setRangeSelected(ranges[0], False)

        # correct set selection
        ran = QTableWidgetSelectionRange(row, 0, row, 1)
        self.setRangeSelected(ran, True)


    def removeRule(self):
        """Remove selected row from rules table
        """
        ranges = self.selectedRanges()
        if not len(ranges):
            return

        removed_row = ranges[0].topRow()
        self.removeRow(removed_row)

        # correct set selection
        ran = QTableWidgetSelectionRange(removed_row, 0, removed_row, 1)
        self.setRangeSelected(ran, True)


    def fromRulesList(self, rules_list):
        """Generate rows from rule list
        rule in list it's tuple with time(int seconds) and speed(float)
        """
        self.clear()
        self.setHorizontalHeaderLabels((u"Время", u"Скорость"))

        for time, speed in rules_list:
            if time == 0:
                continue

            time  = "{0:02d}:{1:02d}".format(time / 60, time % 60)
            speed = "{0:0.02f}x".format(speed)

            self.addRule(time, speed)


    def toRulesList(self):
        """Generate rule list from rules in table rows
        rule in list it's tuple with time(int seconds) and speed(float)
        """
        rules = []
        for row_number in xrange( self.rowCount() ):
            time  = self.item(row_number, 0).text()
            speed = self.item(row_number, 1).text()
            time  = reduce(int.__add__, map(int, time.split(":")))
            speed = float(speed[:-1])

            if time == 0:
                continue

            rules.append((time, speed))

        return rules
    
