#!/usr/bin/env python3
"""
📊 NOTIFICATION DASHBOARD
Dashboard per monitoraggio e statistiche del sistema notifiche Telegram
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationDashboard:
    """Dashboard per monitoraggio notifiche"""
    
    def __init__(self):
        """Inizializza la dashboard"""
        self.telegram_manager = None
        self.supabase_manager = None
        self._init_managers()
    
    def _init_managers(self):
        """Inizializza i manager necessari"""
        try:
            from components.telegram_manager import TelegramManager
            from supabase_manager import SupabaseManager
            
            self.telegram_manager = TelegramManager()
            self.supabase_manager = SupabaseManager()
            
            logger.info("✅ NotificationDashboard inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione NotificationDashboard: {e}")
            st.error(f"❌ Errore inizializzazione: {e}")
    
    def render_dashboard(self):
        """Rende la dashboard principale"""
        st.header("📊 Dashboard Notifiche Telegram")
        st.info("📈 **MONITORAGGIO NOTIFICHE**: Statistiche e analisi del sistema notifiche Telegram")
        
        # Tab per organizzare le informazioni
        tab_overview, tab_statistics, tab_logs, tab_settings = st.tabs([
            "📊 Panoramica", "📈 Statistiche", "📝 Log Dettagliati", "⚙️ Impostazioni"
        ])
        
        with tab_overview:
            self._render_overview_tab()
        
        with tab_statistics:
            self._render_statistics_tab()
        
        with tab_logs:
            self._render_logs_tab()
        
        with tab_settings:
            self._render_settings_tab()
    
    def _render_overview_tab(self):
        """Rende il tab panoramica"""
        st.subheader("📊 Panoramica Sistema")
        
        if not self.telegram_manager:
            st.error("❌ TelegramManager non disponibile")
            return
        
        # Stato configurazione
        status = self.telegram_manager.get_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if status['is_configured']:
                st.success("✅ Bot Configurato")
            else:
                st.error("❌ Bot Non Configurato")
        
        with col2:
            if status['bot_token_set']:
                st.success("✅ Token Impostato")
            else:
                st.error("❌ Token Mancante")
        
        with col3:
            if status['chat_id_set']:
                st.success("✅ Chat ID Impostato")
            else:
                st.error("❌ Chat ID Mancante")
        
        with col4:
            if status['supabase_available']:
                st.success("✅ Database OK")
            else:
                st.error("❌ Database Errore")
        
        # Statistiche rapide
        st.markdown("---")
        st.subheader("📈 Statistiche Rapide")
        
        try:
            stats = self.telegram_manager.get_notification_statistics()
            
            if 'error' not in stats:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📤 Totale Notifiche", stats['total_notifications'])
                
                with col2:
                    st.metric("✅ Successi", stats['successful_notifications'])
                
                with col3:
                    st.metric("❌ Errori", stats['failed_notifications'])
                
                with col4:
                    st.metric("📊 Success Rate", f"{stats['success_rate']}%")
                
                # Tipo più comune
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"🔥 **Tipo Più Comune**: {stats['most_common_type']}")
                
                with col2:
                    st.info(f"⏰ **Ultima Notifica**: {stats['last_notification']}")
                    
            else:
                st.error(f"❌ Errore recupero statistiche: {stats['error']}")
                
        except Exception as e:
            st.error(f"❌ Errore statistiche: {e}")
    
    def _render_statistics_tab(self):
        """Rende il tab statistiche"""
        st.subheader("📈 Statistiche Dettagliate")
        
        if not self.supabase_manager:
            st.error("❌ SupabaseManager non disponibile")
            return
        
        try:
            # Recupera log degli ultimi 30 giorni
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            response = self.supabase_manager.supabase.table('notification_logs').select('*').gte('sent_at', thirty_days_ago).execute()
            
            if not response.data:
                st.info("📋 Nessun log di notifiche trovato negli ultimi 30 giorni")
                return
            
            logs_df = pd.DataFrame(response.data)
            
            # Grafico notifiche per giorno
            st.subheader("📅 Notifiche per Giorno")
            
            logs_df['date'] = pd.to_datetime(logs_df['sent_at']).dt.date
            daily_counts = logs_df.groupby('date').size().reset_index(name='count')
            
            fig_daily = px.line(daily_counts, x='date', y='count', 
                              title='Notifiche Inviate per Giorno',
                              labels={'date': 'Data', 'count': 'Numero Notifiche'})
            fig_daily.update_layout(height=400)
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Grafico notifiche per tipo
            st.subheader("📊 Notifiche per Tipo")
            
            type_counts = logs_df['notification_type'].value_counts().reset_index()
            type_counts.columns = ['Tipo', 'Conteggio']
            
            fig_type = px.pie(type_counts, values='Conteggio', names='Tipo',
                             title='Distribuzione Notifiche per Tipo')
            fig_type.update_layout(height=400)
            st.plotly_chart(fig_type, use_container_width=True)
            
            # Grafico success rate per tipo
            st.subheader("📈 Success Rate per Tipo")
            
            success_by_type = logs_df.groupby('notification_type').agg({
                'status': lambda x: (x == 'sent').sum() / len(x) * 100
            }).reset_index()
            success_by_type.columns = ['Tipo', 'Success Rate']
            
            fig_success = px.bar(success_by_type, x='Tipo', y='Success Rate',
                               title='Success Rate per Tipo di Notifica',
                               labels={'Success Rate': 'Success Rate (%)'})
            fig_success.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_success, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Errore recupero statistiche: {e}")
            logger.error(f"❌ Errore statistiche dashboard: {e}")
    
    def _render_logs_tab(self):
        """Rende il tab log dettagliati"""
        st.subheader("📝 Log Notifiche Dettagliati")
        
        if not self.telegram_manager:
            st.error("❌ TelegramManager non disponibile")
            return
        
        # Filtri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            limit = st.selectbox("Numero Log", [10, 25, 50, 100], index=2)
        
        with col2:
            status_filter = st.selectbox("Filtro Stato", ["Tutti", "Successo", "Errore"], index=0)
        
        with col3:
            if st.button("🔄 Aggiorna Log"):
                st.rerun()
        
        # Recupera log
        try:
            logs = self.telegram_manager.get_notification_logs(limit=limit)
            
            if not logs:
                st.info("📋 Nessun log di notifiche trovato")
                return
            
            # Applica filtri
            if status_filter == "Successo":
                logs = [log for log in logs if log.get('status') == 'sent']
            elif status_filter == "Errore":
                logs = [log for log in logs if log.get('status') != 'sent']
            
            # Mostra log in tabella
            log_data = []
            for log in logs:
                log_data.append({
                    'Data': log.get('sent_at', 'N/A')[:19],
                    'Tipo': log.get('notification_type', 'N/A'),
                    'Stato': '✅ Successo' if log.get('status') == 'sent' else '❌ Errore',
                    'Messaggio': log.get('message', 'N/A')[:50] + '...' if len(log.get('message', '')) > 50 else log.get('message', 'N/A'),
                    'Errore': log.get('error_message', 'N/A')[:30] + '...' if len(log.get('error_message', '')) > 30 else log.get('error_message', 'N/A')
                })
            
            st.dataframe(log_data, use_container_width=True)
            
            # Statistiche filtri
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            total_logs = len(logs)
            successful_logs = sum(1 for log in logs if log.get('status') == 'sent')
            failed_logs = total_logs - successful_logs
            
            with col1:
                st.metric("📊 Totale Log", total_logs)
            
            with col2:
                st.metric("✅ Successi", successful_logs)
            
            with col3:
                st.metric("❌ Errori", failed_logs)
                
        except Exception as e:
            st.error(f"❌ Errore recupero log: {e}")
            logger.error(f"❌ Errore log dashboard: {e}")
    
    def _render_settings_tab(self):
        """Rende il tab impostazioni"""
        st.subheader("⚙️ Impostazioni Dashboard")
        
        # Test connessione
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test Connessione", use_container_width=True):
                if self.telegram_manager:
                    success, message = self.telegram_manager.test_connection()
                    if success:
                        st.success("✅ Connessione OK")
                    else:
                        st.error(f"❌ Errore: {message}")
                else:
                    st.error("❌ TelegramManager non disponibile")
        
        with col2:
            if st.button("📤 Invia Test", use_container_width=True):
                if self.telegram_manager:
                    test_message = f"🧪 **TEST DASHBOARD**\n\nTest inviato dalla dashboard notifiche\n\n⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    success, message = self.telegram_manager.send_message(test_message)
                    if success:
                        st.success("✅ Test inviato")
                    else:
                        st.error(f"❌ Errore: {message}")
                else:
                    st.error("❌ TelegramManager non disponibile")
        
        with col3:
            if st.button("🔄 Refresh Stats", use_container_width=True):
                st.rerun()
        
        # Informazioni sistema
        st.markdown("---")
        st.subheader("ℹ️ Informazioni Sistema")
        
        if self.telegram_manager:
            status = self.telegram_manager.get_status()
            
            info_data = {
                'Configurazione': '✅ Configurato' if status['is_configured'] else '❌ Non Configurato',
                'Bot Token': '✅ Impostato' if status['bot_token_set'] else '❌ Mancante',
                'Chat ID': '✅ Impostato' if status['chat_id_set'] else '❌ Mancante',
                'Database': '✅ Disponibile' if status['supabase_available'] else '❌ Errore'
            }
            
            for key, value in info_data.items():
                st.info(f"**{key}**: {value}")
        
        # Pulsante per aprire impostazioni Telegram
        st.markdown("---")
        st.subheader("🔧 Configurazione")
        
        if st.button("⚙️ Apri Impostazioni Telegram", use_container_width=True):
            st.info("💡 Vai alla sezione 'Impostazioni' → 'Tab Telegram' per configurare il bot")
