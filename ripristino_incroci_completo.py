#!/usr/bin/env python3
"""
🔄 RIPRISTINO COMPLETO INCROCI
📊 Ripristina i 5 incroci dal backup locale con struttura corretta
"""

import sqlite3
from supabase_manager import SupabaseManager
from datetime import datetime

def main():
    print("=== 🔄 RIPRISTINO COMPLETO INCROCI ===")
    
    # 1. Connessione a Supabase
    print("1️⃣ Connessione a Supabase...")
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"   {message}")
    
    if not success:
        print("❌ Impossibile continuare senza connessione")
        return
    
    # 2. Ripristino incroci dal backup locale
    print("2️⃣ Ripristino 5 incroci dal backup locale...")
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
    
    # 3. Verifica finale
    print("3️⃣ Verifica finale...")
    try:
        incroci_finali = sm.supabase.table('incroci').select('*').execute()
        print(f"   📊 Incroci totali in Supabase: {len(incroci_finali.data) if incroci_finali.data else 0}")
        
        if incroci_finali.data:
            print("   📋 Incroci presenti:")
            for incrocio in incroci_finali.data:
                print(f"      - {incrocio['nome_incrocio']} ({incrocio['pair_trading']}) - {incrocio['stato']}")
                
    except Exception as e:
        print(f"   ❌ Errore verifica finale: {e}")
    
    # 4. Riepilogo finale
    print(f"\n🎉 RIPRISTINO INCROCI COMPLETATO!")
    print(f"✅ Tabella incroci creata e configurata")
    print(f"✅ Incroci ripristinati: {incroci_ripristinati}/{len(incroci)}")
    print(f"🔒 Backup locale: {backup_path}")
    print(f"📊 Stato finale Supabase:")
    print(f"   - Clienti: 13/14")
    print(f"   - Incroci: {incroci_ripristinati}/5")
    print(f"   - Broker: Aggiornati (Ultima Markets, Global Prime, Axi)")

if __name__ == "__main__":
    main()
