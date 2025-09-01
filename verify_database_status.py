#!/usr/bin/env python3
"""
🔍 VERIFICA COMPLETA STATO DATABASE SUPABASE - Dashboard CPA
Script per diagnosticare problemi di database e utenti
"""

import streamlit as st
import sys
import os

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

def verify_database_status():
    """Verifica completa dello stato del database"""
    
    st.title("🔍 VERIFICA STATO DATABASE SUPABASE")
    st.markdown("---")
    
    try:
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        st.success("✅ Connessione Supabase stabilita")
        
        # 1. VERIFICA TABELLE UTENTI
        st.header("📊 1. VERIFICA TABELLE UTENTI")
        
        # Tabella users
        st.subheader("👥 Tabella 'users'")
        try:
            users_response = supabase_manager.supabase.table('users').select('*').execute()
            st.info(f"📊 Record trovati: {len(users_response.data) if users_response.data else 0}")
            
            if users_response.data:
                st.success("✅ Tabella 'users' contiene dati")
                # Mostra primo utente (senza password)
                first_user = users_response.data[0]
                safe_user = {k: v for k, v in first_user.items() if k != 'password_hash'}
                st.json(safe_user)
            else:
                st.error("❌ Tabella 'users' è VUOTA!")
                
        except Exception as e:
            st.error(f"❌ Errore accesso tabella 'users': {e}")
        
        # Tabella user_profiles
        st.subheader("👤 Tabella 'user_profiles'")
        try:
            profiles_response = supabase_manager.supabase.table('user_profiles').select('*').execute()
            st.info(f"📊 Record trovati: {len(profiles_response.data) if profiles_response.data else 0}")
            
            if profiles_response.data:
                st.success("✅ Tabella 'user_profiles' contiene dati")
                st.json(profiles_response.data[0])
            else:
                st.error("❌ Tabella 'user_profiles' è VUOTA!")
                
        except Exception as e:
            st.error(f"❌ Errore accesso tabella 'user_profiles': {e}")
        
        # 2. VERIFICA RLS POLICIES
        st.header("🔒 2. VERIFICA RLS POLICIES")
        
        try:
            # Prova a inserire un record di test (dovrebbe fallire se RLS è attivo)
            test_data = {
                'username': 'test_user',
                'email': 'test@test.com',
                'full_name': 'Test User',
                'role': 'user',
                'is_active': True,
                'created_at': '2025-08-31T00:00:00Z'
            }
            
            st.info("🧪 Test inserimento record (dovrebbe fallire se RLS è attivo)...")
            test_response = supabase_manager.supabase.table('users').insert(test_data).execute()
            
            if test_response.data:
                st.warning("⚠️ RLS potrebbe non essere attivo - record inserito!")
                # Rimuovi il record di test
                supabase_manager.supabase.table('users').delete().eq('username', 'test_user').execute()
                st.info("🧹 Record di test rimosso")
            else:
                st.success("✅ RLS attivo - inserimento bloccato correttamente")
                
        except Exception as e:
            st.success(f"✅ RLS attivo - inserimento bloccato: {e}")
        
        # 3. VERIFICA STRUTTURA TABELLE
        st.header("🏗️ 3. VERIFICA STRUTTURA TABELLE")
        
        # Lista tutte le tabelle
        st.subheader("📋 Tabelle disponibili")
        try:
            # Prova a listare le tabelle (se supportato)
            st.info("🔍 Tentativo di listare tabelle disponibili...")
            
            # Verifica tabelle note
            known_tables = ['users', 'user_profiles', 'user_roles', 'user_permissions', 'user_sessions', 'user_access_logs', 'failed_login_attempts']
            
            for table in known_tables:
                try:
                    response = supabase_manager.supabase.table(table).select('count', count='exact').execute()
                    if hasattr(response, 'count'):
                        st.success(f"✅ Tabella '{table}': {response.count} record")
                    else:
                        st.warning(f"⚠️ Tabella '{table}': struttura sconosciuta")
                except Exception as e:
                    st.error(f"❌ Tabella '{table}': {e}")
                    
        except Exception as e:
            st.error(f"❌ Errore verifica tabelle: {e}")
        
        # 4. RACCOMANDAZIONI
        st.header("💡 4. RACCOMANDAZIONI")
        
        st.markdown("""
        **Se le tabelle sono vuote:**
        1. 🔧 Eseguire script `fix_rls_insert_policies.sql` in Supabase
        2. 🔄 Ripopolare tabelle con dati di default
        3. ✅ Verificare funzionamento
        
        **Se RLS non funziona:**
        1. 🔒 Controllare policies in Supabase
        2. 🔧 Correggere configurazione RLS
        3. ✅ Testare sicurezza
        """)
        
    except Exception as e:
        st.error(f"❌ Errore generale: {e}")
        import traceback
        st.error(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    verify_database_status()
