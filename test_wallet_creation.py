#!/usr/bin/env python3
"""
🧪 TEST WALLET CREATION
Script per testare la creazione automatica dei wallet quando si aggiunge un cliente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.wallet_transactions_manager import WalletTransactionsManager
from supabase_manager import SupabaseManager
from datetime import datetime

def test_wallet_creation():
    """Test della creazione automatica dei wallet"""
    print("🧪 TEST WALLET CREATION")
    print("=" * 50)
    
    # Inizializza WalletTransactionsManager
    try:
        wallet_manager = WalletTransactionsManager()
        print("✅ WalletTransactionsManager inizializzato correttamente")
    except Exception as e:
        print(f"❌ Errore inizializzazione WalletTransactionsManager: {e}")
        return
    
    # Simula l'aggiunta di un nuovo cliente con wallet
    print("\n📋 1. SIMULAZIONE AGGIUNTA CLIENTE")
    print("-" * 40)
    
    # Dati cliente di test
    test_cliente = {
        'nome_cliente': 'Test Cliente Wallet',
        'email': 'test.wallet@example.com',
        'wallet': 'TTest123456789012345678901234567890',
        'telefono': '+1234567890',
        'note_cliente': 'Cliente di test per wallet'
    }
    
    print(f"👤 Cliente: {test_cliente['nome_cliente']}")
    print(f"📧 Email: {test_cliente['email']}")
    print(f"💰 Wallet: {test_cliente['wallet']}")
    
    # Verifica se il wallet esiste già
    print("\n📋 2. VERIFICA ESISTENZA WALLET")
    print("-" * 40)
    
    existing_wallets = wallet_manager.get_wallet_collaboratori()
    print(f"📊 Wallet esistenti: {len(existing_wallets)}")
    
    # Controlla se il wallet esiste già
    wallet_exists = False
    for wallet in existing_wallets:
        if 'Wallet:' in wallet.get('note', ''):
            try:
                wallet_address = wallet.get('note', '').split('Wallet:')[1].split('|')[0].strip()
                if wallet_address == test_cliente['wallet']:
                    wallet_exists = True
                    print(f"✅ Wallet già esistente: {wallet['nome_wallet']}")
                    break
            except Exception as e:
                print(f"⚠️ Errore parsing wallet note: {e}")
    
    if not wallet_exists:
        print("❌ Wallet non trovato - procedo con la creazione")
        
        # Simula la creazione del cliente in Supabase
        print("\n📋 3. CREAZIONE CLIENTE IN SUPABASE")
        print("-" * 40)
        
        try:
            # Crea il cliente in Supabase
            cliente_data = {
                'nome_cliente': test_cliente['nome_cliente'],
                'email': test_cliente['email'],
                'telefono': test_cliente['telefono'],
                'wallet': test_cliente['wallet'],
                'note_cliente': test_cliente['note_cliente'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = wallet_manager.supabase_manager.supabase.table('clienti').insert(cliente_data).execute()
            
            if response.data:
                cliente_id = response.data[0]['id']
                print(f"✅ Cliente creato con ID: {cliente_id}")
                
                # Crea il wallet nel sistema dedicato
                print("\n📋 4. CREAZIONE WALLET NEL SISTEMA DEDICATO")
                print("-" * 40)
                
                wallet_data = {
                    'nome_wallet': f"Wallet {test_cliente['nome_cliente']}",
                    'tipo_wallet': 'cliente',
                    'saldo_attuale': 0.0,
                    'valuta': 'USDT',
                    'proprietario': test_cliente['nome_cliente'],
                    'attivo': True,
                    'note': f"Wallet: {test_cliente['wallet']} | Cliente: {test_cliente['nome_cliente']} (ID: {cliente_id})",
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                wallet_response = wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').insert(wallet_data).execute()
                
                if wallet_response.data:
                    print(f"✅ Wallet creato: {wallet_data['nome_wallet']}")
                    print(f"💰 Tipo: {wallet_data['tipo_wallet']}")
                    print(f"💵 Valuta: {wallet_data['valuta']}")
                    print(f"📝 Note: {wallet_data['note']}")
                    
                    # Verifica che il wallet sia visibile nella sezione Wallet
                    print("\n📋 5. VERIFICA VISIBILITÀ WALLET")
                    print("-" * 40)
                    
                    updated_wallets = wallet_manager.get_wallet_collaboratori()
                    client_wallets = [w for w in updated_wallets if w.get('tipo_wallet') == 'cliente']
                    
                    print(f"📊 Wallet clienti totali: {len(client_wallets)}")
                    
                    # Cerca il wallet appena creato
                    new_wallet_found = False
                    for wallet in client_wallets:
                        if wallet.get('nome_wallet') == wallet_data['nome_wallet']:
                            new_wallet_found = True
                            print(f"✅ Wallet trovato nella sezione Wallet: {wallet['nome_wallet']}")
                            print(f"   Proprietario: {wallet.get('proprietario', 'N/A')}")
                            print(f"   Attivo: {wallet.get('attivo', True)}")
                            print(f"   Valuta: {wallet.get('valuta', 'N/A')}")
                            break
                    
                    if not new_wallet_found:
                        print("❌ Wallet non trovato nella sezione Wallet!")
                        print("🔍 Wallet disponibili:")
                        for wallet in client_wallets:
                            print(f"   - {wallet.get('nome_wallet', 'N/A')}")
                    
                else:
                    print("❌ Errore creazione wallet")
            else:
                print("❌ Errore creazione cliente")
                
        except Exception as e:
            print(f"❌ Errore durante la creazione: {e}")
    else:
        print("ℹ️ Wallet già esistente - test completato")

if __name__ == "__main__":
    test_wallet_creation()
