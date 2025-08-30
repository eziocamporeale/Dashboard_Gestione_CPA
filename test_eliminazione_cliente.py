#!/usr/bin/env python3
"""
Test semplice per verificare l'eliminazione clienti da Supabase
"""

from supabase_manager import SupabaseManager

def test_eliminazione_cliente():
    print("=== 🧪 TEST ELIMINAZIONE CLIENTE ===")
    
    try:
        # 1. Connessione a Supabase
        sb = SupabaseManager()
        print("✅ SupabaseManager inizializzato")
        
        # 2. Recupera tutti i clienti
        clienti = sb.get_clienti()
        print(f"📊 Clienti totali: {len(clienti)}")
        
        if len(clienti) == 0:
            print("❌ Nessun cliente presente per il test")
            return False
        
        # 3. Mostra il primo cliente
        primo_cliente = clienti[0]
        print(f"🔍 Primo cliente: {primo_cliente['nome_cliente']} (ID: {primo_cliente['id']})")
        
        # 4. Test eliminazione
        print("🔄 Tentativo eliminazione...")
        success, message = sb.delete_cliente(primo_cliente['id'])
        
        print(f"📋 Risultato: {message}")
        
        if success:
            print("✅ ELIMINAZIONE RIUSCITA!")
            
            # 5. Verifica post-eliminazione
            clienti_dopo = sb.get_clienti()
            print(f"📊 Clienti dopo eliminazione: {len(clienti_dopo)}")
            
            return True
        else:
            print("❌ ELIMINAZIONE FALLITA!")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    test_eliminazione_cliente()
