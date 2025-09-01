#!/usr/bin/env python3
"""
🔧 RIPRISTINO UTENTE ADMIN - Dashboard CPA (VERSIONE TERMINALE)
Script per inserire utente admin e dati necessari nel database Supabase
"""

import sys
import os
import uuid
from datetime import datetime

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

def print_log(message, level="INFO"):
    """Stampa log formattato su terminale"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def restore_admin_user():
    """Ripristina l'utente admin e tutti i dati necessari"""
    
    print_log("🔧 RIPRISTINO UTENTE ADMIN INIZIATO", "START")
    print_log("=" * 60)
    
    try:
        # Inizializza Supabase
        print_log("🔌 Connessione a Supabase...")
        supabase_manager = SupabaseManager()
        print_log("✅ Connessione Supabase stabilita")
        
        # 1. VERIFICA STRUTTURA TABELLE
        print_log("🔍 Verifica struttura tabelle...")
        
        # Conta record esistenti
        try:
            users_count = supabase_manager.supabase.table('users').select('count', count='exact').execute()
            print_log(f"📊 Tabella 'users': {users_count.count if hasattr(users_count, 'count') else 'N/A'} record")
        except Exception as e:
            print_log(f"❌ Errore conteggio users: {e}", "ERROR")
        
        try:
            profiles_count = supabase_manager.supabase.table('user_profiles').select('count', count='exact').execute()
            print_log(f"📊 Tabella 'user_profiles': {profiles_count.count if hasattr(profiles_count, 'count') else 'N/A'} record")
        except Exception as e:
            print_log(f"❌ Errore conteggio user_profiles: {e}", "ERROR")
        
        # 2. INSERIMENTO RUOLI (se tabella esiste)
        print_log("👑 Inserimento ruoli...")
        
        # Verifica se la tabella user_roles esiste
        try:
            roles_test = supabase_manager.supabase.table('user_roles').select('*').limit(1).execute()
            print_log("✅ Tabella 'user_roles' trovata")
            
            # Inserisci ruoli con UUID validi
            roles_data = [
                {
                    'id': str(uuid.uuid4()),
                    'role_name': 'admin',  # Cambiato da 'name' a 'role_name'
                    'description': 'Accesso completo al sistema',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': str(uuid.uuid4()),
                    'role_name': 'manager',  # Cambiato da 'name' a 'role_name'
                    'description': 'Gestione clienti e incroci',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': str(uuid.uuid4()),
                    'role_name': 'user',  # Cambiato da 'name' a 'user'
                    'description': 'Accesso limitato',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                }
            ]
            
            for role in roles_data:
                try:
                    response = supabase_manager.supabase.table('user_roles').insert(role).execute()
                    if response.data:
                        print_log(f"✅ Ruolo '{role['role_name']}' inserito con ID: {role['id']}")
                    else:
                        print_log(f"⚠️ Ruolo '{role['role_name']}' non inserito (già esistente?)")
                except Exception as e:
                    print_log(f"❌ Errore inserimento ruolo '{role['role_name']}': {e}", "ERROR")
                    
        except Exception as e:
            print_log(f"⚠️ Tabella 'user_roles' non trovata o non accessibile: {e}", "WARN")
        
        # 3. INSERIMENTO PERMESSI (se tabella esiste)
        print_log("🔐 Inserimento permessi...")
        
        try:
            perms_test = supabase_manager.supabase.table('user_permissions').select('*').limit(1).execute()
            print_log("✅ Tabella 'user_permissions' trovata")
            
            # Inserisci permessi con UUID validi
            permissions_data = [
                # Admin permissions
                {'id': str(uuid.uuid4()), 'role_id': 'admin', 'permission_name': 'user_management', 'is_active': True},  # Cambiato da 'permission' a 'permission_name'
                {'id': str(uuid.uuid4()), 'role_id': 'admin', 'permission_name': 'system_stats', 'is_active': True},
                {'id': str(uuid.uuid4()), 'role_id': 'admin', 'permission_name': 'all_access', 'is_active': True},
                # Manager permissions
                {'id': str(uuid.uuid4()), 'role_id': 'manager', 'permission_name': 'client_management', 'is_active': True},
                {'id': str(uuid.uuid4()), 'role_id': 'manager', 'permission_name': 'cross_management', 'is_active': True},
                # User permissions
                {'id': str(uuid.uuid4()), 'role_id': 'user', 'permission_name': 'view_clients', 'is_active': True},
                {'id': str(uuid.uuid4()), 'role_id': 'user', 'permission_name': 'view_crosses', 'is_active': True},
            ]
            
            for perm in permissions_data:
                try:
                    response = supabase_manager.supabase.table('user_permissions').insert(perm).execute()
                    if response.data:
                        print_log(f"✅ Permesso '{perm['permission_name']}' per ruolo '{perm['role_id']}' inserito")
                    else:
                        print_log(f"⚠️ Permesso '{perm['permission_name']}' per ruolo '{perm['role_id']}' non inserito")
                except Exception as e:
                    print_log(f"❌ Errore inserimento permesso '{perm['permission_name']}': {e}", "ERROR")
                    
        except Exception as e:
            print_log(f"⚠️ Tabella 'user_permissions' non trovata o non accessibile: {e}", "WARN")
        
        # 4. INSERIMENTO UTENTE ADMIN
        print_log("👤 Inserimento utente admin...")
        
        admin_user_id = str(uuid.uuid4())  # Genera UUID valido
        admin_user = {
            'id': admin_user_id,  # UUID valido
            'username': 'admin',
            'email': 'admin@cpadashboard.com',
            'full_name': 'Amministratore CPA Dashboard',
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            response = supabase_manager.supabase.table('users').insert(admin_user).execute()
            if response.data:
                print_log("✅ Utente admin inserito correttamente")
                print_log(f"   ID: {admin_user_id}")
                print_log(f"   Username: {admin_user['username']}")
                print_log(f"   Email: {admin_user['email']}")
            else:
                print_log("❌ Errore inserimento utente admin")
                return False
        except Exception as e:
            print_log(f"❌ Errore inserimento utente admin: {e}", "ERROR")
            return False
        
        # 5. INSERIMENTO PROFILO ADMIN
        print_log("📝 Inserimento profilo admin...")
        
        admin_profile = {
            'id': str(uuid.uuid4()),  # Genera UUID valido
            'user_id': admin_user_id,  # Riferimento all'utente admin
            'timezone': 'Europe/Rome',
            'language': 'it',
            'phone': '+39 123 456 789',
            'address': 'Via Roma 123, Milano, Italia',
            'preferences': {'theme': 'light', 'notifications': True},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            response = supabase_manager.supabase.table('user_profiles').insert(admin_profile).execute()
            if response.data:
                print_log("✅ Profilo admin inserito correttamente")
            else:
                print_log("❌ Errore inserimento profilo admin")
                return False
        except Exception as e:
            print_log(f"❌ Errore inserimento profilo admin: {e}", "ERROR")
            return False
        
        # 6. VERIFICA FINALE
        print_log("✅ Verifica finale...")
        
        # Conta record finali
        try:
            users_final = supabase_manager.supabase.table('users').select('count', count='exact').execute()
            users_count = users_final.count if hasattr(users_final, 'count') else 0
            
            profiles_final = supabase_manager.supabase.table('user_profiles').select('count', count='exact').execute()
            profiles_count = profiles_final.count if hasattr(profiles_final, 'count') else 0
            
            print_log("📊 STATISTICHE FINALI:")
            print_log(f"   👥 Utenti: {users_count}")
            print_log(f"   👤 Profili: {profiles_count}")
            
            if users_count > 0 and profiles_count > 0:
                print_log("🎉 RIPRISTINO COMPLETATO CON SUCCESSO!", "SUCCESS")
                print_log("🔄 Ora puoi riavviare l'app e fare login con admin/admin123")
                return True
            else:
                print_log("❌ RIPRISTINO INCOMPLETO", "ERROR")
                return False
                
        except Exception as e:
            print_log(f"❌ Errore verifica finale: {e}", "ERROR")
            return False
            
    except Exception as e:
        print_log(f"❌ Errore generale: {e}", "ERROR")
        import traceback
        print_log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")
        return False

if __name__ == "__main__":
    print_log("🚀 AVVIO SCRIPT RIPRISTINO UTENTE ADMIN", "START")
    success = restore_admin_user()
    
    if success:
        print_log("✅ SCRIPT COMPLETATO CON SUCCESSO", "SUCCESS")
    else:
        print_log("❌ SCRIPT COMPLETATO CON ERRORI", "ERROR")
    
    print_log("=" * 60)
    print_log("🏁 FINE SCRIPT", "END")
