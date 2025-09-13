#!/usr/bin/env python3
"""
💰 CREAZIONE WALLET MANCANTI
Script per creare i wallet mancanti per i clienti che hanno wallet address ma non wallet dedicati
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

def create_missing_wallets():
    """Crea i wallet mancanti per i clienti"""
    
    try:
        # Import dei componenti necessari
        from supabase_manager import SupabaseManager
        from components.wallet_transactions_manager import WalletTransactionsManager
        
        logger.info("🔍 Inizializzazione Supabase...")
        
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        if not supabase_manager.supabase:
            logger.error("❌ Supabase non configurato")
            return
        
        logger.info("✅ Supabase inizializzato correttamente")
        
        # Inizializza Wallet Manager
        wallet_manager = WalletTransactionsManager()
        
        # Recupera tutti i clienti con wallet
        logger.info("📋 Recupero clienti con wallet...")
        clienti_response = supabase_manager.supabase.table('clienti').select('*').execute()
        
        clienti_con_wallet = []
        for cliente in clienti_response.data:
            wallet_cliente = cliente.get('wallet', '')
            if wallet_cliente and wallet_cliente.strip():
                clienti_con_wallet.append(cliente)
        
        print(f"\n📊 Trovati {len(clienti_con_wallet)} clienti con wallet")
        
        # Recupera tutti i wallet esistenti
        logger.info("📋 Recupero wallet esistenti...")
        existing_wallets = wallet_manager.get_wallet_collaboratori()
        
        print(f"📊 Trovati {len(existing_wallets)} wallet esistenti")
        
        # Crea wallet mancanti
        wallets_created = 0
        wallets_updated = 0
        
        for cliente in clienti_con_wallet:
            wallet_address = cliente.get('wallet', '').strip()
            cliente_nome = cliente.get('nome_cliente', '')
            cliente_id = cliente.get('id', '')
            cliente_email = cliente.get('email', '')
            
            print(f"\n🔍 Processando cliente: {cliente_nome}")
            print(f"   📧 Email: {cliente_email}")
            print(f"   💰 Wallet: {wallet_address}")
            
            # Verifica se esiste già un wallet per questo indirizzo
            wallet_exists = False
            existing_wallet = None
            
            for wallet in existing_wallets:
                note = wallet.get('note', '')
                if note and 'Wallet:' in note:
                    note_wallet_address = note.split('Wallet:')[1].split('|')[0].strip()
                    if note_wallet_address == wallet_address:
                        wallet_exists = True
                        existing_wallet = wallet
                        break
            
            if wallet_exists:
                print(f"   ✅ Wallet già esistente: {existing_wallet.get('nome_wallet')}")
                
                # Verifica se il wallet è collegato al cliente corretto
                if cliente_id not in existing_wallet.get('note', ''):
                    print(f"   🔄 Aggiornando collegamento al cliente...")
                    
                    # Aggiorna il wallet per collegarlo al cliente corretto
                    updated_note = f"Wallet: {wallet_address} | Cliente: {cliente_nome} (ID: {cliente_id})"
                    
                    response = wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').update({
                        'proprietario': cliente_nome,
                        'nome_wallet': f"Wallet {cliente_nome}",
                        'note': updated_note,
                        'updated_at': datetime.now().isoformat()
                    }).eq('id', existing_wallet['id']).execute()
                    
                    if response.data:
                        print(f"   ✅ Wallet aggiornato con successo")
                        wallets_updated += 1
                    else:
                        print(f"   ❌ Errore aggiornamento wallet")
                else:
                    print(f"   ℹ️ Wallet già collegato al cliente corretto")
            else:
                print(f"   ➕ Creando nuovo wallet...")
                
                # Crea nuovo wallet con nome unico
                wallet_data = {
                    'nome_wallet': f"Wallet {cliente_nome} - {wallet_address[:8]}",
                    'tipo_wallet': 'cliente',
                    'saldo_attuale': 0.0,
                    'valuta': 'USDT',
                    'proprietario': cliente_nome,
                    'attivo': True,
                    'note': f"Wallet: {wallet_address} | Cliente: {cliente_nome} (ID: {cliente_id})",
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                response = wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').insert(wallet_data).execute()
                
                if response.data:
                    print(f"   ✅ Wallet creato con successo")
                    wallets_created += 1
                else:
                    print(f"   ❌ Errore creazione wallet")
        
        print(f"\n🎉 OPERAZIONE COMPLETATA!")
        print(f"   ➕ Wallet creati: {wallets_created}")
        print(f"   🔄 Wallet aggiornati: {wallets_updated}")
        
    except Exception as e:
        logger.error(f"❌ Errore durante la creazione: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("💰 CREAZIONE WALLET MANCANTI")
    print("="*80)
    
    create_missing_wallets()
    
    print("\n✅ Operazione completata!")
