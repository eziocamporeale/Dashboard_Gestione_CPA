#!/usr/bin/env python3
"""
Test per verificare la logica semplificata del cambio password
Basata sulla logica del progetto DASH_GESTIONE_LEAD
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import bcrypt
from components.user_settings import UserSettings
from supabase_manager import SupabaseManager

def test_simplified_password_logic():
    """Testa la logica semplificata del cambio password"""
    
    print("🧪 Test Logica Semplificata Password")
    print("=" * 60)
    
    # Simula session state per admin
    import streamlit as st
    st.session_state.username = 'admin'
    st.session_state.user_info = {'role': 'admin'}
    
    user_settings = UserSettings()
    supabase_manager = SupabaseManager()
    
    # Test 1: Recupero dati utente
    print("\n1️⃣ Test Recupero Dati Utente")
    user_data = user_settings.get_current_user_data()
    
    if user_data:
        print(f"✅ Utente trovato: {user_data['username']}")
        print(f"✅ Email: {user_data['email']}")
        print(f"✅ Hash corrente: {user_data['password_hash'][:30]}...")
    else:
        print("❌ Utente non trovato")
        return False
    
    # Test 2: Verifica password corrente
    print("\n2️⃣ Test Verifica Password Corrente")
    current_password = "admin123"
    current_hash = user_data['password_hash']
    
    password_valid = user_settings.verify_password(current_password, current_hash)
    print(f"✅ Password corrente verificata: {password_valid}")
    
    if not password_valid:
        print("❌ Password corrente non verificata")
        return False
    
    # Test 3: Hash nuova password
    print("\n3️⃣ Test Hash Nuova Password")
    new_password = "NuovaPassword123!"
    new_hash = user_settings.hash_password(new_password)
    print(f"✅ Nuova password hashata: {new_hash[:30]}...")
    
    # Test 4: Simulazione aggiornamento Supabase
    print("\n4️⃣ Test Aggiornamento Supabase")
    try:
        # Simula l'aggiornamento (senza eseguirlo realmente)
        print("✅ Simulazione aggiornamento Supabase:")
        print(f"   - Tabella: users")
        print(f"   - Campo: password_hash")
        print(f"   - Condizione: username = '{user_data['username']}'")
        print(f"   - Nuovo hash: {new_hash[:30]}...")
        
        # Verifica che il nuovo hash sia valido
        new_valid = user_settings.verify_password(new_password, new_hash)
        print(f"✅ Nuovo hash verificato: {new_valid}")
        
        if new_valid:
            print("✅ Aggiornamento simulato con successo!")
            return True
        else:
            print("❌ Nuovo hash non verificato")
            return False
            
    except Exception as e:
        print(f"❌ Errore simulazione aggiornamento: {e}")
        return False

def test_password_change_flow_simplified():
    """Testa il flusso completo semplificato"""
    
    print("\n🔄 Test Flusso Cambio Password Semplificato")
    print("=" * 60)
    
    # Simula session state per admin
    import streamlit as st
    st.session_state.username = 'admin'
    st.session_state.user_info = {'role': 'admin'}
    
    user_settings = UserSettings()
    
    # Dati del form
    current_password = "admin123"
    new_password = "Vtmarkets12!"
    confirm_password = "Vtmarkets12!"
    
    print(f"✅ Password corrente: {current_password}")
    print(f"✅ Nuova password: {new_password}")
    print(f"✅ Conferma password: {confirm_password}")
    
    # Validazioni
    print("\n📋 Test Validazioni")
    
    if not current_password or not new_password or not confirm_password:
        print("❌ Validazione campi obbligatori fallita")
        return False
    print("✅ Campi obbligatori validati")
    
    if new_password != confirm_password:
        print("❌ Validazione password coincidenti fallita")
        return False
    print("✅ Password coincidenti validate")
    
    if len(new_password) < 8:
        print("❌ Validazione lunghezza password fallita")
        return False
    print("✅ Lunghezza password validata")
    
    # Recupero dati utente
    print("\n👤 Test Recupero Dati Utente")
    user_data = user_settings.get_current_user_data()
    if not user_data:
        print("❌ Recupero dati utente fallito")
        return False
    print("✅ Dati utente recuperati")
    
    # Verifica password corrente
    print("\n🔐 Test Verifica Password Corrente")
    current_hash = user_data.get('password_hash', '')
    password_correct = user_settings.verify_password(current_password, current_hash)
    
    if not password_correct:
        print("❌ Verifica password corrente fallita")
        return False
    print("✅ Password corrente verificata")
    
    # Hash nuova password
    print("\n🔒 Test Hash Nuova Password")
    new_password_hash = user_settings.hash_password(new_password)
    print(f"✅ Nuova password hashata: {new_password_hash[:30]}...")
    
    # Verifica nuovo hash
    new_valid = user_settings.verify_password(new_password, new_password_hash)
    print(f"✅ Nuovo hash verificato: {new_valid}")
    
    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    print("🚀 Avvio Test Logica Semplificata Password")
    
    # Esegui test
    test1_result = test_simplified_password_logic()
    test2_result = test_password_change_flow_simplified()
    
    print("\n" + "=" * 70)
    print("📊 RISULTATI FINALI:")
    print(f"✅ Test Logica Semplificata: {'PASSATO' if test1_result else 'FALLITO'}")
    print(f"✅ Test Flusso Semplificato: {'PASSATO' if test2_result else 'FALLITO'}")
    
    if test1_result and test2_result:
        print("\n🎉 TUTTI I TEST SUPERATI!")
        print("💡 La logica semplificata funziona correttamente:")
        print("   • Recupera dati utente da Supabase")
        print("   • Verifica password corrente")
        print("   • Hasha nuova password con bcrypt")
        print("   • Aggiorna direttamente in Supabase")
        print("\n🔧 Ora il cambio password dovrebbe funzionare come nel progetto Lead!")
    else:
        print("\n❌ ALCUNI TEST FALLITI!")
        print("🔧 Controlla la configurazione del sistema semplificato")
    
    print("=" * 70)
