#!/usr/bin/env python3
"""
Sistema di autenticazione SICURO per Dashboard Gestione CPA
LEGGE le credenziali da variabili d'ambiente (.env) - NON hardcoded!
"""

import os
import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

class SecureAuth:
    """Sistema di autenticazione sicuro con credenziali da variabili d'ambiente"""
    
    def __init__(self):
        self.users = self._load_users_from_env()
        self.failed_attempts = {}
        self.max_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', 3))
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', 3600))
        
    def _load_users_from_env(self):
        """Carica utenti da variabili d'ambiente in modo sicuro"""
        users = {}
        
        # Admin user
        admin_user = os.getenv('ADMIN_USERNAME')
        admin_pass = os.getenv('ADMIN_PASSWORD')
        if admin_user and admin_pass:
            users[admin_user] = {
                'password': admin_pass,
                'role': 'admin',
                'permissions': ['read', 'write', 'delete', 'admin']
            }
        
        # Manager user
        manager_user = os.getenv('MANAGER_USERNAME')
        manager_pass = os.getenv('MANAGER_PASSWORD')
        if manager_user and manager_pass:
            users[manager_user] = {
                'password': manager_pass,
                'role': 'manager',
                'permissions': ['read', 'write', 'delete']
            }
        
        # Viewer user
        viewer_user = os.getenv('VIEWER_USERNAME')
        viewer_pass = os.getenv('VIEWER_PASSWORD')
        if viewer_user and viewer_pass:
            users[viewer_user] = {
                'password': viewer_pass,
                'role': 'viewer',
                'permissions': ['read']
            }
        
        # Se non ci sono utenti configurati, crea un admin di default
        if not users:
            st.warning("⚠️ **ATTENZIONE**: Nessun utente configurato nel file .env!")
            st.info("Crea un file .env basato su env.example con le tue credenziali reali")
            # Crea un admin temporaneo solo per sviluppo
            users['admin'] = {
                'password': 'CHANGE_ME_IMMEDIATELY',
                'role': 'admin',
                'permissions': ['read', 'write', 'delete', 'admin']
            }
        
        return users
    
    def _hash_password(self, password):
        """Hash della password per confronto sicuro"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_rate_limit(self, username):
        """Controlla il rate limiting per tentativi di login falliti"""
        if username in self.failed_attempts:
            attempts = self.failed_attempts[username]
            # Rimuovi tentativi più vecchi di 15 minuti
            attempts = [t for t in attempts if datetime.now() - t < timedelta(minutes=15)]
            self.failed_attempts[username] = attempts
            
            if len(attempts) >= self.max_attempts:
                return False
        
        return True
    
    def _record_failed_attempt(self, username):
        """Registra un tentativo di login fallito"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        self.failed_attempts[username].append(datetime.now())
    
    def authenticate(self, username, password):
        """Autentica un utente in modo sicuro"""
        # Controlla rate limiting
        if not self._check_rate_limit(username):
            return False, "🔒 **Account bloccato temporaneamente** - Troppi tentativi falliti"
        
        # Verifica credenziali
        if username in self.users:
            stored_password = self.users[username]['password']
            
            # Per compatibilità, prova sia hash che password in chiaro
            if (password == stored_password or 
                self._hash_password(password) == stored_password):
                return True, "✅ **Autenticazione riuscita**"
            else:
                self._record_failed_attempt(username)
                return False, "❌ **Credenziali non valide**"
        else:
            return False, "❌ **Utente non trovato**"
    
    def get_user_role(self, username):
        """Restituisce il ruolo dell'utente"""
        if username in self.users:
            return self.users[username]['role']
        return 'viewer'
    
    def has_permission(self, username, permission):
        """Verifica se l'utente ha un determinato permesso"""
        if username in self.users:
            return permission in self.users[username]['permissions']
        return False
    
    def init_session(self, username):
        """Inizializza la sessione utente con timestamp"""
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = self.get_user_role(username)
        st.session_state.login_time = datetime.now()
        st.session_state.session_id = secrets.token_urlsafe(32)
    
    def check_session_validity(self):
        """Verifica se la sessione è ancora valida"""
        if not st.session_state.get('authenticated'):
            return False
        
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        # Controlla timeout sessione
        if datetime.now() - login_time > timedelta(seconds=self.session_timeout):
            self.logout()
            return False
        
        return True
    
    def logout(self):
        """Logout utente e pulizia sessione"""
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.login_time = None
        st.session_state.session_id = None

# Istanza globale del sistema di autenticazione
auth_system = SecureAuth()

def init_auth():
    """Inizializza l'autenticazione nella sessione"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def login_form():
    """Mostra il form di login sicuro"""
    st.markdown("---")
    st.markdown("## 🔐 **Accesso Sistema Sicuro**")
    
    # Mostra avviso se non ci sono utenti configurati
    if not auth_system.users:
        st.error("🚨 **ERRORE CRITICO**: Nessun utente configurato!")
        st.info("Configura il file .env con le tue credenziali reali")
        return
    
    with st.form("secure_login_form"):
        username = st.text_input("👤 **Username**", placeholder="Inserisci username")
        password = st.text_input("🔒 **Password**", type="password", placeholder="Inserisci password")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            submit_button = st.form_submit_button("🚀 **Accedi**", type="primary")
        with col2:
            if st.form_submit_button("🔙 **Reset**"):
                auth_system.logout()
                st.rerun()
        
        if submit_button:
            if username and password:
                success, message = auth_system.authenticate(username, password)
                if success:
                    auth_system.init_session(username)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("⚠️ **Inserisci username e password** per accedere.")

def require_auth():
    """Decoratore per richiedere autenticazione sicura"""
    init_auth()
    
    # Verifica validità sessione
    if not auth_system.check_session_validity():
        st.error("🔒 **Sessione scaduta o non valida**")
        st.info("Effettua nuovamente l'accesso per continuare.")
        login_form()
        st.stop()
    
    if not st.session_state.authenticated:
        st.error("🔒 **Accesso Richiesto**")
        st.info("Devi effettuare l'accesso per utilizzare questa funzionalità.")
        login_form()
        st.stop()
    
    return True

def show_user_info():
    """Mostra informazioni sull'utente corrente in modo sicuro"""
    if st.session_state.authenticated:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 **Utente Corrente**")
        st.sidebar.success(f"**Username:** {st.session_state.username}")
        st.sidebar.info(f"**Ruolo:** {st.session_state.user_role}")
        
        # Mostra tempo rimanente sessione
        if 'login_time' in st.session_state:
            elapsed = datetime.now() - st.session_state.login_time
            remaining = self.session_timeout - elapsed.seconds
            if remaining > 0:
                minutes = remaining // 60
                seconds = remaining % 60
                st.sidebar.warning(f"⏰ **Sessione:** {minutes}m {seconds}s rimanenti")
        
        # Pulsante logout
        if st.sidebar.button("🚪 **Logout**"):
            auth_system.logout()
            st.rerun()

def get_current_user():
    """Restituisce l'utente corrente in modo sicuro"""
    if st.session_state.get('authenticated') and auth_system.check_session_validity():
        return st.session_state.username
    return None

def get_current_role():
    """Restituisce il ruolo dell'utente corrente in modo sicuro"""
    if st.session_state.get('authenticated') and auth_system.check_session_validity():
        return st.session_state.user_role
    return 'viewer'
