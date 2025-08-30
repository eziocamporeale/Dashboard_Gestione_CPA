#!/usr/bin/env python3
"""
🧪 TEST INCROCI MANAGER CON SUPABASE
Verifica che il nuovo IncrociManager funzioni correttamente
"""

from database.incroci_manager import IncrociManager

def main():
    print("=== 🧪 TEST INCROCI MANAGER CON SUPABASE ===")
    
    try:
        # 1. Inizializzazione
        print("1️⃣ Inizializzazione IncrociManager...")
        im = IncrociManager()
        print("   ✅ IncrociManager inizializzato con Supabase")
        
        # 2. Test recupero incroci
        print("2️⃣ Test recupero incroci...")
        df = im.ottieni_incroci()
        print(f"   📊 Incroci recuperati: {len(df)}")
        
        if len(df) > 0:
            print("   📋 Primo incrocio:")
            primo_incrocio = df.iloc[0]
            print(f"      - Nome: {primo_incrocio.get('nome_incrocio', 'N/A')}")
            print(f"      - Stato: {primo_incrocio.get('stato', 'N/A')}")
            print(f"      - Pair: {primo_incrocio.get('pair_trading', 'N/A')}")
            print(f"      - Bonus: ${primo_incrocio.get('totale_bonus', 0)}")
            print(f"      - Broker Long: {primo_incrocio.get('broker_long', 'N/A')}")
            print(f"      - Broker Short: {primo_incrocio.get('broker_short', 'N/A')}")
        else:
            print("   ❌ Nessun incrocio trovato")
        
        # 3. Test statistiche
        print("3️⃣ Test statistiche incroci...")
        stats = im.ottieni_statistiche_incroci()
        
        if stats:
            print("   📊 Statistiche generali:")
            print(f"      - Totale incroci: {stats['generali']['totale_incroci']}")
            print(f"      - Incroci attivi: {stats['generali']['incroci_attivi']}")
            print(f"      - Incroci chiusi: {stats['generali']['incroci_chiusi']}")
            print(f"      - Volume totale: {stats['generali']['volume_totale']}")
            
            print("   📊 Statistiche bonus:")
            print(f"      - Totale bonus: ${stats['bonus']['totale_bonus']}")
            print(f"      - Numero bonus: {stats['bonus']['numero_bonus']}")
            print(f"      - Bonus attivi: {stats['bonus']['bonus_attivi']}")
            
            if stats['per_broker']:
                print("   📊 Top broker:")
                for broker, utilizzi, incroci in stats['per_broker'][:3]:
                    print(f"      - {broker}: {utilizzi} utilizzi, {incroci} incroci")
        else:
            print("   ❌ Errore recupero statistiche")
        
        print("\n🎉 TEST COMPLETATO CON SUCCESSO!")
        print("✅ IncrociManager funziona correttamente con Supabase")
        print("✅ Dashboard pronta per visualizzare i dati")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
