# 📁 Setup Storage - Dashboard Gestione CPA

## 🎯 Panoramica

Sistema di storage completo per il Dashboard Gestione CPA che permette di gestire file relativi al trading, EA, backtest, documenti broker e altro materiale CPA.

## ⚡ Setup Rapido (5 minuti)

### 1. Crea le Tabelle nel Database Supabase

1. Vai su: https://supabase.com/dashboard
2. Seleziona il tuo progetto Dashboard Gestione CPA
3. Clicca su "SQL Editor" (icona `</>`)
4. Clicca "New Query"
5. **Copia e incolla tutto il contenuto del file `create_storage_tables.sql`**
6. Clicca "Run"

### 2. Verifica il Setup

```bash
python3 test_storage_setup.py
```

### 3. Avvia l'App

```bash
streamlit run app.py
```

### 4. Testa la Funzionalità

1. Fai login come **Admin** (role = 'admin' o is_admin = true)
2. Vai alla sezione **📁 Storage**
3. Carica un file di test
4. Fai logout e login come utente normale
5. Verifica che puoi scaricare il file

## ✅ Funzionalità Disponibili

### Per Admin (role = 'admin' o is_admin = true):
- ⬆️ **Upload Multiplo**: Carica fino a 10 file contemporaneamente
- 🏷️ **Categorizzazione**: Assegna categorie automatiche specifiche per CPA
- 📝 **Descrizioni**: Aggiungi note ai file
- 🗑️ **Gestione**: Elimina file esistenti
- 📊 **Statistiche**: Visualizza metriche dettagliate

### Per Tutti:
- 👀 **Visualizzazione**: Vedi tutti i file disponibili
- ⬇️ **Download**: Scarica singoli file
- 🔍 **Ricerca**: Cerca per nome file
- 🏷️ **Filtri**: Filtra per categoria

## 🎯 Categorie Supportate (Specifiche CPA)

- **📊 EA Trading**: File .ex4, .ex5, .mq4, .mq5 per Expert Advisor
- **📈 Backtest**: Risultati backtest, report, grafici
- **🏢 Documenti Broker**: Contratti, accordi, certificati
- **📋 Report CPA**: Report mensili, trimestrali, annuali
- **⚖️ Documenti Legali**: Contratti clienti, privacy policy, termini
- **🎬 Materiale Marketing**: Video, presentazioni, brochure
- **📊 Analisi**: Grafici, studi di mercato, ricerche
- **📦 Archivi**: Backup, pacchetti completi
- **📊 Fogli di Calcolo**: XLS, XLSX, CSV, ODS
- **📽️ Presentazioni**: PPT, PPTX, ODP
- **🖼️ Immagini**: JPG, PNG, GIF, BMP, SVG, WEBP
- **🎥 Video**: MP4, AVI, MOV, WMV, FLV, WEBM
- **🎵 Audio**: MP3, WAV, FLAC, AAC, OGG
- **📄 Altro**: File generici

## 🔧 Struttura Tecnica

### Directory
```
Dashboard_Gestione_CPA/
├── components/
│   └── storage/
│       ├── __init__.py
│       ├── storage_manager.py
│       └── storage_ui.py
├── storage/
│   ├── uploads/          # File caricati
│   └── temp/            # File temporanei
├── create_storage_tables.sql
└── test_storage_setup.py
```

### Database (Supabase)
- **storage_files**: Tabella principale per i file
- **storage_downloads**: Tabella per tracciare i download
- **RLS**: Row Level Security per controlli di accesso

## 🐛 Risoluzione Problemi

### "Tabelle non trovate"
- Esegui il codice SQL in `create_storage_tables.sql`
- Verifica che tutte le query siano state eseguite senza errori

### "Permission denied"
- Assicurati di essere loggato come Admin (role = 'admin' o is_admin = true)
- Verifica che le policy RLS siano state create correttamente

### "File non caricato"
- Controlla che la directory `storage/uploads/` esista
- Verifica i permessi di scrittura

### "Errore connessione database"
- Verifica le credenziali Supabase in `supabase_manager.py`
- Controlla che il progetto Supabase sia attivo

## 📊 Esempi di Utilizzo

### Caricamento File EA
1. Vai su **📁 Storage** → **⬆️ Carica File**
2. Seleziona file .ex4/.ex5
3. Categoria: "EA Trading" (automatica)
4. Aggiungi descrizione: "Gold Supreme EA v2.0"

### Caricamento Report CPA
1. Seleziona file PDF/XLSX
2. Categoria: "Report CPA" (automatica)
3. Descrizione: "Report mensile Gennaio 2024"

### Caricamento Documenti Broker
1. Seleziona file PDF
2. Categoria: "Documenti Broker" (automatica)
3. Descrizione: "Contratto con Broker XYZ"

## 🔒 Sicurezza

- **RLS Attivo**: Controlli di accesso a livello database
- **Permessi Differenziati**: Solo Admin può caricare/eliminare
- **Validazione File**: Controllo tipo e dimensione
- **Hash MD5**: Verifica integrità file
- **Soft Delete**: File eliminati ma tracciabili

## 📈 Statistiche Disponibili

- **File Totali**: Numero complessivo di file
- **Spazio Utilizzato**: Dimensione totale in MB/GB
- **Per Categoria**: Distribuzione file per tipo
- **Download Count**: Numero di download per file
- **Grafici**: Visualizzazioni interattive (se Plotly disponibile)

## 🚀 Prossimi Sviluppi

- [ ] Integrazione con sistema di notifiche
- [ ] Versioning dei file
- [ ] Backup automatico
- [ ] Integrazione con AI Assistant per analisi file
- [ ] API REST per accesso esterno

## 📞 Supporto

Se hai problemi:
1. Controlla i log di Supabase nel dashboard
2. Esegui il test: `python3 test_storage_setup.py`
3. Verifica che l'utente abbia i permessi corretti
4. Controlla che le tabelle siano state create correttamente

---

**🎉 Una volta completato il setup, la sezione Storage sarà completamente funzionale per gestire tutti i file del tuo business CPA!**
