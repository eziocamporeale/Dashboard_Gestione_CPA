#!/usr/bin/env python3
"""
🔍 CONTROLLO STRUTTURA TABELLA WALLET_COLLABORATORI
Script per verificare la struttura della tabella wallet_collaboratori
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

def check_wallet_table_structure():
    """Controlla la struttura della tabella wallet_collaboratori"""
    
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
        
        # Recupera un wallet esistente per vedere la struttura
        logger.info("📋 Recupero struttura tabella wallet_collaboratori...")
        wallets_response = supabase_manager.supabase.table('wallet_collaboratori').select('*').limit(1).execute()
        
        if wallets_response.data:
            wallet = wallets_response.data[0]
            print("\n" + "="*80)
            print("📋 STRUTTURA TABELLA WALLET_COLLABORATORI:")
            print("="*80)
            
            for key, value in wallet.items():
                print(f"🔑 {key}: {type(value).__name__} = {value}")
            
            print("\n" + "="*80)
            print("📊 COLONNE DISPONIBILI:")
            print("="*80)
            
            for key in wallet.keys():
                print(f"✅ {key}")
        else:
            print("❌ Nessun wallet trovato nella tabella")
        
        # Controlla se esiste la colonna cliente_id
        print("\n" + "="*80)
        print("🔍 RICERCA COLONNA CLIENTE_ID:")
        print("="*80)
        
        try:
            # Prova a fare una query con cliente_id
            test_response = supabase_manager.supabase.table('wallet_collaboratori').select('cliente_id').limit(1).execute()
            print("✅ Colonna 'cliente_id' esiste")
        except Exception as e:
            print(f"❌ Colonna 'cliente_id' NON esiste: {e}")
        
        # Controlla se esiste la colonna client_id
        try:
            test_response = supabase_manager.supabase.table('wallet_collaboratori').select('client_id').limit(1).execute()
            print("✅ Colonna 'client_id' esiste")
        except Exception as e:
            print(f"❌ Colonna 'client_id' NON esiste: {e}")
        
        # Controlla se esiste la colonna cliente
        try:
            test_response = supabase_manager.supabase.table('wallet_collaboratori').select('cliente').limit(1).execute()
            print("✅ Colonna 'cliente' esiste")
        except Exception as e:
            print(f"❌ Colonna 'cliente' NON esiste: {e}")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il controllo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 CONTROLLO STRUTTURA TABELLA WALLET_COLLABORATORI")
    print("="*80)
    
    check_wallet_table_structure()
    
    print("\n✅ Controllo completato!")
