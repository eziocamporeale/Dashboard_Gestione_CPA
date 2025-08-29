#!/usr/bin/env python3
"""
Configurazione per Dashboard CPA - PROGETTO SVILUPPO
Impostazioni specifiche per test e sviluppo
"""

import os

# ===== CONFIGURAZIONE PROGETTO DEV =====

# Nome progetto
PROJECT_NAME = "Dashboard CPA - PROGETTO SVILUPPO"
PROJECT_VERSION = "DEV-1.0.0"

# Porta separata per evitare conflitti
DEV_PORT = 8506

# Database locale (separato dal progetto stabile)
DEV_DATABASE = "cpa_database_dev.db"

# Cartella per log di sviluppo
DEV_LOGS_DIR = "logs_dev"

# ===== IMPOSTAZIONI SVILUPPO =====

# Modalità sviluppo
DEBUG_MODE = True

# Logging dettagliato
VERBOSE_LOGGING = True

# Test mode
TEST_MODE = True

# ===== SCHEMA RAGGRUPPATO =====

# Abilita schema raggruppato
ENABLE_GROUPED_SCHEMA = True

# Tabelle nuove
NEW_TABLES = [
    "clienti_base",
    "account_broker"
]

# Tabelle esistenti da mantenere
EXISTING_TABLES = [
    "clienti",
    "incroci",
    "incroci_account",
    "incroci_bonus"
]

# ===== FUNZIONALITÀ NUOVE =====

# Broker predefiniti
ENABLE_PREDEFINED_BROKERS = True

# Form semplificato
ENABLE_SIMPLIFIED_FORMS = True

# Interfaccia migliorata
ENABLE_IMPROVED_UI = True

# ===== MIGRAZIONE DATI =====

# Abilita migrazione automatica
ENABLE_AUTO_MIGRATION = False

# Backup prima migrazione
CREATE_BACKUP_BEFORE_MIGRATION = True

# ===== SICUREZZA =====

# RLS per progetto DEV
ENABLE_RLS_DEV = False  # Disabilitato per sviluppo

# Test connessione Supabase
TEST_SUPABASE_CONNECTION = True

# ===== UTILITY =====

def get_dev_config():
    """Restituisce configurazione progetto DEV"""
    return {
        "project_name": PROJECT_NAME,
        "project_version": PROJECT_VERSION,
        "dev_port": DEV_PORT,
        "dev_database": DEV_DATABASE,
        "debug_mode": DEBUG_MODE,
        "enable_grouped_schema": ENABLE_GROUPED_SCHEMA,
        "enable_rls": ENABLE_RLS_DEV
    }

def print_dev_info():
    """Stampa informazioni progetto DEV"""
    print("🧪 PROGETTO SVILUPPO CONFIGURATO")
    print("=" * 50)
    print(f"📋 Nome: {PROJECT_NAME}")
    print(f"🔄 Versione: {PROJECT_VERSION}")
    print(f"🌐 Porta: {DEV_PORT}")
    print(f"🗄️ Database: {DEV_DATABASE}")
    print(f"🔧 Debug: {DEBUG_MODE}")
    print(f"📊 Schema Raggruppato: {ENABLE_GROUPED_SCHEMA}")
    print(f"🛡️ RLS: {ENABLE_RLS_DEV}")
    print("=" * 50)

if __name__ == "__main__":
    print_dev_info()
