#!/usr/bin/env python3
from supabase_manager import SupabaseManager
from datetime import datetime

sm = SupabaseManager()

print("=== 📊 POPOLAMENTO TABELLE CON COLONNE CORRETTE ===")

# 1. Recupera i 5 incroci esistenti
print("1️⃣ Recupero incroci esistenti...")
try:
    response = sm.supabase.table('incroci').select('*').execute()
    incroci = response.data
    print(f"   📊 Incroci trovati: {len(incroci)}")
    
    if not incroci:
        print("   ❌ Nessun incrocio trovato")
        exit()
        
except Exception as e:
    print(f"   ❌ Errore recupero incroci: {e}")
    exit()

# 2. Popola incroci_account
print("2️⃣ Popolamento tabella incroci_account...")
account_inseriti = 0

for i, incrocio in enumerate(incroci):
    try:
        # Account LONG
        account_long = {
            'incrocio_id': incrocio['id'],
            'tipo_posizione': 'long',
            'broker': 'Ultima Markets',
            'piattaforma': 'MT5',
            'numero_conto': f'L{1000 + i}',
            'created_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci_account').insert(account_long).execute()
        if response.data:
            account_inseriti += 1
            print(f"   ✅ Account LONG per {incrocio['nome_incrocio']}")
        
        # Account SHORT
        account_short = {
            'incrocio_id': incrocio['id'],
            'tipo_posizione': 'short',
            'broker': 'Global Prime',
            'piattaforma': 'MT5',
            'numero_conto': f'S{2000 + i}',
            'created_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci_account').insert(account_short).execute()
        if response.data:
            account_inseriti += 1
            print(f"   ✅ Account SHORT per {incrocio['nome_incrocio']}")
            
    except Exception as e:
        print(f"   ❌ Errore account per {incrocio['nome_incrocio']}: {e}")

print(f"   📊 Account inseriti: {account_inseriti}")

# 3. Popola incroci_bonus (se le colonne esistono)
print("3️⃣ Popolamento tabella incroci_bonus...")
bonus_inseriti = 0

for i, incrocio in enumerate(incroci):
    try:
        # Prova con colonne minime
        bonus = {
            'incrocio_id': incrocio['id'],
            'tipo_bonus': 'CPA Welcome Bonus',
            'importo_bonus': 200.0,
            'valuta_bonus': 'USD',
            'stato_bonus': 'attivo',
            'created_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci_bonus').insert(bonus).execute()
        if response.data:
            bonus_inseriti += 1
            print(f"   ✅ Bonus per {incrocio['nome_incrocio']}: $200")
            
    except Exception as e:
        print(f"   ❌ Errore bonus per {incrocio['nome_incrocio']}: {e}")
        # Prova con colonne alternative
        try:
            bonus_alt = {
                'incrocio_id': incrocio['id'],
                'tipo': 'CPA Welcome Bonus',
                'importo': 200.0,
                'created_at': datetime.now().isoformat()
            }
            
            response = sm.supabase.table('incroci_bonus').insert(bonus_alt).execute()
            if response.data:
                bonus_inseriti += 1
                print(f"   ✅ Bonus (alt) per {incrocio['nome_incrocio']}: $200")
                
        except Exception as e2:
            print(f"   ❌ Errore bonus alternativo: {e2}")

print(f"   📊 Bonus inseriti: {bonus_inseriti}")

# 4. Verifica finale
print("4️⃣ Verifica finale...")
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
print(f"📊 Struttura completa popolata per {len(incroci)} incroci")
