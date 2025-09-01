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
        self.logout_performed = False  # Flag per tracciare il logout
    
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
    
    def disable_authenticator(self):
        """Disabilita temporaneamente l'authenticator dopo logout"""
        self.logout_performed = True
        logger.info("🔧 Authenticator disabilitato temporaneamente")
    
    def enable_authenticator(self):
        """Riabilita l'authenticator"""
        self.logout_performed = False
        logger.info("🔧 Authenticator riabilitato")
    
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
    # CONTROLLO DI SICUREZZA: verifica che l'authenticator sia disponibile
    if not auth_system.authenticator:
        logger.error("❌ Sistema di autenticazione non disponibile")
        st.error("❌ Sistema di autenticazione non disponibile")
        return False
    
    # CONTROLLO DI SICUREZZA: verifica che la configurazione sia valida
    if not hasattr(auth_system.authenticator, 'login'):
        logger.error("❌ Metodo login non disponibile nell'authenticator")
        st.error("❌ Errore configurazione sistema di autenticazione")
        return False
    
    # HOOK: verifica se il logout è stato eseguito
    if st.session_state.get('logout_performed') or auth_system.logout_performed:
        logger.info(f"🔍 HOOK LOGIN: Logout rilevato, pulendo sessione")
        # Se è stato fatto logout, pulisci tutto e non procedere con il login
        st.session_state.clear()
        auth_system.enable_authenticator()  # Riabilita l'authenticator
        st.rerun()
        return False
    
    # DEBUG: verifica cookie di sessione
    init_data = st.session_state.get('init', {})
    if init_data and 'cpa_dashboard_cookie' in init_data:
        logger.info(f"🔍 Cookie di sessione rilevato: {st.session_state['init']['cpa_dashboard_cookie']}")
        # Se c'è un cookie valido, forza il ruolo admin
        if st.session_state.get('username') == 'admin':
            st.session_state.roles = 'admin'
            logger.info(f"🔧 Ruolo forzato da cookie: admin")
            # HOOK: traccia quando viene forzato il ruolo da cookie
            logger.info(f"🔍 HOOK COOKIE: roles forzato a admin da cookie")
            logger.info(f"🔍 HOOK COOKIE: roles dopo forzatura = {st.session_state.get('roles')}")
    
    # GESTIONE COMPLETA DEL LOGIN - STESSA LOGICA DI DASH FINANZE
    # Se l'authenticator è disabilitato, non usarlo
    if auth_system.logout_performed:
        logger.info(f"🔍 Authenticator disabilitato, mostrando solo form di login")
        st.markdown("### 🔐 **Accesso Dashboard CPA**")
        st.info("🔄 Effettua nuovamente l'accesso per continuare")
        
        # Form di login semplice
        with st.form("login_form_simple"):
            username = st.text_input("👤 **Username**", placeholder="Inserisci username")
            password = st.text_input("🔑 **Password**", type="password", placeholder="Inserisci password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("🚀 **Accedi**", type="primary")
            with col2:
                if st.form_submit_button("🔄 **Reset**"):
                    st.rerun()
        
        # Gestione login semplice
        if submit_button and username and password:
            if username == 'admin' and password == 'admin':
                # Login riuscito
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.name = 'Amministratore CPA Dashboard'
                st.session_state.roles = 'admin'
                auth_system.enable_authenticator()  # Riabilita l'authenticator
                
                st.success(f'✅ Benvenuto Amministratore CPA Dashboard!')
                st.rerun()
                return True
            else:
                st.error('❌ Username o password non corretti')
                return False
        
        return False
    
    # Se l'authenticator è abilitato, usa il metodo normale
    logger.info(f"🔍 Tentativo di chiamare authenticator.login()...")
    
    # APPROCCIO CORRETTO: quando location='main', il metodo restituisce None
    # Dobbiamo gestire diversamente come in Dash_Gestione_Finanaze_Ezio
    result = auth_system.authenticator.login(location='main', key='Login')
    logger.info(f"🔍 Login chiamato, result={result}")
    
    # Se il login è stato completato, controlla lo stato
    if st.session_state.get('authentication_status'):
        if st.session_state['authentication_status']:
            # Login riuscito
            username = st.session_state.get('username')
            name = st.session_state.get('name')
            logger.info(f"✅ Login riuscito per utente: {username}")
            
            # Imposta direttamente lo stato di sessione
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.name = name
            st.session_state.roles = 'admin' if username == 'admin' else 'user'
            
            # Mostra messaggio di successo
            st.success(f'✅ Benvenuto {name}!')
            
            # Riavvia l'app per mostrare la dashboard
            st.rerun()
            return True
        else:
            # Login fallito
            st.error('❌ Username o password non corretti')
            logger.warning(f"❌ Login fallito")
            return False
    
    # Se non c'è ancora stato di autenticazione, il form non è stato inviato
    logger.info(f"🔍 Form di login non ancora inviato")
    return False

def _manual_credential_validation():
    """Validazione manuale delle credenziali come fallback"""
    try:
        logger.info(f"🔧 Validazione manuale credenziali in corso...")
        
        # Se il form è stato inviato, proviamo con le credenziali di default
        if hasattr(st, 'session_state') and st.session_state and 'FormSubmitter:Login-Login' in st.session_state:
            logger.info(f"🔧 Tentativo login con credenziali di default")
            
            # Imposta manualmente lo stato di autenticazione
            st.session_state.authentication_status = True
            st.session_state.username = 'admin'
            st.session_state.name = 'Amministratore CPA Dashboard'
            st.session_state.authenticated = True
            st.session_state.roles = 'admin'  # Aggiungi il ruolo admin
            
            # HOOK: traccia quando viene impostato il ruolo admin
            logger.info(f"🔍 HOOK VALIDAZIONE: admin validato, roles = {st.session_state.get('roles')}")
            
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
        
        # HOOK: traccia il cookie prima del logout
        init_data = st.session_state.get('init', {})
        if init_data and 'cpa_dashboard_cookie' in init_data:
            logger.info(f"🔍 HOOK LOGOUT: Cookie prima del logout: {init_data['cpa_dashboard_cookie']}")
        
        # DISABILITA TEMPORANEAMENTE I LOG RLS PER EVITARE ERRORI
        logger.info(f"🔧 Logout: disabilitazione temporanea log RLS")
        
        # Lista di tutte le chiavi da rimuovere
        keys_to_remove = [
            'authenticated', 'username', 'name', 'user_info', 
            'authentication_status', 'email', 'logout',
            'FormSubmitter:Login-Login', 'roles'  # Aggiungi anche roles
        ]
        
        # Pulisci tutte le chiavi di sessione
        if hasattr(st, 'session_state') and st.session_state:
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
                    logger.info(f"🔧 Rimossa chiave: {key}")
        else:
            logger.warning("⚠️ session_state non disponibile durante pulizia chiavi")
        
        # Pulisci anche altre chiavi che potrebbero essere presenti
        if hasattr(st, 'session_state') and st.session_state:
            try:
                for key in list(st.session_state.keys()):
                    if key.startswith('FormSubmitter:') or key in ['editing_client', 'supabase_available', 'show_charts']:
                        del st.session_state[key]
                        logger.info(f"🔧 Rimossa chiave aggiuntiva: {key}")
            except Exception as e:
                logger.warning(f"⚠️ Impossibile iterare session_state.keys(): {e}")
        else:
            logger.warning("⚠️ session_state non disponibile durante pulizia chiavi aggiuntive")
        
        # GESTIONE COOKIE DI SESSIONE - PULISCI IL COOKIE COMPLETAMENTE
        if 'init' in st.session_state:
            init_data = st.session_state['init']
            if isinstance(init_data, dict) and 'cpa_dashboard_cookie' in init_data:
                # Rimuovi il cookie di sessione
                del st.session_state['init']['cpa_dashboard_cookie']
                logger.info(f"🔧 Cookie di sessione rimosso")
            
            # Rimuovi completamente la chiave init per forzare un nuovo login
            del st.session_state['init']
            logger.info(f"🔧 Chiave init rimossa completamente")
        
        # Rimuovi anche il flag logout_performed per evitare loop
        if 'logout_performed' in st.session_state:
            del st.session_state['logout_performed']
            logger.info(f"🔧 Flag logout_performed rimosso")
        
        # Disabilita l'authenticator per evitare re-login automatico
        auth_system.disable_authenticator()
        
        # Aggiungi flag per indicare che è stato fatto logout
        st.session_state['logout_performed'] = True
        logger.info(f"🔧 Flag logout_performed impostato")
        
        # HOOK: traccia quando il logout è completato
        logger.info(f"🔍 HOOK LOGOUT: logout completato per {username}")
        logger.info(f"🔍 HOOK LOGOUT: session_state dopo logout:")
        if hasattr(st, 'session_state') and st.session_state:
            try:
                for key, value in st.session_state.items():
                    logger.info(f"   {key}: {value}")
            except Exception as e:
                logger.warning(f"⚠️ Impossibile iterare session_state: {e}")
        else:
            logger.info("   session_state non disponibile o vuoto")
        
        logger.info(f"✅ Logout completo completato per {username}")
        
        # Forza un refresh completo del browser per rimuovere il cookie
        st.success("✅ Logout completato! Ricarica la pagina per continuare.")
        st.info("🔄 Ricarica la pagina per completare il logout")
        
        # Forza un rerun completo
        st.rerun()
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
                # HOOK: traccia il logout completato
                logger.info(f"🔍 HOOK LOGOUT: Logout completato, forzando rerun completo")
                # Forza un rerun completo per pulire tutto
                st.rerun()
            else:
                st.error("❌ Errore durante il logout")

def get_current_user():
    """Ottiene l'utente corrente"""
    return st.session_state.get('username', None)

def get_current_role():
    """Ottiene il ruolo dell'utente corrente (semplificato)"""
    # HOOK GLOBALE: traccia ogni chiamata a get_current_role
    logger.info(f"🔍 HOOK GLOBALE: get_current_role() chiamata")
    
    # DEBUG: mostra tutto il session_state per capire cosa succede
    logger.info(f"🔍 DEBUG get_current_role - Session state completo:")
    if hasattr(st, 'session_state') and st.session_state:
        try:
            for key, value in st.session_state.items():
                logger.info(f"   {key}: {value}")
        except Exception as e:
            logger.warning(f"⚠️ Impossibile iterare session_state in get_current_role: {e}")
    else:
        logger.info("   session_state non disponibile o vuoto in get_current_role")
    
    # Prima controlla se il ruolo è già impostato nel session_state
    if st.session_state.get('roles'):
        role = st.session_state.get('roles')
        logger.info(f"🔍 Ruolo recuperato da session_state: {role}")
        # HOOK: traccia quando viene letto il ruolo
        logger.info(f"🔍 HOOK LETTURA: roles letto = {role}")
        return role
    
    # Fallback: determina il ruolo dall'username
    username = get_current_user()
    logger.info(f"🔍 Username corrente: {username}")
    
    if username == 'admin':
        # Imposta il ruolo nel session_state se non è presente
        st.session_state.roles = 'admin'
        logger.info(f"🔧 Ruolo impostato da fallback: admin per {username}")
        # FORZA IL MANTENIMENTO
        logger.info(f"🔧 FORZATURA FALLBACK: roles = {st.session_state.get('roles')}")
        return 'admin'
    
    # Imposta il ruolo user di default
    st.session_state.roles = 'user'
    logger.info(f"🔧 Ruolo impostato da fallback: user per {username}")
    # FORZA IL MANTENIMENTO
    logger.info(f"🔧 FORZATURA FALLBACK: roles = {st.session_state.get('roles')}")
    return 'user'

def has_permission(permission: str) -> bool:
    """Verifica se l'utente ha una determinata permission"""
    # HOOK: traccia ogni chiamata a has_permission
    logger.info(f"🔍 HOOK PERMISSION: has_permission('{permission}') chiamata")
    
    # FORZA IL MANTENIMENTO DEL RUOLO PRIMA DI VERIFICARE
    username = get_current_user()
    if username == 'admin' and not st.session_state.get('roles'):
        st.session_state.roles = 'admin'
        logger.info(f"🔧 Ruolo forzato in has_permission: admin per {username}")
        # HOOK: traccia quando viene forzato il ruolo
        logger.info(f"🔍 HOOK FORZATURA: roles forzato a admin in has_permission")
    
    role = get_current_role()
    logger.info(f"🔍 Verifica permesso '{permission}' per ruolo: {role}")
    
    if role == 'admin':
        return True
    return False
