"""
🎯 VPS UI - Interfaccia Utente Gestione VPS
🔒 Interfaccia completa per monitoraggio e gestione server VPS
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from components.vps_manager import VPSManager
from utils.translations import t

class VPSUI:
    """Interfaccia utente per la gestione VPS"""
    
    def __init__(self):
        """Inizializza l'interfaccia VPS"""
        self.vps_manager = VPSManager()
    
    def render_vps_dashboard(self):
        """Rende il dashboard principale VPS"""
        st.title("🖥️ Gestione VPS")
        st.markdown("---")
        
        # Statistiche principali
        self._render_vps_statistics()
        
        # Tabs per diverse funzionalità
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Tutti i VPS", 
            "⚠️ Scadenze", 
            "✏️ Gestione", 
            "📈 Analisi"
        ])
        
        with tab1:
            self._render_all_vps_tab()
        
        with tab2:
            self._render_expiring_vps_tab()
        
        with tab3:
            self._render_vps_management_tab()
        
        with tab4:
            self._render_vps_analytics_tab()
    
    def _render_vps_statistics(self):
        """Rende le statistiche principali VPS"""
        try:
            stats = self.vps_manager.get_vps_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🖥️ Totale VPS",
                    value=stats['totale_vps'],
                    help="Numero totale di server VPS attivi"
                )
            
            with col2:
                st.metric(
                    label="⚠️ Scadenti (30g)",
                    value=stats['vps_scadenti_30_giorni'],
                    delta=f"-{stats['vps_scadenti_30_giorni']}" if stats['vps_scadenti_30_giorni'] > 0 else None,
                    help="VPS che scadono nei prossimi 30 giorni"
                )
            
            with col3:
                st.metric(
                    label="🚨 Urgenti (7g)",
                    value=stats['vps_scadenti_7_giorni'],
                    delta=f"-{stats['vps_scadenti_7_giorni']}" if stats['vps_scadenti_7_giorni'] > 0 else None,
                    help="VPS che scadono nei prossimi 7 giorni"
                )
            
            with col4:
                st.metric(
                    label="💰 Costo Mensile",
                    value=f"€{stats['costo_totale_mensile']:.2f}",
                    help="Costo totale mensile di tutti i VPS"
                )
                
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
    
    def _render_all_vps_tab(self):
        """Rende la tab con tutti i VPS"""
        st.subheader("📊 Tutti i VPS Attivi")
        
        try:
            all_vps = self.vps_manager.get_all_vps()
            
            if not all_vps:
                st.info("ℹ️ Nessun VPS trovato nel database")
                return
            
            # Crea DataFrame per visualizzazione
            df = pd.DataFrame(all_vps)
            
            # Filtri
            col1, col2, col3 = st.columns(3)
            
            with col1:
                broker_filter = st.selectbox(
                    "Filtra per Broker",
                    ["Tutti"] + sorted(df['broker'].unique().tolist())
                )
            
            with col2:
                expiring_filter = st.selectbox(
                    "Filtra per Scadenza",
                    ["Tutti", "In Scadenza (30g)", "In Scadenza (7g)", "Senza Data"]
                )
            
            with col3:
                search_term = st.text_input("🔍 Cerca Cliente", placeholder="Nome cliente...")
            
            # Applica filtri
            filtered_df = df.copy()
            
            if broker_filter != "Tutti":
                filtered_df = filtered_df[filtered_df['broker'] == broker_filter]
            
            if expiring_filter == "In Scadenza (30g)":
                expiring_vps = self.vps_manager.get_vps_expiring_soon(30)
                expiring_ids = [vps['id'] for vps in expiring_vps]
                filtered_df = filtered_df[filtered_df['id'].isin(expiring_ids)]
            elif expiring_filter == "In Scadenza (7g)":
                expiring_vps = self.vps_manager.get_vps_expiring_soon(7)
                expiring_ids = [vps['id'] for vps in expiring_vps]
                filtered_df = filtered_df[filtered_df['id'].isin(expiring_ids)]
            elif expiring_filter == "Senza Data":
                filtered_df = filtered_df[filtered_df['data_rinnovo'].isna() | (filtered_df['data_rinnovo'] == '')]
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['nome_cliente'].str.contains(search_term, case=False, na=False)
                ]
            
            # Visualizza tabella
            if not filtered_df.empty:
                # Seleziona colonne da mostrare
                display_columns = [
                    'nome_cliente', 'broker', 'vps_ip', 'vps_username', 
                    'data_rinnovo', 'prezzo_vps'
                ]
                
                # Mantieni solo colonne esistenti
                available_columns = [col for col in display_columns if col in filtered_df.columns]
                display_df = filtered_df[available_columns].copy()
                
                # Formatta colonne
                if 'prezzo_vps' in display_df.columns:
                    display_df['prezzo_vps'] = display_df['prezzo_vps'].apply(
                        lambda x: f"€{x:.2f}" if pd.notna(x) and x != 0 else "N/A"
                    )
                
                # Mostra tabella
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'nome_cliente': 'Cliente',
                        'broker': 'Broker',
                        'vps_ip': 'IP VPS',
                        'vps_username': 'Username',
                        'data_rinnovo': 'Data Rinnovo',
                        'prezzo_vps': 'Prezzo'
                    }
                )
                
                # Pulsante esportazione
                if st.button("📥 Esporta CSV"):
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Scarica CSV",
                        data=csv,
                        file_name=f"vps_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("ℹ️ Nessun VPS trovato con i filtri selezionati")
                
        except Exception as e:
            st.error(f"❌ Errore caricamento VPS: {e}")
    
    def _render_expiring_vps_tab(self):
        """Rende la tab con VPS in scadenza"""
        st.subheader("⚠️ VPS in Scadenza")
        
        try:
            # VPS in scadenza nei prossimi 30 giorni
            expiring_30 = self.vps_manager.get_vps_expiring_soon(30)
            
            if not expiring_30:
                st.success("✅ Nessun VPS in scadenza nei prossimi 30 giorni!")
                return
            
            # Raggruppa per urgenza
            urgent_vps = [vps for vps in expiring_30 if vps.get('giorni_rimanenti', 0) <= 7]
            warning_vps = [vps for vps in expiring_30 if 7 < vps.get('giorni_rimanenti', 0) <= 15]
            normal_vps = [vps for vps in expiring_30 if vps.get('giorni_rimanenti', 0) > 15]
            
            # VPS Urgenti (≤ 7 giorni)
            if urgent_vps:
                st.error(f"🚨 VPS URGENTI - Scadenza entro 7 giorni ({len(urgent_vps)})")
                self._render_expiring_vps_list(urgent_vps, "urgent")
            
            # VPS Warning (8-15 giorni)
            if warning_vps:
                st.warning(f"⚠️ VPS ATTENZIONE - Scadenza 8-15 giorni ({len(warning_vps)})")
                self._render_expiring_vps_list(warning_vps, "warning")
            
            # VPS Normali (16-30 giorni)
            if normal_vps:
                st.info(f"ℹ️ VPS MONITORAGGIO - Scadenza 16-30 giorni ({len(normal_vps)})")
                self._render_expiring_vps_list(normal_vps, "normal")
                
        except Exception as e:
            st.error(f"❌ Errore caricamento VPS in scadenza: {e}")
    
    def _render_expiring_vps_list(self, vps_list: List[Dict], urgency_level: str):
        """Rende la lista di VPS in scadenza"""
        if not vps_list:
            return
        
        for vps in vps_list:
            with st.expander(f"🖥️ {vps['nome_cliente']} - {vps['giorni_rimanenti']} giorni rimanenti"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Broker:** {vps['broker']}")
                    st.write(f"**IP VPS:** {vps['vps_ip']}")
                    st.write(f"**Username:** {vps['vps_username']}")
                
                with col2:
                    st.write(f"**Email:** {vps['email']}")
                    st.write(f"**Data Scadenza:** {vps['data_rinnovo']}")
                    st.write(f"**Prezzo:** €{vps.get('prezzo_vps', 0):.2f}")
                
                # Azioni rapide
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(f"✏️ Modifica", key=f"edit_{vps['id']}"):
                        st.session_state[f"edit_vps_{vps['id']}"] = True
                        st.rerun()
                
                with col_btn2:
                    if st.button(f"📧 Contatta", key=f"contact_{vps['id']}"):
                        st.write(f"📧 Email: {vps['email']}")
                
                with col_btn3:
                    if st.button(f"🔄 Rinnova", key=f"renew_{vps['id']}"):
                        st.session_state[f"renew_vps_{vps['id']}"] = True
                        st.rerun()
    
    def _render_vps_management_tab(self):
        """Rende la tab di gestione VPS"""
        st.subheader("✏️ Gestione VPS")
        
        # Seleziona cliente da modificare
        all_vps = self.vps_manager.get_all_vps()
        
        if not all_vps:
            st.info("ℹ️ Nessun VPS disponibile per la modifica")
            return
        
        # Lista clienti con VPS
        cliente_options = {f"{vps['nome_cliente']} ({vps['broker']})": vps for vps in all_vps}
        selected_cliente = st.selectbox(
            "Seleziona Cliente da Modificare",
            options=list(cliente_options.keys())
        )
        
        if selected_cliente:
            vps_data = cliente_options[selected_cliente]
            
            st.markdown("---")
            st.subheader(f"✏️ Modifica VPS - {vps_data['nome_cliente']}")
            
            # Form di modifica
            with st.form(f"edit_vps_form_{vps_data['id']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    vps_ip = st.text_input(
                        "IP VPS",
                        value=vps_data.get('vps_ip', ''),
                        help="Indirizzo IP del server VPS"
                    )
                    
                    vps_username = st.text_input(
                        "Username VPS",
                        value=vps_data.get('vps_username', ''),
                        help="Username per l'accesso al VPS"
                    )
                    
                    vps_password = st.text_input(
                        "Password VPS",
                        value=vps_data.get('vps_password', ''),
                        type="password",
                        help="Password per l'accesso al VPS"
                    )
                
                with col2:
                    data_rinnovo = st.date_input(
                        "Data Rinnovo",
                        value=datetime.strptime(vps_data.get('data_rinnovo', datetime.now().date()), '%Y-%m-%d').date() if vps_data.get('data_rinnovo') else datetime.now().date(),
                        help="Data di scadenza/rinnovo del VPS"
                    )
                    
                    prezzo_vps = st.number_input(
                        "Prezzo VPS (€/mese)",
                        value=float(vps_data.get('prezzo_vps', 0)) if vps_data.get('prezzo_vps') else 0.0,
                        min_value=0.0,
                        step=0.01,
                        help="Costo mensile del VPS"
                    )
                
                # Pulsanti azione
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.form_submit_button("💾 Salva Modifiche", type="primary"):
                        # Prepara dati per l'aggiornamento
                        update_data = {
                            'vps_ip': vps_ip,
                            'vps_username': vps_username,
                            'vps_password': vps_password,
                            'data_rinnovo': data_rinnovo.isoformat(),
                            'prezzo_vps': prezzo_vps
                        }
                        
                        # Aggiorna VPS
                        if self.vps_manager.update_vps_data(vps_data['id'], update_data):
                            st.success("✅ VPS aggiornato con successo!")
                            st.rerun()
                
                with col_btn2:
                    if st.form_submit_button("🗑️ Rimuovi VPS"):
                        # Rimuove i dati VPS (li azzera)
                        update_data = {
                            'vps_ip': '',
                            'vps_username': '',
                            'vps_password': '',
                            'data_rinnovo': None,
                            'prezzo_vps': 0.0
                        }
                        
                        if self.vps_manager.update_vps_data(vps_data['id'], update_data):
                            st.success("✅ VPS rimosso con successo!")
                            st.rerun()
    
    def _render_vps_analytics_tab(self):
        """Rende la tab di analisi VPS"""
        st.subheader("📈 Analisi VPS")
        
        try:
            all_vps = self.vps_manager.get_all_vps()
            
            if not all_vps:
                st.info("ℹ️ Nessun dato VPS disponibile per l'analisi")
                return
            
            df = pd.DataFrame(all_vps)
            
            # Grafici
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuzione per broker
                if 'broker' in df.columns:
                    broker_counts = df['broker'].value_counts()
                    fig_broker = px.pie(
                        values=broker_counts.values,
                        names=broker_counts.index,
                        title="Distribuzione VPS per Broker"
                    )
                    st.plotly_chart(fig_broker, use_container_width=True)
            
            with col2:
                # Costi per broker
                if 'prezzo_vps' in df.columns and 'broker' in df.columns:
                    costi_broker = df.groupby('broker')['prezzo_vps'].sum().reset_index()
                    fig_costi = px.bar(
                        costi_broker,
                        x='broker',
                        y='prezzo_vps',
                        title="Costi VPS per Broker (€/mese)",
                        labels={'prezzo_vps': 'Costo Mensile (€)', 'broker': 'Broker'}
                    )
                    st.plotly_chart(fig_costi, use_container_width=True)
            
            # Timeline scadenze
            st.subheader("📅 Timeline Scadenze")
            
            expiring_vps = self.vps_manager.get_vps_expiring_soon(90)  # Prossimi 90 giorni
            
            if expiring_vps:
                timeline_data = []
                for vps in expiring_vps:
                    timeline_data.append({
                        'Cliente': vps['nome_cliente'],
                        'Data Scadenza': vps['data_rinnovo'],
                        'Giorni Rimanenti': vps['giorni_rimanenti'],
                        'Broker': vps['broker'],
                        'Costo': vps.get('prezzo_vps', 0)
                    })
                
                timeline_df = pd.DataFrame(timeline_data)
                timeline_df = timeline_df.sort_values('Giorni Rimanenti')
                
                # Grafico timeline
                fig_timeline = px.scatter(
                    timeline_df,
                    x='Giorni Rimanenti',
                    y='Cliente',
                    color='Broker',
                    size='Costo',
                    title="Timeline Scadenze VPS (Prossimi 90 giorni)",
                    labels={'Giorni Rimanenti': 'Giorni alla Scadenza'}
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Tabella dettagliata
                st.subheader("📋 Dettaglio Scadenze")
                st.dataframe(
                    timeline_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ Nessuna scadenza VPS nei prossimi 90 giorni")
                
        except Exception as e:
            st.error(f"❌ Errore generazione analisi: {e}")
