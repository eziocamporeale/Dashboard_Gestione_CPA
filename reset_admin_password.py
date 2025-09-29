#!/usr/bin/env python3
"""
🔧 RESET ADMIN PASSWORD
Script per resettare la password dell'admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_manager import SupabaseManager
import hashlib
import secrets
from datetime import datetime

def reset_admin_password():
    """Reset della password admin"""
    print("🔧 RESET ADMIN PASSWORD")
    print("=" * 50)
    
    # Inizializza Supabase
    try:
        supabase_manager = SupabaseManager()
        print("✅ Supabase inizializzato correttamente")
    except Exception as e:
        print(f"❌ Errore inizializzazione Supabase: {e}")
        return
    
    # Nuova password
    new_password = "admin123"  # Password semplice per test
    
    print(f"🆕 Nuova password: {new_password}")
    
    # Hash della password
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
    new_hash = f"{salt}${password_hash}"
    
    print(f"🔑 Nuovo hash: {new_hash}")
    
    # Aggiorna password nel database
    try:
        response = supabase_manager.supabase.table('users').update({
            'password_hash': new_hash,
            'updated_at': datetime.now().isoformat()
        }).eq('username', 'admin').execute()
        
        if response.data:
            print("✅ Password admin resettata con successo!")
            print(f"👤 Username: admin")
            print(f"🔑 Password: {new_password}")
            print("\n💡 Ora puoi usare questa password per il cambio password")
        else:
            print("❌ Errore nel reset della password")
            
    except Exception as e:
        print(f"❌ Errore durante il reset: {e}")

if __name__ == "__main__":
    reset_admin_password()
