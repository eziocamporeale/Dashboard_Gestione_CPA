#!/usr/bin/env python3
"""
🔍 SCRIPT COMPLETO PER INTERROGARE TUTTI I DATABASE SUPABASE
📊 Ottiene TUTTI i dati degli utenti da tutti e tre i progetti
Creato da Ezio Camporeale
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Import Supabase types
try:
    from supabase import create_client, Client
except ImportError:
    Client = None

# Configurazione dei tre database Supabase
SUPABASE_CONFIGS = {
    'DASH_GESTIONE_LEAD': {
        'url': 'https://xjjmpurdjqwjomxmqqks.supabase.co',
        'key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqam1wdXJkanF3am9teG1xcWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4OTI2NzMsImV4cCI6MjA3MjQ2ODY3M30.grFLiS6zmYGx5wNxuFKND5qHeYc71Nl_Tf8Sp4ce-ao',
        'project_name': 'DASH_GESTIONE_LEAD'
    },
    'DASH_OSINT_STREAMLIT': {
        'url': 'https://kgmfztsceatiioaevytg.supabase.co',
        'key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtnbWZ6dHNjZWF0aWlvYWV2eXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczMjgzOTgsImV4cCI6MjA3MjkwNDM5OH0.cwdf4yfssX98B_yZ0O49UrxUWN0-wIKMGC30Nck2D4s',
        'project_name': 'DASH_OSINT_STREAMLIT'
    }
}

class SupabaseUserQuery:
    """Classe per interrogare tutti i database Supabase e ottenere dati utenti"""
    
    def __init__(self):
        self.results = {}
        self.supabase_clients = {}
        
    def init_supabase_clients(self):
        """Inizializza i client Supabase per tutti i progetti"""
        try:
            from supabase import create_client, Client
            
            for project_name, config in SUPABASE_CONFIGS.items():
                try:
                    client = create_client(config['url'], config['key'])
                    self.supabase_clients[project_name] = client
                    print(f"✅ Client Supabase inizializzato per {project_name}")
                except Exception as e:
                    print(f"❌ Errore inizializzazione {project_name}: {e}")
                    
        except ImportError:
            print("❌ Supabase non installato. Installa con: pip install supabase")
            return False
        
        return len(self.supabase_clients) > 0
    
    def query_users_table(self, project_name: str, client) -> List[Dict[str, Any]]:
        """Interroga la tabella users di un progetto"""
        try:
            print(f"\n🔍 Interrogazione tabella 'users' in {project_name}...")
            
            # Prova a ottenere tutti gli utenti
            response = client.table('users').select('*').execute()
            
            if response.data:
                print(f"   ✅ Trovati {len(response.data)} utenti")
                return response.data
            else:
                print(f"   📭 Nessun utente trovato")
                return []
                
        except Exception as e:
            print(f"   ❌ Errore interrogazione: {e}")
            return []
    
    def query_all_tables(self, project_name: str, client) -> Dict[str, List[Dict[str, Any]]]:
        """Interroga tutte le tabelle di un progetto per trovare dati utenti"""
        try:
            print(f"\n🔍 Interrogazione completa di {project_name}...")
            
            # Tabelle che potrebbero contenere dati utenti
            user_tables = [
                'users', 'user', 'auth_users', 'system_users', 
                'profiles', 'accounts', 'members', 'staff'
            ]
            
            results = {}
            
            for table_name in user_tables:
                try:
                    response = client.table(table_name).select('*').limit(10).execute()
                    if response.data:
                        results[table_name] = response.data
                        print(f"   ✅ Tabella '{table_name}': {len(response.data)} record")
                    else:
                        print(f"   📭 Tabella '{table_name}': vuota")
                except Exception as e:
                    print(f"   ❌ Tabella '{table_name}': errore - {e}")
            
            return results
            
        except Exception as e:
            print(f"❌ Errore interrogazione completa {project_name}: {e}")
            return {}
    
    def get_database_schema(self, project_name: str, client) -> Dict[str, Any]:
        """Ottiene informazioni sullo schema del database"""
        try:
            print(f"\n📋 Analisi schema database {project_name}...")
            
            # Prova a ottenere informazioni sulle tabelle
            schema_info = {
                'project_name': project_name,
                'tables_found': [],
                'user_related_tables': [],
                'total_records': 0
            }
            
            # Tabelle comuni da verificare
            common_tables = [
                'users', 'user', 'auth_users', 'system_users', 'profiles',
                'accounts', 'members', 'staff', 'roles', 'permissions',
                'user_roles', 'user_permissions', 'sessions', 'user_sessions'
            ]
            
            for table_name in common_tables:
                try:
                    # Prova a contare i record
                    count_response = client.table(table_name).select('count', count='exact').execute()
                    if count_response.count is not None:
                        schema_info['tables_found'].append({
                            'name': table_name,
                            'count': count_response.count
                        })
                        schema_info['total_records'] += count_response.count
                        
                        if 'user' in table_name.lower() or table_name in ['profiles', 'accounts', 'members', 'staff']:
                            schema_info['user_related_tables'].append(table_name)
                            
                except Exception as e:
                    # Tabella non esiste o errore di accesso
                    pass
            
            return schema_info
            
        except Exception as e:
            print(f"❌ Errore analisi schema {project_name}: {e}")
            return {'project_name': project_name, 'error': str(e)}
    
    def query_all_projects(self):
        """Interroga tutti i progetti Supabase"""
        print("🚀 INIZIO INTERROGAZIONE COMPLETA DI TUTTI I DATABASE SUPABASE")
        print("=" * 80)
        
        if not self.init_supabase_clients():
            print("❌ Impossibile inizializzare i client Supabase")
            return
        
        for project_name, client in self.supabase_clients.items():
            print(f"\n🎯 PROGETTO: {project_name}")
            print("-" * 50)
            
            # Analisi schema
            schema_info = self.get_database_schema(project_name, client)
            
            # Interrogazione tabelle utenti
            user_data = self.query_users_table(project_name, client)
            
            # Interrogazione completa
            all_tables_data = self.query_all_tables(project_name, client)
            
            # Salva risultati
            self.results[project_name] = {
                'schema': schema_info,
                'users': user_data,
                'all_tables': all_tables_data,
                'timestamp': datetime.now().isoformat()
            }
        
        print("\n" + "=" * 80)
        print("✅ INTERROGAZIONE COMPLETATA")
    
    def generate_report(self):
        """Genera un report completo dei risultati"""
        print("\n📊 GENERAZIONE REPORT COMPLETO")
        print("=" * 80)
        
        total_users = 0
        total_projects = len(self.results)
        
        for project_name, data in self.results.items():
            print(f"\n🎯 PROGETTO: {project_name}")
            print("-" * 50)
            
            # Schema info
            schema = data.get('schema', {})
            print(f"📋 Tabelle trovate: {len(schema.get('tables_found', []))}")
            print(f"👥 Tabelle utenti: {len(schema.get('user_related_tables', []))}")
            print(f"📊 Record totali: {schema.get('total_records', 0)}")
            
            # Dati utenti
            users = data.get('users', [])
            print(f"👤 Utenti nella tabella 'users': {len(users)}")
            total_users += len(users)
            
            if users:
                print("   Dettagli utenti:")
                for user in users:
                    username = user.get('username', 'N/A')
                    email = user.get('email', 'N/A')
                    role = user.get('role', user.get('role_name', 'N/A'))
                    is_active = user.get('is_active', 'N/A')
                    created_at = user.get('created_at', 'N/A')
                    
                    print(f"     👤 {username} | 📧 {email} | 🏷️ {role} | 📈 {is_active} | 📅 {created_at}")
            
            # Altre tabelle con dati utenti
            all_tables = data.get('all_tables', {})
            if all_tables:
                print(f"📋 Altre tabelle con dati:")
                for table_name, table_data in all_tables.items():
                    if table_name != 'users':
                        print(f"     📊 {table_name}: {len(table_data)} record")
        
        print(f"\n📊 RIEPILOGO FINALE:")
        print(f"   🎯 Progetti interrogati: {total_projects}")
        print(f"   👥 Utenti totali trovati: {total_users}")
        print(f"   📅 Data interrogazione: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    def save_results_to_file(self, filename: str = None):
        """Salva i risultati in un file JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"supabase_users_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Risultati salvati in: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Errore salvataggio: {e}")
            return None
    
    def export_to_excel(self, filename: str = None):
        """Esporta i dati utenti in Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"supabase_users_export_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for project_name, data in self.results.items():
                    users = data.get('users', [])
                    if users:
                        df = pd.DataFrame(users)
                        df.to_excel(writer, sheet_name=project_name, index=False)
                        print(f"✅ Dati {project_name} esportati in Excel")
            
            print(f"\n📊 Export Excel completato: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Errore export Excel: {e}")
            return None

def main():
    """Funzione principale"""
    print("🔍 SCRIPT INTERROGAZIONE COMPLETA DATABASE SUPABASE")
    print("📊 Ottiene TUTTI i dati degli utenti da tutti i progetti")
    print("=" * 80)
    
    # Inizializza il query manager
    query_manager = SupabaseUserQuery()
    
    # Interroga tutti i progetti
    query_manager.query_all_projects()
    
    # Genera report
    query_manager.generate_report()
    
    # Salva risultati
    json_file = query_manager.save_results_to_file()
    excel_file = query_manager.export_to_excel()
    
    print(f"\n🎉 COMPLETATO!")
    print(f"📄 Report JSON: {json_file}")
    print(f"📊 Export Excel: {excel_file}")
    
    return query_manager.results

if __name__ == "__main__":
    results = main()
