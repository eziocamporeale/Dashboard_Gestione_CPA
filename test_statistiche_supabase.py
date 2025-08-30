#!/usr/bin/env python3
"""
Test script per statistiche clienti da Supabase
"""

from components.client_table import ClientTable

def test_statistiche():
    print("=== 🧪 TEST STATISTICHE SUPABASE ===")
    
    try:
        # 1. Crea ClientTable
        ct = ClientTable()
        print("✅ ClientTable creato")
        
        # 2. Recupera statistiche da Supabase
        stats = ct.get_statistiche_clienti()
        print("✅ Statistiche calcolate da Supabase")
        
        # 3. Mostra statistiche
        print("📊 Statistiche clienti:")
        print(f"  - Totale clienti: {stats['totale_clienti']}")
        print(f"  - Broker attivi: {stats['broker_attivi']}")
        print(f"  - Depositi totali: €{stats['depositi_totali']:,.2f}")
        print(f"  - CPA attive: {stats['cpa_attive']}")
        
        # 4. Verifica che siano 13 clienti
        if stats['totale_clienti'] == 13:
            print("🎉 PERFETTO! Statistiche sincronizzate con Supabase!")
        else:
            print(f"⚠️ ATTENZIONE: Attesi 13 clienti, trovati {stats['totale_clienti']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        return False

if __name__ == "__main__":
    test_statistiche()
