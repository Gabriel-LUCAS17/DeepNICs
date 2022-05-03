@ECHO OFF
REM Program : Clear-Results.bat
REM Description : Remove .csv and .jpg files inside folder given as command-line argument. 
REM Author : Mathieu Brunner.

SET oldwd=%~dp0

REM Counting the number of command-line arguments.
SET argc=0
FOR %%x in (%*) do SET /A argc+=1

REM Checking the number of command-line arguments.
IF NOT %argc%==1 GOTO Usage 

REM Setting folder name for stratified variable.
SET wd=%1
ECHO Processing folder : %wd%

:PROMPT
SET /P AREYOUSURE=Is this the correct command-line argument (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

REM Checking if specified folder exists.
IF EXIST %wd%/ ( 
	RMDIR /S %wd%
) ELSE ( 
	ECHO Specified folder doesn't exist : %wd%
	EXIT /B 1 
)

CD /D %oldwd%
EXIT /B 0

REM Subroutine to explain the script usage.
:Usage
ECHO Wrong number of arguments ! One command-line argument expected.
ECHO Usage : Remove-Csv-Files.bat arg1
ECHO    where arg1 is the name of the folder.
ECHO Example usage : Remove-Csv-Files.bat C:\Users\UserName\Desktop\Results-Wisconsin-AP
ECHO ** Use only \ for path in command-line argument. **
ECHO ** Use uppercases for command-line argument confirmation. **
ECHO ** !!! WARNING !!! All .csv and .jpg files will be deleted ! **
EXIT /B 1

:END
ECHO You didn't answer Y (uppercase y), therefore the execution ends here.
EXIT /b
