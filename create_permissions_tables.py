#!/usr/bin/env python3
"""
Script per creare le tabelle del sistema permessi su Supabase
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def create_permissions_tables():
    """Crea le tabelle del sistema permessi su Supabase"""
    
    try:
        from supabase_manager import SupabaseManager
        
        print("🔧 Creazione tabelle sistema permessi su Supabase...")
        
        # Inizializza Supabase Manager
        supabase_manager = SupabaseManager()
        
        if not supabase_manager.is_configured:
            print("❌ Supabase non configurato")
            return False
        
        # Leggi lo schema SQL
        schema_file = Path("database/supabase_permissions_schema.sql")
        if not schema_file.exists():
            print(f"❌ File schema non trovato: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            sql_script = f.read()
        
        print("📋 Schema SQL caricato correttamente")
        
        # Esegui lo script SQL su Supabase
        try:
            # Dividi lo script in comandi separati
            commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
            
            print(f"🔄 Esecuzione {len(commands)} comandi SQL...")
            
            for i, command in enumerate(commands, 1):
                if command:
                    print(f"📝 Comando {i}/{len(commands)}: {command[:50]}...")
                    
                    # Esegui il comando SQL
                    result = supabase_manager.supabase.rpc('exec_sql', {'sql': command}).execute()
                    
                    print(f"✅ Comando {i} eseguito con successo")
            
            print("✅ Tutte le tabelle del sistema permessi create con successo!")
            return True
            
        except Exception as e:
            print(f"❌ Errore esecuzione SQL: {e}")
            
            # Fallback: prova con query dirette
            print("🔄 Tentativo con query dirette...")
            
            # Crea le tabelle una per una
            tables_queries = [
                """
                CREATE TABLE IF NOT EXISTS system_users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255),
                    password_hash VARCHAR(255),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS roles (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    level INTEGER DEFAULT 1,
                    is_system BOOLEAN DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS permissions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    resource VARCHAR(100) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    is_system BOOLEAN DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
            ]
            
            for i, query in enumerate(tables_queries, 1):
                try:
                    print(f"📝 Creazione tabella {i}...")
                    supabase_manager.supabase.rpc('exec_sql', {'sql': query}).execute()
                    print(f"✅ Tabella {i} creata")
                except Exception as table_error:
                    print(f"⚠️ Errore tabella {i}: {table_error}")
            
            return True
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return False

def insert_default_data():
    """Inserisce i dati di default per il sistema permessi"""
    
    try:
        from supabase_manager import SupabaseManager
        
        print("📊 Inserimento dati di default...")
        
        supabase_manager = SupabaseManager()
        
        # Inserisci ruolo admin
        try:
            supabase_manager.supabase.table('roles').insert({
                'name': 'admin',
                'description': 'Amministratore del sistema',
                'level': 3,
                'is_system': True
            }).execute()
            print("✅ Ruolo admin creato")
        except Exception as e:
            print(f"⚠️ Ruolo admin già esistente: {e}")
        
        # Inserisci permessi di base
        base_permissions = [
            {'name': 'user_management', 'description': 'Gestione utenti', 'resource': 'users', 'action': 'manage'},
            {'name': 'role_management', 'description': 'Gestione ruoli', 'resource': 'roles', 'action': 'manage'},
            {'name': 'permission_management', 'description': 'Gestione permessi', 'resource': 'permissions', 'action': 'manage'},
            {'name': 'system_settings', 'description': 'Impostazioni sistema', 'resource': 'settings', 'action': 'manage'}
        ]
        
        for perm in base_permissions:
            try:
                supabase_manager.supabase.table('permissions').insert(perm).execute()
                print(f"✅ Permesso {perm['name']} creato")
            except Exception as e:
                print(f"⚠️ Permesso {perm['name']} già esistente: {e}")
        
        print("✅ Dati di default inseriti")
        return True
        
    except Exception as e:
        print(f"❌ Errore inserimento dati: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CREAZIONE TABELLE SISTEMA PERMESSI")
    print("=" * 50)
    
    # Crea le tabelle
    if create_permissions_tables():
        # Inserisci dati di default
        insert_default_data()
        print("\n🎉 SISTEMA PERMESSI CONFIGURATO CON SUCCESSO!")
    else:
        print("\n❌ ERRORE NELLA CONFIGURAZIONE DEL SISTEMA PERMESSI")
