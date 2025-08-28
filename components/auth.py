#!/usr/bin/env python3
"""
Componente per l'autenticazione e gestione sessioni
"""

import streamlit as st

# Import dal package config
from config.users import is_valid_user, get_user_role, has_permission

def init_auth():
    """Inizializza l'autenticazione nella sessione"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def login_form():
    """Mostra il form di login"""
    st.markdown("---")
    st.markdown("## 🔐 **Accesso Sistema**")
    
    with st.form("login_form"):
        username = st.text_input("👤 **Username**", placeholder="Inserisci username")
        password = st.text_input("🔒 **Password**", type="password", placeholder="Inserisci password")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            submit_button = st.form_submit_button("🚀 **Accedi**", type="primary")
        with col2:
            if st.form_submit_button("🔙 **Reset**"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.rerun()
        
        if submit_button:
            if username and password:
                if is_valid_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = get_user_role(username)
                    st.success(f"✅ **Benvenuto {username}!** Accesso effettuato con successo.")
                    st.rerun()
                else:
                    st.error("❌ **Credenziali non valide!** Username o password errati.")
            else:
                st.warning("⚠️ **Inserisci username e password** per accedere.")

def require_auth():
    """Decoratore per richiedere autenticazione"""
    init_auth()
    
    if not st.session_state.authenticated:
        st.error("🔒 **Accesso Richiesto**")
        st.info("Devi effettuare l'accesso per utilizzare questa funzionalità.")
        login_form()
        st.stop()
    
    return True

def show_user_info():
    """Mostra informazioni sull'utente corrente"""
    if st.session_state.authenticated:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 **Utente Corrente**")
        st.sidebar.success(f"**Username:** {st.session_state.username}")
        st.sidebar.info(f"**Ruolo:** {st.session_state.user_role}")
        
        if st.sidebar.button("🚪 **Logout**"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.rerun()

def check_permission(permission: str) -> bool:
    """Verifica se l'utente corrente ha una permission specifica"""
    if not st.session_state.authenticated:
        return False
    
    username = st.session_state.username
    return has_permission(username, permission)

def permission_required(permission: str):
    """Decoratore per richiedere una permission specifica"""
    if not check_permission(permission):
        st.error(f"🚫 **Permesso Negato** - Non hai i permessi per questa operazione.")
        st.info(f"Richiesta permission: **{permission}**")
        st.stop()
    return True
