# 🔗 Gestione Link Broker - Dashboard CPA

## 📋 Panoramica

La funzionalità **Gestione Link Broker** permette di gestire i link di affiliate per i broker nel sistema Dashboard CPA. Questa funzionalità è stata implementata seguendo la stessa logica del progetto DASH_GESTIONE_LEAD, utilizzando il database Supabase per la persistenza dei dati.

## 🚀 Funzionalità

### ✨ Caratteristiche Principali

- **📊 Statistiche in Tempo Reale**: Visualizza il numero totale di link, link attivi/inattivi e percentuali
- **➕ Gestione Completa**: Crea, modifica, elimina e attiva/disattiva link broker
- **🔍 Interfaccia Intuitiva**: Form user-friendly con validazione dei dati
- **🗑️ Eliminazione Multipla**: Possibilità di eliminare più link contemporaneamente
- **📋 Visualizzazione Tabellare**: Lista completa dei link con azioni rapide
- **🔗 Copia Link**: Funzione per copiare rapidamente i link di affiliate

### 🎯 Operazioni Supportate

1. **Creazione Link**: Aggiungi nuovi link broker con nome e URL affiliate
2. **Modifica Link**: Aggiorna nome broker, link affiliate e stato attivo/inattivo
3. **Eliminazione**: Rimuovi singoli link o elimina multipli selezionati
4. **Attivazione/Disattivazione**: Cambia lo stato dei link senza eliminarli
5. **Visualizzazione**: Consulta tutti i link con filtri per stato

## 🗄️ Struttura Database

### Tabella `broker_links`

```sql
CREATE TABLE broker_links (
    id SERIAL PRIMARY KEY,
    broker_name VARCHAR(255) NOT NULL,
    affiliate_link TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL
);
```

### Indici per Performance

- `idx_broker_links_broker_name`: Indice sul nome broker
- `idx_broker_links_is_active`: Indice sullo stato attivo/inattivo
- `idx_broker_links_created_at`: Indice sulla data di creazione
- `idx_broker_links_created_by`: Indice sull'utente creatore

### Sicurezza (RLS)

- **Politica Admin/Manager**: Accesso completo per amministratori e manager
- **Politica Lettura**: Tutti gli utenti autenticati possono leggere i link
- **Trigger Automatico**: Aggiornamento automatico del campo `updated_at`

## 📁 File Implementati

### Componenti Principali

1. **`components/broker_links_manager.py`**
   - Gestore principale per l'interfaccia utente
   - Metodi per rendering delle pagine e gestione form
   - Integrazione con SupabaseManager

2. **`supabase_manager.py`** (aggiornato)
   - Metodi per operazioni CRUD sui broker links
   - Gestione errori e validazione
   - Statistiche e reportistica

3. **`database/create_broker_links_table.sql`**
   - Script SQL per creazione tabella
   - Indici e politiche di sicurezza
   - Trigger per aggiornamenti automatici

4. **`create_broker_links_table.py`**
   - Script Python per eseguire la creazione della tabella
   - Test automatico della funzionalità
   - Validazione della configurazione Supabase

### Integrazione App

- **`app.py`** (aggiornato)
  - Aggiunta voce menu "🔗 Broker"
  - Inizializzazione BrokerLinksManager
  - Gestione routing alla sezione broker

- **`locales/it.json`** (aggiornato)
  - Traduzioni per il menu broker
  - Supporto multilingua

## 🛠️ Installazione e Configurazione

### 1. Creazione Tabella Database

```bash
# Esegui lo script di creazione tabella
python create_broker_links_table.py
```

### 2. Verifica Configurazione Supabase

Assicurati che le variabili ambiente siano configurate:

```bash
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-anon-key"
```

### 3. Avvio Applicazione

```bash
# Avvia il dashboard
streamlit run app.py
```

## 🎮 Utilizzo

### Accesso alla Sezione Broker

1. Avvia il dashboard CPA
2. Seleziona la voce "🔗 Broker" dal menu principale
3. La pagina si caricherà con le statistiche e la lista dei link

### Operazioni Base

#### ➕ Aggiungere Nuovo Link

1. Clicca su "➕ Nuovo Link Broker"
2. Compila il form:
   - **Nome Broker**: Nome del broker (es. eToro, Plus500)
   - **Link Affiliate**: URL completo del link di affiliate
   - **Link Attivo**: Checkbox per attivare/disattivare
3. Clicca "💾 Salva Link"

#### ✏️ Modificare Link Esistente

1. Seleziona un link dalla lista
2. Clicca "✏️ Modifica"
3. Modifica i campi necessari
4. Clicca "💾 Salva Link"

#### 🗑️ Eliminare Link

**Singolo:**
1. Seleziona il link da eliminare
2. Clicca "🗑️ Elimina"
3. Conferma l'eliminazione

**Multipli:**
1. Clicca "🗑️ Elimina Multipli"
2. Seleziona i link da eliminare
3. Clicca "🗑️ Elimina Selezionati"

#### 🔄 Attivare/Disattivare Link

1. Seleziona il link
2. Clicca "🔄 Attiva" o "🔄 Disattiva"
3. Lo stato viene aggiornato immediatamente

## 📊 Statistiche Disponibili

- **Totale Link**: Numero complessivo di link broker
- **Link Attivi**: Link attualmente attivi
- **Link Inattivi**: Link disattivati
- **Percentuale Attivi**: Percentuale di link attivi sul totale

## 🔒 Sicurezza

### Controlli di Accesso

- Solo utenti autenticati possono accedere ai link broker
- Amministratori e manager hanno accesso completo (CRUD)
- Altri utenti hanno accesso in sola lettura

### Validazione Dati

- Nome broker obbligatorio
- Link affiliate obbligatorio e validato
- Protezione contro SQL injection tramite Supabase
- Validazione URL per link affiliate

## 🐛 Troubleshooting

### Problemi Comuni

1. **Errore "Supabase non configurato"**
   - Verifica le variabili ambiente SUPABASE_URL e SUPABASE_KEY
   - Controlla la connessione internet

2. **Tabella broker_links non esiste**
   - Esegui `python create_broker_links_table.py`
   - Verifica i permessi del database

3. **Errore durante operazioni CRUD**
   - Controlla i log di Supabase
   - Verifica le politiche RLS
   - Assicurati di essere autenticato

### Log e Debug

I log sono disponibili nella console dell'applicazione e includono:
- Operazioni di creazione/modifica/eliminazione
- Errori di connessione Supabase
- Validazione dei dati

## 🔄 Aggiornamenti Futuri

### Funzionalità Pianificate

- **📈 Analytics Avanzate**: Grafici per performance dei link
- **🔗 Short URL**: Generazione di URL corti per i link
- **📊 Reportistica**: Export dei dati in CSV/Excel
- **🔔 Notifiche**: Alert per link scaduti o problematici
- **🏷️ Categorizzazione**: Tag e categorie per i broker
- **📱 API REST**: Endpoint per integrazioni esterne

### Miglioramenti Tecnici

- Cache locale per performance
- Paginazione per grandi volumi di dati
- Ricerca avanzata e filtri
- Backup automatico dei dati

## 📞 Supporto

Per problemi o domande relative alla funzionalità Broker Links:

1. Controlla questo README
2. Verifica i log dell'applicazione
3. Controlla la configurazione Supabase
4. Contatta il team di sviluppo

---

**Creato da Ezio Camporeale**  
**Versione**: 1.0.0  
**Data**: $(date)  
**Compatibilità**: Dashboard CPA v1.0+
