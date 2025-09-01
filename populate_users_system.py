#!/usr/bin/env python3
"""
🚀 POPOLAMENTO SISTEMA GESTIONE UTENTI IN SUPABASE
Script per inserire i dati di default nelle tabelle del sistema utenti
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

def populate_users_system():
    """Popola il sistema di gestione utenti con i dati di default"""
    
    print("🚀 POPOLAMENTO SISTEMA GESTIONE UTENTI IN SUPABASE...\n")
    
    # Inizializza Supabase Manager
    supabase_manager = SupabaseManager()
    
    # Test connessione
    print("📡 TEST CONNESSIONE SUPABASE...")
    connection_ok, message = supabase_manager.test_connection()
    print(f"   {message}")
    
    if not connection_ok:
        print("❌ Impossibile continuare - Connessione Supabase fallita")
        return False
    
    print("\n🔧 INSERIMENTO DATI DI DEFAULT...")
    
    # 1. Inserisci ruoli predefiniti
    print(f"   🔧 Inserimento ruoli predefiniti...")
    user_roles_data = [
        {
            'role_name': 'admin',
            'description': 'Amministratore completo del sistema',
            'permissions': ['*'],
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'role_name': 'manager',
            'description': 'Manager con accesso esteso',
            'permissions': ['clienti:read', 'clienti:update', 'incroci:read', 'incroci:update'],
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'role_name': 'user',
            'description': 'Utente base con accesso limitato',
            'permissions': ['clienti:read', 'incroci:read'],
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
    ]
    
    success_roles = True
    for role_data in user_roles_data:
        try:
            response = supabase_manager.supabase.table('user_roles').insert(role_data).execute()
            print(f"      ✅ Ruolo '{role_data['role_name']}' inserito")
        except Exception as e:
            print(f"      ❌ Errore inserimento ruolo '{role_data['role_name']}': {e}")
            success_roles = False
    
    # 2. Inserisci permessi base
    print(f"   🔧 Inserimento permessi base...")
    user_permissions_data = [
        {
            'permission_name': 'clienti:create',
            'description': 'Creare nuovi clienti',
            'resource': 'clienti',
            'action': 'create',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'clienti:read',
            'description': 'Visualizzare clienti',
            'resource': 'clienti',
            'action': 'read',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'clienti:update',
            'description': 'Modificare clienti',
            'resource': 'clienti',
            'action': 'update',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'clienti:delete',
            'description': 'Eliminare clienti',
            'resource': 'clienti',
            'action': 'delete',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'incroci:create',
            'description': 'Creare nuovi incroci',
            'resource': 'incroci',
            'action': 'create',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'incroci:read',
            'description': 'Visualizzare incroci',
            'resource': 'incroci',
            'action': 'read',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'incroci:update',
            'description': 'Modificare incroci',
            'resource': 'incroci',
            'action': 'update',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'incroci:delete',
            'description': 'Eliminare incroci',
            'resource': 'incroci',
            'action': 'delete',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'users:create',
            'description': 'Creare nuovi utenti',
            'resource': 'users',
            'action': 'create',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'users:read',
            'description': 'Visualizzare utenti',
            'resource': 'users',
            'action': 'read',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'users:update',
            'description': 'Modificare utenti',
            'resource': 'users',
            'action': 'update',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'permission_name': 'users:delete',
            'description': 'Eliminare utenti',
            'resource': 'users',
            'action': 'delete',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
    ]
    
    success_permissions = True
    for perm_data in user_permissions_data:
        try:
            response = supabase_manager.supabase.table('user_permissions').insert(perm_data).execute()
            print(f"      ✅ Permesso '{perm_data['permission_name']}' inserito")
        except Exception as e:
            print(f"      ❌ Errore inserimento permesso '{perm_data['permission_name']}': {e}")
            success_permissions = False
    
    # 3. Inserisci utente admin
    print(f"   🔧 Inserimento utente admin...")
    admin_user_data = {
        'username': 'admin',
        'email': 'admin@cpadashboard.com',
        'password_hash': '$2b$12$riBfpHpVpccsb7NT7GFIRObLccRmnOiOtsSx65wbMb3C6Cuy/mDfu',
        'full_name': 'Amministratore CPA Dashboard',
        'role': 'admin',
        'is_active': True,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    try:
        response = supabase_manager.supabase.table('users').insert(admin_user_data).execute()
        print(f"      ✅ Utente admin inserito")
        success_admin = True
    except Exception as e:
        print(f"      ❌ Errore inserimento utente admin: {e}")
        success_admin = False
    
    # 4. Inserisci profilo admin
    if success_admin:
        print(f"   🔧 Inserimento profilo admin...")
        try:
            # Prima ottieni l'ID dell'utente admin
            response = supabase_manager.supabase.table('users').select('id').eq('username', 'admin').execute()
            if response.data:
                admin_id = response.data[0]['id']
                
                admin_profile_data = {
                    'user_id': admin_id,
                    'timezone': 'Europe/Rome',
                    'language': 'it',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                response = supabase_manager.supabase.table('user_profiles').insert(admin_profile_data).execute()
                print(f"      ✅ Profilo admin inserito")
                success_profile = True
            else:
                print(f"      ❌ ID utente admin non trovato")
                success_profile = False
                
        except Exception as e:
            print(f"      ❌ Errore inserimento profilo admin: {e}")
            success_profile = False
    else:
        success_profile = False
    
    # 5. Inserisci log di sistema
    print(f"   🔧 Inserimento log di sistema...")
    try:
        system_log_data = {
            'user_id': None,  # Sistema
            'action': 'system_populated',
            'success': True,
            'details': {'note': 'Sistema popolato automaticamente'},
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase_manager.supabase.table('user_access_logs').insert(system_log_data).execute()
        print(f"      ✅ Log di sistema inserito")
        success_log = True
        
    except Exception as e:
        print(f"      ❌ Errore inserimento log di sistema: {e}")
        success_log = False
    
    # Riepilogo
    print(f"\n📊 RIEPILOGO POPOLAMENTO:")
    print(f"   ✅ Ruoli: {'OK' if success_roles else 'KO'}")
    print(f"   ✅ Permessi: {'OK' if success_permissions else 'KO'}")
    print(f"   ✅ Utente admin: {'OK' if success_admin else 'KO'}")
    print(f"   ✅ Profilo admin: {'OK' if success_profile else 'KO'}")
    print(f"   ✅ Log di sistema: {'OK' if success_log else 'KO'}")
    
    if success_roles and success_permissions and success_admin and success_profile:
        print(f"\n🎉 SISTEMA POPOLATO CON SUCCESSO!")
        print(f"   👑 Utente admin: admin/admin123")
        print(f"   🏷️ Ruoli: admin, manager, user")
        print(f"   🔐 Permessi: 12 permessi base")
        print(f"   🚀 Sistema pronto per l'uso!")
        return True
    else:
        print(f"\n❌ POPOLAMENTO PARZIALMENTE FALLITO")
        print(f"   Controlla i log per identificare i problemi")
        return False

def main():
    """Funzione principale"""
    
    print("=" * 70)
    print("🚀 POPOLAMENTO SISTEMA GESTIONE UTENTI - DASHBOARD CPA")
    print("=" * 70)
    
    try:
        success = populate_users_system()
        
        if success:
            print(f"\n🎊 POPOLAMENTO COMPLETATO CON SUCCESSO!")
            print(f"   🔐 Sistema di autenticazione popolato")
            print(f"   👥 Gestione utenti multi-ruolo attiva")
            print(f"   🚀 Pronto per la prossima fase!")
        else:
            print(f"\n❌ POPOLAMENTO FALLITO")
            print(f"   Controlla i log per identificare i problemi")
            
    except Exception as e:
        print(f"\n💥 ERRORE CRITICO: {e}")
        logger.error(f"Errore critico durante il popolamento: {e}")
        return False
    
    print(f"\n" + "=" * 70)
    return True

if __name__ == "__main__":
    main()
