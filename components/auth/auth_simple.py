#!/usr/bin/env python3
"""
Sistema di Autenticazione Semplificato per Dashboard_Gestione_CPA
Gestisce login, logout, sessioni e permessi
Creato da Ezio Camporeale
"""

import streamlit as st
import hashlib
import secrets
import logging
from typing import Dict, Optional
from datetime import datetime

# Configurazione logging
logger = logging.getLogger(__name__)

class SimpleAuthSystem:
    """Sistema di autenticazione semplificato"""
    
    def __init__(self):
        """Inizializza il sistema di autenticazione"""
        self.users = {
            'admin': {
                'user_id': 1,
                'username': 'admin',
                'password_hash': 'admin123',  # Password corretta per progetto CPA
                'email': 'admin@cpadashboard.com',
                'name': 'Amministratore CPA Dashboard',
                'role': 'admin',
                'from_supabase': False
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
            # Se è un hash bcrypt (inizia con $2b$)
            if stored_hash.startswith('$2b$'):
                import bcrypt
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            # Se è un hash semplice (per test)
            elif stored_hash == password:
                return True
            # Se è un hash con salt
            elif '$' in stored_hash:
                salt, hash_part = stored_hash.split('$', 1)
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return password_hash == hash_part
            else:
                return False
        except Exception as e:
            logger.error(f"Errore verifica password: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Autentica un utente"""
        try:
            if username in self.users:
                user = self.users[username]
                if self.verify_password(password, user['password_hash']):
                    logger.info(f"✅ Autenticazione riuscita per utente: {username}")
                    return True
                else:
                    logger.warning(f"❌ Password errata per utente: {username}")
                    return False
            else:
                logger.warning(f"❌ Utente non trovato: {username}")
                return False
        except Exception as e:
            logger.error(f"❌ Errore autenticazione: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Ottiene le informazioni di un utente"""
        try:
            if username in self.users:
                user = self.users[username]
                # Ritorna solo i dati non sensibili
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role'],
                    'from_supabase': user['from_supabase']
                }
            else:
                logger.warning(f"❌ Utente non trovato: {username}")
                return None
        except Exception as e:
            logger.error(f"❌ Errore recupero info utente: {e}")
            return None

# Istanza globale del sistema di autenticazione
auth_system = SimpleAuthSystem()

def require_auth(func):
    """Decorator per richiedere autenticazione"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("❌ Accesso non autorizzato. Effettua il login.")
            return None
        return func(*args, **kwargs)
    return wrapper

def get_current_user():
    """Ottiene l'utente corrente"""
    if st.session_state.get('authenticated', False):
        username = st.session_state.get('username')
        if username:
            return auth_system.get_user_info(username)
    return None

def render_login_form():
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
                    # Reset senza rerun per evitare loop
                    st.session_state.clear()
        
        # Gestione login
        if submit_button and username and password:
            if auth_system.authenticate_user(username, password):
                # Login riuscito
                user_info = auth_system.get_user_info(username)
                
                # Imposta lo stato di sessione
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.name = user_info['name']
                st.session_state.role = user_info['role']
                st.session_state.user_id = user_info['user_id']
                # IMPORTANTE: Imposta user_info completo con tutti i dati inclusi l'id
                st.session_state.user_info = user_info
                
                logger.info(f"✅ Login riuscito per utente: {username}")
                logger.info(f"🔍 DEBUG: user_info impostato nella sessione (senza dati sensibili)")
                st.success(f'✅ Benvenuto {user_info["name"]}!')
                
                # Rerun necessario per aggiornare la pagina dopo il login
                st.rerun()
                return True
            else:
                # Login fallito
                st.error('❌ Username o password non corretti')
                logger.warning(f"❌ Login fallito per utente: {username}")
                return False
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Errore login form: {e}")
        st.error(f"❌ Errore sistema di autenticazione: {e}")
        return False

def render_logout_section():
    """Mostra la sezione di logout"""
    try:
        if st.session_state.get('authenticated', False):
            username = st.session_state.get('username', 'Utente')
            name = st.session_state.get('name', username)
            role = st.session_state.get('role', 'user')
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 **Utente Corrente**")
            st.sidebar.info(f"**Nome:** {name}\n\n**Username:** {username}\n\n**Ruolo:** {role}")
            
            if st.sidebar.button("🚪 **Logout**", use_container_width=True):
                # Pulisci session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                st.success("✅ Logout effettuato con successo!")
                st.rerun()
                
    except Exception as e:
        logger.error(f"❌ Errore logout: {e}")
        st.error(f"❌ Errore durante il logout: {e}")

# Alias per compatibilità
login_form = render_login_form
show_user_info = render_logout_section
init_auth = lambda: None  # Non serve inizializzazione
