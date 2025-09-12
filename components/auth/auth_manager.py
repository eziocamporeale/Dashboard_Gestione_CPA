#!/usr/bin/env python3
"""
Sistema di Autenticazione per DASH_GESTIONE_LEAD
Gestisce login, logout, sessioni e permessi
Creato da Ezio Camporeale
"""

import streamlit as st
import bcrypt
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from config import AUTH_CONFIG

# Configurazione logging
logger = logging.getLogger(__name__)

class AuthManager:
    """Gestisce l'autenticazione e le sessioni degli utenti"""
    
    def __init__(self):
        """Inizializza il gestore di autenticazione"""
        self.db = DatabaseManager()
        self.session_key = AUTH_CONFIG['cookie_name']
        self.session_timeout = timedelta(days=AUTH_CONFIG['cookie_expiry_days'])
        
        # Inizializza la sessione se non esiste
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = None
    
    def hash_password(self, password: str) -> str:
        """Crea l'hash di una password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica una password contro il suo hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Errore verifica password: {e}")
            return False
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Effettua il login di un utente"""
        try:
            # Ottieni l'utente dal database
            user = self.db.get_user_by_username(username)
            
            if not user:
                logger.warning(f"Tentativo di login con username non esistente: {username}")
                return None
            
            # Verifica la password
            if not self.verify_password(password, user['password_hash']):
                logger.warning(f"Password errata per utente: {username}")
                return None
            
            # Verifica che l'utente sia attivo
            if not user['is_active']:
                logger.warning(f"Tentativo di login per utente disattivato: {username}")
                return None
            
            # Aggiorna l'ultimo login
            self.db.update_user_last_login(user['id'])
            
            # Registra l'attività
            self.db.log_activity(
                user_id=user['id'],
                action='login',
                entity_type='user',
                entity_id=user['id'],
                details=f"Login effettuato da {username}"
            )
            
            # Ottieni il nome del ruolo
            role_name = self._get_role_name(user['role_id'])
            
            # Salva la sessione
            session_data = {
                'user_id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role_id': user['role_id'],
                'role_name': role_name,
                'department_id': user.get('department_id'),
                'department_name': self._get_department_name(user.get('department_id')),
                'login_time': datetime.now().isoformat(),
                'permissions': self._get_user_permissions(user['role_id'])
            }
            
            st.session_state[self.session_key] = session_data
            
            logger.info(f"Login effettuato con successo: {username}")
            return session_data
            
        except Exception as e:
            logger.error(f"Errore durante il login: {e}")
            return None
    
    def logout(self):
        """Effettua il logout dell'utente corrente"""
        try:
            current_user = self.get_current_user()
            if current_user:
                # Registra l'attività
                self.db.log_activity(
                    user_id=current_user['user_id'],
                    action='logout',
                    entity_type='user',
                    entity_id=current_user['user_id'],
                    details=f"Logout effettuato da {current_user['username']}"
                )
                logger.info(f"Logout effettuato: {current_user['username']}")
            
            # Pulisci la sessione
            st.session_state[self.session_key] = None
            
        except Exception as e:
            logger.error(f"Errore durante il logout: {e}")
    
    def get_current_user(self) -> Optional[Dict]:
        """Ottiene l'utente corrente dalla sessione"""
        session_data = st.session_state.get(self.session_key)
        
        if not session_data:
            return None
        
        # Verifica se la sessione è scaduta
        login_time = datetime.fromisoformat(session_data['login_time'])
        if datetime.now() - login_time > self.session_timeout:
            logger.info("Sessione scaduta, logout automatico")
            self.logout()
            return None
        
        return session_data
    
    def is_authenticated(self) -> bool:
        """Verifica se l'utente è autenticato"""
        return self.get_current_user() is not None
    
    def require_auth(self):
        """Decoratore per richiedere autenticazione"""
        if not self.is_authenticated():
            st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
            st.stop()
    
    def require_role(self, required_roles: List[str]):
        """Verifica che l'utente abbia uno dei ruoli richiesti"""
        current_user = self.get_current_user()
        
        if not current_user:
            st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
            st.stop()
        
        if current_user['role_name'] not in required_roles:
            st.error("🚫 Accesso negato. Non hai i permessi necessari per questa sezione.")
            st.stop()
    
    def require_permission(self, permission: str):
        """Verifica che l'utente abbia il permesso specifico"""
        current_user = self.get_current_user()
        
        if not current_user:
            st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
            st.stop()
        
        user_permissions = current_user.get('permissions', [])
        
        if 'all' in user_permissions or permission in user_permissions:
            return True
        else:
            st.error(f"🚫 Accesso negato. Permesso richiesto: {permission}")
            st.stop()
    
    def _get_role_name(self, role_id: int) -> str:
        """Ottiene il nome del ruolo"""
        try:
            roles = self.db.get_roles()
            for role in roles:
                if role['id'] == role_id:
                    return role['name']
            return 'Unknown'
        except Exception as e:
            logger.error(f"Errore ottenimento nome ruolo: {e}")
            return 'Unknown'
    
    def _get_department_name(self, department_id: int) -> str:
        """Ottiene il nome del dipartimento"""
        if not department_id:
            return 'N/A'
        try:
            departments = self.db.get_departments()
            for dept in departments:
                if dept['id'] == department_id:
                    return dept['name']
            return 'Unknown'
        except Exception as e:
            logger.error(f"Errore ottenimento nome dipartimento: {e}")
            return 'Unknown'
    
    def _get_user_permissions(self, role_id: int) -> List[str]:
        """Ottiene i permessi per un ruolo specifico"""
        try:
            roles = self.db.get_roles()
            for role in roles:
                if role['id'] == role_id:
                    permissions = role['permissions']
                    # Se è già una lista, usala direttamente
                    if isinstance(permissions, list):
                        return permissions
                    # Se è una stringa JSON, parsala
                    elif isinstance(permissions, str):
                        return json.loads(permissions)
                    else:
                        return []
            return []
        except Exception as e:
            logger.error(f"Errore nel recupero permessi: {e}")
            return []
    
    def create_user(self, user_data: Dict) -> bool:
        """Crea un nuovo utente (solo per admin)"""
        try:
            # Verifica che l'utente corrente sia admin
            current_user = self.get_current_user()
            if not current_user or current_user['role_name'] != 'Admin':
                logger.warning("Tentativo di creazione utente da utente non admin")
                return False
            
            # Hash della password
            user_data['password_hash'] = self.hash_password(user_data['password'])
            
            # Crea l'utente
            user_id = self.db.create_user(user_data)
            
            if user_id:
                # Registra l'attività
                self.db.log_activity(
                    user_id=current_user['user_id'],
                    action='create_user',
                    entity_type='user',
                    entity_id=user_id,
                    details=f"Creato nuovo utente: {user_data['username']}"
                )
                
                logger.info(f"Nuovo utente creato: {user_data['username']} (ID: {user_id})")
                return True
            else:
                logger.error(f"Errore nella creazione dell'utente: {user_data['username']}")
                return False
            
        except Exception as e:
            logger.error(f"Errore nella creazione utente: {e}")
            return False
    
    def update_user(self, user_id: int, user_data: Dict) -> bool:
        """Aggiorna un utente esistente"""
        try:
            # Verifica che l'utente corrente sia admin o stia modificando il proprio profilo
            current_user = self.get_current_user()
            if not current_user:
                return False
            
            if current_user['role_name'] != 'Admin' and current_user['user_id'] != user_id:
                logger.warning("Tentativo di modifica utente non autorizzato")
                return False
            
            # Se viene fornita una nuova password, la hasha
            if 'password' in user_data and user_data['password']:
                user_data['password_hash'] = self.hash_password(user_data['password'])
                del user_data['password']
            
            # Aggiorna l'utente
            success = self.db.execute_update(
                """
                UPDATE users 
                SET first_name = ?, last_name = ?, email = ?, role_id = ?, department_id = ?
                WHERE id = ?
                """,
                (user_data['first_name'], user_data['last_name'], user_data['email'],
                 user_data['role_id'], user_data.get('department_id'), user_id)
            )
            
            if success:
                # Registra l'attività
                self.db.log_activity(
                    user_id=current_user['user_id'],
                    action='update_user',
                    entity_type='user',
                    entity_id=user_id,
                    details=f"Aggiornato utente: {user_data.get('username', 'N/A')}"
                )
            
            return success > 0
            
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento utente: {e}")
            return False
    
    def get_user_info(self) -> Dict:
        """Ottiene informazioni sull'utente corrente per display"""
        user = self.get_current_user()
        if not user:
            return {}
        
        return {
            'name': f"{user['first_name']} {user['last_name']}",
            'email': user['email'],
            'role': user['role_name'],
            'department': user.get('department_name', 'N/A'),
            'login_time': user['login_time']
        }

# Istanza globale del gestore di autenticazione
auth_manager = AuthManager()

def require_auth():
    """Decoratore per richiedere autenticazione"""
    auth_manager.require_auth()

def require_role(roles: List[str]):
    """Decoratore per richiedere ruoli specifici"""
    auth_manager.require_role(roles)

def require_permission(permission: str):
    """Decoratore per richiedere permessi specifici"""
    auth_manager.require_permission(permission)

def get_current_user():
    """Ottiene l'utente corrente"""
    return auth_manager.get_current_user()

def is_authenticated():
    """Verifica se l'utente è autenticato"""
    return auth_manager.is_authenticated()

# Test della classe
if __name__ == "__main__":
    print("🧪 Test AuthManager...")
    
    # Test hash password
    password = "test123"
    hashed = auth_manager.hash_password(password)
    print(f"✅ Hash password: {hashed[:20]}...")
    
    # Test verifica password
    is_valid = auth_manager.verify_password(password, hashed)
    print(f"✅ Verifica password: {is_valid}")
    
    # Test login con credenziali di default
    user = auth_manager.login("admin", "admin123")
    if user:
        print(f"✅ Login admin: {user['username']}")
    else:
        print("❌ Login admin fallito")
    
    print("✅ AuthManager testato con successo!")
