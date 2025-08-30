#!/usr/bin/env python3
"""
Script per ripristinare gli ultimi 2 incroci mancanti (ID 23 e 24) da Supabase
"""

import sqlite3
from supabase_manager import SupabaseManager

def ripristina_ultimi_incroci():
    print("=== 🔄 RIPRISTINO ULTIMI 2 INCROCI ===")
    
    try:
        # 1. Connessione al backup locale
        backup_path = "/Users/ezio/Downloads/cpa_database_backup_20250829_225348.db"
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # 2. Lista degli ID da ripristinare
        id_da_ripristinare = [23, 24]
        
        for incrocio_id in id_da_ripristinare:
            print(f"\n🔄 Ripristino incrocio ID {incrocio_id}...")
            
            # 3. Recupera l'incrocio
            cursor.execute("""
                SELECT id, nome_incrocio, pair_trading, volume_trading, data_apertura, 
                       data_chiusura, stato, note, data_creazione
                FROM incroci 
                WHERE id = ?
            """, (incrocio_id,))
            incrocio = cursor.fetchone()
            
            if not incrocio:
                print(f"❌ Incrocio ID {incrocio_id} non trovato nel backup!")
                continue
            
            print(f"✅ Incrocio trovato: {incrocio[1]} ({incrocio[2]})")
            
            # 4. Recupera gli account associati
            cursor.execute("""
                SELECT id, tipo_posizione, broker, piattaforma, numero_conto, 
                       volume_posizione, note_posizione
                FROM incroci_account 
                WHERE incrocio_id = ?
            """, (incrocio_id,))
            accounts = cursor.fetchall()
            
            print(f"✅ Account trovati: {len(accounts)}")
            
            # 5. Recupera i bonus associati
            cursor.execute("""
                SELECT id, importo_bonus, data_sblocco, note_bonus
                FROM incroci_bonus 
                WHERE incrocio_id = ?
            """, (incrocio_id,))
            bonuses = cursor.fetchall()
            
            print(f"✅ Bonus trovati: {len(bonuses)}")
            
            # 6. Connessione a Supabase
            sb = SupabaseManager()
            
            # 7. Inserisci l'incrocio
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
                nuovo_incrocio_id = result.data[0]['id']
                print(f"✅ Incrocio inserito con ID: {nuovo_incrocio_id}")
                
                # 8. Inserisci gli account
                for account in accounts:
                    account_data = {
                        'incrocio_id': nuovo_incrocio_id,
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
                
                # 9. Inserisci i bonus
                for bonus in bonuses:
                    bonus_data = {
                        'incrocio_id': nuovo_incrocio_id,
                        'importo_bonus': bonus[1],
                        'data_bonus': bonus[2],
                        'note': bonus[3] or ''
                    }
                    
                    result = sb.supabase.table('incroci_bonus').insert(bonus_data).execute()
                    if result.data:
                        print(f"✅ Bonus €{bonus[1]} inserito")
                    else:
                        print(f"❌ Errore inserimento bonus €{bonus[1]}")
                
                print(f"✅ Incrocio ID {incrocio_id} ripristinato con successo!")
            else:
                print(f"❌ Errore inserimento incrocio ID {incrocio_id} in Supabase")
        
        conn.close()
        
        print("\n🎉 RIPRISTINO COMPLETATO!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante il ripristino: {e}")
        return False

if __name__ == "__main__":
    ripristina_ultimi_incroci()
