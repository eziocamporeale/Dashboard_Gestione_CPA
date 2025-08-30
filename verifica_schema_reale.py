#!/usr/bin/env python3
from supabase_manager import SupabaseManager
import json

sm = SupabaseManager()

print("=== 🔍 VERIFICA SCHEMA REALE TABELLE ===")

# Verifica incroci_account
print("1️⃣ Verifica schema incroci_account...")
try:
    # Prova a vedere se la tabella esiste e ha colonne
    response = sm.supabase.table('incroci_account').select('*').limit(0).execute()
    print(f"   ✅ Tabella accessibile")
    print(f"   📊 Dati: {json.dumps(response.data, indent=2)}")
    
    # Prova inserimento con solo colonne essenziali
    test_data = {
        'incrocio_id': '00000000-0000-0000-0000-000000000000',  # UUID valido
        'account_id': 999,
        'tipo_posizione': 'long'
    }
    
    print(f"   🧪 Test inserimento con: {json.dumps(test_data, indent=2)}")
    response = sm.supabase.table('incroci_account').insert(test_data).execute()
    
    if response.data:
        print("   ✅ Inserimento riuscito!")
        print(f"   📊 Dati inseriti: {json.dumps(response.data, indent=2)}")
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('account_id', 999).execute()
        print("   🗑️ Test record rimosso")
    else:
        print("   ❌ Inserimento fallito")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print()

# Verifica incroci_bonus
print("2️⃣ Verifica schema incroci_bonus...")
try:
    # Prova a vedere se la tabella esiste e ha colonne
    response = sm.supabase.table('incroci_bonus').select('*').limit(0).execute()
    print(f"   ✅ Tabella accessibile")
    print(f"   📊 Dati: {json.dumps(response.data, indent=2)}")
    
    # Prova inserimento con solo colonne essenziali
    test_data = {
        'incrocio_id': '00000000-0000-0000-0000-000000000000',  # UUID valido
        'tipo_bonus': 'Test',
        'importo_bonus': 100.0
    }
    
    print(f"   🧪 Test inserimento con: {json.dumps(test_data, indent=2)}")
    response = sm.supabase.table('incroci_bonus').insert(test_data).execute()
    
    if response.data:
        print("   ✅ Inserimento riuscito!")
        print(f"   📊 Dati inseriti: {json.dumps(response.data, indent=2)}")
        # Rimuovi test
        sm.supabase.table('incroci_bonus').delete().eq('tipo_bonus', 'Test').execute()
        print("   🗑️ Test record rimosso")
    else:
        print("   ❌ Inserimento fallito")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print()

# Se entrambi i test falliscono, prova a vedere se le tabelle hanno nomi diversi
print("3️⃣ Verifica se le tabelle hanno nomi diversi...")
try:
    # Lista possibili nomi di tabelle
    possibili_tabelle = ['incroci_account', 'incroci_accounts', 'incroci_bonus', 'incroci_bonuses']
    
    for nome_tabella in possibili_tabelle:
        try:
            response = sm.supabase.table(nome_tabella).select('*').limit(0).execute()
            print(f"   ✅ Tabella {nome_tabella} accessibile")
            break
        except:
            continue
    else:
        print("   ❌ Nessuna tabella incroci trovata")
        
except Exception as e:
    print(f"   ❌ Errore verifica tabelle: {e}")
