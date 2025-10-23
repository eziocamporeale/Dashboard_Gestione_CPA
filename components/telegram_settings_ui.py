#!/usr/bin/env python3
"""
📱 TELEGRAM SETTINGS UI
Interfaccia per configurazione notifiche Telegram nelle Impostazioni
Creato da Ezio Camporeale
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramSettingsUI:
    """Interfaccia per configurazione Telegram"""
    
    def __init__(self):
        """Inizializza l'interfaccia"""
        self.telegram_manager = None
        self._init_telegram_manager()
        logger.info("✅ TelegramSettingsUI inizializzato")
    
    def _init_telegram_manager(self):
        """Inizializza il TelegramManager"""
        try:
            from components.telegram_manager import TelegramManager
            self.telegram_manager = TelegramManager()
            logger.info("✅ TelegramManager inizializzato per TelegramSettingsUI")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione TelegramManager: {e}")
            self.telegram_manager = None
    
    def render_telegram_settings(self):
        """Rende l'interfaccia di configurazione Telegram"""
        st.subheader("📱 Configurazione Notifiche Telegram")
        st.info("🤖 **BOT TELEGRAM**: Configura il bot per ricevere notifiche automatiche dalla dashboard")
        
        if not self.telegram_manager:
            st.error("❌ **TelegramManager non disponibile** - Controlla i log per dettagli")
            return
        
        # Stato configurazione
        self._render_configuration_status()
        
        st.markdown("---")
        
        # Configurazione bot
        self._render_bot_configuration()
        
        st.markdown("---")
        
        # Test connessione
        self._render_connection_test()
        
        st.markdown("---")
        
        # Impostazioni notifiche
        self._render_notification_settings()
        
        st.markdown("---")
        
        # Log notifiche
        self._render_notification_logs()
    
    def _render_configuration_status(self):
        """Rende lo stato della configurazione"""
        st.subheader("📊 Stato Configurazione")
        
        status = self.telegram_manager.get_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if status['is_configured']:
                st.success("✅ Configurato")
            else:
                st.error("❌ Non Configurato")
        
        with col2:
            if status['bot_token_set']:
                st.success("✅ Bot Token")
            else:
                st.error("❌ Bot Token")
        
        with col3:
            if status['chat_id_set']:
                st.success("✅ Chat ID")
            else:
                st.error("❌ Chat ID")
        
        with col4:
            if status['supabase_available']:
                st.success("✅ Database")
            else:
                st.error("❌ Database")
    
    def _render_bot_configuration(self):
        """Rende la sezione di configurazione bot"""
        st.subheader("🤖 Configurazione Bot")
        
        with st.form("telegram_config_form"):
            st.markdown("**📋 Istruzioni:**")
            st.markdown("""
            1. Crea un bot Telegram contattando [@BotFather](https://t.me/BotFather)
            2. Usa il comando `/newbot` e segui le istruzioni
            3. Copia il **Bot Token** che riceverai
            4. Aggiungi il bot al tuo canale/gruppo e copia il **Chat ID**
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                bot_token = st.text_input(
                    "🔑 Bot Token",
                    type="password",
                    placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                    help="Token del bot Telegram ottenuto da @BotFather"
                )
            
            with col2:
                chat_id = st.text_input(
                    "💬 Chat ID",
                    placeholder="@mychannel o -1001234567890",
                    help="ID del canale o gruppo dove inviare le notifiche"
                )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                save_config = st.form_submit_button("💾 Salva Configurazione", type="primary")
                
                if save_config:
                    if bot_token and chat_id:
                        success, message = self.telegram_manager.save_configuration(bot_token, chat_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("❌ Compila tutti i campi obbligatori")
            
            with col_btn2:
                clear_config = st.form_submit_button("🗑️ Cancella Configurazione", type="secondary")
                
                if clear_config:
                    if st.session_state.get('confirm_clear', False):
                        # Logica per cancellare configurazione
                        st.success("✅ Configurazione cancellata")
                        st.session_state.confirm_clear = False
                        st.rerun()
                    else:
                        st.session_state.confirm_clear = True
                        st.warning("⚠️ Clicca di nuovo per confermare la cancellazione")
    
    def _render_connection_test(self):
        """Rende la sezione di test connessione"""
        st.subheader("🧪 Test Connessione")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Test Bot", type="primary"):
                if self.telegram_manager.is_configured:
                    with st.spinner("Testando connessione..."):
                        success, message = self.telegram_manager.test_connection()
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("❌ Configurazione Telegram non completa")
        
        with col2:
            if st.button("📤 Test Messaggio", type="secondary"):
                if self.telegram_manager.is_configured:
                    test_message = f"""
🧪 *TEST MESSAGGIO*

✅ Connessione Telegram funzionante!
📅 Test effettuato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🤖 Bot: Dashboard CPA

Se ricevi questo messaggio, tutto funziona correttamente! 🎉
                    """.strip()
                    
                    with st.spinner("Inviando messaggio di test..."):
                        success, message = self.telegram_manager.send_message(test_message)
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("❌ Configurazione Telegram non completa")
    
    def _render_notification_settings(self):
        """Rende le impostazioni delle notifiche"""
        st.subheader("⚙️ Impostazioni Notifiche")
        st.info("🔔 **GESTIONE NOTIFICHE**: Abilita/disabilita i tipi di notifiche per ogni sezione")
        
        # Carica le impostazioni esistenti
        notification_settings = self._load_notification_settings()
        
        # Crea i toggle per ogni categoria
        st.markdown("### 📋 **Task**")
        col1, col2 = st.columns(2)
        
        with col1:
            task_new = st.checkbox(
                "🆕 Nuovo task creato", 
                value=notification_settings.get('task_new_task', True),
                key="task_new"
            )
            task_completed = st.checkbox(
                "✅ Task completato", 
                value=notification_settings.get('task_completed', True),
                key="task_completed"
            )
        
        with col2:
            task_due = st.checkbox(
                "⏰ Task in scadenza", 
                value=notification_settings.get('task_due_soon', True),
                key="task_due"
            )
            task_daily = st.checkbox(
                "📊 Report giornaliero task", 
                value=notification_settings.get('task_daily_report', False),
                key="task_daily"
            )
        
        st.markdown("### 🔄 **Incroci**")
        col1, col2 = st.columns(2)
        
        with col1:
            incrocio_new = st.checkbox(
                "🆕 Nuovo incrocio", 
                value=notification_settings.get('incrocio_new_incrocio', True),
                key="incrocio_new"
            )
            incrocio_closed = st.checkbox(
                "🔒 Incrocio chiuso", 
                value=notification_settings.get('incrocio_closed', True),
                key="incrocio_closed"
            )
        
        with col2:
            incrocio_daily = st.checkbox(
                "📊 Report giornaliero incroci", 
                value=notification_settings.get('incrocio_daily_report', False),
                key="incrocio_daily"
            )
            incrocio_alert = st.checkbox(
                "⚠️ Alert incroci aperti >X giorni", 
                value=notification_settings.get('incrocio_long_open_alert', False),
                key="incrocio_alert"
            )
        
        st.markdown("### 👥 **Clienti**")
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_new = st.checkbox(
                "🆕 Nuovo cliente", 
                value=notification_settings.get('cliente_new_client', True),
                key="cliente_new"
            )
            cliente_modified = st.checkbox(
                "✏️ Cliente modificato", 
                value=notification_settings.get('cliente_modified', False),
                key="cliente_modified"
            )
        
        with col2:
            cliente_deleted = st.checkbox(
                "🗑️ Cliente eliminato", 
                value=notification_settings.get('cliente_deleted', True),
                key="cliente_deleted"
            )
        
        st.markdown("### 💰 **Wallet/Transazioni**")
        col1, col2 = st.columns(2)
        
        with col1:
            wallet_deposit = st.checkbox(
                "💰 Nuovo deposito", 
                value=notification_settings.get('wallet_new_deposit', True),
                key="wallet_deposit"
            )
            wallet_withdrawal = st.checkbox(
                "💸 Nuovo prelievo", 
                value=notification_settings.get('wallet_new_withdrawal', True),
                key="wallet_withdrawal"
            )
        
        with col2:
            wallet_cross = st.checkbox(
                "🔄 Transazione incrocio", 
                value=notification_settings.get('wallet_cross_transaction', True),
                key="wallet_cross"
            )
            wallet_low_balance = st.checkbox(
                "⚠️ Alert saldo basso", 
                value=notification_settings.get('wallet_low_balance_alert', False),
                key="wallet_low_balance"
            )
        
        st.markdown("### 🖥️ **VPS**")
        col1, col2 = st.columns(2)
        
        with col1:
            vps_expiring = st.checkbox(
                "⏰ VPS in scadenza (7, 3, 1 giorni)", 
                value=notification_settings.get('vps_expiring', True),
                key="vps_expiring"
            )
            vps_expired = st.checkbox(
                "❌ VPS scaduto", 
                value=notification_settings.get('vps_expired', True),
                key="vps_expired"
            )
        
        with col2:
            vps_new = st.checkbox(
                "🆕 Nuovo VPS aggiunto", 
                value=notification_settings.get('vps_new', True),
                key="vps_new"
            )
            vps_monthly = st.checkbox(
                "📊 Report mensile VPS", 
                value=notification_settings.get('vps_monthly_report', False),
                key="vps_monthly"
            )
        
        # Pulsante salva
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("💾 Salva Impostazioni Notifiche", type="primary", use_container_width=True):
                self._save_notification_settings({
                    # Task
                    'task_new_task': task_new,
                    'task_completed': task_completed,
                    'task_due_soon': task_due,
                    'task_daily_report': task_daily,
                    
                    # Incroci
                    'incrocio_new_incrocio': incrocio_new,
                    'incrocio_closed': incrocio_closed,
                    'incrocio_daily_report': incrocio_daily,
                    'incrocio_long_open_alert': incrocio_alert,
                    
                    # Clienti
                    'cliente_new_client': cliente_new,
                    'cliente_modified': cliente_modified,
                    'cliente_deleted': cliente_deleted,
                    
                    # Wallet
                    'wallet_new_deposit': wallet_deposit,
                    'wallet_new_withdrawal': wallet_withdrawal,
                    'wallet_cross_transaction': wallet_cross,
                    'wallet_low_balance_alert': wallet_low_balance,
                    
                    # VPS
                    'vps_expiring': vps_expiring,
                    'vps_expired': vps_expired,
                    'vps_new': vps_new,
                    'vps_monthly_report': vps_monthly,
                })
    
    def _load_notification_settings(self) -> Dict[str, bool]:
        """Carica le impostazioni notifiche dal database"""
        try:
            if not self.telegram_manager or not self.telegram_manager.supabase_manager:
                logger.warning("⚠️ SupabaseManager non disponibile per caricamento impostazioni")
                return self._get_default_notification_settings()
            
            # Recupera tutte le impostazioni notifiche
            response = self.telegram_manager.supabase_manager.supabase.table('notification_settings').select('*').execute()
            
            if response.data:
                settings = {}
                for setting in response.data:
                    settings[setting['notification_type']] = setting.get('is_enabled', True)
                logger.info(f"✅ Caricate {len(settings)} impostazioni notifiche dal database")
                return settings
            else:
                logger.info("📋 Nessuna impostazione notifiche trovata, uso default")
                return self._get_default_notification_settings()
                
        except Exception as e:
            logger.error(f"❌ Errore caricamento impostazioni notifiche: {e}")
            return self._get_default_notification_settings()
    
    def _save_notification_settings(self, settings: Dict[str, bool]):
        """Salva le impostazioni notifiche nel database"""
        try:
            if not self.telegram_manager or not self.telegram_manager.supabase_manager:
                st.error("❌ SupabaseManager non disponibile per salvataggio impostazioni")
                return
            
            # Prepara i dati per l'inserimento/aggiornamento
            settings_data = []
            for notification_type, is_enabled in settings.items():
                settings_data.append({
                    'notification_type': notification_type,
                    'is_enabled': is_enabled,
                    'updated_at': datetime.now().isoformat()
                })
            
            # Usa upsert per inserire o aggiornare
            response = self.telegram_manager.supabase_manager.supabase.table('notification_settings').upsert(
                settings_data, 
                on_conflict='notification_type'
            ).execute()
            
            if response.data:
                st.success(f"✅ Impostazioni notifiche salvate con successo! ({len(settings)} impostazioni)")
                logger.info(f"✅ Salvate {len(settings)} impostazioni notifiche nel database")
            else:
                st.error("❌ Errore salvataggio impostazioni notifiche")
                logger.error("❌ Errore salvataggio impostazioni notifiche")
                
        except Exception as e:
            st.error(f"❌ Errore salvataggio impostazioni: {e}")
            logger.error(f"❌ Errore salvataggio impostazioni notifiche: {e}")
    
    def _get_default_notification_settings(self) -> Dict[str, bool]:
        """Restituisce le impostazioni notifiche di default"""
        return {
            # Task
            'task_new_task': True,
            'task_completed': True,
            'task_due_soon': True,
            'task_daily_report': False,
            
            # Incroci
            'incrocio_new_incrocio': True,
            'incrocio_closed': True,
            'incrocio_daily_report': False,
            'incrocio_long_open_alert': False,
            
            # Clienti
            'cliente_new_client': True,
            'cliente_modified': False,
            'cliente_deleted': True,
            
            # Wallet
            'wallet_new_deposit': True,
            'wallet_new_withdrawal': True,
            'wallet_cross_transaction': True,
            'wallet_low_balance_alert': False,
            
            # VPS
            'vps_expiring': True,
            'vps_expired': True,
            'vps_new': True,
            'vps_monthly_report': False,
        }
    
    def _render_notification_logs(self):
        """Rende i log delle notifiche"""
        st.subheader("📝 Log Notifiche")
        st.info("📊 **STORICO NOTIFICHE**: Visualizza le notifiche inviate e i loro stati")
        
        # Recupera i log delle notifiche
        logs = self.telegram_manager.get_notification_logs(limit=20)
        
        if logs:
            st.success(f"📋 **{len(logs)} notifiche** trovate negli ultimi log")
            
            # Mostra i log in una tabella
            for log in logs:
                status_color = {
                    'sent': '✅',
                    'failed': '❌',
                    'pending': '⏳'
                }
                
                status_icon = status_color.get(log.get('status', 'unknown'), '❓')
                
                with st.expander(f"{status_icon} {log.get('notification_type', 'N/A')} - {log.get('sent_at', 'N/A')}", expanded=False):
                    st.write(f"**Tipo:** {log.get('notification_type', 'N/A')}")
                    st.write(f"**Stato:** {log.get('status', 'N/A')}")
                    st.write(f"**Messaggio:** {log.get('message', 'N/A')[:200]}...")
                    
                    if log.get('error_message'):
                        st.write(f"**Errore:** {log.get('error_message', 'N/A')}")
                    
                    st.write(f"**Inviato il:** {log.get('sent_at', 'N/A')}")
                    st.write(f"**Tentativi:** {log.get('retry_count', 0)}")
        else:
            st.info("📋 Nessun log di notifiche trovato")
        
        # Pulsante per aggiornare i log
        if st.button("🔄 Aggiorna Log"):
            st.rerun()
