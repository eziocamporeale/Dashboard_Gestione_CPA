#!/usr/bin/env python3
"""
🔐 SISTEMA DI AUTENTICAZIONE AVANZATO - Dashboard Gestione CPA
Integrazione completa con Supabase + streamlit_authenticator
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

class AdvancedAuthSystem:
    """Sistema di autenticazione avanzato integrato con Supabase"""
    
    def __init__(self):
        self.config_path = Path("config/auth_config.yaml")
        self.supabase_manager = None
        self.authenticator = None
        self.init_supabase()
        self.load_config()
    
    def init_supabase(self):
        """Inizializza la connessione Supabase"""
        try:
            from progetti.supabase_integration.supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
            if self.supabase_manager.is_configured:
                logger.info("✅ Supabase Manager inizializzato")
            else:
                logger.warning("⚠️ Supabase non configurato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase: {e}")
            self.supabase_manager = None
    
    def load_config(self):
        """Carica la configurazione degli utenti"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as file:
                    self.config = yaml.load(file, Loader=yaml.SafeLoader)
                logger.info("✅ Configurazione autenticazione caricata")
            except Exception as e:
                logger.error(f"❌ Errore caricamento config: {e}")
                self.config = self.create_default_config()
        else:
            self.config = self.create_default_config()
            self.save_config()
        
        # Inizializza l'authenticator
        self.init_authenticator()
    
    def create_default_config(self):
        """Crea configurazione di default con utente admin"""
        return {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@cpadashboard.com',
                        'name': 'Amministratore CPA Dashboard',
                        'password': stauth.Hasher(['admin123']).generate()[0]
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
    
    def sync_users_with_supabase(self):
        """Sincronizza utenti tra config locale e Supabase"""
        if not self.supabase_manager or not self.supabase_manager.supabase:
            return False, "Supabase non disponibile"
        
        try:
            # Recupera utenti da Supabase
            response = self.supabase_manager.supabase.table('users').select('*').execute()
            supabase_users = response.data if response.data else []
            
            # Aggiorna config locale
            for user in supabase_users:
                username = user.get('username')
                if username and username not in self.config['credentials']['usernames']:
                    self.config['credentials']['usernames'][username] = {
                        'email': user.get('email', ''),
                        'name': user.get('full_name', username),
                        'password': user.get('password_hash', '')
                    }
            
            self.save_config()
            self.init_authenticator()
            return True, f"Sincronizzati {len(supabase_users)} utenti"
            
        except Exception as e:
            return False, f"Errore sincronizzazione: {e}"
    
    def create_user(self, username: str, email: str, password: str, full_name: str, role: str = 'user') -> Tuple[bool, str]:
        """Crea un nuovo utente sia in config che in Supabase"""
        try:
            # Verifica se l'utente esiste già
            if username in self.config['credentials']['usernames']:
                return False, "Username già esistente"
            
            # Hash della password
            hashed_password = stauth.Hasher([password]).generate()[0]
            
            # Crea utente nella configurazione locale
            self.config['credentials']['usernames'][username] = {
                'email': email,
                'name': full_name,
                'password': hashed_password
            }
            self.save_config()
            
            # Crea utente in Supabase se disponibile
            if self.supabase_manager and self.supabase_manager.supabase:
                user_data = {
                    'username': username,
                    'email': email,
                    'password_hash': hashed_password,
                    'full_name': full_name,
                    'role': role
                }
                
                response = self.supabase_manager.supabase.table('users').insert(user_data).execute()
                if response.data:
                    logger.info(f"✅ Utente {username} creato in Supabase")
                else:
                    logger.warning(f"⚠️ Utente {username} creato solo localmente")
            
            # Reinizializza authenticator
            self.init_authenticator()
            return True, f"Utente {username} creato con successo"
            
        except Exception as e:
            return False, f"Errore creazione utente: {e}"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Autentica un utente"""
        if not self.authenticator:
            return False, "Sistema di autenticazione non disponibile", None
        
        try:
            # Verifica credenziali
            if username in self.config['credentials']['usernames']:
                stored_password = self.config['credentials']['usernames'][username]['password']
                
                # Verifica password
                if stauth.Hasher([password]).verify(stored_password):
                    # Login riuscito
                    user_info = self.config['credentials']['usernames'][username]
                    
                    # Aggiorna ultimo login in Supabase
                    if self.supabase_manager and self.supabase_manager.supabase:
                        try:
                            self.supabase_manager.supabase.table('users').update({
                                'last_login': datetime.now().isoformat()
                            }).eq('username', username).execute()
                        except Exception as e:
                            logger.warning(f"⚠️ Errore aggiornamento ultimo login: {e}")
                    
                    return True, f"✅ Benvenuto {username}!", user_info
                else:
                    # Password errata
                    self.record_failed_attempt(username)
                    return False, "❌ Password non valida", None
            else:
                return False, "❌ Utente non trovato", None
                
        except Exception as e:
            return False, f"❌ Errore autenticazione: {e}", None
    
    def record_failed_attempt(self, username: str):
        """Registra un tentativo di login fallito"""
        if self.supabase_manager and self.supabase_manager.supabase:
            try:
                failed_attempt = {
                    'username': username,
                    'ip_address': '127.0.0.1',  # In produzione, usa IP reale
                    'user_agent': 'Streamlit App'
                }
                
                self.supabase_manager.supabase.table('failed_login_attempts').insert(failed_attempt).execute()
            except Exception as e:
                logger.warning(f"⚠️ Errore registrazione tentativo fallito: {e}")
    
    def check_rate_limit(self, username: str) -> bool:
        """Controlla il rate limiting per un utente"""
        if not self.supabase_manager or not self.supabase_manager.supabase:
            return True  # Se Supabase non disponibile, non bloccare
        
        try:
            # Conta tentativi falliti negli ultimi 15 minuti
            cutoff_time = (datetime.now() - timedelta(minutes=15)).isoformat()
            
            response = self.supabase_manager.supabase.table('failed_login_attempts').select(
                'count', count='exact'
            ).eq('username', username).gte('attempted_at', cutoff_time).execute()
            
            failed_count = response.count if response.count else 0
            max_attempts = 3
            
            if failed_count >= max_attempts:
                logger.warning(f"⚠️ Utente {username} bloccato per troppi tentativi falliti")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Errore controllo rate limit: {e}")
            return True  # In caso di errore, non bloccare
    
    def get_user_role(self, username: str) -> str:
        """Recupera il ruolo di un utente da Supabase"""
        if not self.supabase_manager or not self.supabase_manager.supabase:
            return 'user'  # Default se Supabase non disponibile
        
        try:
            response = self.supabase_manager.supabase.table('users').select('role').eq('username', username).execute()
            if response.data:
                return response.data[0].get('role', 'user')
        except Exception as e:
            logger.warning(f"⚠️ Errore recupero ruolo utente: {e}")
        
        return 'user'
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Verifica se un utente ha un determinato permesso"""
        if not self.supabase_manager or not self.supabase_manager.supabase:
            return True  # Default se Supabase non disponibile
        
        try:
            # Recupera permessi utente
            response = self.supabase_manager.supabase.table('user_permissions').select('permission').eq('user_id', 
                self.supabase_manager.supabase.table('users').select('id').eq('username', username)
            ).execute()
            
            if response.data:
                user_permissions = [p.get('permission') for p in response.data]
                return permission in user_permissions
            
        except Exception as e:
            logger.warning(f"⚠️ Errore verifica permessi: {e}")
        
        # Fallback: verifica per ruolo
        role = self.get_user_role(username)
        if role == 'admin':
            return True
        elif role == 'manager' and permission in ['read', 'write']:
            return True
        elif role == 'user' and permission == 'read':
            return True
        
        return False
    
    def logout_user(self, username: str):
        """Logout di un utente"""
        try:
            # Rimuovi sessioni in Supabase
            if self.supabase_manager and self.supabase_manager.supabase:
                self.supabase_manager.supabase.table('user_sessions').delete().eq('user_id', 
                    self.supabase_manager.supabase.table('users').select('id').eq('username', username)
                ).execute()
            
            logger.info(f"✅ Utente {username} disconnesso")
            
        except Exception as e:
            logger.warning(f"⚠️ Errore logout: {e}")

# Istanza globale del sistema di autenticazione
auth_system = AdvancedAuthSystem()

# Funzioni di interfaccia per compatibilità
def init_auth():
    """Inizializza l'autenticazione nella sessione"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

def login_form():
    """Mostra il form di login avanzato"""
    st.markdown("---")
    st.markdown("## 🔐 **Accesso Sistema Avanzato CPA**")
    
    # Sincronizza utenti con Supabase
    if st.button("🔄 Sincronizza con Supabase"):
        success, message = auth_system.sync_users_with_supabase()
        if success:
            st.success(message)
        else:
            st.error(message)
    
    with st.form("advanced_login_form"):
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
                st.session_state.user_info = None
                st.rerun()
        
        if submit_button:
            if username and password:
                # Controlla rate limiting
                if not auth_system.check_rate_limit(username):
                    st.error("🔒 **Account bloccato temporaneamente** - Troppi tentativi falliti")
                    return
                
                # Autentica utente
                success, message, user_info = auth_system.authenticate_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = auth_system.get_user_role(username)
                    st.session_state.user_info = user_info
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("⚠️ **Inserisci username e password** per accedere.")

def require_auth():
    """Decoratore per richiedere autenticazione avanzata"""
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
        
        if st.session_state.user_info:
            st.sidebar.info(f"**Nome:** {st.session_state.user_info.get('name', 'N/A')}")
            st.sidebar.info(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")
        
        # Pulsante logout
        if st.sidebar.button("🚪 **Logout**"):
            auth_system.logout_user(st.session_state.username)
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.user_info = None
            st.rerun()

def get_current_user():
    """Restituisce l'utente corrente"""
    if st.session_state.get('authenticated'):
        return st.session_state.username
    return None

def get_current_role():
    """Restituisce il ruolo dell'utente corrente"""
    if st.session_state.get('authenticated'):
        return st.session_state.user_role
    return 'user'

def has_permission(permission: str) -> bool:
    """Verifica se l'utente corrente ha un determinato permesso"""
    username = get_current_user()
    if username:
        return auth_system.has_permission(username, permission)
    return False
