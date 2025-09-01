#!/usr/bin/env python3
"""
🧪 TEST SISTEMA GESTIONE UTENTI - Dashboard CPA
Script per testare tutti i componenti del sistema utenti
"""

import streamlit as st
import sys
import os

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'progetti', 'supabase_integration'))

def test_user_management():
    """Test del componente gestione utenti"""
    st.header("🧪 Test Gestione Utenti")
    
    try:
        from user_management import render_user_management
        st.success("✅ Componente user_management importato correttamente")
        
        # Test renderizzazione
        st.subheader("📊 Test Rendering")
        render_user_management()
        
    except Exception as e:
        st.error(f"❌ Errore test user_management: {e}")

def test_user_settings():
    """Test del componente impostazioni utente"""
    st.header("🧪 Test Impostazioni Utente")
    
    try:
        from user_settings import render_user_settings
        st.success("✅ Componente user_settings importato correttamente")
        
        # Test renderizzazione
        st.subheader("⚙️ Test Rendering")
        render_user_settings()
        
    except Exception as e:
        st.error(f"❌ Errore test user_settings: {e}")

def test_user_navigation():
    """Test del componente navigazione utente"""
    st.header("🧪 Test Navigazione Utente")
    
    try:
        from user_navigation import render_user_navigation
        st.success("✅ Componente user_navigation importato correttamente")
        
        # Test renderizzazione
        st.subheader("🧭 Test Rendering")
        render_user_navigation()
        
    except Exception as e:
        st.error(f"❌ Errore test user_navigation: {e}")

def test_supabase_connection():
    """Test della connessione Supabase"""
    st.header("🧪 Test Connessione Supabase")
    
    try:
        from supabase_manager import SupabaseManager
        st.success("✅ SupabaseManager importato correttamente")
        
        # Test connessione
        supabase_manager = SupabaseManager()
        connection_ok, message = supabase_manager.test_connection()
        
        if connection_ok:
            st.success(f"✅ Connessione Supabase: {message}")
        else:
            st.error(f"❌ Connessione Supabase: {message}")
            
    except Exception as e:
        st.error(f"❌ Errore test Supabase: {e}")

def main():
    """Funzione principale di test"""
    st.title("🧪 TEST COMPLETO SISTEMA UTENTI")
    st.markdown("---")
    
    # Tab per diversi test
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 Supabase", "👥 Gestione Utenti", "⚙️ Impostazioni", "🧭 Navigazione"])
    
    with tab1:
        test_supabase_connection()
    
    with tab2:
        test_user_management()
    
    with tab3:
        test_user_settings()
    
    with tab4:
        test_user_navigation()
    
    st.markdown("---")
    st.success("🎉 Test completato!")

if __name__ == "__main__":
    main()
