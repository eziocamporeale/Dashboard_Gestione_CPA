# 🧪 Dashboard Gestione CPA - PROGETTO SVILUPPO

## 📋 Descrizione
**PROGETTO DUPLICATO PER SVILUPPO E TEST** - Versione sperimentale per implementare schema raggruppato e nuove funzionalità.

## ⚠️ IMPORTANTE
**Questo è un progetto di SVILUPPO separato dal progetto di PRODUZIONE!**

- **🏠 Progetto Stabile:** `Dashboard_Gestione_CPA` (per lavoro)
- **🧪 Progetto Sviluppo:** `Dashboard_Gestione_CPA_DEV` (questo)

## 🎯 OBIETTIVI SVILUPPO

### **1. Schema Raggruppato**
- **Tabella `clienti_base`** - Dati base clienti (email unica)
- **Tabella `account_broker`** - Multipli account per cliente
- **Risoluzione** email duplicate

### **2. Nuove Funzionalità**
- **Gestione broker** predefiniti
- **Form semplificato** per account
- **Interfaccia migliorata**

### **3. Migrazione Dati**
- **Consolidamento** clienti con email duplicate
- **Mantenimento** integrità dati
- **Test** nuove funzionalità

## 🚀 Avvio Progetto DEV

### **Porta Separata:**
```bash
cd Dashboard_Gestione_CPA_DEV
streamlit run app.py --server.port 8506
```

### **URL Accesso:**
- **Progetto Stabile:** http://localhost:8501
- **Progetto DEV:** http://localhost:8506

## 📊 Struttura Database

### **Schema Attuale (Stabile):**
- `clienti` - Tabella singola con tutti i dati

### **Schema Nuovo (Raggruppato):**
- `clienti_base` - Dati base clienti
- `account_broker` - Account broker per cliente

## 🔄 Flusso Sviluppo

1. **Test** nuove funzionalità qui
2. **Verifica** stabilità e funzionalità
3. **Confronta** con versione stabile
4. **Implementa** in produzione quando pronto

## 🛡️ Sicurezza

- **Zero impatto** sul progetto di produzione
- **Test isolati** e sicuri
- **Rollback** istantaneo se necessario
- **Confronto diretto** tra versioni

## 📞 Supporto

**Per problemi:**
1. **Progetto Stabile** → Controlla README principale
2. **Progetto DEV** → Controlla questo README
3. **Bug o Errori** → Testa qui prima di produzione

---

**🧪 SVILUPPO SICURO E ISOLATO! 🚀**
