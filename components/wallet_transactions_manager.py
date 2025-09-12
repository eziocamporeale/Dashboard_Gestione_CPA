"""
💰 WALLET TRANSACTIONS MANAGER
Gestione completa delle transazioni tra wallet nel sistema CPA
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletTransactionsManager:
    """Gestore delle transazioni tra wallet"""
    
    def __init__(self):
        """Inizializza il gestore delle transazioni wallet"""
        self.supabase_manager = None
        self._init_supabase()
    
    def _init_supabase(self):
        """Inizializza la connessione Supabase"""
        try:
            from supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
            
            if not self.supabase_manager.is_configured:
                logger.warning("⚠️ Supabase non configurato per WalletTransactionsManager")
                self.supabase_manager = None
            else:
                logger.info("✅ Supabase inizializzato per WalletTransactionsManager")
                
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase: {e}")
            self.supabase_manager = None
    
    def get_wallet_collaboratori(self) -> List[Dict[str, Any]]:
        """Recupera tutti i wallet dei collaboratori"""
        if not self.supabase_manager:
            return []
        
        try:
            response = self.supabase_manager.supabase.table('wallet_collaboratori').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero wallet collaboratori: {e}")
            return []
    
    def get_wallet_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera le transazioni wallet"""
        if not self.supabase_manager:
            return []
        
        try:
            response = self.supabase_manager.supabase.table('wallet_transactions').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero transazioni wallet: {e}")
            return []
    
    def add_wallet_transaction(self, transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiunge una nuova transazione wallet e aggiorna i saldi"""
        if not self.supabase_manager:
            return False, "❌ Supabase non configurato"
        
        try:
            # Genera hash univoco per la transazione
            import hashlib
            transaction_string = f"{transaction_data['wallet_mittente']}_{transaction_data['wallet_destinatario']}_{transaction_data['importo']}_{datetime.now().isoformat()}"
            transaction_data['hash_transazione'] = hashlib.md5(transaction_string.encode()).hexdigest()
            
            # Aggiungi timestamp
            transaction_data['created_at'] = datetime.now().isoformat()
            transaction_data['updated_at'] = datetime.now().isoformat()
            
            # Inserisci la transazione
            response = self.supabase_manager.supabase.table('wallet_transactions').insert(transaction_data).execute()
            
            if response.data:
                # Non aggiorniamo più i saldi nel database
                # I saldi vengono calcolati dinamicamente dalle transazioni completed
                return True, f"✅ Transazione aggiunta con successo"
            else:
                return False, "❌ Errore inserimento transazione"
                
        except Exception as e:
            logger.error(f"❌ Errore aggiunta transazione: {e}")
            return False, f"❌ Errore: {e}"
    
    def update_wallet_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiorna una transazione wallet esistente"""
        if not self.supabase_manager:
            return False, "❌ Supabase non configurato"
        
        try:
            # Recupera la transazione esistente per confrontare lo stato
            existing_transaction = self.supabase_manager.supabase.table('wallet_transactions').select('*').eq('id', transaction_id).execute()
            
            transaction_data['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase_manager.supabase.table('wallet_transactions').update(transaction_data).eq('id', transaction_id).execute()
            
            if response.data:
                # Non aggiorniamo più i saldi nel database
                # I saldi vengono calcolati dinamicamente dalle transazioni completed
                return True, f"✅ Transazione aggiornata con successo"
            else:
                return False, "❌ Errore aggiornamento transazione"
                
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento transazione: {e}")
            return False, f"❌ Errore: {e}"
    
    # Le funzioni _update_wallet_balances e _update_single_wallet_balance sono state rimosse
    # perché ora i saldi vengono calcolati dinamicamente dalle transazioni completed
    
    def delete_wallet_transaction(self, transaction_id: str) -> Tuple[bool, str]:
        """Elimina una transazione wallet"""
        if not self.supabase_manager:
            return False, "❌ Supabase non configurato"
        
        try:
            response = self.supabase_manager.supabase.table('wallet_transactions').delete().eq('id', transaction_id).execute()
            
            if response.data:
                return True, f"✅ Transazione eliminata con successo"
            else:
                return False, "❌ Errore eliminazione transazione"
                
        except Exception as e:
            logger.error(f"❌ Errore eliminazione transazione: {e}")
            return False, f"❌ Errore: {e}"
    
    def get_wallet_balance(self, wallet_name: str) -> float:
        """Calcola il saldo di un wallet basato sulle transazioni"""
        if not self.supabase_manager:
            return 0.0
        
        try:
            # Transazioni in uscita (mittente)
            outgoing_response = self.supabase_manager.supabase.table('wallet_transactions').select('importo').eq('wallet_mittente', wallet_name).eq('stato', 'completed').execute()
            outgoing_amount = sum(float(t['importo']) for t in outgoing_response.data) if outgoing_response.data else 0
            
            # Transazioni in entrata (destinatario)
            incoming_response = self.supabase_manager.supabase.table('wallet_transactions').select('importo').eq('wallet_destinatario', wallet_name).eq('stato', 'completed').execute()
            incoming_amount = sum(float(t['importo']) for t in incoming_response.data) if incoming_response.data else 0
            
            return incoming_amount - outgoing_amount
            
        except Exception as e:
            logger.error(f"❌ Errore calcolo saldo wallet {wallet_name}: {e}")
            return 0.0
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        """Ottiene statistiche delle transazioni"""
        if not self.supabase_manager:
            return {}
        
        try:
            transactions = self.get_wallet_transactions(limit=1000)
            
            if not transactions:
                return {
                    'totale_transazioni': 0,
                    'importo_totale': 0,
                    'transazioni_pending': 0,
                    'transazioni_completed': 0,
                    'transazioni_failed': 0
                }
            
            total_amount = sum(float(t.get('importo', 0)) for t in transactions)
            pending_count = len([t for t in transactions if t.get('stato') == 'pending'])
            completed_count = len([t for t in transactions if t.get('stato') == 'completed'])
            failed_count = len([t for t in transactions if t.get('stato') == 'failed'])
            
            return {
                'totale_transazioni': len(transactions),
                'importo_totale': total_amount,
                'transazioni_pending': pending_count,
                'transazioni_completed': completed_count,
                'transazioni_failed': failed_count
            }
            
        except Exception as e:
            logger.error(f"❌ Errore calcolo statistiche: {e}")
            return {}
    
    def get_wallet_list(self) -> List[str]:
        """Ottiene la lista dei wallet disponibili"""
        wallets = self.get_wallet_collaboratori()
        return [w['nome_wallet'] for w in wallets if w.get('attivo', True)]
    
    def validate_transaction(self, transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida i dati di una transazione"""
        try:
            # Verifica campi obbligatori
            required_fields = ['wallet_mittente', 'wallet_destinatario', 'importo']
            for field in required_fields:
                if not transaction_data.get(field):
                    return False, f"❌ Campo obbligatorio mancante: {field}"
            
            # Verifica che mittente e destinatario siano diversi
            if transaction_data['wallet_mittente'] == transaction_data['wallet_destinatario']:
                return False, "❌ Il wallet mittente e destinatario devono essere diversi"
            
            # Verifica importo positivo
            try:
                importo = float(transaction_data['importo'])
                if importo <= 0:
                    return False, "❌ L'importo deve essere positivo"
            except ValueError:
                return False, "❌ Importo non valido"
            
            # Verifica che i wallet esistano
            wallet_list = self.get_wallet_list()
            if transaction_data['wallet_mittente'] not in wallet_list:
                return False, f"❌ Wallet mittente '{transaction_data['wallet_mittente']}' non trovato"
            
            if transaction_data['wallet_destinatario'] not in wallet_list:
                return False, f"❌ Wallet destinatario '{transaction_data['wallet_destinatario']}' non trovato"
            
            return True, "✅ Transazione valida"
            
        except Exception as e:
            logger.error(f"❌ Errore validazione transazione: {e}")
            return False, f"❌ Errore validazione: {e}"
    
    def get_team_wallets(self) -> List[Dict[str, Any]]:
        """Recupera tutti i wallet del team (tipo 'collaboratore' o 'principale')"""
        if not self.supabase_manager:
            return []
        
        try:
            response = self.supabase_manager.supabase.table('wallet_collaboratori').select('*').in_('tipo_wallet', ['collaboratore', 'principale']).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero wallet team: {e}")
            return []
    
    def get_client_wallets(self) -> List[Dict[str, Any]]:
        """Recupera tutti i wallet dei clienti"""
        if not self.supabase_manager:
            return []
        
        try:
            response = self.supabase_manager.supabase.table('wallet_collaboratori').select('*').eq('tipo_wallet', 'cliente').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero wallet clienti: {e}")
            return []
    
    def create_deposit_transaction(self, team_wallet: str, client_wallet: str, amount: float, motivo: str, hash_blockchain: str = None, commissione_network: float = 0.0) -> Tuple[bool, str]:
        """
        Crea una transazione di deposito da wallet team a wallet cliente
        
        Args:
            team_wallet: Nome del wallet team
            client_wallet: Nome del wallet cliente
            amount: Importo in USDT
            motivo: Motivo del deposito (deposit_iniziale, rideposito)
            hash_blockchain: Hash della transazione blockchain
            commissione_network: Commissione di rete
            
        Returns:
            (success, transaction_id o messaggio errore)
        """
        if not self.supabase_manager:
            return False, "❌ Supabase non configurato"
        
        try:
            # Prepara dati transazione
            transaction_data = {
                'wallet_mittente': team_wallet,
                'wallet_destinatario': client_wallet,
                'importo': amount,
                'valuta': 'USDT',
                'tipo_transazione': motivo,
                'stato': 'completed',  # Depositi automatici
                'note': f"Deposito {motivo} da team a cliente",
                'hash_transazione': hash_blockchain or f"deposit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'commissione': commissione_network,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Inserisci transazione
            response = self.supabase_manager.supabase.table('wallet_transactions').insert(transaction_data).execute()
            
            if response.data:
                return True, f"✅ Deposito {motivo} creato con successo"
            else:
                return False, "❌ Errore creazione deposito"
                
        except Exception as e:
            logger.error(f"❌ Errore creazione deposito: {e}")
            return False, f"❌ Errore creazione deposito: {e}"
    
    def create_withdrawal_transaction(self, client_wallet: str, team_wallet: str, amount: float, motivo: str, hash_blockchain: str = None, commissione_network: float = 0.0) -> Tuple[bool, str]:
        """
        Crea una transazione di prelievo da wallet cliente a wallet team
        
        Args:
            client_wallet: Nome del wallet cliente
            team_wallet: Nome del wallet team
            amount: Importo in USDT
            motivo: Motivo del prelievo (prelievo)
            hash_blockchain: Hash della transazione blockchain
            commissione_network: Commissione di rete
            
        Returns:
            (success, transaction_id o messaggio errore)
        """
        if not self.supabase_manager:
            return False, "❌ Supabase non configurato"
        
        try:
            # Prepara dati transazione
            transaction_data = {
                'wallet_mittente': client_wallet,
                'wallet_destinatario': team_wallet,
                'importo': amount,
                'valuta': 'USDT',
                'tipo_transazione': motivo,
                'stato': 'completed',  # Prelievi automatici
                'note': f"Prelievo {motivo} da cliente a team",
                'hash_transazione': hash_blockchain or f"withdrawal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'commissione': commissione_network,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Inserisci transazione
            response = self.supabase_manager.supabase.table('wallet_transactions').insert(transaction_data).execute()
            
            if response.data:
                return True, f"✅ Prelievo {motivo} creato con successo"
            else:
                return False, "❌ Errore creazione prelievo"
                
        except Exception as e:
            logger.error(f"❌ Errore creazione prelievo: {e}")
            return False, f"❌ Errore creazione prelievo: {e}"
    
    def calculate_wallet_balance(self, wallet_name: str) -> float:
        """
        Calcola il saldo attuale di un wallet basato sulle transazioni
        
        Args:
            wallet_name: Nome del wallet
            
        Returns:
            Saldo attuale del wallet
        """
        if not self.supabase_manager:
            return 0.0
        
        try:
            # Transazioni in uscita (mittente)
            outgoing_response = self.supabase_manager.supabase.table('wallet_transactions').select('importo').eq('wallet_mittente', wallet_name).eq('stato', 'completed').execute()
            outgoing_amount = sum(float(t['importo']) for t in outgoing_response.data) if outgoing_response.data else 0
            
            # Transazioni in entrata (destinatario)
            incoming_response = self.supabase_manager.supabase.table('wallet_transactions').select('importo').eq('wallet_destinatario', wallet_name).eq('stato', 'completed').execute()
            incoming_amount = sum(float(t['importo']) for t in incoming_response.data) if incoming_response.data else 0
            
            # Saldo = entrate - uscite
            balance = incoming_amount - outgoing_amount
            return balance
            
        except Exception as e:
            logger.error(f"❌ Errore calcolo saldo wallet {wallet_name}: {e}")
            return 0.0