#!/usr/bin/env python3
"""
🔍 DEBUG WALLET BALANCES
Script per debuggare il problema dei saldi wallet non visibili
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.wallet_transactions_manager import WalletTransactionsManager
from supabase_manager import SupabaseManager

def debug_wallet_balances():
    """Debug dei saldi wallet"""
    print("🔍 DEBUG WALLET BALANCES")
    print("=" * 50)
    
    # Inizializza Supabase
    try:
        supabase_manager = SupabaseManager()
        print("✅ Supabase inizializzato correttamente")
    except Exception as e:
        print(f"❌ Errore inizializzazione Supabase: {e}")
        return
    
    # Inizializza WalletTransactionsManager
    try:
        wallet_manager = WalletTransactionsManager()
        print("✅ WalletTransactionsManager inizializzato correttamente")
    except Exception as e:
        print(f"❌ Errore inizializzazione WalletTransactionsManager: {e}")
        return
    
    # 1. Verifica wallet collaboratori
    print("\n📋 1. VERIFICA WALLET COLLABORATORI")
    print("-" * 40)
    
    try:
        wallets = wallet_manager.get_wallet_collaboratori()
        print(f"📊 Totale wallet trovati: {len(wallets)}")
        
        if wallets:
            print("\n💰 Wallet disponibili:")
            for i, wallet in enumerate(wallets, 1):
                print(f"  {i}. {wallet.get('nome_wallet', 'N/A')} - {wallet.get('proprietario', 'N/A')} ({wallet.get('tipo_wallet', 'N/A')})")
                print(f"     Attivo: {wallet.get('attivo', True)}")
                print(f"     Valuta: {wallet.get('valuta', 'USD')}")
                print(f"     Creato: {wallet.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ Nessun wallet trovato!")
            
    except Exception as e:
        print(f"❌ Errore recupero wallet: {e}")
    
    # 2. Verifica transazioni wallet
    print("\n📋 2. VERIFICA TRANSAZIONI WALLET")
    print("-" * 40)
    
    try:
        transactions = wallet_manager.get_wallet_transactions(limit=50)
        print(f"📊 Totale transazioni trovate: {len(transactions)}")
        
        if transactions:
            print("\n💸 Ultime transazioni:")
            for i, trans in enumerate(transactions[:10], 1):
                print(f"  {i}. {trans.get('wallet_mittente', 'N/A')} → {trans.get('wallet_destinatario', 'N/A')}")
                print(f"     Importo: {trans.get('importo', 'N/A')} {trans.get('valuta', 'USD')}")
                print(f"     Stato: {trans.get('stato', 'N/A')}")
                print(f"     Data: {trans.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ Nessuna transazione trovata!")
            
    except Exception as e:
        print(f"❌ Errore recupero transazioni: {e}")
    
    # 3. Calcola saldi per ogni wallet
    print("\n📋 3. CALCOLO SALDI WALLET")
    print("-" * 40)
    
    try:
        wallets = wallet_manager.get_wallet_collaboratori()
        if wallets:
            for wallet in wallets:
                wallet_name = wallet.get('nome_wallet', 'N/A')
                if wallet_name != 'N/A':
                    balance = wallet_manager.calculate_wallet_balance(wallet_name)
                    print(f"💰 {wallet_name}: {balance:.2f} {wallet.get('valuta', 'USD')}")
        else:
            print("❌ Nessun wallet per calcolare i saldi!")
            
    except Exception as e:
        print(f"❌ Errore calcolo saldi: {e}")
    
    # 4. Verifica tabella wallet_collaboratori direttamente
    print("\n📋 4. VERIFICA DIRETTA TABELLA WALLET_COLLABORATORI")
    print("-" * 40)
    
    try:
        response = supabase_manager.supabase.table('wallet_collaboratori').select('*').execute()
        print(f"📊 Record nella tabella wallet_collaboratori: {len(response.data)}")
        
        if response.data:
            print("\n📋 Dettagli record:")
            for i, record in enumerate(response.data, 1):
                print(f"  {i}. ID: {record.get('id', 'N/A')}")
                print(f"     Nome: {record.get('nome_wallet', 'N/A')}")
                print(f"     Proprietario: {record.get('proprietario', 'N/A')}")
                print(f"     Tipo: {record.get('tipo_wallet', 'N/A')}")
                print(f"     Attivo: {record.get('attivo', True)}")
                print(f"     Valuta: {record.get('valuta', 'USD')}")
                print(f"     Creato: {record.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ Nessun record nella tabella wallet_collaboratori!")
            
    except Exception as e:
        print(f"❌ Errore verifica tabella: {e}")
    
    # 5. Verifica tabella wallet_transactions direttamente
    print("\n📋 5. VERIFICA DIRETTA TABELLA WALLET_TRANSACTIONS")
    print("-" * 40)
    
    try:
        response = supabase_manager.supabase.table('wallet_transactions').select('*').limit(10).execute()
        print(f"📊 Record nella tabella wallet_transactions: {len(response.data)}")
        
        if response.data:
            print("\n📋 Dettagli record:")
            for i, record in enumerate(response.data, 1):
                print(f"  {i}. ID: {record.get('id', 'N/A')}")
                print(f"     Mittente: {record.get('wallet_mittente', 'N/A')}")
                print(f"     Destinatario: {record.get('wallet_destinatario', 'N/A')}")
                print(f"     Importo: {record.get('importo', 'N/A')}")
                print(f"     Stato: {record.get('stato', 'N/A')}")
                print(f"     Data: {record.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ Nessun record nella tabella wallet_transactions!")
            
    except Exception as e:
        print(f"❌ Errore verifica tabella: {e}")

if __name__ == "__main__":
    debug_wallet_balances()
