# newpython
![license](https://img.shields.io/github/license/dpaskal/newpython?style=plastic "License")  

This program produces a spreadsheet-like table. Its only purpose is to sort, filter, and merge duplicates in the pending list.  
<sub><sup>No longer needing to print 200-500 pages of paper is a plus.</sup></sub>

# Setup
First time set up requires one thing: [The SmarTerm macro.](https://github.com/dpaskal/newpython/blob/master/UserVT.stm)  
The UserVT.stm file needs to be placed in "C:\Users\\(user)\Documents\SmarTerm\Macros\UserVT.stm"  

# Instructions  
This program works in two steps.  
* First: Acquire the pending list as a text file. This is done via the SmarTerm macro.   
* Second: Use that text file to generate a spreadsheet.

Part 1) Get the text file:  
Sign into Antrim and go to the Main Menu. Run macro "CAPTURE_PEND_LIST".

Part 2) Generate the spreadsheet:  
Run DanielPaskalev.exe. Give it 10-15 seconds to load up depending on the size of the pending list. 

# Details

The macro prints the DEPT:REFERENCE (2 day delay) pending list to the screen while recording it to a text file. This takes 1-2 minutes.

The text file is created in "My Documents" with the name "REFERENCE PENDING LIST [month]-[day].txt". Where month and day are the digits of the month and day. No leading zeros.  
For example the pending list for July 26th would be "REFERENCE PENDING LIST 7-26.txt"  

The macro will do all of this for you. You are encouraged to run the macro several times a day. This will overwrite the day's pending list with a more up-to-date version.


In [Text format](https://0bin.net/paste/W46-CwVSK8K0Lcfp#wN1opncV7E2R+AI-JPko++iSPiie0slujtKgD3Fk3+S), the macro is essentially a visual basic script. It needs to be placed inside UserVT.stm and put in the Documents\SmarTerm\Macros folder for SmarTerm to read it.  
Several other macros exist.  
"CAPTURE_SEND_OUT_LIST" - Puts the Send-out Pending list into a text file.  
"CAPTURE_TS_QUEST" - Puts the TS QUEST worklist (0 delay) into a text file.  
"CAPTURE_QUEST" - Puts the QUEST worklist (0 delay) into a text file.  
"MORNING_ROUTINE" - Puts several worklists on the screen. They are: ARIOSA, AMBRY, MAYO63, MERCY, DEMO.
