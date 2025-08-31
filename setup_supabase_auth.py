#!/usr/bin/env python3
"""
🚀 SETUP SUPABASE AUTH - Creazione tabelle utenti
Esegue lo script SQL direttamente in Supabase tramite API
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Aggiungi il percorso per importare supabase_manager
sys.path.append(str(Path(__file__).parent / 'progetti' / 'supabase_integration'))

def setup_supabase_auth():
    """Configura il sistema di autenticazione Supabase"""
    
    st.title("🚀 Setup Sistema Autenticazione Supabase")
    st.markdown("---")
    
    try:
        # Importa SupabaseManager
        from supabase_manager import SupabaseManager
        
        # Inizializza connessione
        st.info("🔧 Inizializzazione connessione Supabase...")
        supabase_manager = SupabaseManager()
        
        if not supabase_manager.is_configured:
            st.error("❌ Supabase non configurato correttamente")
            st.info("Verifica le credenziali nei secrets di Streamlit")
            return False
        
        # Test connessione
        st.info("🧪 Test connessione Supabase...")
        success, message = supabase_manager.test_connection()
        
        if not success:
            st.error(f"❌ Errore connessione: {message}")
            return False
        
        st.success(f"✅ {message}")
        
        # Leggi script SQL
        st.info("📖 Lettura script SQL...")
        sql_file = Path(__file__).parent / 'database' / 'create_users_tables.sql'
        
        if not sql_file.exists():
            st.error("❌ File SQL non trovato")
            return False
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        st.success("✅ Script SQL caricato")
        
        # Esegui script SQL
        st.info("🚀 Esecuzione script SQL in Supabase...")
        
        # Dividi lo script in comandi separati
        sql_commands = []
        current_command = ""
        
        for line in sql_script.split('\n'):
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('COMMENT') and not line.startswith('DO $$'):
                current_command += line + " "
                if line.endswith(';'):
                    sql_commands.append(current_command.strip())
                    current_command = ""
        
        # Rimuovi comandi vuoti
        sql_commands = [cmd for cmd in sql_commands if cmd.strip()]
        
        st.info(f"📊 Trovati {len(sql_commands)} comandi SQL da eseguire")
        
        # Esegui ogni comando
        success_count = 0
        error_count = 0
        
        for i, command in enumerate(sql_commands, 1):
            try:
                st.text(f"Esecuzione comando {i}/{len(sql_commands)}...")
                
                # Esegui comando SQL
                response = supabase_manager.supabase.rpc('exec_sql', {'sql': command}).execute()
                
                if response.data:
                    st.success(f"✅ Comando {i} eseguito con successo")
                    success_count += 1
                else:
                    st.warning(f"⚠️ Comando {i} completato senza dati")
                    success_count += 1
                    
            except Exception as e:
                st.error(f"❌ Errore comando {i}: {e}")
                error_count += 1
        
        # Risultato finale
        st.markdown("---")
        st.markdown("## 📊 **RISULTATO SETUP**")
        
        if error_count == 0:
            st.success(f"🎉 **SETUP COMPLETATO CON SUCCESSO!**")
            st.info(f"✅ Comandi eseguiti: {success_count}")
            st.info(f"❌ Errori: {error_count}")
            
            st.markdown("### 🔐 **CREDENZIALI DI DEFAULT**")
            st.warning("⚠️ **IMPORTANTE**: Cambia immediatamente queste credenziali!")
            st.code("Username: admin\nPassword: admin123")
            
            st.markdown("### 🚀 **PROSSIMI PASSI**")
            st.info("1. ✅ Tabelle utenti create in Supabase")
            st.info("2. 🔄 Aggiorna app.py per usare auth_advanced")
            st.info("3. 🧪 Testa il sistema di autenticazione")
            st.info("4. 🔐 Cambia password admin di default")
            
            return True
            
        else:
            st.error(f"⚠️ **SETUP COMPLETATO CON ERRORI**")
            st.info(f"✅ Comandi eseguiti: {success_count}")
            st.error(f"❌ Errori: {error_count}")
            
            st.markdown("### 🔧 **RISOLUZIONE PROBLEMI**")
            st.info("1. Verifica le credenziali Supabase")
            st.info("2. Controlla i permessi del database")
            st.info("3. Esegui manualmente lo script SQL")
            
            return False
            
    except Exception as e:
        st.error(f"❌ **ERRORE CRITICO**: {e}")
        st.info("Verifica la configurazione e riprova")
        return False

def manual_sql_execution():
    """Esecuzione manuale di comandi SQL specifici"""
    
    st.markdown("---")
    st.markdown("## 🔧 **ESECUZIONE MANUALE SQL**")
    
    st.info("Se l'esecuzione automatica fallisce, puoi eseguire comandi SQL manualmente")
    
    # Comando per creare tabella users
    st.markdown("### 📋 **Tabella Users**")
    users_sql = """
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
    """
    
    st.code(users_sql, language='sql')
    
    if st.button("🚀 Esegui Creazione Tabella Users"):
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            # Esegui comando
            response = supabase_manager.supabase.rpc('exec_sql', {'sql': users_sql}).execute()
            
            if response.data:
                st.success("✅ Tabella users creata con successo!")
            else:
                st.warning("⚠️ Comando completato senza dati")
                
        except Exception as e:
            st.error(f"❌ Errore: {e}")

if __name__ == "__main__":
    # Esegui setup automatico
    success = setup_supabase_auth()
    
    # Se fallisce, mostra opzioni manuali
    if not success:
        manual_sql_execution()
    
    st.markdown("---")
    st.markdown("### 📚 **DOCUMENTAZIONE**")
    st.info("Per maggiori informazioni, consulta il file README.md")
