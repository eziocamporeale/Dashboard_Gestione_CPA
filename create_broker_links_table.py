#!/usr/bin/env python3
"""
Script per creare la tabella broker_links nel database Supabase
Creato da Ezio Camporeale per Dashboard Gestione CPA
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from supabase_manager import SupabaseManager

def create_broker_links_table():
    """Crea la tabella broker_links nel database Supabase"""
    
    print("🔧 Creazione tabella broker_links...")
    
    # Inizializza SupabaseManager
    supabase_manager = SupabaseManager()
    
    if not supabase_manager.is_configured:
        print("❌ Supabase non configurato!")
        print("📋 Configura le variabili ambiente SUPABASE_URL e SUPABASE_KEY")
        return False
    
    if not supabase_manager.supabase:
        print("❌ Client Supabase non disponibile!")
        return False
    
    try:
        # Leggi il file SQL
        sql_file = Path(__file__).parent / "database" / "create_broker_links_table.sql"
        
        if not sql_file.exists():
            print(f"❌ File SQL non trovato: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📄 Contenuto SQL letto correttamente")
        print("⚠️ ATTENZIONE: Questo script esegue SQL direttamente su Supabase")
        print("📋 Assicurati di aver configurato correttamente le credenziali")
        
        # Conferma dall'utente
        confirm = input("🤔 Vuoi procedere con la creazione della tabella? (s/N): ")
        if confirm.lower() != 's':
            print("❌ Operazione annullata dall'utente")
            return False
        
        # Esegui le query SQL
        # Dividi il contenuto in singole query
        queries = [q.strip() for q in sql_content.split(';') if q.strip()]
        
        for i, query in enumerate(queries, 1):
            if query:
                print(f"🔄 Esecuzione query {i}/{len(queries)}...")
                try:
                    # Per le query DDL, usiamo rpc se disponibile
                    result = supabase_manager.supabase.rpc('exec_sql', {'sql': query}).execute()
                    print(f"✅ Query {i} eseguita con successo")
                except Exception as e:
                    print(f"⚠️ Query {i} potrebbe essere già eseguita o non supportata: {e}")
                    # Continua con le altre query
                    continue
        
        print("✅ Creazione tabella broker_links completata!")
        
        # Test della tabella
        print("🧪 Test della tabella...")
        try:
            # Prova a inserire un record di test
            test_data = {
                'broker_name': 'Test Broker',
                'affiliate_link': 'https://test-broker.com/affiliate/test',
                'is_active': True
            }
            
            result = supabase_manager.supabase.table('broker_links').insert(test_data).execute()
            
            if result.data:
                print("✅ Test inserimento riuscito!")
                
                # Elimina il record di test
                test_id = result.data[0]['id']
                supabase_manager.supabase.table('broker_links').delete().eq('id', test_id).execute()
                print("✅ Record di test eliminato")
            else:
                print("❌ Test inserimento fallito")
                return False
                
        except Exception as e:
            print(f"❌ Errore durante il test: {e}")
            return False
        
        print("🎉 Tabella broker_links creata e testata con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la creazione della tabella: {e}")
        return False

def main():
    """Funzione principale"""
    print("🚀 CREAZIONE TABELLA BROKER_LINKS")
    print("=" * 50)
    
    success = create_broker_links_table()
    
    if success:
        print("\n✅ OPERAZIONE COMPLETATA CON SUCCESSO!")
        print("🔗 La tabella broker_links è ora disponibile nel database Supabase")
        print("📱 Puoi ora utilizzare la sezione Broker nel dashboard")
    else:
        print("\n❌ OPERAZIONE FALLITA!")
        print("🔍 Controlla i log sopra per dettagli sull'errore")
        print("📋 Assicurati che Supabase sia configurato correttamente")

if __name__ == "__main__":
    main()
