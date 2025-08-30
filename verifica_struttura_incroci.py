#!/usr/bin/env python3
from supabase_manager import SupabaseManager

sm = SupabaseManager()

print("=== 🔍 VERIFICA STRUTTURA ATTUALE TABELLA INCROCI ===")

try:
    response = sm.supabase.table('incroci').select('*').limit(1).execute()
    
    if response.data:
        print("📋 Colonne attuali:")
        for key, value in response.data[0].items():
            print(f"   - {key}: {type(value).__name__}")
            
        print(f"\n📊 Totale colonne: {len(response.data[0])}")
        
        # Verifica colonne specifiche
        colonne_necessarie = [
            'id', 'nome_incrocio', 'data_apertura', 'data_chiusura', 
            'stato', 'pair_trading', 'volume_trading', 'note',
            'created_at', 'updated_at'
        ]
        
        print(f"\n🔍 Verifica colonne necessarie:")
        for colonna in colonne_necessarie:
            if colonna in response.data[0]:
                print(f"   ✅ {colonna}")
            else:
                print(f"   ❌ {colonna} - MANCANTE")
                
    else:
        print("Tabella vuota")
        
except Exception as e:
    print(f"❌ Errore: {e}")
