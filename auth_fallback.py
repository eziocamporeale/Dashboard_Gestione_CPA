#!/usr/bin/env python3
"""
🔐 SISTEMA DI AUTENTICAZIONE DI FALLBACK - Dashboard Gestione CPA
Versione semplificata che funziona senza dipendenze esterne
"""

import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FallbackAuthSystem:
    """Sistema di autenticazione di fallback senza dipendenze esterne"""
    
    def __init__(self):
        """Inizializza il sistema di autenticazione"""
        self.users = self.create_default_users()
        self.session_timeout = 3600  # 1 ora
        
    def create_default_users(self) -> Dict:
        """Crea utenti di default"""
        return {
            'admin': {
                'username': 'admin',
                'password_hash': self.hash_password('admin123'),
                'email': 'admin@cpadashboard.com',
                'name': 'Amministratore CPA Dashboard',
                'role': 'admin'
            }
        }
    
    def hash_password(self, password: str) -> str:
        """Hash della password con salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verifica password"""
        try:
            salt, hash_value = stored_hash.split('$')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == hash_value
        except:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Autentica un utente"""
        if username in self.users:
            user = self.users[username]
            if self.verify_password(password, user['password_hash']):
                return True, "Autenticazione riuscita"
            else:
                return False, "Password non corretta"
        else:
            return False, "Utente non trovato"
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Ottiene informazioni su un utente"""
        return self.users.get(username)

# Istanza globale del sistema di autenticazione
auth_system = FallbackAuthSystem()

# Funzioni di interfaccia per compatibilità
def init_auth():
    """Inizializza il sistema di autenticazione"""
    global auth_system
    auth_system = FallbackAuthSystem()
    logger.info("✅ Sistema di autenticazione di fallback inizializzato")

def login_form():
    """Mostra il form di login personalizzato"""
    try:
        st.markdown("### 🔐 **Accesso Dashboard CPA**")
        
        # Form di login
        with st.form("login_form"):
            username = st.text_input("👤 **Username**", placeholder="Inserisci username")
            password = st.text_input("🔑 **Password**", type="password", placeholder="Inserisci password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("🚀 **Accedi**", type="primary")
            with col2:
                if st.form_submit_button("🔄 **Reset**"):
                    st.rerun()
        
        # Gestione login
        if submit_button and username and password:
            success, message = auth_system.authenticate_user(username, password)
            
            if success:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_info = auth_system.get_user_info(username)
                st.session_state.login_time = datetime.now()
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        return st.session_state.get('authenticated', False)
        
    except Exception as e:
        logger.error(f"❌ Errore login form: {e}")
        st.error(f"Errore login: {e}")
        return False

def require_auth():
    """Richiede autenticazione per accedere alla pagina"""
    if not st.session_state.get('authenticated', False):
        st.error("❌ Accesso non autorizzato. Effettua il login.")
        st.stop()
    
    # Verifica timeout sessione
    login_time = st.session_state.get('login_time')
    if login_time:
        elapsed = datetime.now() - login_time
        if elapsed.total_seconds() > auth_system.session_timeout:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.error("⏰ Sessione scaduta. Effettua nuovamente il login.")
            st.stop()

def show_user_info():
    """Mostra informazioni sull'utente corrente"""
    if st.session_state.get('authenticated', False):
        username = st.session_state.get('username', 'N/A')
        user_info = st.session_state.get('user_info', {})
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 **Informazioni Utente**")
        st.sidebar.info(f"**Username:** {username}")
        st.sidebar.info(f"**Nome:** {user_info.get('name', 'N/A')}")
        st.sidebar.info(f"**Email:** {user_info.get('email', 'N/A')}")
        st.sidebar.info(f"**Ruolo:** {user_info.get('role', 'N/A')}")
        
        # Tempo rimanente sessione
        login_time = st.session_state.get('login_time')
        if login_time:
            elapsed = datetime.now() - login_time
            remaining = auth_system.session_timeout - elapsed.total_seconds()
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                st.sidebar.info(f"⏰ **Sessione:** {minutes}m {seconds}s")
        
        if st.sidebar.button("🚪 **Logout**"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.session_state.login_time = None
            st.rerun()

def get_current_user():
    """Ottiene l'utente corrente"""
    return st.session_state.get('username', None)

def get_current_role():
    """Ottiene il ruolo dell'utente corrente"""
    username = get_current_user()
    if username:
        user_info = auth_system.get_user_info(username)
        return user_info.get('role', 'user') if user_info else 'user'
    return None

def has_permission(permission: str) -> bool:
    """Verifica se l'utente ha una determinata permission"""
    role = get_current_role()
    if role == 'admin':
        return True
    return False
