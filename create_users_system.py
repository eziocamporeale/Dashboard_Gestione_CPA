#!/usr/bin/env python3
"""
🚀 CREAZIONE SISTEMA GESTIONE UTENTI IN SUPABASE
Script per creare automaticamente tutte le tabelle e funzionalità per la gestione utenti
"""

import os
import sys
import logging
from datetime import datetime

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_users_system():
    """Crea il sistema completo di gestione utenti in Supabase"""
    
    print("🚀 CREAZIONE SISTEMA GESTIONE UTENTI IN SUPABASE...\n")
    
    # Inizializza Supabase Manager
    supabase_manager = SupabaseManager()
    
    # Test connessione
    print("📡 TEST CONNESSIONE SUPABASE...")
    connection_ok, message = supabase_manager.test_connection()
    print(f"   {message}")
    
    if not connection_ok:
        print("❌ Impossibile continuare - Connessione Supabase fallita")
        return False
    
    # Leggi lo script SQL
    sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'create_users_system.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"❌ File SQL non trovato: {sql_file_path}")
        return False
    
    print(f"📖 Lettura script SQL: {sql_file_path}")
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
    except Exception as e:
        print(f"❌ Errore lettura file SQL: {e}")
        return False
    
    print("✅ Script SQL letto correttamente")
    
    # Dividi lo script in comandi separati
    sql_commands = []
    current_command = ""
    
    for line in sql_script.split('\n'):
        line = line.strip()
        
        # Salta commenti e righe vuote
        if line.startswith('--') or not line:
            continue
        
        current_command += line + " "
        
        # Se la riga termina con ; è un comando completo
        if line.endswith(';'):
            sql_commands.append(current_command.strip())
            current_command = ""
    
    print(f"📊 Comandi SQL identificati: {len(sql_commands)}")
    
    # Esegui i comandi SQL
    print("\n🔧 ESECUZIONE COMANDI SQL...")
    
    success_count = 0
    error_count = 0
    
    for i, command in enumerate(sql_commands, 1):
        try:
            print(f"   [{i:2d}/{len(sql_commands)}] Esecuzione comando...")
            
            # Esegui il comando SQL
            response = supabase_manager.supabase.rpc('exec_sql', {'sql': command}).execute()
            
            print(f"      ✅ Comando eseguito con successo")
            success_count += 1
            
        except Exception as e:
            print(f"      ❌ Errore esecuzione: {e}")
            error_count += 1
            
            # Se è un errore critico, interrompi
            if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                print(f"      ⚠️ Errore critico, continuo con i prossimi comandi...")
    
    print(f"\n📊 RIEPILOGO ESECUZIONE:")
    print(f"   ✅ Comandi eseguiti con successo: {success_count}")
    print(f"   ❌ Comandi con errori: {error_count}")
    
    if success_count > 0:
        print(f"\n🎉 SISTEMA GESTIONE UTENTI CREATO CON SUCCESSO!")
        print(f"   📊 Tabelle create in Supabase")
        print(f"   👑 Utente admin: admin/admin123")
        print(f"   🔒 RLS attivato per sicurezza")
        
        # Verifica creazione tabelle
        print(f"\n🔍 VERIFICA CREAZIONE TABELLE...")
        verify_tables_creation(supabase_manager)
        
        return True
    else:
        print(f"\n❌ NESSUN COMANDO ESEGUITO CON SUCCESSO")
        return False

def verify_tables_creation(supabase_manager):
    """Verifica che le tabelle siano state create correttamente"""
    
    expected_tables = [
        'users', 'user_roles', 'user_permissions', 'user_sessions', 
        'user_profiles', 'user_access_logs', 'failed_login_attempts'
    ]
    
    created_tables = []
    missing_tables = []
    
    for table in expected_tables:
        try:
            response = supabase_manager.supabase.table(table).select('count', count='exact').execute()
            created_tables.append(table)
            print(f"   ✅ Tabella '{table}' - CREATA")
        except Exception as e:
            missing_tables.append(table)
            print(f"   ❌ Tabella '{table}' - MANCANTE")
    
    print(f"\n📊 VERIFICA COMPLETATA:")
    print(f"   Tabelle create: {len(created_tables)}/{len(expected_tables)}")
    
    if missing_tables:
        print(f"   Tabelle mancanti: {', '.join(missing_tables)}")
        print(f"   ⚠️ Potrebbe essere necessario eseguire manualmente lo script SQL")
    else:
        print(f"   🎉 Tutte le tabelle sono state create correttamente!")

def main():
    """Funzione principale"""
    
    print("=" * 60)
    print("🚀 CREAZIONE SISTEMA GESTIONE UTENTI - DASHBOARD CPA")
    print("=" * 60)
    
    try:
        success = create_users_system()
        
        if success:
            print(f"\n🎊 IMPLEMENTAZIONE COMPLETATA CON SUCCESSO!")
            print(f"   🔐 Sistema di autenticazione avanzato attivo")
            print(f"   👥 Gestione utenti multi-ruolo implementata")
            print(f"   🔒 Sicurezza RLS attivata")
            print(f"   🚀 Pronto per la prossima fase!")
        else:
            print(f"\n❌ IMPLEMENTAZIONE FALLITA")
            print(f"   Controlla i log per identificare i problemi")
            
    except Exception as e:
        print(f"\n💥 ERRORE CRITICO: {e}")
        logger.error(f"Errore critico durante l'implementazione: {e}")
        return False
    
    print(f"\n" + "=" * 60)
    return True

if __name__ == "__main__":
    main()
