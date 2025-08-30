#!/usr/bin/env python3
"""
🔄 RIPRISTINO COMPLETO SUPABASE
📊 Ripristina 14 clienti + 5 incroci con email con errori per duplicati
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
        'Altro': 'Altro'
    }
    
    # 4. Inserimento clienti mancanti con email con errori
    print("4️⃣ Inserimento clienti mancanti con email con errori...")
    
    # Lista clienti già inseriti (per evitare duplicati)
    clienti_esistenti = sm.get_clienti()
    email_esistenti = {cliente['email'] for cliente in clienti_esistenti}
    
    print(f"   📊 Clienti già presenti: {len(clienti_esistenti)}")
    print(f"   📧 Email esistenti: {email_esistenti}")
    
    # Clienti da inserire con email con errori
    clienti_da_inserire = [
        # Yuri Carrasco - Axi (email con errore)
        (20, 'Yuri Carrasco - Axi', 'yuricarrasco247@gmail.comm', 'Axi', 'MT5', 1050.0),
        # Miguel Angel Garcia - Axi (email con errore)
        (23, 'Miguel Angel Garcia - Axi', 'garciaroman.ma@gmail.comm', 'Axi', 'MT5', 1100.0),
        # Miguel Angel Garcia - Global (email con errore)
        (24, 'Miguel Angel Garcia - Global', 'garciaroman.ma@gmail.commm', 'Global Prime', 'MT4', 1053.0),
        # Nora Martinez - Global (email con errore)
        (26, 'Nora Martinez - Global', 'noramartinezlima9@gmail.comm', 'Global Prime', 'MT5', 1150.0),
        # Gabriel del Cristo - Global (email con errore)
        (28, 'Gabriel del Cristo - Global', 'cristo.manu@outlook.comm', 'Global Prime', 'MT5', 1050.0),
        # Rocio Munoz - Global (email con errore)
        (30, 'Rocio Munoz - Global', 'rocio.monuz@outlook.comm', 'Global Prime', 'MT5', 0.02)
    ]
    
    clienti_inseriti = 0
    for cliente in clienti_da_inserire:
        try:
            cliente_data = {
                'nome_cliente': cliente[1],
                'email': cliente[2],  # Email con errore per evitare duplicati
                'broker': broker_mapping.get(cliente[3], cliente[3]),
                'piattaforma': cliente[4],
                'numero_conto': str(cliente[0]),
                'volume_posizione': cliente[5] if cliente[5] else 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            success, message = sm.add_cliente(cliente_data)
            if success:
                clienti_inseriti += 1
                print(f"   ✅ {cliente[1]} - {cliente_data['broker']} (email: {cliente[2]})")
            else:
                print(f"   ❌ {cliente[1]}: {message}")
                
        except Exception as e:
            print(f"   ❌ Errore cliente {cliente[1]}: {e}")
    
    print(f"   📊 Clienti aggiuntivi inseriti: {clienti_inseriti}/{len(clienti_da_inserire)}")
    
    # 5. Creazione tabella incroci se non esiste
    print("5️⃣ Gestione tabella incroci...")
    try:
        # Prova a inserire un incrocio di test per vedere se la tabella esiste
        test_incrocio = {
            'nome_incrocio': 'TEST',
            'data_apertura': '2025-08-30',
            'stato': 'test',
            'pair_trading': 'TEST/USD',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci').insert(test_incrocio).execute()
        if response.data:
            print("   ✅ Tabella incroci esiste, rimuovo test...")
            # Rimuovi incrocio di test
            sm.supabase.table('incroci').delete().eq('nome_incrocio', 'TEST').execute()
            
            # 6. Ripristino incroci
            print("6️⃣ Ripristino 5 incroci...")
            cursor.execute('SELECT id, nome_incrocio, data_apertura, data_chiusura, stato, pair_trading, volume_trading, note FROM incroci ORDER BY id')
            incroci = cursor.fetchall()
            
            incroci_ripristinati = 0
            for incrocio in incroci:
                try:
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
                    
                    response = sm.supabase.table('incroci').insert(incrocio_data).execute()
                    if response.data:
                        incroci_ripristinati += 1
                        print(f"   ✅ {incrocio[1]} - {incrocio[5]}")
                    else:
                        print(f"   ❌ {incrocio[1]}: errore inserimento")
                        
                except Exception as e:
                    print(f"   ❌ Errore incrocio {incrocio[1]}: {e}")
            
            print(f"   📊 Incroci ripristinati: {incroci_ripristinati}/{len(incroci)}")
            
        else:
            print("   ❌ Tabella incroci non accessibile")
            
    except Exception as e:
        print(f"   ⚠️ Tabella incroci non disponibile: {e}")
        print("   💡 Potrebbe essere necessario crearla manualmente in Supabase")
    
    # 7. Verifica finale
    print("7️⃣ Verifica finale...")
    clienti_finali = sm.get_clienti()
    print(f"   📊 Clienti totali in Supabase: {len(clienti_finali)}")
    
    # 8. Chiusura
    conn.close()
    print(f"\n🎉 RIPRISTINO COMPLETO FINALIZZATO!")
    print(f"✅ Clienti totali: {len(clienti_finali)}")
    print(f"✅ Clienti aggiuntivi inseriti: {clienti_inseriti}")
    print(f"🔒 Backup originale: {backup_path}")
    print(f"💾 Backup Supabase: supabase_backup_20250830_114154.json")
    print(f"📝 Commit stabile: a01fb65")

if __name__ == "__main__":
    main()
