#!/usr/bin/env python3
"""
🧭 COMPONENTE NAVIGAZIONE UTENTE - Dashboard CPA
Navigazione e integrazione del sistema utenti nella dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os
import logging

# Configura il logger
logger = logging.getLogger(__name__)

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

class UserNavigation:
    """Classe per la navigazione e integrazione utente"""
    
    def __init__(self):
        """Inizializza il sistema di navigazione"""
        self.supabase_manager = SupabaseManager()
        self.current_user = st.session_state.get('username')
        self.current_user_info = st.session_state.get('user_info', {})
        
    def render_user_header(self):
        """Rende l'header con informazioni utente compatte"""
        if not self.current_user:
            return
        
        # Header utente compatto nella sidebar
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 **Utente**")
            
            # Informazioni utente in layout compatto
            current_role = st.session_state.get('roles', 'user')
            role_icon = {'admin': '👑', 'manager': '👔', 'user': '👤'}
            
            # Layout compatto con tutte le info
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"<h2>{role_icon.get(current_role, '👤')}</h2>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{self.current_user_info.get('full_name', self.current_user)}**")
                st.markdown(f"*{current_role.title()}*")
                st.markdown(f"`{self.current_user}`")
            
            # Pulsante logout nella sezione utente
            if st.button("🚪 Logout", type="secondary", use_container_width=True, key="logout_user_section"):
                from auth_simple_no_cookie import logout_user
                logout_user()
            
            st.markdown("---")
    
    def render_user_menu(self):
        """Rende il menu utente nella sidebar"""
        if not self.current_user:
            return
        
        with st.sidebar:
            st.markdown("### 🧭 **Menu Utente**")
            
            # Menu principale
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state['current_page'] = 'dashboard'
                st.rerun()  # Necessario per la navigazione
            
            if st.button("⚙️ Impostazioni", use_container_width=True):
                st.session_state['current_page'] = 'settings'
                st.rerun()  # Necessario per la navigazione
            
            # Pulsante logout rimosso - ora gestito nella sezione utente
            
            # Menu amministratore - USA IL RUOLO CORRETTO DAL SESSION_STATE
            # HOOK: traccia quando viene verificato il ruolo per il menu admin
            logger.info(f"🔍 HOOK NAVIGATION: Verifica ruolo per menu admin")
            logger.info(f"🔍 HOOK NAVIGATION: user_info.role = {self.current_user_info.get('role')}")
            logger.info(f"🔍 HOOK NAVIGATION: session_state.roles = {st.session_state.get('roles')}")
            
            # Usa il ruolo dal user_info invece che dal session_state
            current_role = self.current_user_info.get('role', 'user')
            if current_role == 'admin':
                st.markdown("---")
                st.markdown("#### 👑 **Amministrazione**")
                
                if st.button("📊 Statistiche Sistema", use_container_width=True):
                    st.session_state['current_page'] = 'system_stats'
                    st.rerun()  # Necessario per la navigazione
            
            st.markdown("---")
            
            # Logout - RIMOSSO PER EVITARE DUPLICAZIONE
            # Il logout è già gestito da show_user_info() nell'app principale
            # if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            #     self.logout_user()
    
    def render_breadcrumb(self):
        """Rende il breadcrumb per la navigazione"""
        current_page = st.session_state.get('current_page', 'dashboard')
        
        breadcrumb_map = {
            'dashboard': '🏠 Dashboard',
            'settings': '⚙️ Impostazioni',
            'system_stats': '📊 Statistiche Sistema'
        }
        
        if current_page in breadcrumb_map:
            st.markdown(f"**Navigazione**: {breadcrumb_map[current_page]}")
            st.markdown("---")
    
    def render_page_content(self):
        """Rende il contenuto della pagina corrente"""
        current_page = st.session_state.get('current_page', 'dashboard')
        
        if current_page == 'settings':
            from .user_settings import render_user_settings
            render_user_settings()
        
        elif current_page == 'system_stats':
            self.render_system_statistics()
        
        else:
            # Pagina dashboard predefinita
            self.render_dashboard_welcome()
    
    def render_dashboard_welcome(self):
        """Rende la pagina di benvenuto della dashboard"""
        
        if self.current_user:
            st.success(f"👋 Benvenuto, **{self.current_user_info.get('full_name', self.current_user)}**!")
            
            # Informazioni rapide
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # HOOK: traccia quando viene visualizzato il ruolo nel dashboard
                logger.info(f"🔍 HOOK NAVIGATION: Visualizzazione ruolo nel dashboard")
                logger.info(f"🔍 HOOK NAVIGATION: user_info.role = {self.current_user_info.get('role')}")
                logger.info(f"🔍 HOOK NAVIGATION: session_state.roles = {st.session_state.get('roles')}")
                
                # Usa il ruolo dal session_state invece che da user_info
                current_role = st.session_state.get('roles', 'user')
                st.info(f"**🏷️ Ruolo**: {current_role.title()}")
            
            with col2:
                st.info(f"**📅 Data**: {datetime.now().strftime('%d/%m/%Y')}")
            
            with col3:
                st.info(f"**⏰ Ora**: {datetime.now().strftime('%H:%M')}")
            
            st.markdown("---")
            
            # Contenuto dashboard esistente
            st.subheader("📊 Panoramica Sistema")
            
            # Statistiche rapide
            try:
                # Conta clienti
                clienti_response = self.supabase_manager.supabase.table('clienti').select('count', count='exact').execute()
                clienti_count = clienti_response.count if hasattr(clienti_response, 'count') else 0
                
                # Conta incroci
                incroci_response = self.supabase_manager.supabase.table('incroci').select('count', count='exact').execute()
                incroci_count = incroci_response.count if hasattr(incroci_response, 'count') else 0
                
                # Conta utenti
                users_response = self.supabase_manager.supabase.table('users').select('count', count='exact').execute()
                users_count = users_response.count if hasattr(users_response, 'count') else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("👥 Clienti", clienti_count)
                
                with col2:
                    st.metric("🔗 Incroci", incroci_count)
                
                with col3:
                    st.metric("👤 Utenti", users_count)
                
            except Exception as e:
                st.warning(f"⚠️ Impossibile recuperare le statistiche: {e}")
            
            st.markdown("---")
            
            # Azioni rapide
            # Riepilogo Depositi Totali
            try:
                depositi_response = self.supabase_manager.supabase.table("clienti").select("deposito").execute()
                if depositi_response.data:
                    df_depositi = pd.DataFrame(depositi_response.data)
                    depositi_totali = df_depositi["deposito"].sum() if "deposito" in df_depositi.columns else 0
                    st.metric("💰 Depositi Totali", f"€{depositi_totali:,.2f}")
                else:
                    st.metric("💰 Depositi Totali", "€0.00")
            except Exception as e:
                st.metric("💰 Depositi Totali", "€0.00")

            # Grafici a torta
            st.subheader("📊 Grafici Sistema")
            col1, col2 = st.columns(2)

            with col1:
                try:
                    # Distribuzione Clienti per Broker
                    broker_response = self.supabase_manager.supabase.table("clienti").select("broker").execute()
                    if broker_response.data:
                        df_broker = pd.DataFrame(broker_response.data)
                        broker_counts = df_broker["broker"].value_counts()
                        fig_broker = px.pie(values=broker_counts.values, names=broker_counts.index, title="Distribuzione Clienti per Broker")
                        st.plotly_chart(fig_broker, use_container_width=True)
                    else:
                        st.info("📊 Nessun dato disponibile per la distribuzione broker")
                except Exception as e:
                    st.info("📊 Errore nel caricamento grafico broker")

                try:
                    # Distribuzione Piattaforme
                    piattaforma_response = self.supabase_manager.supabase.table("clienti").select("piattaforma").execute()
                    if piattaforma_response.data:
                        df_piattaforma = pd.DataFrame(piattaforma_response.data)
                        piattaforma_counts = df_piattaforma["piattaforma"].value_counts()
                        fig_piattaforma = px.pie(values=piattaforma_counts.values, names=piattaforma_counts.index, title="Distribuzione Piattaforme")
                        st.plotly_chart(fig_piattaforma, use_container_width=True)
                    else:
                        st.info("📊 Nessun dato disponibile per la distribuzione piattaforme")
                except Exception as e:
                    st.info("📊 Errore nel caricamento grafico piattaforme")

            with col2:
                try:
                    # Depositi Totali per Broker
                    depositi_broker_response = self.supabase_manager.supabase.table("clienti").select("broker,deposito").execute()
                    if depositi_broker_response.data:
                        df_depositi_broker = pd.DataFrame(depositi_broker_response.data)
                        depositi_per_broker = df_depositi_broker.groupby("broker")["deposito"].sum()
                        fig_depositi = px.pie(values=depositi_per_broker.values, names=depositi_per_broker.index, title="Depositi Totali per Broker")
                        st.plotly_chart(fig_depositi, use_container_width=True)
                    else:
                        st.info("📊 Nessun dato disponibile per i depositi per broker")
                except Exception as e:
                    st.info("📊 Errore nel caricamento grafico depositi")

                try:
                    # Statistiche Sistema
                    stats_data = {"Metrica": ["Clienti", "Incroci", "Utenti"], "Valore": [clienti_count, incroci_count, users_count]}
                    df_stats = pd.DataFrame(stats_data)
                    fig_stats = px.pie(values=df_stats["Valore"], names=df_stats["Metrica"], title="Statistiche Sistema")
                    st.plotly_chart(fig_stats, use_container_width=True)
                except Exception as e:
                    st.info("📊 Errore nel caricamento grafico statistiche")
        else:
            st.warning("⚠️ Devi effettuare il login per accedere alla dashboard.")
    
    def render_system_statistics(self):
        """Rende le statistiche del sistema"""
        st.title("📊 Statistiche Sistema")
        
        # HOOK: traccia quando viene verificato il permesso per statistiche
        logger.info(f"🔍 HOOK NAVIGATION: Verifica permesso statistiche sistema")
        logger.info(f"🔍 HOOK NAVIGATION: user_info.role = {self.current_user_info.get('role')}")
        logger.info(f"🔍 HOOK NAVIGATION: session_state.roles = {st.session_state.get('roles')}")
        
        # Usa il ruolo dal session_state invece che da user_info
        if not st.session_state.get('roles') == 'admin':
            st.error("❌ Accesso negato. Solo gli amministratori possono visualizzare le statistiche del sistema.")
            logger.warning(f"🔍 HOOK NAVIGATION: Accesso negato per statistiche - ruolo: {st.session_state.get('roles')}")
            return
        
        logger.info(f"🔍 HOOK NAVIGATION: Accesso consentito per statistiche - ruolo: {st.session_state.get('roles')}")
        
        st.markdown("---")
        
        try:
            # Statistiche utenti
            st.subheader("👥 Statistiche Utenti")
            
            users_response = self.supabase_manager.supabase.table('users').select('*').execute()
            if users_response.data:
                users_df = pd.DataFrame(users_response.data)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("👥 Utenti Totali", len(users_df))
                
                with col2:
                    active_users = len(users_df[users_df['is_active'] == True])
                    st.metric("🟢 Utenti Attivi", active_users)
                
                with col3:
                    inactive_users = len(users_df[users_df['is_active'] == False])
                    st.metric("🔴 Utenti Inattivi", inactive_users)
                
                with col4:
                    roles_count = users_df['role'].nunique()
                    st.metric("🏷️ Ruoli", roles_count)
                
                # Distribuzione ruoli
                st.subheader("📊 Distribuzione Ruoli")
                role_counts = users_df['role'].value_counts()
                st.bar_chart(role_counts)
            
            # Statistiche accessi
            st.subheader("🔑 Statistiche Accessi")
            
            logs_response = self.supabase_manager.supabase.table('user_access_logs').select('*').execute()
            if logs_response.data:
                logs_df = pd.DataFrame(logs_response.data)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_logs = len(logs_df)
                    st.metric("📝 Log Totali", total_logs)
                
                with col2:
                    successful_logs = len(logs_df[logs_df['success'] == True])
                    st.metric("✅ Accessi Riusciti", successful_logs)
                
                with col3:
                    failed_logs = len(logs_df[logs_df['success'] == False])
                    st.metric("❌ Accessi Falliti", failed_logs)
                
                # Attività recenti
                st.subheader("📅 Attività Recenti")
                recent_logs = logs_df.head(10)
                if not recent_logs.empty:
                    st.dataframe(recent_logs[['action', 'success', 'created_at']], use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Errore nel recupero statistiche: {e}")
    
    def logout_user(self):
        """Gestisce il logout dell'utente"""
        try:
            # Log logout
            if self.current_user:
                user_response = self.supabase_manager.supabase.table('users').select('id').eq('username', self.current_user).execute()
                if user_response.data:
                    user_id = user_response.data[0]['id']
                    
                    log_data = {
                        'user_id': user_id,
                        'action': 'logout',
                        'success': True,
                        'details': {'logout_time': datetime.now().isoformat()},
                        'created_at': datetime.now().isoformat()
                    }
                    
                    self.supabase_manager.supabase.table('user_access_logs').insert(log_data).execute()
            
            # Pulisci session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.success("✅ Logout effettuato con successo!")
            # Rimuoviamo st.rerun() per evitare loop infinito
            
        except Exception as e:
            st.error(f"❌ Errore durante il logout: {e}")
    
    def render_complete_navigation(self):
        """Rende la navigazione completa"""
        # Header utente
        self.render_user_header()
        
        # Menu utente
        self.render_user_menu()
        
        # Breadcrumb
        self.render_breadcrumb()
        
        # Contenuto pagina
        self.render_page_content()

def render_user_navigation():
    """Funzione principale per rendere la navigazione utente"""
    user_nav = UserNavigation()
    user_nav.render_complete_navigation()
