@echo off
REM Esegue i test Python nel sottoalbero Ver_02 usando l'interprete del venv locale.
setlocal

REM Determina il percorso assoluto della cartella del batch file
set SCRIPT_DIR=%~dp0

REM Percorso dell'interprete Python nel venv dell'workspace
set PYTHON_EXE=%SCRIPT_DIR%..\ai_env\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
    echo Errore: interprete Python non trovato in %PYTHON_EXE%
    exit /b 1
)

echo Using Python interpreter: %PYTHON_EXE%
cd /d "%SCRIPT_DIR%"

REM Usa unittest discovery sui file test_*.py nella cartella corrente
"%PYTHON_EXE%" -m unittest discover -s "%SCRIPT_DIR%" -p "test_*.py" %*
set TEST_RESULT=%ERRORLEVEL%

if %TEST_RESULT% neq 0 (
    echo.
    echo Alcuni test sono falliti.
    exit /b %TEST_RESULT%
)

echo.
echo Tutti i test sono passati.
exit /b 0
