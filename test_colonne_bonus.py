#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🧪 TEST COLONNE INCROCI_BONUS ===")

# Test con colonne diverse per identificare quelle corrette
colonne_test = [
    'incrocio_id', 'tipo', 'importo', 'valuta', 'stato', 'note',
    'tipo_bonus', 'importo_bonus', 'valuta_bonus', 'stato_bonus',
    'bonus_type', 'amount', 'currency', 'status', 'description'
]

for colonna in colonne_test:
    try:
        test_data = {
            'incrocio_id': '00000000-0000-0000-0000-000000000000'
        }
        
        # Aggiungi la colonna di test
        if colonna == 'incrocio_id':
            test_data[colonna] = '00000000-0000-0000-0000-000000000000'
        elif colonna in ['importo', 'importo_bonus', 'amount']:
            test_data[colonna] = 100.0
        else:
            test_data[colonna] = 'test'
        
        print(f"🧪 Test colonna: {colonna}")
        response = sm.supabase.table('incroci_bonus').insert(test_data).execute()
        
        if response.data:
            print(f"   ✅ Colonna {colonna} FUNZIONA!")
            print(f"   📊 Dati inseriti: {response.data}")
            # Rimuovi test
            sm.supabase.table('incroci_bonus').delete().eq('incrocio_id', '00000000-0000-0000-0000-000000000000').execute()
            print(f"   🗑️ Test record rimosso")
            break
        else:
            print(f"   ❌ Inserimento fallito")
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        continue

print("\n🎯 Test completato!")
