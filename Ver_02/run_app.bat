@echo off
REM Avvia l'app GUI usando l'interprete Python del venv locale.
setlocal

set SCRIPT_DIR=%~dp0
set PYTHON_EXE=%SCRIPT_DIR%..\ai_env\Scripts\python.exe
set APP_FILE=%SCRIPT_DIR%app_gui.py

if not exist "%PYTHON_EXE%" (
    echo Errore: interprete Python non trovato in %PYTHON_EXE%
    exit /b 1
)

if not exist "%APP_FILE%" (
    echo Errore: file app non trovato in %APP_FILE%
    exit /b 1
)

echo Avvio dell'applicazione...
Start "AppGUI" "%PYTHON_EXE%" "%APP_FILE%"
echo App avviata.
exit /b 0
