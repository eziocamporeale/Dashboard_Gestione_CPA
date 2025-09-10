#!/usr/bin/env python3
"""
🔍 SCRIPT SPECIFICO PER INTERROGARE IL DATABASE CPA
📊 Ottiene TUTTI i dati degli utenti dal progetto Dashboard_Gestione_CPA
Creato da Ezio Camporeale
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

class CPADatabaseQuery:
    """Classe per interrogare il database CPA usando le variabili ambiente"""
    
    def __init__(self):
        self.results = {}
        self.supabase_client = None
        
    def init_supabase_client(self):
        """Inizializza il client Supabase usando le variabili ambiente"""
        try:
            from supabase import create_client, Client
            
            # Leggi le variabili ambiente
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                print("❌ Variabili ambiente SUPABASE_URL e SUPABASE_KEY non configurate")
                print("💡 Configura le variabili ambiente per il progetto CPA:")
                print("   export SUPABASE_URL='https://your-project.supabase.co'")
                print("   export SUPABASE_KEY='your-anon-key'")
                return False
            
            self.supabase_client = create_client(supabase_url, supabase_key)
            print(f"✅ Client Supabase CPA inizializzato")
            print(f"   URL: {supabase_url}")
            print(f"   Key: {supabase_key[:20]}...")
            
            return True
            
        except ImportError:
            print("❌ Supabase non installato. Installa con: pip install supabase")
            return False
        except Exception as e:
            print(f"❌ Errore inizializzazione client CPA: {e}")
            return False
    
    def test_connection(self):
        """Testa la connessione al database CPA"""
        if not self.supabase_client:
            return False
        
        try:
            print("\n🔍 Test connessione database CPA...")
            
            # Prova a fare una query semplice
            response = self.supabase_client.table('users').select('count', count='exact').execute()
            
            print(f"✅ Connessione riuscita!")
            print(f"   Record nella tabella 'users': {response.count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
    
    def query_all_users(self) -> List[Dict[str, Any]]:
        """Interroga tutti gli utenti dal database CPA"""
        if not self.supabase_client:
            return []
        
        try:
            print("\n👥 Interrogazione tutti gli utenti CPA...")
            
            # Query completa per ottenere tutti gli utenti con informazioni sui ruoli
            response = self.supabase_client.table('users').select(
                'id, username, email, full_name, first_name, last_name, '
                'is_active, role_id, created_at, updated_at, '
                'roles(name, description, permissions)'
            ).execute()
            
            if response.data:
                print(f"✅ Trovati {len(response.data)} utenti")
                return response.data
            else:
                print("📭 Nessun utente trovato")
                return []
                
        except Exception as e:
            print(f"❌ Errore interrogazione utenti: {e}")
            return []
    
    def query_user_roles(self) -> List[Dict[str, Any]]:
        """Interroga tutti i ruoli dal database CPA"""
        if not self.supabase_client:
            return []
        
        try:
            print("\n🏷️ Interrogazione ruoli CPA...")
            
            response = self.supabase_client.table('roles').select('*').execute()
            
            if response.data:
                print(f"✅ Trovati {len(response.data)} ruoli")
                return response.data
            else:
                print("📭 Nessun ruolo trovato")
                return []
                
        except Exception as e:
            print(f"❌ Errore interrogazione ruoli: {e}")
            return []
    
    def query_all_tables(self) -> Dict[str, List[Dict[str, Any]]]:
        """Interroga tutte le tabelle del database CPA"""
        if not self.supabase_client:
            return {}
        
        try:
            print("\n📋 Interrogazione tutte le tabelle CPA...")
            
            # Tabelle che potrebbero esistere nel database CPA
            tables_to_check = [
                'users', 'roles', 'permissions', 'user_roles', 'user_permissions',
                'clienti', 'incroci', 'broker_links', 'system_users',
                'profiles', 'accounts', 'sessions', 'activity_logs'
            ]
            
            results = {}
            
            for table_name in tables_to_check:
                try:
                    # Prova a contare i record
                    count_response = self.supabase_client.table(table_name).select('count', count='exact').execute()
                    
                    if count_response.count is not None:
                        # Se la tabella esiste, ottieni alcuni record
                        data_response = self.supabase_client.table(table_name).select('*').limit(5).execute()
                        results[table_name] = {
                            'count': count_response.count,
                            'sample_data': data_response.data if data_response.data else []
                        }
                        print(f"   ✅ {table_name}: {count_response.count} record")
                    else:
                        print(f"   📭 {table_name}: vuota")
                        
                except Exception as e:
                    print(f"   ❌ {table_name}: errore - {e}")
            
            return results
            
        except Exception as e:
            print(f"❌ Errore interrogazione tabelle: {e}")
            return {}
    
    def analyze_database_structure(self):
        """Analizza la struttura del database CPA"""
        print("\n🔍 ANALISI STRUTTURA DATABASE CPA")
        print("=" * 50)
        
        # Test connessione
        if not self.test_connection():
            return
        
        # Interroga utenti
        users = self.query_all_users()
        
        # Interroga ruoli
        roles = self.query_user_roles()
        
        # Interroga tutte le tabelle
        all_tables = self.query_all_tables()
        
        # Salva risultati
        self.results = {
            'project': 'Dashboard_Gestione_CPA',
            'timestamp': datetime.now().isoformat(),
            'users': users,
            'roles': roles,
            'all_tables': all_tables,
            'summary': {
                'total_users': len(users),
                'total_roles': len(roles),
                'total_tables': len(all_tables),
                'total_records': sum(table_info['count'] for table_info in all_tables.values())
            }
        }
    
    def generate_detailed_report(self):
        """Genera un report dettagliato dei risultati"""
        print("\n📊 REPORT DETTAGLIATO DATABASE CPA")
        print("=" * 60)
        
        if not self.results:
            print("❌ Nessun dato da mostrare")
            return
        
        summary = self.results.get('summary', {})
        print(f"📊 RIEPILOGO GENERALE:")
        print(f"   👥 Utenti totali: {summary.get('total_users', 0)}")
        print(f"   🏷️ Ruoli totali: {summary.get('total_roles', 0)}")
        print(f"   📋 Tabelle totali: {summary.get('total_tables', 0)}")
        print(f"   📊 Record totali: {summary.get('total_records', 0)}")
        
        # Dettagli utenti
        users = self.results.get('users', [])
        if users:
            print(f"\n👥 DETTAGLI UTENTI ({len(users)}):")
            print("-" * 40)
            
            for i, user in enumerate(users, 1):
                print(f"{i:2d}. 👤 {user.get('username', 'N/A')}")
                print(f"     📧 Email: {user.get('email', 'N/A')}")
                print(f"     👤 Nome: {user.get('full_name', user.get('first_name', 'N/A') + ' ' + user.get('last_name', ''))}")
                print(f"     🏷️ Ruolo: {user.get('role_id', 'N/A')}")
                print(f"     📈 Attivo: {'✅ Sì' if user.get('is_active') else '❌ No'}")
                print(f"     📅 Creato: {user.get('created_at', 'N/A')}")
                print(f"     🔄 Aggiornato: {user.get('updated_at', 'N/A')}")
                
                # Informazioni ruolo se disponibili
                roles_info = user.get('roles')
                if roles_info:
                    print(f"     🏢 Ruolo dettagli: {roles_info.get('name', 'N/A')} - {roles_info.get('description', 'N/A')}")
                
                print()
        
        # Dettagli ruoli
        roles = self.results.get('roles', [])
        if roles:
            print(f"\n🏷️ DETTAGLI RUOLI ({len(roles)}):")
            print("-" * 40)
            
            for i, role in enumerate(roles, 1):
                print(f"{i:2d}. 🏷️ {role.get('name', 'N/A')}")
                print(f"     📝 Descrizione: {role.get('description', 'N/A')}")
                print(f"     🔑 Permessi: {role.get('permissions', 'N/A')}")
                print()
        
        # Dettagli tabelle
        all_tables = self.results.get('all_tables', {})
        if all_tables:
            print(f"\n📋 DETTAGLI TABELLE ({len(all_tables)}):")
            print("-" * 40)
            
            for table_name, table_info in all_tables.items():
                print(f"📊 {table_name}: {table_info['count']} record")
                
                # Mostra alcuni dati di esempio
                sample_data = table_info.get('sample_data', [])
                if sample_data:
                    print(f"   📄 Esempio dati:")
                    for j, record in enumerate(sample_data[:2], 1):  # Mostra solo i primi 2
                        print(f"      {j}. {record}")
                    if len(sample_data) > 2:
                        print(f"      ... e altri {len(sample_data) - 2} record")
                print()
    
    def save_results(self, filename: str = None):
        """Salva i risultati in un file JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cpa_database_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Risultati CPA salvati in: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Errore salvataggio: {e}")
            return None
    
    def export_users_to_excel(self, filename: str = None):
        """Esporta i dati utenti in Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cpa_users_export_{timestamp}.xlsx"
        
        try:
            users = self.results.get('users', [])
            if not users:
                print("❌ Nessun utente da esportare")
                return None
            
            df = pd.DataFrame(users)
            df.to_excel(filename, index=False, engine='openpyxl')
            
            print(f"\n📊 Export Excel CPA completato: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Errore export Excel: {e}")
            return None

def main():
    """Funzione principale"""
    print("🔍 SCRIPT INTERROGAZIONE DATABASE CPA")
    print("📊 Ottiene TUTTI i dati degli utenti dal progetto Dashboard_Gestione_CPA")
    print("=" * 70)
    
    # Inizializza il query manager
    query_manager = CPADatabaseQuery()
    
    # Inizializza client Supabase
    if not query_manager.init_supabase_client():
        print("\n❌ Impossibile inizializzare il client Supabase")
        print("💡 Assicurati di aver configurato le variabili ambiente:")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_KEY='your-anon-key'")
        return None
    
    # Analizza il database
    query_manager.analyze_database_structure()
    
    # Genera report dettagliato
    query_manager.generate_detailed_report()
    
    # Salva risultati
    json_file = query_manager.save_results()
    excel_file = query_manager.export_users_to_excel()
    
    print(f"\n🎉 ANALISI CPA COMPLETATA!")
    if json_file:
        print(f"📄 Report JSON: {json_file}")
    if excel_file:
        print(f"📊 Export Excel: {excel_file}")
    
    return query_manager.results

if __name__ == "__main__":
    results = main()
