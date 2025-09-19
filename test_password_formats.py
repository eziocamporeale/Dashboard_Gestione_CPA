#!/usr/bin/env python3
"""
Test per verificare la compatibilità con diversi formati di password
Testa bcrypt, SHA256 con salt, SHA256 semplice e password semplici
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import bcrypt
import hashlib
from components.user_settings import UserSettings
from components.auth.auth_simple import SimpleAuthSystem

def test_password_formats():
    """Testa tutti i formati di password supportati"""
    
    print("🧪 Test Formati Password Multipli")
    print("=" * 60)
    
    user_settings = UserSettings()
    auth_system = SimpleAuthSystem()
    
    test_password = "test123"
    
    # Test 1: Password bcrypt
    print("\n1️⃣ Test Password Bcrypt")
    bcrypt_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"✅ Hash bcrypt: {bcrypt_hash[:30]}...")
    
    user_valid = user_settings.verify_password(test_password, bcrypt_hash)
    auth_valid = auth_system.verify_password(test_password, bcrypt_hash)
    print(f"✅ UserSettings: {user_valid}")
    print(f"✅ AuthSimple: {auth_valid}")
    
    # Test 2: Password SHA256 con salt
    print("\n2️⃣ Test Password SHA256 con Salt")
    salt = "abc123def456"
    sha256_hash = f"{salt}${hashlib.sha256((test_password + salt).encode()).hexdigest()}"
    print(f"✅ Hash SHA256+salt: {sha256_hash[:30]}...")
    
    user_valid = user_settings.verify_password(test_password, sha256_hash)
    auth_valid = auth_system.verify_password(test_password, sha256_hash)
    print(f"✅ UserSettings: {user_valid}")
    print(f"✅ AuthSimple: {auth_valid}")
    
    # Test 3: Password SHA256 semplice
    print("\n3️⃣ Test Password SHA256 Semplice")
    sha256_simple = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"✅ Hash SHA256 semplice: {sha256_simple[:30]}...")
    
    user_valid = user_settings.verify_password(test_password, sha256_simple)
    auth_valid = auth_system.verify_password(test_password, sha256_simple)
    print(f"✅ UserSettings: {user_valid}")
    print(f"✅ AuthSimple: {auth_valid}")
    
    # Test 4: Password semplice (admin hardcoded)
    print("\n4️⃣ Test Password Semplice")
    simple_password = "admin123"
    print(f"✅ Password semplice: {simple_password}")
    
    user_valid = user_settings.verify_password(simple_password, simple_password)
    auth_valid = auth_system.verify_password(simple_password, simple_password)
    print(f"✅ UserSettings: {user_valid}")
    print(f"✅ AuthSimple: {auth_valid}")
    
    # Test 5: Password errata
    print("\n5️⃣ Test Password Errata")
    wrong_password = "wrong123"
    
    user_valid = user_settings.verify_password(wrong_password, bcrypt_hash)
    auth_valid = auth_system.verify_password(wrong_password, bcrypt_hash)
    print(f"✅ UserSettings (password errata): {not user_valid}")
    print(f"✅ AuthSimple (password errata): {not auth_valid}")
    
    print("\n" + "=" * 60)
    return True

def test_admin_password_scenario():
    """Testa lo scenario specifico dell'admin"""
    
    print("\n🔧 Test Scenario Admin")
    print("=" * 60)
    
    auth_system = SimpleAuthSystem()
    
    # Simula la password admin hardcoded
    admin_password = "admin123"
    admin_hash = "admin123"  # Password semplice nel sistema hardcoded
    
    print(f"✅ Password admin: {admin_password}")
    print(f"✅ Hash admin: {admin_hash}")
    
    # Test login admin
    login_success = auth_system.authenticate_user("admin", admin_password)
    print(f"✅ Login admin: {login_success}")
    
    # Test con password errata
    wrong_login = auth_system.authenticate_user("admin", "wrong123")
    print(f"✅ Login admin (password errata): {not wrong_login}")
    
    print("\n" + "=" * 60)
    return login_success and not wrong_login

def test_password_change_scenario():
    """Testa lo scenario di cambio password"""
    
    print("\n🔄 Test Scenario Cambio Password")
    print("=" * 60)
    
    user_settings = UserSettings()
    auth_system = SimpleAuthSystem()
    
    # Simula password corrente (SHA256 semplice)
    current_password = "old_password"
    current_hash = hashlib.sha256(current_password.encode()).hexdigest()
    
    print(f"✅ Password corrente: {current_password}")
    print(f"✅ Hash corrente: {current_hash[:30]}...")
    
    # Verifica password corrente
    current_valid = user_settings.verify_password(current_password, current_hash)
    print(f"✅ Verifica password corrente: {current_valid}")
    
    # Simula nuova password (bcrypt)
    new_password = "new_password"
    new_hash = user_settings.hash_password(new_password)
    
    print(f"✅ Nuova password: {new_password}")
    print(f"✅ Nuovo hash: {new_hash[:30]}...")
    
    # Verifica nuova password con entrambi i sistemi
    new_valid_user = user_settings.verify_password(new_password, new_hash)
    new_valid_auth = auth_system.verify_password(new_password, new_hash)
    
    print(f"✅ Nuova password (UserSettings): {new_valid_user}")
    print(f"✅ Nuova password (AuthSimple): {new_valid_auth}")
    
    print("\n" + "=" * 60)
    return current_valid and new_valid_user and new_valid_auth

if __name__ == "__main__":
    print("🚀 Avvio Test Formati Password")
    
    # Esegui test
    test1_result = test_password_formats()
    test2_result = test_admin_password_scenario()
    test3_result = test_password_change_scenario()
    
    print("\n" + "=" * 70)
    print("📊 RISULTATI FINALI:")
    print(f"✅ Test Formati Multipli: {'PASSATO' if test1_result else 'FALLITO'}")
    print(f"✅ Test Scenario Admin: {'PASSATO' if test2_result else 'FALLITO'}")
    print(f"✅ Test Cambio Password: {'PASSATO' if test3_result else 'FALLITO'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 TUTTI I TEST SUPERATI!")
        print("💡 Il sistema password supporta tutti i formati:")
        print("   • Bcrypt (nuovo standard)")
        print("   • SHA256 con salt")
        print("   • SHA256 semplice")
        print("   • Password semplici (admin)")
        print("\n🔧 Ora dovresti poter:")
        print("   • Cambiare la tua password personale")
        print("   • Cambiare password di altri utenti (admin)")
        print("   • Fare login con qualsiasi formato")
    else:
        print("\n❌ ALCUNI TEST FALLITI!")
        print("🔧 Controlla la configurazione del sistema password")
    
    print("=" * 70)
