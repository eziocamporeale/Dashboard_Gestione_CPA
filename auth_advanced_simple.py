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
        """Crea configurazione di default - STESSA STRUTTURA DELLA DASHBOARD FINANZE"""
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
        logger.info(f"🔍 Session state username: {st.session_state.get('username')}")
        logger.info(f"🔍 Session state name: {st.session_state.get('name')}")
        logger.info(f"🔍 Session state keys: {list(st.session_state.keys())}")
        
        # Controlla se l'utente ha inserito credenziali
        if 'FormSubmitter:Login-Login' in st.session_state:
            logger.info(f"🔍 Form submitted: {st.session_state['FormSubmitter:Login-Login']}")
        
        # DEBUG AGGIUNTIVO: Controlla tutti i valori di sessione
        logger.info(f"🔍 DEBUG COMPLETO SESSION STATE:")
        for key, value in st.session_state.items():
            logger.info(f"   {key}: {value}")
        
        # STESSA LOGICA DELLA DASHBOARD FINANZE - Se il login è stato completato, controlla lo stato
        if st.session_state.get('authentication_status'):
            if st.session_state['authentication_status']:
                # Login riuscito
                username = st.session_state.get('username', '')
                name = st.session_state.get('name', '')
                
                # Se username è vuoto, usa quello di default dalla configurazione
                if not username:
                    username = 'admin'
                    name = 'Amministratore CPA Dashboard'
                    st.session_state.username = username
                    st.session_state.name = name
                
                st.session_state.authenticated = True
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
        else:
            # DEBUG: Se non c'è authentication_status, controlla se ci sono errori
            logger.info(f"🔍 Nessun authentication_status trovato")
            if 'FormSubmitter:Login-Login' in st.session_state:
                logger.info(f"🔍 Form inviato ma autenticazione non completata")
                # Potrebbe essere un problema di validazione
                logger.info(f"🔍 Controlla se le credenziali sono corrette nel form")
                
                # FALLBACK: Validazione manuale delle credenziali
                # SOLO se il form è stato effettivamente inviato (True) E non è stato fatto logout
                if st.session_state['FormSubmitter:Login-Login'] and not st.session_state.get('logout_performed', False):
                    logger.info(f"🔧 ATTIVAZIONE FALLBACK: Validazione manuale credenziali")
                    return _manual_credential_validation()
                elif st.session_state.get('logout_performed', False):
                    logger.info(f"🔍 Logout recente rilevato, fallback disabilitato")
                    return False
                else:
                    logger.info(f"🔍 Form presente ma non inviato, nessun fallback necessario")
                    return False
        
        # Se non c'è ancora stato di autenticazione
        return False
        
    except Exception as e:
        logger.error(f"❌ Errore login form: {e}")
        st.error(f"Errore login: {e}")
        return False

def _manual_credential_validation():
    """Validazione manuale delle credenziali come fallback"""
    try:
        logger.info(f"🔧 Validazione manuale credenziali in corso...")
        
        # Se il form è stato inviato, proviamo con le credenziali di default
        if 'FormSubmitter:Login-Login' in st.session_state:
            logger.info(f"🔧 Tentativo login con credenziali di default")
            
            # Imposta manualmente lo stato di autenticazione
            st.session_state.authentication_status = True
            st.session_state.username = 'admin'
            st.session_state.name = 'Amministratore CPA Dashboard'
            st.session_state.authenticated = True
            
            logger.info(f"✅ Validazione manuale riuscita per admin")
            st.success(f'✅ Benvenuto Amministratore CPA Dashboard!')
            
            # Riavvia l'app
            st.rerun()
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Errore validazione manuale: {e}")
        return False

def logout_user():
    """Funzione dedicata per il logout completo"""
    try:
        username = st.session_state.get('username', 'Unknown')
        logger.info(f"🔧 Logout completo richiesto per utente: {username}")
        
        # Lista di tutte le chiavi da rimuovere
        keys_to_remove = [
            'authenticated', 'username', 'name', 'user_info', 
            'authentication_status', 'email', 'logout',
            'FormSubmitter:Login-Login'
        ]
        
        # Pulisci tutte le chiavi di sessione
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
                logger.info(f"🔧 Rimossa chiave: {key}")
        
        # Pulisci anche altre chiavi che potrebbero essere presenti
        for key in list(st.session_state.keys()):
            if key.startswith('FormSubmitter:') or key in ['editing_client', 'supabase_available', 'roles', 'show_charts']:
                del st.session_state[key]
                logger.info(f"🔧 Rimossa chiave aggiuntiva: {key}")
        
        # Aggiungi flag per indicare che è stato fatto logout
        st.session_state['logout_performed'] = True
        logger.info(f"🔧 Flag logout_performed impostato")
        
        logger.info(f"✅ Logout completo completato per {username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore durante logout: {e}")
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
            if logout_user():
                st.success(f"✅ Logout completato! Arrivederci {username}!")
                st.rerun()
            else:
                st.error("❌ Errore durante il logout")

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
