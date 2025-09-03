#!/usr/bin/env python3
"""
🛡️ SISTEMA PERMESSI AVANZATO SUPABASE - Dashboard Gestione CPA
Gestione completa di ruoli, permessi e autorizzazioni granulari per Supabase
"""

import logging
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from functools import wraps
import streamlit as st
from utils.translations import t

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Istanza globale del gestore permessi

class SupabasePermissionManager:
    """Gestore permessi per Supabase - Adattato alla struttura esistente"""
    
    def __init__(self):
        """Inizializza il gestore permessi"""
        self._supabase = None
        self._cache = {}
        self._cache_ttl = 300  # 5 minuti
        
    def _get_supabase(self):
        """Ottiene l'istanza Supabase"""
        if self._supabase is None:
            try:
                from supabase_manager import SupabaseManager
                supabase_manager = SupabaseManager()
                self._supabase = supabase_manager.supabase
            except Exception as e:
                logger.error(f"❌ Errore inizializzazione Supabase: {e}")
                return None
        return self._supabase
    
    def _clear_cache(self):
        """Pulisce la cache"""
        self._cache = {}
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Ottiene l'ID utente dal username"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return None
            
            # Usa la tabella users esistente
            result = supabase.table('users').select('id').eq('username', username).eq('is_active', True).execute()
            
            if result.data:
                return result.data[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento user_id per {username}: {e}")
            return None
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Ottiene i ruoli di un utente dalla tabella users"""
        try:
            logger.info(f"🔍 DEBUG get_user_roles: user_id={user_id}")
            
            supabase = self._get_supabase()
            if not supabase:
                logger.error("❌ DEBUG get_user_roles: Supabase non disponibile")
                return []
            
            # Ottieni il ruolo dalla tabella users
            result = supabase.table('users').select('role').eq('id', user_id).execute()
            logger.info(f"🔍 DEBUG get_user_roles: Risultato query={result.data}")
            
            if result.data and result.data[0]['role']:
                roles = [result.data[0]['role']]
                logger.info(f"🔍 DEBUG get_user_roles: Ruoli trovati={roles}")
                return roles
            
            logger.warning(f"⚠️ DEBUG get_user_roles: Nessun ruolo trovato per user_id={user_id}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento ruoli per user_id {user_id}: {e}")
            return []
    
    def get_role_permissions(self, role_name: str) -> List[str]:
        """Ottiene i permessi di un ruolo dalla tabella user_roles"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return []
            
            # Ottieni i permessi dalla tabella user_roles
            result = supabase.table('user_roles').select('permissions').eq('role_name', role_name).eq('is_active', True).execute()
            
            if result.data and result.data[0]['permissions']:
                return result.data[0]['permissions']
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento permessi per ruolo {role_name}: {e}")
            return []
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Ottiene i permessi di un utente (combinati da ruolo e personalizzati)"""
        try:
            # Ottieni il ruolo dell'utente
            user_roles = self.get_user_roles(user_id)
            if not user_roles:
                return []
            
            # Ottieni i permessi del ruolo
            all_permissions = []
            for role in user_roles:
                role_permissions = self.get_role_permissions(role)
                all_permissions.extend(role_permissions)
            
            # Rimuovi duplicati
            return list(set(all_permissions))
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento permessi per user_id {user_id}: {e}")
            return []
    
    def has_permission(self, user_id: str, permission_name: str) -> bool:
        """Verifica se un utente ha un permesso specifico"""
        try:
            user_permissions = self.get_user_permissions(user_id)
            return permission_name in user_permissions
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso {permission_name} per user_id {user_id}: {e}")
            return False
    
    def has_role(self, user_id: str, role_name: str) -> bool:
        """Verifica se un utente ha un ruolo specifico"""
        try:
            logger.info(f"🔍 DEBUG SupabasePermissionManager.has_role: user_id={user_id}, role_name={role_name}")
            
            user_roles = self.get_user_roles(user_id)
            logger.info(f"🔍 DEBUG SupabasePermissionManager.has_role: user_roles={user_roles}")
            
            result = role_name in user_roles
            logger.info(f"🔍 DEBUG SupabasePermissionManager.has_role: Risultato={result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Errore verifica ruolo {role_name} per user_id {user_id}: {e}")
            return False
    
    def has_resource_access(self, user_id: str, resource: str, action: str) -> bool:
        """Verifica se un utente ha accesso a una risorsa specifica"""
        try:
            # Crea il nome del permesso nel formato esistente
            permission_name = f"{resource}:{action}"
            return self.has_permission(user_id, permission_name)
            
        except Exception as e:
            logger.error(f"❌ Errore verifica accesso risorsa {resource}:{action} per user_id {user_id}: {e}")
            return False
    
    def assign_role_to_user(self, user_id: str, role_name: str, assigned_by: str = None) -> bool:
        """Assegna un ruolo a un utente"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return False
            
            # Aggiorna il ruolo nella tabella users
            result = supabase.table('users').update({
                'role': role_name,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            
            # Log dell'azione
            self._log_action(assigned_by or user_id, 'assign_role', {
                'target_user_id': user_id,
                'role': role_name
            })
            
            self._clear_cache()
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore assegnazione ruolo {role_name} a user_id {user_id}: {e}")
            return False
    
    def revoke_role_from_user(self, user_id: str, role_name: str, revoked_by: str = None) -> bool:
        """Rimuove un ruolo da un utente"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return False
            
            # Rimuovi il ruolo dalla tabella users
            result = supabase.table('users').update({
                'role': None,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).eq('role', role_name).execute()
            
            # Log dell'azione
            self._log_action(revoked_by or user_id, 'revoke_role', {
                'target_user_id': user_id,
                'role': role_name
            })
            
            self._clear_cache()
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore rimozione ruolo {role_name} da user_id {user_id}: {e}")
            return False
    
    def grant_permission_to_user(self, user_id: str, permission_name: str, granted_by: str = None) -> bool:
        """Concede un permesso a un utente (aggiunge alla tabella user_permissions)"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return False
            
            # Inserisci nella tabella user_permissions
            data = {
                'permission_name': permission_name,
                'description': f'Permesso {permission_name}',
                'resource': permission_name.split(':')[0] if ':' in permission_name else 'unknown',
                'action': permission_name.split(':')[1] if ':' in permission_name else 'unknown',
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }
            
            result = supabase.table('user_permissions').insert(data).execute()
            
            # Log dell'azione
            self._log_action(granted_by or user_id, 'grant_permission', {
                'target_user_id': user_id,
                'permission': permission_name
            })
            
            self._clear_cache()
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore concessione permesso {permission_name} a user_id {user_id}: {e}")
            return False
    
    def revoke_permission_from_user(self, user_id: str, permission_name: str, revoked_by: str = None) -> bool:
        """Rimuove un permesso da un utente"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return False
            
            # Rimuovi dalla tabella user_permissions
            result = supabase.table('user_permissions').delete().eq('permission_name', permission_name).execute()
            
            # Log dell'azione
            self._log_action(revoked_by or user_id, 'revoke_permission', {
                'target_user_id': user_id,
                'permission': permission_name
            })
            
            self._clear_cache()
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore rimozione permesso {permission_name} da user_id {user_id}: {e}")
            return False
    
    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i ruoli disponibili"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return []
            
            # Ottieni dalla tabella user_roles
            result = supabase.table('user_roles').select('*').eq('is_active', True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento ruoli: {e}")
            return []
    
    def get_all_permissions(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i permessi disponibili"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return []
            
            # Ottieni dalla tabella user_permissions
            result = supabase.table('user_permissions').select('*').eq('is_active', True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento permessi: {e}")
            return []
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Ottiene il log delle azioni"""
        try:
            supabase = self._get_supabase()
            if not supabase:
                return []
            
            # Per ora usa la tabella user_permissions come log
            result = supabase.table('user_permissions').select('*').order('created_at', desc=True).limit(limit).execute()
            
            # Converti in formato audit log
            audit_log = []
            for row in result.data:
                audit_log.append({
                    'id': row.get('id', str(uuid.uuid4())),
                    'user_id': 'system',
                    'action': 'grant_permission',
                    'details': {
                        'permission': row.get('permission_name'),
                        'resource': row.get('resource'),
                        'action': row.get('action')
                    },
                    'created_at': row.get('created_at', datetime.now().isoformat())
                })
            
            return audit_log
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento audit log: {e}")
            return []
    
    def _log_action(self, user_id: str, action: str, details: Dict[str, Any]):
        """Logga un'azione nel sistema"""
        try:
            # Per ora logghiamo solo localmente
            logger.info(f"🔍 AUDIT: User {user_id} performed {action}: {details}")
        except Exception as e:
            logger.error(f"❌ Errore logging azione: {e}")

# Decoratori per Streamlit
def require_permission(permission_name: str):
    """Decoratore per richiedere un permesso specifico"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Ottieni l'utente corrente dalla sessione
            if 'user_info' not in st.session_state:
                st.error("❌ Accesso negato. Effettua il login.")
                st.stop()
            
            user_info = st.session_state.user_info
            user_id = user_info.get('id')
            
            if not user_id:
                st.error("❌ Utente non trovato nella sessione.")
                st.stop()
            
            # Verifica il permesso
            if not supabase_permission_manager.has_permission(user_id, permission_name):
                st.error("❌ Permessi insufficienti per accedere a questa sezione.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name: str):
    """Decoratore per richiedere un ruolo specifico"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Ottieni l'utente corrente dalla sessione
            if 'user_info' not in st.session_state:
                st.error("❌ Accesso negato. Effettua il login.")
                st.stop()
            
            user_info = st.session_state.user_info
            user_id = user_info.get('id')
            
            if not user_id:
                st.error("❌ Utente non trovato nella sessione.")
                st.stop()
            
            # Verifica il ruolo
            if not supabase_permission_manager.has_role(user_id, role_name):
                st.error("❌ Ruolo insufficiente per accedere a questa sezione.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_resource_access(resource: str, action: str):
    """Decoratore per richiedere accesso a una risorsa specifica"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Ottieni l'utente corrente dalla sessione
            if 'user_info' not in st.session_state:
                st.error("❌ Accesso negato. Effettua il login.")
                st.stop()
            
            user_info = st.session_state.user_info
            user_id = user_info.get('id')
            
            if not user_id:
                st.error("❌ Utente non trovato nella sessione.")
                st.stop()
            
            # Verifica l'accesso alla risorsa
            if not supabase_permission_manager.has_resource_access(user_id, resource, action):
                st.error("❌ Accesso negato alla risorsa richiesta.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Funzioni utility per Streamlit
def get_current_user_permissions() -> List[str]:
    """Ottiene i permessi dell'utente corrente"""
    if 'user_info' not in st.session_state:
        return []
    
    user_info = st.session_state.user_info
    user_id = user_info.get('id')
    
    if not user_id:
        return []
    
    return supabase_permission_manager.get_user_permissions(user_id)

def get_current_user_roles() -> List[str]:
    """Ottiene i ruoli dell'utente corrente"""
    if 'user_info' not in st.session_state:
        return []
    
    user_info = st.session_state.user_info
    user_id = user_info.get('id')
    
    if not user_id:
        return []
    
    return supabase_permission_manager.get_user_roles(user_id)

def can_access_resource(resource: str, action: str) -> bool:
    """Verifica se l'utente corrente può accedere a una risorsa"""
    if 'user_info' not in st.session_state:
        return False
    
    user_info = st.session_state.user_info
    user_id = user_info.get('id')
    
    if not user_id:
        return False
    
    return supabase_permission_manager.has_resource_access(user_id, resource, action)

def has_permission(permission_name: str) -> bool:
    """Verifica se l'utente corrente ha un permesso specifico"""
    if 'user_info' not in st.session_state:
        return False
    
    user_info = st.session_state.user_info
    user_id = user_info.get('id')
    
    if not user_id:
        return False
    
    return supabase_permission_manager.has_permission(user_id, permission_name)

def has_role(role_name: str) -> bool:
    """Verifica se l'utente corrente ha un ruolo specifico"""
    logger.info(f"🔍 DEBUG has_role: Verificando ruolo '{role_name}'")
    
    if 'user_info' not in st.session_state:
        logger.error("❌ DEBUG has_role: user_info non presente nella sessione")
        return False
    
    user_info = st.session_state.user_info
    user_id = user_info.get('id')
    username = user_info.get('username')
    role = user_info.get('role')
    
    logger.info(f"🔍 DEBUG has_role: user_id={user_id}, username={username}, role={role}")
    
    if not user_id:
        logger.error("❌ DEBUG has_role: user_id non presente")
        return False
    
    result = supabase_permission_manager.has_role(user_id, role_name)
    logger.info(f"🔍 DEBUG has_role: Risultato verifica ruolo '{role_name}' = {result}")
    
    return result
# Istanza globale del gestore permessi
supabase_permission_manager = SupabasePermissionManager()
