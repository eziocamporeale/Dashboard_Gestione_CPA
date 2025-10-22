"""
🔄 INCROCI CLOSE MANAGER
Gestione chiusura incroci con bilanciamento automatico saldi
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncrociCloseManager:
    """Gestore per la chiusura degli incroci con bilanciamento automatico"""
    
    def __init__(self):
        """Inizializza il gestore chiusura incroci"""
        self.supabase_manager = None
        self.wallet_manager = None
        self._init_managers()
    
    def _init_managers(self):
        """Inizializza i manager necessari"""
        try:
            from supabase_manager import SupabaseManager
            from components.wallet_transactions_manager import WalletTransactionsManager
            
            self.supabase_manager = SupabaseManager()
            self.wallet_manager = WalletTransactionsManager()
            
            if not self.supabase_manager.is_configured:
                logger.warning("⚠️ Supabase non configurato per IncrociCloseManager")
                self.supabase_manager = None
            
            logger.info("✅ IncrociCloseManager inizializzato correttamente")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione IncrociCloseManager: {e}")
            self.supabase_manager = None
            self.wallet_manager = None
    
    def get_active_crosses(self) -> List[Dict[str, Any]]:
        """Recupera tutti gli incroci attivi"""
        if not self.supabase_manager:
            return []
        
        try:
            # Query per incroci attivi con informazioni clienti
            response = self.supabase_manager.supabase.table('incroci').select('''
                *,
                incroci_account!inner(*)
            ''').eq('stato', 'attivo').order('data_apertura', desc=True).execute()
            
            if not response.data:
                return []
            
            # Organizza i dati per incrocio
            incroci_data = {}
            for incrocio in response.data:
                incrocio_id = incrocio['id']
                if incrocio_id not in incroci_data:
                    incroci_data[incrocio_id] = {
                        'id': incrocio_id,
                        'nome_incrocio': incrocio['nome_incrocio'],
                        'data_apertura': incrocio['data_apertura'],
                        'pair_trading': incrocio['pair_trading'],
                        'volume_trading': incrocio.get('volume_trading', 0),
                        'note': incrocio.get('note', ''),
                        'accounts': []
                    }
                
                # Aggiungi account
                for account in incrocio.get('incroci_account', []):
                    incroci_data[incrocio_id]['accounts'].append(account)
            
            # Converti in lista e aggiungi informazioni clienti
            incroci_list = []
            for incrocio_id, incrocio_data in incroci_data.items():
                # Trova account long e short
                account_long = None
                account_short = None
                
                for account in incrocio_data['accounts']:
                    if account['tipo_posizione'] == 'long':
                        account_long = account
                    elif account['tipo_posizione'] == 'short':
                        account_short = account
                
                if account_long and account_short:
                    # Recupera informazioni clienti
                    cliente_long_info = self._get_cliente_info(account_long['numero_conto'])
                    cliente_short_info = self._get_cliente_info(account_short['numero_conto'])
                    
                    incroci_list.append({
                        'id': incrocio_id,
                        'nome_incrocio': incrocio_data['nome_incrocio'],
                        'data_apertura': incrocio_data['data_apertura'],
                        'pair_trading': incrocio_data['pair_trading'],
                        'volume_trading': incrocio_data['volume_trading'],
                        'note': incrocio_data['note'],
                        'cliente_long': cliente_long_info,
                        'cliente_short': cliente_short_info,
                        'account_long': account_long,
                        'account_short': account_short
                    })
            
            return incroci_list
            
        except Exception as e:
            logger.error(f"❌ Errore recupero incroci attivi: {e}")
            return []
    
    def _get_cliente_info(self, numero_conto: str) -> Optional[Dict[str, Any]]:
        """Recupera informazioni cliente dal numero conto"""
        if not self.supabase_manager:
            return None
        
        try:
            response = self.supabase_manager.supabase.table('clienti').select('id, nome_cliente, wallet').eq('numero_conto', numero_conto).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ Errore recupero cliente {numero_conto}: {e}")
            return None
    
    def render_close_cross_interface(self):
        """Rende l'interfaccia per chiudere gli incroci"""
        
        st.subheader("🔄 Chiusura Incroci con Bilanciamento")
        st.info("💡 **Seleziona un incrocio attivo e inserisci i saldi attuali per chiuderlo**")
        
        # Recupera incroci attivi
        incroci_attivi = self.get_active_crosses()
        
        if not incroci_attivi:
            st.info("📋 Nessun incrocio attivo disponibile per la chiusura.")
            return
        
        # Seleziona incrocio
        st.markdown("### 📋 Seleziona Incrocio da Chiudere")
        
        incrocio_options = []
        for incrocio in incroci_attivi:
            cliente_long_nome = incrocio['cliente_long']['nome_cliente'] if incrocio['cliente_long'] else 'N/A'
            cliente_short_nome = incrocio['cliente_short']['nome_cliente'] if incrocio['cliente_short'] else 'N/A'
            option_text = f"{incrocio['nome_incrocio']} - {cliente_long_nome} vs {cliente_short_nome} ({incrocio['pair_trading']})"
            incrocio_options.append((option_text, incrocio))
        
        selected_option = st.selectbox(
            "🎯 Incrocio da Chiudere",
            options=[opt[0] for opt in incrocio_options],
            help="Seleziona l'incrocio che vuoi chiudere"
        )
        
        if selected_option:
            # Trova l'incrocio selezionato
            selected_incrocio = None
            for option_text, incrocio in incrocio_options:
                if option_text == selected_option:
                    selected_incrocio = incrocio
                    break
            
            if selected_incrocio:
                self._render_close_form(selected_incrocio)
    
    def _render_close_form(self, incrocio: Dict[str, Any]):
        """Rende il form per chiudere un incrocio specifico"""
        
        st.markdown("---")
        st.markdown(f"### 🔄 Chiusura: {incrocio['nome_incrocio']}")
        
        # Mostra informazioni incrocio
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.write("**📊 Informazioni Incrocio**")
            st.write(f"**Pair:** {incrocio['pair_trading']}")
            st.write(f"**Volume:** {incrocio['volume_trading']} lotti")
            st.write(f"**Apertura:** {incrocio['data_apertura']}")
        
        with col_info2:
            st.write("**👤 Cliente Long (Buy)**")
            cliente_long = incrocio['cliente_long']
            if cliente_long:
                st.write(f"**Nome:** {cliente_long['nome_cliente']}")
                st.write(f"**Conto:** {incrocio['account_long']['numero_conto']}")
                st.write(f"**Broker:** {incrocio['account_long']['broker']}")
            else:
                st.error("❌ Cliente Long non trovato")
        
        with col_info3:
            st.write("**👤 Cliente Short (Sell)**")
            cliente_short = incrocio['cliente_short']
            if cliente_short:
                st.write(f"**Nome:** {cliente_short['nome_cliente']}")
                st.write(f"**Conto:** {incrocio['account_short']['numero_conto']}")
                st.write(f"**Broker:** {incrocio['account_short']['broker']}")
            else:
                st.error("❌ Cliente Short non trovato")
        
        # Form chiusura
        st.markdown("---")
        st.markdown("### 💰 Inserisci Saldi Attuali")
        
        with st.form("close_cross_form", clear_on_submit=False):
            col_saldi1, col_saldi2 = st.columns(2)
            
            with col_saldi1:
                st.write("**👤 Saldo Cliente Long**")
                saldo_long_attuale = st.number_input(
                    "💰 Saldo Attuale (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Inserisci il saldo attuale del conto Long",
                    key=f"saldo_long_{incrocio['id']}"
                )
            
            with col_saldi2:
                st.write("**👤 Saldo Cliente Short**")
                saldo_short_attuale = st.number_input(
                    "💰 Saldo Attuale (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Inserisci il saldo attuale del conto Short",
                    key=f"saldo_short_{incrocio['id']}"
                )
            
            st.markdown("---")
            st.markdown("### 🏆 Risultato Incrocio")
            
            vincitore = st.radio(
                "🎯 Chi ha vinto l'incrocio?",
                options=["long", "short"],
                format_func=lambda x: {
                    "long": f"👤 {incrocio['cliente_long']['nome_cliente']} (Long/Buy)",
                    "short": f"👤 {incrocio['cliente_short']['nome_cliente']} (Short/Sell)"
                }[x],
                help="Seleziona chi ha vinto l'incrocio"
            )
            
            # Note aggiuntive
            note_chiusura = st.text_area(
                "📝 Note Chiusura",
                placeholder="Note aggiuntive sulla chiusura dell'incrocio...",
                help="Note opzionali per la chiusura"
            )
            
            # Pulsanti
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit_button = st.form_submit_button(
                    "✅ Chiudi Incrocio",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                if saldo_long_attuale > 0 and saldo_short_attuale > 0:
                    success, message = self._close_cross(
                        incrocio=incrocio,
                        saldo_long_attuale=saldo_long_attuale,
                        saldo_short_attuale=saldo_short_attuale,
                        vincitore=vincitore,
                        note_chiusura=note_chiusura
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Inserisci saldi validi per entrambi i clienti")
            
            if cancel_button:
                st.rerun()
    
    def _close_cross(self, incrocio: Dict[str, Any], saldo_long_attuale: float, 
                    saldo_short_attuale: float, vincitore: str, note_chiusura: str) -> Tuple[bool, str]:
        """Chiude un incrocio con bilanciamento automatico"""
        
        try:
            # 1. Aggiorna stato incrocio nel database
            if not self.supabase_manager:
                return False, "❌ Supabase non configurato"
            
            # Aggiorna incrocio
            update_data = {
                'stato': 'chiuso',
                'data_chiusura': datetime.now().isoformat(),
                'note': f"{incrocio.get('note', '')}\n\nChiusura: {note_chiusura}".strip()
            }
            
            response = self.supabase_manager.supabase.table('incroci').update(update_data).eq('id', incrocio['id']).execute()
            
            if not response.data:
                return False, "❌ Errore aggiornamento stato incrocio"
            
            # 2. Crea transazione wallet per tracciare la chiusura
            if self.wallet_manager and incrocio['cliente_long'] and incrocio['cliente_short']:
                wallet_success, wallet_message = self.wallet_manager.close_cross_transaction(
                    incrocio_id=incrocio['id'],
                    cliente_long_id=incrocio['cliente_long']['id'],
                    cliente_short_id=incrocio['cliente_short']['id'],
                    saldo_long_attuale=saldo_long_attuale,
                    saldo_short_attuale=saldo_short_attuale,
                    vincitore=vincitore,
                    pair_trading=incrocio['pair_trading']
                )
                
                if wallet_success:
                    logger.info(f"✅ Transazione wallet chiusura creata per incrocio {incrocio['id']}")
                else:
                    logger.warning(f"⚠️ Errore transazione wallet: {wallet_message}")
            
            # 3. Calcola P&L per il messaggio di successo
            if vincitore == 'long':
                pnl_long = saldo_long_attuale
                pnl_short = -saldo_short_attuale
                vincitore_nome = incrocio['cliente_long']['nome_cliente']
            else:
                pnl_long = -saldo_long_attuale
                pnl_short = saldo_short_attuale
                vincitore_nome = incrocio['cliente_short']['nome_cliente']
            
            success_message = f"✅ **Incrocio chiuso con successo!**\n\n"
            success_message += f"🏆 **Vincitore:** {vincitore_nome}\n"
            success_message += f"💰 **P&L Long:** {pnl_long:.2f} USDT\n"
            success_message += f"💰 **P&L Short:** {pnl_short:.2f} USDT\n"
            success_message += f"📊 **Pair:** {incrocio['pair_trading']}\n"
            success_message += f"📅 **Data chiusura:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            return True, success_message
            
        except Exception as e:
            logger.error(f"❌ Errore chiusura incrocio: {e}")
            return False, f"❌ Errore chiusura incrocio: {e}"
