"""
💰 WALLET TRANSACTION FORM
Form per inserire e modificare transazioni tra wallet
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.translations import t

class WalletTransactionForm:
    """Form per la gestione delle transazioni wallet"""
    
    def __init__(self, wallet_manager):
        """Inizializza il form con il gestore wallet"""
        self.wallet_manager = wallet_manager
    
    def render_form(self, transaction_data: Optional[Dict[str, Any]] = None, is_edit: bool = False):
        """Rende il form per inserimento/modifica transazione"""
        
        # Titolo del form
        title = "➕ Nuova Transazione Wallet" if not is_edit else "✏️ Modifica Transazione"
        st.subheader(title)
        
        # Ottieni lista wallet disponibili
        wallet_list = self.wallet_manager.get_wallet_list()
        
        if not wallet_list:
            st.error("❌ Nessun wallet disponibile. Crea prima i wallet dei collaboratori.")
            return False, None, None
        
        # Form per la transazione
        with st.form("wallet_transaction_form", clear_on_submit=not is_edit):
            col1, col2 = st.columns(2)
            
            with col1:
                # Wallet mittente
                wallet_mittente = st.selectbox(
                    "💰 Wallet Mittente",
                    options=wallet_list,
                    index=0,
                    help="Seleziona il wallet da cui trasferire i fondi"
                )
                
                # Importo
                importo = st.number_input(
                    "💵 Importo",
                    min_value=0.01,
                    max_value=1000000.0,
                    step=0.01,
                    format="%.2f",
                    help="Importo da trasferire"
                )
                
                # Valuta
                valuta = st.selectbox(
                    "💱 Valuta",
                    options=["USD", "EUR", "GBP", "BTC", "ETH"],
                    index=0,
                    help="Valuta della transazione"
                )
            
            with col2:
                # Wallet destinatario
                wallet_destinatario = st.selectbox(
                    "🎯 Wallet Destinatario",
                    options=[w for w in wallet_list if w != wallet_mittente],
                    help="Seleziona il wallet destinatario"
                )
                
                # Tipo transazione
                tipo_transazione = st.selectbox(
                    "📋 Tipo Transazione",
                    options=["transfer", "deposit", "withdrawal"],
                    format_func=lambda x: {
                        "transfer": "🔄 Trasferimento",
                        "deposit": "📥 Deposito",
                        "withdrawal": "📤 Prelievo"
                    }[x],
                    help="Tipo di transazione"
                )
                
                # Commissione
                commissione = st.number_input(
                    "💸 Commissione",
                    min_value=0.0,
                    max_value=1000.0,
                    step=0.01,
                    format="%.2f",
                    help="Commissione applicata alla transazione"
                )
            
            # Note
            note = st.text_area(
                "📝 Note",
                placeholder="Inserisci note aggiuntive sulla transazione...",
                help="Note opzionali per la transazione"
            )
            
            # Stato (solo per modifica)
            if is_edit:
                stato = st.selectbox(
                    "📊 Stato Transazione",
                    options=["pending", "completed", "failed", "cancelled"],
                    format_func=lambda x: {
                        "pending": "⏳ In Attesa",
                        "completed": "✅ Completata",
                        "failed": "❌ Fallita",
                        "cancelled": "🚫 Cancellata"
                    }[x],
                    help="Stato corrente della transazione"
                )
            else:
                stato = "pending"
            
            # Pulsanti
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                submit_button = st.form_submit_button(
                    "💾 Salva Transazione" if not is_edit else "💾 Aggiorna Transazione",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                if is_edit:
                    cancel_button = st.form_submit_button(
                        "❌ Annulla",
                        use_container_width=True
                    )
                else:
                    clear_button = st.form_submit_button(
                        "🗑️ Pulisci",
                        use_container_width=True
                    )
            
            with col_btn3:
                # Anteprima transazione
                preview_button = st.form_submit_button(
                    "👁️ Anteprima",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                # Prepara dati transazione
                transaction_data = {
                    'wallet_mittente': wallet_mittente,
                    'wallet_destinatario': wallet_destinatario,
                    'importo': float(importo),
                    'valuta': valuta,
                    'tipo_transazione': tipo_transazione,
                    'commissione': float(commissione),
                    'note': note,
                    'stato': stato,
                    'data_transazione': datetime.now().isoformat()
                }
                
                # Valida transazione
                is_valid, validation_message = self.wallet_manager.validate_transaction(transaction_data)
                
                if not is_valid:
                    st.error(validation_message)
                    return False, None, None
                
                # Gestione submit del form
                if submit_button:
                    # Mostra anteprima prima di salvare
                    st.info("📋 **Anteprima Transazione:**")
                    col_preview1, col_preview2 = st.columns(2)
                    
                    with col_preview1:
                        st.write(f"**💰 Da:** {wallet_mittente}")
                        st.write(f"**🎯 A:** {wallet_destinatario}")
                        st.write(f"**💵 Importo:** {importo} {valuta}")
                    
                    with col_preview2:
                        st.write(f"**📋 Tipo:** {tipo_transazione}")
                        st.write(f"**💸 Commissione:** {commissione} {valuta}")
                        st.write(f"**📊 Stato:** {stato}")
                    
                    if note:
                        st.write(f"**📝 Note:** {note}")
                    
                    # Salva la transazione
                    if is_edit:
                        # Aggiorna transazione esistente
                        success, message = self.wallet_manager.update_wallet_transaction(
                            transaction_data.get('id'), transaction_data
                        )
                    else:
                        # Aggiungi nuova transazione
                        success, message = self.wallet_manager.add_wallet_transaction(transaction_data)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                
                return False, None, None
            
            # Gestione anteprima
            if preview_button:
                transaction_data = {
                    'wallet_mittente': wallet_mittente,
                    'wallet_destinatario': wallet_destinatario,
                    'importo': float(importo),
                    'valuta': valuta,
                    'tipo_transazione': tipo_transazione,
                    'commissione': float(commissione),
                    'note': note,
                    'stato': stato
                }
                
                # Valida transazione
                is_valid, validation_message = self.wallet_manager.validate_transaction(transaction_data)
                
                if is_valid:
                    st.success("✅ Transazione valida!")
                    self._show_transaction_preview(transaction_data)
                else:
                    st.error(validation_message)
                
                return False, None, None
            
            # Gestione annulla/pulisci
            if (is_edit and cancel_button) or (not is_edit and clear_button):
                st.rerun()
        
        return False, None, None
    
    def _show_transaction_preview(self, transaction_data: Dict[str, Any]):
        """Mostra l'anteprima della transazione"""
        st.markdown("---")
        st.subheader("👁️ Anteprima Transazione")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("💰 Wallet Mittente", transaction_data['wallet_mittente'])
            st.metric("🎯 Wallet Destinatario", transaction_data['wallet_destinatario'])
            st.metric("💵 Importo", f"{transaction_data['importo']} {transaction_data['valuta']}")
        
        with col2:
            st.metric("📋 Tipo", transaction_data['tipo_transazione'])
            st.metric("💸 Commissione", f"{transaction_data['commissione']} {transaction_data['valuta']}")
            st.metric("📊 Stato", transaction_data['stato'])
        
        if transaction_data.get('note'):
            st.write("**📝 Note:**")
            st.write(transaction_data['note'])
        
        # Calcola saldi attuali
        saldo_mittente = self.wallet_manager.get_wallet_balance(transaction_data['wallet_mittente'])
        saldo_destinatario = self.wallet_manager.get_wallet_balance(transaction_data['wallet_destinatario'])
        
        st.markdown("---")
        st.subheader("💰 Saldi Attuali")
        
        col_saldo1, col_saldo2 = st.columns(2)
        
        with col_saldo1:
            st.metric(
                f"Saldo {transaction_data['wallet_mittente']}", 
                f"{saldo_mittente:.2f} {transaction_data['valuta']}"
            )
        
        with col_saldo2:
            st.metric(
                f"Saldo {transaction_data['wallet_destinatario']}", 
                f"{saldo_destinatario:.2f} {transaction_data['valuta']}"
            )
