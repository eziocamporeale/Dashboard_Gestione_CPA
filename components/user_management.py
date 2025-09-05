#!/usr/bin/env python3
"""
👥 COMPONENTE GESTIONE UTENTI - Dashboard CPA
Sistema completo per la gestione di utenti, ruoli e permessi
SOLO ADMIN PUÒ ACCEDERE A QUESTA SEZIONE
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import logging

# Configura il logger
logger = logging.getLogger(__name__)

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

class UserManagement:
    """Classe per la gestione completa degli utenti - SOLO ADMIN"""
    
    def __init__(self):
        """Inizializza il sistema di gestione utenti"""
        self.supabase_manager = SupabaseManager()
        # Verifica ruolo corrente dall'user_info
        user_info = st.session_state.get('user_info', {})
        self.current_user_role = user_info.get('role', 'user')
        logger.info(f"🔍 USER_MANAGEMENT: Inizializzazione per ruolo {self.current_user_role}")
        logger.info(f"🔍 USER_MANAGEMENT: user_info caricato (senza dati sensibili)")
        
    def check_admin_permissions(self):
        """Verifica che l'utente abbia i permessi di amministratore"""
        if self.current_user_role != 'admin':
            st.error("❌ **ACCESSO NEGATO** - Solo gli amministratori possono gestire gli utenti.")
            st.info("🔒 Questa sezione è riservata agli utenti con ruolo **admin**")
            logger.warning(f"🔍 USER_MANAGEMENT: Accesso negato per ruolo {self.current_user_role}")
            return False
        
        logger.info(f"🔍 USER_MANAGEMENT: Accesso consentito per ruolo {self.current_user_role}")
        return True
    
    def get_all_users(self):
        """Recupera tutti gli utenti dal database con informazioni sui ruoli"""
        try:
            logger.info(f"🔍 GET_ALL_USERS: Recupero utenti da Supabase...")
            # Query con join sui ruoli per ottenere informazioni complete
            response = self.supabase_manager.supabase.table('users').select(
                'id, username, email, full_name, first_name, last_name, '
                'is_active, role_id, created_at, updated_at, '
                'roles(name, description, permissions)'
            ).execute()
            
            logger.info(f"🔍 GET_ALL_USERS: Risposta Supabase: {len(response.data) if response.data else 0} utenti")
            
            if response.data:
                df = pd.DataFrame(response.data)
                logger.info(f"🔍 GET_ALL_USERS: DataFrame creato con {len(df)} righe")
                logger.info(f"🔍 GET_ALL_USERS: Colonne disponibili: {list(df.columns)}")
                return df
            else:
                logger.warning(f"🔍 GET_ALL_USERS: Nessun utente trovato")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"🔍 GET_ALL_USERS: Errore nel recupero utenti: {e}")
            st.error(f"❌ Errore nel recupero utenti: {e}")
            return pd.DataFrame()
    
    def get_all_roles(self):
        """Recupera tutti i ruoli disponibili"""
        try:
            response = self.supabase_manager.supabase.table('roles').select('*').execute()
            if response.data:
                return response.data
            return []
        except Exception as e:
            st.error(f"❌ Errore nel recupero ruoli: {e}")
            return []
    
    def get_roles(self):
        """Recupera tutti i ruoli dal database (alias per get_all_roles)"""
        return self.get_all_roles()
    
    def render_user_management(self):
        """Rende l'interfaccia principale di gestione utenti - SOLO ADMIN"""
        
        # CONTROLLO PRINCIPALE: Solo Admin può accedere
        if not self.check_admin_permissions():
            return
        
        # Controlla se mostrare il form di modifica
        if st.session_state.get('edit_user_id'):
            self.render_edit_form(st.session_state['edit_user_id'])
            return
        
        st.header("👥 Gestione Utenti")
        st.markdown("**🔒 Sezione riservata agli amministratori**")
        st.markdown("---")
        
        # Mostra lista utenti
        users_df = self.get_all_users()
        
        if users_df.empty:
            st.info("📭 Nessun utente trovato")
            return
        
        # Mostra tabella utenti con azioni
        st.subheader("📊 Lista Utenti")
        
        # Tabella interattiva con azioni
        for index, user in users_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{user['username']}**")
                
                with col2:
                    st.write(user['email'])
                
                with col3:
                    st.write(user['full_name'] or 'N/A')
                
                with col4:
                    status = "🟢 Attivo" if user['is_active'] else "🔴 Inattivo"
                    st.write(status)
                
                with col5:
                    if st.button("✏️ Modifica", key=f"edit_{user['id']}"):
                        st.session_state['edit_user_id'] = user['id']
                        st.rerun()
                
                with col6:
                    if st.button("🗑️ Elimina", key=f"delete_{user['id']}"):
                        self.delete_user(user['id'])
                
                st.markdown("---")
        
        # Statistiche rapide
        st.subheader("📈 Statistiche")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_users = len(users_df)
            st.metric("👥 Totale Utenti", total_users)
        
        with col2:
            active_users = len(users_df[users_df['is_active'] == True])
            st.metric("🟢 Utenti Attivi", active_users)
        
        with col3:
            inactive_users = len(users_df[users_df['is_active'] == False])
            st.metric("🔴 Utenti Inattivi", inactive_users)
    
    def delete_user(self, user_id: str):
        """Elimina un utente con conferma"""
        
        # Verifica se è già stata richiesta la conferma
        if st.session_state.get('confirm_delete_user'):
            # Esegui l'eliminazione
            success, message = self.supabase_manager.delete_user(user_id)
            
            if success:
                st.success(message)
                # Log dell'azione
                logger.info(f"🔍 USER_MANAGEMENT: Utente {user_id} eliminato da admin")
            else:
                st.error(message)
            
            # Reset dello stato di conferma
            st.session_state['confirm_delete_user'] = False
            st.rerun()
        else:
            # Richiedi conferma
            st.session_state['confirm_delete_user'] = True
            st.warning("⚠️ **Conferma eliminazione utente**")
            st.info("🔒 Questa azione non può essere annullata. L'utente verrà eliminato definitivamente dal sistema.")
    
    def edit_user(self, user_id: str):
        """Modifica un utente"""
        
        # Verifica se è già stata richiesta la modifica
        if st.session_state.get('edit_user_id') == user_id:
            # Mostra form di modifica
            self.render_edit_form(user_id)
        else:
            # Imposta l'utente da modificare
            st.session_state['edit_user_id'] = user_id
            st.rerun()
    
    def render_edit_form(self, user_id: str):
        """Renderizza il form di modifica utente"""
        
        # Recupera i dati dell'utente
        users_df = self.get_all_users()
        user_data = users_df[users_df['id'] == user_id].iloc[0]
        
        st.markdown("### ✏️ Modifica Utente")
        
        # Pulsante per tornare alla lista
        if st.button("← Torna alla Lista"):
            st.session_state['edit_user_id'] = None
            st.rerun()
        
        # Form di modifica
        with st.form("edit_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input(
                    "Username",
                    value=user_data['username'],
                    help="Username dell'utente"
                )
                
                email = st.text_input(
                    "Email",
                    value=user_data['email'],
                    help="Email dell'utente"
                )
            
            with col2:
                full_name = st.text_input(
                    "Nome Completo",
                    value=user_data['full_name'] or '',
                    help="Nome completo dell'utente"
                )
                
                is_active = st.selectbox(
                    "Stato",
                    options=[True, False],
                    index=0 if user_data['is_active'] else 1,
                    format_func=lambda x: "🟢 Attivo" if x else "🔴 Inattivo"
                )
            
            # Ruolo
            try:
                roles = self.get_roles()
                if roles:
                    role_options = [role['name'] for role in roles]
                    current_role = user_data.get('role', 'User')
                    
                    try:
                        role_index = role_options.index(current_role)
                    except ValueError:
                        role_index = 0
                    
                    selected_role = st.selectbox(
                        "Ruolo",
                        options=role_options,
                        index=role_index,
                        help="Ruolo dell'utente"
                    )
                else:
                    selected_role = user_data.get('role', 'User')
                    st.selectbox(
                        "Ruolo",
                        options=[selected_role],
                        index=0,
                        help="Ruolo dell'utente (solo ruolo corrente disponibile)"
                    )
            except Exception as e:
                logger.error(f"❌ Errore nel caricamento ruoli: {e}")
                selected_role = user_data.get('role', 'User')
                st.selectbox(
                    "Ruolo",
                    options=[selected_role],
                    index=0,
                    help="Ruolo dell'utente (errore nel caricamento ruoli)"
                )
            
            # Pulsanti dentro il form
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Salva Modifiche", use_container_width=True):
                    # Prepara i dati per l'aggiornamento
                    update_data = {
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'is_active': is_active,
                        'role': selected_role
                    }
                    
                    # Aggiorna l'utente
                    success, message = self.supabase_manager.update_user(user_id, update_data)
                    
                    if success:
                        st.success(message)
                        logger.info(f"🔍 USER_MANAGEMENT: Utente {user_id} modificato da admin")
                        # Reset dello stato e torna alla lista
                        st.session_state['edit_user_id'] = None
                        st.rerun()
                    else:
                        st.error(message)
            
            with col2:
                if st.form_submit_button("❌ Annulla", use_container_width=True):
                    st.session_state['edit_user_id'] = None
                    st.rerun()

def render_user_management():
    """Funzione principale per rendere il componente di gestione utenti - SOLO ADMIN"""
    user_mgmt = UserManagement()
    user_mgmt.render_user_management()
