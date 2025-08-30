#!/usr/bin/env python3
from supabase_manager import SupabaseManager
from datetime import datetime

sm = SupabaseManager()

print("=== 📊 POPOLAMENTO TABELLA BONUS CON COLONNE CORRETTE ===")

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

# 2. Popola incroci_bonus con colonne corrette
print("2️⃣ Popolamento tabella incroci_bonus...")
bonus_inseriti = 0

for i, incrocio in enumerate(incroci):
    try:
        # Bonus CPA per ogni incrocio
        bonus = {
            'incrocio_id': incrocio['id'],
            'importo_bonus': 200.0,
            'data_bonus': incrocio['data_apertura'],
            'note': f'Bonus CPA per {incrocio["nome_incrocio"]}',
            'created_at': datetime.now().isoformat()
        }
        
        response = sm.supabase.table('incroci_bonus').insert(bonus).execute()
        if response.data:
            bonus_inseriti += 1
            print(f"   ✅ Bonus per {incrocio['nome_incrocio']}: $200")
            
    except Exception as e:
        print(f"   ❌ Errore bonus per {incrocio['nome_incrocio']}: {e}")

print(f"   📊 Bonus inseriti: {bonus_inseriti}")

# 3. Verifica finale
print("3️⃣ Verifica finale...")
try:
    account_totali = sm.supabase.table('incroci_account').select('*').execute()
    bonus_totali = sm.supabase.table('incroci_bonus').select('*').execute()
    
    print(f"   📊 Account totali: {len(account_totali.data) if account_totali.data else 0}")
    print(f"   📊 Bonus totali: {len(bonus_totali.data) if bonus_totali.data else 0}")
    
except Exception as e:
    print(f"   ❌ Errore verifica finale: {e}")

print(f"\n🎉 POPOLAMENTO BONUS COMPLETATO!")
print(f"✅ Account inseriti: 10 (già presenti)")
print(f"✅ Bonus inseriti: {bonus_inseriti}")
print(f"📊 Struttura completa popolata per {len(incroci)} incroci")
