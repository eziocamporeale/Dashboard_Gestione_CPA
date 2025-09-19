#!/usr/bin/env python3
"""
Test per verificare la compatibilità del sistema di password
Testa sia il sistema di cambio password che quello di autenticazione
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import bcrypt
from components.user_settings import UserSettings
from components.auth.auth_simple import SimpleAuthSystem

def test_password_compatibility():
    """Testa la compatibilità tra cambio password e autenticazione"""
    
    print("🧪 Test Compatibilità Sistema Password")
    print("=" * 50)
    
    # Test 1: Hash password con UserSettings
    print("\n1️⃣ Test Hash Password (UserSettings)")
    user_settings = UserSettings()
    test_password = "nuova_password_123"
    
    hashed_password = user_settings.hash_password(test_password)
    print(f"✅ Password hashata: {hashed_password[:30]}...")
    
    # Test 2: Verifica password con UserSettings
    print("\n2️⃣ Test Verifica Password (UserSettings)")
    is_valid = user_settings.verify_password(test_password, hashed_password)
    print(f"✅ Verifica password: {is_valid}")
    
    # Test 3: Verifica password con AuthSimple
    print("\n3️⃣ Test Verifica Password (AuthSimple)")
    auth_system = SimpleAuthSystem()
    is_valid_auth = auth_system.verify_password(test_password, hashed_password)
    print(f"✅ Verifica password (AuthSimple): {is_valid_auth}")
    
    # Test 4: Test con password bcrypt esistente
    print("\n4️⃣ Test Password Bcrypt Esistente")
    bcrypt_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"✅ Password bcrypt creata: {bcrypt_password[:30]}...")
    
    # Verifica con entrambi i sistemi
    is_valid_user = user_settings.verify_password("test123", bcrypt_password)
    is_valid_auth = auth_system.verify_password("test123", bcrypt_password)
    print(f"✅ Verifica UserSettings: {is_valid_user}")
    print(f"✅ Verifica AuthSimple: {is_valid_auth}")
    
    # Test 5: Test con password semplice (per admin)
    print("\n5️⃣ Test Password Semplice (Admin)")
    simple_password = "admin123"
    is_valid_simple = auth_system.verify_password(simple_password, simple_password)
    print(f"✅ Verifica password semplice: {is_valid_simple}")
    
    print("\n" + "=" * 50)
    if is_valid and is_valid_auth and is_valid_user and is_valid_auth and is_valid_simple:
        print("🎉 TUTTI I TEST SUPERATI! Sistema password compatibile")
        return True
    else:
        print("❌ ALCUNI TEST FALLITI! Sistema password non compatibile")
        return False

def test_password_change_simulation():
    """Simula un cambio password completo"""
    
    print("\n🔄 Simulazione Cambio Password")
    print("=" * 50)
    
    # Simula cambio password
    user_settings = UserSettings()
    auth_system = SimpleAuthSystem()
    
    old_password = "vecchia_password"
    new_password = "nuova_password_456"
    
    # Hash della vecchia password
    old_hash = user_settings.hash_password(old_password)
    print(f"✅ Vecchia password hashata: {old_hash[:30]}...")
    
    # Verifica vecchia password
    old_valid = user_settings.verify_password(old_password, old_hash)
    print(f"✅ Vecchia password verificata: {old_valid}")
    
    # Hash della nuova password
    new_hash = user_settings.hash_password(new_password)
    print(f"✅ Nuova password hashata: {new_hash[:30]}...")
    
    # Verifica nuova password con entrambi i sistemi
    new_valid_user = user_settings.verify_password(new_password, new_hash)
    new_valid_auth = auth_system.verify_password(new_password, new_hash)
    
    print(f"✅ Nuova password (UserSettings): {new_valid_user}")
    print(f"✅ Nuova password (AuthSimple): {new_valid_auth}")
    
    print("\n" + "=" * 50)
    if old_valid and new_valid_user and new_valid_auth:
        print("🎉 SIMULAZIONE CAMBIO PASSWORD RIUSCITA!")
        return True
    else:
        print("❌ SIMULAZIONE CAMBIO PASSWORD FALLITA!")
        return False

if __name__ == "__main__":
    print("🚀 Avvio Test Sistema Password")
    
    # Esegui test
    test1_result = test_password_compatibility()
    test2_result = test_password_change_simulation()
    
    print("\n" + "=" * 60)
    print("📊 RISULTATI FINALI:")
    print(f"✅ Test Compatibilità: {'PASSATO' if test1_result else 'FALLITO'}")
    print(f"✅ Test Cambio Password: {'PASSATO' if test2_result else 'FALLITO'}")
    
    if test1_result and test2_result:
        print("\n🎉 TUTTI I TEST SUPERATI! Il sistema password è pronto!")
        print("💡 Ora puoi cambiare le password e fare login correttamente")
    else:
        print("\n❌ ALCUNI TEST FALLITI! Controlla la configurazione")
    
    print("=" * 60)
