import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_manager import SupabaseManager

class ClientTable:
    def __init__(self):
        """Inizializza la tabella dei clienti con Supabase"""
        try:
            self.supabase = SupabaseManager()
            st.session_state.supabase_available = True
        except Exception as e:
            st.error(f"❌ Errore inizializzazione Supabase: {e}")
            st.session_state.supabase_available = False
    
    def get_clienti(self):
        """Recupera tutti i clienti da Supabase"""
        try:
            if not st.session_state.get('supabase_available', False):
                return pd.DataFrame()
            
            clienti = self.supabase.get_clienti()
            if not clienti:
                return pd.DataFrame()
            
            # Converti in DataFrame
            df = pd.DataFrame(clienti)
            
            # Rinomina le colonne per compatibilità
            if 'data_registrazione' not in df.columns and 'created_at' in df.columns:
                df['data_registrazione'] = df['created_at']
            
            if 'deposito' not in df.columns and 'volume_posizione' in df.columns:
                df['deposito'] = df['volume_posizione']
            
            if 'piattaforma' not in df.columns:
                df['piattaforma'] = 'MT5'  # Default
            
            if 'vps_ip' not in df.columns:
                df['vps_ip'] = ''  # Default
            
            return df
            
        except Exception as e:
            st.error(f"❌ Errore recupero clienti: {e}")
            return pd.DataFrame()
    
    def get_statistiche_clienti(self):
        """Calcola le statistiche dei clienti da Supabase"""
        try:
            if not st.session_state.get('supabase_available', False):
                return {
                    'totale_clienti': 0,
                    'broker_attivi': 0,
                    'depositi_totali': 0,
                    'cpa_attive': 0
                }
            
            clienti = self.supabase.get_clienti()
            if not clienti:
                return {
                    'totale_clienti': 0,
                    'broker_attivi': 0,
                    'depositi_totali': 0,
                    'cpa_attive': 0
                }
            
            # Converti in DataFrame per calcoli
            df = pd.DataFrame(clienti)
            
            # Calcola statistiche
            totale_clienti = len(df)
            broker_attivi = df['broker'].nunique() if 'broker' in df.columns else 0
            
            # Gestisci depositi/volume_posizione
            if 'deposito' in df.columns:
                depositi_totali = df['deposito'].sum()
            elif 'volume_posizione' in df.columns:
                depositi_totali = df['volume_posizione'].sum()
            else:
                depositi_totali = 0
            
            # CPA attive (clienti con deposito > 0)
            if 'deposito' in df.columns:
                cpa_attive = len(df[df['deposito'] > 0])
            elif 'volume_posizione' in df.columns:
                cpa_attive = len(df[df['volume_posizione'] > 0])
            else:
                cpa_attive = 0
            
            return {
                'totale_clienti': totale_clienti,
                'broker_attivi': broker_attivi,
                'depositi_totali': depositi_totali,
                'cpa_attive': cpa_attive
            }
            
        except Exception as e:
            st.error(f"❌ Errore calcolo statistiche: {e}")
            return {
                'totale_clienti': 0,
                'broker_attivi': 0,
                'depositi_totali': 0,
                'cpa_attive': 0
            }
    
    def render_table(self, df_clienti=None, on_edit=None, on_delete=None):
        """Rende la tabella dei clienti con opzioni di modifica ed eliminazione"""
        
        # Se non viene passato df_clienti, lo recupera da Supabase
        if df_clienti is None:
            df_clienti = self.get_clienti()
        
        if df_clienti.empty:
            st.info("Nessun cliente presente nel database. Aggiungi il primo cliente!")
            return
        
        # Formattazione della tabella per una migliore visualizzazione
        df_display = df_clienti.copy()
        
        # Formattazione delle colonne
        if 'data_registrazione' in df_display.columns:
            df_display['data_registrazione'] = pd.to_datetime(df_display['data_registrazione']).dt.strftime('%d/%m/%Y')
        
        if 'deposito' in df_display.columns:
            df_display['deposito'] = df_display['deposito'].apply(lambda x: f"€{x:,.2f}" if pd.notna(x) and x != 0 else "€0.00")
        
        if 'data_creazione' in df_display.columns:
            df_display['data_creazione'] = pd.to_datetime(df_display['data_creazione']).dt.strftime('%d/%m/%Y %H:%M')
        
        if 'data_modifica' in df_display.columns:
            df_display['data_modifica'] = pd.to_datetime(df_display['data_modifica']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Selezione delle colonne da mostrare
        colonne_display = [
            'id', 'nome_cliente', 'email', 'broker', 'data_registrazione', 
            'deposito', 'piattaforma', 'numero_conto', 'vps_ip'
        ]
        
        # Filtra le colonne disponibili
        colonne_disponibili = [col for col in colonne_display if col in df_display.columns]
        df_display = df_display[colonne_disponibili]
        
        # Rinomina le colonne per una migliore visualizzazione
        mapping_colonne = {
            'id': 'ID',
            'nome_cliente': 'Nome Cliente',
            'email': 'Email',
            'broker': 'Broker',
            'data_registrazione': 'Data Registrazione',
            'deposito': 'Deposito',
            'piattaforma': 'Piattaforma',
            'numero_conto': 'Numero Conto',
            'vps_ip': 'IP VPS'
        }
        
        df_display = df_display.rename(columns=mapping_colonne)
        
        # Gestione conferma eliminazione cliente (come negli incroci)
        if st.session_state.get('mostra_conferma_eliminazione_cliente', False) and st.session_state.get('cliente_da_eliminare'):
            cliente_id = st.session_state.cliente_da_eliminare
            st.warning(f"⚠️ **Attenzione**: Stai per eliminare il cliente ID {cliente_id}")
            st.info("Questa azione è irreversibile e eliminerà tutti i dati del cliente")
            
            col_confirm1, col_confirm2 = st.columns(2)
            
            with col_confirm1:
                if st.button("❌ Conferma Eliminazione", key="confirm_elimina_cliente_finale", type="primary"):
                    st.info(f"🔄 Eliminazione cliente {cliente_id} in corso...")
                    
                    # Chiama la funzione di eliminazione
                    if on_delete:
                        on_delete(cliente_id)
                        
                        # Reset dello stato
                        st.session_state.mostra_conferma_eliminazione_cliente = False
                        st.session_state.cliente_da_eliminare = None
                        
                        st.success("✅ **Eliminazione completata!** Clicca '🔄 Aggiorna' per vedere i cambiamenti.")
                        st.rerun()
            
            with col_confirm2:
                if st.button("🔙 Annulla", key="cancel_elimina_cliente_finale"):
                    # Reset dello stato
                    st.session_state.mostra_conferma_eliminazione_cliente = False
                    st.session_state.cliente_da_eliminare = None
                    st.rerun()
        
        # Filtri per la tabella
        st.subheader("🔍 Filtri")
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            filtro_nome = st.text_input("Filtra per Nome", placeholder="Nome cliente...")
        
        with col_filtro2:
            filtro_broker = st.selectbox("Filtra per Broker", 
                                       ["Tutti"] + list(df_clienti['broker'].unique()) if 'broker' in df_clienti.columns else ["Tutti"])
        
        with col_filtro3:
            filtro_piattaforma = st.selectbox("Filtra per Piattaforma", 
                                            ["Tutte"] + list(df_clienti['piattaforma'].unique()) if 'piattaforma' in df_clienti.columns else ["Tutte"])
        
        # Applicazione filtri
        df_filtrato = df_clienti.copy()
        
        if filtro_nome:
            df_filtrato = df_filtrato[df_filtrato['nome_cliente'].str.contains(filtro_nome, case=False, na=False)]
        
        if filtro_broker and filtro_broker != "Tutti":
            df_filtrato = df_filtrato[df_filtrato['broker'] == filtro_broker]
        
        if filtro_piattaforma and filtro_piattaforma != "Tutte":
            df_filtrato = df_filtrato[df_filtrato['piattaforma'] == filtro_piattaforma]
        
        # Aggiorna df_display con i dati filtrati
        df_display = df_filtrato[colonne_disponibili].rename(columns=mapping_colonne)
        
        # Mostra statistiche dei filtri
        st.write(f"**Risultati:** {len(df_filtrato)} cliente{'i' if len(df_filtrato) != 1 else ''} su {len(df_clienti)} totali")
        
        # Tabella principale
        st.subheader("📋 Tabella Clienti")
        
        # Mostra la tabella con st.dataframe per una migliore interazione
        st.dataframe(
            df_display,
            width='stretch',
            hide_index=True,
            height=300,  # Altezza fissa per compattezza
            column_config={
                "ID": st.column_config.NumberColumn("ID", width=50),
                "Nome Cliente": st.column_config.TextColumn("Nome", width=120),
                "Email": st.column_config.TextColumn("Email", width=150),
                "Broker": st.column_config.TextColumn("Broker", width=80),
                "Data Registrazione": st.column_config.TextColumn("Data", width=80),
                "Deposito": st.column_config.TextColumn("Deposito", width=80),
                "Piattaforma": st.column_config.TextColumn("Platform", width=80),
                "Numero Conto": st.column_config.TextColumn("Conto", width=80),
                "IP VPS": st.column_config.TextColumn("VPS", width=80)
            }
        )
        
        # Azioni rapide (sempre visibili)
        st.subheader("⚡ Azioni Rapide")
        
        col_azione1, col_azione2, col_azione3 = st.columns(3)
        
        with col_azione1:
            if st.button("📊 Esporta", help="Esporta i dati filtrati in formato CSV"):
                csv = df_filtrato.to_csv(index=False)
                st.download_button(
                    label="💾 CSV",
                    data=csv,
                    file_name=f"clienti_cpa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_azione2:
            if st.button("🔄 Aggiorna", help="Aggiorna i dati dalla tabella"):
                st.rerun()
        
        with col_azione3:
            if st.button("📈 Grafici", help="Mostra grafici riassuntivi"):
                st.session_state.show_charts = True
                st.rerun()
        
        # Azioni sui clienti (solo quando si seleziona un cliente)
        if len(df_filtrato) > 0:
            st.subheader("⚡ Azioni sui Clienti")
            st.info("💡 **Seleziona un cliente dalla sezione 'Dettagli Cliente' per visualizzare le azioni disponibili**")
        
        # Dettagli cliente selezionato (opzionale)
        if len(df_filtrato) > 0:
            st.subheader("👤 Dettagli Cliente")
            
            # Selezione cliente per visualizzare i dettagli
            cliente_selezionato = st.selectbox(
                "Seleziona un cliente per visualizzare i dettagli completi:",
                options=df_filtrato['nome_cliente'].tolist(),
                index=0
            )
            
            if cliente_selezionato:
                cliente_dettagli = df_filtrato[df_filtrato['nome_cliente'] == cliente_selezionato].iloc[0]
                
                # Mostra dettagli completi
                col_det1, col_det2 = st.columns(2)
                
                with col_det1:
                    st.write(f"**Nome:** {cliente_dettagli['nome_cliente']}")
                    st.write(f"**Email:** {cliente_dettagli['email']}")
                    st.write(f"**Broker:** {cliente_dettagli['broker']}")
                    st.write(f"**Data Registrazione:** {cliente_dettagli['data_registrazione']}")
                    st.write(f"**Deposito:** €{cliente_dettagli.get('deposito', 0):,.2f}" if cliente_dettagli.get('deposito') is not None else "**Deposito:** Non specificato")
                
                with col_det2:
                    st.write(f"**Piattaforma:** {cliente_dettagli['piattaforma']}")
                    st.write(f"**Numero Conto:** {cliente_dettagli['numero_conto']}")
                    st.write(f"**IP VPS:** {cliente_dettagli.get('vps_ip', 'Non specificato')}")
                    st.write(f"**Username VPS:** {cliente_dettagli.get('vps_username', 'Non specificato')}")
                
                # Campi aggiuntivi se presenti
                if 'campi_aggiuntivi' in cliente_dettagli and cliente_dettagli['campi_aggiuntivi']:
                    st.write("**Campi Aggiuntivi:**")
                    campi = cliente_dettagli['campi_aggiuntivi']
                    if isinstance(campi, str):
                        for campo in campi.split(';'):
                            if campo.strip():
                                st.write(f"• {campo.strip()}")
                
                # Pulsanti azione (visibili solo quando si seleziona un cliente)
                st.markdown("---")
                st.subheader("⚡ Azioni Disponibili")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    # Chiave semplice per modifica
                    if st.button("✏️ Modifica", key=f"edit_simple_{cliente_dettagli['id']}", help="Modifica cliente"):
                        if on_edit:
                            on_edit(cliente_dettagli)
                            st.rerun()  # Forza il refresh immediato
                
                with col_btn2:
                    # Chiave unica con timestamp per eliminazione
                    if st.button("🗑️ Elimina", key=f"delete_simple_{cliente_dettagli['id']}", type="secondary", help="Elimina cliente"):
                        if on_delete:
                            # Invece di chiamare direttamente, impostiamo lo stato come negli incroci
                            st.session_state.cliente_da_eliminare = cliente_dettagli['id']
                            st.session_state.mostra_conferma_eliminazione_cliente = True
                            st.rerun()
                
                with col_btn3:
                    # Chiave unica con timestamp per copia
                    if st.button("📋 Copia Dati", key=f"copy_simple_{cliente_dettagli['id']}", help="Copia dati"):
                        # Copia i dati negli appunti (simulato)
                        st.success("Dati copiati negli appunti!")
