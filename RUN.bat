@echo off

set "VENV_DIR=%~dp0%venv"

mkdir tmp 2>NUL

dir "%VENV_DIR%\Scripts\Python.exe" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :activate
echo Creating venv...
python -m venv "%VENV_DIR%"

:activate
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
call venv\Scripts\activate.bat

%PYTHON% script_requirements.py

call venv\Scripts\deactivate.bat
pause
