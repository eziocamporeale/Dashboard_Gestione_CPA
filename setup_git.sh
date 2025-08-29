#!/bin/bash

# Script per configurare Git su Streamlit Cloud
# Questo script configura le credenziali Git per abilitare il push automatico

echo "🔧 Configurazione Git per Streamlit Cloud..."

# Configura le credenziali Git
git config --global user.email "ezio@camporeale.com"
git config --global user.name "Ezio Camporeale"

# Verifica la configurazione
echo "✅ Configurazione Git completata:"
echo "   Email: $(git config --global user.email)"
echo "   Nome: $(git config --global user.name)"

# Testa la connessione a GitHub
echo "🔍 Test connessione GitHub..."
if git ls-remote --exit-code origin >/dev/null 2>&1; then
    echo "✅ Connessione GitHub OK"
else
    echo "❌ Problema connessione GitHub"
fi

echo "🎯 Setup Git completato!"
