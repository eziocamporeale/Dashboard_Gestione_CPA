@echo off
REM Script di installazione per Dashboard Gestione CPA (Windows)
REM Esegui questo file come amministratore se necessario

echo 🚀 Installazione Dashboard Gestione CPA
echo ======================================

REM Controllo Python
echo 🐍 Controllo versione Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato. Installa Python 3.8+ e riprova.
    pause
    exit /b 1
)

echo ✅ Python trovato

REM Controllo pip
echo 📦 Controllo pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip non trovato. Installa pip e riprova.
    pause
    exit /b 1
)

echo ✅ pip trovato

REM Creazione ambiente virtuale
echo 🔧 Creazione ambiente virtuale...
if not exist "venv" (
    python -m venv venv
    echo ✅ Ambiente virtuale creato
) else (
    echo ✅ Ambiente virtuale già esistente
)

REM Attivazione ambiente virtuale
echo 🔄 Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

REM Aggiornamento pip
echo ⬆️ Aggiornamento pip...
python -m pip install --upgrade pip

REM Installazione dipendenze
echo 📚 Installazione dipendenze...
pip install -r requirements.txt

REM Creazione directory necessarie
echo 📁 Creazione directory...
if not exist "exports" mkdir exports
if not exist ".streamlit" mkdir .streamlit

echo.
echo 🎉 Installazione completata con successo!
echo.
echo Per avviare l'applicazione:
echo   venv\Scripts\activate.bat
echo   python run.py
echo.
echo Per eseguire i test:
echo   python test_app.py
echo.
echo L'applicazione sarà disponibile su: http://localhost:8501
echo.
pause
