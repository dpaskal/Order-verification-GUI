#!usr/bin/python
 
"""
Daniel Paskalev
07/30/2019
dpaskalev@gmail.com

This program is used to *quickly* and *accurately* go through 
the reference pending list.

To get the pending list it must be a text file in 'My Documents'.
A SmarTerm macro can do this with its "Capture" functionality
and the associated macro file is included in github page as 'UserVT.stm'.

Once the text file containing the reference pending list exists, you may run this program.
It could take 15-30 seconds to initialize on slow machines.

The program is a (non-editable) spreadsheet with a line to enter what
you would like to filter for.

There are 4 buttons:

Filter:  Filters the pending list with what is typed into the entry line.
Copy:    Copies all of the current accessions (no duplicates) for pasting into excel.
Refresh: To be used if you updated the reference pending list.txt. It re-parses the file.
Merge:   Temporarily merge duplicate accessions who have other tests pending in other worklists.
"""

from copy import deepcopy
import os, sys, datetime, re
# import numpy as np
from PySide2.QtWidgets import (QApplication, QWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, qApp,
                               QAbstractItemView, QLabel, QPushButton,
                               QHBoxLayout, QLineEdit, QErrorMessage,
                               QFileDialog, QAction, QMenuBar)
from PySide2.QtGui import QIcon, QPalette, QColor, QFont
from PySide2.QtCore import Slot, Qt

"""
order_list is 2D array where
order_list[i][0] = worklist
order_list[i][1] = accession
order_list[i][2] = tests
order_list[i][3] = doc
order_list[i][4] = name
 """

def filter_dups(accessions):
    """Removes duplicate accessions from a list of accessions."""
    return list(dict.fromkeys(accessions))


def get_filename():
    """
    Uses system date to generate location of today's pending list.
    """
    month = datetime.datetime.now().strftime("%m")
    day = datetime.datetime.now().strftime("%d")
    # strip leading 0 in month or day
    month = month[1] if month[0] == "0" else month
    day = day[1] if day[0] == "0" else day
    # get pending list file location. Hard-coded to My Documents
    location = "".join(["C:\\Users\\" + os.getlogin() + "\\Documents\\"
                        "REFERENCE PENDING LIST ", month, "-", day, ".txt"])
    if not os.path.isfile(location):
        error_dialogue("Today's pending list not found in My Documents.")
    return location


def error_dialogue(message):
    """Create error window with the message given.
    Must be called outside of a Qt instance.
    """
    error = QApplication([])
    error_dialog = QErrorMessage()
    error_dialog.setWindowTitle("File not found")
    error_dialog.showMessage(message)
    sys.exit(error.exec_())


def process(filename):
    """
    This function parses the reference pending list.
    Argument is the location + text file we are parsing.
    Return 2D array of all accessions in the format:
    order_list[i][0] = worklist
    order_list[i][1] = accession
    order_list[i][2] = tests
    order_list[i][3] = doc
    order_list[i][4] = name
    """
    worklist, tests = "", ""
    order_list = []
    add_more_tests = False
    with open(filename, 'r') as f:
        for line in f:
            if "WORKLIST:" in line:
                worklist = line[9:].strip().split('/', 1)[0]
            if re.match(r'[A-Z][A-Z]\d\d\d\d\d\d', line[12:20]):
                # collect accession
                name = line[28:47].strip()
                doc = line[64:69]
                accession = line[12:21].strip()
                if accession[-1:] == '(':
                    accession = accession[:-1]
                # cleans a trailing ( in MC accessions that are *(H)
            if add_more_tests:
                # collects secondary lines of tests
                tests += " " + line.strip()
                if line.strip()[-1] != ",":
                    add_more_tests = False
                    order_list.append([worklist, accession, tests, doc, name])
                    # empty the variables in preparation for next accession.
                    accession, tests, doc, name = [""]*4
            if "Pending Tests: " in line:
                # collect first line of tests and raise flag if line ends w/ ","
                tests += line[27:].strip()
                if line.strip()[-1] == ",":
                    add_more_tests = True
                else:
                    order_list.append([worklist, accession, tests, doc, name])
                    # empty the variables in preparation for next accession.
                    accession, tests, doc, name = [""]*4
    return order_list


