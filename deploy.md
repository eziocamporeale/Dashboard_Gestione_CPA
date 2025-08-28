# 🚀 Guida Deploy su Streamlit Cloud

## 📋 Prerequisiti

### 1. Account GitHub
- Repository GitHub pubblico
- Accesso per push e pull

### 2. Account Streamlit Cloud
- Vai su [share.streamlit.io](https://share.streamlit.io)
- Login con GitHub

### 3. Python Environment
- Python 3.9+ (Streamlit Cloud supporta 3.9, 3.10, 3.11)

## 🔧 Preparazione Repository

### 1. Struttura File Richiesta
```
Dashboard_Gestione_CPA/
├── app.py                 # ✅ File principale (obbligatorio)
├── requirements.txt       # ✅ Dipendenze (obbligatorio)
├── .streamlit/           # ✅ Configurazioni (opzionale)
│   └── config.toml      # ✅ Configurazioni app
├── components/           # ✅ Componenti UI
├── config/               # ✅ Configurazioni
├── database/             # ✅ Database e manager
└── utils/                # ✅ Utility
```

### 2. File Obbligatori
- **`app.py`**: Entry point dell'applicazione
- **`requirements.txt`**: Lista dipendenze Python
- **`.streamlit/config.toml`**: Configurazioni Streamlit

### 3. File Opzionali ma Consigliati
- **`README.md`**: Documentazione progetto
- **`.gitignore`**: Esclusione file sensibili
- **`LICENSE`**: Licenza del progetto

## 🚀 Deploy Step-by-Step

### Step 1: Preparazione Repository
```bash
# Assicurati che tutti i file siano committati
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy su Streamlit Cloud
1. **Vai su** [share.streamlit.io](https://share.streamlit.io)
2. **Clicca** "New app"
3. **Connetti** il tuo repository GitHub
4. **Configura** l'app:
   - **Repository**: `your-username/Dashboard_Gestione_CPA`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Python version**: `3.9`
5. **Clicca** "Deploy!"

### Step 3: Configurazione Post-Deploy
1. **Aspetta** che il deploy sia completato
2. **Vai su** la tua app deployata
3. **Configura** le credenziali utente
4. **Testa** tutte le funzionalità

## ⚙️ Configurazioni Avanzate

### 1. Configurazione Database
Per il deploy online, considera di usare un database esterno:
- **PostgreSQL**: Streamlit Cloud supporta connessioni esterne
- **MongoDB**: Database NoSQL per flessibilità
- **SQLite**: Solo per test e sviluppo

### 2. Variabili d'Ambiente
Configura in `.streamlit/secrets.toml`:
```toml
[secrets]
DATABASE_URL = "your-database-url"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secure-password"
```

### 3. Performance e Ottimizzazioni
- **Caching**: Usa `@st.cache_data` per dati statici
- **Lazy Loading**: Carica componenti solo quando servono
- **Database Indexing**: Ottimizza query frequenti

## 🔒 Sicurezza e Privacy

### 1. Credenziali
- **Non committare** mai password in chiaro
- **Usa** `.streamlit/secrets.toml` per credenziali
- **Rotazione** periodica delle password

### 2. Accesso
- **Limita** accesso solo a utenti autorizzati
- **Implementa** rate limiting per API
- **Monitora** accessi e attività sospette

### 3. Dati
- **Cripta** dati sensibili nel database
- **Backup** regolari dei dati
- **GDPR compliance** se applicabile

## 🐛 Troubleshooting

### Problemi Comuni

#### 1. App Non Si Avvia
```bash
# Verifica requirements.txt
pip install -r requirements.txt

# Controlla log Streamlit
streamlit run app.py --logger.level debug
```

#### 2. Errori di Database
```bash
# Verifica connessione database
python -c "from database.database import DatabaseManager; db = DatabaseManager(); print(db.test_connection())"

# Ricrea database se necessario
python -c "from database.database import DatabaseManager; DatabaseManager().init_database()"
```

#### 3. Problemi di Performance
- **Controlla** dimensioni database
- **Ottimizza** query frequenti
- **Implementa** caching dove possibile

### Log e Debug
- **Streamlit logs**: Terminal locale
- **Browser console**: F12 per errori JavaScript
- **Network tab**: Controlla chiamate API

## 📊 Monitoraggio e Manutenzione

### 1. Metriche da Monitorare
- **Uptime**: Disponibilità dell'app
- **Performance**: Tempo di risposta
- **Utilizzo**: Numero utenti attivi
- **Errori**: Rate di errori e crash

### 2. Manutenzione Regolare
- **Aggiornamenti**: Dipendenze e sicurezza
- **Backup**: Database e configurazioni
- **Pulizia**: Log e file temporanei
- **Testing**: Funzionalità critiche

### 3. Scaling
- **Database**: Migrazione a soluzioni enterprise
- **Caching**: Redis per performance
- **CDN**: Distribuzione contenuti statici
- **Load Balancing**: Per traffico elevato

## 🌐 Dominio Personalizzato

### 1. Configurazione DNS
1. **Vai su** le impostazioni della tua app Streamlit
2. **Configura** dominio personalizzato
3. **Aggiorna** record DNS del tuo provider
4. **Verifica** propagazione DNS

### 2. SSL e Sicurezza
- **HTTPS**: Automatico con Streamlit Cloud
- **Certificati**: Gestiti automaticamente
- **Headers**: Configurazione sicurezza personalizzabile

## 📱 Mobile e Responsive

### 1. Test Mobile
- **Chrome DevTools**: Simulazione dispositivi
- **Browser mobile**: Test su dispositivi reali
- **Performance**: Ottimizzazioni mobile-first

### 2. Responsive Design
- **Colonne**: Usa `st.columns` per layout adattivo
- **Container**: `st.container` per raggruppamenti
- **Sidebar**: `st.sidebar` per navigazione mobile

## 🔄 CI/CD e Automazione

### 1. GitHub Actions
```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Streamlit Cloud
        run: |
          # Script di deploy automatico
```

### 2. Testing Automatico
- **Unit tests**: Per componenti critici
- **Integration tests**: Per flussi completi
- **Performance tests**: Per benchmark

## 📚 Risorse Utili

### Documentazione
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Python Best Practices](https://docs.python-guide.org/)

### Community
- [Streamlit Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/streamlit)

---

**🚀 Pronto per il deploy! La tua app sarà online in pochi minuti.**
