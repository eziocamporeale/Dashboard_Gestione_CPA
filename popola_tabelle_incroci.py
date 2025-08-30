#!/usr/bin/env python3
"""
📊 POPOLAMENTO TABELLE INCROCI COMPLETE
🔗 Collega i 5 incroci esistenti con account e bonus
"""

from supabase_manager import SupabaseManager
from datetime import datetime

def main():
    print("=== 📊 POPOLAMENTO TABELLE INCROCI COMPLETE ===")
    
    # 1. Connessione a Supabase
    print("1️⃣ Connessione a Supabase...")
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"   {message}")
    
    if not success:
        print("❌ Impossibile continuare senza connessione")
        return
    
    # 2. Recupera i 5 incroci esistenti
    print("2️⃣ Recupero incroci esistenti...")
    try:
        response = sm.supabase.table('incroci').select('*').execute()
        incroci = response.data
        print(f"   📊 Incroci trovati: {len(incroci)}")
        
        if not incroci:
            print("   ❌ Nessun incrocio trovato")
            return
            
    except Exception as e:
        print(f"   ❌ Errore recupero incroci: {e}")
        return
    
    # 3. Popola incroci_account per ogni incrocio
    print("3️⃣ Popolamento tabella incroci_account...")
    
    account_inseriti = 0
    for incrocio in incroci:
        try:
            # Account LONG per ogni incrocio
            account_long = {
                'incrocio_id': incrocio['id'],
                'account_id': 100 + account_inseriti,  # ID fittizio
                'tipo_posizione': 'long',
                'broker': 'Ultima Markets',
                'piattaforma': 'MT5',
                'numero_conto': f'L{1000 + account_inseriti}',
                'volume_posizione': 1.0,
                'data_apertura_posizione': incrocio['data_apertura'],
                'stato_posizione': 'aperta',
                'note_posizione': f'Account long per {incrocio["nome_incrocio"]}',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = sm.supabase.table('incroci_account').insert(account_long).execute()
            if response.data:
                account_inseriti += 1
                print(f"   ✅ Account LONG per {incrocio['nome_incrocio']}")
            
            # Account SHORT per ogni incrocio
            account_short = {
                'incrocio_id': incrocio['id'],
                'account_id': 200 + account_inseriti,  # ID fittizio
                'tipo_posizione': 'short',
                'broker': 'Global Prime',
                'piattaforma': 'MT5',
                'numero_conto': f'S{2000 + account_inseriti}',
                'volume_posizione': 1.0,
                'data_apertura_posizione': incrocio['data_apertura'],
                'stato_posizione': 'aperta',
                'note_posizione': f'Account short per {incrocio["nome_incrocio"]}',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = sm.supabase.table('incroci_account').insert(account_short).execute()
            if response.data:
                account_inseriti += 1
                print(f"   ✅ Account SHORT per {incrocio['nome_incrocio']}")
                
        except Exception as e:
            print(f"   ❌ Errore account per {incrocio['nome_incrocio']}: {e}")
    
    print(f"   📊 Account inseriti: {account_inseriti}")
    
    # 4. Popola incroci_bonus per ogni incrocio
    print("4️⃣ Popolamento tabella incroci_bonus...")
    
    bonus_inseriti = 0
    for incrocio in incroci:
        try:
            # Bonus CPA per ogni incrocio
            bonus = {
                'incrocio_id': incrocio['id'],
                'tipo_bonus': 'CPA Welcome Bonus',
                'importo_bonus': 200.0,
                'valuta_bonus': 'USD',
                'data_sblocco': incrocio['data_apertura'],
                'stato_bonus': 'attivo',
                'note_bonus': f'Bonus CPA per {incrocio["nome_incrocio"]}',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = sm.supabase.table('incroci_bonus').insert(bonus).execute()
            if response.data:
                bonus_inseriti += 1
                print(f"   ✅ Bonus per {incrocio['nome_incrocio']}: $200")
                
        except Exception as e:
            print(f"   ❌ Errore bonus per {incrocio['nome_incrocio']}: {e}")
    
    print(f"   📊 Bonus inseriti: {bonus_inseriti}")
    
    # 5. Verifica finale
    print("5️⃣ Verifica finale...")
    try:
        account_totali = sm.supabase.table('incroci_account').select('*').execute()
        bonus_totali = sm.supabase.table('incroci_bonus').select('*').execute()
        
        print(f"   📊 Account totali: {len(account_totali.data) if account_totali.data else 0}")
        print(f"   📊 Bonus totali: {len(bonus_totali.data) if bonus_totali.data else 0}")
        
    except Exception as e:
        print(f"   ❌ Errore verifica finale: {e}")
    
    print(f"\n🎉 POPOLAMENTO COMPLETATO!")
    print(f"✅ Account inseriti: {account_inseriti}")
    print(f"✅ Bonus inseriti: {bonus_inseriti}")
    print(f"📊 Struttura completa creata per 5 incroci")

if __name__ == "__main__":
    main()
