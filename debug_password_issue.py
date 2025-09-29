#!/usr/bin/env python3
"""
🔍 DEBUG PASSWORD ISSUE
Script per debuggare il problema del cambio password
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_manager import SupabaseManager
import hashlib
import secrets

def debug_password_issue():
    """Debug del problema password"""
    print("🔍 DEBUG PASSWORD ISSUE")
    print("=" * 50)
    
    # Inizializza Supabase
    try:
        supabase_manager = SupabaseManager()
        print("✅ Supabase inizializzato correttamente")
    except Exception as e:
        print(f"❌ Errore inizializzazione Supabase: {e}")
        return
    
    # Recupera dati utente admin
    print("\n📋 1. RECUPERO DATI UTENTE ADMIN")
    print("-" * 40)
    
    try:
        response = supabase_manager.supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if response.data:
            user_data = response.data[0]
            print(f"👤 Username: {user_data.get('username', 'N/A')}")
            print(f"📧 Email: {user_data.get('email', 'N/A')}")
            print(f"🏷️ Ruolo: {user_data.get('role', 'N/A')}")
            print(f"🔑 Password Hash: {user_data.get('password_hash', 'N/A')}")
            print(f"📅 Creato: {user_data.get('created_at', 'N/A')}")
            print(f"📅 Aggiornato: {user_data.get('updated_at', 'N/A')}")
            
            stored_password = user_data.get('password_hash', '')
            
            # Test password corrente
            print("\n📋 2. TEST PASSWORD CORRENTE")
            print("-" * 40)
            
            current_password = "admin123"
            print(f"🔑 Password inserita: {current_password}")
            print(f"🔑 Password nel DB: {stored_password}")
            
            # Test confronto diretto
            print("\n🧪 Test 1: Confronto diretto")
            direct_match = current_password == stored_password
            print(f"   Risultato: {direct_match}")
            
            # Test hash
            print("\n🧪 Test 2: Verifica hash")
            hash_match = False
            if '$' in stored_password:
                try:
                    salt, hash_value = stored_password.split('$')
                    password_hash = hashlib.sha256((current_password + salt).encode()).hexdigest()
                    hash_match = password_hash == hash_value
                    print(f"   Salt: {salt}")
                    print(f"   Hash nel DB: {hash_value}")
                    print(f"   Hash calcolato: {password_hash}")
                    print(f"   Risultato: {hash_match}")
                except Exception as e:
                    print(f"   Errore parsing hash: {e}")
            else:
                print("   Password non è un hash (formato salt$hash)")
            
            # Test hash semplice (senza salt)
            print("\n🧪 Test 3: Hash semplice (senza salt)")
            simple_hash = hashlib.sha256(current_password.encode()).hexdigest()
            simple_match = simple_hash == stored_password
            print(f"   Hash semplice: {simple_hash}")
            print(f"   Risultato: {simple_match}")
            
            # Test MD5 (per compatibilità)
            print("\n🧪 Test 4: MD5")
            md5_hash = hashlib.md5(current_password.encode()).hexdigest()
            md5_match = md5_hash == stored_password
            print(f"   MD5: {md5_hash}")
            print(f"   Risultato: {md5_match}")
            
            # Riassunto
            print("\n📊 RIASSUNTO TEST")
            print("-" * 40)
            print(f"✅ Confronto diretto: {direct_match}")
            print(f"✅ Hash con salt: {hash_match}")
            print(f"✅ Hash semplice: {simple_match}")
            print(f"✅ MD5: {md5_match}")
            
            if not any([direct_match, hash_match, simple_match, md5_match]):
                print("\n❌ PROBLEMA IDENTIFICATO:")
                print("   La password 'admin123' non corrisponde a nessun formato nel database")
                print("   Possibili soluzioni:")
                print("   1. La password nel DB è diversa da 'admin123'")
                print("   2. Il formato di hash è diverso da quelli testati")
                print("   3. C'è un problema nella logica di verifica")
            else:
                print("\n✅ PASSWORD TROVATA:")
                if direct_match:
                    print("   Formato: Testo semplice")
                elif hash_match:
                    print("   Formato: Hash con salt")
                elif simple_match:
                    print("   Formato: Hash semplice")
                elif md5_match:
                    print("   Formato: MD5")
                
        else:
            print("❌ Utente admin non trovato!")
            
    except Exception as e:
        print(f"❌ Errore durante il debug: {e}")
    
    # Test creazione nuovo hash
    print("\n📋 3. TEST CREAZIONE NUOVO HASH")
    print("-" * 40)
    
    new_password = "Vtmarkets12!"
    print(f"🆕 Nuova password: {new_password}")
    
    # Hash con salt (metodo attuale)
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
    new_hash = f"{salt}${password_hash}"
    
    print(f"🔑 Nuovo hash (con salt): {new_hash}")
    print(f"🔑 Salt: {salt}")
    print(f"🔑 Hash: {password_hash}")
    
    # Test verifica nuovo hash
    try:
        test_salt, test_hash = new_hash.split('$')
        test_password_hash = hashlib.sha256((new_password + test_salt).encode()).hexdigest()
        test_match = test_password_hash == test_hash
        print(f"✅ Verifica nuovo hash: {test_match}")
    except Exception as e:
        print(f"❌ Errore verifica nuovo hash: {e}")

if __name__ == "__main__":
    debug_password_issue()
