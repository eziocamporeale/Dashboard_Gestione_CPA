# ☁️ Supabase Integration - Dashboard CPA

## 📋 Descrizione
Integrazione con Supabase per database remoto PostgreSQL della Dashboard CPA.

## ✨ Caratteristiche
- **☁️ Database Remoto** - PostgreSQL su Supabase
- **🔄 Sincronizzazione** - Dati locali ↔ Supabase
- **🔐 Sicurezza** - Row Level Security (RLS)
- **📊 Scalabilità** - Database professionale

## 🚀 Avvio
```bash
cd progetti/supabase_integration
python test_supabase.py
```

## 🌐 Accesso
- **Supabase Dashboard:** https://supabase.com
- **Database:** PostgreSQL remoto
- **API:** REST e GraphQL

## 📊 Schema Database
- **`clienti`** - Tabella clienti
- **`incroci`** - Tabella incroci
- **`incroci_account`** - Tabella account incroci
- **`incroci_bonus`** - Tabella bonus

## 🔧 Configurazione
1. **Crea progetto Supabase**
2. **Configura variabili ambiente:**
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key
   ```
3. **Esegui test connessione**

## ⚠️ Note
- Richiede account Supabase
- Configurazione API keys necessaria
- Sincronizzazione manuale implementata
