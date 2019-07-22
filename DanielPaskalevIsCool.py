#!usr/bin/python3

import os, sys, datetime, re
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QAbstractItemView, QLabel, QPushButton,
                             QHBoxLayout, QLineEdit, qApp, QErrorMessage)
from PyQt5.QtGui import QIcon, QKeySequence, QPalette, QColor, QFont
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal
from PyQt5.QtWidgets import QMenuBar


def merge_accessions(tests):
    """" DEPRECATED
    list_of_tests is 2D array where
    list_of_tests[i][0] = worklist
    list_of_tests[i][1] = accession
    list_of_tests[i][2] = tests
    list_of_tests[i][3] = doc
    list_of_tests[i][4] = name
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
    if not os.path.isfile(location):
        # sys.exit("Current pending list missing")
        error_dialogue("Today's pending list not found in My Documents.")
    return location


def error_dialogue(message):
    """Create error window with the message given"""
    error = QApplication([])
    error_dialog = QErrorMessage()
    error_dialog.setWindowTitle("File not found")
    error_dialog.showMessage(message)
    sys.exit(error.exec_())


def print_tests(list_of_tests):
    """Print accessions in worklists as filtered by the 'search' key."""
    class App(QWidget):
        # resized = pyqtSignal()
        def __init__(self):
            super().__init__()
            self.setWindowIcon(QIcon('icon.ico'))
            QApplication.setFont(QFont("Helvetica", 9, QFont.Normal, italic=False))
            self.title = 'DanielPaskalev'
            self.left = 0
            self.top = 0
            self.width = 900
            self.height = 920
            self.current_tests = list_of_tests
            self.search = ""
            # self.resized.connect(self.resizedSlot)
            self.initUI()

        def initUI(self):
            # self.is_button_clicked = False
            self.setWindowTitle(self.title)
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.mainMenu = QMenuBar()
            self.mainMenu.addMenu('File')
            # self.setMenuBar(self.mainMenu)
            self.createLabel()
            self.createTable()
            self.createButton()
            self.createCopyButton()
            self.createLe()
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

        def createLe(self):
            # Create user input box for filter.
            self.le = QLineEdit()
            self.le.setObjectName("Filter")
            self.le.setPlaceholderText("Filter")
            self.le.setMaximumWidth(200)
            self.le.returnPressed.connect(self.filter_accessions)

        def createButton(self):
            # Create "Filter Accessions" button.
            self.button = QPushButton('Filter', self)
            self.button.setToolTip('Filters the accessions by any matches.')
            self.button.setMaximumWidth(100)
            self.button.clicked.connect(self.filter_accessions)

        def createCopyButton(self):
            # Create Copy accessions button.
            self.copyButton = QPushButton('Copy accessions', self)
            self.copyButton.setToolTip('Copy all unique accessions to clipboard.')
            self.copyButton.setMaximumWidth(100)
            self.copyButton.clicked.connect(self.on_copyButton_click)

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
            self.tableWidget.setRowCount(len(list_of_tests))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["Accession",
                                                        "Name",
                                                        "DOC",
                                                        "Worklist(s)",
                                                        "Pending Tests"])
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            self.tableWidget.horizontalHeaderItem(4).setTextAlignment(Qt.AlignLeft)
            for i in range(len(list_of_tests)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(list_of_tests[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(list_of_tests[i][4]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(list_of_tests[i][3]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(list_of_tests[i][0]))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(list_of_tests[i][2]))
            self.tableWidget.resizeColumnsToContents()  # resize columns only once.
            self.tableWidget.resizeRowsToContents()  # widen height to fit tests
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setWordWrap(True)
            self.tableWidget.move(0, 0)
            # table selection change
            self.tableWidget.doubleClicked.connect(self.on_click)

        @pyqtSlot()
        def on_click(self):
            # double click to put selected item into clipboard
            qApp.clipboard().setText(self.tableWidget.selectedItems()[0].text())

        @pyqtSlot()
        def on_copyButton_click(self):
            # click to copy all accessions into clipboard
            self.cp = [i[1] for i in self.current_tests]
            qApp.clipboard().setText(self.search + ''.join(['\n' +
                                    a for a in filter_duplicates(self.cp)]))

        @pyqtSlot()
        def filter_accessions(self):
            # Button / Return pressed to filter the orders.
            self.search = self.le.text().upper()
            self.current_tests = [a for a in list_of_tests if
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


def process(filename):
    """
    Argument is the text file we are processing.
    Return 2D array of all accessions.
    list_of_tests[i][worklist, accession, tests, doc]
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
                    add_more_tests = 0
                    list_of_tests.append([worklist, accession, tests, doc, name])
                    # empty the variables in preparation for next accession.
                    accession, tests, doc, name = [""]*4
            if "Pending Tests: " in line:
                # collect first line of tests and raise flag if line ends w/ ,
                tests += line[27:].strip()
                if line.strip()[-1] == ",":
                    add_more_tests = 1
                else:
                    list_of_tests.append([worklist, accession, tests, doc, name])
                    # empty the variables in preparation for next accession.
                    accession, tests, doc, name = [""]*4
    return list_of_tests


def main():
    print_tests(process(get_filename()))


if __name__ == '__main__':
    main()