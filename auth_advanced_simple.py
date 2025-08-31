#!/usr/bin/env python3
"""
🔐 SISTEMA DI AUTENTICAZIONE AVANZATO CORRETTO - Dashboard Gestione CPA
Versione pulita e funzionante basata su streamlit_authenticator
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleAuthSystem:
    """Sistema di autenticazione semplificato e funzionante"""
    
    def __init__(self):
        """Inizializza il sistema di autenticazione"""
        self.config_path = Path("auth_config.yaml")
        self.load_config()
        self.init_authenticator()
    
    def load_config(self):
        """Carica la configurazione degli utenti"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file)
                logger.info("✅ Configurazione caricata")
            else:
                self.config = self.create_default_config()
                self.save_config()
                logger.info("✅ Configurazione di default creata")
        except Exception as e:
            logger.error(f"❌ Errore caricamento config: {e}")
            self.config = self.create_default_config()
    
    def create_default_config(self):
        """Crea configurazione di default"""
        return {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@cpadashboard.com',
                        'name': 'Amministratore CPA Dashboard',
                        'password': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO6e'  # admin123
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': secrets.token_hex(16),
                'name': 'cpa_dashboard_cookie'
            },
            'preauthorized': {
                'emails': ['admin@cpadashboard.com']
            }
        }
    
    def save_config(self):
        """Salva la configurazione degli utenti"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            logger.info("✅ Configurazione salvata")
        except Exception as e:
            logger.error(f"❌ Errore salvataggio config: {e}")
    
    def init_authenticator(self):
        """Inizializza streamlit_authenticator"""
        try:
            self.authenticator = stauth.Authenticate(
                self.config['credentials'],
                self.config['cookie']['name'],
                self.config['cookie']['key'],
                self.config['cookie']['expiry_days']
            )
            logger.info("✅ Authenticator inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione authenticator: {e}")
            self.authenticator = None
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Ottiene informazioni su un utente"""
        if username in self.config['credentials']['usernames']:
            return self.config['credentials']['usernames'][username]
        return None

# Istanza globale del sistema di autenticazione
auth_system = SimpleAuthSystem()

# Funzioni di interfaccia per compatibilità
def init_auth():
    """Inizializza il sistema di autenticazione"""
    global auth_system
    auth_system = SimpleAuthSystem()
    logger.info("✅ Sistema di autenticazione inizializzato")

def login_form():
    """Mostra il form di login e gestisce l'autenticazione - STESSA LOGICA DELLA DASHBOARD FINANZE"""
    try:
        if not auth_system.authenticator:
            st.error("❌ Sistema di autenticazione non disponibile")
            return False
        
        # STESSA LOGICA DELLA DASHBOARD FINANZE - Quando location='main', il metodo restituisce None
        result = auth_system.authenticator.login(location='main', key='Login')
        
        # Debug: mostra lo stato corrente
        logger.info(f"🔍 Login result: {result}")
        logger.info(f"🔍 Session state auth_status: {st.session_state.get('authentication_status')}")
        
        # STESSA LOGICA DELLA DASHBOARD FINANZE - Se il login è stato completato, controlla lo stato
        if st.session_state.get('authentication_status'):
            if st.session_state['authentication_status']:
                # Login riuscito
                username = st.session_state.get('username', '')
                name = st.session_state.get('name', '')
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_info = auth_system.get_user_info(username)
                
                # Mostra messaggio di successo
                st.success(f'✅ Benvenuto {name}!')
                logger.info(f"✅ Login riuscito per utente: {username}")
                
                # Riavvia l'app per mostrare la dashboard
                st.rerun()
                return True
            else:
                st.error('❌ Username o password non corretti')
                logger.warning(f"❌ Login fallito")
                return False
        
        # Se non c'è ancora stato di autenticazione
        return False
        
    except Exception as e:
        logger.error(f"❌ Errore login form: {e}")
        st.error(f"Errore login: {e}")
        return False

def require_auth():
    """Richiede autenticazione per accedere alla pagina"""
    if not st.session_state.get('authenticated', False):
        st.error("❌ Accesso non autorizzato. Effettua il login.")
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
        
        if st.sidebar.button("🚪 **Logout**"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.rerun()

def get_current_user():
    """Ottiene l'utente corrente"""
    return st.session_state.get('username', None)

def get_current_role():
    """Ottiene il ruolo dell'utente corrente (semplificato)"""
    username = get_current_user()
    if username == 'admin':
        return 'admin'
    return 'user'

def has_permission(permission: str) -> bool:
    """Verifica se l'utente ha una determinata permission"""
    role = get_current_role()
    if role == 'admin':
        return True
    return False
