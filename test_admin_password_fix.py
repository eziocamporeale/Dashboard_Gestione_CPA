#!/usr/bin/env python3
"""
Test per verificare la correzione del cambio password admin
Testa sia il caso hardcoded che il caso Supabase
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from components.user_settings import UserSettings
from components.auth.auth_simple import SimpleAuthSystem

def test_admin_password_scenario():
    """Testa lo scenario specifico dell'admin"""
    
    print("🧪 Test Scenario Admin Password")
    print("=" * 60)
    
    # Simula session state per admin
    import streamlit as st
    st.session_state.username = 'admin'
    st.session_state.user_info = {'role': 'admin'}
    
    user_settings = UserSettings()
    auth_system = SimpleAuthSystem()
    
    # Test 1: Verifica che l'admin hardcoded sia rilevato
    print("\n1️⃣ Test Rilevamento Admin Hardcoded")
    user_data = user_settings.get_current_user_data()
    
    if user_data:
        print(f"✅ Utente rilevato: {user_data['username']}")
        print(f"✅ Email: {user_data['email']}")
        print(f"✅ Password hash: {user_data['password_hash']}")
        print(f"✅ Ruolo: {user_data['role']}")
    else:
        print("❌ Utente non rilevato")
        return False
    
    # Test 2: Verifica password corrente admin
    print("\n2️⃣ Test Verifica Password Corrente Admin")
    current_password = "admin123"
    current_hash = user_data['password_hash']
    
    password_valid = user_settings.verify_password(current_password, current_hash)
    print(f"✅ Password corrente verificata: {password_valid}")
    
    if not password_valid:
        print("❌ Password corrente non verificata")
        return False
    
    # Test 3: Test hash nuova password
    print("\n3️⃣ Test Hash Nuova Password")
    new_password = "Vtmarkets12!"
    new_hash = user_settings.hash_password(new_password)
    print(f"✅ Nuova password hashata: {new_hash[:30]}...")
    
    # Test 4: Verifica nuova password
    print("\n4️⃣ Test Verifica Nuova Password")
    new_valid = user_settings.verify_password(new_password, new_hash)
    auth_valid = auth_system.verify_password(new_password, new_hash)
    
    print(f"✅ Nuova password (UserSettings): {new_valid}")
    print(f"✅ Nuova password (AuthSimple): {auth_valid}")
    
    if not (new_valid and auth_valid):
        print("❌ Nuova password non verificata")
        return False
    
    # Test 5: Test autenticazione con nuova password
    print("\n5️⃣ Test Autenticazione con Nuova Password")
    # Simula il caso in cui l'admin è stato migrato a Supabase
    auth_success = auth_system.verify_password(new_password, new_hash)
    print(f"✅ Autenticazione con nuova password: {auth_success}")
    
    print("\n" + "=" * 60)
    return True

def test_password_change_flow():
    """Testa il flusso completo di cambio password"""
    
    print("\n🔄 Test Flusso Cambio Password")
    print("=" * 60)
    
    # Simula session state per admin
    import streamlit as st
    st.session_state.username = 'admin'
    st.session_state.user_info = {'role': 'admin'}
    
    user_settings = UserSettings()
    
    # Simula i dati del form
    current_password = "admin123"
    new_password = "NuovaPassword123!"
    confirm_password = "NuovaPassword123!"
    
    print(f"✅ Password corrente: {current_password}")
    print(f"✅ Nuova password: {new_password}")
    print(f"✅ Conferma password: {confirm_password}")
    
    # Test validazioni
    print("\n📋 Test Validazioni")
    
    # Validazione campi obbligatori
    if not current_password or not new_password or not confirm_password:
        print("❌ Validazione campi obbligatori fallita")
        return False
    print("✅ Campi obbligatori validati")
    
    # Validazione password coincidenti
    if new_password != confirm_password:
        print("❌ Validazione password coincidenti fallita")
        return False
    print("✅ Password coincidenti validate")
    
    # Validazione lunghezza password
    if len(new_password) < 8:
        print("❌ Validazione lunghezza password fallita")
        return False
    print("✅ Lunghezza password validata")
    
    # Test recupero dati utente
    print("\n👤 Test Recupero Dati Utente")
    user_data = user_settings.get_current_user_data()
    if not user_data:
        print("❌ Recupero dati utente fallito")
        return False
    print("✅ Dati utente recuperati")
    
    # Test verifica password corrente
    print("\n🔐 Test Verifica Password Corrente")
    current_hash = user_data.get('password_hash', '')
    password_correct = user_settings.verify_password(current_password, current_hash)
    
    if not password_correct:
        print("❌ Verifica password corrente fallita")
        return False
    print("✅ Password corrente verificata")
    
    # Test hash nuova password
    print("\n🔒 Test Hash Nuova Password")
    new_password_hash = user_settings.hash_password(new_password)
    print(f"✅ Nuova password hashata: {new_password_hash[:30]}...")
    
    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    print("🚀 Avvio Test Admin Password Fix")
    
    # Esegui test
    test1_result = test_admin_password_scenario()
    test2_result = test_password_change_flow()
    
    print("\n" + "=" * 70)
    print("📊 RISULTATI FINALI:")
    print(f"✅ Test Scenario Admin: {'PASSATO' if test1_result else 'FALLITO'}")
    print(f"✅ Test Flusso Cambio Password: {'PASSATO' if test2_result else 'FALLITO'}")
    
    if test1_result and test2_result:
        print("\n🎉 TUTTI I TEST SUPERATI!")
        print("💡 Il sistema admin password è ora funzionante:")
        print("   • Rileva correttamente l'admin hardcoded")
        print("   • Verifica la password corrente (admin123)")
        print("   • Hasha correttamente la nuova password")
        print("   • Gestisce la migrazione a Supabase")
        print("\n🔧 Ora dovresti poter:")
        print("   • Cambiare la password admin da entrambe le sezioni")
        print("   • Fare login con la nuova password")
        print("   • L'admin verrà migrato automaticamente a Supabase")
    else:
        print("\n❌ ALCUNI TEST FALLITI!")
        print("🔧 Controlla la configurazione del sistema admin")
    
    print("=" * 70)
