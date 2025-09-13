#!/usr/bin/env python3
"""
🔍 CONTROLLO STRUTTURA TABELLA USERS
Script per verificare la struttura della tabella users
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

def check_users_table():
    """Controlla la struttura della tabella users"""
    
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
        
        # Recupera un utente esistente per vedere la struttura
        logger.info("📋 Recupero struttura tabella users...")
        users_response = supabase_manager.supabase.table('users').select('*').limit(1).execute()
        
        if users_response.data:
            user = users_response.data[0]
            print("\n" + "="*80)
            print("📋 STRUTTURA TABELLA USERS:")
            print("="*80)
            
            for key, value in user.items():
                print(f"🔑 {key}: {type(value).__name__} = {value}")
            
            print("\n" + "="*80)
            print("📊 COLONNE DISPONIBILI:")
            print("="*80)
            
            for key in user.keys():
                print(f"✅ {key}")
        else:
            print("❌ Nessun utente trovato nella tabella")
        
        # Controlla se esiste la colonna id
        print("\n" + "="*80)
        print("🔍 RICERCA COLONNA ID:")
        print("="*80)
        
        try:
            # Prova a fare una query con id
            test_response = supabase_manager.supabase.table('users').select('id').limit(1).execute()
            print("✅ Colonna 'id' esiste")
        except Exception as e:
            print(f"❌ Colonna 'id' NON esiste: {e}")
        
        # Controlla se esiste la colonna user_id
        try:
            test_response = supabase_manager.supabase.table('users').select('user_id').limit(1).execute()
            print("✅ Colonna 'user_id' esiste")
        except Exception as e:
            print(f"❌ Colonna 'user_id' NON esiste: {e}")
        
        # Controlla se esiste la colonna username
        try:
            test_response = supabase_manager.supabase.table('users').select('username').limit(1).execute()
            print("✅ Colonna 'username' esiste")
        except Exception as e:
            print(f"❌ Colonna 'username' NON esiste: {e}")
        
        # Controlla se esiste la colonna email
        try:
            test_response = supabase_manager.supabase.table('users').select('email').limit(1).execute()
            print("✅ Colonna 'email' esiste")
        except Exception as e:
            print(f"❌ Colonna 'email' NON esiste: {e}")
        
        # Controlla se esiste la colonna password
        try:
            test_response = supabase_manager.supabase.table('users').select('password').limit(1).execute()
            print("✅ Colonna 'password' esiste")
        except Exception as e:
            print(f"❌ Colonna 'password' NON esiste: {e}")
        
        # Controlla se esiste la colonna role
        try:
            test_response = supabase_manager.supabase.table('users').select('role').limit(1).execute()
            print("✅ Colonna 'role' esiste")
        except Exception as e:
            print(f"❌ Colonna 'role' NON esiste: {e}")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il controllo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 CONTROLLO STRUTTURA TABELLA USERS")
    print("="*80)
    
    check_users_table()
    
    print("\n✅ Controllo completato!")
