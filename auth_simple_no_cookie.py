#!/usr/bin/env python3
"""
🔐 SISTEMA DI AUTENTICAZIONE SEMPLICE SENZA COOKIE - Dashboard Gestione CPA
Versione completamente personalizzata senza dipendenze esterne
INTEGRATO CON SUPABASE
"""

import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from utils.translations import t

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleAuthSystem:
    """Sistema di autenticazione semplice senza cookie - INTEGRATO CON SUPABASE"""
    
    def __init__(self):
        """Inizializza il sistema di autenticazione"""
        self.users = self.create_default_users()
        self.session_timeout = 3600  # 1 ora
        self.supabase_manager = None
        self.load_users_from_supabase()
        
    def load_users_from_supabase(self):
        """Carica utenti da Supabase con nuova struttura ruoli"""
        try:
            from supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
            
            if self.supabase_manager.is_configured:
                # Recupera utenti da Supabase SENZA join sui ruoli per evitare RLS recursion
                response = self.supabase_manager.supabase.table('users').select(
                    'id, username, password_hash, email, full_name, first_name, last_name, '
                    'is_active, role_id, role'
                ).execute()
                
                if response.data:
                    for user in response.data:
                        username = user.get('username')
                        if username:
                            # Usa il ruolo diretto dalla tabella users (senza join)
                            role_name = user.get('role', 'User')
                            
                            # Aggiungi utente da Supabase al dizionario locale
                            self.users[username] = {
                                'id': user.get('id'),  # IMPORTANTE: Salva l'ID
                                'username': username,
                                'password_hash': user.get('password_hash', ''),
                                'email': user.get('email', ''),
                                'name': user.get('full_name', username),
                                'first_name': user.get('first_name', ''),
                                'last_name': user.get('last_name', ''),
                                'role': role_name,  # Nome del ruolo per compatibilità
                                'role_id': user.get('role_id'),  # ID del ruolo
                                'role_info': {},  # Vuoto per ora, evita problemi RLS
                                'is_active': user.get('is_active', True),
                                'from_supabase': True
                            }
                    logger.info(t("auth.system.users_loaded", "✅ Caricati {count} utenti da Supabase con struttura ruoli").format(count=len(response.data)))
                else:
                    logger.warning(t("auth.system.no_users_supabase", "⚠️ Nessun utente trovato in Supabase"))
            else:
                logger.warning(t("auth.system.supabase_not_configured", "⚠️ Supabase non configurato, uso solo utenti locali"))
                
        except Exception as e:
            logger.error(t("auth.system.supabase_error", "❌ Errore caricamento utenti da Supabase: {error}").format(error=e))
            logger.info(t("auth.system.continue_local", "ℹ️ Continuo con utenti locali"))
    
    def create_default_users(self) -> Dict:
        """Crea utenti di default"""
        return {
            'admin': {
                'username': 'admin',
                'password_hash': 'admin',  # Password semplice per test
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
            
            # Se è un hash semplice (per utenti locali)
            if stored_hash == password:
                return True
                
            # Se è un hash SHA256 con salt
            if '$' in stored_hash:
                salt, hash_value = stored_hash.split('$')
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return password_hash == hash_value
                
            return False
        except Exception as e:
            logger.error(f"❌ Errore verifica password: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Autentica un utente"""
        try:
            if username in self.users:
                user = self.users[username]
                
                # Verifica se l'utente è attivo
                if not user.get('is_active', True):
                    logger.warning(f"❌ Utente {username} non attivo")
                    return False
                
                # Verifica password
                if self.verify_password(password, user['password_hash']):
                    logger.info(f"✅ Autenticazione riuscita per {username}")
                    return True
                else:
                    logger.warning(f"❌ Password errata per {username}")
                    return False
            else:
                logger.warning(f"❌ Utente {username} non trovato")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore autenticazione: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Ottiene informazioni su un utente"""
        return self.users.get(username)

# Istanza globale del sistema di autenticazione
auth_system = SimpleAuthSystem()

# Funzioni di interfaccia per compatibilità
def init_auth():
    """Inizializza il sistema di autenticazione"""
    global auth_system
    auth_system = SimpleAuthSystem()
    logger.info("✅ Sistema di autenticazione semplice inizializzato")

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
                st.session_state.roles = user_info['role']
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

def logout_user():
    """Funzione dedicata per il logout completo"""
    try:
        username = st.session_state.get('username', 'Unknown')
        logger.info(f"🔧 Logout completo richiesto per utente: {username}")
        
        # Lista di tutte le chiavi da rimuovere
        keys_to_remove = [
            'authenticated', 'username', 'name', 'user_info', 
            'authentication_status', 'email', 'logout',
            'FormSubmitter:Login-Login', 'roles'
        ]
        
        # Pulisci tutte le chiavi di sessione
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
                logger.info(f"🔧 Rimossa chiave: {key}")
        
        # Pulisci anche altre chiavi che potrebbero essere presenti
        try:
            for key in list(st.session_state.keys()):
                if key.startswith('FormSubmitter:') or key in ['editing_client', 'supabase_available', 'show_charts']:
                    del st.session_state[key]
                    logger.info(f"🔧 Rimossa chiave aggiuntiva: {key}")
        except Exception as e:
            logger.warning(f"⚠️ Impossibile iterare session_state.keys(): {e}")
        
        logger.info(f"✅ Logout completo completato per {username}")
        st.success("✅ Logout completato!")
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
    """Funzione vuota - informazioni utente e logout gestiti da user_navigation.py"""
    # Tutte le informazioni utente e il logout sono ora gestiti da user_navigation.py
    pass

def get_current_role():
    """Ottiene il ruolo corrente dell'utente"""
    # Prima controlla se è autenticato
    if not st.session_state.get('authenticated', False):
        return 'user'
    
    # Ottieni le informazioni dell'utente corrente
    user_info = st.session_state.get('user_info', {})
    current_role = user_info.get('role', 'user')
    
    # Log per debug
    logger.info(f"🔍 HOOK AUTH: get_current_role() - user_info caricato (senza dati sensibili)")
    logger.info(f"🔍 HOOK AUTH: get_current_role() - current_role: {current_role}")
    
    return current_role

def has_permission(required_role: str) -> bool:
    """Verifica se l'utente ha i permessi necessari usando la nuova struttura ruoli"""
    current_role = get_current_role()
    
    # Log per debug
    logger.info(f"🔍 HOOK AUTH: has_permission() - current_role: {current_role}, required_role: {required_role}")
    
    # Gerarchia dei ruoli (aggiornata con i nomi corretti dal database)
    role_hierarchy = {
        'user': 1,
        'manager': 2,
        'admin': 3
    }
    
    current_level = role_hierarchy.get(current_role.lower(), 0)
    required_level = role_hierarchy.get(required_role.lower(), 0)
    
    has_perm = current_level >= required_level
    logger.info(f"🔍 HOOK AUTH: has_permission() - current_level: {current_level}, required_level: {required_level}, has_perm: {has_perm}")
    
    return has_perm

def get_user_role_info():
    """Ottiene informazioni complete del ruolo dell'utente corrente"""
    user_info = st.session_state.get('user_info', {})
    return user_info.get('role_info', {})

def has_role_permission(permission: str) -> bool:
    """Verifica se l'utente ha un permesso specifico dal suo ruolo"""
    role_info = get_user_role_info()
    permissions = role_info.get('permissions', [])
    
    # Se ha permesso "all", può fare tutto
    if 'all' in permissions:
        return True
    
    # Verifica il permesso specifico
    return permission in permissions

# Funzione duplicata rimossa - utilizziamo solo la prima login_form()

def init_auth():
    """Inizializza il sistema di autenticazione"""
    try:
        # Crea un'istanza del sistema di autenticazione
        auth_system = SimpleAuthSystem()
        logger.info("✅ Sistema di autenticazione semplice inizializzato")
        return True
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione sistema di autenticazione: {e}")
        return False
