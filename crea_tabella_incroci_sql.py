#!/usr/bin/env python3
"""
🏗️ CREAZIONE TABELLA INCROCI VIA SQL
📊 Crea la tabella incroci direttamente in Supabase
"""

from supabase_manager import SupabaseManager
import sqlite3
from datetime import datetime

def main():
    print("=== 🏗️ CREAZIONE TABELLA INCROCI VIA SQL ===")
    
    # 1. Connessione a Supabase
    print("1️⃣ Connessione a Supabase...")
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"   {message}")
    
    if not success:
        print("❌ Impossibile continuare senza connessione")
        return
    
    # 2. Creazione tabella incroci via SQL diretto
    print("2️⃣ Creazione tabella incroci via SQL...")
    try:
        # SQL per creare la tabella incroci
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS incroci (
            id SERIAL PRIMARY KEY,
            nome_incrocio TEXT NOT NULL,
            data_apertura DATE,
            data_chiusura DATE,
            stato TEXT,
            pair_trading TEXT,
            volume_trading REAL,
            note TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        print("   🔧 SQL per creare tabella incroci:")
        print("   " + create_table_sql)
        print("\n   💡 DEVI ESEGUIRE QUESTO SQL MANUALMENTE IN SUPABASE:")
        print("   1. Vai su supabase.com → Dashboard → SQL Editor")
        print("   2. Incolla il SQL sopra")
        print("   3. Esegui la query")
        print("   4. Dimmi quando hai finito e riprovo il ripristino")
        
        # Aspetta conferma utente
        input("\n   ⏸️ Premi INVIO quando hai creato la tabella in Supabase...")
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return
    
    # 3. Verifica che la tabella sia stata creata
    print("3️⃣ Verifica creazione tabella...")
    try:
        test_incrocio = {
            'nome_incrocio': 'TEST_VERIFICA',
            'data_apertura': '2025-08-30',
            'stato': 'test',
            'pair_trading': 'TEST/USD',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci').insert(test_incrocio).execute()
        if response.data:
            print("   ✅ Tabella incroci creata con successo!")
            # Rimuovi incrocio di test
            sm.supabase.table('incroci').delete().eq('nome_incrocio', 'TEST_VERIFICA').execute()
            print("   🧹 Incrocio di test rimosso")
            
            # 4. Ripristino incroci dal backup locale
            print("4️⃣ Ripristino 5 incroci dal backup locale...")
            backup_path = "/Users/ezio/Downloads/cpa_database_backup_20250829_225348.db"
            
            try:
                conn = sqlite3.connect(backup_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT id, nome_incrocio, data_apertura, data_chiusura, stato, pair_trading, volume_trading, note FROM incroci ORDER BY id')
                incroci = cursor.fetchall()
                
                print(f"   📊 Incroci trovati nel backup: {len(incroci)}")
                
                incroci_ripristinati = 0
                for incrocio in incroci:
                    try:
                        incrocio_data = {
                            'nome_incrocio': incrocio[1],
                            'data_apertura': incrocio[2],
                            'data_chiusura': incrocio[3],
                            'stato': incrocio[4],
                            'pair_trading': incrocio[5],
                            'volume_trading': incrocio[6] if incrocio[6] else 0,
                            'note': incrocio[7] if incrocio[7] else '',
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        response = sm.supabase.table('incroci').insert(incrocio_data).execute()
                        if response.data:
                            incroci_ripristinati += 1
                            print(f"   ✅ {incrocio[1]} - {incrocio[5]} - {incrocio[4]}")
                        else:
                            print(f"   ❌ {incrocio[1]}: errore inserimento")
                            
                    except Exception as e:
                        print(f"   ❌ Errore incrocio {incrocio[1]}: {e}")
                
                print(f"   📊 Incroci ripristinati: {incroci_ripristinati}/{len(incroci)}")
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Errore lettura backup locale: {e}")
                return
            
            # 5. Verifica finale
            print("5️⃣ Verifica finale...")
            try:
                incroci_finali = sm.supabase.table('incroci').select('*').execute()
                print(f"   📊 Incroci totali in Supabase: {len(incroci_finali.data) if incroci_finali.data else 0}")
                
                if incroci_finali.data:
                    print("   📋 Incroci presenti:")
                    for incrocio in incroci_finali.data:
                        print(f"      - {incrocio['nome_incrocio']} ({incrocio['pair_trading']}) - {incrocio['stato']}")
                        
            except Exception as e:
                print(f"   ❌ Errore verifica finale: {e}")
            
            print(f"\n🎉 RIPRISTINO INCROCI COMPLETATO!")
            print(f"✅ Tabella incroci creata")
            print(f"✅ Incroci ripristinati: {incroci_ripristinati}/{len(incroci)}")
            
        else:
            print("   ❌ Tabella incroci ancora non accessibile")
            print("   💡 Verifica di aver eseguito il SQL correttamente")
            
    except Exception as e:
        print(f"   ❌ Errore verifica: {e}")

if __name__ == "__main__":
    main()
