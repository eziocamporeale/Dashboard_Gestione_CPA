"""
💰 DEPOSIT MANAGEMENT
Interfaccia per gestione depositi e prelievi tra wallet team e clienti
Integrato con il sistema wallet esistente
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DepositManagement:
    """Gestione depositi e prelievi tra wallet team e clienti"""
    
    def __init__(self, wallet_manager):
        """Inizializza il gestore depositi"""
        self.wallet_manager = wallet_manager
    
    def render_deposit_management(self):
        """Rende l'interfaccia completa per gestione depositi"""
        
        st.subheader("💰 Gestione Depositi e Prelievi")
        st.info("🔄 **Gestisci depositi e prelievi** tra wallet team e clienti")
        
        # Tab per organizzare le funzionalità
        tab_deposits, tab_withdrawals, tab_history, tab_balances = st.tabs([
            "💸 Depositi Team → Cliente", "💳 Prelievi Cliente → Team", "📋 Cronologia", "💰 Saldi Wallet"
        ])
        
        # TAB 1: Depositi Team → Cliente
        with tab_deposits:
            self._render_deposit_form()
        
        # TAB 2: Prelievi Cliente → Team
        with tab_withdrawals:
            self._render_withdrawal_form()
        
        # TAB 3: Cronologia Transazioni
        with tab_history:
            self._render_transaction_history()
        
        # TAB 4: Saldi Wallet
        with tab_balances:
            self._render_wallet_balances()
    
    def _render_deposit_form(self):
        """Rende il form per depositi da team a cliente"""
        
        st.markdown("### 💸 Deposito da Team a Cliente")
        st.info("💡 **Seleziona wallet team e cliente, inserisci importo e motivo**")
        
        # Recupera wallet disponibili
        team_wallets = self.wallet_manager.get_team_wallets()
        client_wallets = self.wallet_manager.get_client_wallets()
        
        if not team_wallets:
            st.warning("⚠️ Nessun wallet team disponibile. Configura prima i wallet team.")
            return
        
        if not client_wallets:
            st.warning("⚠️ Nessun wallet cliente disponibile. I wallet clienti vengono creati automaticamente quando si inserisce un wallet nel form cliente.")
            return
        
        # Form deposito
        with st.form("deposit_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Selezione wallet team
                team_wallet_names = [f"{w['nome_wallet']} ({w['tipo_wallet']})" for w in team_wallets]
                team_selected = st.selectbox(
                    "👥 Wallet Team (Mittente)",
                    options=team_wallet_names,
                    help="Seleziona il wallet team da cui prelevare"
                )
                
                # Selezione wallet cliente
                client_wallet_names = [f"{w['nome_wallet']} ({w.get('proprietario', 'Cliente')})" for w in client_wallets]
                client_selected = st.selectbox(
                    "👤 Wallet Cliente (Destinatario)",
                    options=client_wallet_names,
                    help="Seleziona il wallet cliente a cui depositare"
                )
            
            with col2:
                # Importo
                amount = st.number_input(
                    "💰 Importo (USDT)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Importo da depositare in USDT"
                )
                
                # Motivo deposito
                motivo_options = ["deposit_iniziale", "rideposito"]
                motivo = st.selectbox(
                    "📝 Motivo Deposito",
                    options=motivo_options,
                    format_func=lambda x: {
                        "deposit_iniziale": "🏁 Deposito Iniziale",
                        "rideposito": "🔄 Rideposito"
                    }[x],
                    help="Motivo del deposito"
                )
            
            # Campi aggiuntivi
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                hash_blockchain = st.text_input(
                    "🔗 Hash Blockchain (Opzionale)",
                    placeholder="0x...",
                    help="Hash della transazione blockchain (opzionale)"
                )
            
            with col4:
                commissione_network = st.number_input(
                    "⛽ Commissione Network (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=0.0,
                    help="Commissione di rete pagata"
                )
            
            # Note aggiuntive
            note = st.text_area(
                "📝 Note Aggiuntive",
                placeholder="Note opzionali per la transazione...",
                help="Note aggiuntive per la transazione"
            )
            
            # Pulsante submit
            submitted = st.form_submit_button("💸 Crea Deposito", type="primary")
            
            if submitted:
                if amount > 0:
                    # Estrai nomi wallet dalle selezioni
                    team_wallet_name = team_selected.split(" (")[0]
                    client_wallet_name = client_selected.split(" (")[0]
                    
                    # Crea transazione
                    success, message = self.wallet_manager.create_deposit_transaction(
                        team_wallet=team_wallet_name,
                        client_wallet=client_wallet_name,
                        amount=amount,
                        motivo=motivo,
                        hash_blockchain=hash_blockchain if hash_blockchain else None,
                        commissione_network=commissione_network
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        
                        # Mostra riepilogo
                        st.markdown("### 📊 Riepilogo Transazione")
                        col_summary1, col_summary2 = st.columns(2)
                        with col_summary1:
                            st.write(f"**👥 Da:** {team_wallet_name}")
                            st.write(f"**👤 A:** {client_wallet_name}")
                            st.write(f"**💰 Importo:** {amount} USDT")
                        with col_summary2:
                            st.write(f"**📝 Motivo:** {motivo}")
                            st.write(f"**⛽ Commissione:** {commissione_network} USDT")
                            if hash_blockchain:
                                st.write(f"**🔗 Hash:** {hash_blockchain}")
                    else:
                        st.error(message)
                else:
                    st.error("❌ Inserisci un importo valido")
    
    def _render_withdrawal_form(self):
        """Rende il form per prelievi da cliente a team"""
        
        st.markdown("### 💳 Prelievo da Cliente a Team")
        st.info("💡 **Seleziona wallet cliente e team, inserisci importo**")
        
        # Recupera wallet disponibili
        team_wallets = self.wallet_manager.get_team_wallets()
        client_wallets = self.wallet_manager.get_client_wallets()
        
        if not team_wallets:
            st.warning("⚠️ Nessun wallet team disponibile.")
            return
        
        if not client_wallets:
            st.warning("⚠️ Nessun wallet cliente disponibile.")
            return
        
        # Form prelievo
        with st.form("withdrawal_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Selezione wallet cliente
                client_wallet_names = [f"{w['nome_wallet']} ({w.get('proprietario', 'Cliente')})" for w in client_wallets]
                client_selected = st.selectbox(
                    "👤 Wallet Cliente (Mittente)",
                    options=client_wallet_names,
                    help="Seleziona il wallet cliente da cui prelevare",
                    key="withdrawal_client"
                )
                
                # Selezione wallet team
                team_wallet_names = [f"{w['nome_wallet']} ({w['tipo_wallet']})" for w in team_wallets]
                team_selected = st.selectbox(
                    "👥 Wallet Team (Destinatario)",
                    options=team_wallet_names,
                    help="Seleziona il wallet team a cui depositare",
                    key="withdrawal_team"
                )
            
            with col2:
                # Importo
                amount = st.number_input(
                    "💰 Importo (USDT)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Importo da prelevare in USDT",
                    key="withdrawal_amount"
                )
                
                # Motivo prelievo
                motivo = st.selectbox(
                    "📝 Motivo Prelievo",
                    options=["prelievo"],
                    format_func=lambda x: "💳 Prelievo",
                    help="Motivo del prelievo",
                    key="withdrawal_motivo"
                )
            
            # Campi aggiuntivi
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                hash_blockchain = st.text_input(
                    "🔗 Hash Blockchain (Opzionale)",
                    placeholder="0x...",
                    help="Hash della transazione blockchain (opzionale)",
                    key="withdrawal_hash"
                )
            
            with col4:
                commissione_network = st.number_input(
                    "⛽ Commissione Network (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=0.0,
                    help="Commissione di rete pagata",
                    key="withdrawal_commission"
                )
            
            # Note aggiuntive
            note = st.text_area(
                "📝 Note Aggiuntive",
                placeholder="Note opzionali per la transazione...",
                help="Note aggiuntive per la transazione",
                key="withdrawal_note"
            )
            
            # Pulsante submit
            submitted = st.form_submit_button("💳 Crea Prelievo", type="primary")
            
            if submitted:
                if amount > 0:
                    # Estrai nomi wallet dalle selezioni
                    client_wallet_name = client_selected.split(" (")[0]
                    team_wallet_name = team_selected.split(" (")[0]
                    
                    # Crea transazione
                    success, message = self.wallet_manager.create_withdrawal_transaction(
                        client_wallet=client_wallet_name,
                        team_wallet=team_wallet_name,
                        amount=amount,
                        motivo=motivo,
                        hash_blockchain=hash_blockchain if hash_blockchain else None,
                        commissione_network=commissione_network
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        
                        # Mostra riepilogo
                        st.markdown("### 📊 Riepilogo Transazione")
                        col_summary1, col_summary2 = st.columns(2)
                        with col_summary1:
                            st.write(f"**👤 Da:** {client_wallet_name}")
                            st.write(f"**👥 A:** {team_wallet_name}")
                            st.write(f"**💰 Importo:** {amount} USDT")
                        with col_summary2:
                            st.write(f"**📝 Motivo:** {motivo}")
                            st.write(f"**⛽ Commissione:** {commissione_network} USDT")
                            if hash_blockchain:
                                st.write(f"**🔗 Hash:** {hash_blockchain}")
                    else:
                        st.error(message)
                else:
                    st.error("❌ Inserisci un importo valido")
    
    def _render_transaction_history(self):
        """Rende la cronologia delle transazioni"""
        
        st.markdown("### 📋 Cronologia Transazioni")
        
        # Filtri
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            tipo_filter = st.selectbox(
                "📊 Tipo Transazione",
                options=["Tutti", "deposit_iniziale", "rideposito", "prelievo", "transfer"],
                help="Filtra per tipo di transazione"
            )
        
        with col_filter2:
            stato_filter = st.selectbox(
                "📈 Stato",
                options=["Tutti", "completed", "pending", "failed"],
                help="Filtra per stato transazione"
            )
        
        with col_filter3:
            limit = st.selectbox(
                "📄 Numero Righe",
                options=[10, 25, 50, 100],
                index=1,
                help="Numero di transazioni da mostrare"
            )
        
        # Recupera transazioni
        transactions = self.wallet_manager.get_wallet_transactions(limit=limit)
        
        if not transactions:
            st.info("📋 Nessuna transazione presente.")
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(transactions)
        
        # Applica filtri
        if tipo_filter != "Tutti":
            df = df[df['tipo_transazione'] == tipo_filter]
        
        if stato_filter != "Tutti":
            df = df[df['stato'] == stato_filter]
        
        if df.empty:
            st.info(f"📋 Nessuna transazione trovata con i filtri selezionati.")
            return
        
        # Formatta colonne
        df['data_transazione'] = pd.to_datetime(df['data_transazione']).dt.strftime('%d/%m/%Y %H:%M')
        df['importo'] = df['importo'].astype(float)
        
        # Mostra tabella
        st.dataframe(
            df[['data_transazione', 'wallet_mittente', 'wallet_destinatario', 'importo', 'valuta', 'tipo_transazione', 'stato']],
            use_container_width=True,
            column_config={
                "data_transazione": st.column_config.DatetimeColumn("📅 Data", width=120),
                "wallet_mittente": st.column_config.TextColumn("👤 Da", width=120),
                "wallet_destinatario": st.column_config.TextColumn("👥 A", width=120),
                "importo": st.column_config.NumberColumn("💰 Importo", width=100, format="%.2f"),
                "valuta": st.column_config.TextColumn("💱 Valuta", width=80),
                "tipo_transazione": st.column_config.TextColumn("📝 Tipo", width=120),
                "stato": st.column_config.TextColumn("📈 Stato", width=100)
            }
        )
        
        # Statistiche rapide
        st.markdown("### 📊 Statistiche Rapide")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            total_amount = df['importo'].sum()
            st.metric("💰 Totale Transazioni", f"{total_amount:,.2f} USDT")
        
        with col_stat2:
            completed_count = len(df[df['stato'] == 'completed'])
            st.metric("✅ Transazioni Completate", completed_count)
        
        with col_stat3:
            pending_count = len(df[df['stato'] == 'pending'])
            st.metric("⏳ Transazioni Pending", pending_count)
    
    def _render_wallet_balances(self):
        """Rende i saldi dei wallet"""
        
        st.markdown("### 💰 Saldi Wallet")
        
        # Recupera tutti i wallet
        all_wallets = self.wallet_manager.get_wallet_collaboratori()
        
        if not all_wallets:
            st.info("📋 Nessun wallet disponibile.")
            return
        
        # Calcola saldi
        wallet_data = []
        for wallet in all_wallets:
            if wallet.get('attivo', True):
                saldo = self.wallet_manager.calculate_wallet_balance(wallet['nome_wallet'])
                wallet_data.append({
                    'nome_wallet': wallet['nome_wallet'],
                    'proprietario': wallet.get('proprietario', 'N/A'),
                    'tipo_wallet': wallet['tipo_wallet'],
                    'saldo': saldo,
                    'valuta': wallet.get('valuta', 'USD')
                })
        
        if not wallet_data:
            st.info("📋 Nessun wallet attivo disponibile.")
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(wallet_data)
        
        # Mostra tabella saldi
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "nome_wallet": st.column_config.TextColumn("💰 Wallet", width=150),
                "proprietario": st.column_config.TextColumn("👤 Proprietario", width=150),
                "tipo_wallet": st.column_config.TextColumn("📋 Tipo", width=120),
                "saldo": st.column_config.NumberColumn("💵 Saldo", width=120, format="%.2f"),
                "valuta": st.column_config.TextColumn("💱 Valuta", width=80)
            }
        )
        
        # Statistiche saldi
        st.markdown("### 📊 Statistiche Saldi")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            total_balance = df['saldo'].sum()
            st.metric("💰 Saldo Totale", f"{total_balance:,.2f} USDT")
        
        with col_stat2:
            team_wallets = df[df['tipo_wallet'].isin(['collaboratore', 'principale'])]
            team_balance = team_wallets['saldo'].sum()
            st.metric("👥 Saldo Team", f"{team_balance:,.2f} USDT")
        
        with col_stat3:
            client_wallets = df[df['tipo_wallet'] == 'cliente']
            client_balance = client_wallets['saldo'].sum()
            st.metric("👤 Saldo Clienti", f"{client_balance:,.2f} USDT")
