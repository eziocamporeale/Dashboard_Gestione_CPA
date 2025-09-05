#!/usr/bin/env python3
"""
🛡️ SISTEMA PERMESSI AVANZATO - Dashboard Gestione CPA
Gestione completa di ruoli, permessi e autorizzazioni granulari
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from functools import wraps
import streamlit as st
from utils.translations import t

# Configurazione logging
logger = logging.getLogger(__name__)

class PermissionManager:
    """Gestore centrale per il sistema di permessi avanzato"""
    
    def __init__(self, db_path: str = "cpa_database.db"):
        """Inizializza il gestore permessi"""
        self.db_path = db_path
        self._cache = {}  # Cache per performance
        self._cache_timeout = 300  # 5 minuti
        
    def _get_connection(self) -> sqlite3.Connection:
        """Ottiene una connessione al database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permette accesso per nome colonna
        return conn
    
    def _clear_cache(self):
        """Pulisce la cache"""
        self._cache.clear()
    
    def get_user_id(self, username: str) -> Optional[int]:
        """Ottiene l'ID utente dal username"""
        cache_key = f"user_id_{username}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM system_users WHERE username = ? AND is_active = 1", (username,))
            result = cursor.fetchone()
            conn.close()
            
            user_id = result['id'] if result else None
            self._cache[cache_key] = user_id
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento user_id per {username}: {e}")
            return None
    
    def get_user_roles(self, user_id: int) -> List[Dict]:
        """Ottiene tutti i ruoli di un utente"""
        cache_key = f"user_roles_{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.name, r.description, r.level, r.is_system
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ?
                ORDER BY r.level DESC
            """, (user_id,))
            roles = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self._cache[cache_key] = roles
            return roles
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento ruoli per user_id {user_id}: {e}")
            return []
    
    def get_role_permissions(self, role_id: int) -> List[Dict]:
        """Ottiene tutti i permessi di un ruolo"""
        cache_key = f"role_permissions_{role_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.resource, p.action, p.is_system
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                ORDER BY p.resource, p.action
            """, (role_id,))
            permissions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self._cache[cache_key] = permissions
            return permissions
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento permessi per role_id {role_id}: {e}")
            return []
    
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Ottiene tutti i permessi di un utente (combinati da ruoli e personalizzati)"""
        cache_key = f"user_permissions_{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Permessi ereditati dai ruoli
            cursor.execute("""
                SELECT DISTINCT p.name
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN user_roles ur ON rp.role_id = ur.role_id
                WHERE ur.user_id = ?
            """, (user_id,))
            role_permissions = {row['name'] for row in cursor.fetchall()}
            
            # Permessi personalizzati (granted = 1)
            cursor.execute("""
                SELECT DISTINCT p.name
                FROM permissions p
                JOIN user_permissions up ON p.id = up.permission_id
                WHERE up.user_id = ? AND up.granted = 1
            """, (user_id,))
            personal_permissions = {row['name'] for row in cursor.fetchall()}
            
            # Permessi personalizzati negati (granted = 0)
            cursor.execute("""
                SELECT DISTINCT p.name
                FROM permissions p
                JOIN user_permissions up ON p.id = up.permission_id
                WHERE up.user_id = ? AND up.granted = 0
            """, (user_id,))
            denied_permissions = {row['name'] for row in cursor.fetchall()}
            
            conn.close()
            
            # Combina permessi: ruoli + personali - negati
            all_permissions = role_permissions | personal_permissions - denied_permissions
            self._cache[cache_key] = all_permissions
            return all_permissions
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento permessi per user_id {user_id}: {e}")
            return set()
    
    def has_permission(self, user_id: int, permission_name: str) -> bool:
        """Verifica se un utente ha un permesso specifico"""
        user_permissions = self.get_user_permissions(user_id)
        return permission_name in user_permissions
    
    def has_role(self, user_id: int, role_name: str) -> bool:
        """Verifica se un utente ha un ruolo specifico"""
        user_roles = self.get_user_roles(user_id)
        return any(role['name'] == role_name for role in user_roles)
    
    def has_resource_access(self, user_id: int, resource: str, action: str) -> bool:
        """Verifica se un utente ha accesso a una risorsa specifica"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica permessi ereditati dai ruoli
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN user_roles ur ON rp.role_id = ur.role_id
                WHERE ur.user_id = ? AND p.resource = ? AND p.action = ?
            """, (user_id, resource, action))
            role_access = cursor.fetchone()['count'] > 0
            
            # Verifica permessi personalizzati
            cursor.execute("""
                SELECT up.granted
                FROM permissions p
                JOIN user_permissions up ON p.id = up.permission_id
                WHERE up.user_id = ? AND p.resource = ? AND p.action = ?
            """, (user_id, resource, action))
            personal_result = cursor.fetchone()
            
            conn.close()
            
            if personal_result:
                return personal_result['granted'] == 1
            return role_access
            
        except Exception as e:
            logger.error(f"❌ Errore verifica accesso risorsa per user_id {user_id}: {e}")
            return False
    
    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: int) -> bool:
        """Assegna un ruolo a un utente"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica se l'assegnazione esiste già
            cursor.execute("SELECT id FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
            if cursor.fetchone():
                logger.warning(f"⚠️ Ruolo già assegnato a user_id {user_id}")
                conn.close()
                return False
            
            # Assegna il ruolo
            cursor.execute("""
                INSERT INTO user_roles (user_id, role_id, assigned_by, assigned_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, role_id, assigned_by, datetime.now()))
            
            # Log dell'azione
            cursor.execute("""
                INSERT INTO permission_audit_log (user_id, action, target_user_id, target_role_id, details)
                VALUES (?, ?, ?, ?, ?)
            """, (assigned_by, 'assign_role', user_id, role_id, f'Ruolo assegnato'))
            
            conn.commit()
            conn.close()
            
            # Pulisce cache
            self._clear_cache()
            logger.info(f"✅ Ruolo assegnato con successo a user_id {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore assegnazione ruolo: {e}")
            return False
    
    def revoke_role_from_user(self, user_id: int, role_id: int, revoked_by: int) -> bool:
        """Rimuove un ruolo da un utente"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica se l'assegnazione esiste
            cursor.execute("SELECT id FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
            if not cursor.fetchone():
                logger.warning(f"⚠️ Ruolo non assegnato a user_id {user_id}")
                conn.close()
                return False
            
            # Rimuove il ruolo
            cursor.execute("DELETE FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
            
            # Log dell'azione
            cursor.execute("""
                INSERT INTO permission_audit_log (user_id, action, target_user_id, target_role_id, details)
                VALUES (?, ?, ?, ?, ?)
            """, (revoked_by, 'revoke_role', user_id, role_id, f'Ruolo rimosso'))
            
            conn.commit()
            conn.close()
            
            # Pulisce cache
            self._clear_cache()
            logger.info(f"✅ Ruolo rimosso con successo da user_id {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore rimozione ruolo: {e}")
            return False
    
    def grant_permission_to_user(self, user_id: int, permission_id: int, granted_by: int) -> bool:
        """Concede un permesso personalizzato a un utente"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica se il permesso esiste già
            cursor.execute("SELECT id FROM user_permissions WHERE user_id = ? AND permission_id = ?", (user_id, permission_id))
            existing = cursor.fetchone()
            
            if existing:
                # Aggiorna il permesso esistente
                cursor.execute("""
                    UPDATE user_permissions 
                    SET granted = 1, granted_by = ?, granted_at = ?
                    WHERE user_id = ? AND permission_id = ?
                """, (granted_by, datetime.now(), user_id, permission_id))
            else:
                # Crea nuovo permesso
                cursor.execute("""
                    INSERT INTO user_permissions (user_id, permission_id, granted, granted_by, granted_at)
                    VALUES (?, ?, 1, ?, ?)
                """, (user_id, permission_id, granted_by, datetime.now()))
            
            # Log dell'azione
            cursor.execute("""
                INSERT INTO permission_audit_log (user_id, action, target_user_id, target_permission_id, details)
                VALUES (?, ?, ?, ?, ?)
            """, (granted_by, 'grant_permission', user_id, permission_id, f'Permesso concesso'))
            
            conn.commit()
            conn.close()
            
            # Pulisce cache
            self._clear_cache()
            logger.info(f"✅ Permesso concesso con successo a user_id {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore concessione permesso: {e}")
            return False
    
    def revoke_permission_from_user(self, user_id: int, permission_id: int, revoked_by: int) -> bool:
        """Revoca un permesso personalizzato da un utente"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica se il permesso esiste
            cursor.execute("SELECT id FROM user_permissions WHERE user_id = ? AND permission_id = ?", (user_id, permission_id))
            if not cursor.fetchone():
                logger.warning(f"⚠️ Permesso non assegnato a user_id {user_id}")
                conn.close()
                return False
            
            # Revoca il permesso
            cursor.execute("""
                UPDATE user_permissions 
                SET granted = 0, granted_by = ?, granted_at = ?
                WHERE user_id = ? AND permission_id = ?
            """, (revoked_by, datetime.now(), user_id, permission_id))
            
            # Log dell'azione
            cursor.execute("""
                INSERT INTO permission_audit_log (user_id, action, target_user_id, target_permission_id, details)
                VALUES (?, ?, ?, ?, ?)
            """, (revoked_by, 'revoke_permission', user_id, permission_id, f'Permesso revocato'))
            
            conn.commit()
            conn.close()
            
            # Pulisce cache
            self._clear_cache()
            logger.info(f"✅ Permesso revocato con successo da user_id {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore revoca permesso: {e}")
            return False
    
    def get_all_roles(self) -> List[Dict]:
        """Ottiene tutti i ruoli disponibili"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, level, is_system, created_at
                FROM roles
                ORDER BY level DESC, name
            """)
            roles = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return roles
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento ruoli: {e}")
            return []
    
    def get_all_permissions(self) -> List[Dict]:
        """Ottiene tutti i permessi disponibili"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, resource, action, is_system, created_at
                FROM permissions
                ORDER BY resource, action
            """)
            permissions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return permissions
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento permessi: {e}")
            return []
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Ottiene il log delle modifiche ai permessi"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    pal.id,
                    u1.username as user_username,
                    pal.action,
                    u2.username as target_username,
                    r.name as role_name,
                    p.name as permission_name,
                    pal.details,
                    pal.created_at
                FROM permission_audit_log pal
                LEFT JOIN system_users u1 ON pal.user_id = u1.id
                LEFT JOIN system_users u2 ON pal.target_user_id = u2.id
                LEFT JOIN roles r ON pal.target_role_id = r.id
                LEFT JOIN permissions p ON pal.target_permission_id = p.id
                ORDER BY pal.created_at DESC
                LIMIT ?
            """, (limit,))
            log_entries = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return log_entries
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento audit log: {e}")
            return []

# Istanza globale del gestore permessi
permission_manager = PermissionManager()

# ========================================
# DECORATORI PER CONTROLLO PERMESSI
# ========================================

def require_permission(permission_name: str):
    """Decoratore per richiedere un permesso specifico"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error(t("permissions.access_denied", "❌ Accesso negato. Effettua il login."))
                st.stop()
            
            username = st.session_state.get('username')
            if not username:
                st.error(t("permissions.user_not_found", "❌ Utente non trovato nella sessione."))
                st.stop()
            
            user_id = permission_manager.get_user_id(username)
            if not user_id:
                st.error(t("permissions.user_not_found_db", "❌ Utente non trovato nel database."))
                st.stop()
            
            if not permission_manager.has_permission(user_id, permission_name):
                st.error(t("permissions.insufficient_permissions", "❌ Permessi insufficienti per accedere a questa sezione."))
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name: str):
    """Decoratore per richiedere un ruolo specifico"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error(t("permissions.access_denied", "❌ Accesso negato. Effettua il login."))
                st.stop()
            
            username = st.session_state.get('username')
            if not username:
                st.error(t("permissions.user_not_found", "❌ Utente non trovato nella sessione."))
                st.stop()
            
            user_id = permission_manager.get_user_id(username)
            if not user_id:
                st.error(t("permissions.user_not_found_db", "❌ Utente non trovato nel database."))
                st.stop()
            
            if not permission_manager.has_role(user_id, role_name):
                st.error(t("permissions.insufficient_role", "❌ Ruolo insufficiente per accedere a questa sezione."))
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_resource_access(resource: str, action: str):
    """Decoratore per richiedere accesso a una risorsa specifica"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error(t("permissions.access_denied", "❌ Accesso negato. Effettua il login."))
                st.stop()
            
            username = st.session_state.get('username')
            if not username:
                st.error(t("permissions.user_not_found", "❌ Utente non trovato nella sessione."))
                st.stop()
            
            user_id = permission_manager.get_user_id(username)
            if not user_id:
                st.error(t("permissions.user_not_found_db", "❌ Utente non trovato nel database."))
                st.stop()
            
            if not permission_manager.has_resource_access(user_id, resource, action):
                st.error(t("permissions.resource_access_denied", "❌ Accesso negato alla risorsa richiesta."))
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ========================================
# FUNZIONI UTILITY PER STREAMLIT
# ========================================

def get_current_user_permissions() -> Set[str]:
    """Ottiene i permessi dell'utente corrente"""
    if not st.session_state.get('authenticated', False):
        return set()
    
    username = st.session_state.get('username')
    if not username:
        return set()
    
    user_id = permission_manager.get_user_id(username)
    if not user_id:
        return set()
    
    return permission_manager.get_user_permissions(user_id)

def get_current_user_roles() -> List[Dict]:
    """Ottiene i ruoli dell'utente corrente"""
    if not st.session_state.get('authenticated', False):
        return []
    
    username = st.session_state.get('username')
    if not username:
        return []
    
    user_id = permission_manager.get_user_id(username)
    if not user_id:
        return []
    
    return permission_manager.get_user_roles(user_id)

def can_access_resource(resource: str, action: str) -> bool:
    """Verifica se l'utente corrente può accedere a una risorsa"""
    if not st.session_state.get('authenticated', False):
        return False
    
    username = st.session_state.get('username')
    if not username:
        return False
    
    user_id = permission_manager.get_user_id(username)
    if not user_id:
        return False
    
    return permission_manager.has_resource_access(user_id, resource, action)

def has_permission(permission_name: str) -> bool:
    """Verifica se l'utente corrente ha un permesso specifico"""
    if not st.session_state.get('authenticated', False):
        return False
    
    username = st.session_state.get('username')
    if not username:
        return False
    
    user_id = permission_manager.get_user_id(username)
    if not user_id:
        return False
    
    return permission_manager.has_permission(user_id, permission_name)

def has_role(role_name: str) -> bool:
    """Verifica se l'utente corrente ha un ruolo specifico"""
    if not st.session_state.get('authenticated', False):
        return False
    
    username = st.session_state.get('username')
    if not username:
        return False
    
    user_id = permission_manager.get_user_id(username)
    if not user_id:
        return False
    
    return permission_manager.has_role(user_id, role_name)
