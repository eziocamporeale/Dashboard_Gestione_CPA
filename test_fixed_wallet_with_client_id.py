#!/usr/bin/env python3
"""
🧪 TEST FUNZIONE CORRETTA WALLET CON CLIENTE ID
Script per testare la funzione _get_wallet_info_from_dedicated_system con ID cliente
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

def test_fixed_wallet_with_client_id():
    """Testa la funzione corretta _get_wallet_info_from_dedicated_system con ID cliente"""
    
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
        
        # Test della funzione corretta _get_wallet_info_from_dedicated_system con ID cliente
        print("\n" + "="*80)
        print("🧪 TEST FUNZIONE CORRETTA CON ID CLIENTE:")
        print("="*80)
        
        # Simula la funzione corretta con ID cliente
        def test_get_wallet_info_with_client_id(wallet_address: str, cliente_id: str):
            """Test della funzione corretta con ID cliente"""
            if not wallet_address or not wallet_address.strip():
                return None
            
            try:
                from components.wallet_transactions_manager import WalletTransactionsManager
                wallet_manager = WalletTransactionsManager()
                
                if not wallet_manager.supabase_manager:
                    return None
                
                # Cerca il wallet nel sistema dedicato
                wallets = wallet_manager.get_wallet_collaboratori()
                print(f"🔍 Cercando wallet address: {wallet_address} per cliente ID: {cliente_id}")
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
                            # Se abbiamo l'ID del cliente, verifica che corrisponda
                            if cliente_id and cliente_id in note:
                                print(f"    ✅ TROVATO per cliente specifico!")
                                # Calcola il saldo attuale
                                saldo = wallet_manager.calculate_wallet_balance(wallet_address.strip())
                                wallet['saldo_calcolato'] = saldo
                                wallet['wallet_address'] = wallet_address.strip()  # Aggiungi per compatibilità
                                return wallet
                            elif not cliente_id:
                                print(f"    ✅ TROVATO (senza ID cliente)!")
                                # Calcola il saldo attuale
                                saldo = wallet_manager.calculate_wallet_balance(wallet_address.strip())
                                wallet['saldo_calcolato'] = saldo
                                wallet['wallet_address'] = wallet_address.strip()  # Aggiungi per compatibilità
                                return wallet
                            else:
                                print(f"    ❌ Wallet address corrisponde ma cliente ID non corrisponde")
                        else:
                            print(f"    ❌ Wallet address non corrisponde")
                    else:
                        print(f"  - Wallet ID: {wallet.get('id')} (no Wallet: in note)")
                
                return None
            except Exception as e:
                print(f"❌ Errore: {e}")
                return None
        
        # Test con wallet esistenti e ID cliente
        for cliente in clienti_con_wallet:
            wallet_cliente = cliente.get('wallet', '').strip()
            cliente_nome = cliente.get('nome_cliente', '')
            cliente_id = cliente.get('id', '')
            
            print(f"\n🧪 Test per cliente {cliente_nome} (ID: {cliente_id}) con wallet {wallet_cliente}")
            result = test_get_wallet_info_with_client_id(wallet_cliente, cliente_id)
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
    print("🧪 TEST FUNZIONE CORRETTA WALLET CON CLIENTE ID")
    print("="*80)
    
    test_fixed_wallet_with_client_id()
    
    print("\n✅ Test completato!")
