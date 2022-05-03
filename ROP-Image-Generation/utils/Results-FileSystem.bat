@ECHO OFF
REM Program : Results-FileSystem.bat
REM Description : Generates folders containing results of ROP-Image-Generation. 
REM Author : Mathieu Brunner.

SET oldwd=%~dp0

ECHO Generating filesystem for ROP-Image-Generation Results.

REM Counting the number of command-line arguments.
SET argc=0
FOR %%x in (%*) do SET /A argc+=1

REM Checking the number of command-line arguments.
IF NOT %argc%==2 GOTO Usage 

REM Setting folder name for ROP-Results.
SET data_path=%1
SET wd=%2
ECHO Generating ROP-Results folder : %wd%

REM Checking if specified folders exist.
IF NOT EXIST %data_path%/ (
	ECHO Specified Data Path doesn't exist.
	ECHO The Data Path argument was set to : %data_path%
	EXIT /B 1
)

IF NOT EXIST %wd%/ (
	ECHO Creating folder: %wd%
	MKDIR %wd%
)
CD /D %wd%

REM Generation of subfolders.
MKDIR ImagesPNG > nul 2> nul
CD ImagesPNG
FOR /L %%j IN (1,1,96) DO (
	MKDIR NIC%%j > nul 2> nul
	CD NIC%%j
	MKDIR 0 > nul 2> nul
	MKDIR 1 > nul 2> nul
	CD ..
)
CD ..
MKDIR ImagesFusePNG > nul 2> nul
FOR /F %%i IN ('DIR /B %data_path%a*') DO (
	MKDIR %%i > nul 2> nul
	CD %%i
	MKDIR Images > nul 2> nul
	CD Images
	MKDIR Fuse > nul 2> nul
	FOR /L %%j IN (1,1,96) DO (
		MKDIR NIC%%j > nul 2> nul
	)
	CD ..
	MKDIR ImagesTransform > nul 2> nul
	CD ImagesTransform
        MKDIR Fuse > nul 2> nul
	FOR /L %%j IN (1,1,96) DO (
		MKDIR NIC%%j > nul 2> nul
	)
        CD ..
	MKDIR NICmatrix > nul 2> nul
	CD ..
)

CD /D %oldwd%
EXIT /B 0

REM Subroutine to explain the script usage.
:Usage
ECHO Wrong number of arguments ! Two command-line arguments expected.
ECHO Usage : Batch-ROP-Training.bat arg1 arg2
ECHO    where arg1 is the path towards the ROP-Training samples folder.
ECHO          arg2 is the path towards the Results folder.
ECHO Example usage : Batch-ROP-Training.bat C:\Users\UserName\Desktop\Data\ C:\Users\UserName\Desktop\Results-ROP\
EXIT /B 1
