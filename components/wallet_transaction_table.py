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
            # Filtro per stato
            stati_disponibili = ['Tutti'] + list(df['stato'].unique()) if not df.empty else ['Tutti']
            stato_selezionato = st.selectbox("📊 Stato", stati_disponibili)
            
            if stato_selezionato != 'Tutti' and not df.empty:
                df = df[df['stato'] == stato_selezionato]
        
        with col_filter2:
            # Filtro per wallet mittente
            wallet_mittenti = ['Tutti'] + list(df['wallet_mittente'].unique()) if not df.empty else ['Tutti']
            mittente_selezionato = st.selectbox("💰 Wallet Mittente", wallet_mittenti)
            
            if mittente_selezionato != 'Tutti' and not df.empty:
                df = df[df['wallet_mittente'] == mittente_selezionato]
        
        with col_filter3:
            # Filtro per data
            if not df.empty:
                date_range = st.date_input(
                    "📅 Periodo",
                    value=(datetime.now() - timedelta(days=30), datetime.now()),
                    max_value=datetime.now()
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
                        if st.button("✏️", key=f"edit_{row['id']}", help="Modifica transazione"):
                            on_edit(row.to_dict())
                
                with col5:
                    # Pulsanti per gestire transazioni pending
                    if row['stato'] == 'pending':
                        col_confirm, col_cancel = st.columns(2)
                        
                        with col_confirm:
                            if st.button("✅ Conferma", key=f"confirm_{row['id']}", help="Conferma transazione"):
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
                            if st.button("❌ Annulla", key=f"cancel_{row['id']}", help="Annulla transazione"):
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
                        if st.button("🗑️", key=f"delete_{row['id']}", help="Elimina transazione"):
                            if st.button("✅ Conferma", key=f"confirm_delete_{row['id']}"):
                                success, message = self.wallet_manager.delete_wallet_transaction(row['id'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                
                # Note (se presenti)
                if row['note'] and pd.notna(row['note']):
                    st.write(f"📝 **Note:** {row['note']}")
                
                st.markdown("---")
        
        # Grafici
        self._render_charts(df)
    
    def _render_charts(self, df: pd.DataFrame):
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
            
            st.plotly_chart(fig_stato, use_container_width=True)
        
        with col_chart2:
            # Grafico transazioni per tipo
            tipo_counts = df['tipo_transazione'].value_counts()
            
            fig_tipo = px.bar(
                x=tipo_counts.index,
                y=tipo_counts.values,
                title="📋 Transazioni per Tipo",
                labels={'x': 'Tipo Transazione', 'y': 'Numero Transazioni'}
            )
            
            st.plotly_chart(fig_tipo, use_container_width=True)
        
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
            
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    def render_wallet_balances(self):
        """Rende la tabella dei saldi wallet"""
        st.subheader("💰 Saldi Wallet")
        
        wallets = self.wallet_manager.get_wallet_collaboratori()
        
        if not wallets:
            st.info("📋 Nessun wallet disponibile.")
            return
        
        # Calcola saldi
        wallet_data = []
        for wallet in wallets:
            if wallet.get('attivo', True):
                saldo = self.wallet_manager.get_wallet_balance(wallet['nome_wallet'])
                wallet_data.append({
                    'nome_wallet': wallet['nome_wallet'],
                    'proprietario': wallet['proprietario'],
                    'tipo_wallet': wallet['tipo_wallet'],
                    'saldo_attuale': saldo,
                    'valuta': wallet.get('valuta', 'USD'),
                    'note': wallet.get('note', '')
                })
        
        if wallet_data:
            df_wallets = pd.DataFrame(wallet_data)
            
            # Formatta saldi
            df_wallets['saldo_formatted'] = df_wallets.apply(
                lambda x: f"{x['saldo_attuale']:.2f} {x['valuta']}", axis=1
            )
            
            # Mostra tabella saldi
            for _, row in df_wallets.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.write(f"**💰 {row['nome_wallet']}**")
                
                with col2:
                    st.write(f"👤 {row['proprietario']}")
                
                with col3:
                    st.write(f"📋 {row['tipo_wallet']}")
                
                with col4:
                    # Colore saldo basato su valore
                    if row['saldo_attuale'] > 0:
                        st.success(f"💚 {row['saldo_formatted']}")
                    elif row['saldo_attuale'] < 0:
                        st.error(f"💔 {row['saldo_formatted']}")
                    else:
                        st.info(f"⚪ {row['saldo_formatted']}")
                
                if row['note']:
                    st.write(f"📝 {row['note']}")
                
                st.markdown("---")
            
            # Grafico saldi
            fig_balances = px.bar(
                df_wallets,
                x='nome_wallet',
                y='saldo_attuale',
                title="💰 Saldi Wallet",
                labels={'nome_wallet': 'Wallet', 'saldo_attuale': 'Saldo'},
                color='saldo_attuale',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            
            st.plotly_chart(fig_balances, use_container_width=True)
