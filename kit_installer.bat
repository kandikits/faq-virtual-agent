@echo off
REM This is a sample script
ECHO======================================================================================
ECHO		Kandi kit installation process has begun
ECHO======================================================================================
ECHO 	This kit installer works only on Windows OS
ECHO 	Based on your network speed, the installation may take a while
ECHO======================================================================================
setlocal ENABLEDELAYEDEXPANSION
REM update below path if required
SET PY_LOCATION="C:\Python"
SET PY_VERSION=3.9.8
SET PY_DOWNLOAD_URL=https://www.python.org/ftp/python/3.9.8/python-3.9.8-amd64.exe
SET REPO_DOWNLOAD_URL=https://github.com/kandikits/faq-virtual-agent/releases/download/v1.0.0/faq-virtual-agent.zip
SET REPO_DEPENDENCIES_URL=https://raw.githubusercontent.com/kandikits/faq-virtual-agent/main/requirements.txt
SET REPO_NAME=faq-virtual-agent.zip
where /q python
IF ERRORLEVEL 1 (
	ECHO==========================================================================
    ECHO Python wasn't found in PATH variable
	ECHO==========================================================================
	CALL :Install_python_and_modules
	IF ERRORLEVEL 1 (
		PAUSE
	) ELSE (
		CALL :Download_repo
	)
) ELSE (
	for /f %%i in ('python -c "import sys; print(sys.version_info[0])"') do set PYTHON_M_VERSION=%%i
	REM ECHO The major version of python was "!PYTHON_M_VERSION!"
	IF !PYTHON_M_VERSION! EQU 2 (
		ECHO==========================================================================
		ECHO python3 will be installed since the version of existing python is 2
		ECHO==========================================================================
		CALL :Install_python_and_modules
		IF ERRORLEVEL 1 (
			PAUSE
		) ELSE (
			CALL :Download_repo
		)
	) ELSE (
		IF !PYTHON_M_VERSION! EQU 3 (
			ECHO==========================================================================
			ECHO A valid python is detected and hence installing dependent modules ...
			ECHO==========================================================================
			bitsadmin /transfer dependency_download_job /download %REPO_DEPENDENCIES_URL% "%cd%\requirements.txt"
			python -m pip install -r requirements.txt
			CALL :Download_repo
		) else (
			ECHO==========================================================================
			ECHO Python wasn't detected!
			ECHO==========================================================================
			CALL :Install_python_and_modules
			IF ERRORLEVEL 1 (
				PAUSE
			) ELSE (
				CALL :Download_repo
			)
		)	
	)
)
PAUSE
EXIT /B %ERRORLEVEL%

:Download_repo
bitsadmin /transfer repo_download_job /download %REPO_DOWNLOAD_URL% "%cd%\%REPO_NAME%"
ECHO==========================================================================
ECHO 	The Kit has been installed successfully
ECHO==========================================================================
ECHO 	To run the kit, follow further instructions of the kit in kandi	
ECHO==========================================================================
EXIT /B 0

:Install_python_and_modules
ECHO==========================================================================
ECHO Downloading python%PY_VERSION% ... 
ECHO==========================================================================
REM curl -o python-%PY_VERSION%-amd64.exe %PY_DOWNLOAD_URL%
bitsadmin /transfer python_download_job /download %PY_DOWNLOAD_URL% "%cd%\python-%PY_VERSION%-amd64.exe"
ECHO Installing python%PY_VERSION% ...
python-%PY_VERSION%-amd64.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 TargetDir=%PY_LOCATION%
ECHO==========================================================================
ECHO Python installed in path : %PY_LOCATION%
ECHO==========================================================================
IF ERRORLEVEL 1 (
		ECHO==========================================================================
		ECHO There was an error while installing python!
		ECHO==========================================================================
		EXIT /B 1
) ELSE (
	ECHO==========================================================================
	ECHO Installing dependent modules ...
	bitsadmin /transfer dependency_download_job /download %REPO_DEPENDENCIES_URL% "%cd%\requirements.txt"
	%PY_LOCATION%\python.exe -m pip install -r requirements.txt
	ECHO==========================================================================
)
EXIT /B 0
