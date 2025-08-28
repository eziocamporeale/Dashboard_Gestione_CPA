# 🚀 Dashboard Gestione CPA Broker

Dashboard web per la gestione completa delle CPA (Cost Per Acquisition) dei broker, sviluppata con Streamlit.

## ✨ Caratteristiche Principali

- **🔐 Sistema di Autenticazione** - Login sicuro con ruoli e permessi
- **👥 Gestione Clienti** - CRUD completo per clienti e broker
- **🔄 Gestione Incroci** - Sistema avanzato per incroci e CPA
- **📊 Dashboard Analitica** - Grafici e statistiche in tempo reale
- **📱 Interfaccia Responsiva** - Design moderno e intuitivo
- **🗄️ Database SQLite** - Archiviazione locale sicura

## 🛠️ Tecnologie Utilizzate

- **Frontend**: Streamlit 1.32.0+
- **Backend**: Python 3.9+
- **Database**: SQLite3
- **Grafici**: Plotly
- **Gestione Dati**: Pandas

## 🚀 Deploy su Streamlit Cloud

### Prerequisiti
- Account Streamlit Cloud
- Repository GitHub pubblico
- Python 3.9+

### Passi per il Deploy

1. **Fork/Clone** questo repository su GitHub
2. **Vai su** [share.streamlit.io](https://share.streamlit.io)
3. **Connetti** il tuo repository GitHub
4. **Configura** il deploy:
   - **Main file path**: `app.py`
   - **Python version**: 3.9
5. **Clicca Deploy**

### Configurazione Post-Deploy

1. **Vai su** la tua app deployata
2. **Configura** le credenziali utente in `.streamlit/secrets.toml`
3. **Riavvia** l'app per applicare le modifiche

## 🔧 Configurazione Locale

### Installazione

```bash
# Clone del repository
git clone <your-repo-url>
cd Dashboard_Gestione_CPA

# Creazione ambiente virtuale
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oppure
.venv\Scripts\activate     # Windows

# Installazione dipendenze
pip install -r requirements.txt
```

### Configurazione Database

```bash
# Inizializzazione database
python -c "from database.database import DatabaseManager; DatabaseManager().init_database()"

# Inserimento dati di esempio (opzionale)
python sample_data.py
```

### Avvio Locale

```bash
# Avvio dell'applicazione
streamlit run app.py

# Oppure con configurazioni personalizzate
streamlit run app.py --server.port 8501 --server.headless true
```

## 🔐 Credenziali di Default

**Admin:**
- Username: `admin`
- Password: `admin123`

**Utente Standard:**
- Username: `ezio`
- Password: `password123`

**Visualizzatore:**
- Username: `user`
- Password: `user123`

## 📁 Struttura del Progetto

```
Dashboard_Gestione_CPA/
├── app.py                 # App principale Streamlit
├── components/            # Componenti UI riutilizzabili
│   ├── auth.py           # Sistema di autenticazione
│   ├── charts.py         # Grafici e visualizzazioni
│   ├── client_form.py    # Form per clienti
│   ├── client_table.py   # Tabella clienti
│   └── incroci_tab.py   # Gestione incroci
├── config/               # Configurazioni
│   └── users.py         # Utenti e permessi
├── database/            # Gestione database
│   ├── database.py      # Manager database principale
│   └── incroci_manager.py # Manager incroci
├── utils/               # Utility e helper
├── .streamlit/          # Configurazioni Streamlit
├── requirements.txt     # Dipendenze Python
└── README.md           # Questo file
```

## 🔒 Sicurezza

- **Autenticazione** basata su sessioni Streamlit
- **Ruoli e permessi** per diverse funzionalità
- **Validazione input** per prevenire SQL injection
- **Gestione errori** sicura senza esposizione di dati sensibili

## 📊 Funzionalità Principali

### Gestione Clienti
- ✅ Creazione nuovi clienti
- ✅ Modifica dati esistenti
- ✅ Eliminazione sicura
- ✅ Ricerca e filtri avanzati
- ✅ Esportazione dati CSV

### Gestione Incroci
- ✅ Creazione incroci CPA
- ✅ Monitoraggio performance
- ✅ Chiusura automatica
- ✅ Storico completo

### Dashboard Analitica
- ✅ Statistiche in tempo reale
- ✅ Grafici interattivi
- ✅ Metriche KPI
- ✅ Report personalizzabili

## 🐛 Risoluzione Problemi

### Problemi Comuni

1. **App non si avvia**: Verifica Python 3.9+ e dipendenze
2. **Database vuoto**: Esegui `init_database()` e `sample_data.py`
3. **Errori di autenticazione**: Verifica credenziali in `config/users.py`
4. **Problemi di performance**: Controlla dimensioni database e ottimizzazioni

### Log e Debug

- **Log locali**: `logs/` directory
- **Console browser**: F12 per errori JavaScript
- **Streamlit logs**: Terminal dove avvii l'app

## 🤝 Contributi

1. **Fork** il progetto
2. **Crea** un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** le modifiche (`git commit -m 'Add AmazingFeature'`)
4. **Push** al branch (`git push origin feature/AmazingFeature`)
5. **Apri** una Pull Request

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi `LICENSE` per dettagli.

## 📞 Supporto

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentazione**: [Wiki del progetto](https://github.com/your-repo/wiki)
- **Email**: support@your-domain.com

---

**Sviluppato con ❤️ per la gestione professionale delle CPA Broker**
