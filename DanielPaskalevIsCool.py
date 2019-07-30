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
Depending on size of the list it will take 10-15 seconds.

The program is a (non-editable) spreadsheet with a line to enter what
you would like to filter for.

There are 3 buttons:

Filter:  Filters the pending list with what is in the entry line.
Copy:    Copies all of the current accessions (no duplicates) for pasting into excel.
Refresh: To be used if you updated the reference pending list.txt. It re-parses the file.
"""


import os, sys, datetime, re
from PySide2.QtWidgets import (QApplication, QWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, qApp,
                               QAbstractItemView, QLabel, QPushButton,
                               QHBoxLayout, QLineEdit, QErrorMessage)
from PySide2.QtGui import QIcon, QPalette, QColor, QFont
from PySide2.QtCore import Slot, Qt

"""
def merge_accessions(tests):
    " DEPRECATED
    order_list is 2D array where
    order_list[i][0] = worklist
    order_list[i][1] = accession
    order_list[i][2] = tests
    order_list[i][3] = doc
    order_list[i][4] = name
    "
    # merge duplicate worklists for same accessions
    # DEPRECATED BECAUSE LISTS PASS BY REFERENCE
    temp = tests[:][:]
    for i in temp:
        for j in temp:
            if j[1] == i[1] and j[2] != i[2]:
                i[2] += ', ' + j[2]
                i[0] += ', ' + j[0]
                tempx = list(temp)
                tempx.remove(j)  # shoot me in the face
                temp = tuple(tempx)
    return temp
 """

def filter_duplicates(accessions):
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
    order_list[i][worklist, accession, tests, doc, name]
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
                name = line[28:47]
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


def main():
    test = get_filename()  # To create error_dialog outside of App.
    class App(QWidget):
        # resized = pyqtSignal()
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
            # self.resized.connect(self.resizedSlot)
            self.initUI()

        def initUI(self):
            # self.is_button_clicked = False
            self.setWindowTitle(self.title)
            # self.setGeometry(self.left, self.top, self.width, self.height)
            self.setWindowState(Qt.WindowMaximized)
            self.createLabel()
            self.createTable()
            self.createButton()
            self.createCopyButton()
            self.createRefreshButton()
            # self.createMergeButton()
            self.createLe()
            # Create vertical box layout and horizontal box layout,
            # add label, button, to hbox,
            # add hbox to vbox,
            # and add table to vbox.
            self.layout = QVBoxLayout()
            self.hbox = QHBoxLayout()
            self.hbox.addWidget(self.label)
            self.hbox.addWidget(self.le)
            self.hbox.addWidget(self.button)
            self.hbox.addWidget(self.copyButton)
            self.hbox.addWidget(self.refreshButton)
            # self.hbox.addWidget(self.mergeButton)
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
            self.le.returnPressed.connect(self.filter_accessions)

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
            self.refreshButton = QPushButton('Refresh', self)
            self.refreshButton.setToolTip('Refresh table with new pending list.')
            self.refreshButton.setMaximumWidth(60)
            self.refreshButton.clicked.connect(self.on_refresh)

        # def createMergeButton(self):
        #     self.mergeButton = QPushButton('Merge', self)
        #     self.mergeButton.setToolTip('Merges tests for duplicate accessions')
        #     self.mergeButton.setMaximumWidth(60)
        #     self.mergeButton.clicked.connect(self.on_merge)

        def createLabel(self):
            # label with general information.
            self.label = QLabel()
            self.label.setTextFormat(Qt.PlainText)
            text = ("Double click entry to copy | Order count: " +
                    str(len(self.current_tests)))
            self.label.setText(text)
            self.label.setAlignment(Qt.AlignCenter)

        def createTable(self):
            # Create table with accession info.
            self.tableWidget = QTableWidget()
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(self.current_tests))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["Accession",
                                                        "Name",
                                                        "DOC",
                                                        "Worklist(s)",
                                                        "Pending Tests"])
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            self.tableWidget.horizontalHeaderItem(4).setTextAlignment(Qt.AlignLeft)
            for i in range(len(self.current_tests)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(self.current_tests[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(self.current_tests[i][4]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(self.current_tests[i][3]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(self.current_tests[i][0]))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(self.current_tests[i][2]))
            self.tableWidget.resizeColumnsToContents()  # resize columns only once.
            self.tableWidget.resizeRowsToContents()  # widen height to fit tests
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setWordWrap(True)
            self.tableWidget.move(0, 0)
            # table selection change
            self.tableWidget.doubleClicked.connect(self.on_click)

        @Slot()
        def on_click(self):
            # Double click to put selected item into clipboard
            qApp.clipboard().setText(self.tableWidget.selectedItems()[0].text())

        @Slot()
        def on_refresh(self):
            # Refresh button clicked to re-create qtablewidget with new pending list.
            self.original_tests = process(get_filename())
            self.filter_accessions()

        @Slot()
        def on_copyButton_click(self):
            # Click to copy all accessions into clipboard
            self.cp = [i[1] for i in self.current_tests]
            qApp.clipboard().setText(self.search + ''.join(['\n' +
                                    a for a in filter_duplicates(self.cp)]))

        # @Slot()
        # def on_merge(self):
        #     # Merge current accessions to remove situation where multiple tests for
        #     # the same patient are on multiple worklists.
        #     # pass
        #     for i in self.current_tests:
        #         for j in self.current_tests:
        #             if j[1] == i[1] and j[2] != i[2]:
        #                 i[2] += ', ' + j[2]
        #                 i[0] += ', ' + j[0]
        #                 self.current_tests.pop(j)  # shoot me in the face

        @Slot()
        def filter_accessions(self):
            # Button / Return pressed to filter the orders.
            self.search = self.le.text().upper()
            self.current_tests = [a for a in self.original_tests if
                                  self.search in a[0] or
                                  self.search in a[1] or
                                  self.search in a[2] or
                                  self.search in a[3] or
                                  self.search in a[4]]
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(self.current_tests))
            self.tableWidget.setColumnCount(5)
            for i in range(len(self.current_tests)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(self.current_tests[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(self.current_tests[i][4]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(self.current_tests[i][3]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(self.current_tests[i][0]))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(self.current_tests[i][2]))
            self.tableWidget.resizeRowsToContents()  # resize height to fit tests
            # self.tableWidget.resizeColumnsToContents()  # no need to resize column twice
            self.label.setText("Double click entry to copy | Order count: " +
                                str(len(self.current_tests)))

        # def resizeEvent(self, event):
        #     self.resized.emit()
        #     return super(App, self).resizeEvent(event)

        # def resizedSlot(self):
        #     self.tableWidget.resizeRowsToContents()

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


if __name__ == '__main__':
    main()