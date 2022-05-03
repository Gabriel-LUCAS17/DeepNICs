@ECHO OFF
REM Program : Batch-ROP-Training.bat
REM Description : Launch ROP-Training on ROP-Training samples ("apprentissage" files). 
REM Author : Mathieu Brunner.

REM Counting the number of command-line arguments.
SET argc=0
FOR %%x in (%*) do SET /A argc+=1
ECHO Number of command-line arguments : %argc%

REM Checking the number of command-line arguments.
IF NOT %argc%==7 GOTO Usage 

REM Define variable for current working directory.
SET oldwd=%~dp0
ECHO Current working directory: %oldwd%

REM Setting path towards rop executable.
SET ropPath=%~dp0\..\Release-ROP\rop82.exe
REM Check if rop executable exists.
IF NOT EXIST %ropPath% (
	ECHO ROP executable not found.
	ECHO Path towards rop executable set to : %ropPath%
	ECHO You may want to change the value of the ropPath variable.
	EXIT /B 1
)

REM Setting folder name for stratified variable.
SET wd=%1
ECHO Processing folder : %wd%

REM Checking if specified folder exists.
IF EXIST %wd%\ ( 
	CD /D %wd%
) ELSE ( 
	ECHO Specified folder doesn't exist : %wd%
	EXIT /B 1 
)

REM Setting constants.
SET /A infRange=%2
SET /A supRange=%3
SET /A infVar=%4
SET /A supVar=%5
SET /A TreeBegins=%6
SET /A TreeEnds=%7
SET /A nbCombMin=5000

REM For Loop : Simulation Range.
FOR /L %%i IN (%infRange%,1,%supRange%) DO ( ECHO Processing range folder R%%i
	IF EXIST R%%i\ (
		CD R%%i
	) ELSE (
		ECHO Specified folder doesn't exist : R%%i
		CD /D %oldwd%
		EXIT /B 1
	)
	REM For Loop : Number of Selected Variables.
	FOR /L %%j IN (%infVar%,1,%supVar%) DO ( ECHO Processing range/var folders R%%i V%%j
		IF EXIST V%%j\ (
			CD V%%j
		) ELSE (
			ECHO Specified folder doesn't exist : V%%j
			CD /D %oldwd%
			EXIT /B 1
		)

		ECHO Launching ROP-Training.	
		CALL :ROPTraining %TreeBegins% %TreeEnds% %%i %%j
		REM Second pass to check for any missing file.
		ECHO Launching second pass to check for any missing file.
		CALL :ROPTraining %TreeBegins% %TreeEnds% %%i %%j

		CD ..
	)
	CD ..
)
REM Deletion of unnecessary files.
REM PAUSE
DEL /S *_sol.csv > nul 2> nul
DEL /S debug.csv > nul 2> nul
CD /D %oldwd%
EXIT /B 0

REM Subroutine to explain the script usage.
:Usage
ECHO Wrong number of arguments ! Seven command-line arguments expected.
ECHO Usage : Batch-ROP-Training.bat arg1 arg2 arg3 arg4 arg5 arg6 arg7
ECHO    where arg1 is the name of the folder : a1, ..., a30.
ECHO	      arg2 is the minimum range of simulation (just the number).
ECHO	      arg3 is the maximum range of simulation (just the number).
ECHO	      arg4 is the minimum number of selected variables (just the number).
ECHO	      arg5 is the maximum number of selected variables (just the number).
ECHO 	      arg6 is the index of the tree on which the Training begins (integer).
ECHO 	      arg7 is the index of the tree on which the Training ends (integer).
ECHO Example usage : Batch-ROP-Training.bat a5 3 9 3 10 1 100
EXIT /B 1

REM Subroutine for ROP-Training on given configuration.
REM Takes four positional arguments : arg1 = treeBegins, arg2 = TreeEnds, arg3 = simulRange, arg4 = nbSelectedFeatures.
:ROPTraining
SET /A begins=%1
SET /A ends=%2
SET /A simulRange=%3
SET /A nbVarROP=%4
FOR /L %%k IN (%begins%,1,%ends%) DO ( IF NOT EXIST apprentissage_%%k_res.csv ( ECHO Processing file : %%k
	CALL :ROPexecution %%k %simulRange% %nbVarROP% )
)
EXIT /B 0

REM Subroutine for ROP execution.
REM Takes three positional arguments : arg1 = tree number, arg2 = range of simul range, arg3 = nb selected var.
:ROPexecution
SET /A simulRange=%2
SET /A nbVarROP=%3
SET /A count=1
SET /A nbComb=1
REM Power function.
:Multiply
SET /A nbComb=nbComb*simulRange
SET /A count=count+1

REM Setting num of processors to use depending on num of combinations to test.
IF %nbComb% GEQ %nbCombMin% (
	%ropPath% apprentissage_%1 3 2 50000 > nul 2> nul
) ELSE (
	IF %count% LEQ %nbVarROP% (
		GOTO Multiply
	) ELSE (
		START /B %ropPath% apprentissage_%1 3 2 50000 1 > nul 2> nul
	)
)
EXIT /B 0
