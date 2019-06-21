#!usr/bin/python3

import re
import datetime
import sys
import os
import pyperclip


def merge_accessions(tests):
    """" DEPRECATED
    list_of_tests is 2D array where
    list_of_tests[i][0] = worklist
    list_of_tests[i][1] = accession
    list_of_tests[i][2] = tests
    list_of_tests[i][3] = doc
    """
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


def filter_duplicates(accessions):
    """Removes duplicate accessions from a list of accessions."""
    return list(dict.fromkeys(accessions))


def get_filename():
    """Return string. Location of today's pending list."""
    month = datetime.datetime.now().strftime("%m")
    day = datetime.datetime.now().strftime("%d")
    # strip leading 0 in month or day
    if month[0] == "0":
        month = month[1]
    if day[0] == "0":
        day = day[1]
    location = "".join(["C:\\Users\\" + os.getlogin() + "\\Documents\\"
                        "REFERENCE PENDING LIST ", month, "-", day, ".txt"])
    # location = "C:\\Users\\desktop\\Documents\\test.txt"
    if not os.path.isfile(location):
        sys.exit("Current pending list missing")
    return location


def print_tests(list_of_tests):
    """Print accessions in worklists as filtered by the 'search' key."""
    output_array = []
    unfiltered_list = list_of_tests
    #list_of_tests = [a for a in list_of_tests if search in a[0]]  # not yet

    from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction,
                                 QTableWidget, QTableWidgetItem, QVBoxLayout,
                                 QAbstractItemView, QLabel, QPushButton,
                                 QHBoxLayout, QLineEdit)
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import pyqtSlot, Qt

    class App(QWidget):
        def __init__(self):
            super().__init__()
            self.title = 'DanielPaskalevIsCool'
            self.left = 0
            self.top = 0
            self.width = 800
            self.height = 920
            self.current_tests = list_of_tests
            self.search = "All"
            self.initUI()

        def initUI(self):
            self.is_button_clicked = False
            self.setWindowTitle(self.title)
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.createLabel()
            self.createTable()
            self.createButton()
            self.createCopyButton()
            self.le = QLineEdit()
            self.le.setObjectName("Filter")
            self.le.setPlaceholderText("Filter for worklists")
            self.le.setMaximumWidth(200)
            self.le.returnPressed.connect(self.on_button_click)
            # Create vertical box layout and horizontal box layout,
            # add label, button, to hbox,
            # add hbox to vbox,
            # and add table to vbox.
            self.layout = QVBoxLayout()
            self.hbox = QHBoxLayout()
            self.minivbox = QVBoxLayout()
            self.hbox.addWidget(self.label)
            self.hbox.addWidget(self.le)
            self.hbox.addWidget(self.button)
            self.hbox.addWidget(self.copyButton)
            self.layout.addLayout(self.hbox)
            self.layout.addWidget(self.tableWidget)
            self.setLayout(self.layout)
            # Show widget
            self.show()

        def createButton(self):
            # Create "Filter Accessions" button.
            self.button = QPushButton('Filter accessions', self)
            self.button.setToolTip('Filters the accessions by worklist.')
            self.button.setMaximumWidth(100)
            self.button.clicked.connect(self.on_button_click)

        def createCopyButton(self):
            # Create Copy accessions button.
            self.copyButton = QPushButton('Copy accessions', self)
            self.copyButton.setToolTip('Copy all unique accessions for excel.')
            self.copyButton.setMaximumWidth(100)
            self.copyButton.clicked.connect(self.on_copyButton_click)

        def createLabel(self):
            # label with general information.
            self.label = QLabel()
            self.label.setTextFormat(Qt.PlainText)
            if len(self.current_tests):
                text = ('Total order count: ' + str(len(self.current_tests)))
            else:
                text = ('No orders found.')
            text += "\nDouble clicking an entry will copy it to clipboard."
            self.label.setText(text)
            self.label.setAlignment(Qt.AlignCenter)

        def createTable(self):
            # Create table with accession info.
            self.tableWidget = QTableWidget()
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(list_of_tests))
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(["Accession",
                                                        "DOC",
                                                        "Worklist(s)",
                                                        "Pending Tests"])
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            self.tableWidget.horizontalHeaderItem(3).setTextAlignment(Qt.AlignLeft)
            for i in range(len(list_of_tests)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(list_of_tests[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(list_of_tests[i][3]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(list_of_tests[i][0]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(list_of_tests[i][2]))
            self.tableWidget.resizeRowsToContents()  # widen height to fit tests
            # self.tableWidget.resizeColumnsToContents()   # do NOT resize columns
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setWordWrap(True)
            self.tableWidget.move(0, 0)
            # table selection change
            self.tableWidget.doubleClicked.connect(self.on_click)

        @pyqtSlot()
        def on_click(self):
            # double click to put selected item into clipboard
            pyperclip.copy(self.tableWidget.selectedItems()[0].text())

        @pyqtSlot()
        def on_copyButton_click(self):
            # click to copy all accessions into clipboard
            self.cp = [i[1] for i in self.current_tests]
            pyperclip.copy(self.search + ''.join(['\n' +
                           a for a in filter_duplicates(self.cp)]))

        @pyqtSlot()
        def on_button_click(self):
            # Button / Return pressed to filter the orders by worklist.
            self.search = self.le.text().upper()
            self.current_tests = [a for a in list_of_tests if self.search in a[0]]
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(self.current_tests))
            self.tableWidget.setColumnCount(4)
            for i in range(len(self.current_tests)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(self.current_tests[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(self.current_tests[i][3]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(self.current_tests[i][0]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(self.current_tests[i][2]))
            self.tableWidget.resizeRowsToContents()  # resize height to fit tests
            # self.tableWidget.resizeColumnsToContents()   # no need to resize column
            self.label.setText("Order count: " + str(len(self.current_tests)) +
                               "\nDouble clicking an entry will copy it to clipboard.")
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


def process(filename):
    """
    Argument is the text file we are processing.
    Return 2D array of all accessions.
    List[i][worklist, accession, tests, doc]
    """
    worklist = ""
    list_of_tests = []
    tests = ""
    add_more_tests = 0
    with open(filename, 'r') as f:
        for line in f:
            if "WORKLIST:" in line:
                worklist = line[9:].strip().split('/', 1)[0]
            if re.match(r'[A-Z][A-Z]\d\d\d\d\d\d', line[12:20]):
                # collect accession
                doc = line[64:74]
                accession = line[12:21].strip()
                if accession[-1:] == '(': 
                    accession = accession[:-1]
                # cleans a trailing ( in MC accessions that are *(H)
            if add_more_tests:
                # collects secondary lines of tests
                tests += " " + line.strip()
                if line.strip()[-1] != ",":
                    add_more_tests = 0
                    list_of_tests.append([worklist, accession, tests, doc])
                    tests = ""
            if "Pending Tests: " in line:
                # collect first line of tests and raise flag if there
                # are more than one line of tests
                tests += line[27:].strip()
                if line.strip()[-1] == ",":
                    add_more_tests = 1
                else:
                    list_of_tests.append([worklist, accession, tests, doc])
                    tests = ""
    return list_of_tests


def main():
    list_of_tests = process(get_filename())
    print_tests(list_of_tests)


if __name__ == '__main__':
    main()
