"""
💰 WALLET MANAGEMENT
Gestione completa dei wallet per amministratori
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletManagement:
    """Gestione completa dei wallet per amministratori"""
    
    def __init__(self, wallet_manager):
        """Inizializza il gestore wallet"""
        self.wallet_manager = wallet_manager
    
    def render_wallet_management(self):
        """Rende l'interfaccia di gestione wallet per admin"""
        
        st.subheader("🔧 Gestione Wallet (Admin)")
        st.info("👑 **Accesso Amministratore**: Gestisci wallet, saldi e configurazioni")
        
        # Tab per organizzare le funzionalità
        tab_wallets, tab_add_wallet, tab_edit_saldo = st.tabs([
            "📋 Lista Wallet", "➕ Aggiungi Wallet", "💰 Modifica Saldi"
        ])
        
        # TAB 1: Lista Wallet
        with tab_wallets:
            self._render_wallet_list()
        
        # TAB 2: Aggiungi Wallet
        with tab_add_wallet:
            self._render_add_wallet_form()
        
        # TAB 3: Modifica Saldi
        with tab_edit_saldo:
            self._render_edit_saldo_form()
    
    def _render_wallet_list(self):
        """Rende la lista dei wallet con azioni admin"""
        
        st.subheader("📋 Wallet Esistenti")
        
        # Ottieni wallet
        wallets = self.wallet_manager.get_wallet_collaboratori()
        
        if not wallets:
            st.info("📋 Nessun wallet presente.")
            return
        
        # Mostra wallet in formato tabella
        for wallet in wallets:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**💰 {wallet['nome_wallet']}**")
                    st.write(f"👤 {wallet['proprietario']}")
                
                with col2:
                    st.write(f"📋 {wallet['tipo_wallet']}")
                    st.write(f"💱 {wallet.get('valuta', 'USD')}")
                
                with col3:
                    saldo = self.wallet_manager.get_wallet_balance(wallet['nome_wallet'])
                    if saldo > 0:
                        st.success(f"💚 {saldo:.2f}")
                    elif saldo < 0:
                        st.error(f"💔 {saldo:.2f}")
                    else:
                        st.info(f"⚪ {saldo:.2f}")
                
                with col4:
                    if st.button("✏️", key=f"edit_wallet_{wallet['id']}", help="Modifica wallet"):
                        st.session_state.editing_wallet = wallet
                        st.rerun()
                
                with col5:
                    # Usa un approccio più semplice con checkbox per conferma
                    delete_key = f"delete_wallet_{wallet['id']}"
                    confirm_key = f"confirm_delete_{wallet['id']}"
                    
                    if st.button("🗑️", key=delete_key, help="Elimina wallet"):
                        # Mostra checkbox di conferma
                        st.session_state[f"show_confirm_{wallet['id']}"] = True
                        st.rerun()
                    
                    # Mostra checkbox di conferma se necessario
                    if st.session_state.get(f"show_confirm_{wallet['id']}", False):
                        if st.checkbox("✅ Conferma eliminazione", key=confirm_key):
                            success, message = self._delete_wallet(wallet['id'])
                            if success:
                                st.success(message)
                                st.balloons()
                                st.session_state[f"show_confirm_{wallet['id']}"] = False
                                st.rerun()
                            else:
                                st.error(message)
                                st.session_state[f"show_confirm_{wallet['id']}"] = False
                
                # Note
                if wallet.get('note'):
                    st.write(f"📝 **Note:** {wallet['note']}")
                
                st.markdown("---")
        
        # Form modifica wallet
        if 'editing_wallet' in st.session_state:
            self._render_edit_wallet_form(st.session_state.editing_wallet)
    
    def _render_add_wallet_form(self):
        """Rende il form per aggiungere un nuovo wallet"""
        
        st.subheader("➕ Aggiungi Nuovo Wallet")
        
        with st.form("add_wallet_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_wallet = st.text_input(
                    "💰 Nome Wallet",
                    placeholder="Es: Wallet_Collaboratore_3",
                    help="Nome univoco del wallet"
                )
                
                proprietario = st.text_input(
                    "👤 Proprietario",
                    placeholder="Es: Collaboratore 3",
                    help="Nome del proprietario del wallet"
                )
                
                tipo_wallet = st.selectbox(
                    "📋 Tipo Wallet",
                    options=["principale", "collaboratore", "cliente"],
                    format_func=lambda x: {
                        "principale": "🏠 Principale",
                        "collaboratore": "👥 Collaboratore", 
                        "cliente": "👤 Cliente"
                    }[x],
                    help="Tipo di wallet"
                )
            
            with col2:
                valuta = st.selectbox(
                    "💱 Valuta",
                    options=["USD", "EUR", "GBP", "BTC", "ETH"],
                    index=0,
                    help="Valuta del wallet"
                )
                
                saldo_iniziale = st.number_input(
                    "💰 Saldo Iniziale",
                    min_value=0.0,
                    max_value=1000000.0,
                    step=0.01,
                    value=0.0,
                    format="%.2f",
                    help="Saldo iniziale del wallet"
                )
                
                attivo = st.checkbox(
                    "✅ Wallet Attivo",
                    value=True,
                    help="Se il wallet è attivo"
                )
            
            # Note
            note = st.text_area(
                "📝 Note",
                placeholder="Note aggiuntive sul wallet...",
                help="Note opzionali"
            )
            
            # Pulsanti
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit_button = st.form_submit_button(
                    "💾 Crea Wallet",
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
                if not nome_wallet.strip():
                    st.error("❌ Il nome del wallet è obbligatorio")
                else:
                    wallet_data = {
                        'nome_wallet': nome_wallet.strip(),
                        'proprietario': proprietario.strip() or nome_wallet.strip(),
                        'tipo_wallet': tipo_wallet,
                        'valuta': valuta,
                        'saldo_attuale': float(saldo_iniziale),
                        'attivo': attivo,
                        'note': note.strip() if note else None
                    }
                    
                    success, message = self._add_wallet(wallet_data)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            if cancel_button:
                st.rerun()
    
    def _render_edit_wallet_form(self, wallet_data: Dict[str, Any]):
        """Rende il form per modificare un wallet esistente"""
        
        st.markdown("---")
        st.subheader("✏️ Modifica Wallet")
        
        with st.form("edit_wallet_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_wallet = st.text_input(
                    "💰 Nome Wallet",
                    value=wallet_data['nome_wallet'],
                    help="Nome univoco del wallet"
                )
                
                proprietario = st.text_input(
                    "👤 Proprietario",
                    value=wallet_data['proprietario'],
                    help="Nome del proprietario del wallet"
                )
                
                tipo_wallet = st.selectbox(
                    "📋 Tipo Wallet",
                    options=["principale", "collaboratore", "cliente"],
                    index=["principale", "collaboratore", "cliente"].index(wallet_data['tipo_wallet']),
                    format_func=lambda x: {
                        "principale": "🏠 Principale",
                        "collaboratore": "👥 Collaboratore", 
                        "cliente": "👤 Cliente"
                    }[x],
                    help="Tipo di wallet"
                )
            
            with col2:
                valuta = st.selectbox(
                    "💱 Valuta",
                    options=["USD", "EUR", "GBP", "BTC", "ETH"],
                    index=["USD", "EUR", "GBP", "BTC", "ETH"].index(wallet_data.get('valuta', 'USD')),
                    help="Valuta del wallet"
                )
                
                attivo = st.checkbox(
                    "✅ Wallet Attivo",
                    value=wallet_data.get('attivo', True),
                    help="Se il wallet è attivo"
                )
            
            # Note
            note = st.text_area(
                "📝 Note",
                value=wallet_data.get('note', ''),
                placeholder="Note aggiuntive sul wallet...",
                help="Note opzionali"
            )
            
            # Pulsanti
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                submit_button = st.form_submit_button(
                    "💾 Salva Modifiche",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            with col_btn3:
                if st.form_submit_button("🗑️ Elimina Wallet", use_container_width=True):
                    success, message = self._delete_wallet(wallet_data['id'])
                    if success:
                        st.success(message)
                        st.balloons()
                        del st.session_state.editing_wallet
                        st.rerun()
                    else:
                        st.error(message)
            
            # Gestione submit
            if submit_button:
                if not nome_wallet.strip():
                    st.error("❌ Il nome del wallet è obbligatorio")
                else:
                    updated_data = {
                        'nome_wallet': nome_wallet.strip(),
                        'proprietario': proprietario.strip(),
                        'tipo_wallet': tipo_wallet,
                        'valuta': valuta,
                        'attivo': attivo,
                        'note': note.strip() if note else None
                    }
                    
                    success, message = self._update_wallet(wallet_data['id'], updated_data)
                    if success:
                        st.success(message)
                        del st.session_state.editing_wallet
                        st.rerun()
                    else:
                        st.error(message)
            
            if cancel_button:
                del st.session_state.editing_wallet
                st.rerun()
    
    def _render_edit_saldo_form(self):
        """Rende il form per modificare i saldi dei wallet"""
        
        st.subheader("💰 Modifica Saldi Wallet")
        st.info("💡 **Nota**: I saldi vengono calcolati automaticamente dalle transazioni. Usa questo form solo per correzioni manuali.")
        
        # Ottieni wallet
        wallets = self.wallet_manager.get_wallet_collaboratori()
        
        if not wallets:
            st.info("📋 Nessun wallet presente.")
            return
        
        # Seleziona wallet
        wallet_names = [w['nome_wallet'] for w in wallets if w.get('attivo', True)]
        selected_wallet = st.selectbox(
            "💰 Seleziona Wallet",
            options=wallet_names,
            help="Scegli il wallet da modificare"
        )
        
        if selected_wallet:
            # Mostra saldo attuale
            saldo_attuale = self.wallet_manager.get_wallet_balance(selected_wallet)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("💰 Saldo Attuale", f"{saldo_attuale:.2f}")
            
            with col2:
                st.metric("📊 Wallet", selected_wallet)
            
            # Form modifica saldo
            with st.form("edit_saldo_form"):
                st.subheader("🔧 Modifica Saldo")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nuovo_saldo = st.number_input(
                        "💰 Nuovo Saldo",
                        min_value=-1000000.0,
                        max_value=1000000.0,
                        step=0.01,
                        format="%.2f",
                        value=float(saldo_attuale),
                        help="Imposta il nuovo saldo del wallet"
                    )
                
                with col2:
                    motivo_modifica = st.selectbox(
                        "📋 Motivo Modifica",
                        options=["correzione", "bonifico_esterno", "commissione", "altro"],
                        format_func=lambda x: {
                            "correzione": "🔧 Correzione",
                            "bonifico_esterno": "💸 Bonifico Esterno",
                            "commissione": "💼 Commissione",
                            "altro": "📝 Altro"
                        }[x],
                        help="Motivo della modifica del saldo"
                    )
                
                # Note
                note_modifica = st.text_area(
                    "📝 Note Modifica",
                    placeholder="Spiega il motivo della modifica del saldo...",
                    help="Note obbligatorie per la modifica"
                )
                
                # Pulsanti
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    submit_button = st.form_submit_button(
                        "💾 Aggiorna Saldo",
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
                    if not note_modifica.strip():
                        st.error("❌ Le note sono obbligatorie per modificare il saldo")
                    else:
                        # Crea una transazione di correzione
                        # Determina il tipo di transazione basato sulla variazione del saldo
                        if nuovo_saldo > saldo_attuale:
                            tipo_transazione = 'deposit'
                            wallet_mittente = 'Sistema'
                            wallet_destinatario = selected_wallet
                        else:
                            tipo_transazione = 'withdrawal'
                            wallet_mittente = selected_wallet
                            wallet_destinatario = 'Sistema'
                        
                        correzione_data = {
                            'wallet_mittente': wallet_mittente,
                            'wallet_destinatario': wallet_destinatario,
                            'importo': abs(nuovo_saldo - saldo_attuale),
                            'valuta': 'USD',
                            'tipo_transazione': tipo_transazione,
                            'stato': 'completed',
                            'note': f"Correzione saldo: {note_modifica} (Motivo: {motivo_modifica})"
                        }
                        
                        success, message = self.wallet_manager.add_wallet_transaction(correzione_data)
                        if success:
                            st.success(f"✅ Saldo aggiornato! {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ Errore aggiornamento saldo: {message}")
                
                if cancel_button:
                    st.rerun()
    
    def _add_wallet(self, wallet_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiunge un nuovo wallet"""
        try:
            if not self.wallet_manager.supabase_manager:
                return False, "❌ Supabase non configurato"
            
            response = self.wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').insert(wallet_data).execute()
            
            if response.data:
                return True, f"✅ Wallet '{wallet_data['nome_wallet']}' creato con successo"
            else:
                return False, "❌ Errore creazione wallet"
                
        except Exception as e:
            logger.error(f"❌ Errore aggiunta wallet: {e}")
            return False, f"❌ Errore: {e}"
    
    def _update_wallet(self, wallet_id: str, wallet_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiorna un wallet esistente"""
        try:
            if not self.wallet_manager.supabase_manager:
                return False, "❌ Supabase non configurato"
            
            response = self.wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').update(wallet_data).eq('id', wallet_id).execute()
            
            if response.data:
                return True, f"✅ Wallet aggiornato con successo"
            else:
                return False, "❌ Errore aggiornamento wallet"
                
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento wallet: {e}")
            return False, f"❌ Errore: {e}"
    
    def _delete_wallet(self, wallet_id: str) -> Tuple[bool, str]:
        """Elimina un wallet"""
        try:
            if not self.wallet_manager.supabase_manager:
                return False, "❌ Supabase non configurato"
            
            # Verifica se ci sono transazioni associate
            transactions = self.wallet_manager.get_wallet_transactions(limit=1000)
            wallet_name = None
            
            # Trova il nome del wallet
            wallets = self.wallet_manager.get_wallet_collaboratori()
            for wallet in wallets:
                if wallet['id'] == wallet_id:
                    wallet_name = wallet['nome_wallet']
                    break
            
            if wallet_name:
                # Controlla transazioni
                wallet_transactions = [t for t in transactions if t.get('wallet_mittente') == wallet_name or t.get('wallet_destinatario') == wallet_name]
                
                if wallet_transactions:
                    return False, f"❌ Impossibile eliminare '{wallet_name}': ci sono {len(wallet_transactions)} transazioni associate. Elimina prima le transazioni."
            
            # Elimina wallet
            response = self.wallet_manager.supabase_manager.supabase.table('wallet_collaboratori').delete().eq('id', wallet_id).execute()
            
            if response.data:
                return True, f"✅ Wallet eliminato con successo"
            else:
                return False, "❌ Errore eliminazione wallet"
                
        except Exception as e:
            logger.error(f"❌ Errore eliminazione wallet: {e}")
            return False, f"❌ Errore: {e}"
