#!/usr/bin/env python3
"""
💰 CREAZIONE WALLET PER CLIENTE TEST
Script per creare il wallet mancante per il cliente TEST
"""

import sys
import os
import logging
from datetime import datetime

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_wallet():
    """Crea il wallet per il cliente TEST"""
    
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
        
        # Trova il cliente TEST
        logger.info("🔍 Ricerca cliente TEST...")
        clienti_response = supabase_manager.supabase.table('clienti').select('*').eq('email', 'test@test.it').eq('nome_cliente', 'TEST').execute()
        
        if not clienti_response.data:
            logger.error("❌ Cliente TEST non trovato")
            return
        
        cliente = clienti_response.data[0]
        logger.info(f"✅ Cliente TEST trovato: {cliente['nome_cliente']} (ID: {cliente['id']})")
        
        # Verifica se il wallet esiste già
        logger.info("🔍 Verifica wallet esistente...")
        wallets_response = supabase_manager.supabase.table('wallet_collaboratori').select('*').execute()
        
        wallet_address = cliente.get('wallet', '')
        if wallet_address:
            logger.info(f"💰 Wallet address del cliente: {wallet_address}")
            
            # Controlla se esiste già un wallet con questo indirizzo
            existing_wallet = None
            for wallet in wallets_response.data:
                if wallet.get('note') and 'Wallet:' in wallet.get('note', ''):
                    note_wallet = wallet.get('note', '').split('Wallet:')[1].split('|')[0].strip()
                    if note_wallet == wallet_address:
                        existing_wallet = wallet
                        break
            
            if existing_wallet:
                logger.info(f"✅ Wallet già esistente: {existing_wallet['nome_wallet']}")
                return
            
            # Crea nuovo wallet
            logger.info("💰 Creazione nuovo wallet...")
            wallet_data = {
                'nome_wallet': f"Wallet {cliente['nome_cliente']}",
                'tipo_wallet': 'cliente',
                'saldo_attuale': 0.0,
                'valuta': 'USDT',
                'proprietario': cliente['nome_cliente'],
                'attivo': True,
                'note': f"Wallet: {wallet_address} | Cliente: {cliente['nome_cliente']} (ID: {cliente['id']})",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = supabase_manager.supabase.table('wallet_collaboratori').insert(wallet_data).execute()
            
            if response.data:
                logger.info(f"✅ Wallet creato con successo: {response.data[0]['nome_wallet']}")
                print(f"\n🎉 WALLET CREATO CON SUCCESSO!")
                print(f"📝 Nome: {response.data[0]['nome_wallet']}")
                print(f"👤 Proprietario: {response.data[0]['proprietario']}")
                print(f"🏷️ Tipo: {response.data[0]['tipo_wallet']}")
                print(f"💵 Saldo: {response.data[0]['saldo_attuale']} {response.data[0]['valuta']}")
                print(f"📄 Note: {response.data[0]['note']}")
            else:
                logger.error("❌ Errore nella creazione del wallet")
        else:
            logger.warning("⚠️ Cliente TEST non ha un wallet address")
        
    except Exception as e:
        logger.error(f"❌ Errore durante la creazione: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("💰 CREAZIONE WALLET PER CLIENTE TEST")
    print("="*80)
    
    create_test_wallet()
    
    print("\n✅ Operazione completata!")

