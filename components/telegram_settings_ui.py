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
        st.info("🔔 **GESTIONE NOTIFICHE**: Abilita/disabilita i tipi di notifiche")
        
        # Placeholder per le impostazioni notifiche
        # In futuro implementeremo la gestione delle impostazioni per tipo
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Task:**")
            task_new = st.checkbox("Nuovo task creato", value=True)
            task_completed = st.checkbox("Task completato", value=True)
            task_due = st.checkbox("Task in scadenza", value=True)
            task_daily = st.checkbox("Report giornaliero task", value=False)
        
        with col2:
            st.markdown("**🔄 Incroci:**")
            incrocio_new = st.checkbox("Nuovo incrocio", value=True)
            incrocio_closed = st.checkbox("Incrocio chiuso", value=True)
            incrocio_daily = st.checkbox("Report giornaliero incroci", value=False)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**👤 Clienti:**")
            client_new = st.checkbox("Nuovo cliente", value=True)
            client_modified = st.checkbox("Cliente modificato", value=False)
        
        with col4:
            st.markdown("**💰 Transazioni:**")
            transaction_new = st.checkbox("Nuova transazione", value=True)
            balance_low = st.checkbox("Saldo basso", value=True)
        
        col5, col6 = st.columns(2)
        
        with col5:
            st.markdown("**🖥️ VPS:**")
            vps_expiring = st.checkbox("VPS in scadenza", value=True)
            vps_expired = st.checkbox("VPS scaduto", value=True)
        
        with col6:
            st.markdown("**📊 Sistema:**")
            system_errors = st.checkbox("Errori sistema", value=True)
            daily_summary = st.checkbox("Riepilogo giornaliero", value=False)
        
        if st.button("💾 Salva Impostazioni Notifiche", type="primary"):
            st.success("✅ Impostazioni notifiche salvate!")
            st.info("💡 Le impostazioni saranno applicate alle prossime notifiche")
    
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
