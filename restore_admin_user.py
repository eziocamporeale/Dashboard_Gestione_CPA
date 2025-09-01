#!/usr/bin/env python3
"""
🔧 RIPRISTINO UTENTE ADMIN - Dashboard CPA
Script per inserire utente admin e dati necessari nel database Supabase
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

def restore_admin_user():
    """Ripristina l'utente admin e tutti i dati necessari"""
    
    st.title("🔧 RIPRISTINO UTENTE ADMIN")
    st.markdown("---")
    
    try:
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        st.success("✅ Connessione Supabase stabilita")
        
        # 1. INSERIMENTO RUOLI
        st.header("👑 1. INSERIMENTO RUOLI")
        
        roles_data = [
            {
                'id': 'admin',
                'name': 'Amministratore',
                'description': 'Accesso completo al sistema',
                'is_active': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'manager',
                'name': 'Manager',
                'description': 'Gestione clienti e incroci',
                'is_active': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'user',
                'name': 'Utente',
                'description': 'Accesso limitato',
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }
        ]
        
        st.info("🔧 Inserimento ruoli...")
        for role in roles_data:
            try:
                response = supabase_manager.supabase.table('user_roles').insert(role).execute()
                if response.data:
                    st.success(f"✅ Ruolo '{role['name']}' inserito")
                else:
                    st.warning(f"⚠️ Ruolo '{role['name']}' già esistente")
            except Exception as e:
                st.warning(f"⚠️ Ruolo '{role['name']}' non inserito: {e}")
        
        # 2. INSERIMENTO PERMESSI
        st.header("🔐 2. INSERIMENTO PERMESSI")
        
        permissions_data = [
            # Admin permissions
            {'role_id': 'admin', 'permission': 'user_management', 'is_active': True},
            {'role_id': 'admin', 'permission': 'system_stats', 'is_active': True},
            {'role_id': 'admin', 'permission': 'all_access', 'is_active': True},
            # Manager permissions
            {'role_id': 'manager', 'permission': 'client_management', 'is_active': True},
            {'role_id': 'manager', 'permission': 'cross_management', 'is_active': True},
            # User permissions
            {'role_id': 'user', 'permission': 'view_clients', 'is_active': True},
            {'role_id': 'user', 'permission': 'view_crosses', 'is_active': True},
        ]
        
        st.info("🔧 Inserimento permessi...")
        for perm in permissions_data:
            try:
                response = supabase_manager.supabase.table('user_permissions').insert(perm).execute()
                if response.data:
                    st.success(f"✅ Permesso '{perm['permission']}' per ruolo '{perm['role_id']}' inserito")
                else:
                    st.warning(f"⚠️ Permesso '{perm['permission']}' per ruolo '{perm['role_id']}' già esistente")
            except Exception as e:
                st.warning(f"⚠️ Permesso '{perm['permission']}' per ruolo '{perm['role_id']}' non inserito: {e}")
        
        # 3. INSERIMENTO UTENTE ADMIN
        st.header("👤 3. INSERIMENTO UTENTE ADMIN")
        
        admin_user = {
            'id': 'admin-user-001',
            'username': 'admin',
            'email': 'admin@cpadashboard.com',
            'full_name': 'Amministratore CPA Dashboard',
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        st.info("🔧 Inserimento utente admin...")
        try:
            response = supabase_manager.supabase.table('users').insert(admin_user).execute()
            if response.data:
                st.success("✅ Utente admin inserito correttamente")
                st.json(response.data[0])
            else:
                st.error("❌ Errore inserimento utente admin")
        except Exception as e:
            st.error(f"❌ Errore inserimento utente admin: {e}")
            return False
        
        # 4. INSERIMENTO PROFILO ADMIN
        st.header("📝 4. INSERIMENTO PROFILO ADMIN")
        
        admin_profile = {
            'id': 'admin-profile-001',
            'user_id': 'admin-user-001',
            'timezone': 'Europe/Rome',
            'language': 'it',
            'phone': '+39 123 456 789',
            'address': 'Via Roma 123, Milano, Italia',
            'preferences': {'theme': 'light', 'notifications': True},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        st.info("🔧 Inserimento profilo admin...")
        try:
            response = supabase_manager.supabase.table('user_profiles').insert(admin_profile).execute()
            if response.data:
                st.success("✅ Profilo admin inserito correttamente")
                st.json(response.data[0])
            else:
                st.error("❌ Errore inserimento profilo admin")
        except Exception as e:
            st.error(f"❌ Errore inserimento profilo admin: {e}")
            return False
        
        # 5. VERIFICA FINALE
        st.header("✅ 5. VERIFICA FINALE")
        
        st.info("🔍 Verifica inserimento...")
        
        # Conta utenti
        users_response = supabase_manager.supabase.table('users').select('count', count='exact').execute()
        users_count = users_response.count if hasattr(users_response, 'count') else 0
        
        # Conta profili
        profiles_response = supabase_manager.supabase.table('user_profiles').select('count', count='exact').execute()
        profiles_count = profiles_response.count if hasattr(profiles_response, 'count') else 0
        
        # Conta ruoli
        roles_response = supabase_manager.supabase.table('user_roles').select('count', count='exact').execute()
        roles_count = roles_response.count if hasattr(roles_response, 'count') else 0
        
        # Conta permessi
        perms_response = supabase_manager.supabase.table('user_permissions').select('count', count='exact').execute()
        perms_count = perms_response.count if hasattr(perms_response, 'count') else 0
        
        st.success(f"📊 STATISTICHE FINALI:")
        st.success(f"👥 Utenti: {users_count}")
        st.success(f"👤 Profili: {profiles_count}")
        st.success(f"👑 Ruoli: {roles_count}")
        st.success(f"🔐 Permessi: {perms_count}")
        
        if users_count > 0 and profiles_count > 0:
            st.success("🎉 RIPRISTINO COMPLETATO CON SUCCESSO!")
            st.info("🔄 Ora puoi riavviare l'app e fare login con admin/admin123")
            return True
        else:
            st.error("❌ RIPRISTINO INCOMPLETO - Controlla gli errori sopra")
            return False
            
    except Exception as e:
        st.error(f"❌ Errore generale: {e}")
        import traceback
        st.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    restore_admin_user()
