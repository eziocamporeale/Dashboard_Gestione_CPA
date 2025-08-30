#!/usr/bin/env python3
"""
🔍 VERIFICA STRUTTURA SUPABASE
📋 Controlla le colonne delle tabelle per il ripristino
"""

from supabase_manager import SupabaseManager

def main():
    print("=== 🔍 VERIFICA STRUTTURA SUPABASE ===")
    
    # 1. Connessione
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"1️⃣ {message}")
    
    if not success:
        return
    
    # 2. Verifica tabella clienti
    print("\n2️⃣ Struttura tabella CLIENTI:")
    try:
        clienti = sm.get_clienti()
        if clienti:
            print(f"   📊 Clienti presenti: {len(clienti)}")
            print(f"   📋 Colonne: {list(clienti[0].keys())}")
            
            # Mostra primo cliente come esempio
            primo = clienti[0]
            print(f"   📝 Esempio primo cliente:")
            for key, value in primo.items():
                print(f"      {key}: {value}")
        else:
            print("   ℹ️ Nessun cliente presente")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # 3. Verifica tabella incroci
    print("\n3️⃣ Struttura tabella INCROCI:")
    try:
        incroci = sm.supabase.table('incroci').select('*').limit(1).execute()
        if incroci.data:
            print(f"   📊 Incroci presenti: {len(incroci.data)}")
            print(f"   📋 Colonne: {list(incroci.data[0].keys())}")
            
            # Mostra primo incrocio come esempio
            primo = incroci.data[0]
            print(f"   📝 Esempio primo incrocio:")
            for key, value in primo.items():
                print(f"      {key}: {value}")
        else:
            print("   ℹ️ Nessun incrocio presente")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    print("\n✅ Verifica struttura completata!")

if __name__ == "__main__":
    main()
