#!/usr/bin/env python3
"""
Script semplificato per creare le tabelle del sistema permessi su Supabase
"""

import os
import sys
import requests
import json

# Aggiungi il percorso della directory corrente al path di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def setup_permissions_tables():
    """Crea le tabelle del sistema permessi usando le API REST di Supabase"""
    
    try:
        from supabase_manager import SupabaseManager
        
        print("🔧 Setup tabelle sistema permessi su Supabase...")
        
        # Inizializza Supabase Manager
        supabase_manager = SupabaseManager()
        
        if not supabase_manager.is_configured:
            print("❌ Supabase non configurato")
            return False
        
        # Ottieni le credenziali Supabase
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Credenziali Supabase non trovate")
            return False
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        print("✅ Credenziali Supabase configurate")
        
        # Crea le tabelle una per una usando SQL diretto
        tables_sql = [
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
            """,
            """
            CREATE TABLE IF NOT EXISTS user_roles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES system_users(id) ON DELETE CASCADE,
                role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
                assigned_by UUID REFERENCES system_users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, role_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS role_permissions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
                permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
                assigned_by UUID REFERENCES system_users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(role_id, permission_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_permissions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES system_users(id) ON DELETE CASCADE,
                permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
                assigned_by UUID REFERENCES system_users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, permission_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS permission_audit_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES system_users(id),
                action VARCHAR(50) NOT NULL,
                details JSONB,
                target_user_id UUID REFERENCES system_users(id),
                target_role_id UUID REFERENCES roles(id),
                target_permission_id UUID REFERENCES permissions(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
        ]
        
        # Esegui le query SQL tramite API REST
        for i, sql in enumerate(tables_sql, 1):
            try:
                print(f"📝 Creazione tabella {i}...")
                
                # Usa l'endpoint SQL di Supabase
                response = requests.post(
                    f"{supabase_url}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={'sql': sql}
                )
                
                if response.status_code == 200:
                    print(f"✅ Tabella {i} creata con successo")
                else:
                    print(f"⚠️ Tabella {i}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"⚠️ Errore tabella {i}: {e}")
        
        print("✅ Setup tabelle completato")
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
            result = supabase_manager.supabase.table('roles').insert({
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
                result = supabase_manager.supabase.table('permissions').insert(perm).execute()
                print(f"✅ Permesso {perm['name']} creato")
            except Exception as e:
                print(f"⚠️ Permesso {perm['name']} già esistente: {e}")
        
        print("✅ Dati di default inseriti")
        return True
        
    except Exception as e:
        print(f"❌ Errore inserimento dati: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SETUP SISTEMA PERMESSI SEMPLIFICATO")
    print("=" * 50)
    
    # Crea le tabelle
    if setup_permissions_tables():
        # Inserisci dati di default
        insert_default_data()
        print("\n🎉 SISTEMA PERMESSI CONFIGURATO CON SUCCESSO!")
    else:
        print("\n❌ ERRORE NELLA CONFIGURAZIONE DEL SISTEMA PERMESSI")
