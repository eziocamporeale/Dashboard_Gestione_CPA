#!/usr/bin/env python3
"""
🔍 CONTROLLO UTENTE DIEGO
Script per verificare se Diego esiste nella tabella users
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

def check_diego_user():
    """Controlla se Diego esiste nella tabella users"""
    
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
        
        # Cerca Diego nella tabella users
        logger.info("🔍 Ricerca utente Diego...")
        users_response = supabase_manager.supabase.table('users').select('*').ilike('username', '%diego%').execute()
        
        if users_response.data:
            print("\n" + "="*80)
            print("👤 UTENTI TROVATI CON 'diego':")
            print("="*80)
            
            for user in users_response.data:
                print(f"🔑 ID: {user.get('id')}")
                print(f"👤 Username: {user.get('username')}")
                print(f"📧 Email: {user.get('email')}")
                print(f"👨‍💼 Nome: {user.get('full_name')}")
                print(f"🎭 Ruolo: {user.get('role')}")
                print(f"🆔 Role ID: {user.get('role_id')}")
                print(f"✅ Attivo: {user.get('is_active')}")
                print(f"🔐 Password Hash: {user.get('password_hash', 'N/A')[:20]}...")
                print("-" * 40)
        else:
            print("❌ Nessun utente trovato con 'diego'")
        
        # Cerca anche per nome completo
        logger.info("🔍 Ricerca per nome completo...")
        users_response2 = supabase_manager.supabase.table('users').select('*').ilike('full_name', '%diego%').execute()
        
        if users_response2.data:
            print("\n" + "="*80)
            print("👤 UTENTI TROVATI PER NOME COMPLETO:")
            print("="*80)
            
            for user in users_response2.data:
                print(f"🔑 ID: {user.get('id')}")
                print(f"👤 Username: {user.get('username')}")
                print(f"📧 Email: {user.get('email')}")
                print(f"👨‍💼 Nome: {user.get('full_name')}")
                print(f"🎭 Ruolo: {user.get('role')}")
                print(f"🆔 Role ID: {user.get('role_id')}")
                print(f"✅ Attivo: {user.get('is_active')}")
                print(f"🔐 Password Hash: {user.get('password_hash', 'N/A')[:20]}...")
                print("-" * 40)
        
        # Mostra tutti gli utenti per riferimento
        logger.info("📋 Lista tutti gli utenti...")
        all_users_response = supabase_manager.supabase.table('users').select('*').execute()
        
        if all_users_response.data:
            print("\n" + "="*80)
            print("👥 TUTTI GLI UTENTI:")
            print("="*80)
            
            for user in all_users_response.data:
                print(f"👤 {user.get('username')} ({user.get('full_name')}) - {user.get('role')}")
        
    except Exception as e:
        logger.error(f"❌ Errore durante il controllo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 CONTROLLO UTENTE DIEGO")
    print("="*80)
    
    check_diego_user()
    
    print("\n✅ Controllo completato!")
