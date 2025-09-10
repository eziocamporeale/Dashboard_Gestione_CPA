# 🔐 REPORT COMPLETO UTENTI DATABASE SUPABASE

**Data Generazione**: 08/09/2025 14:06:01  
**Progetti Analizzati**: 3  
**Utenti Totali Trovati**: 4  

---

## 📊 RIEPILOGO GENERALE

| Progetto | Database URL | Utenti | Stato |
|----------|--------------|--------|-------|
| **DASH_GESTIONE_LEAD** | `xjjmpurdjqwjomxmqqks.supabase.co` | 4 | ✅ Attivo |
| **Dashboard_Gestione_CPA** | Configurato via env vars | ? | ⚠️ Non configurato |
| **DASH_OSINT_STREAMLIT** | `kgmfztsceatiioaevytg.supabase.co` | 0 | ✅ Attivo (vuoto) |

---

## 🎯 DASH_GESTIONE_LEAD - DATI COMPLETI

**Database**: `xjjmpurdjqwjomxmqqks.supabase.co`  
**Tabelle**: `users` (4 record), `roles` (2 record)  
**Record Totali**: 6  

### 👥 UTENTI IDENTIFICATI (4)

#### 1. 👤 **admin** (Amministratore)
- **ID**: 1
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Nome Completo**: Admin User
- **Telefono**: N/A
- **Ruolo**: Admin (role_id: 1)
- **Stato**: ✅ Attivo
- **Admin**: 👑 Sì
- **Password Hash**: `$2b$12$Fu7hvLj6Wi6vE41MWIKP..AsvmPh55KkTRpcw.KzST/Mnxa682bcC`
- **Ultimo Login**: 08/09/2025 13:46:32
- **Creato**: 03/09/2025 10:26:34
- **Dipartimento**: N/A

#### 2. 👤 **simone** (Seller)
- **ID**: 10
- **Username**: `simone`
- **Email**: `simoneserio022@gmail.com`
- **Nome Completo**: Simone Serio
- **Telefono**: 603103061
- **Ruolo**: User (role_id: 2)
- **Stato**: ✅ Attivo
- **Admin**: 👤 No
- **Password Hash**: `$2b$12$PcOO3ar23w6TzyjUWts32uGOAtEmQmKOLTlkePMahmnkKVqigGKyC`
- **Ultimo Login**: 08/09/2025 10:23:56
- **Creato**: 04/09/2025 08:31:44
- **Dipartimento**: 1
- **Note**: "seller"

#### 3. 👤 **marco** (User)
- **ID**: 11
- **Username**: `marco`
- **Email**: `marcoamatobsn@gmail.com`
- **Nome Completo**: marco amato
- **Telefono**: 3500850900
- **Ruolo**: User (role_id: 2)
- **Stato**: ✅ Attivo
- **Admin**: 👤 No
- **Password Hash**: `$2b$12$/80AIP1jhNlVtN11i3mcKe0.2vd9AJcooxSOpGipppX.fHUQ0Rtgq`
- **Ultimo Login**: 08/09/2025 12:42:05
- **Creato**: 04/09/2025 10:37:05
- **Dipartimento**: 4
- **Note**: "marco amato"

#### 4. 👤 **jack** (User)
- **ID**: 12
- **Username**: `jack`
- **Email**: `jack.rmn@hotmail.it`
- **Nome Completo**: Giacomo Romano
- **Telefono**: +39 33333333
- **Ruolo**: User (role_id: 2)
- **Stato**: ✅ Attivo
- **Admin**: 👤 No
- **Password Hash**: `giacomo123` ⚠️ **PASSWORD IN CHIARO!**
- **Ultimo Login**: Mai effettuato
- **Creato**: 07/09/2025 01:11:35
- **Dipartimento**: 4
- **Note**: N/A

---

## 💰 Dashboard_Gestione_CPA - STATO

**Database**: Configurato tramite variabili ambiente  
**Stato**: ⚠️ **NON CONFIGURATO**  
**Motivo**: Le variabili ambiente `SUPABASE_URL` e `SUPABASE_KEY` non sono configurate  

