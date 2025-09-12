#!/usr/bin/env python3
"""
🔧 AGGIUNTA COLONNA CLIENTE_ID ALLA TABELLA WALLET_COLLABORATORI
Script per aggiungere la colonna cliente_id alla tabella wallet_collaboratori
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

def add_cliente_id_column():
    """Aggiunge la colonna cliente_id alla tabella wallet_collaboratori"""
    
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
        
        print("\n" + "="*80)
        print("🔧 AGGIUNTA COLONNA CLIENTE_ID:")
        print("="*80)
        
        # Nota: Non possiamo aggiungere colonne direttamente con Supabase Python client
        # Dobbiamo usare SQL diretto o l'interfaccia Supabase
        
        print("⚠️ ATTENZIONE: Non è possibile aggiungere colonne direttamente con il client Python")
        print("📋 Devi aggiungere la colonna manualmente in Supabase:")
        print("")
        print("1. Vai su https://supabase.com/dashboard")
        print("2. Seleziona il tuo progetto")
        print("3. Vai su 'Table Editor'")
        print("4. Seleziona la tabella 'wallet_collaboratori'")
        print("5. Clicca su 'Add Column'")
        print("6. Configura la colonna:")
        print("   - Name: cliente_id")
        print("   - Type: uuid")
        print("   - Default: null")
        print("   - Allow nullable: Yes")
        print("7. Clicca su 'Save'")
        print("")
        print("🔗 Oppure esegui questo SQL nella sezione 'SQL Editor':")
        print("")
        print("-- Aggiungi colonna wallet_address")
        print("ALTER TABLE wallet_collaboratori ADD COLUMN wallet_address TEXT;")
        print("")
        print("-- Aggiungi colonna cliente_id")
        print("ALTER TABLE wallet_collaboratori ADD COLUMN cliente_id UUID REFERENCES clienti(id);")
        print("")
        print("📝 Questo creerà:")
        print("   - Una colonna 'wallet_address' di tipo TEXT per l'indirizzo del wallet")
        print("   - Una colonna 'cliente_id' di tipo UUID")
        print("   - Un foreign key constraint verso la tabella 'clienti'")
        print("   - Permetterà valori NULL per wallet non collegati a clienti")
        
        # Verifica se le colonne esistono già
        cliente_id_exists = False
        wallet_address_exists = False
        
        try:
            test_response = supabase_manager.supabase.table('wallet_collaboratori').select('cliente_id').limit(1).execute()
            print("\n✅ La colonna 'cliente_id' esiste già!")
            cliente_id_exists = True
        except Exception as e:
            print(f"\n❌ La colonna 'cliente_id' non esiste ancora: {e}")
        
        try:
            test_response = supabase_manager.supabase.table('wallet_collaboratori').select('wallet_address').limit(1).execute()
            print("✅ La colonna 'wallet_address' esiste già!")
            wallet_address_exists = True
        except Exception as e:
            print(f"❌ La colonna 'wallet_address' non esiste ancora: {e}")
        
        return cliente_id_exists and wallet_address_exists
        
    except Exception as e:
        logger.error(f"❌ Errore durante il controllo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 AGGIUNTA COLONNA CLIENTE_ID ALLA TABELLA WALLET_COLLABORATORI")
    print("="*80)
    
    success = add_cliente_id_column()
    
    if success:
        print("\n✅ Colonna già presente!")
    else:
        print("\n⚠️ Aggiungi la colonna manualmente in Supabase!")
    
    print("\n✅ Controllo completato!")
