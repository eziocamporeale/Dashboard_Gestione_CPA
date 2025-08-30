#!/usr/bin/env python3
"""
🔄 RIPRISTINO COMPLETO SUPABASE
📊 Ripristina 14 clienti + 5 incroci con broker aggiornati
"""

import sqlite3
from supabase_manager import SupabaseManager
from datetime import datetime

def main():
    print("=== 🔄 RIPRISTINO COMPLETO SUPABASE ===")
    
    # 1. Connessione a Supabase
    print("1️⃣ Connessione a Supabase...")
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"   {message}")
    
    if not success:
        print("❌ Impossibile continuare senza connessione")
        return
    
    # 2. Lettura backup locale
    print("2️⃣ Lettura backup locale...")
    backup_path = "/Users/ezio/Downloads/cpa_database_backup_20250829_225348.db"
    
    try:
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Conta clienti e incroci
        cursor.execute('SELECT COUNT(*) FROM clienti')
        count_clienti = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM incroci')
        count_incroci = cursor.fetchone()[0]
        
        print(f"   ✅ Clienti nel backup: {count_clienti}")
        print(f"   ✅ Incroci nel backup: {count_incroci}")
        
    except Exception as e:
        print(f"   ❌ Errore lettura backup: {e}")
        return
    
    # 3. Aggiornamento broker (standardizzazione)
    print("3️⃣ Aggiornamento nomi broker...")
    broker_mapping = {
        'Ultima': 'Ultima Markets',
        'Global': 'Global Prime',
        'Altro': 'Altro'  # Mantieni Altro per Rocio Munoz
    }
    
    # 4. Pulizia Supabase (rimuovi tutto)
    print("4️⃣ Pulizia Supabase...")
    try:
        # Rimuovi tutti i clienti esistenti uno per uno
        clienti_esistenti = sm.get_clienti()
        if clienti_esistenti:
            for cliente in clienti_esistenti:
                try:
                    sm.supabase.table('clienti').delete().eq('id', cliente['id']).execute()
                except:
                    pass
            print(f"   ✅ Clienti esistenti rimossi: {len(clienti_esistenti)}")
        else:
            print("   ℹ️ Nessun cliente esistente da rimuovere")
        
        # Rimuovi tutti gli incroci esistenti (se esistono)
        try:
            incroci_esistenti = sm.supabase.table('incroci').select('*').execute()
            if incroci_esistenti.data:
                for incrocio in incroci_esistenti.data:
                    try:
                        sm.supabase.table('incroci').delete().eq('id', incrocio['id']).execute()
                    except:
                        pass
                print(f"   ✅ Incroci esistenti rimossi: {len(incroci_esistenti.data)}")
            else:
                print("   ℹ️ Nessun incrocio esistente da rimuovere")
        except:
            print("   ℹ️ Tabella incroci non trovata o vuota")
            
    except Exception as e:
        print(f"   ❌ Errore pulizia: {e}")
        return
    
    # 5. Ripristino clienti
    print("5️⃣ Ripristino 14 clienti...")
    cursor.execute('SELECT id, nome_cliente, email, broker, piattaforma, deposito, data_registrazione FROM clienti ORDER BY id')
    clienti = cursor.fetchall()
    
    clienti_ripristinati = 0
    for cliente in clienti:
        try:
            # Standardizza broker
            broker_originale = cliente[3]
            broker_standardizzato = broker_mapping.get(broker_originale, broker_originale)
            
            cliente_data = {
                'nome_cliente': cliente[1],
                'email': cliente[2],
                'broker': broker_standardizzato,
                'piattaforma': cliente[4],
                'numero_conto': str(cliente[0]),  # Usa ID come numero conto temporaneo
                'volume_posizione': cliente[5] if cliente[5] else 0,  # Deposito come volume
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            success, message = sm.add_cliente(cliente_data)
            if success:
                clienti_ripristinati += 1
                print(f"   ✅ {cliente[1]} - {broker_standardizzato}")
            else:
                print(f"   ❌ {cliente[1]}: {message}")
                
        except Exception as e:
            print(f"   ❌ Errore cliente {cliente[1]}: {e}")
    
    print(f"   📊 Clienti ripristinati: {clienti_ripristinati}/{len(clienti)}")
    
    # 6. Ripristino incroci (se la tabella esiste)
    print("6️⃣ Ripristino 5 incroci...")
    try:
        cursor.execute('SELECT id, nome_incrocio, data_apertura, data_chiusura, stato, pair_trading, volume_trading, note FROM incroci ORDER BY id')
        incroci = cursor.fetchall()
        
        incroci_ripristinati = 0
        for incrocio in incroci:
            try:
                # Verifica se la tabella incroci esiste in Supabase
                incrocio_data = {
                    'nome_incrocio': incrocio[1],
                    'data_apertura': incrocio[2],
                    'data_chiusura': incrocio[3],
                    'stato': incrocio[4],
                    'pair_trading': incrocio[5],
                    'volume_trading': incrocio[6],
                    'note': incrocio[7],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Prova a inserire incrocio
                response = sm.supabase.table('incroci').insert(incrocio_data).execute()
                if response.data:
                    incroci_ripristinati += 1
                    print(f"   ✅ {incrocio[1]} - {incrocio[5]}")
                else:
                    print(f"   ❌ {incrocio[1]}: errore inserimento")
                    
            except Exception as e:
                print(f"   ⚠️ {incrocio[1]}: tabella incroci non disponibile - {e}")
                break
        
        print(f"   📊 Incroci ripristinati: {incroci_ripristinati}/{len(incroci)}")
        
    except Exception as e:
        print(f"   ℹ️ Tabella incroci non trovata nel backup locale: {e}")
        incroci_ripristinati = 0
    
    # 7. Verifica finale
    print("7️⃣ Verifica finale...")
    clienti_finali = sm.get_clienti()
    print(f"   📊 Clienti in Supabase: {len(clienti_finali)}")
    
    # 8. Chiusura
    conn.close()
    print(f"\n🎉 RIPRISTINO COMPLETATO!")
    print(f"✅ Clienti: {clienti_ripristinati}/{len(clienti)}")
    print(f"✅ Incroci: {incroci_ripristinati}/{len(incroci)}")
    print(f"🔒 Backup originale: {backup_path}")
    print(f"💾 Backup Supabase: supabase_backup_20250830_114154.json")

if __name__ == "__main__":
    main()
