# usr/bin/python3

import re
import datetime
import sys
import os
# from openpyxl import Workbook


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
    location = "C:\\Users\\desktop\\Documents\\test.txt"
    if not os.path.isfile(location):
        sys.exit("Current pending list missing")
    return location


def print_accessions(search, sort_flag, list_of_worklists):
    """Prints the list of accessions as filtered by the search variable"""
    output_array = []
    for i in list_of_worklists:
        if search in i[0]:
            if len(i) >= 2:
                for z in i:
                    output_array.append(z)

    if sort_flag:
        output_array = filter_duplicates(output_array)
    total_count = 0
    for g in output_array:
        print(g, end='\n')
        total_count += 1
    print("total_count:", total_count)


def print_tests(search, list_of_tests):
    """Print accessions in worklists as filtered by the 'search' key."""
    # import pandas
    output_array = []
    list_of_tests = [a for a in list_of_tests if search in a[0]]
    for i in list_of_tests:
        for j in list_of_tests:
            if j[1] == i[1] and j[2] != i[2]:
                continue  # remove if you want to merge duplicate accessions
                i[2] += ', ' + j[2]
                i[0] += ', ' + j[0]
                list_of_tests.remove(j)
        # print("{: <20} {: >10}  {}".format(*i))
        output_array.append([i[0], i[1]])

    import pyperclip
    # Puts accessions into clipboard. First value is the FILTER.
    # There are no duplicates to worry about.
    pyperclip.copy(search + ''.join(['\n' + a[1] for a in output_array]))
    if len(list_of_tests) == 0:
        print("No matches found for ", search)
    else:
        print("Total accession count:", len(list_of_tests))
    # no filtering duplicates should be done here as duplicates are merged

    from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction,
                                 QTableWidget, QTableWidgetItem, QVBoxLayout,
                                 QAbstractItemView, QLabel, QPushButton)
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
            self.initUI()

        def initUI(self):
            self.setWindowTitle(self.title)
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.createLabel()
            self.createTable(list_of_tests)
            self.createButton()
            # Add vertical box layout,
            # add widgets to box layout,
            # and add box layout to widget
            self.layout = QVBoxLayout()
            self.layout.addWidget(self.label)
            self.layout.addWidget(self.button, 0, Qt.AlignCenter)
            self.layout.addWidget(self.tableWidget)
            self.setLayout(self.layout)
            # Show widget
            self.show()

        def createButton(self):
            # Button to merge accessions.
            self.button = QPushButton('Merge accessions', self)
            self.button.setToolTip('Merges the accessions that have multiple'
                                   ' worklists in this filter.')
            self.button.setMaximumWidth(150)
            self.button.clicked.connect(self.on_button_click)

        def createLabel(self):
            # label with general information.
            self.label = QLabel()
            self.label.setTextFormat(Qt.PlainText)
            text = ("*" + search +
                    '*\nTotal order count: ' + str(len(list_of_tests)) +
                    "\nDouble clicking an entry will copy it to clipboard.")
            self.label.setText(text)
            self.label.setAlignment(Qt.AlignCenter)

        def createTable(self, list_of_tests):
            # Create table with accession info.
            self.tableWidget = QTableWidget()
            self.tableWidget.setRowCount(len(list_of_tests))
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(["Accession",
                                                        "DOC",
                                                        "Worklist(s)",
                                                        "Pending Tests"])
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            self.tableWidget.horizontalHeaderItem(3).setTextAlignment(Qt.AlignLeft)
            for i in range(len(list_of_tests)):
                self.tableWidget.clearContents()
                self.tableWidget.setItem(i, 0, QTableWidgetItem(self.list_of_tests[i][1]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(self.list_of_tests[i][3]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(self.list_of_tests[i][0]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(self.list_of_tests[i][2]))
                self.tableWidget.resizeRowsToContents()  # widen height to fit tests
            self.tableWidget.resizeColumnsToContents()   # resize columns once
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setWordWrap(True)  # Doesn't do anything what the fuck
            self.tableWidget.move(0, 0)
            # table selection change
            self.tableWidget.doubleClicked.connect(self.on_click)

        @pyqtSlot()
        def on_click(self):
            # double click to put selected item into clipboard
            pyperclip.copy(self.tableWidget.selectedItems()[0].text())

        @pyqtSlot()
        def on_button_click(self):
            # TODO recreate tableWidget with accessions merged.
            print('merge button clicked. NOW MAKE IT REDRAW ENTIRE TABLE.')
            self.update()

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


def check_accession(accession, list_of_tests):
    """Check if there is a repeat in accessions"""
    for i in list_of_tests:
        print(i)
        if i[1] == accession:
            print("duplicate")
            print(len(list_of_tests[:i]))
            return len(list_of_tests[:i])
        else:
            return False


def main():
    # gathering the initial values for 1) filter and 2) delete duplicates
    if len(sys.argv) >= 2:
        search = " ".join(sys.argv[1:])  # unable to get multiple arguments
        search = search.upper()
    elif len(sys.argv) == 1:
        search = input("Worklist filter? (enter to skip): ")
    else:
        sys.exit("More than 1 argument; Feature not yet implemented...")
    #--------------------------------------------------------------------------------
    pending_list = []
    list_of_worklists = []
    with open(get_filename(),'r') as f:
        for line in f:
            if line.strip() == '': continue
            if "W O R K L I S T   P E N D I N G" in line:	
                previous = ''
                line = ''						#skips fist new-page-header-line
                for i in range(7):				#skips the next 7 new-page-header-lines
                    next(f)
                    # pass
            pending_list.append(line)
    total_count = 0
    for line in pending_list:
        if "TOTAL FOR WORKLIST" in line:
            digits = line.strip()
            total_count += int(digits[-6:])
    
    #print_accessions(search, sort_flag, list_of_worklists)
    worklist = []
    list_of_worklists = []
    list_of_tests = []
    tests = ""
    add_more_tests = 0
    for line in pending_list:
        if "WORKLIST:" in line:
            # collect worklist
            line = line.replace("DELAY=2", "")
            if worklist:
                list_of_worklists.append(worklist)
            worklist = []
            line = line[9:].strip()
            line = line.split('/', 1)[0]
            worklist.append(line)
        if re.match(r'[A-Z][A-Z]\d\d\d\d\d\d', line[12:20]):
            # collect accession
            doc = line[64:74]
            accession = line[12:21].strip()
            if accession[-1:] == '(': accession = accession[:-1]
            # cleans a trailing ( in MC accessions that are *(H) 
            worklist.append(accession)
        if add_more_tests:
            # collects secondary lines of tests
            tests += " " + line.strip()
            if line.strip()[-1] != ",":
                add_more_tests = 0
                list_of_tests.append([worklist[0], accession, tests, doc])
                tests = ""
        if "Pending Tests: " in line:
            # collect first line of tests and raise flag if there
            # are more than one line of tests
            tests += line[27:].strip()
            if line.strip()[-1] == ",":
                add_more_tests = 1
            else:
                list_of_tests.append([worklist[0], accession, tests, doc])
                tests = ""
    #print_accessions(search, sort_flag, list_of_worklists)
    print_tests(search, list_of_tests)
    os.system('pause')


if __name__ == '__main__':
    main()
