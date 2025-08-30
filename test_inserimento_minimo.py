#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🧪 TEST INSERIMENTO MINIMO ===")

# Test 1: Solo colonne essenziali per incroci_account
print("1️⃣ Test incroci_account con colonne minime...")
test_minimo = {
    'incrocio_id': 'test',
    'account_id': 999,
    'tipo_posizione': 'long',
    'broker': 'Test'
}

try:
    response = sm.supabase.table('incroci_account').insert(test_minimo).execute()
    if response.data:
        print("✅ Inserimento minimo riuscito!")
        print("📊 Dati inseriti:", response.data)
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('account_id', 999).execute()
    else:
        print("❌ Inserimento fallito")
except Exception as e:
    print(f"❌ Errore: {e}")

print()

# Test 2: Solo colonne essenziali per incroci_bonus
print("2️⃣ Test incroci_bonus con colonne minime...")
test_minimo_bonus = {
    'incrocio_id': 'test',
    'tipo_bonus': 'Test',
    'importo_bonus': 100.0
}

try:
    response = sm.supabase.table('incroci_bonus').insert(test_minimo_bonus).execute()
    if response.data:
        print("✅ Inserimento minimo riuscito!")
        print("📊 Dati inseriti:", response.data)
        # Rimuovi test
        sm.supabase.table('incroci_bonus').delete().eq('tipo_bonus', 'Test').execute()
    else:
        print("❌ Inserimento fallito")
except Exception as e:
    print(f"❌ Errore: {e}")

print()

# Test 3: Prova a vedere se le tabelle hanno colonne diverse
print("3️⃣ Verifica colonne reali...")
try:
    # Prova a vedere se ci sono colonne con nomi diversi
    test_colonne = {
        'incrocio_id': 'test',
        'account_id': 999,
        'tipo_posizione': 'long',
        'broker': 'Test',
        'piattaforma': 'MT5',
        'numero_conto': 'TEST999',
        'volume_posizione': 1.0,
        'stato': 'aperta'  # Provo senza _posizione
    }
    
    response = sm.supabase.table('incroci_account').insert(test_colonne).execute()
    if response.data:
        print("✅ Inserimento con colonne alternative riuscito!")
        print("📊 Dati inseriti:", response.data)
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('account_id', 999).execute()
    else:
        print("❌ Inserimento fallito")
except Exception as e:
    print(f"❌ Errore: {e}")
