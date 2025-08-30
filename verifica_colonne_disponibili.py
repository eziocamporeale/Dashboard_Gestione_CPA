#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🔍 VERIFICA COLONNE DISPONIBILI ===")

# Verifica incroci_account
print("1️⃣ Verifica colonne incroci_account...")
try:
    # Prova inserimento con solo colonne essenziali
    test_data = {
        'incrocio_id': '00000000-0000-0000-0000-000000000000',  # UUID valido
        'account_id': 999,
        'tipo': 'long'  # Provo senza _posizione
    }
    
    print(f"   🧪 Test inserimento con: {test_data}")
    response = sm.supabase.table('incroci_account').insert(test_data).execute()
    
    if response.data:
        print("   ✅ Inserimento riuscito!")
        print(f"   📊 Dati inseriti: {response.data}")
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('account_id', 999).execute()
        print("   🗑️ Test record rimosso")
    else:
        print("   ❌ Inserimento fallito")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print()

# Verifica incroci_bonus
print("2️⃣ Verifica colonne incroci_bonus...")
try:
    # Prova inserimento con solo colonne essenziali
    test_data = {
        'incrocio_id': '00000000-0000-0000-0000-000000000000',  # UUID valido
        'tipo': 'Test',  # Provo senza _bonus
        'importo': 100.0  # Provo senza _bonus
    }
    
    print(f"   🧪 Test inserimento con: {test_data}")
    response = sm.supabase.table('incroci_bonus').insert(test_data).execute()
    
    if response.data:
        print("   ✅ Inserimento riuscito!")
        print(f"   📊 Dati inseriti: {response.data}")
        # Rimuovi test
        sm.supabase.table('incroci_bonus').delete().eq('tipo', 'Test').execute()
        print("   🗑️ Test record rimosso")
    else:
        print("   ❌ Inserimento fallito")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print()

# Se entrambi i test falliscono, prova con nomi di colonne ancora più semplici
print("3️⃣ Test con nomi di colonne semplici...")
try:
    # Prova con nomi di colonne molto semplici
    test_semplice = {
        'incrocio_id': '00000000-0000-0000-0000-000000000000',
        'id': 999,
        'nome': 'Test'
    }
    
    print(f"   🧪 Test inserimento semplice: {test_semplice}")
    response = sm.supabase.table('incroci_account').insert(test_semplice).execute()
    
    if response.data:
        print("   ✅ Inserimento semplice riuscito!")
        print(f"   📊 Dati inseriti: {response.data}")
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('id', 999).execute()
        print("   🗑️ Test record rimosso")
    else:
        print("   ❌ Inserimento semplice fallito")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print()

# Se tutto fallisce, prova a vedere se le tabelle hanno colonne diverse
print("4️⃣ Verifica se le tabelle hanno colonne diverse...")
try:
    # Prova a vedere se ci sono colonne con nomi diversi
    test_colonne = {
        'incrocio_id': '00000000-0000-0000-0000-000000000000',
        'account_id': 999,
        'tipo_posizione': 'long',
        'broker': 'Test',
        'piattaforma': 'MT5',
        'numero_conto': 'TEST999',
        'volume_posizione': 1.0,
        'stato_posizione': 'aperta'
    }
    
    print(f"   🧪 Test inserimento completo: {test_colonne}")
    response = sm.supabase.table('incroci_account').insert(test_colonne).execute()
    
    if response.data:
        print("   ✅ Inserimento completo riuscito!")
        print(f"   📊 Dati inseriti: {response.data}")
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('account_id', 999).execute()
        print("   🗑️ Test record rimosso")
    else:
        print("   ❌ Inserimento completo fallito")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")
