#!/usr/bin/env python3
"""
⚙️ COMPONENTE IMPOSTAZIONI UTENTE - Dashboard CPA
Gestione profilo utente, password e preferenze personali
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import hashlib

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

class UserSettings:
    """Classe per la gestione delle impostazioni utente"""
    
    def __init__(self):
        """Inizializza il sistema di impostazioni utente"""
        self.supabase_manager = SupabaseManager()
        self.current_user = st.session_state.get('username')
        self.current_user_info = st.session_state.get('user_info', {})
        
    def get_user_profile(self):
        """Recupera il profilo dell'utente corrente"""
        try:
            if not self.current_user:
                st.error(f"❌ Username non trovato in session_state: {st.session_state.get('username')}")
                return None
            
            st.info(f"🔍 Recupero profilo per utente: {self.current_user}")
            
            # Recupera utente
            st.info("🔍 Query tabella users...")
            response = self.supabase_manager.supabase.table('users').select('*').eq('username', self.current_user).execute()
            st.info(f"📊 Risposta users: {len(response.data) if response.data else 0} record")
            
            if not response.data:
                st.error(f"❌ Nessun utente trovato con username: {self.current_user}")
                return None
            
            user_data = response.data[0]
            st.info(f"✅ Utente trovato: {user_data.get('username')} (ID: {user_data.get('id')})")
            
            # Recupera profilo
            st.info("🔍 Query tabella user_profiles...")
            profile_response = self.supabase_manager.supabase.table('user_profiles').select('*').eq('user_id', user_data['id']).execute()
            st.info(f"📊 Risposta user_profiles: {len(profile_response.data) if profile_response.data else 0} record")
            
            if profile_response.data:
                user_data['profile'] = profile_response.data[0]
                st.info("✅ Profilo utente trovato")
            else:
                st.warning("⚠️ Nessun profilo trovato per questo utente")
                user_data['profile'] = {}
            
            return user_data
            
        except Exception as e:
            st.error(f"❌ Errore nel recupero profilo: {e}")
            import traceback
            st.error(f"📋 Traceback completo: {traceback.format_exc()}")
            return None
    
    def update_profile(self, updates):
        """Aggiorna il profilo dell'utente"""
        try:
            if not self.current_user:
                st.error("❌ Utente non autenticato")
                return False
            
            # Recupera ID utente
            response = self.supabase_manager.supabase.table('users').select('id').eq('username', self.current_user).execute()
            if not response.data:
                st.error("❌ ID utente non trovato")
                return False
            
            user_id = response.data[0]['id']
            
            # Aggiorna utente
            user_updates = {k: v for k, v in updates.items() if k in ['full_name', 'email']}
            if user_updates:
                user_updates['updated_at'] = datetime.now().isoformat()
                self.supabase_manager.supabase.table('users').update(user_updates).eq('id', user_id).execute()
            
            # Aggiorna profilo
            profile_updates = {k: v for k, v in updates.items() if k in ['timezone', 'language', 'phone', 'address']}
            if profile_updates:
                profile_updates['updated_at'] = datetime.now().isoformat()
                self.supabase_manager.supabase.table('user_profiles').update(profile_updates).eq('user_id', user_id).execute()
            
            # Log aggiornamento
            log_data = {
                'user_id': user_id,
                'action': 'profile_updated',
                'success': True,
                'details': {'updated_fields': list(updates.keys())},
                'created_at': datetime.now().isoformat()
            }
            
            self.supabase_manager.supabase.table('user_access_logs').insert(log_data).execute()
            
            st.success("✅ Profilo aggiornato con successo!")
            return True
            
        except Exception as e:
            st.error(f"❌ Errore nell'aggiornamento del profilo: {e}")
            return False
    
    def change_password(self, current_password, new_password, confirm_password):
        """Cambia la password dell'utente"""
        try:
            if not self.current_user:
                st.error("❌ Utente non autenticato")
                return False
            
            # Validazione
            if new_password != confirm_password:
                st.error("❌ Le password non coincidono!")
                return False
            
            if len(new_password) < 8:
                st.error("❌ La nuova password deve essere di almeno 8 caratteri!")
                return False
            
            # Recupera utente
            response = self.supabase_manager.supabase.table('users').select('*').eq('username', self.current_user).execute()
            if not response.data:
                st.error("❌ Utente non trovato")
                return False
            
            user_data = response.data[0]
            
            # Verifica password corrente (semplificato per ora)
            current_hash = hashlib.sha256(current_password.encode()).hexdigest()
            if current_hash != user_data.get('password_hash', ''):
                st.error("❌ Password corrente non corretta!")
                return False
            
            # Aggiorna password
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            updates = {
                'password_hash': new_hash,
                'updated_at': datetime.now().isoformat()
            }
            
            self.supabase_manager.supabase.table('users').update(updates).eq('id', user_data['id']).execute()
            
            # Log cambio password
            log_data = {
                'user_id': user_data['id'],
                'action': 'password_changed',
                'success': True,
                'details': {'changed_at': datetime.now().isoformat()},
                'created_at': datetime.now().isoformat()
            }
            
            self.supabase_manager.supabase.table('user_access_logs').insert(log_data).execute()
            
            st.success("✅ Password cambiata con successo!")
            return True
            
        except Exception as e:
            st.error(f"❌ Errore nel cambio password: {e}")
            return False
    
    def get_user_activity(self):
        """Recupera l'attività dell'utente"""
        try:
            if not self.current_user:
                return pd.DataFrame()
            
            # Recupera ID utente
            response = self.supabase_manager.supabase.table('users').select('id').eq('username', self.current_user).execute()
            if not response.data:
                return pd.DataFrame()
            
            user_id = response.data[0]['id']
            
            # Recupera log attività
            response = self.supabase_manager.supabase.table('user_access_logs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"❌ Errore nel recupero attività: {e}")
            return pd.DataFrame()
    
    def render_user_settings(self):
        """Rende l'interfaccia principale delle impostazioni utente"""
        
        if not self.current_user:
            st.error("❌ Devi essere autenticato per accedere alle impostazioni.")
            return
        
        st.header("⚙️ Impostazioni Utente")
        st.markdown("---")
        
        # Informazioni utente corrente
        st.subheader(f"👤 Profilo di {self.current_user}")
        
        # Recupera profilo
        user_data = self.get_user_profile()
        
        if not user_data:
            st.error("❌ Impossibile recuperare il profilo utente.")
            return
        
        # Tab per diverse sezioni
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Modifica Profilo", "🔐 Cambia Password", "📊 Attività Recenti", "🎨 Preferenze"])
        
        with tab1:
            self.render_profile_edit(user_data)
        
        with tab2:
            self.render_password_change()
        
        with tab3:
            self.render_user_activity_log()
        
        with tab4:
            self.render_user_preferences(user_data)
    
    def render_profile_edit(self, user_data):
        """Rende il form per la modifica del profilo"""
        st.subheader("📝 Modifica Profilo")
        
        with st.form("profile_edit_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("📝 Nome Completo", value=user_data.get('full_name', ''))
                email = st.text_input("📧 Email", value=user_data.get('email', ''))
                phone = st.text_input("📱 Telefono", value=user_data.get('profile', {}).get('phone', ''))
            
            with col2:
                timezone = st.selectbox("🌍 Fuso Orario", 
                    options=['Europe/Rome', 'Europe/London', 'America/New_York', 'Asia/Tokyo'],
                    index=['Europe/Rome', 'Europe/London', 'America/New_York', 'Asia/Tokyo'].index(
                        user_data.get('profile', {}).get('timezone', 'Europe/Rome')
                    )
                )
                language = st.selectbox("🌐 Lingua", 
                    options=['it', 'en', 'es', 'fr', 'de'],
                    index=['it', 'en', 'es', 'fr', 'de'].index(
                        user_data.get('profile', {}).get('language', 'it')
                    )
                )
                address = st.text_area("📍 Indirizzo", value=user_data.get('profile', {}).get('address', ''))
            
            if st.form_submit_button("💾 Salva Modifiche"):
                updates = {
                    'full_name': full_name,
                    'email': email,
                    'timezone': timezone,
                    'language': language,
                    'phone': phone,
                    'address': address
                }
                
                if self.update_profile(updates):
                    st.rerun()
    
    def render_password_change(self):
        """Rende il form per il cambio password"""
        st.subheader("🔐 Cambia Password")
        
        with st.form("password_change_form"):
            current_password = st.text_input("🔑 Password Corrente", type="password")
            new_password = st.text_input("🆕 Nuova Password", type="password")
            confirm_password = st.text_input("✅ Conferma Nuova Password", type="password")
            
            st.info("ℹ️ La password deve essere di almeno 8 caratteri")
            
            if st.form_submit_button("🔄 Cambia Password"):
                if self.change_password(current_password, new_password, confirm_password):
                    st.rerun()
    
    def render_user_activity_log(self):
        """Rende il log delle attività dell'utente"""
        st.subheader("📊 Attività Recenti")
        
        # Recupera attività
        activity_df = self.get_user_activity()
        
        if activity_df.empty:
            st.info("ℹ️ Nessuna attività recente trovata.")
            return
        
        # Formatta dati
        display_df = activity_df.copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
        display_df['action'] = display_df['action'].map({
            'login': '🔑 Login',
            'logout': '🚪 Logout',
            'profile_updated': '📝 Profilo Aggiornato',
            'password_changed': '🔐 Password Cambiata',
            'user_created': '👤 Utente Creato'
        })
        display_df['success'] = display_df['success'].map({True: '✅', False: '❌'})
        
        # Mostra tabella
        st.dataframe(
            display_df[['action', 'success', 'created_at', 'details']],
            use_container_width=True,
            hide_index=True
        )
    
    def render_user_preferences(self, user_data):
        """Rende le preferenze dell'utente"""
        st.subheader("🎨 Preferenze")
        
        # Mostra preferenze attuali
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🌍 Fuso Orario", user_data.get('profile', {}).get('timezone', 'Europe/Rome'))
            st.metric("🌐 Lingua", user_data.get('profile', {}).get('language', 'it').upper())
        
        with col2:
            st.metric("🏷️ Ruolo", user_data.get('role', 'user').title())
            st.metric("📱 Telefono", user_data.get('profile', {}).get('phone', 'Non impostato'))
        
        # Informazioni account
        st.subheader("📋 Informazioni Account")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**👤 Username**: {user_data.get('username', 'N/A')}")
            st.info(f"**📧 Email**: {user_data.get('email', 'N/A')}")
        
        with col2:
            st.info(f"**📅 Creato il**: {pd.to_datetime(user_data.get('created_at')).strftime('%d/%m/%Y %H:%M')}")
            st.info(f"**🔄 Ultimo aggiornamento**: {pd.to_datetime(user_data.get('updated_at')).strftime('%d/%m/%Y %H:%M')}")
        
        # Ultimo accesso
        if user_data.get('last_login'):
            st.info(f"**🔑 Ultimo accesso**: {pd.to_datetime(user_data.get('last_login')).strftime('%d/%m/%Y %H:%M')}")
        else:
            st.info("**🔑 Ultimo accesso**: Primo accesso")

def render_user_settings():
    """Funzione principale per rendere il componente impostazioni utente"""
    user_settings = UserSettings()
    user_settings.render_user_settings()
