#!/usr/bin/env python3
"""
🧪 TEST WALLET CLIENT TRANSACTIONS
Script per testare le transazioni verso i wallet dei clienti
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.wallet_transactions_manager import WalletTransactionsManager
from supabase_manager import SupabaseManager
from datetime import datetime

def test_client_wallet_transactions():
    """Test delle transazioni verso i wallet dei clienti"""
    print("🧪 TEST WALLET CLIENT TRANSACTIONS")
    print("=" * 50)
    
    # Inizializza WalletTransactionsManager
    try:
        wallet_manager = WalletTransactionsManager()
        print("✅ WalletTransactionsManager inizializzato correttamente")
    except Exception as e:
        print(f"❌ Errore inizializzazione WalletTransactionsManager: {e}")
        return
    
    # Recupera i wallet disponibili
    print("\n📋 1. RECUPERO WALLET DISPONIBILI")
    print("-" * 40)
    
    wallets = wallet_manager.get_wallet_collaboratori()
    if not wallets:
        print("❌ Nessun wallet disponibile!")
        return
    
    # Separa wallet collaboratori e clienti
    collaborator_wallets = [w for w in wallets if w.get('tipo_wallet') in ['principale', 'collaboratore']]
    client_wallets = [w for w in wallets if w.get('tipo_wallet') == 'cliente']
    
    print(f"📊 Wallet collaboratori: {len(collaborator_wallets)}")
    print(f"📊 Wallet clienti: {len(client_wallets)}")
    
    if not collaborator_wallets:
        print("❌ Nessun wallet collaboratore disponibile!")
        return
    
    if not client_wallets:
        print("❌ Nessun wallet cliente disponibile!")
        return
    
    # Mostra wallet collaboratori
    print("\n💰 Wallet Collaboratori:")
    for i, wallet in enumerate(collaborator_wallets, 1):
        balance = wallet_manager.calculate_wallet_balance(wallet['nome_wallet'])
        print(f"  {i}. {wallet['nome_wallet']} - Saldo: {balance:.2f} {wallet.get('valuta', 'USD')}")
    
    # Mostra wallet clienti
    print("\n👤 Wallet Clienti:")
    for i, wallet in enumerate(client_wallets, 1):
        balance = wallet_manager.calculate_wallet_balance(wallet['nome_wallet'])
        print(f"  {i}. {wallet['nome_wallet']} - Saldo: {balance:.2f} {wallet.get('valuta', 'USD')}")
    
    # Test transazioni verso clienti
    print("\n🧪 2. TEST TRANSAZIONI VERSO CLIENTI")
    print("-" * 40)
    
    # Usa il primo wallet collaboratore disponibile
    source_wallet = collaborator_wallets[0]
    source_name = source_wallet['nome_wallet']
    source_balance = wallet_manager.calculate_wallet_balance(source_name)
    
    print(f"💰 Wallet sorgente: {source_name}")
    print(f"💵 Saldo disponibile: {source_balance:.2f} {source_wallet.get('valuta', 'USD')}")
    
    if source_balance < 100:
        print("⚠️ Saldo insufficiente per i test. Creando transazione di test...")
        
        # Crea una transazione di test dal Sistema al wallet sorgente
        test_transaction = {
            'wallet_mittente': 'Sistema',
            'wallet_destinatario': source_name,
            'importo': 1000.0,
            'valuta': source_wallet.get('valuta', 'USD'),
            'tipo_transazione': 'deposito',
            'descrizione': 'Test - Deposito per transazioni clienti',
            'stato': 'completed',
            'created_at': datetime.now().isoformat()
        }
        
        success, message = wallet_manager.add_wallet_transaction(test_transaction)
        if success:
            print(f"✅ Transazione di test creata: {message}")
            source_balance = wallet_manager.calculate_wallet_balance(source_name)
            print(f"💵 Nuovo saldo: {source_balance:.2f} {source_wallet.get('valuta', 'USD')}")
        else:
            print(f"❌ Errore creazione transazione di test: {message}")
            return
    
    # Crea transazioni verso i primi 3 wallet clienti
    test_amounts = [100.0, 150.0, 200.0]
    successful_transactions = 0
    
    for i, client_wallet in enumerate(client_wallets[:3]):
        client_name = client_wallet['nome_wallet']
        amount = test_amounts[i] if i < len(test_amounts) else 100.0
        
        # Verifica che il wallet sorgente abbia abbastanza saldo
        if source_balance < amount:
            print(f"⚠️ Saldo insufficiente per {client_name}. Saltando...")
            continue
        
        # Crea transazione
        transaction_data = {
            'wallet_mittente': source_name,
            'wallet_destinatario': client_name,
            'importo': amount,
            'valuta': source_wallet.get('valuta', 'USD'),
            'tipo_transazione': 'deposito_cliente',
            'descrizione': f'Test - Deposito verso {client_name}',
            'stato': 'completed',
            'created_at': datetime.now().isoformat()
        }
        
        print(f"\n💸 Creando transazione: {source_name} → {client_name}")
        print(f"   Importo: {amount} {source_wallet.get('valuta', 'USD')}")
        
        success, message = wallet_manager.add_wallet_transaction(transaction_data)
        if success:
            print(f"✅ Transazione creata: {message}")
            successful_transactions += 1
            
            # Aggiorna saldo sorgente
            source_balance -= amount
        else:
            print(f"❌ Errore transazione: {message}")
    
    # Verifica risultati
    print(f"\n📊 3. RISULTATI TEST")
    print("-" * 40)
    print(f"✅ Transazioni create: {successful_transactions}")
    
    if successful_transactions > 0:
        print("\n💰 Nuovi saldi:")
        
        # Saldo wallet sorgente
        new_source_balance = wallet_manager.calculate_wallet_balance(source_name)
        print(f"  {source_name}: {new_source_balance:.2f} {source_wallet.get('valuta', 'USD')}")
        
        # Saldi wallet clienti
        for client_wallet in client_wallets[:3]:
            client_name = client_wallet['nome_wallet']
            new_balance = wallet_manager.calculate_wallet_balance(client_name)
            print(f"  {client_name}: {new_balance:.2f} {client_wallet.get('valuta', 'USD')}")
        
        print("\n🎯 Test completato! Ora i wallet dei clienti dovrebbero avere saldi > 0")
        print("💡 Vai alla sezione '💰 Saldi Wallet' nell'applicazione per verificare")
    else:
        print("❌ Nessuna transazione creata. Verifica i saldi e riprova.")

if __name__ == "__main__":
    test_client_wallet_transactions()
