#!/usr/bin/env python3
"""
🧪 TEST FUNZIONE CORRETTA WALLET
Script per testare la funzione _get_wallet_info_from_dedicated_system corretta
"""

import sys
import os
import logging

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fixed_wallet_function():
    """Testa la funzione corretta _get_wallet_info_from_dedicated_system"""
    
    try:
        # Import dei componenti necessari
        from supabase_manager import SupabaseManager
        
        logger.info("🔍 Inizializzazione Supabase...")
        
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        if not supabase_manager.supabase:
            logger.error("❌ Supabase non configurato")
            return
        
        logger.info("✅ Supabase inizializzato correttamente")
        
        # Recupera tutti i clienti con wallet
        logger.info("📋 Recupero clienti con wallet...")
        clienti_response = supabase_manager.supabase.table('clienti').select('*').execute()
        
        clienti_con_wallet = []
        for cliente in clienti_response.data:
            wallet_cliente = cliente.get('wallet', '')
            if wallet_cliente and wallet_cliente.strip():
                clienti_con_wallet.append(cliente)
        
        print(f"\n📊 Trovati {len(clienti_con_wallet)} clienti con wallet")
        
        # Test della funzione corretta _get_wallet_info_from_dedicated_system
        print("\n" + "="*80)
        print("🧪 TEST FUNZIONE CORRETTA _get_wallet_info_from_dedicated_system:")
        print("="*80)
        
        # Simula la funzione corretta
        def test_get_wallet_info_fixed(wallet_address: str):
            """Test della funzione corretta"""
            if not wallet_address or not wallet_address.strip():
                return None
            
            try:
                from components.wallet_transactions_manager import WalletTransactionsManager
                wallet_manager = WalletTransactionsManager()
                
                if not wallet_manager.supabase_manager:
                    return None
                
                # Cerca il wallet nel sistema dedicato
                wallets = wallet_manager.get_wallet_collaboratori()
                print(f"🔍 Cercando wallet address: {wallet_address}")
                print(f"📋 Wallet trovati: {len(wallets)}")
                
                for wallet in wallets:
                    # Cerca nel campo note che contiene il wallet address
                    note = wallet.get('note', '')
                    if note and 'Wallet:' in note:
                        note_wallet_address = note.split('Wallet:')[1].split('|')[0].strip()
                        print(f"  - Wallet ID: {wallet.get('id')}")
                        print(f"    Nome: {wallet.get('nome_wallet')}")
                        print(f"    Note: {note}")
                        print(f"    Wallet address estratto: {note_wallet_address}")
                        
                        if note_wallet_address == wallet_address.strip():
                            print(f"    ✅ TROVATO!")
                            # Calcola il saldo attuale
                            saldo = wallet_manager.calculate_wallet_balance(wallet_address.strip())
                            wallet['saldo_calcolato'] = saldo
                            wallet['wallet_address'] = wallet_address.strip()  # Aggiungi per compatibilità
                            return wallet
                        else:
                            print(f"    ❌ Non corrisponde")
                    else:
                        print(f"  - Wallet ID: {wallet.get('id')} (no Wallet: in note)")
                
                return None
            except Exception as e:
                print(f"❌ Errore: {e}")
                return None
        
        # Test con wallet esistenti
        for cliente in clienti_con_wallet:
            wallet_cliente = cliente.get('wallet', '').strip()
            cliente_nome = cliente.get('nome_cliente', '')
            
            print(f"\n🧪 Test per cliente {cliente_nome} con wallet {wallet_cliente}")
            result = test_get_wallet_info_fixed(wallet_cliente)
            if result:
                print(f"✅ Wallet trovato: {result.get('nome_wallet')}")
                print(f"   💰 Saldo: {result.get('saldo_calcolato', 0)}")
                print(f"   👤 Proprietario: {result.get('proprietario')}")
            else:
                print(f"❌ Wallet NON trovato")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 TEST FUNZIONE CORRETTA WALLET")
    print("="*80)
    
    test_fixed_wallet_function()
    
    print("\n✅ Test completato!")
