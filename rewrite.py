import re
import datetime
import sys
import os
# from openpyxl import Workbook


def filter_duplicates(accessions):
    """Removes duplicate accessions from a 1D list of accessions."""
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
    location = "".join(["C:\\Users\\DPaskalev\\Documents\\"
                        "REFERENCE PENDING LIST " , month , "-" , day , ".txt"])
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
        print(g, end = '\n')
        total_count += 1
    print("total_count:", total_count)


def print_tests(search, list_of_tests):
    """Print accessions in worklists as filtered by the 'search' key."""
    list_of_tests = [a for a in list_of_tests if search in a[0]]
    for i in list_of_tests:
        for j in list_of_tests:
            if j[2] == i[2] and j[3] != i[3]:
                i[3] += ', ' + j[3]
                i[0] += ', ' + j[0]
                list_of_tests.remove(j)
    # new loop b/c previous loop catches edge cases
    for i in list_of_tests:
        print("{: <20}  {}  {: >10}  {}".format(*i))
    output_array = [[i[0], i[2]] for i in list_of_tests]

    import pyperclip
    # Puts accessions into clipboard. First value is the FILTER.
    # There are NO DUPLICATES.
    pyperclip.copy(search + ''.join(['\n' + a[1] for a in output_array]))

    if len(list_of_tests) == 0:
        print("No matches found for ", search)
    else:
        print("Total accession count:", len(list_of_tests))
    # no filtering duplicates should be done here as duplicates are merged

    # import xlsxwriter as xl
    # import random, string

    # workbook = xl.Workbook('hello' + ''.join(random.choices(string.ascii_letters + string.digits, k=6)) + '.xlsx')
    # worksheet = workbook.add_worksheet()

    # for i in range(len(list_of_tests)):
    # 	worksheet.write('A' + str(i), list_of_tests[i][0])
    # 	worksheet.write('B' + str(i), list_of_tests[i][1])
    # 	worksheet.write('C' + str(i), list_of_tests[i][2])
    # 	worksheet.write('D' + str(i), list_of_tests[i][3])
    # workbook.close()


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


class Accession:
    def __init__(self, accession, name, dob, client, date, tests):
        self.accession = accession
        self.name = name
        self.dob = dob
        self.client = client
        self.date = date
        #is there a way to enforce tests variable type?
        self.tests = []
        self.tests.append(tests)
    
    def get_tests(self):
        #return a string containing the tests in format "test1, test2, test3"
        return ", ".join(self.tests)
    
    def __str__(self):
        #to string operator. Returns a string with the accession in it
        return ("This is an object contain the information for the following accession:\n", accession) 
        
    def printpatient(self):
        print(accession, '\n', 
                    name,'\n', 
                    dob,'\n', 
                    client,'\n', 
                    date,'\n', 
                    #comment,'\n',
                    self.get_tests(),'\n')


def main():
    # gathering the initial values for 1) filter and 2) delete duplicates
    if len(sys.argv) >= 2:
        search = " ".join(sys.argv[1:])
    elif len(sys.argv) == 1:
        search = input("Worklist filter? (enter to skip): ")
    else:
        sys.exit("More than 1 argument; Feature not yet implemented...")

    # sort = "dummy value"
    # sort = input("Would you like to remove duplicate accessions? [Y/n] ")
    # sort = sort.lower()
    # if (sort != "" and sort != "y" and sort != "n"): sys.exit("Improper value")
    # if sort == "n": sort_flag = 0
    # else: sort_flag = 1
    #--------------------------------------------------------------------------------

    pending_list = []
    list_of_worklists = []
    with open(get_filename(),'r') as f:
        for line in f:
            if line.strip() == '':
                continue
            if "W O R K L I S T   P E N D I N G" in line:	
                previous = ''
                line = ''				# skips fist new-page-header-line
                for i in range(7):		# skips the next 7 new-page-header-lines
                    next(f)             # this saves times processing
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
                list_of_tests.append([worklist[0], doc, accession, tests])
                tests = ""
        if "Pending Tests: " in line:
            # collect first line of tests and raise flag if there
            # are more than one line of tests
            tests += line[27:].strip()
            if line.strip()[-1] == ",":
                add_more_tests = 1
            else:
                list_of_tests.append([worklist[0], doc, accession, tests])
                tests = ""
    #print_accessions(search, sort_flag, list_of_worklists)
    print_tests(search, list_of_tests)
    os.system('pause')


if __name__ == '__main__':
    main()
