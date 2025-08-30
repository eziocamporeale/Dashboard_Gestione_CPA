#!/usr/bin/env python3
"""
🏗️ CREAZIONE TABELLA INCROCI SUPABASE
📊 Crea la tabella e ripristina i 5 incroci del backup
"""

from supabase_manager import SupabaseManager
import sqlite3
from datetime import datetime

def main():
    print("=== 🏗️ CREAZIONE TABELLA INCROCI SUPABASE ===")
    
    # 1. Connessione a Supabase
    print("1️⃣ Connessione a Supabase...")
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"   {message}")
    
    if not success:
        print("❌ Impossibile continuare senza connessione")
        return
    
    # 2. Creazione tabella incroci via SQL
    print("2️⃣ Creazione tabella incroci...")
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
        
        # Esegui SQL via RPC (se disponibile) o prova inserimento diretto
        print("   🔧 Tentativo creazione tabella...")
        
        # Prova inserimento diretto per vedere se la tabella esiste
        test_incrocio = {
            'nome_incrocio': 'TEST_CREAZIONE',
            'data_apertura': '2025-08-30',
            'stato': 'test',
            'pair_trading': 'TEST/USD',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci').insert(test_incrocio).execute()
        if response.data:
            print("   ✅ Tabella incroci esiste già!")
            # Rimuovi incrocio di test
            sm.supabase.table('incroci').delete().eq('nome_incrocio', 'TEST_CREAZIONE').execute()
            print("   🧹 Incrocio di test rimosso")
        else:
            print("   ❌ Tabella incroci non accessibile")
            return
            
    except Exception as e:
        print(f"   ⚠️ Errore creazione tabella: {e}")
        print("   💡 Potrebbe essere necessario crearla manualmente in Supabase")
        return
    
    # 3. Ripristino incroci dal backup locale
    print("3️⃣ Ripristino 5 incroci dal backup locale...")
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
    
    # 4. Verifica finale
    print("4️⃣ Verifica finale...")
    try:
        incroci_finali = sm.supabase.table('incroci').select('*').execute()
        print(f"   📊 Incroci totali in Supabase: {len(incroci_finali.data) if incroci_finali.data else 0}")
        
        if incroci_finali.data:
            print("   📋 Incroci presenti:")
            for incrocio in incroci_finali.data:
                print(f"      - {incrocio['nome_incrocio']} ({incrocio['pair_trading']}) - {incrocio['stato']}")
                
    except Exception as e:
        print(f"   ❌ Errore verifica finale: {e}")
    
    print(f"\n🎉 CREAZIONE TABELLA INCROCI COMPLETATA!")
    print(f"✅ Tabella incroci creata/verificata")
    print(f"✅ Incroci ripristinati: {incroci_ripristinati}/{len(incroci)}")
    print(f"🔒 Backup locale: {backup_path}")

if __name__ == "__main__":
    main()
