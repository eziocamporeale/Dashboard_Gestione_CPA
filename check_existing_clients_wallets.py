#!/usr/bin/env python3
"""
🔍 CONTROLLO CLIENTI ESISTENTI E CREAZIONE WALLET MANCANTI
Script per verificare clienti con wallet e creare wallet mancanti nel sistema dedicato
"""

import sys
import os
from datetime import datetime
import logging

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_existing_clients_wallets():
    """Controlla clienti esistenti e crea wallet mancanti"""
    
    try:
        # Import dei componenti necessari
        from supabase_manager import SupabaseManager
        from components.wallet_transactions_manager import WalletTransactionsManager
        
        logger.info("🔍 Inizializzazione componenti...")
        
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        if not supabase_manager.supabase:
            logger.error("❌ Supabase non configurato")
            return
        
        # Inizializza Wallet Manager
        wallet_manager = WalletTransactionsManager()
        if not wallet_manager.supabase_manager:
            logger.error("❌ Wallet Manager non configurato")
            return
        
        logger.info("✅ Componenti inizializzati correttamente")
        
        # Recupera tutti i clienti
        logger.info("📋 Recupero clienti esistenti...")
        clienti_response = supabase_manager.supabase.table('clienti').select('*').execute()
        
        if not clienti_response.data:
            logger.info("📋 Nessun cliente trovato")
            return
        
        clienti = clienti_response.data
        logger.info(f"📋 Trovati {len(clienti)} clienti")
        
        # Recupera wallet esistenti
        logger.info("💰 Recupero wallet esistenti...")
        existing_wallets = wallet_manager.get_wallet_collaboratori()
        
        # Estrai indirizzi wallet dal campo note
        existing_wallet_addresses = set()
        for w in existing_wallets:
            note = w.get('note') or ''
            if 'Wallet:' in note:
                try:
                    wallet_addr = note.split('Wallet:')[1].split('|')[0].strip()
                    existing_wallet_addresses.add(wallet_addr)
                except:
                    pass
        
        logger.info(f"💰 Trovati {len(existing_wallets)} wallet esistenti")
        
        # Controlla clienti con wallet
        clienti_con_wallet = []
        wallet_da_creare = []
        
        for cliente in clienti:
            wallet_address = cliente.get('wallet', '').strip()
            if wallet_address:
                clienti_con_wallet.append(cliente)
                
                # Verifica se il wallet esiste già nel sistema dedicato
                if wallet_address not in existing_wallet_addresses:
                    wallet_da_creare.append({
                        'cliente': cliente,
                        'wallet_address': wallet_address
                    })
        
        logger.info(f"👥 Clienti con wallet: {len(clienti_con_wallet)}")
        logger.info(f"💰 Wallet da creare: {len(wallet_da_creare)}")
        
        # Mostra clienti con wallet
        if clienti_con_wallet:
            print("\n" + "="*80)
            print("👥 CLIENTI CON WALLET:")
            print("="*80)
            
            for cliente in clienti_con_wallet:
                wallet_address = cliente.get('wallet', '').strip()
                wallet_exists = wallet_address in existing_wallet_addresses
                status = "✅ ESISTENTE" if wallet_exists else "❌ MANCANTE"
                
                print(f"👤 {cliente['nome_cliente']}")
                print(f"   📧 Email: {cliente['email']}")
                print(f"   💰 Wallet: {wallet_address}")
                print(f"   📊 Status: {status}")
                print(f"   🆔 ID Cliente: {cliente['id']}")
                print("-" * 40)
        
        # Crea wallet mancanti
        if wallet_da_creare:
            print("\n" + "="*80)
            print("🔧 CREAZIONE WALLET MANCANTI:")
            print("="*80)
            
            for item in wallet_da_creare:
                cliente = item['cliente']
                wallet_address = item['wallet_address']
                
                try:
                    # Crea wallet nel sistema dedicato
                    wallet_data = {
                        'nome_wallet': f"Wallet {cliente['nome_cliente']}",
                        'tipo_wallet': 'cliente',
                        'saldo_attuale': 0.0,
                        'valuta': 'USDT',
                        'proprietario': cliente['nome_cliente'],
                        'attivo': True,
                        'note': f"Wallet: {wallet_address} | Cliente: {cliente['nome_cliente']} (ID: {cliente['id']}) - creato da script",
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    response = wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').insert(wallet_data).execute()
                    
                    if response.data:
                        print(f"✅ Wallet creato per {cliente['nome_cliente']}")
                        print(f"   💰 Indirizzo: {wallet_address}")
                        print(f"   🆔 ID Cliente: {cliente['id']}")
                    else:
                        print(f"❌ Errore creazione wallet per {cliente['nome_cliente']}")
                    
                except Exception as e:
                    print(f"❌ Errore creazione wallet per {cliente['nome_cliente']}: {e}")
                
                print("-" * 40)
        
        # Verifica finale
        print("\n" + "="*80)
        print("📊 VERIFICA FINALE:")
        print("="*80)
        
        # Ricontrolla wallet esistenti
        final_wallets = wallet_manager.get_wallet_collaboratori()
        
        # Estrai indirizzi wallet dal campo note
        final_wallet_addresses = set()
        for w in final_wallets:
            note = w.get('note') or ''
            if 'Wallet:' in note:
                try:
                    wallet_addr = note.split('Wallet:')[1].split('|')[0].strip()
                    final_wallet_addresses.add(wallet_addr)
                except:
                    pass
        
        wallet_creati = 0
        for cliente in clienti_con_wallet:
            wallet_address = cliente.get('wallet', '').strip()
            if wallet_address in final_wallet_addresses:
                wallet_creati += 1
        
        print(f"👥 Clienti con wallet: {len(clienti_con_wallet)}")
        print(f"💰 Wallet nel sistema: {len(final_wallets)}")
        print(f"✅ Wallet collegati: {wallet_creati}")
        print(f"❌ Wallet mancanti: {len(clienti_con_wallet) - wallet_creati}")
        
        if wallet_creati == len(clienti_con_wallet):
            print("\n🎉 TUTTI I WALLET SONO STATI CREATI CORRETTAMENTE!")
        else:
            print(f"\n⚠️ RIMANGONO {len(clienti_con_wallet) - wallet_creati} WALLET DA CREARE")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il controllo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 CONTROLLO CLIENTI ESISTENTI E CREAZIONE WALLET MANCANTI")
    print("="*80)
    
    check_existing_clients_wallets()
    
    print("\n✅ Controllo completato!")
