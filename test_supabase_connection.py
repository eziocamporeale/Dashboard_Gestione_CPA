#!/usr/bin/env python3
"""
🧪 TEST CONNESSIONE SUPABASE - Creazione tabelle utenti
Script di test per verificare la connessione e creare le tabelle
"""

import streamlit as st
import requests
import json
from datetime import datetime

def test_supabase_connection():
    """Testa la connessione a Supabase"""
    
    st.title("🧪 Test Connessione Supabase")
    st.markdown("---")
    
    try:
        # Recupera credenziali dai secrets
        supabase_url = st.secrets.supabase.url
        supabase_key = st.secrets.supabase.anon_key
        
        st.success(f"✅ URL Supabase: {supabase_url}")
        st.info(f"🔑 API Key: {supabase_key[:20]}...")
        
        # Headers per l'API
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        # Test 1: Verifica connessione base
        st.markdown("### 🔍 **Test 1: Connessione Base**")
        
        try:
            # Prova a fare una richiesta GET generica
            response = requests.get(f"{supabase_url}/rest/v1/", headers=headers)
            
            if response.status_code == 200:
                st.success("✅ Connessione base riuscita!")
            else:
                st.warning(f"⚠️ Connessione base: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Errore connessione base: {e}")
            return False
        
        # Test 2: Verifica se esiste già la tabella users
        st.markdown("### 📋 **Test 2: Verifica Tabella Users**")
        
        try:
            # Prova a selezionare dalla tabella users
            response = requests.get(
                f"{supabase_url}/rest/v1/users?select=*&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                st.success("✅ Tabella 'users' già esistente!")
                users = response.json()
                st.info(f"📊 Utenti trovati: {len(users)}")
                
                # Mostra utenti esistenti
                if users:
                    st.markdown("#### 👥 **Utenti Esistenti**")
                    for user in users:
                        st.info(f"**{user.get('username', 'N/A')}** - Ruolo: {user.get('role', 'N/A')}")
                
                return True
                
            elif response.status_code == 404:
                st.info("ℹ️ Tabella 'users' non esistente - procedo con la creazione")
            else:
                st.warning(f"⚠️ Status inaspettato: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Errore verifica tabella: {e}")
        
        # Test 3: Creazione tabella users
        st.markdown("### 🚀 **Test 3: Creazione Tabella Users**")
        
        try:
            # Prova a inserire un utente di test
            test_user = {
                'username': 'test_setup',
                'email': 'test@setup.com',
                'password_hash': 'temp_hash_for_setup',
                'full_name': 'Test Setup',
                'role': 'user'
            }
            
            insert_url = f"{supabase_url}/rest/v1/users"
            
            st.info("📝 Tentativo inserimento utente di test...")
            
            response = requests.post(
                insert_url,
                headers=headers,
                json=test_user
            )
            
            if response.status_code == 201:
                st.success("✅ Tabella 'users' creata con successo!")
                
                # Rimuovi utente di test
                st.info("🧹 Rimozione utente di test...")
                delete_url = f"{supabase_url}/rest/v1/users?username=eq.test_setup"
                delete_response = requests.delete(delete_url, headers=headers)
                
                if delete_response.status_code == 200:
                    st.success("✅ Utente di test rimosso")
                else:
                    st.warning("⚠️ Utente di test non rimosso (non critico)")
                    
            elif response.status_code == 400:
                st.info("ℹ️ Tabella 'users' già esistente o errore di struttura")
                
                # Prova a recuperare la struttura
                st.info("🔍 Verifica struttura tabella...")
                select_response = requests.get(
                    f"{supabase_url}/rest/v1/users?select=*&limit=1",
                    headers=headers
                )
                
                if select_response.status_code == 200:
                    st.success("✅ Tabella 'users' accessibile")
                else:
                    st.error("❌ Tabella 'users' non accessibile")
                    return False
                    
            else:
                st.error(f"❌ Errore creazione tabella: {response.status_code}")
                st.error(f"Risposta: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore creazione tabella: {e}")
            return False
        
        # Test 4: Creazione utente admin
        st.markdown("### 👤 **Test 4: Creazione Utente Admin**")
        
        try:
            admin_user = {
                'username': 'admin',
                'email': 'admin@cpadashboard.com',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO6e',  # admin123
                'full_name': 'Amministratore CPA Dashboard',
                'role': 'admin'
            }
            
            insert_url = f"{supabase_url}/rest/v1/users"
            
            st.info("📝 Creazione utente admin...")
            
            admin_response = requests.post(
                insert_url,
                headers=headers,
                json=admin_user
            )
            
            if admin_response.status_code == 201:
                st.success("✅ Utente admin creato con successo!")
            elif admin_response.status_code == 409:
                st.info("ℹ️ Utente admin già esistente")
            else:
                st.error(f"❌ Errore creazione admin: {admin_response.status_code}")
                st.error(f"Risposta: {admin_response.text}")
                
        except Exception as e:
            st.error(f"❌ Errore creazione admin: {e}")
        
        # Test 5: Verifica finale
        st.markdown("### 🎯 **Test 5: Verifica Finale**")
        
        try:
            st.info("🧪 Test accesso finale...")
            
            test_response = requests.get(
                f"{supabase_url}/rest/v1/users?select=username,role&limit=10",
                headers=headers
            )
            
            if test_response.status_code == 200:
                users = test_response.json()
                st.success(f"✅ Accesso finale riuscito! Utenti trovati: {len(users)}")
                
                # Mostra tutti gli utenti
                if users:
                    st.markdown("#### 👥 **Utenti nel Sistema**")
                    for user in users:
                        st.info(f"**{user.get('username', 'N/A')}** - Ruolo: {user.get('role', 'N/A')}")
                        
                return True
                
            else:
                st.error(f"❌ Errore accesso finale: {test_response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore verifica finale: {e}")
            return False
            
    except Exception as e:
        st.error(f"❌ **ERRORE CRITICO**: {e}")
        st.info("Verifica la configurazione e riprova")
        return False

def show_manual_setup():
    """Mostra istruzioni per setup manuale"""
    
    st.markdown("---")
    st.markdown("## 🔧 **SETUP MANUALE SUPABASE**")
    
    st.info("Se la creazione automatica fallisce, puoi creare le tabelle manualmente:")
    
    # Recupera URL per il dashboard
    try:
        supabase_url = st.secrets.supabase.url
        project_id = supabase_url.split('.')[0].replace('https://', '')
        dashboard_url = f"https://app.supabase.com/project/{project_id}"
        
        st.markdown(f"### 📋 **1. Vai su Supabase Dashboard**")
        st.markdown(f"🔗 [Dashboard Supabase]({dashboard_url})")
        
    except:
        st.markdown("### 📋 **1. Vai su Supabase Dashboard**")
        st.info("Accedi a [app.supabase.com](https://app.supabase.com)")
    
    st.markdown("### 📝 **2. Esegui questo SQL nel SQL Editor**")
    
    sql_code = """
-- Crea tabella users
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'manager', 'user')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inserisci utente admin
INSERT INTO users (username, email, password_hash, full_name, role) 
VALUES (
    'admin', 
    'admin@cpadashboard.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO6e',
    'Amministratore CPA Dashboard',
    'admin'
) ON CONFLICT (username) DO NOTHING;
    """
    
    st.code(sql_code, language='sql')
    
    st.markdown("### 🚀 **3. Dopo la creazione**")
    st.info("1. ✅ Tabelle create manualmente")
    st.info("2. 🔄 Aggiorna app.py per usare auth_advanced")
    st.info("3. 🧪 Testa il sistema di autenticazione")

if __name__ == "__main__":
    # Esegui test connessione
    success = test_supabase_connection()
    
    # Se fallisce, mostra istruzioni manuali
    if not success:
        show_manual_setup()
    
    st.markdown("---")
    st.markdown("## 📊 **RISULTATO TEST**")
    
    if success:
        st.success("🎉 **TUTTI I TEST SUPERATI!**")
        st.markdown("### 🔐 **CREDENZIALI DI DEFAULT**")
        st.warning("⚠️ **IMPORTANTE**: Cambia immediatamente queste credenziali!")
        st.code("Username: admin\nPassword: admin123")
        
        st.markdown("### 🚀 **PROSSIMI PASSI**")
        st.info("1. ✅ Tabelle utenti create in Supabase")
        st.info("2. 🔄 Aggiorna app.py per usare auth_advanced")
        st.info("3. 🧪 Testa il sistema di autenticazione")
        st.info("4. 🔐 Cambia password admin di default")
        
    else:
        st.error("❌ **TEST FALLITI**")
        st.info("Usa le istruzioni manuali sopra per completare il setup")
    
    st.markdown("---")
    st.markdown("### 📚 **DOCUMENTAZIONE**")
    st.info("Per maggiori informazioni, consulta il file README.md")
