import streamlit as st
import pandas as pd
from datetime import datetime

class ClientTable:
    def __init__(self):
        """Inizializza la tabella dei clienti"""
        pass
    
    def render_table(self, df_clienti, on_edit=None, on_delete=None):
        """Rende la tabella dei clienti con opzioni di modifica ed eliminazione"""
        
        if df_clienti.empty:
            st.info("Nessun cliente presente nel database. Aggiungi il primo cliente!")
            return
        
        # Formattazione della tabella per una migliore visualizzazione
        df_display = df_clienti.copy()
        
        # Formattazione delle colonne
        if 'data_registrazione' in df_display.columns:
            df_display['data_registrazione'] = pd.to_datetime(df_display['data_registrazione']).dt.strftime('%d/%m/%Y')
        
        if 'deposito' in df_display.columns:
            df_display['deposito'] = df_display['deposito'].apply(lambda x: f"€{x:,.2f}")
        
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
            use_container_width=True,
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
            if st.button("📊 Esporta", help="Esporta i dati filtrati in formato CSV", use_container_width=True):
                csv = df_filtrato.to_csv(index=False)
                st.download_button(
                    label="💾 CSV",
                    data=csv,
                    file_name=f"clienti_cpa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col_azione2:
            if st.button("🔄 Aggiorna", help="Aggiorna i dati dalla tabella", use_container_width=True):
                st.rerun()
        
        with col_azione3:
            if st.button("📈 Grafici", help="Mostra grafici riassuntivi", use_container_width=True):
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
                    st.write(f"**Deposito:** €{cliente_dettagli['deposito']:,.2f}")
                
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
                    # Chiave unica con timestamp per modifica
                    import time
                    timestamp = int(time.time() * 1000)  # Millisecondi per unicità
                    unique_edit_key = f"edit_btn_{cliente_dettagli['id']}_{timestamp}_{id(st.session_state)}"
                    if st.button("✏️ Modifica", key=unique_edit_key, help="Modifica cliente", use_container_width=True):
                        if on_edit:
                            on_edit(cliente_dettagli)
                
                with col_btn2:
                    # Chiave unica con timestamp per eliminazione
                    timestamp = int(time.time() * 1000)  # Millisecondi per unicità
                    unique_delete_key = f"delete_btn_{cliente_dettagli['id']}_{timestamp}_{id(st.session_state)}"
                    if st.button("🗑️ Elimina", key=unique_delete_key, type="secondary", help="Elimina cliente", use_container_width=True):
                        if on_delete:
                            on_delete(cliente_dettagli['id'])
                
                with col_btn3:
                    # Chiave unica con timestamp per copia
                    timestamp = int(time.time() * 1000)  # Millisecondi per unicità
                    unique_copy_key = f"copy_btn_{cliente_dettagli['id']}_{timestamp}_{id(st.session_state)}"
                    if st.button("📋 Copia Dati", key=unique_copy_key, help="Copia dati", use_container_width=True):
                        # Copia i dati negli appunti (simulato)
                        st.success("Dati copiati negli appunti!")
