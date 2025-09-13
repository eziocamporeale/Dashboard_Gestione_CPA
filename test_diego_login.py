#!/usr/bin/env python3
"""
🧪 TEST LOGIN DIEGO
Script per testare il login di Diego con il sistema di autenticazione integrato
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

def test_diego_login():
    """Testa il login di Diego"""
    
    try:
        # Import dei componenti necessari
        from components.auth.auth_simple import SimpleAuthSystem
        
        logger.info("🔍 Inizializzazione sistema di autenticazione...")
        
        # Inizializza il sistema di autenticazione
        auth_system = SimpleAuthSystem()
        
        # Test con password diverse per Diego
        test_passwords = [
            "diego123",
            "diego",
            "Diego123",
            "password",
            "admin",
            "manager"
        ]
        
        username = "diego"
        
        print("\n" + "="*80)
        print("🧪 TEST LOGIN DIEGO")
        print("="*80)
        
        for password in test_passwords:
            logger.info(f"🔍 Test login con password: {password}")
            
            # Test autenticazione
            auth_result = auth_system.authenticate_user(username, password)
            
            if auth_result:
                print(f"✅ LOGIN RIUSCITO con password: {password}")
                
                # Test recupero info utente
                user_info = auth_system.get_user_info(username)
                if user_info:
                    print(f"👤 Info utente:")
                    print(f"  - ID: {user_info.get('user_id')}")
                    print(f"  - Username: {user_info.get('username')}")
                    print(f"  - Email: {user_info.get('email')}")
                    print(f"  - Nome: {user_info.get('name')}")
                    print(f"  - Ruolo: {user_info.get('role')}")
                    print(f"  - Da Supabase: {user_info.get('from_supabase')}")
                
                break
            else:
                print(f"❌ Login fallito con password: {password}")
        
        # Test con password vuota
        print(f"\n🔍 Test con password vuota...")
        auth_result = auth_system.authenticate_user(username, "")
        if auth_result:
            print(f"✅ LOGIN RIUSCITO con password vuota")
        else:
            print(f"❌ Login fallito con password vuota")
        
        # Test con username sbagliato
        print(f"\n🔍 Test con username sbagliato...")
        auth_result = auth_system.authenticate_user("diego_wrong", "diego123")
        if auth_result:
            print(f"✅ LOGIN RIUSCITO con username sbagliato")
        else:
            print(f"❌ Login fallito con username sbagliato (corretto)")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 TEST LOGIN DIEGO")
    print("="*80)
    
    test_diego_login()
    
    print("\n✅ Test completato!")
