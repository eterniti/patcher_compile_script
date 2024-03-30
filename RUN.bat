@echo off

set "VENV_DIR=%~dp0%venv"

dir "%VENV_DIR%\Scripts\Python.exe" >NUL 2>NUL
if %ERRORLEVEL% == 0 goto :activate
echo Creating venv...
py.exe -m venv "%VENV_DIR%"

:activate
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
call venv\Scripts\activate.bat

%PYTHON% script_requirements.py

call venv\Scripts\deactivate.bat
pause