if __name__ == '__main__':
    test = get_filename()  # To create error_dialog outside of App.
    class App(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowIcon(QIcon('icon.ico'))
            QApplication.setFont(QFont("Helvetica", 9, QFont.Normal, italic=False))
            self.title = 'DanielPaskalev'
            self.left, self.top = 0, 0
            self.width, self.height = 900, 920
            self.current_tests = process(get_filename())
            self.original_tests = process(get_filename())
            self.search = ""
            self.initUI()

        def initUI(self):
            # self.is_button_clicked = False
            self.setWindowTitle(self.title)
            self.setWindowState(Qt.WindowMaximized)
            self.createLabel()
            self.createLe()
            self.createTable()
            self.createButton()
            self.createCopyButton()
            self.createRefreshButton()
            self.createMergeButton()
            self.createMenuBox()
            # Create vertical box layout and horizontal box layout,
            # add label, button, to hbox,
            # add hbox to vbox,
            # and add table to vbox.
            self.layout = QVBoxLayout()
            self.layout.setContentsMargins(0,5,0,0)
            # self.layout.setSpacing(0)
            self.hbox = QHBoxLayout()
            self.hbox.addWidget(self.menuBar)
            self.hbox.addWidget(self.label)
            self.hbox.addWidget(self.le)
            self.hbox.addWidget(self.button)
            self.hbox.addWidget(self.copyButton)
            self.hbox.addWidget(self.refreshButton)
            self.hbox.addWidget(self.mergeButton)
            self.layout.addLayout(self.hbox)
            self.layout.addWidget(self.tableWidget)
            self.setLayout(self.layout)
            # Show widget
            self.show()

        def createLe(self):
            # Create user input box for filter.
            self.le = QLineEdit()
            self.le.setObjectName("Filter")
            self.le.setPlaceholderText("Filter")
            self.le.setToolTip('Enter text to filter the pending list')
            self.le.setMaximumWidth(200)
            self.le.returnPressed.connect(self.filter_accessions)  # Enter pressed

        def createButton(self):
            # Create "Filter Accessions" button.
            self.button = QPushButton('Filter', self)
            self.button.setToolTip('Filters the accessions by text matches.')
            self.button.setMaximumWidth(60)
            self.button.clicked.connect(self.filter_accessions)

        def createCopyButton(self):
            # Create Copy accessions button.
            self.copyButton = QPushButton('Copy', self)
            self.copyButton.setToolTip('Copy all unique accessions to clipboard.')
            self.copyButton.setMaximumWidth(60)
            self.copyButton.clicked.connect(self.on_copyButton_click)

        def createRefreshButton(self):
            # Re-acquire the ref pending list.
            self.refreshButton = QPushButton('Refresh', self)
            self.refreshButton.setToolTip('Refresh table with new pending list.')
            self.refreshButton.setMaximumWidth(60)
            self.refreshButton.clicked.connect(self.on_refresh)

        def createMergeButton(self):
            # Merge the currently showing accessions.
            self.mergeButton = QPushButton('Merge', self)
            self.mergeButton.setToolTip('Merges tests for duplicate accessions')
            self.mergeButton.setMaximumWidth(60)
            self.mergeButton.clicked.connect(self.on_merge)

        def createLabel(self):
            # label with general information.
            self.label = QLabel()
            self.label.setTextFormat(Qt.PlainText)
            text = ("Double click entry to copy | Order count: " +
                    str(len(self.current_tests)))
            self.label.setText(text)
            self.label.setAlignment(Qt.AlignCenter)

        def createTable(self):
            # Initialize table with proper attributes. Then populateTable.
            self.tableWidget = QTableWidget()
            self.tableWidget.clicked.connect(self.on_click)  # If cell is clicked, copy.
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
            self.tableWidget.setWordWrap(True)
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["Accession",
                                                        "Name",
                                                        "DOC",
                                                        "Worklist(s)",
                                                        "Pending Tests"])
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            self.tableWidget.horizontalHeaderItem(4).setTextAlignment(Qt.AlignLeft)
            self.populateTable(self.current_tests)      # Populate table with data
            self.tableWidget.resizeColumnsToContents()  # Resize columns only once.
            self.tableWidget.resizeRowsToContents()     # Resize height to fit tests.

        def populateTable(self, orderList):
            # Re-populate table with argument 'orderList'
            self.tableWidget.setSortingEnabled(False)
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(orderList))
            for i in range(len(orderList)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(orderList[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(orderList[i][4]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(orderList[i][3]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(orderList[i][0]))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(orderList[i][2]))
            self.tableWidget.resizeRowsToContents()  # Resize height to fit tests
            # self.tableWidget.resizeColumnsToContents()
            self.label.setText("Double click entry to copy | Order count: " +
                                str(len(orderList)))
            self.tableWidget.setSortingEnabled(True)

        def createMenuBox(self):
            # Menu bar at the top of the window.
            self.menuBar = QMenuBar()
            self.fileMenu = self.menuBar.addMenu('File')
            self.open_action = QAction('Open', self)
            self.exit_action = QAction('Exit', self)
            self.open_action.triggered.connect(self.open)
            self.exit_action.triggered.connect(app.quit())  # just quit
            self.fileMenu.addAction(self.open_action)
            self.fileMenu.addAction(self.exit_action)

        @Slot()
        def open(self):
            fname = QFileDialog.getOpenFileName(self, 'Open File', os.path.expanduser('~/Documents'),
                                                'Text Files (*.txt)')
            if fname[0]:
                self.original_tests = process(fname[0])
                self.filter_accessions()

        @Slot()
        def on_click(self):
            # Double click to put selected item into clipboard
            qApp.clipboard().setText(self.tableWidget.selectedItems()[0].text())

        @Slot()
        def on_refresh(self):
            # Refresh button clicked to re-create table with new pending list.
            self.original_tests = process(get_filename())
            self.filter_accessions()

        @Slot()
        def on_copyButton_click(self):
            # Click to copy all accessions into clipboard
            self.cp = [i[1] for i in self.current_tests]
            qApp.clipboard().setText(self.search + ''.join(['\n' +
                                     a for a in filter_dups(self.cp)]))

        @Slot()
        def on_merge(self):
            # Merge current accessions to remove situation where multiple tests for
            # the same patient are on multiple worklists.
            self.tableWidget.setSortingEnabled(False)
            # Aglorithm to merge duplicate accessions.
            temp_tests = deepcopy(self.current_tests)  # DEEEEPcopy
            temp_tests.sort(key=lambda x: x[1])  # Sort by accession number
            result = []
            i = 0
            # Compare the current accession to the next to see if duplicate.
            length = len(temp_tests) - 1
            while i < length:
                if temp_tests[i][1] == temp_tests[i+1][1]:
                    # If duplicates, add worklist and tests to first accesion.
                    temp_tests[i][0] += ', ' + temp_tests[i+1][0]
                    temp_tests[i][2] += ' ||| ' + temp_tests[i+1][2]
                    del temp_tests[i+1]  # Delete second accession.
                    length -= 1
                else:  # If current and next accession numbers don't match
                    result.append(temp_tests[i])
                    i += 1
            result.append(temp_tests[-1])  # add the last accession that we missed.

            # Re-create table with 'result'
            self.populateTable(result)
            self.mergeButton.setDown(True)  # Click down merge button

        @Slot()
        def filter_accessions(self):
            # Button / Return pressed to filter the orders.
            self.tableWidget.setSortingEnabled(False)
            self.mergeButton.setDown(False)  # Unclick merge button
            self.search = self.le.text().upper()
            self.current_tests = [a for a in self.original_tests if
                                  self.search in a[0] or
                                  self.search in a[1] or
                                  self.search in a[2] or
                                  self.search in a[3] or
                                  self.search in a[4]]
            self.populateTable(self.current_tests)


    app = QApplication(sys.argv)
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")
    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    ex = App()
    sys.exit(app.exec_())
