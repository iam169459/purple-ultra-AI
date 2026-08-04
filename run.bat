@echo off
REM Purple Ultra AI - Windows Run Script

echo.
echo ===================================
echo   Purple Ultra AI - Advanced Assistant
echo ===================================
echo.

if "%1"=="" goto run
if "%1"=="run" goto run
if "%1"=="voice" goto voice
if "%1"=="install" goto install
if "%1"=="clean" goto clean
goto help

:run
echo Starting in interactive mode...
python main.py %2 %3 %4
goto end

:voice
echo Starting in voice mode...
python main.py --voice %2 %3 %4
goto end

:install
echo Installing dependencies...
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo Done!
goto end

:clean
echo Cleaning temporary files...
del /q temp\* 2>nul
del /q generated\images\* 2>nul
echo Done!
goto end

:help
echo Usage: run.bat [command]
echo.
echo Commands:
echo   run         - Run in text mode (default)
echo   voice       - Run in voice mode
echo   install     - Install dependencies
echo   clean       - Clean temp files
goto end

:end
