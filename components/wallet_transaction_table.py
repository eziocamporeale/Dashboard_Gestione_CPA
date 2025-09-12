"""
💰 WALLET TRANSACTION TABLE
Tabella per visualizzare e gestire le transazioni wallet esistenti
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable, Optional
import plotly.express as px
import plotly.graph_objects as go

class WalletTransactionTable:
    """Tabella per la gestione delle transazioni wallet"""
    
    def __init__(self, wallet_manager):
        """Inizializza la tabella con il gestore wallet"""
        self.wallet_manager = wallet_manager
    
    def render_table(self, on_edit: Optional[Callable] = None, on_delete: Optional[Callable] = None):
        """Rende la tabella delle transazioni wallet"""
        
        # Genera un ID unico per questa istanza
        import time
        unique_id = int(time.time() * 1000) % 100000  # ID unico basato su timestamp
        
        # Ottieni transazioni
        transactions = self.wallet_manager.get_wallet_transactions(limit=100)
        
        if not transactions:
            st.info("📋 Nessuna transazione wallet presente. Crea la prima transazione usando il form sopra.")
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(transactions)
        
        # Formatta le colonne
        if not df.empty:
            # Formatta data
            df['data_transazione'] = pd.to_datetime(df['data_transazione']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Formatta importo
            df['importo_formatted'] = df.apply(lambda x: f"{x['importo']:.2f} {x['valuta']}", axis=1)
            
            # Formatta commissione
            df['commissione_formatted'] = df.apply(lambda x: f"{x['commissione']:.2f} {x['valuta']}", axis=1)
            
            # Formatta stato
            df['stato_formatted'] = df['stato'].map({
                'pending': '⏳ In Attesa',
                'completed': '✅ Completata',
                'failed': '❌ Fallita',
                'cancelled': '🚫 Cancellata'
            })
            
            # Formatta tipo transazione
            df['tipo_formatted'] = df['tipo_transazione'].map({
                'transfer': '🔄 Trasferimento',
                'deposit': '📥 Deposito',
                'withdrawal': '📤 Prelievo'
            })
        
        # Filtri
        st.subheader("🔍 Filtri")
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            # Filtro per stato (ordinato alfabeticamente)
            stati_list = list(df['stato'].unique()) if not df.empty else []
            stati_list.sort()
            stati_disponibili = ['Tutti'] + stati_list
            stato_selezionato = st.selectbox("📊 Stato", stati_disponibili, key=f"filter_stato_wallet_table_{unique_id}")
            
            if stato_selezionato != 'Tutti' and not df.empty:
                df = df[df['stato'] == stato_selezionato]
        
        with col_filter2:
            # Filtro per wallet mittente (ordinato alfabeticamente)
            wallet_mittenti_list = list(df['wallet_mittente'].unique()) if not df.empty else []
            wallet_mittenti_list.sort()
            wallet_mittenti = ['Tutti'] + wallet_mittenti_list
            mittente_selezionato = st.selectbox("💰 Wallet Mittente", wallet_mittenti, key=f"filter_mittente_wallet_table_{unique_id}")
            
            if mittente_selezionato != 'Tutti' and not df.empty:
                df = df[df['wallet_mittente'] == mittente_selezionato]
        
        with col_filter3:
            # Filtro per data
            if not df.empty:
                date_range = st.date_input(
                    "📅 Periodo",
                    value=(datetime.now() - timedelta(days=30), datetime.now()),
                    max_value=datetime.now(),
                    key=f"filter_date_wallet_table_{unique_id}"
                )
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    df['data_transazione_parsed'] = pd.to_datetime(df['data_transazione'], format='%d/%m/%Y %H:%M')
                    df = df[(df['data_transazione_parsed'].dt.date >= start_date) & 
                           (df['data_transazione_parsed'].dt.date <= end_date)]
        
        # Statistiche rapide
        if not df.empty:
            st.subheader("📊 Statistiche Rapide")
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("📋 Totale Transazioni", len(df))
            
            with col_stat2:
                importo_totale = df['importo'].sum()
                valuta_principale = df['valuta'].mode().iloc[0] if not df.empty else 'USD'
                st.metric("💵 Importo Totale", f"{importo_totale:.2f} {valuta_principale}")
            
            with col_stat3:
                transazioni_completate = len(df[df['stato'] == 'completed'])
                st.metric("✅ Completate", transazioni_completate)
            
            with col_stat4:
                transazioni_pending = len(df[df['stato'] == 'pending'])
                st.metric("⏳ In Attesa", transazioni_pending)
        
        # Tabella principale
        st.subheader("📋 Transazioni Wallet")
        
        if df.empty:
            st.info("📋 Nessuna transazione corrisponde ai filtri selezionati.")
            return
        
        # Seleziona colonne da mostrare
        columns_to_show = [
            'data_transazione', 'wallet_mittente', 'wallet_destinatario',
            'importo_formatted', 'tipo_formatted', 'stato_formatted',
            'commissione_formatted', 'note'
        ]
        
        # Crea tabella con azioni
        for idx, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**📅 {row['data_transazione']}**")
                    st.write(f"💰 {row['wallet_mittente']} → 🎯 {row['wallet_destinatario']}")
                
                with col2:
                    st.write(f"**💵 {row['importo_formatted']}**")
                    st.write(f"💸 Commissione: {row['commissione_formatted']}")
                
                with col3:
                    st.write(f"**{row['tipo_formatted']}**")
                    st.write(f"**{row['stato_formatted']}**")
                
                with col4:
                    if on_edit:
                        if st.button("✏️", key=f"edit_{row['id']}_{unique_id}", help="Modifica transazione"):
                            st.session_state.editing_transaction = row.to_dict()
                            st.rerun()
                
                with col5:
                    # Pulsanti per gestire transazioni pending
                    if row['stato'] == 'pending':
                        col_confirm, col_cancel = st.columns(2)
                        
                        with col_confirm:
                            if st.button("✅ Conferma", key=f"confirm_{row['id']}_{unique_id}", help="Conferma transazione"):
                                success, message = self.wallet_manager.update_wallet_transaction(
                                    row['id'], 
                                    {'stato': 'completed'}
                                )
                                if success:
                                    st.success("✅ Transazione confermata!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Errore: {message}")
                        
                        with col_cancel:
                            if st.button("❌ Annulla", key=f"cancel_{row['id']}_{unique_id}", help="Annulla transazione"):
                                success, message = self.wallet_manager.update_wallet_transaction(
                                    row['id'], 
                                    {'stato': 'cancelled'}
                                )
                                if success:
                                    st.success("❌ Transazione annullata!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Errore: {message}")
                    
                    # Pulsante per eliminare (solo per transazioni non pending)
                    elif on_delete and row['stato'] != 'pending':
                        delete_key = f"delete_{row['id']}_{unique_id}"
                        confirm_key = f"confirm_delete_{row['id']}_{unique_id}"
                        
                        if st.button("🗑️", key=delete_key, help="Elimina transazione"):
                            st.session_state[f"show_delete_confirm_{row['id']}_{unique_id}"] = True
                            st.rerun()
                        
                        # Mostra conferma eliminazione se necessario
                        if st.session_state.get(f"show_delete_confirm_{row['id']}_{unique_id}", False):
                            st.warning("⚠️ **ATTENZIONE**: Eliminazione definitiva!")
                            st.write(f"**Transazione:** {row['wallet_mittente']} → {row['wallet_destinatario']}")
                            st.write(f"**Importo:** {row['importo_formatted']}")
                            
                            if st.checkbox("✅ Confermo l'eliminazione", key=confirm_key):
                                success, message = self.wallet_manager.delete_wallet_transaction(row['id'])
                                if success:
                                    st.success(message)
                                    st.session_state[f"show_delete_confirm_{row['id']}_{unique_id}"] = False
                                    st.rerun()
                                else:
                                    st.error(message)
                                    st.session_state[f"show_delete_confirm_{row['id']}_{unique_id}"] = False
                            
                            if st.button("❌ Annulla", key=f"cancel_delete_{row['id']}_{unique_id}"):
                                st.session_state[f"show_delete_confirm_{row['id']}_{unique_id}"] = False
                                st.rerun()
                
                # Note (se presenti)
                if row['note'] and pd.notna(row['note']):
                    st.write(f"📝 **Note:** {row['note']}")
                
                st.markdown("---")
        
        # Form modifica transazione
        if 'editing_transaction' in st.session_state:
            self._render_edit_transaction_form(st.session_state.editing_transaction, unique_id)
        
        # Grafici
        self._render_charts(df, unique_id)
    
    def _render_charts(self, df: pd.DataFrame, unique_id: int):
        """Rende i grafici delle transazioni"""
        if df.empty:
            return
        
        st.subheader("📈 Grafici Transazioni")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Grafico transazioni per stato
            stato_counts = df['stato'].value_counts()
            
            fig_stato = px.pie(
                values=stato_counts.values,
                names=stato_counts.index,
                title="📊 Transazioni per Stato",
                color_discrete_map={
                    'pending': '#FFA500',
                    'completed': '#00FF00',
                    'failed': '#FF0000',
                    'cancelled': '#808080'
                }
            )
            
            st.plotly_chart(fig_stato, use_container_width=True, key=f"chart_stato_wallet_table_{unique_id}")
        
        with col_chart2:
            # Grafico transazioni per tipo
            tipo_counts = df['tipo_transazione'].value_counts()
            
            fig_tipo = px.bar(
                x=tipo_counts.index,
                y=tipo_counts.values,
                title="📋 Transazioni per Tipo",
                labels={'x': 'Tipo Transazione', 'y': 'Numero Transazioni'}
            )
            
            st.plotly_chart(fig_tipo, use_container_width=True, key=f"chart_tipo_wallet_table_{unique_id}")
        
        # Grafico timeline transazioni
        if len(df) > 1:
            st.subheader("📅 Timeline Transazioni")
            
            # Prepara dati per timeline
            df_timeline = df.copy()
            df_timeline['data_transazione_parsed'] = pd.to_datetime(df_timeline['data_transazione'], format='%d/%m/%Y %H:%M')
            df_timeline = df_timeline.sort_values('data_transazione_parsed')
            
            fig_timeline = go.Figure()
            
            # Colori per stato
            color_map = {
                'pending': '#FFA500',
                'completed': '#00FF00',
                'failed': '#FF0000',
                'cancelled': '#808080'
            }
            
            for stato in df_timeline['stato'].unique():
                df_stato = df_timeline[df_timeline['stato'] == stato]
                
                fig_timeline.add_trace(go.Scatter(
                    x=df_stato['data_transazione_parsed'],
                    y=df_stato['importo'],
                    mode='markers',
                    name=stato,
                    marker=dict(color=color_map.get(stato, '#000000')),
                    text=df_stato.apply(lambda x: f"{x['wallet_mittente']} → {x['wallet_destinatario']}<br>{x['importo']:.2f} {x['valuta']}", axis=1),
                    hovertemplate='<b>%{text}</b><br>Data: %{x}<br>Importo: %{y}<extra></extra>'
                ))
            
            fig_timeline.update_layout(
                title="📈 Timeline Transazioni per Importo",
                xaxis_title="Data",
                yaxis_title="Importo",
                hovermode='closest'
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True, key=f"chart_timeline_wallet_table_{unique_id}")
    
    # Funzione render_wallet_balances rimossa - ora integrata in deposit_management per evitare duplicazioni
    
    def _render_edit_transaction_form(self, transaction_data: Dict[str, Any], unique_id: int):
        """Rende il form per modificare una transazione esistente"""
        
        st.markdown("---")
        st.subheader("✏️ Modifica Transazione")
        
        with st.form(f"edit_transaction_form_{unique_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Wallet mittente (ordinato alfabeticamente)
                wallet_list = self.wallet_manager.get_wallet_list()
                wallet_list_sorted = sorted(wallet_list)
                try:
                    wallet_mittente_index = wallet_list_sorted.index(transaction_data['wallet_mittente'])
                except ValueError:
                    wallet_mittente_index = 0
                
                wallet_mittente = st.selectbox(
                    "💰 Wallet Mittente",
                    options=wallet_list_sorted,
                    index=wallet_mittente_index,
                    help="Wallet da cui parte la transazione",
                    key=f"edit_mittente_{transaction_data['id']}_{unique_id}"
                )
                
                # Wallet destinatario (ordinato alfabeticamente)
                try:
                    wallet_destinatario_index = wallet_list_sorted.index(transaction_data['wallet_destinatario'])
                except ValueError:
                    wallet_destinatario_index = 0
                
                wallet_destinatario = st.selectbox(
                    "🎯 Wallet Destinatario",
                    options=wallet_list_sorted,
                    index=wallet_destinatario_index,
                    help="Wallet destinatario della transazione",
                    key=f"edit_destinatario_{transaction_data['id']}_{unique_id}"
                )
                
                # Importo
                importo = st.number_input(
                    "💵 Importo",
                    min_value=0.01,
                    max_value=1000000.0,
                    step=0.01,
                    value=float(transaction_data['importo']),
                    format="%.2f",
                    help="Importo della transazione",
                    key=f"edit_importo_{transaction_data['id']}_{unique_id}"
                )
            
            with col2:
                # Valuta (ordinata alfabeticamente)
                valute_options = ["BTC", "ETH", "EUR", "GBP", "USD"]
                try:
                    valuta_index = valute_options.index(transaction_data.get('valuta', 'USD'))
                except ValueError:
                    valuta_index = 0
                
                valuta = st.selectbox(
                    "💱 Valuta",
                    options=valute_options,
                    index=valuta_index,
                    help="Valuta della transazione",
                    key=f"edit_valuta_{transaction_data['id']}_{unique_id}"
                )
                
                # Tipo transazione (ordinato alfabeticamente)
                tipi_transazione = ["deposit", "transfer", "withdrawal"]
                try:
                    tipo_index = tipi_transazione.index(transaction_data.get('tipo_transazione', 'transfer'))
                except ValueError:
                    tipo_index = 0
                
                tipo_transazione = st.selectbox(
                    "📋 Tipo Transazione",
                    options=tipi_transazione,
                    index=tipo_index,
                    format_func=lambda x: {
                        "transfer": "🔄 Trasferimento",
                        "deposit": "📥 Deposito",
                        "withdrawal": "📤 Prelievo"
                    }[x],
                    help="Tipo di transazione",
                    key=f"edit_tipo_{transaction_data['id']}_{unique_id}"
                )
                
                # Stato (ordinato alfabeticamente)
                stati_options = ["cancelled", "completed", "failed", "pending"]
                try:
                    stato_index = stati_options.index(transaction_data.get('stato', 'pending'))
                except ValueError:
                    stato_index = 0
                
                stato = st.selectbox(
                    "📊 Stato",
                    options=stati_options,
                    index=stato_index,
                    format_func=lambda x: {
                        "pending": "⏳ In Attesa",
                        "completed": "✅ Completata",
                        "failed": "❌ Fallita",
                        "cancelled": "🚫 Cancellata"
                    }[x],
                    help="Stato della transazione",
                    key=f"edit_stato_{transaction_data['id']}_{unique_id}"
                )
            
            # Commissione
            commissione = st.number_input(
                "💸 Commissione",
                min_value=0.0,
                max_value=1000.0,
                step=0.01,
                value=float(transaction_data.get('commissione', 0.0)),
                format="%.2f",
                help="Commissione della transazione",
                key=f"edit_commissione_{transaction_data['id']}_{unique_id}"
            )
            
            # Note
            note = st.text_area(
                "📝 Note",
                value=transaction_data.get('note', ''),
                placeholder="Note aggiuntive sulla transazione...",
                help="Note opzionali",
                key=f"edit_note_{transaction_data['id']}_{unique_id}"
            )
            
            # Pulsanti
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                submit_button = st.form_submit_button(
                    "💾 Salva Modifiche",
                    type="primary",
                    use_container_width=True,
                    key=f"edit_save_{transaction_data['id']}_{unique_id}"
                )
            
            with col_btn2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True,
                    key=f"edit_cancel_{transaction_data['id']}_{unique_id}"
                )
            
            with col_btn3:
                delete_button = st.form_submit_button(
                    "🗑️ Elimina Transazione",
                    use_container_width=True,
                    key=f"edit_delete_{transaction_data['id']}_{unique_id}"
                )
            
            # Gestione submit
            if submit_button:
                if wallet_mittente == wallet_destinatario:
                    st.error("❌ Il wallet mittente e destinatario devono essere diversi")
                else:
                    updated_data = {
                        'wallet_mittente': wallet_mittente,
                        'wallet_destinatario': wallet_destinatario,
                        'importo': float(importo),
                        'valuta': valuta,
                        'tipo_transazione': tipo_transazione,
                        'stato': stato,
                        'commissione': float(commissione),
                        'note': note.strip() if note else None
                    }
                    
                    success, message = self.wallet_manager.update_wallet_transaction(
                        transaction_data['id'], 
                        updated_data
                    )
                    if success:
                        st.success(message)
                        del st.session_state.editing_transaction
                        st.rerun()
                    else:
                        st.error(message)
            
            if cancel_button:
                del st.session_state.editing_transaction
                st.rerun()
            
            if delete_button:
                # Conferma eliminazione
                st.warning("⚠️ **ATTENZIONE**: Stai per eliminare definitivamente questa transazione!")
                st.write(f"**Transazione da eliminare:**")
                st.write(f"- Da: {wallet_mittente}")
                st.write(f"- A: {wallet_destinatario}")
                st.write(f"- Importo: {importo} {valuta}")
                st.write(f"- Data: {transaction_data.get('data_transazione', 'N/A')}")
                
                if st.checkbox("✅ Confermo l'eliminazione definitiva", key=f"edit_confirm_delete_{transaction_data['id']}_{unique_id}"):
                    success, message = self.wallet_manager.delete_wallet_transaction(transaction_data['id'])
                    if success:
                        st.success(message)
                        del st.session_state.editing_transaction
                        st.rerun()
                    else:
                        st.error(message)
