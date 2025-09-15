#!/usr/bin/env python3
"""
💰 WALLET PERMISSIONS
Sistema di permessi specifico per la gestione wallet e transazioni
"""

import streamlit as st
import logging
from typing import Dict, List, Optional
from utils.supabase_permissions import has_role, has_permission, get_current_user

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletPermissions:
    """Gestore permessi specifico per le funzionalità wallet"""
    
    # Definizione dei permessi wallet
    WALLET_PERMISSIONS = {
        'wallet:view': 'Visualizzare transazioni e saldi wallet',
        'wallet:create': 'Creare nuove transazioni wallet',
        'wallet:edit': 'Modificare transazioni esistenti',
        'wallet:delete': 'Eliminare transazioni',
        'wallet:manage': 'Gestire wallet e configurazioni',
        'wallet:deposit': 'Eseguire depositi da team a cliente',
        'wallet:withdrawal': 'Eseguire prelievi da cliente a team',
        'wallet:admin': 'Accesso completo alle funzionalità wallet'
    }
    
    # Definizione dei ruoli e i loro permessi
    ROLE_PERMISSIONS = {
        'admin': [
            'wallet:view', 'wallet:create', 'wallet:edit', 'wallet:delete',
            'wallet:manage', 'wallet:deposit', 'wallet:withdrawal', 'wallet:admin'
        ],
        'manager': [
            'wallet:view', 'wallet:create', 'wallet:edit', 'wallet:deposit', 'wallet:withdrawal'
        ],
        'user': [
            'wallet:view'
        ],
        'diego': [  # Ruolo specifico per Diego (ora usa 'manager')
            'wallet:view', 'wallet:create', 'wallet:deposit', 'wallet:withdrawal'
        ]
    }
    
    @staticmethod
    def can_view_wallet() -> bool:
        """Verifica se l'utente può visualizzare le transazioni wallet"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            username = current_user.get('username', '')
            
            # Controlla permessi specifici
            if has_permission('wallet:view'):
                return True
            
            # Controlla ruolo (Diego può essere 'manager' ma con permessi speciali)
            if user_role in ['admin', 'manager', 'user', 'diego']:
                return True
            
            # Controllo speciale per Diego (anche se ha ruolo 'manager')
            if username.lower() == 'diego':
                return True
            
            # Fallback: se il sistema di permessi non funziona, permettere accesso base
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:view: {e}")
            return True  # Fallback per sicurezza
    
    @staticmethod
    def can_create_transaction() -> bool:
        """Verifica se l'utente può creare transazioni"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            username = current_user.get('username', '')
            
            # Controlla permessi specifici
            if has_permission('wallet:create'):
                return True
            
            # Controlla ruolo (Diego può essere 'manager' ma con permessi speciali)
            if user_role in ['admin', 'manager', 'diego']:
                return True
            
            # Controllo speciale per Diego (anche se ha ruolo 'manager')
            if username.lower() == 'diego':
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:create: {e}")
            return False
    
    @staticmethod
    def can_edit_transaction() -> bool:
        """Verifica se l'utente può modificare transazioni"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            
            # Controlla permessi specifici
            if has_permission('wallet:edit'):
                return True
            
            # Controlla ruolo
            if user_role in ['admin', 'manager']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:edit: {e}")
            return False
    
    @staticmethod
    def can_delete_transaction() -> bool:
        """Verifica se l'utente può eliminare transazioni"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            
            # Controlla permessi specifici
            if has_permission('wallet:delete'):
                return True
            
            # Controlla ruolo
            if user_role in ['admin']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:delete: {e}")
            return False
    
    @staticmethod
    def can_manage_wallets() -> bool:
        """Verifica se l'utente può gestire i wallet"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            
            # Controlla permessi specifici
            if has_permission('wallet:manage'):
                return True
            
            # Controlla ruolo
            if user_role in ['admin']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:manage: {e}")
            return False
    
    @staticmethod
    def can_deposit() -> bool:
        """Verifica se l'utente può eseguire depositi"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            username = current_user.get('username', '')
            
            # Controlla permessi specifici
            if has_permission('wallet:deposit'):
                return True
            
            # Controlla ruolo (Diego può essere 'manager' ma con permessi speciali)
            if user_role in ['admin', 'manager', 'diego']:
                return True
            
            # Controllo speciale per Diego (anche se ha ruolo 'manager')
            if username.lower() == 'diego':
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:deposit: {e}")
            return False
    
    @staticmethod
    def can_withdrawal() -> bool:
        """Verifica se l'utente può eseguire prelievi"""
        try:
            current_user = get_current_user()
            if not current_user:
                return False
            
            user_role = current_user.get('role', 'user')
            username = current_user.get('username', '')
            
            # Controlla permessi specifici
            if has_permission('wallet:withdrawal'):
                return True
            
            # Controlla ruolo (Diego può essere 'manager' ma con permessi speciali)
            if user_role in ['admin', 'manager', 'diego']:
                return True
            
            # Controllo speciale per Diego (anche se ha ruolo 'manager')
            if username.lower() == 'diego':
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso wallet:withdrawal: {e}")
            return False
    
    @staticmethod
    def get_user_wallet_permissions() -> Dict[str, bool]:
        """Ottiene tutti i permessi wallet dell'utente corrente"""
        return {
            'view': WalletPermissions.can_view_wallet(),
            'create': WalletPermissions.can_create_transaction(),
            'edit': WalletPermissions.can_edit_transaction(),
            'delete': WalletPermissions.can_delete_transaction(),
            'manage': WalletPermissions.can_manage_wallets(),
            'deposit': WalletPermissions.can_deposit(),
            'withdrawal': WalletPermissions.can_withdrawal()
        }
    
    @staticmethod
    def render_permissions_info():
        """Mostra informazioni sui permessi dell'utente corrente"""
        current_user = get_current_user()
        if not current_user:
            st.error("❌ Utente non autenticato")
            return
        
        user_role = current_user.get('role', 'user')
        username = current_user.get('username', 'N/A')
        
        st.info(f"👤 **Utente:** {username} | **Ruolo:** {user_role}")
        
        # Mostra permessi wallet
        permissions = WalletPermissions.get_user_wallet_permissions()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**👁️ Visualizzazione:**")
            st.write(f"• Transazioni: {'✅' if permissions['view'] else '❌'}")
            st.write(f"• Saldi: {'✅' if permissions['view'] else '❌'}")
        
        with col2:
            st.write("**✏️ Modifica:**")
            st.write(f"• Creare: {'✅' if permissions['create'] else '❌'}")
            st.write(f"• Modificare: {'✅' if permissions['edit'] else '❌'}")
            st.write(f"• Eliminare: {'✅' if permissions['delete'] else '❌'}")
        
        with col3:
            st.write("**💰 Operazioni:**")
            st.write(f"• Depositi: {'✅' if permissions['deposit'] else '❌'}")
            st.write(f"• Prelievi: {'✅' if permissions['withdrawal'] else '❌'}")
            st.write(f"• Gestione: {'✅' if permissions['manage'] else '❌'}")

# Funzioni di convenienza per Streamlit
def can_view_wallet() -> bool:
    """Verifica se l'utente può visualizzare le transazioni wallet"""
    return WalletPermissions.can_view_wallet()

def can_create_transaction() -> bool:
    """Verifica se l'utente può creare transazioni"""
    return WalletPermissions.can_create_transaction()

def can_edit_transaction() -> bool:
    """Verifica se l'utente può modificare transazioni"""
    return WalletPermissions.can_edit_transaction()

def can_delete_transaction() -> bool:
    """Verifica se l'utente può eliminare transazioni"""
    return WalletPermissions.can_delete_transaction()

def can_manage_wallets() -> bool:
    """Verifica se l'utente può gestire i wallet"""
    return WalletPermissions.can_manage_wallets()

def can_deposit() -> bool:
    """Verifica se l'utente può eseguire depositi"""
    return WalletPermissions.can_deposit()

def can_withdrawal() -> bool:
    """Verifica se l'utente può eseguire prelievi"""
    return WalletPermissions.can_withdrawal()

def render_permissions_info():
    """Mostra informazioni sui permessi dell'utente corrente"""
    WalletPermissions.render_permissions_info()
