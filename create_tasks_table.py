#!/usr/bin/env python3
"""
🔧 CREAZIONE TABELLA TASKS
Script per creare la tabella tasks in Supabase
"""

import os
import sys
from supabase_manager import SupabaseManager

def create_tasks_table():
    """Crea la tabella tasks in Supabase"""
    try:
        supabase_manager = SupabaseManager()
        print("🔧 Creazione tabella tasks...")
        
        # SQL per creare la tabella tasks
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            priority VARCHAR(50) NOT NULL DEFAULT 'Media',
            period VARCHAR(50) NOT NULL DEFAULT 'Giornaliero',
            due_date DATE,
            status VARCHAR(50) NOT NULL DEFAULT 'Da Fare',
            assigned_to TEXT[] DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by VARCHAR(255),
            completed_at TIMESTAMP WITH TIME ZONE,
            notes TEXT
        );
        """
        
        # Crea la tabella usando RPC
        response = supabase_manager.supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        
        if response.data:
            print("✅ Tabella tasks creata con successo!")
        else:
            print("⚠️ Risposta vuota, ma potrebbe essere stata creata")
        
        # Verifica che la tabella sia stata creata
        print("\n🔍 Verifica creazione tabella...")
        test_response = supabase_manager.supabase.table('tasks').select('*').limit(1).execute()
        
        if test_response.data is not None:
            print("✅ Tabella tasks verificata e funzionante!")
            return True
        else:
            print("❌ Errore nella verifica della tabella")
            return False
            
    except Exception as e:
        print(f"❌ Errore creazione tabella: {e}")
        
        # Prova metodo alternativo con SQL diretto
        try:
            print("\n🔄 Tentativo metodo alternativo...")
            # Prova a inserire un task di test per creare la tabella
            test_task = {
                'title': 'Test Task',
                'description': 'Task di test per verificare la tabella',
                'priority': 'Media',
                'period': 'Giornaliero',
                'status': 'Da Fare',
                'assigned_to': ['admin']
            }
            
            response = supabase_manager.supabase.table('tasks').insert(test_task).execute()
            
            if response.data:
                print("✅ Tabella tasks creata tramite inserimento!")
                # Elimina il task di test
                supabase_manager.supabase.table('tasks').delete().eq('title', 'Test Task').execute()
                print("🧹 Task di test eliminato")
                return True
            else:
                print("❌ Errore anche con metodo alternativo")
                return False
                
        except Exception as e2:
            print(f"❌ Errore metodo alternativo: {e2}")
            return False

if __name__ == "__main__":
    print("🚀 AVVIO CREAZIONE TABELLA TASKS")
    print("=" * 50)
    
    success = create_tasks_table()
    
    if success:
        print("\n✅ SUCCESSO: Tabella tasks creata e verificata!")
        print("💡 Ora puoi creare e gestire task persistenti")
    else:
        print("\n❌ ERRORE: Impossibile creare la tabella tasks")
        print("💡 Controlla i permessi e la connessione a Supabase")