### 🔧 Per Configurare il Database CPA:
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### 📋 Dati Utenti Attesi (dalla documentazione):
- **Username**: `admin`
- **Password**: `admin` (semplice)
- **Email**: `admin@cpadashboard.com`
- **Nome**: `Amministratore CPA Dashboard`
- **Ruolo**: `admin`

---

## 🕵️ DASH_OSINT_STREAMLIT - STATO

**Database**: `kgmfztsceatiioaevytg.supabase.co`  
**Tabelle**: `users` (0 record), `user_sessions` (0 record)  
**Stato**: ✅ **ATTIVO MA VUOTO**  

### 📋 Nessun Utente Trovato
Il database OSINT è configurato correttamente ma non contiene utenti.  
Per creare l'utente admin, eseguire lo script SQL documentato:

```sql
INSERT INTO users (
    username, email, password_hash, role, is_active, created_at, updated_at
) VALUES (
    'admin', 'admin@osint.local', 
    '09526266bdae1f9755144e4f10744489:9d2934120a33dd46fe1640d10ba7edeaa2c9986ab26b4a1a0b7a4c4621aa50ff',
    'Admin', true, NOW(), NOW()
);
```

### 🔐 Credenziali Attese:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@osint.local`

---

## 🚨 PROBLEMI DI SICUREZZA IDENTIFICATI

### ⚠️ **CRITICO**: Password in Chiaro
- **Utente**: `jack` (DASH_GESTIONE_LEAD)
- **Password**: `giacomo123` (non hashata)
- **Raccomandazione**: Cambiare immediatamente la password

### ⚠️ **MEDIO**: Password Semplice
- **Progetto**: Dashboard_Gestione_CPA
- **Password**: `admin` (troppo semplice)
- **Raccomandazione**: Usare password più complessa

---

## 📊 STATISTICHE DETTAGLIATE

### 👥 Distribuzione Utenti per Ruolo
- **Admin**: 1 utente (25%)
- **User**: 3 utenti (75%)

### 📅 Attività Recente
- **Ultimo Login**: 08/09/2025 13:46:32 (admin)
- **Utenti Attivi**: 4/4 (100%)
- **Utenti Mai Loggati**: 1 (jack)

### 📞 Informazioni di Contatto
- **Con Telefono**: 3/4 utenti (75%)
- **Con Email Valida**: 4/4 utenti (100%)

---

## 🔧 RACCOMANDAZIONI IMMEDIATE

### 1. **Sicurezza Password**
- [ ] Cambiare password di `jack` da `giacomo123` a hash sicuro
- [ ] Implementare policy password complesse
- [ ] Forzare cambio password al prossimo login

### 2. **Configurazione CPA**
- [ ] Configurare variabili ambiente per Dashboard_Gestione_CPA
- [ ] Verificare utenti nel database CPA
- [ ] Aggiornare password admin da `admin` a password sicura

### 3. **Database OSINT**
- [ ] Creare utente admin nel database OSINT
- [ ] Testare login con credenziali `admin`/`admin123`

### 4. **Monitoraggio**
- [ ] Implementare logging accessi
- [ ] Monitorare tentativi di login falliti
- [ ] Backup regolari dei dati utenti

---

## 📁 FILE GENERATI

- **Report JSON**: `supabase_users_report_20250908_140601.json`
- **Export Excel**: `supabase_users_export_20250908_140601.xlsx`
- **Script Interrogazione**: `query_all_supabase_users.py`
- **Script CPA**: `query_cpa_database.py`

---

## 🎯 CONCLUSIONI

**✅ Database Interrogati**: 2/3 (DASH_GESTIONE_LEAD, DASH_OSINT_STREAMLIT)  
**⚠️ Database Non Configurato**: 1/3 (Dashboard_Gestione_CPA)  
**👥 Utenti Totali**: 4 utenti attivi  
**🚨 Problemi Sicurezza**: 1 password in chiaro identificata  

Il sistema DASH_GESTIONE_LEAD è il più attivo con 4 utenti, mentre DASH_OSINT_STREAMLIT è configurato ma vuoto. Il progetto Dashboard_Gestione_CPA richiede configurazione delle variabili ambiente per essere interrogato.

---

*Report generato automaticamente il 08/09/2025 alle 14:06:01*
