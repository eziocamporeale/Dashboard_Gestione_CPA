# 🔄 App Hybrid - Dashboard CPA

## 📋 Descrizione
Versione ibrida della Dashboard CPA che permette di passare tra schema originale e schema raggruppato.

## ✨ Caratteristiche
- **🔄 Doppio Schema** - Passaggio tra schema originale e raggruppato
- **👥 Gestione Clienti** - Entrambi gli schemi supportati
- **🏦 Gestione Account** - Compatibilità con entrambi i sistemi
- **📊 Dashboard** - Visualizzazione unificata

## 🚀 Avvio
```bash
cd progetti/app_hybrid
streamlit run app_hybrid.py
```

## 🌐 Accesso
- **URL:** http://localhost:8501 (porta default)
- **Database:** SQLite locale con supporto dual-schema

## 📊 Schema Database
- **Schema Originale** - Tabella clienti singola
- **Schema Raggruppato** - clienti_base + account_broker

## 🎯 Vantaggi
- ✅ Transizione graduale tra schemi
- ✅ Compatibilità con dati esistenti
- ✅ Confronto diretto tra approcci
- ✅ Migrazione sicura dei dati
