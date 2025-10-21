"""
🔔 VPS NOTIFICATIONS - Sistema Notifiche Scadenze VPS
🔒 Sistema automatico di notifiche per monitoraggio scadenze VPS
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from components.vps_manager import VPSManager

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VPSNotifications:
    """Sistema notifiche per scadenze VPS"""
    
    def __init__(self):
        """Inizializza il sistema notifiche VPS"""
        self.vps_manager = VPSManager()
    
    def get_expiring_vps_notifications(self) -> Dict[str, List[Dict]]:
        """Recupera notifiche VPS in scadenza organizzate per urgenza"""
        try:
            notifications = {
                'critical': [],    # ≤ 7 giorni
                'warning': [],     # 8-15 giorni  
                'info': [],        # 16-30 giorni
                'upcoming': []     # 31-60 giorni
            }
            
            # Recupera VPS in scadenza nei prossimi 60 giorni
            expiring_vps = self.vps_manager.get_vps_expiring_soon(60)
            
            for vps in expiring_vps:
                giorni_rimanenti = vps.get('giorni_rimanenti', 999)
                
                # Categorizza per urgenza
                if giorni_rimanenti <= 7:
                    notifications['critical'].append(vps)
                elif giorni_rimanenti <= 15:
                    notifications['warning'].append(vps)
                elif giorni_rimanenti <= 30:
                    notifications['info'].append(vps)
                elif giorni_rimanenti <= 60:
                    notifications['upcoming'].append(vps)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Errore recupero notifiche VPS: {e}")
            return {'critical': [], 'warning': [], 'info': [], 'upcoming': []}
    
    def render_notifications_banner(self):
        """Rende il banner delle notifiche VPS nella sidebar"""
        try:
            notifications = self.get_expiring_vps_notifications()
            
            # Conta notifiche totali
            total_notifications = sum(len(notifications[key]) for key in notifications)
            
            if total_notifications == 0:
                return  # Nessuna notifica
            
            # Banner principale
            with st.sidebar:
                st.markdown("---")
                
                if notifications['critical']:
                    st.error(f"🚨 **{len(notifications['critical'])} VPS URGENTI** (≤7 giorni)")
                    
                    for vps in notifications['critical']:
                        with st.expander(f"⚠️ {vps['nome_cliente']} - {vps['giorni_rimanenti']}g"):
                            st.write(f"**IP:** {vps['vps_ip']}")
                            st.write(f"**Scadenza:** {vps['data_rinnovo']}")
                            st.write(f"**Email:** {vps['email']}")
                
                if notifications['warning']:
                    st.warning(f"⚠️ **{len(notifications['warning'])} VPS ATTENZIONE** (8-15 giorni)")
                    
                    for vps in notifications['warning']:
                        with st.expander(f"⚠️ {vps['nome_cliente']} - {vps['giorni_rimanenti']}g"):
                            st.write(f"**IP:** {vps['vps_ip']}")
                            st.write(f"**Scadenza:** {vps['data_rinnovo']}")
                            st.write(f"**Email:** {vps['email']}")
                
                if notifications['info']:
                    st.info(f"ℹ️ **{len(notifications['info'])} VPS MONITORAGGIO** (16-30 giorni)")
                
                if notifications['upcoming']:
                    st.info(f"📅 **{len(notifications['upcoming'])} VPS PROSSIMI** (31-60 giorni)")
                
                # Link rapido alla sezione VPS
                if st.button("🖥️ Vai a Gestione VPS"):
                    st.session_state.current_page = "🖥️ VPS"
                    st.rerun()
                    
        except Exception as e:
            logger.error(f"Errore rendering banner notifiche: {e}")
    
    def render_notifications_dashboard(self):
        """Rende il dashboard completo delle notifiche VPS"""
        st.title("🔔 Notifiche VPS")
        st.markdown("---")
        
        try:
            notifications = self.get_expiring_vps_notifications()
            
            # Statistiche notifiche
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🚨 Urgenti (≤7g)",
                    value=len(notifications['critical']),
                    delta=f"-{len(notifications['critical'])}" if notifications['critical'] else None
                )
            
            with col2:
                st.metric(
                    label="⚠️ Attenzione (8-15g)",
                    value=len(notifications['warning']),
                    delta=f"-{len(notifications['warning'])}" if notifications['warning'] else None
                )
            
            with col3:
                st.metric(
                    label="ℹ️ Monitoraggio (16-30g)",
                    value=len(notifications['info']),
                    delta=f"-{len(notifications['info'])}" if notifications['info'] else None
                )
            
            with col4:
                st.metric(
                    label="📅 Prossimi (31-60g)",
                    value=len(notifications['upcoming']),
                    delta=f"-{len(notifications['upcoming'])}" if notifications['upcoming'] else None
                )
            
            # Sezioni notifiche
            self._render_notification_section("🚨 VPS URGENTI - Scadenza entro 7 giorni", notifications['critical'], "error")
            self._render_notification_section("⚠️ VPS ATTENZIONE - Scadenza 8-15 giorni", notifications['warning'], "warning")
            self._render_notification_section("ℹ️ VPS MONITORAGGIO - Scadenza 16-30 giorni", notifications['info'], "info")
            self._render_notification_section("📅 VPS PROSSIMI - Scadenza 31-60 giorni", notifications['upcoming'], "info")
            
            # Azioni rapide
            st.markdown("---")
            st.subheader("🛠️ Azioni Rapide")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("📧 Invia Email Promemoria"):
                    self._send_reminder_emails(notifications)
            
            with col_btn2:
                if st.button("📊 Esporta Report Scadenze"):
                    self._export_expiring_report(notifications)
            
            with col_btn3:
                if st.button("🔄 Aggiorna Notifiche"):
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Errore caricamento notifiche: {e}")
    
    def _render_notification_section(self, title: str, vps_list: List[Dict], alert_type: str):
        """Rende una sezione di notifiche"""
        if not vps_list:
            return
        
        if alert_type == "error":
            st.error(title)
        elif alert_type == "warning":
            st.warning(title)
        else:
            st.info(title)
        
        # Tabella riassuntiva
        df_data = []
        for vps in vps_list:
            df_data.append({
                'Cliente': vps['nome_cliente'],
                'Broker': vps['broker'],
                'IP VPS': vps['vps_ip'],
                'Scadenza': vps['data_rinnovo'],
                'Giorni Rimanenti': vps['giorni_rimanenti'],
                'Email': vps['email'],
                'Prezzo': f"€{vps.get('prezzo_vps', 0):.2f}" if vps.get('prezzo_vps') else "N/A"
            })
        
        if df_data:
            import pandas as pd
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Dettagli per ogni VPS
            for vps in vps_list:
                with st.expander(f"🖥️ {vps['nome_cliente']} - {vps['giorni_rimanenti']} giorni rimanenti"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Broker:** {vps['broker']}")
                        st.write(f"**IP VPS:** {vps['vps_ip']}")
                        st.write(f"**Username:** {vps['vps_username']}")
                        st.write(f"**Email:** {vps['email']}")
                    
                    with col2:
                        st.write(f"**Data Scadenza:** {vps['data_rinnovo']}")
                        st.write(f"**Prezzo:** €{vps.get('prezzo_vps', 0):.2f}")
                        st.write(f"**Giorni Rimanenti:** {vps['giorni_rimanenti']}")
                    
                    # Azioni rapide
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button(f"✏️ Modifica VPS", key=f"edit_{vps['id']}"):
                            st.session_state.current_page = "🖥️ VPS"
                            st.session_state[f"edit_vps_{vps['id']}"] = True
                            st.rerun()
                    
                    with col_btn2:
                        if st.button(f"📧 Contatta Cliente", key=f"contact_{vps['id']}"):
                            st.write(f"📧 **Email Cliente:** {vps['email']}")
                            st.write("💡 **Messaggio suggerito:**")
                            st.text_area(
                                "Messaggio",
                                value=f"Gentile {vps['nome_cliente']},\n\nIl VPS {vps['vps_ip']} scadrà il {vps['data_rinnovo']} ({vps['giorni_rimanenti']} giorni rimanenti).\n\nPer evitare interruzioni del servizio, si prega di procedere al rinnovo.\n\nCordiali saluti,\nTeam CPA",
                                height=100,
                                key=f"message_{vps['id']}"
                            )
                    
                    with col_btn3:
                        if st.button(f"🔄 Rinnova", key=f"renew_{vps['id']}"):
                            st.session_state.current_page = "🖥️ VPS"
                            st.session_state[f"renew_vps_{vps['id']}"] = True
                            st.rerun()
    
    def _send_reminder_emails(self, notifications: Dict[str, List[Dict]]):
        """Simula invio email promemoria"""
        total_vps = sum(len(notifications[key]) for key in notifications)
        
        if total_vps == 0:
            st.info("ℹ️ Nessun VPS in scadenza per cui inviare promemoria")
            return
        
        # Simula invio email
        st.info(f"📧 **Simulazione invio email promemoria per {total_vps} VPS**")
        
        for alert_type, vps_list in notifications.items():
            if vps_list:
                alert_name = {
                    'critical': 'URGENTE',
                    'warning': 'ATTENZIONE', 
                    'info': 'MONITORAGGIO',
                    'upcoming': 'PROSSIMI'
                }.get(alert_type, 'INFO')
                
                st.write(f"📤 **{alert_name}:** {len(vps_list)} email inviate")
                
                for vps in vps_list:
                    st.write(f"  • {vps['nome_cliente']} ({vps['email']}) - {vps['giorni_rimanenti']} giorni")
        
        st.success("✅ **Simulazione completata!** In un'implementazione reale, qui verrebbero inviate le email effettive.")
    
    def _export_expiring_report(self, notifications: Dict[str, List[Dict]]):
        """Esporta report VPS in scadenza"""
        try:
            import pandas as pd
            
            # Combina tutti i VPS in scadenza
            all_expiring = []
            for alert_type, vps_list in notifications.items():
                for vps in vps_list:
                    vps['urgenza'] = alert_type
                    all_expiring.append(vps)
            
            if not all_expiring:
                st.info("ℹ️ Nessun VPS in scadenza da esportare")
                return
            
            # Crea DataFrame
            df_data = []
            for vps in all_expiring:
                df_data.append({
                    'Cliente': vps['nome_cliente'],
                    'Email': vps['email'],
                    'Broker': vps['broker'],
                    'IP VPS': vps['vps_ip'],
                    'Username': vps['vps_username'],
                    'Data Scadenza': vps['data_rinnovo'],
                    'Giorni Rimanenti': vps['giorni_rimanenti'],
                    'Urgenza': vps['urgenza'],
                    'Prezzo Mensile': vps.get('prezzo_vps', 0)
                })
            
            df = pd.DataFrame(df_data)
            
            # Esporta CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Scarica Report CSV",
                data=csv,
                file_name=f"vps_expiring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success(f"✅ Report generato per {len(all_expiring)} VPS in scadenza")
            
        except Exception as e:
            st.error(f"❌ Errore esportazione report: {e}")
    
    def get_notification_count(self) -> int:
        """Restituisce il numero totale di notifiche VPS"""
        try:
            notifications = self.get_expiring_vps_notifications()
            return sum(len(notifications[key]) for key in notifications)
        except Exception as e:
            logger.error(f"Errore conteggio notifiche: {e}")
            return 0
