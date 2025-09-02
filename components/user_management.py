#!/usr/bin/env python3
"""
👥 COMPONENTE GESTIONE UTENTI - Dashboard CPA
Sistema completo per la gestione di utenti, ruoli e permessi
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
    """Classe per la gestione completa degli utenti"""
    
    def __init__(self):
        """Inizializza il sistema di gestione utenti"""
        self.supabase_manager = SupabaseManager()
        # HOOK: traccia quando viene verificato il ruolo per user_management
        logger.info(f"🔍 HOOK USER_MANAGEMENT: Inizializzazione componente")
        logger.info(f"🔍 HOOK USER_MANAGEMENT: user_info.role = {st.session_state.get('user_info', {}).get('role')}")
        logger.info(f"🔍 HOOK USER_MANAGEMENT: session_state.roles = {st.session_state.get('roles')}")
        
        # Usa il ruolo dal session_state invece che da user_info
        self.current_user_role = st.session_state.get('roles', 'user')
        logger.info(f"🔍 HOOK USER_MANAGEMENT: Ruolo finale impostato = {self.current_user_role}")
        
    def check_admin_permissions(self):
        """Verifica che l'utente abbia i permessi di amministratore"""
        # HOOK: traccia quando viene verificato il permesso admin
        logger.info(f"🔍 HOOK USER_MANAGEMENT: Verifica permesso admin")
        logger.info(f"🔍 HOOK USER_MANAGEMENT: current_user_role = {self.current_user_role}")
        logger.info(f"🔍 HOOK USER_MANAGEMENT: session_state.roles = {st.session_state.get('roles')}")
        
        if self.current_user_role != 'admin':
            st.error("❌ Accesso negato. Solo gli amministratori possono gestire gli utenti.")
            logger.warning(f"🔍 HOOK USER_MANAGEMENT: Accesso negato per ruolo {self.current_user_role}")
            return False
        
        logger.info(f"🔍 HOOK USER_MANAGEMENT: Accesso consentito per ruolo {self.current_user_role}")
        return True
    
    def get_all_users(self):
        """Recupera tutti gli utenti dal database"""
        try:
            logger.info(f"🔍 GET_ALL_USERS: Recupero utenti da Supabase...")
            response = self.supabase_manager.supabase.table('users').select('*').execute()
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
    
    def get_user_roles(self):
        """Recupera tutti i ruoli disponibili"""
        try:
            response = self.supabase_manager.supabase.table('user_roles').select('*').execute()
            if response.data:
                return {role['role_name']: role['description'] for role in response.data}
            return {}
        except Exception as e:
            st.error(f"❌ Errore nel recupero ruoli: {e}")
            return {}
    
    def create_user(self, username, email, password, full_name, role):
        """Crea un nuovo utente"""
        try:
            # Hash della password (semplificato per ora)
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user_data = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'role': role,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase_manager.supabase.table('users').insert(user_data).execute()
            
            if response.data:
                # Crea profilo utente
                user_id = response.data[0]['id']
                profile_data = {
                    'user_id': user_id,
                    'timezone': 'Europe/Rome',
                    'language': 'it',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.supabase_manager.supabase.table('user_profiles').insert(profile_data).execute()
                
                # Log creazione
                log_data = {
                    'user_id': user_id,
                    'action': 'user_created',
                    'success': True,
                    'details': {'created_by': st.session_state.get('username', 'admin')},
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase_manager.supabase.table('user_access_logs').insert(log_data).execute()
                
                st.success(f"✅ Utente '{username}' creato con successo!")
                return True
            else:
                st.error("❌ Errore nella creazione dell'utente")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore nella creazione dell'utente: {e}")
            return False
    
    def update_user(self, user_id, updates):
        """Aggiorna un utente esistente"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase_manager.supabase.table('users').update(updates).eq('id', user_id).execute()
            
            if response.data:
                st.success("✅ Utente aggiornato con successo!")
                return True
            else:
                st.error("❌ Errore nell'aggiornamento dell'utente")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore nell'aggiornamento dell'utente: {e}")
            return False
    
    def delete_user(self, user_id, username):
        """Elimina un utente (solo per admin)"""
        try:
            logger.info(f"🔍 HOOK DELETE_USER: Tentativo eliminazione utente {username} (ID: {user_id})")
            
            # Verifica che non sia l'utente corrente
            if user_id == st.session_state.get('user_info', {}).get('id'):
                st.error("❌ Non puoi eliminare il tuo stesso account!")
                logger.warning(f"🔍 HOOK DELETE_USER: Tentativo eliminazione account corrente bloccato")
                return False
            
            logger.info(f"🔍 HOOK DELETE_USER: Eliminazione profilo utente per ID {user_id}")
            # Elimina profilo utente
            profile_response = self.supabase_manager.supabase.table('user_profiles').delete().eq('user_id', user_id).execute()
            logger.info(f"🔍 HOOK DELETE_USER: Profilo eliminato: {profile_response.data}")
            
            logger.info(f"🔍 HOOK DELETE_USER: Eliminazione utente per ID {user_id}")
            # Elimina utente
            response = self.supabase_manager.supabase.table('users').delete().eq('id', user_id).execute()
            logger.info(f"🔍 HOOK DELETE_USER: Risposta eliminazione: {response.data}")
            
            if response.data:
                st.success(f"✅ Utente '{username}' eliminato con successo!")
                logger.info(f"🔍 HOOK DELETE_USER: Utente {username} eliminato con successo")
                return True
            else:
                st.error("❌ Errore nell'eliminazione dell'utente")
                logger.error(f"🔍 HOOK DELETE_USER: Errore eliminazione - nessun dato restituito")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore nell'eliminazione dell'utente: {e}")
            logger.error(f"🔍 HOOK DELETE_USER: Eccezione durante eliminazione: {e}")
            return False
    
    def toggle_user_status(self, user_id, current_status, username):
        """Attiva/disattiva un utente"""
        try:
            new_status = not current_status
            updates = {
                'is_active': new_status,
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase_manager.supabase.table('users').update(updates).eq('id', user_id).execute()
            
            if response.data:
                status_text = "attivato" if new_status else "disattivato"
                st.success(f"✅ Utente '{username}' {status_text} con successo!")
                return True
            else:
                st.error("❌ Errore nel cambio di stato dell'utente")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore nel cambio di stato dell'utente: {e}")
            return False
    
    def render_user_management(self):
        """Rende l'interfaccia principale di gestione utenti"""
        
        if not self.check_admin_permissions():
            return
        
        st.header("👥 Gestione Utenti")
        st.markdown("---")
        
        # Tab per diverse funzionalità
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Lista Utenti", "➕ Nuovo Utente", "🔧 Modifica Utente", "📈 Statistiche"])
        
        with tab1:
            self.render_users_list()
        
        with tab2:
            self.render_create_user()
        
        with tab3:
            self.render_edit_user()
        
        with tab4:
            self.render_user_statistics()
    
    def render_users_list(self):
        """Rende la lista degli utenti"""
        st.subheader("📊 Lista Utenti")
        
        # Recupera utenti
        users_df = self.get_all_users()
        
        if users_df.empty:
            st.info("ℹ️ Nessun utente trovato nel sistema.")
            return
        
        # Formatta i dati per la visualizzazione
        display_df = users_df.copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
        display_df['last_login'] = pd.to_datetime(display_df['last_login']).dt.strftime('%d/%m/%Y %H:%M') if 'last_login' in display_df.columns else 'Mai'
        display_df['status'] = display_df['is_active'].map({True: '🟢 Attivo', False: '🔴 Inattivo'})
        
        # Mostra tabella
        st.dataframe(
            display_df[['username', 'full_name', 'email', 'role', 'status', 'created_at', 'last_login']],
            use_container_width=True,
            hide_index=True
        )
        
        # Azioni rapide
        st.subheader("⚡ Azioni Rapide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Attiva/Disattiva utente
            selected_user = st.selectbox(
                "Seleziona utente per cambio stato:",
                options=users_df['username'].tolist(),
                key="status_user_select"
            )
            
            if selected_user:
                user_data = users_df[users_df['username'] == selected_user].iloc[0]
                current_status = user_data['is_active']
                
                if st.button(f"{'🔴 Disattiva' if current_status else '🟢 Attiva'} {selected_user}"):
                    self.toggle_user_status(user_data['id'], current_status, selected_user)
                    pass  # st.rerun() rimosso per evitare reindirizzamento
        
        with col2:
            # Elimina utente
            delete_user = st.selectbox(
                "Seleziona utente da eliminare:",
                options=users_df[users_df['username'] != 'admin']['username'].tolist(),
                key="delete_user_select"
            )
            
            if delete_user:
                user_data = users_df[users_df['username'] == delete_user].iloc[0]
                
                # Gestione stato di conferma per eliminazione
                confirm_key = f"confirm_delete_{delete_user}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                # Se non è ancora stata richiesta la conferma, mostra il pulsante elimina
                if not st.session_state[confirm_key]:
                    if st.button(f"🗑️ Elimina {delete_user}", type="secondary", key=f"delete_btn_{delete_user}"):
                        logger.info(f"🔍 ELIMINAZIONE UTENTE: Pulsante elimina cliccato per {delete_user}")
                        st.session_state[confirm_key] = True
                        pass  # st.rerun() rimosso per evitare reindirizzamento
                
                # Se è richiesta la conferma, mostra il checkbox e il pulsante di conferma
                else:
                    logger.info(f"🔍 ELIMINAZIONE UTENTE: Mostrando conferma per {delete_user}")
                    st.warning(f"⚠️ Sei sicuro di voler eliminare l'utente '{delete_user}'?")
                    
                    col_confirm1, col_confirm2 = st.columns(2)
                    
                    with col_confirm1:
                        if st.button("✅ Conferma Eliminazione", type="primary", key=f"confirm_btn_{delete_user}"):
                            logger.info(f"🔍 ELIMINAZIONE UTENTE: Conferma eliminazione cliccata per {delete_user}")
                            if self.delete_user(user_data['id'], delete_user):
                                st.session_state[confirm_key] = False
                                pass  # st.rerun() rimosso per evitare reindirizzamento
                    
                    with col_confirm2:
                        if st.button("❌ Annulla", type="secondary", key=f"cancel_btn_{delete_user}"):
                            logger.info(f"🔍 ELIMINAZIONE UTENTE: Annulla eliminazione cliccato per {delete_user}")
                            st.session_state[confirm_key] = False
                            pass  # st.rerun() rimosso per evitare reindirizzamento
    
    def render_create_user(self):
        """Rende il form per la creazione di nuovi utenti"""
        st.subheader("➕ Nuovo Utente")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("👤 Username *", placeholder="es. mario.rossi")
                email = st.text_input("📧 Email *", placeholder="es. mario@example.com")
                password = st.text_input("🔐 Password *", type="password", placeholder="Minimo 8 caratteri")
            
            with col2:
                full_name = st.text_input("📝 Nome Completo *", placeholder="es. Mario Rossi")
                role = st.selectbox("🏷️ Ruolo *", options=['user', 'manager', 'admin'])
                is_active = st.checkbox("✅ Utente Attivo", value=True)
            
            # Validazione
            if st.form_submit_button("🚀 Crea Utente"):
                if not all([username, email, password, full_name, role]):
                    st.error("❌ Tutti i campi obbligatori devono essere compilati!")
                elif len(password) < 8:
                    st.error("❌ La password deve essere di almeno 8 caratteri!")
                else:
                    if self.create_user(username, email, password, full_name, role):
                        pass  # st.rerun() rimosso per evitare reindirizzamento
    
    def render_edit_user(self):
        """Rende l'interfaccia per la modifica degli utenti"""
        st.subheader("🔧 Modifica Utente")
        
        # Recupera utenti
        users_df = self.get_all_users()
        
        if users_df.empty:
            st.info("ℹ️ Nessun utente da modificare.")
            return
        
        # Selezione utente
        selected_user = st.selectbox(
            "Seleziona utente da modificare:",
            options=users_df['username'].tolist(),
            key="edit_user_select"
        )
        
        if selected_user:
            user_data = users_df[users_df['username'] == selected_user].iloc[0]
            
            with st.form("edit_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_email = st.text_input("📧 Email", value=user_data.get('email', ''))
                    new_full_name = st.text_input("📝 Nome Completo", value=user_data.get('full_name', ''))
                
                with col2:
                    new_role = st.selectbox("🏷️ Ruolo", options=['user', 'manager', 'admin'], index=['user', 'manager', 'admin'].index(user_data.get('role', 'user')))
                    new_status = st.checkbox("✅ Utente Attivo", value=user_data.get('is_active', True))
                
                if st.form_submit_button("💾 Salva Modifiche"):
                    updates = {
                        'email': new_email,
                        'full_name': new_full_name,
                        'role': new_role,
                        'is_active': new_status
                    }
                    
                    if self.update_user(user_data['id'], updates):
                        pass  # st.rerun() rimosso per evitare reindirizzamento
    
    def render_user_statistics(self):
        """Rende le statistiche degli utenti"""
        st.subheader("📈 Statistiche Utenti")
        
        # Recupera dati
        users_df = self.get_all_users()
        
        if users_df.empty:
            st.info("ℹ️ Nessun dato disponibile per le statistiche.")
            return
        
        # Calcola statistiche
        total_users = len(users_df)
        active_users = len(users_df[users_df['is_active'] == True])
        inactive_users = total_users - active_users
        
        role_counts = users_df['role'].value_counts()
        
        # Mostra metriche
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Utenti Totali", total_users)
        
        with col2:
            st.metric("🟢 Utenti Attivi", active_users)
        
        with col3:
            st.metric("🔴 Utenti Inattivi", inactive_users)
        
        with col4:
            st.metric("🏷️ Ruoli", len(role_counts))
        
        # Grafico distribuzione ruoli
        st.subheader("📊 Distribuzione Ruoli")
        if not role_counts.empty:
            st.bar_chart(role_counts)
        
        # Grafico utenti per data creazione
        st.subheader("📅 Utenti per Data Creazione")
        if 'created_at' in users_df.columns:
            users_df['created_date'] = pd.to_datetime(users_df['created_at']).dt.date
            date_counts = users_df['created_date'].value_counts().sort_index()
            st.line_chart(date_counts)

def render_user_management():
    """Funzione principale per rendere il componente di gestione utenti"""
    user_mgmt = UserManagement()
    user_mgmt.render_user_management()
