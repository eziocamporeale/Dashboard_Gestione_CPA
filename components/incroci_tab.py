#!/usr/bin/env python3
"""
Tab per la gestione degli incroci tra account CPA
Permette di creare, visualizzare e gestire gli incroci per sbloccare bonus senza rischio
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from typing import Dict, List
import logging
import time
from utils.translations import t

class IncrociTab:
    """Tab per la gestione degli incroci"""
    
    def __init__(self, incroci_manager, database_manager):
        """Inizializza il tab incroci"""
        self.incroci_manager = incroci_manager
        self.database_manager = database_manager
        
        # Aggiungi SupabaseManager per i clienti
        try:
            from supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
        except Exception as e:
            st.error(f"❌ Errore inizializzazione SupabaseManager: {e}")
            self.supabase_manager = None
    
    def render(self):
        """Rende il tab completo degli incroci"""
        st.header(t("incroci.title", "🔄 Gestione Incroci CPA"))
        st.markdown(t("incroci.description", "Gestisci gli incroci tra account per sbloccare bonus senza rischio"))
        
        # Sidebar per filtri e azioni rapide
        with st.sidebar:
            st.subheader(t("incroci.filters.title", "🔍 Filtri"))
            stato_filtro = st.selectbox(
                t("incroci.filters.status", "Stato Incroci"),
                [
                    t("incroci.filters.status_options.all", "Tutti"),
                    t("incroci.filters.status_options.active", "Attivi"),
                    t("incroci.filters.status_options.closed", "Chiusi"),
                    t("incroci.filters.status_options.suspended", "Sospesi")
                ],
                index=0
            )
            
            st.subheader(t("incroci.quick_stats.title", "📊 Statistiche Rapide"))
            stats = self.incroci_manager.ottieni_statistiche_incroci()
            if stats:
                st.metric(t("incroci.quick_stats.active_crosses", "Incroci Attivi"), stats['generali']['incroci_attivi'])
                st.metric(t("incroci.quick_stats.total_volume", "Volume Totale"), f"{stats['generali']['volume_totale']:,.0f}")
                st.metric(t("incroci.quick_stats.total_bonus", "Bonus Totali"), f"{stats['bonus']['totale_bonus']:,.0f} USD")
        
        # Tab principali
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            t("incroci.tabs.list", "📋 Lista Incroci"), 
            t("incroci.tabs.new", "➕ Nuovo Incrocio"), 
            t("incroci.tabs.close", "🔄 Chiusura Incroci"), 
            t("incroci.tabs.statistics", "📊 Statistiche"), 
            t("incroci.tabs.search", "🔍 Ricerca")
        ])
        
        with tab1:
            self.render_lista_incroci(stato_filtro)
        
        with tab2:
            self.render_nuovo_incrocio()
        
        with tab3:
            self.render_chiusura_incroci()
        
        with tab4:
            self.render_statistiche()
        
        with tab5:
            self.render_ricerca()
    
    def render_lista_incroci(self, stato_filtro: str):
        """Rende la lista degli incroci"""
        st.subheader("📋 Lista Incroci")
        
        # Controlla se è necessario aggiornare la lista
        if st.session_state.get('incroci_aggiornati', False):
            ultimo_eliminato = st.session_state.get('ultimo_eliminato', None)
            if ultimo_eliminato:
                st.success(f"✅ Incrocio {ultimo_eliminato} eliminato con successo! Lista aggiornata.")
                # Forza aggiornamento immediato
                st.session_state.incroci_aggiornati = False
                st.session_state.ultimo_eliminato = None
                st.rerun()
            else:
                st.info("🔄 Lista aggiornata dopo operazioni")
                st.session_state.incroci_aggiornati = False
                st.session_state.ultimo_eliminato = None
        
        # Timestamp per forzare aggiornamento
        if 'ultimo_aggiornamento' not in st.session_state:
            st.session_state.ultimo_aggiornamento = 0
        
        # Pulsante per forzare aggiornamento
        if st.button("🔄 Aggiorna Lista", key="refresh_incroci"):
            # Forza refresh completo
            st.session_state.incroci_aggiornati = False
            st.session_state.ultimo_eliminato = None
            st.session_state.ultimo_aggiornamento = int(time.time())
            st.rerun()
        

        
        # Ottieni incroci filtrati
        if stato_filtro == t("incroci.filters.status_options.all", "Tutti"):
            incroci_df = self.incroci_manager.ottieni_incroci()
        else:
            stato_map = {
                t("incroci.filters.status_options.active", "Attivi"): "attivo", 
                t("incroci.filters.status_options.closed", "Chiusi"): "chiuso", 
                t("incroci.filters.status_options.suspended", "Sospesi"): "sospeso"
            }
            incroci_df = self.incroci_manager.ottieni_incroci(stato_map[stato_filtro])
        
        if incroci_df.empty:
            st.info(t("incroci.list.no_crosses", "Nessun incrocio trovato"))
            return
        
        # Mostra numero totale incroci
        st.write(t("incroci.list.total_found", "**Totale incroci trovati: {count}**").format(count=len(incroci_df)))
        
        # Gestione conferma eliminazione
        if st.session_state.get('mostra_conferma_eliminazione', False) and st.session_state.get('incrocio_da_eliminare'):
            incrocio_id = st.session_state.incrocio_da_eliminare
            st.warning(t("incroci.list.delete_warning", "⚠️ **Attenzione**: Stai per eliminare l'incrocio {cross_id}").format(cross_id=incrocio_id))
            st.info(t("incroci.list.delete_irreversible", "Questa azione è irreversibile e eliminerà tutti i dati correlati (account e bonus)"))
            
            col_confirm1, col_confirm2 = st.columns(2)
            
            with col_confirm1:
                if st.button("❌ Conferma Eliminazione", key="confirm_elimina_finale", type="primary"):
                    st.info(t("incroci.list.delete_in_progress", "🔄 Eliminazione incrocio {cross_id} in corso...").format(cross_id=incrocio_id))
                    
                    success = self.incroci_manager.elimina_incrocio(incrocio_id)
                    
                    if success:
                        st.success(t("incroci.list.delete_success", "✅ Incrocio eliminato con successo!"))
                        
                        st.session_state.incroci_aggiornati = True
                        st.session_state.ultimo_eliminato = incrocio_id
                        st.session_state.ultimo_aggiornamento = int(time.time())
                        
                        # Reset dello stato
                        st.session_state.mostra_conferma_eliminazione = False
                        st.session_state.incrocio_da_eliminare = None
                        
                        st.success(t("incroci.list.delete_completed", "✅ **Eliminazione completata!** Clicca '🔄 Aggiorna Lista' per vedere i cambiamenti."))
                        st.rerun()
                    else:
                        st.error(t("incroci.list.delete_error", "❌ Errore nell'eliminazione dell'incrocio"))
                        # Reset dello stato in caso di errore
                        st.session_state.mostra_conferma_eliminazione = False
                        st.session_state.incrocio_da_eliminare = None
            
            with col_confirm2:
                if st.button("🔙 Annulla", key="cancel_elimina_finale"):
                    # Reset dello stato
                    st.session_state.mostra_conferma_eliminazione = False
                    st.session_state.incrocio_da_eliminare = None
                    st.rerun()
        
        # Gestione chiusura incroci
        if st.session_state.get('incrocio_da_chiudere'):
            incrocio_id = st.session_state.incrocio_da_chiudere
            self.chiudi_incrocio(incrocio_id)
            return
        
        # Mostra incroci in una tabella interattiva
        for _, incrocio in incroci_df.iterrows():
            with st.expander(f"🔄 {incrocio['nome_incrocio']} - {incrocio['pair_trading']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(t("incroci.details.long_account", "**Account Long:**"))
                    st.write(t("incroci.details.client", "Cliente: {client}").format(client=incrocio['cliente_long']))
                    st.write(t("incroci.details.broker", "Broker: {broker}").format(broker=incrocio['broker_long']))
                    st.write(t("incroci.details.account", "Conto: {account}").format(account=incrocio['conto_long']))
                    volume_long = incrocio.get('volume_long', 0) or 0
                    st.write(t("incroci.details.volume", "Volume: {volume}").format(volume=f"{volume_long:,.0f}"))
                
                with col2:
                    st.write(t("incroci.details.short_account", "**Account Short:**"))
                    st.write(t("incroci.details.client", "Cliente: {client}").format(client=incrocio['cliente_short']))
                    st.write(t("incroci.details.broker", "Broker: {broker}").format(broker=incrocio['broker_short']))
                    st.write(t("incroci.details.account", "Conto: {account}").format(account=incrocio['conto_short']))
                    volume_short = incrocio.get('volume_short', 0) or 0
                    st.write(t("incroci.details.volume", "Volume: {volume}").format(volume=f"{volume_short:,.0f}"))
                
                with col3:
                    st.write(t("incroci.details.details", "**Dettagli:**"))
                    st.write(t("incroci.details.status", "Stato: {status}").format(status=incrocio['stato']))
                    st.write(t("incroci.details.opening", "Apertura: {date}").format(date=incrocio['data_apertura']))
                    if pd.notna(incrocio['data_chiusura']):
                        st.write(t("incroci.details.closing", "Chiusura: {date}").format(date=incrocio['data_chiusura']))
                    bonus_totale = incrocio.get('totale_bonus', 0) or 0
                    st.write(t("incroci.details.bonus", "Bonus: ${bonus}").format(bonus=f"{bonus_totale:,.0f}"))
                
                # Azioni
                col_azioni1, col_azioni2, col_azioni3, col_azioni4 = st.columns(4)
                
                with col_azioni1:
                    if st.button(f"👁️ Dettagli", key=f"dett_{incrocio['id']}"):
                        self.mostra_dettagli_incrocio(incrocio['id'])
                
                with col_azioni2:
                    if incrocio['stato'] == 'attivo':
                        if st.button(f"❌ Chiudi", key=f"chiudi_{incrocio['id']}"):
                            st.session_state.incrocio_da_chiudere = incrocio['id']
                            st.rerun()
                
                with col_azioni3:
                    if st.button(f"📝 Modifica", key=f"mod_{incrocio['id']}"):
                        st.info(t("incroci.details.edit_development", "Funzionalità di modifica in sviluppo"))
                
                with col_azioni4:
                    if st.button(f"🗑️ Elimina", key=f"elimina_{incrocio['id']}", type="secondary"):
                        # Invece di chiamare il metodo, impostiamo lo stato
                        st.session_state.incrocio_da_eliminare = incrocio['id']
                        st.session_state.mostra_conferma_eliminazione = True
                        st.rerun()
    
    def render_nuovo_incrocio(self):
        """Rende il form per creare un nuovo incrocio"""
        st.subheader("➕ Nuovo Incrocio")
        
        with st.form("nuovo_incrocio_form"):
            # Informazioni generali
            st.write("**Informazioni Generali**")
            nome_incrocio = st.text_input("Nome Incrocio", placeholder="es. Incrocio EURUSD Gennaio")
            # Pair trading ordinati alfabeticamente
            pair_options = ["AUD/USD", "EUR/USD", "GBP/USD", "USD/CAD", "USD/JPY", "Altro"]
            pair_trading = st.selectbox("Pair Trading", pair_options)
            volume_trading = st.number_input("Volume Trading (lotti)", min_value=0.01, value=1.0, step=0.01)
            data_apertura = st.date_input("Data Apertura", value=date.today())
            note = st.text_area("Note", placeholder="Note aggiuntive sull'incrocio")
            
            st.divider()
            
            # Info auto-caricamento
            st.info("💡 **Auto-caricamento**: I campi Broker e Numero Conto si compilano automaticamente quando selezioni un cliente")
            
            # Account Long
            st.write("**Account Long (Buy)**")
            col_long1, col_long2 = st.columns(2)
            
            with col_long1:
                account_long_id = st.selectbox(
                    "Cliente Long",
                    options=self.get_clienti_options(),
                    key="long_cliente"
                )
                
                # Auto-carica i dati del cliente selezionato
                if account_long_id:
                    cliente_id = account_long_id[1] if isinstance(account_long_id, tuple) else account_long_id
                    cliente_info = self.get_cliente_info(cliente_id)
                    if cliente_info:
                        st.session_state.long_broker = cliente_info['broker']
                        st.session_state.long_conto = cliente_info['numero_conto']
                
                broker_long_input = st.text_input("Broker Long", value=st.session_state.get('long_broker', ''), key="long_broker_input", disabled=True)
                # Piattaforme ordinate alfabeticamente
                piattaforme_options = ["cTrader", "MT4", "MT5", "Altro"]
                piattaforma_long = st.selectbox("Piattaforma Long", piattaforme_options, index=0, key="long_piattaforma")
            
            with col_long2:
                conto_long_input = st.text_input("Numero Conto Long", value=st.session_state.get('long_conto', ''), key="long_conto_input", disabled=True)
                volume_long = st.number_input("Volume Long", min_value=0.01, value=volume_trading, step=0.01, key="long_volume")
            
            st.divider()
            
            # Account Short
            st.write("**Account Short (Sell)**")
            col_short1, col_short2 = st.columns(2)
            
            with col_short1:
                account_short_id = st.selectbox(
                    "Cliente Short",
                    options=self.get_clienti_options(),
                    key="short_cliente"
                )
                
                # Auto-carica i dati del cliente selezionato
                if account_short_id:
                    cliente_id = account_short_id[1] if isinstance(account_short_id, tuple) else account_long_id
                    cliente_info = self.get_cliente_info(cliente_id)
                    if cliente_info:
                        st.session_state.short_broker = cliente_info['broker']
                        st.session_state.short_conto = cliente_info['numero_conto']
                
                broker_short_input = st.text_input("Broker Short", value=st.session_state.get('short_broker', ''), key="short_broker_input", disabled=True)
                # Piattaforme ordinate alfabeticamente
                piattaforme_options = ["cTrader", "MT4", "MT5", "Altro"]
                piattaforma_short = st.selectbox("Piattaforma Short", piattaforme_options, index=0, key="short_piattaforma")
            
            with col_short2:
                conto_short_input = st.text_input("Numero Conto Short", value=st.session_state.get('short_conto', ''), key="short_conto_input", disabled=True)
                volume_short = st.number_input("Volume Short", min_value=0.01, value=volume_trading, step=0.01, key="short_volume")
            
            st.divider()
            
            # Bonus CPA - Sempre visibili
            st.write("**Bonus CPA**")
            st.info("💡 **Opzionale**: Compila i campi bonus se vuoi tracciare i bonus CPA sbloccati")
            
            col_bonus1, col_bonus2, col_bonus3 = st.columns(3)
            
            with col_bonus1:
                tipo_bonus = st.text_input("Tipo Bonus", placeholder="es. Welcome Bonus", key="bonus_tipo")
            
            with col_bonus2:
                importo_bonus = st.number_input("Importo Bonus", min_value=0.01, value=100.0, step=0.01, key="bonus_importo")
            
            with col_bonus3:
                # Valute ordinate alfabeticamente
                valute_options = ["EUR", "GBP", "USD"]
                valuta_bonus = st.selectbox("Valuta", valute_options, key="bonus_valuta")
            
            # Mostra bonus configurato se compilato
            bonus_list = []
            if tipo_bonus and importo_bonus:
                st.info(f"💡 **Bonus configurato**: {tipo_bonus} - {importo_bonus} {valuta_bonus}")
                bonus_list.append({
                    'tipo': tipo_bonus,
                    'importo': importo_bonus,
                    'valuta': valuta_bonus
                })
            else:
                st.info("💡 **Bonus opzionale**: Lascia vuoto se non vuoi tracciare bonus")
            
            # Pulsante creazione
            if st.form_submit_button("🚀 Crea Incrocio"):
                if self.validazione_incrocio(nome_incrocio, account_long_id, account_short_id):
                    # Ottieni i dati dalla session state
                    broker_long = st.session_state.get('long_broker', '')
                    conto_long = st.session_state.get('long_conto', '')
                    broker_short = st.session_state.get('short_broker', '')
                    conto_short = st.session_state.get('short_conto', '')
                    
                    # Debug: mostra i dati che verranno salvati
                    st.write("🔍 **Debug - Dati da salvare:**")
                    st.write(f"Broker Long: {broker_long}")
                    st.write(f"Conto Long: {conto_long}")
                    st.write(f"Broker Short: {broker_short}")
                    st.write(f"Conto Short: {conto_short}")
                    
                    success = self.crea_incrocio({
                        'nome_incrocio': nome_incrocio,
                        'data_apertura': data_apertura,
                        'pair_trading': pair_trading,
                        'volume_trading': volume_trading,
                        'note': note,
                        'account_long_id': account_long_id,
                        'broker_long': broker_long,
                        'piattaforma_long': piattaforma_long,
                        'conto_long': conto_long,
                        'volume_long': volume_long,
                        'account_short_id': account_short_id,
                        'broker_short': broker_short,
                        'piattaforma_short': piattaforma_short,
                        'conto_short': conto_short,
                        'volume_short': volume_short,
                        'bonus': bonus_list
                    })
                    
                    if success:
                        st.success("✅ Incrocio creato con successo!")
                        st.rerun()
                    else:
                        st.error("❌ Errore nella creazione dell'incrocio")
                else:
                    st.error("❌ Dati mancanti o non validi")
    
    def render_statistiche(self):
        """Rende le statistiche degli incroci"""
        st.subheader("📊 Statistiche Incroci")
        
        stats = self.incroci_manager.ottieni_statistiche_incroci()
        if not stats:
            st.info("Nessuna statistica disponibile")
            return
        
        # Metriche generali
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Totale Incroci", stats['generali']['totale_incroci'])
        
        with col2:
            st.metric("Incroci Attivi", stats['generali']['incroci_attivi'])
        
        with col3:
            st.metric("Volume Totale", f"{stats['generali']['volume_totale']:,.0f}")
        
        with col4:
            st.metric("Bonus Totali", f"${stats['bonus']['totale_bonus']:,.0f}")
        
        st.divider()
        
        # Grafici
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.write("**Incroci per Pair**")
            if stats['per_pair']:
                pair_data = pd.DataFrame(stats['per_pair'], columns=['Pair', 'Utilizzi', 'Volume'])
                fig = px.pie(pair_data, values='Utilizzi', names='Pair', title="Distribuzione per Pair")
                st.plotly_chart(fig, width='stretch')
        
        with col_chart2:
            st.write("**Incroci per Broker**")
            if stats['per_broker']:
                broker_data = pd.DataFrame(stats['per_broker'], columns=['Broker', 'Utilizzi', 'Incroci Unici'])
                fig = px.bar(broker_data, x='Broker', y='Utilizzi', title="Utilizzo per Broker")
                st.plotly_chart(fig, width='stretch')
        
        # Tabella dettagliata
        st.write("**Dettagli per Pair**")
        if stats['per_pair']:
            pair_df = pd.DataFrame(stats['per_pair'], columns=['Pair', 'Utilizzi', 'Volume Totale'])
            st.dataframe(pair_df, width='stretch')
    
    def render_ricerca(self):
        """Rende la ricerca incroci"""
        st.subheader("🔍 Ricerca Incroci")
        
        query = st.text_input("Cerca per nome, pair, broker o cliente", placeholder="Inserisci termine di ricerca...")
        
        if query:
            st.info("Funzionalità di ricerca in sviluppo")
        else:
            st.info("Inserisci un termine di ricerca per iniziare")
    
    def get_clienti_options(self) -> List[tuple]:
        """Ottiene la lista dei clienti per i selectbox da Supabase"""
        try:
            if self.supabase_manager:
                # Usa Supabase per i clienti
                clienti = self.supabase_manager.get_clienti()
                if clienti:
                    options = [(f"{cliente['nome_cliente']} ({cliente['broker']})", cliente['id']) for cliente in clienti]
                    return options
                else:
                    st.warning("⚠️ Nessun cliente trovato in Supabase. Aggiungi prima alcuni clienti!")
                    return []
            else:
                # Fallback al database locale se Supabase non è disponibile
                clienti_df = self.database_manager.ottieni_tutti_clienti()
                if not clienti_df.empty:
                    options = [(f"{row['nome_cliente']} ({row['broker']})", row['id']) for _, row in clienti_df.iterrows()]
                    return options
                else:
                    st.warning("⚠️ Nessun cliente trovato nel database. Aggiungi prima alcuni clienti!")
                    return []
        except Exception as e:
            st.error(f"❌ Errore nel caricamento clienti: {e}")
            return []
    
    def validazione_incrocio(self, nome: str, account_long: int, account_short: int) -> bool:
        """Valida i dati dell'incrocio"""
        if not nome or not account_long or not account_short:
            return False
        
        if account_long == account_short:
            st.error("❌ Gli account long e short devono essere diversi")
            return False
        
        return True
    
    def crea_incrocio(self, dati: Dict) -> bool:
        """Crea un nuovo incrocio"""
        try:
            # Estrai solo l'ID dal tuple se account_long_id o account_short_id sono tuple
            if isinstance(dati['account_long_id'], tuple):
                dati['account_long_id'] = dati['account_long_id'][1]
            if isinstance(dati['account_short_id'], tuple):
                dati['account_short_id'] = dati['account_short_id'][1]
            
            success, incrocio_id = self.incroci_manager.crea_incrocio(dati)
            return success
        except Exception as e:
            logging.error(f"Errore creazione incrocio: {e}")
            return False
    
    def render_chiusura_incroci(self):
        """Rende l'interfaccia per chiudere gli incroci"""
        try:
            from components.incroci_close_manager import IncrociCloseManager
            
            close_manager = IncrociCloseManager()
            close_manager.render_close_cross_interface()
            
        except Exception as e:
            st.error(f"❌ Errore caricamento interfaccia chiusura incroci: {e}")
            logging.error(f"Errore render_chiusura_incroci: {e}")
    

    
    def get_cliente_info(self, cliente_id: int) -> Dict:
        """Ottiene le informazioni di un cliente specifico da Supabase"""
        try:
            if self.supabase_manager:
                # Usa Supabase per le info cliente
                clienti = self.supabase_manager.get_clienti()
                for cliente in clienti:
                    if str(cliente['id']) == str(cliente_id):
                        return cliente
                return {}
            else:
                # Fallback al database locale se Supabase non è disponibile
                clienti_df = self.database_manager.ottieni_tutti_clienti()
                cliente = clienti_df[clienti_df['id'] == cliente_id]
                if not cliente.empty:
                    return cliente.iloc[0].to_dict()
                return {}
        except Exception as e:
            logging.error(f"Errore recupero info cliente: {e}")
            return {}
    
    def mostra_dettagli_incrocio(self, incrocio_id: int):
        """Mostra i dettagli completi di un incrocio"""
        st.write("**Dettagli Completi Incrocio**")
        st.info("Funzionalità di dettagli in sviluppo")
    
    def chiudi_incrocio(self, incrocio_id: str):
        """Chiude un incrocio attivo con bilanciamento automatico"""
        try:
            from components.incroci_close_manager import IncrociCloseManager
            
            # Usa il nuovo sistema di chiusura
            close_manager = IncrociCloseManager()
            
            # Recupera informazioni incrocio
            incroci = self.incroci_manager.ottieni_incroci()
            incrocio_data = None
            
            for _, incrocio in incroci.iterrows():
                if incrocio['id'] == incrocio_id:
                    incrocio_data = incrocio
                    break
            
            if incrocio_data is None:
                st.error("❌ Incrocio non trovato")
                return
            
            # Mostra informazioni incrocio
            st.markdown(f"### 🔄 Chiusura: {incrocio_data['nome_incrocio']}")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write("**👤 Cliente Long (Buy)**")
                st.write(f"**Nome:** {incrocio_data['cliente_long']}")
                st.write(f"**Conto:** {incrocio_data['conto_long']}")
                st.write(f"**Broker:** {incrocio_data['broker_long']}")
            
            with col_info2:
                st.write("**👤 Cliente Short (Sell)**")
                st.write(f"**Nome:** {incrocio_data['cliente_short']}")
                st.write(f"**Conto:** {incrocio_data['conto_short']}")
                st.write(f"**Broker:** {incrocio_data['broker_short']}")
            
            # Form chiusura
            st.markdown("---")
            st.markdown("### 💰 Inserisci Saldi Attuali")
            
            col_saldi1, col_saldi2 = st.columns(2)
            
            with col_saldi1:
                saldo_long_attuale = st.number_input(
                    "💰 Saldo Cliente Long (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Inserisci il saldo attuale del conto Long",
                    key=f"saldo_long_{incrocio_id}"
                )
            
            with col_saldi2:
                saldo_short_attuale = st.number_input(
                    "💰 Saldo Cliente Short (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Inserisci il saldo attuale del conto Short",
                    key=f"saldo_short_{incrocio_id}"
                )
            
            st.markdown("---")
            st.markdown("### 🏆 Risultato Incrocio")
            
            vincitore = st.radio(
                "🎯 Chi ha vinto l'incrocio?",
                options=["long", "short"],
                format_func=lambda x: {
                    "long": f"👤 {incrocio_data['cliente_long']} (Long/Buy)",
                    "short": f"👤 {incrocio_data['cliente_short']} (Short/Sell)"
                }[x],
                help="Seleziona chi ha vinto l'incrocio",
                key=f"vincitore_{incrocio_id}"
            )
            
            # Note aggiuntive
            note_chiusura = st.text_area(
                "📝 Note Chiusura",
                placeholder="Note aggiuntive sulla chiusura dell'incrocio...",
                help="Note opzionali per la chiusura",
                key=f"note_chiusura_{incrocio_id}"
            )
            
            # Pulsanti
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✅ Chiudi Incrocio", type="primary", key=f"confirm_close_{incrocio_id}"):
                    if saldo_long_attuale > 0 and saldo_short_attuale > 0:
                        # Prepara dati per la chiusura
                        incrocio_dict = {
                            'id': incrocio_id,
                            'nome_incrocio': incrocio_data['nome_incrocio'],
                            'pair_trading': incrocio_data['pair_trading'],
                            'cliente_long': {'id': incrocio_data.get('cliente_long_id', ''), 'nome_cliente': incrocio_data['cliente_long']},
                            'cliente_short': {'id': incrocio_data.get('cliente_short_id', ''), 'nome_cliente': incrocio_data['cliente_short']},
                            'note': incrocio_data.get('note', '')
                        }
                        
                        success, message = close_manager._close_cross(
                            incrocio=incrocio_dict,
                            saldo_long_attuale=saldo_long_attuale,
                            saldo_short_attuale=saldo_short_attuale,
                            vincitore=vincitore,
                            note_chiusura=note_chiusura
                        )
                        
                        if success:
                            st.success(message)
                            st.balloons()
                            st.session_state.incrocio_da_chiudere = None
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("❌ Inserisci saldi validi per entrambi i clienti")
            
            with col_btn2:
                if st.button("❌ Annulla", key=f"cancel_close_{incrocio_id}"):
                    st.session_state.incrocio_da_chiudere = None
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Errore chiusura incrocio: {e}")
            logging.error(f"Errore chiudi_incrocio: {e}")


