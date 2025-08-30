#!/usr/bin/env python3
"""
🧪 TEST COLONNE TABELLA INCROCI
🔍 Prova diversi nomi di colonne per identificare la struttura corretta
"""

from supabase_manager import SupabaseManager
from datetime import datetime

sm = SupabaseManager()

print("=== 🧪 TEST COLONNE TABELLA INCROCI ===")

# Prova con nomi di colonne alternativi
test_cases = [
    # Test 1: Nomi originali
    {
        'nome_incrocio': 'TEST1',
        'data_apertura': '2025-08-30',
        'stato': 'test',
        'pair_trading': 'TEST/USD'
    },
    # Test 2: Nomi in inglese
    {
        'name': 'TEST2',
        'open_date': '2025-08-30',
        'status': 'test',
        'pair': 'TEST/USD'
    },
    # Test 3: Nomi semplificati
    {
        'nome': 'TEST3',
        'data': '2025-08-30',
        'stato': 'test',
        'pair': 'TEST/USD'
    },
    # Test 4: Solo colonne essenziali
    {
        'nome': 'TEST4'
    }
]

for i, test_data in enumerate(test_cases, 1):
    print(f"\n🧪 Test {i}: {list(test_data.keys())}")
    try:
        response = sm.supabase.table('incroci').insert(test_data).execute()
        print(f"   ✅ SUCCESSO! Colonne corrette: {list(test_data.keys())}")
        print(f"   📊 Dati inseriti: {response.data}")
        
        # Rimuovi incrocio di test
        if 'nome' in test_data:
            sm.supabase.table('incroci').delete().eq('nome', test_data['nome']).execute()
        elif 'name' in test_data:
            sm.supabase.table('incroci').delete().eq('name', test_data['name']).execute()
        elif 'nome_incrocio' in test_data:
            sm.supabase.table('incroci').delete().eq('nome_incrocio', test_data['nome_incrocio']).execute()
            
        print("   🧹 Incrocio di test rimosso")
        break
        
    except Exception as e:
        print(f"   ❌ Fallito: {e}")
        continue

print("\n🔍 Se tutti i test falliscono, potrebbe essere necessario:")
print("1. Aspettare più tempo per la sincronizzazione schema")
print("2. Verificare i nomi delle colonne in Supabase Dashboard")
print("3. Refresh manuale dello schema cache")
