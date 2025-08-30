#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🔍 VERIFICA STRUTTURA TABELLA INCROCI ===")

try:
    # Prova select semplice
    response = sm.supabase.table('incroci').select('*').limit(1).execute()
    print("✅ Tabella incroci accessibile")
    print(f"📊 Dati: {response.data}")
    
    if response.data:
        print("📋 Colonne disponibili:")
        for key in response.data[0].keys():
            print(f"   - {key}")
    
except Exception as e:
    print(f"❌ Errore accesso tabella: {e}")
    
    # Prova a vedere se la tabella esiste almeno
    try:
        response = sm.supabase.table('incroci').select('id').limit(0).execute()
        print("✅ Tabella esiste ma potrebbe avere colonne diverse")
    except Exception as e2:
        print(f"❌ Tabella non accessibile: {e2}")
