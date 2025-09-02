#!/usr/bin/env python3
"""
⚙️ COMPONENTE IMPOSTAZIONI UTENTE - Dashboard CPA
Gestione impostazioni personali, cambio password, profilo utente
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import logging
import hashlib
import secrets
from utils.translations import t

# Configura il logger
logger = logging.getLogger(__name__)

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

class UserSettings:
    """Classe per la gestione delle impostazioni utente"""
    
    def __init__(self):
        """Inizializza il sistema di impostazioni utente"""
        self.supabase_manager = SupabaseManager()
        self.current_user = st.session_state.get('username')
        self.current_role = st.session_state.get('roles')
        
        logger.info(f"🔍 USER_SETTINGS: Inizializzazione per utente {self.current_user}")
        
    def hash_password(self, password: str) -> str:
        """Hash della password con salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verifica password"""
        try:
            salt, hash_value = stored_hash.split('$')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == hash_value
        except:
            return False
    
    def get_current_user_data(self):
        """Recupera i dati dell'utente corrente"""
        try:
            if not self.current_user:
                return None
                
            response = self.supabase_manager.supabase.table('users').select('*').eq('username', self.current_user).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"🔍 USER_SETTINGS: Errore recupero dati utente: {e}")
            return None
    
    def change_password(self, current_password: str, new_password: str, confirm_password: str) -> bool:
        """Cambia la password dell'utente corrente"""
        try:
            logger.info(f"🔍 USER_SETTINGS: Tentativo cambio password per {self.current_user}")
            
            # Validazioni
            if not current_password or not new_password or not confirm_password:
                st.error("❌ Tutti i campi sono obbligatori")
                return False
            
            if new_password != confirm_password:
                st.error("❌ Le nuove password non coincidono")
                return False
            
            if len(new_password) < 8:
                st.error("❌ La nuova password deve essere di almeno 8 caratteri")
                return False
            
            # Recupera dati utente corrente
            user_data = self.get_current_user_data()
            if not user_data:
                st.error("❌ Utente non trovato")
                return False
            
            # Verifica password corrente
            current_hash = user_data.get('password_hash', '')
            logger.info(f"🔍 USER_SETTINGS: Password corrente nel DB: {current_hash}")
            logger.info(f"🔍 USER_SETTINGS: Password inserita: {current_password}")
            
            # Per compatibilità con il sistema attuale (password semplice)
            password_correct = False
            
            # Prova confronto diretto (per password semplici)
            if current_password == current_hash:
                password_correct = True
                logger.info(f"🔍 USER_SETTINGS: Password corretta (confronto diretto)")
            else:
                # Prova con hash (per password hashate)
                password_correct = self.verify_password(current_password, current_hash)
                logger.info(f"🔍 USER_SETTINGS: Password corretta (hash): {password_correct}")
            
            if not password_correct:
                st.error("❌ Password corrente non corretta")
                logger.warning(f"🔍 USER_SETTINGS: Password corrente non corretta")
                return False
            
            # Hash della nuova password
            new_password_hash = self.hash_password(new_password)
            logger.info(f"🔍 USER_SETTINGS: Nuova password hashata: {new_password_hash}")
            
            # Aggiorna password nel database
            response = self.supabase_manager.supabase.table('users').update({
                'password_hash': new_password_hash,
                'updated_at': datetime.now().isoformat()
            }).eq('username', self.current_user).execute()
            
            if response.data:
                logger.info(f"🔍 USER_SETTINGS: Password cambiata con successo per {self.current_user}")
                st.success("✅ Password cambiata con successo!")
                return True
            else:
                st.error("❌ Errore nell'aggiornamento della password")
                return False
                
        except Exception as e:
            logger.error(f"🔍 USER_SETTINGS: Errore cambio password: {e}")
            st.error(f"❌ Errore durante il cambio password: {e}")
            return False
    
    def update_profile(self, full_name: str, email: str) -> bool:
        """Aggiorna il profilo utente"""
        try:
            logger.info(f"🔍 USER_SETTINGS: Aggiornamento profilo per {self.current_user}")
            
            # Validazioni
            if not full_name or not email:
                st.error("❌ Nome completo e email sono obbligatori")
                return False
            
            # Aggiorna profilo nel database
            response = self.supabase_manager.supabase.table('users').update({
                'full_name': full_name,
                'email': email,
                'updated_at': datetime.now().isoformat()
            }).eq('username', self.current_user).execute()
            
            if response.data:
                logger.info(f"🔍 USER_SETTINGS: Profilo aggiornato con successo per {self.current_user}")
                st.success("✅ Profilo aggiornato con successo!")
                return True
            else:
                st.error("❌ Errore nell'aggiornamento del profilo")
                return False
                
        except Exception as e:
            logger.error(f"🔍 USER_SETTINGS: Errore aggiornamento profilo: {e}")
            st.error(f"❌ Errore durante l'aggiornamento del profilo: {e}")
            return False
    
    def render_user_settings(self):
        """Rende l'interfaccia principale delle impostazioni utente"""
        
        if not self.current_user:
            st.error(t("user_settings.not_authenticated", "❌ Utente non autenticato"))
            return
        
        st.header(t("user_settings.title", "⚙️ Impostazioni Utente"))
        st.markdown("---")
        
        # Recupera dati utente corrente
        user_data = self.get_current_user_data()
        
        if not user_data:
            st.error(t("user_settings.user_data_error", "❌ Impossibile recuperare i dati utente"))
            return
        
        # Tab per diverse funzionalità
        if self.current_role == 'admin':
            # Admin ha accesso a tutte le funzionalità
            tab1, tab2, tab3, tab4 = st.tabs([
                t("user_settings.tabs.change_password", "🔐 Cambio Password"),
                t("user_settings.tabs.profile", "👤 Profilo Utente"),
                t("user_settings.tabs.account_info", "📊 Informazioni Account"),
                t("user_settings.tabs.admin_password_management", "👑 Gestione Password Utenti")
            ])
            
            with tab1:
                self.render_change_password()
            
            with tab2:
                self.render_profile_settings(user_data)
            
            with tab3:
                self.render_account_info(user_data)
            
            with tab4:
                self.render_admin_password_management()
        else:
            # Utenti normali hanno accesso limitato
            tab1, tab2, tab3 = st.tabs([
                t("user_settings.tabs.change_password", "🔐 Cambio Password"),
                t("user_settings.tabs.profile", "👤 Profilo Utente"),
                t("user_settings.tabs.account_info", "📊 Informazioni Account")
            ])
            
            with tab1:
                self.render_change_password()
            
            with tab2:
                self.render_profile_settings(user_data)
            
            with tab3:
                self.render_account_info(user_data)
    
    def render_change_password(self):
        """Rende il form per il cambio password"""
        st.subheader("🔐 Cambio Password")
        st.info("⚠️ **Attenzione**: Il cambio password richiede la password corrente per sicurezza")
        
        with st.form("change_password_form"):
            current_password = st.text_input("🔑 Password Corrente", type="password", placeholder="Inserisci la password corrente")
            new_password = st.text_input("🆕 Nuova Password", type="password", placeholder="Minimo 8 caratteri")
            confirm_password = st.text_input("✅ Conferma Nuova Password", type="password", placeholder="Ripeti la nuova password")
            
            # Validazione password
            if new_password:
                if len(new_password) < 8:
                    st.warning("⚠️ La password deve essere di almeno 8 caratteri")
                elif new_password != confirm_password:
                    st.warning("⚠️ Le password non coincidono")
                else:
                    st.success("✅ Password valida")
            
            if st.form_submit_button("🔄 Cambia Password", type="primary"):
                if self.change_password(current_password, new_password, confirm_password):
                    st.rerun()
    
    def render_profile_settings(self, user_data):
        """Rende il form per le impostazioni del profilo"""
        st.subheader("👤 Profilo Utente")
        
        with st.form("profile_settings_form"):
            full_name = st.text_input("📝 Nome Completo", value=user_data.get('full_name', ''))
            email = st.text_input("📧 Email", value=user_data.get('email', ''))
            
            # Informazioni di sola lettura
            st.info(f"**👤 Username:** {user_data.get('username', 'N/A')}")
            st.info(f"**🏷️ Ruolo:** {user_data.get('role', 'N/A')}")
            st.info(f"**📅 Account creato:** {user_data.get('created_at', 'N/A')}")
            
            if st.form_submit_button("💾 Salva Modifiche", type="primary"):
                if self.update_profile(full_name, email):
                    st.rerun()
    
    def render_account_info(self, user_data):
        """Rende le informazioni dell'account"""
        st.subheader("📊 Informazioni Account")
        
        # Informazioni principali
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("👤 Username", user_data.get('username', 'N/A'))
            st.metric("📧 Email", user_data.get('email', 'N/A'))
            st.metric("🏷️ Ruolo", user_data.get('role', 'N/A'))
        
        with col2:
            st.metric("📅 Data Creazione", user_data.get('created_at', 'N/A')[:10] if user_data.get('created_at') else 'N/A')
            st.metric("🔄 Ultimo Aggiornamento", user_data.get('updated_at', 'N/A')[:10] if user_data.get('updated_at') else 'N/A')
            st.metric("🟢 Stato", "Attivo" if user_data.get('is_active', True) else "Inattivo")
        
        # Ultimo accesso
        last_login = user_data.get('last_login', 'Mai')
        if last_login and last_login != 'Mai':
            st.info(f"**🕐 Ultimo Accesso:** {last_login}")
        else:
            st.info("**🕐 Ultimo Accesso:** Mai")
        
        # Statistiche sessione
        st.markdown("---")
        st.subheader("📈 Statistiche Sessione")
        
        session_start = st.session_state.get('session_start', 'N/A')
        st.info(f"**🕐 Inizio Sessione:** {session_start}")
        
        # Pulsante per forzare il logout
        if st.button("🚪 Forza Logout", type="secondary"):
            st.warning("⚠️ Sei sicuro di voler forzare il logout?")
            if st.button("✅ Conferma Logout Forzato", type="primary"):
                # Importa la funzione di logout
                from auth_simple_no_cookie import logout_user
                logout_user()
    
    def render_admin_password_management(self):
        """Rende l'interfaccia per la gestione password degli utenti (solo admin)"""
        st.subheader("👑 Gestione Password Utenti")
        st.info("🔐 **FUNZIONALITÀ ADMIN**: Cambia le password di qualsiasi utente del sistema")
        
        # Recupera tutti gli utenti
        try:
            response = self.supabase_manager.supabase.table('users').select('*').execute()
            if not response.data:
                st.warning("⚠️ Nessun utente trovato nel sistema")
                return
            
            users_df = pd.DataFrame(response.data)
            
            # Selezione utente
            selected_user = st.selectbox(
                "👤 Seleziona utente per cambio password:",
                options=users_df['username'].tolist(),
                key="admin_user_select"
            )
            
            if selected_user:
                user_data = users_df[users_df['username'] == selected_user].iloc[0]
                
                st.markdown("---")
                st.subheader(f"🔐 Cambio Password per: {selected_user}")
                
                # Informazioni utente
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**👤 Username:** {user_data.get('username', 'N/A')}")
                    st.info(f"**📧 Email:** {user_data.get('email', 'N/A')}")
                with col2:
                    st.info(f"**🏷️ Ruolo:** {user_data.get('role', 'N/A')}")
                    st.info(f"**🟢 Stato:** {'Attivo' if user_data.get('is_active', True) else 'Inattivo'}")
                
                # Form cambio password
                with st.form("admin_change_password_form"):
                    new_password = st.text_input("🆕 Nuova Password", type="password", placeholder="Minimo 8 caratteri")
                    confirm_password = st.text_input("✅ Conferma Nuova Password", type="password", placeholder="Ripeti la nuova password")
                    
                    # Validazione password
                    if new_password:
                        if len(new_password) < 8:
                            st.warning("⚠️ La password deve essere di almeno 8 caratteri")
                        elif new_password != confirm_password:
                            st.warning("⚠️ Le password non coincidono")
                        else:
                            st.success("✅ Password valida")
                    
                    if st.form_submit_button("🔄 Cambia Password Utente", type="primary"):
                        if self.admin_change_user_password(selected_user, new_password, confirm_password):
                            st.rerun()
                            
        except Exception as e:
            logger.error(f"🔍 USER_SETTINGS: Errore gestione password admin: {e}")
            st.error(f"❌ Errore nel caricamento utenti: {e}")
    
    def admin_change_user_password(self, username: str, new_password: str, confirm_password: str) -> bool:
        """Cambia la password di un utente (solo admin)"""
        try:
            logger.info(f"🔍 USER_SETTINGS: Admin cambio password per utente {username}")
            
            # Validazioni
            if not new_password or not confirm_password:
                st.error("❌ Tutti i campi sono obbligatori")
                return False
            
            if new_password != confirm_password:
                st.error("❌ Le password non coincidono")
                return False
            
            if len(new_password) < 8:
                st.error("❌ La password deve essere di almeno 8 caratteri")
                return False
            
            # Verifica che l'utente esista
            response = self.supabase_manager.supabase.table('users').select('*').eq('username', username).execute()
            if not response.data:
                st.error(f"❌ Utente {username} non trovato")
                return False
            
            # Hash della nuova password
            new_password_hash = self.hash_password(new_password)
            logger.info(f"🔍 USER_SETTINGS: Nuova password hashata per {username}: {new_password_hash}")
            
            # Aggiorna password nel database
            update_response = self.supabase_manager.supabase.table('users').update({
                'password_hash': new_password_hash,
                'updated_at': datetime.now().isoformat()
            }).eq('username', username).execute()
            
            if update_response.data:
                logger.info(f"🔍 USER_SETTINGS: Password cambiata con successo per {username}")
                st.success(f"✅ Password cambiata con successo per l'utente {username}!")
                return True
            else:
                st.error("❌ Errore nell'aggiornamento della password")
                return False
                
        except Exception as e:
            logger.error(f"🔍 USER_SETTINGS: Errore cambio password admin: {e}")
            st.error(f"❌ Errore durante il cambio password: {e}")
            return False

def render_user_settings():
    """Funzione principale per rendere il componente di impostazioni utente"""
    user_settings = UserSettings()
    user_settings.render_user_settings()
