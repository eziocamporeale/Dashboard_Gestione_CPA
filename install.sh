#!/bin/bash

# Script di installazione per Dashboard Gestione CPA
# Compatibile con Linux e macOS

set -e

echo "🚀 Installazione Dashboard Gestione CPA"
echo "======================================"

# Controllo Python
echo "🐍 Controllo versione Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python non trovato. Installa Python 3.8+ e riprova."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION trovato"

# Controllo pip
echo "📦 Controllo pip..."
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip non trovato. Installa pip e riprova."
    exit 1
fi

PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "✅ pip trovato"

# Creazione ambiente virtuale
echo "🔧 Creazione ambiente virtuale..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✅ Ambiente virtuale creato"
else
    echo "✅ Ambiente virtuale già esistente"
fi

# Attivazione ambiente virtuale
echo "🔄 Attivazione ambiente virtuale..."
source venv/bin/activate

# Aggiornamento pip
echo "⬆️ Aggiornamento pip..."
$PIP_CMD install --upgrade pip

# Installazione dipendenze
echo "📚 Installazione dipendenze..."
$PIP_CMD install -r requirements.txt

# Creazione directory necessarie
echo "📁 Creazione directory..."
mkdir -p exports
mkdir -p .streamlit

# Permessi di esecuzione
echo "🔐 Impostazione permessi..."
chmod +x run.py
chmod +x test_app.py

echo ""
echo "🎉 Installazione completata con successo!"
echo ""
echo "Per avviare l'applicazione:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Per eseguire i test:"
echo "  python test_app.py"
echo ""
echo "L'applicazione sarà disponibile su: http://localhost:8501"
