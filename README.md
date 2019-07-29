# newpython

This program produces a spreadsheet-like table. Its only purpose is to sort and filter the pending list.  
<sub><sup>No longer needing to print 200-500 pages of paper is a plus.</sup></sub>

# Setup
First time set up requires one thing: [The SmarTerm macro.](https://github.com/dpaskal/newpython/blob/master/UserVT.stm)  
The UserVT.stm file needs to be placed in "C:\Users\\(user)\Documents\SmarTerm\Macros\UserVT.stm"  

# Instructions  
This program works in two steps.  
* First acquire the pending list as a text file. This is done via a SmarTerm macro.   
* Second use that text file to generate a spreadsheet.

Part 1) Get the text file:  
Sign into Antrim and go to the Main Menu. Run macro "CAPTURE_PEND_LIST".

Part 2) Generate the spreadsheet:  
Run DanielPaskalev.exe. Give it 10-15 seconds to load up depending on the size of the pending list. 

# Details

The macro prints the DEPT:REFERENCE pending list to the screen while recording it to a text file.

The text file is created in "My Documents" with the name "REFERENCE PENDING LIST [month]-[day].txt". Where month and day are the digits of the month and day. No leading zeros.  
For example the pending list for July 26th would be "REFERENCE PENDING LIST 7-26.txt"  

The macro will do all of this for you. You are encouraged to run the macro several times a day. This will overwrite the day's pending list with a more up-to-date version.


An accompanying SmarTerm macro is used to create this text file. See [UserVT.stm](https://github.com/dpaskal/newpython/blob/master/UserVT.stm) or in [Text format](https://0bin.net/paste/W46-CwVSK8K0Lcfp#wN1opncV7E2R+AI-JPko++iSPiie0slujtKgD3Fk3+S)  

The UserVT.stm file needs to be placed in "C:\Users\\(user)\Documents\SmarTerm\Macros\UserVT.stm"  
Macro name: "CAPTURE_PEND_LIST"
