#!/usr/bin/env python3
"""
Script per ripristinare l'incrocio mancante (ID 24) da Supabase
"""

import sqlite3
import json
from supabase_manager import SupabaseManager
from datetime import datetime

def ripristina_incrocio_mancante():
    print("=== 🔄 RIPRISTINO INCROCIO MANCANTE ===")
    
    try:
        # 1. Connessione al backup locale
        backup_path = "/Users/ezio/Downloads/cpa_database_backup_20250829_225348.db"
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # 2. Recupera l'incrocio mancante (ID 24)
        cursor.execute("""
            SELECT id, nome_incrocio, pair_trading, volume_trading, data_apertura, 
                   data_chiusura, stato, note, data_creazione
            FROM incroci 
            WHERE id = 24
        """)
        incrocio = cursor.fetchone()
        
        if not incrocio:
            print("❌ Incrocio ID 24 non trovato nel backup!")
            return False
        
        print(f"✅ Incrocio trovato nel backup: {incrocio[1]} ({incrocio[2]})")
        
        # 3. Recupera gli account associati
        cursor.execute("""
            SELECT id, tipo_posizione, broker, piattaforma, numero_conto, 
                   volume_posizione, note_posizione
            FROM incroci_account 
            WHERE incrocio_id = 24
        """)
        accounts = cursor.fetchall()
        
        print(f"✅ Account trovati: {len(accounts)}")
        
        # 4. Recupera i bonus associati
        cursor.execute("""
            SELECT id, importo_bonus, data_sblocco, note_bonus
            FROM incroci_bonus 
            WHERE incrocio_id = 24
        """)
        bonuses = cursor.fetchall()
        
        print(f"✅ Bonus trovati: {len(bonuses)}")
        
        conn.close()
        
        # 5. Connessione a Supabase
        sb = SupabaseManager()
        
        # 6. Inserisci l'incrocio
        incrocio_data = {
            'nome_incrocio': incrocio[1],
            'pair_trading': incrocio[2],
            'volume_trading': incrocio[3],
            'data_apertura': incrocio[4],
            'data_chiusura': incrocio[5],
            'stato': incrocio[6],
            'note': incrocio[7] or ''
        }
        
        print("🔄 Inserimento incrocio in Supabase...")
        result = sb.supabase.table('incroci').insert(incrocio_data).execute()
        
        if result.data:
            incrocio_id = result.data[0]['id']
            print(f"✅ Incrocio inserito con ID: {incrocio_id}")
            
            # 7. Inserisci gli account
            for account in accounts:
                account_data = {
                    'incrocio_id': incrocio_id,
                    'tipo_posizione': account[1],
                    'broker': account[2],
                    'piattaforma': account[3],
                    'numero_conto': account[4],
                    'volume_posizione': account[5]
                }
                
                result = sb.supabase.table('incroci_account').insert(account_data).execute()
                if result.data:
                    print(f"✅ Account {account[1]} inserito")
                else:
                    print(f"❌ Errore inserimento account {account[1]}")
            
            # 8. Inserisci i bonus
            for bonus in bonuses:
                bonus_data = {
                    'incrocio_id': incrocio_id,
                    'importo_bonus': bonus[1],
                    'data_bonus': bonus[2],
                    'note': bonus[3] or ''
                }
                
                result = sb.supabase.table('incroci_bonus').insert(bonus_data).execute()
                if result.data:
                    print(f"✅ Bonus €{bonus[1]} inserito")
                else:
                    print(f"❌ Errore inserimento bonus €{bonus[1]}")
            
            print("🎉 RIPRISTINO COMPLETATO!")
            return True
            
        else:
            print("❌ Errore inserimento incrocio in Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il ripristino: {e}")
        return False

if __name__ == "__main__":
    ripristina_incrocio_mancante()
