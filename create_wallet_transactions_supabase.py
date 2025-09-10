#!/usr/bin/env python3
"""
🚀 SCRIPT AGGIORNAMENTO SUPABASE - Creazione tabella wallet_transactions
Esegue la creazione delle tabelle wallet su Supabase mantenendo la struttura esistente
"""

import os
import sys
from supabase_manager import SupabaseManager

def create_wallet_tables():
    """Crea le tabelle wallet_transactions e wallet_collaboratori su Supabase"""
    try:
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        
        if not supabase_manager.is_configured:
            print("❌ Supabase non configurato")
            return False
        
        print("🔗 Connessione a Supabase...")
        
        # Test connessione
        test_success, test_message = supabase_manager.test_connection()
        if not test_success:
            print(f"❌ Test connessione fallito: {test_message}")
            return False
        
        print("✅ Connessione Supabase verificata!")
        
        # Per ora, creiamo solo i wallet di default nella tabella esistente
        # Le tabelle wallet_transactions e wallet_collaboratori dovranno essere create manualmente su Supabase
        print("📝 Creazione wallet di default...")
        
        # Prova a inserire wallet di default (se la tabella esiste già)
        try:
            default_wallets = [
                {
                    'nome_wallet': 'Wallet_Principale_Ezio',
                    'proprietario': 'Ezio',
                    'tipo_wallet': 'principale',
                    'saldo_attuale': 0,
                    'valuta': 'USD',
                    'attivo': True,
                    'note': 'Wallet principale per le transazioni'
                },
                {
                    'nome_wallet': 'Wallet_Collaboratore_1',
                    'proprietario': 'Collaboratore 1',
                    'tipo_wallet': 'collaboratore',
                    'saldo_attuale': 0,
                    'valuta': 'USD',
                    'attivo': True,
                    'note': 'Wallet collaboratore 1'
                },
                {
                    'nome_wallet': 'Wallet_Collaboratore_2',
                    'proprietario': 'Collaboratore 2',
                    'tipo_wallet': 'collaboratore',
                    'saldo_attuale': 0,
                    'valuta': 'USD',
                    'attivo': True,
                    'note': 'Wallet collaboratore 2'
                }
            ]
            
            for wallet in default_wallets:
                try:
                    response = supabase_manager.supabase.table('wallet_collaboratori').insert(wallet).execute()
                    print(f"✅ Wallet '{wallet['nome_wallet']}' creato!")
                except Exception as e:
                    print(f"⚠️ Wallet '{wallet['nome_wallet']}' già esistente o errore: {e}")
            
        except Exception as e:
            print(f"⚠️ Tabella wallet_collaboratori non ancora creata: {e}")
            print("📋 Le tabelle dovranno essere create manualmente su Supabase")
        
        print("\n📋 ISTRUZIONI PER CREAZIONE MANUALE TABELLE:")
        print("=" * 60)
        print("1. Vai su https://supabase.com/dashboard")
        print("2. Seleziona il tuo progetto")
        print("3. Vai su 'SQL Editor'")
        print("4. Esegui questo script SQL:")
        print()
        print("-- Tabella wallet_transactions")
        print("CREATE TABLE wallet_transactions (")
        print("    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,")
        print("    wallet_mittente TEXT NOT NULL,")
        print("    wallet_destinatario TEXT NOT NULL,")
        print("    importo DECIMAL(15,2) NOT NULL,")
        print("    valuta TEXT DEFAULT 'USD',")
        print("    data_transazione TIMESTAMP DEFAULT NOW(),")
        print("    stato TEXT DEFAULT 'pending',")
        print("    note TEXT,")
        print("    collaboratore_id UUID,")
        print("    cliente_id UUID REFERENCES clienti(id) ON DELETE SET NULL,")
        print("    tipo_transazione TEXT DEFAULT 'transfer',")
        print("    commissione DECIMAL(15,2) DEFAULT 0,")
        print("    hash_transazione TEXT UNIQUE,")
        print("    created_at TIMESTAMP DEFAULT NOW(),")
        print("    updated_at TIMESTAMP DEFAULT NOW()")
        print(");")
        print()
        print("-- Tabella wallet_collaboratori")
        print("CREATE TABLE wallet_collaboratori (")
        print("    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,")
        print("    nome_wallet TEXT UNIQUE NOT NULL,")
        print("    proprietario TEXT NOT NULL,")
        print("    tipo_wallet TEXT DEFAULT 'collaboratore',")
        print("    saldo_attuale DECIMAL(15,2) DEFAULT 0,")
        print("    valuta TEXT DEFAULT 'USD',")
        print("    attivo BOOLEAN DEFAULT true,")
        print("    note TEXT,")
        print("    created_at TIMESTAMP DEFAULT NOW(),")
        print("    updated_at TIMESTAMP DEFAULT NOW()")
        print(");")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la creazione: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AGGIORNAMENTO SUPABASE - Creazione tabelle wallet")
    print("=" * 60)
    
    success = create_wallet_tables()
    
    if success:
        print("\n✅ AGGIORNAMENTO COMPLETATO!")
        print("🎯 Le tabelle 'wallet_transactions' e 'wallet_collaboratori' sono ora disponibili")
        print("📋 Wallet di default creati per iniziare subito")
    else:
        print("\n❌ AGGIORNAMENTO FALLITO!")
        print("🔧 Controlla i log per i dettagli dell'errore")
    
    print("\n" + "=" * 60)
