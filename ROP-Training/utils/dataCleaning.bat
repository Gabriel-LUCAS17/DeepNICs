@ECHO OFF
REM Program : dataCleaning.bat
REM Description : Clean a folder and all its subfolders. You can change the types of files you want to delete. 
REM Author : Mathieu Brunner.

REM Counting the number of command-line arguments.
SET argc=0
FOR %%x in (%*) do SET /A argc+=1
ECHO Number of command-line arguments : %argc%

REM Checking the number of command-line arguments.
IF NOT %argc%==1 GOTO Usage 

ECHO Beginning of dataCleaning.
ECHO You have entered the following command-line argument : %1

:PROMPT
SET /P AREYOUSURE=Is this the correct command-line argument (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

REM Check if command-line argument path exists.
IF NOT EXIST %1 (
	ECHO Specified path doesn't exist.
	ECHO Path set to : %1
	EXIT /B 1
)

REM Part of the script dedicated to cleaning useless files.
CD /D %1
FOR /D /r %%G IN (*) DO (
	CD %%G
	ECHO Cleaning folder : %%G
	DEL debug.csv > nul 2> nul
	DEL *_sol.csv > nul 2> nul
	DEL *_SUPPRIMER_ > nul 2> nul
	DEL rop82.exe > nul 2> nul
	DEL *.bat > nul 2> nul
	DEL *.dll > nul 2> nul
	DEL *.error > nul 2> nul
	DEL *.out > nul 2> nul
	DEL *.txt > nul 2> nul
	)
CD /D %1
ECHO End of dataCleaning.
EXIT /b

:Usage
ECHO Wrong number of arguments !
ECHO Usage :
ECHO    dataCleaning.bat arg1
ECHO             where arg1 is the path to the folders to clean.
ECHO ** Use only \ for path in command-line argument. **
ECHO ** Use uppercases for command-line argument confirmation. **
ECHO ** WARNING ! All the subfolders will also be cleaned ! **
ECHO ** You may want to change the types of files which will be deleted. **
EXIT /b 1

:END
ECHO You didn't answer Y (uppercase y), therefore the execution ends here.
EXIT /b
