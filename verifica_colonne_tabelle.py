#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🔍 VERIFICA COLONNE TABELLE NUOVE ===")

# Verifica incroci_account
try:
    response = sm.supabase.table('incroci_account').select('*').limit(1).execute()
    print("📋 Tabella incroci_account:")
    if response.data:
        for key in response.data[0].keys():
            print(f"   - {key}")
    else:
        print("   (vuota)")
except Exception as e:
    print(f"❌ Errore incroci_account: {e}")

print()

# Verifica incroci_bonus
try:
    response = sm.supabase.table('incroci_bonus').select('*').limit(1).execute()
    print("📋 Tabella incroci_bonus:")
    if response.data:
        for key in response.data[0].keys():
            print(f"   - {key}")
    else:
        print("   (vuota)")
except Exception as e:
    print(f"❌ Errore incroci_bonus: {e}")

print()

# Prova inserimento con colonne corrette
print("🧪 Test inserimento con colonne corrette...")

# Test incroci_account
try:
    test_account = {
        'incrocio_id': 'test',
        'account_id': 999,
        'tipo_posizione': 'long',
        'broker': 'Test',
        'piattaforma': 'MT5',
        'numero_conto': 'TEST999',
        'volume_posizione': 1.0,
        'stato_posizione': 'aperta'
    }
    
    response = sm.supabase.table('incroci_account').insert(test_account).execute()
    if response.data:
        print("✅ Inserimento incroci_account riuscito!")
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('account_id', 999).execute()
    else:
        print("❌ Inserimento incroci_account fallito")
        
except Exception as e:
    print(f"❌ Errore test incroci_account: {e}")

# Test incroci_bonus
try:
    test_bonus = {
        'incrocio_id': 'test',
        'tipo_bonus': 'Test',
        'importo_bonus': 100.0,
        'valuta_bonus': 'USD',
        'stato_bonus': 'attivo'
    }
    
    response = sm.supabase.table('incroci_bonus').insert(test_bonus).execute()
    if response.data:
        print("✅ Inserimento incroci_bonus riuscito!")
        # Rimuovi test
        sm.supabase.table('incroci_bonus').delete().eq('tipo_bonus', 'Test').execute()
    else:
        print("❌ Inserimento incroci_bonus fallito")
        
except Exception as e:
    print(f"❌ Errore test incroci_bonus: {e}")
