#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🔍 VERIFICA SCHEMA FINALE ===")

# Prova inserimento con solo colonne essenziali
print("1️⃣ Test inserimento minimo...")
test_minimo = {
    'incrocio_id': '00000000-0000-0000-0000-000000000000'
}

try:
    response = sm.supabase.table('incroci_account').insert(test_minimo).execute()
    if response.data:
        print("✅ Inserimento minimo riuscito!")
        print(f"📊 Dati: {response.data}")
        # Rimuovi test
        sm.supabase.table('incroci_account').delete().eq('incrocio_id', '00000000-0000-0000-0000-000000000000').execute()
    else:
        print("❌ Inserimento fallito")
except Exception as e:
    print(f"❌ Errore: {e}")

print()

# Prova con colonne diverse
print("2️⃣ Test con colonne alternative...")
colonne_alternative = [
    'incrocio_id', 'account_id', 'tipo', 'broker', 'piattaforma', 
    'numero_conto', 'volume', 'stato', 'note', 'created_at', 'updated_at'
]

for colonna in colonne_alternative:
    try:
        test_data = {'incrocio_id': '00000000-0000-0000-0000-000000000000'}
        test_data[colonna] = 'test' if colonna != 'incrocio_id' else '00000000-0000-0000-0000-000000000000'
        
        response = sm.supabase.table('incroci_account').insert(test_data).execute()
        if response.data:
            print(f"✅ Colonna {colonna} funziona!")
            # Rimuovi test
            sm.supabase.table('incroci_account').delete().eq('incrocio_id', '00000000-0000-0000-0000-000000000000').execute()
            break
    except Exception as e:
        print(f"❌ Colonna {colonna}: {e}")
        continue
