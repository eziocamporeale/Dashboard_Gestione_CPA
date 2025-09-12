#!/usr/bin/env python3
"""
🔍 CONTROLLO WALLET CLIENTE TEST
Script per verificare se il wallet del cliente test è stato creato correttamente
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

def check_client_wallet():
    """Controlla se il wallet del cliente test è stato creato"""
    
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
            print("👥 CLIENTI TROVATI:")
            print("="*80)
            
            for cliente in clienti_response.data:
                print(f"🔑 ID: {cliente.get('id')}")
                print(f"👤 Nome: {cliente.get('nome_cliente')}")
                print(f"📧 Email: {cliente.get('email')}")
                print(f"💰 Wallet: {cliente.get('wallet', 'N/A')}")
                print("-" * 40)
        else:
            print("❌ Nessun cliente trovato")
        
        # Recupera tutti i wallet
        logger.info("📋 Recupero wallet...")
        wallets_response = supabase_manager.supabase.table('wallet_collaboratori').select('*').execute()
        
        if wallets_response.data:
            print("\n" + "="*80)
            print("💰 WALLET TROVATI:")
            print("="*80)
            
            for wallet in wallets_response.data:
                print(f"🔑 ID: {wallet.get('id')}")
                print(f"📝 Nome: {wallet.get('nome_wallet')}")
                print(f"👤 Proprietario: {wallet.get('proprietario')}")
                print(f"🏷️ Tipo: {wallet.get('tipo_wallet')}")
                print(f"💵 Saldo: {wallet.get('saldo_attuale')} {wallet.get('valuta')}")
                print(f"📄 Note: {wallet.get('note', 'N/A')}")
                print("-" * 40)
        else:
            print("❌ Nessun wallet trovato")
        
        # Verifica se ci sono wallet di clienti
        logger.info("🔍 Verifica wallet clienti...")
        client_wallets = [w for w in wallets_response.data if w.get('tipo_wallet') == 'cliente']
        
        if client_wallets:
            print(f"\n✅ Trovati {len(client_wallets)} wallet di clienti:")
            for wallet in client_wallets:
                print(f"  - {wallet.get('nome_wallet')} ({wallet.get('proprietario')})")
        else:
            print("\n❌ Nessun wallet di cliente trovato")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il controllo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 CONTROLLO WALLET CLIENTE TEST")
    print("="*80)
    
    check_client_wallet()
    
    print("\n✅ Controllo completato!")
