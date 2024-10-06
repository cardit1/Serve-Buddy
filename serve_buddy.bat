@echo off
setlocal enabledelayedexpansion

:: Serve Buddy Batch File
echo ===============================
echo         Serve Buddy
echo         Version 1.0.0
echo ===============================
echo.

:: Set default values
set "PORT=8000"
set "DIR=%CD%"

:: Parse command-line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="-h" goto :show_help
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-p" set "PORT=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="--port" set "PORT=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="-d" set "DIR=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="--dir" set "DIR=%~2" & shift & shift & goto :parse_args
shift
goto :parse_args

:end_parse_args

:: Prompt for port if not provided
if "%PORT%"=="8000" (
    set /p "PORT_INPUT=Enter the port number for Serve Buddy (default 8000): "
    if not "!PORT_INPUT!"=="" set "PORT=!PORT_INPUT!"
)

:: Validate port number
set "VALID_PORT="
for /f "delims=0123456789" %%i in ("!PORT!") do set "VALID_PORT=%%i"
if not "!VALID_PORT!"=="" (
    echo Invalid port number. Using default port 8000.
    set "PORT=8000"
)

:: Check if the directory exists
if not exist "!DIR!" (
    echo Error: The directory '!DIR!' does not exist.
    pause
    exit /b 1
)

:: Create a simple HTML file with directory listing
echo ^<!DOCTYPE html^>^<html^>^<head^>^<title^>Serve Buddy^</title^>^</head^>^<body^> > index.html
echo ^<h1^>Files in %DIR%:^</h1^>^<ul^> >> index.html
for %%F in ("%DIR%\*.*") do (
    echo ^<li^>^<a href="%%~nxF"^>%%~nxF^</a^>^</li^> >> index.html
)
echo ^</ul^>^</body^>^</html^> >> index.html

:: Start a simple HTTP server using hfs (HTTP File Server)
echo Starting Serve Buddy...
echo.
echo Local URL: http://localhost:%PORT%
echo Network URL: http://%COMPUTERNAME%:%PORT%
echo.
echo Press Ctrl+C to stop Serve Buddy
echo.
hfs.exe -p %PORT% "%DIR%"

:: Clean up
del index.html

goto :eof

:show_help
echo Usage: %~nx0 [options]
echo.
echo Options:
echo   -h, --help            Show this help message and exit
echo   -p PORT, --port PORT  Port to run Serve Buddy on (default: 8000)
echo   -d DIR, --dir DIR     Directory to serve files from (default: current working directory)
echo.
echo Once Serve Buddy is running, open a web browser and navigate
echo to the provided URL to access the file server interface.
pause
exit /b 0