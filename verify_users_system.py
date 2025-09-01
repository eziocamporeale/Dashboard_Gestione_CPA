#!/usr/bin/env python3
"""
🔍 VERIFICA SISTEMA GESTIONE UTENTI IN SUPABASE
Script per verificare che tutte le tabelle e funzionalità siano state create correttamente
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

def verify_users_system():
    """Verifica che il sistema di gestione utenti sia completo e funzionante"""
    
    print("🔍 VERIFICA SISTEMA GESTIONE UTENTI IN SUPABASE...\n")
    
    # Inizializza Supabase Manager
    supabase_manager = SupabaseManager()
    
    # Test connessione
    print("📡 TEST CONNESSIONE SUPABASE...")
    connection_ok, message = supabase_manager.test_connection()
    print(f"   {message}")
    
    if not connection_ok:
        print("❌ Impossibile continuare - Connessione Supabase fallita")
        return False
    
    print("\n🔍 VERIFICA TABELLE SISTEMA UTENTI...")
    
    # Lista tabelle da verificare
    expected_tables = [
        'users', 'user_roles', 'user_permissions', 'user_sessions', 
        'user_profiles', 'user_access_logs', 'failed_login_attempts'
    ]
    
    created_tables = []
    missing_tables = []
    
    for table in expected_tables:
        try:
            print(f"   🔍 Verifica tabella '{table}'...")
            response = supabase_manager.supabase.table(table).select('count', count='exact').execute()
            created_tables.append(table)
            print(f"      ✅ Tabella '{table}' - PRESENTE")
            
            # Conta i record
            count = response.count if hasattr(response, 'count') else 'N/A'
            print(f"         📊 Record presenti: {count}")
            
        except Exception as e:
            missing_tables.append(table)
            print(f"      ❌ Tabella '{table}' - MANCANTE")
            print(f"         🔍 Errore: {e}")
    
    print(f"\n📊 VERIFICA TABELLE COMPLETATA:")
    print(f"   Tabelle presenti: {len(created_tables)}/{len(expected_tables)}")
    
    if missing_tables:
        print(f"   ❌ Tabelle mancanti: {', '.join(missing_tables)}")
        return False
    else:
        print(f"   🎉 Tutte le tabelle sono presenti!")
    
    # Verifica dati di default
    print(f"\n🔍 VERIFICA DATI DI DEFAULT...")
    
    # 1. Verifica utente admin
    try:
        print(f"   🔍 Verifica utente admin...")
        response = supabase_manager.supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if response.data:
            admin_user = response.data[0]
            print(f"      ✅ Utente admin trovato:")
            print(f"         👤 Username: {admin_user.get('username')}")
            print(f"         📧 Email: {admin_user.get('email')}")
            print(f"         🏷️ Ruolo: {admin_user.get('role')}")
            print(f"         ✅ Attivo: {admin_user.get('is_active')}")
        else:
            print(f"      ❌ Utente admin non trovato")
            return False
            
    except Exception as e:
        print(f"      ❌ Errore verifica utente admin: {e}")
        return False
    
    # 2. Verifica ruoli
    try:
        print(f"   🔍 Verifica ruoli predefiniti...")
        response = supabase_manager.supabase.table('user_roles').select('*').execute()
        
        if response.data:
            print(f"      ✅ Ruoli trovati: {len(response.data)}")
            for role in response.data:
                print(f"         🏷️ {role.get('role_name')}: {role.get('description')}")
        else:
            print(f"      ❌ Nessun ruolo trovato")
            return False
            
    except Exception as e:
        print(f"      ❌ Errore verifica ruoli: {e}")
        return False
    
    # 3. Verifica permessi
    try:
        print(f"   🔍 Verifica permessi base...")
        response = supabase_manager.supabase.table('user_permissions').select('*').execute()
        
        if response.data:
            print(f"      ✅ Permessi trovati: {len(response.data)}")
            for perm in response.data:
                print(f"         🔐 {perm.get('permission_name')}: {perm.get('description')}")
        else:
            print(f"      ❌ Nessun permesso trovato")
            return False
            
    except Exception as e:
        print(f"      ❌ Errore verifica permessi: {e}")
        return False
    
    # Test funzionalità
    print(f"\n🧪 TEST FUNZIONALITÀ SISTEMA...")
    
    # 1. Test inserimento utente
    try:
        print(f"   🧪 Test inserimento utente...")
        test_user_data = {
            'username': 'test_user_verify',
            'email': 'test_verify@example.com',
            'password_hash': '$2b$12$test_hash_verify',
            'full_name': 'Utente Test Verifica',
            'role': 'user',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = supabase_manager.supabase.table('users').insert(test_user_data).execute()
        print(f"      ✅ Test inserimento: SUCCESSO")
        
        # Rimuovi utente di test
        supabase_manager.supabase.table('users').delete().eq('username', 'test_user_verify').execute()
        print(f"      🧹 Utente di test rimosso")
        
    except Exception as e:
        print(f"      ❌ Test inserimento: FALLITO - {e}")
        return False
    
    # 2. Test query con filtri
    try:
        print(f"   🧪 Test query con filtri...")
        response = supabase_manager.supabase.table('users').select('username, role').eq('role', 'admin').execute()
        
        if response.data:
            print(f"      ✅ Test query: SUCCESSO - {len(response.data)} admin trovati")
        else:
            print(f"      ⚠️ Test query: Nessun admin trovato")
            
    except Exception as e:
        print(f"      ❌ Test query: FALLITO - {e}")
        return False
    
    print(f"\n🎉 VERIFICA COMPLETATA CON SUCCESSO!")
    print(f"   ✅ Tutte le tabelle sono presenti")
    print(f"   ✅ Dati di default sono stati inseriti")
    print(f"   ✅ Funzionalità di base funzionano")
    print(f"   🚀 Sistema pronto per l'uso!")
    
    return True

def main():
    """Funzione principale"""
    
    print("=" * 70)
    print("🔍 VERIFICA SISTEMA GESTIONE UTENTI - DASHBOARD CPA")
    print("=" * 70)
    
    try:
        success = verify_users_system()
        
        if success:
            print(f"\n🎊 VERIFICA COMPLETATA CON SUCCESSO!")
            print(f"   🔐 Sistema di autenticazione avanzato VERIFICATO")
            print(f"   👥 Gestione utenti multi-ruolo FUNZIONANTE")
            print(f"   🚀 Pronto per la prossima fase!")
        else:
            print(f"\n❌ VERIFICA FALLITA")
            print(f"   Controlla i log per identificare i problemi")
            print(f"   Potrebbe essere necessario rieseguire lo script SQL")
            
    except Exception as e:
        print(f"\n💥 ERRORE CRITICO: {e}")
        logger.error(f"Errore critico durante la verifica: {e}")
        return False
    
    print(f"\n" + "=" * 70)
    return True

if __name__ == "__main__":
    main()
