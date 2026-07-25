@echo off
REM Build HTML docs using sphinx (requires packages in venv)
setlocal
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=%SCRIPT_DIR%..\ai_env\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
  echo Errore: interprete Python non trovato in %PYTHON_EXE%
  exit /b 1
)

echo Building Sphinx docs...
"%PYTHON_EXE%" -m sphinx -b html "%SCRIPT_DIR%docs" "%SCRIPT_DIR%docs\_build\html"
if %ERRORLEVEL% neq 0 (
  echo Errore: la build della documentazione non e\' riuscita.
  exit /b %ERRORLEVEL%
)

echo Documentazione generata in: %SCRIPT_DIR%docs\_build\html
exit /b 0
