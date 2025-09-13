#!/usr/bin/env python3
"""
🐛 DEBUG WALLET BUG
Script per verificare il bug del wallet che si applica a tutti i clienti
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

def debug_wallet_bug():
    """Debug del bug del wallet"""
    
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
        
        # Recupera tutti i clienti
        logger.info("📋 Recupero clienti...")
        clienti_response = supabase_manager.supabase.table('clienti').select('*').execute()
        
        if clienti_response.data:
            print("\n" + "="*80)
            print("👥 CLIENTI CON WALLET:")
            print("="*80)
            
            for cliente in clienti_response.data:
                wallet_cliente = cliente.get('wallet', '')
                if wallet_cliente and wallet_cliente.strip():
                    print(f"👤 Cliente: {cliente.get('nome_cliente')}")
                    print(f"📧 Email: {cliente.get('email')}")
                    print(f"💰 Wallet: {wallet_cliente}")
                    print("-" * 40)
        
        # Recupera tutti i wallet
        logger.info("📋 Recupero wallet...")
        wallets_response = supabase_manager.supabase.table('wallet_collaboratori').select('*').execute()
        
        if wallets_response.data:
            print("\n" + "="*80)
            print("💰 WALLET NEL SISTEMA DEDICATO:")
            print("="*80)
            
            for wallet in wallets_response.data:
                print(f"🔑 ID: {wallet.get('id')}")
                print(f"📝 Nome: {wallet.get('nome_wallet')}")
                print(f"👤 Proprietario: {wallet.get('proprietario')}")
                print(f"🏷️ Tipo: {wallet.get('tipo_wallet')}")
                print(f"📄 Note: {wallet.get('note', 'N/A')}")
                print("-" * 40)
        
        # Test della funzione _get_wallet_info_from_dedicated_system
        print("\n" + "="*80)
        print("🧪 TEST FUNZIONE _get_wallet_info_from_dedicated_system:")
        print("="*80)
        
        # Simula la funzione problematica
        def test_get_wallet_info(wallet_address: str):
            """Test della funzione problematica"""
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
                    print(f"  - Wallet ID: {wallet.get('id')}")
                    print(f"    Nome: {wallet.get('nome_wallet')}")
                    print(f"    Note: {wallet.get('note', 'N/A')}")
                    
                    # PROBLEMA: Cerca wallet_address che non esiste
                    if wallet.get('wallet_address') == wallet_address.strip():
                        print(f"    ✅ TROVATO con wallet_address")
                        return wallet
                    else:
                        print(f"    ❌ Non trovato con wallet_address")
                
                return None
            except Exception as e:
                print(f"❌ Errore: {e}")
                return None
        
        # Test con wallet esistenti
        for cliente in clienti_response.data:
            wallet_cliente = cliente.get('wallet', '')
            if wallet_cliente and wallet_cliente.strip():
                print(f"\n🧪 Test per cliente {cliente.get('nome_cliente')} con wallet {wallet_cliente}")
                result = test_get_wallet_info(wallet_cliente)
                if result:
                    print(f"✅ Wallet trovato: {result.get('nome_wallet')}")
                else:
                    print(f"❌ Wallet NON trovato")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🐛 DEBUG WALLET BUG")
    print("="*80)
    
    debug_wallet_bug()
    
    print("\n✅ Debug completato!")
