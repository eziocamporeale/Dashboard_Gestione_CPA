#!/usr/bin/env python3
"""
Gestione degli incroci tra account CPA
Permette di tracciare gli account in hedging per sbloccare bonus senza rischio
USO SUPABASE invece di SQLite locale
"""

import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any
import logging

try:
    from supabase_manager import SupabaseManager
except ImportError:
    SupabaseManager = None

class IncrociManager:
    """Gestisce gli incroci tra account CPA usando Supabase"""
    
    def __init__(self):
        """Inizializza il manager degli incroci con Supabase"""
        if SupabaseManager:
            self.supabase = SupabaseManager()
            self.telegram_manager = None
            # Non inizializzare TelegramManager qui per evitare loop infinito
            # self._init_telegram()
            logging.info("IncrociManager inizializzato con Supabase")
        else:
            self.supabase = None
            self.telegram_manager = None
            logging.warning("IncrociManager inizializzato senza Supabase")
    
    def _init_telegram(self):
        """Inizializza il gestore Telegram"""
        try:
            from components.telegram_manager import TelegramManager
            self.telegram_manager = TelegramManager()
            logging.info("✅ TelegramManager inizializzato per IncrociManager")
        except Exception as e:
            logging.error(f"❌ Errore inizializzazione TelegramManager: {e}")
            self.telegram_manager = None
    
    def ottieni_incroci(self, stato: Optional[str] = None) -> pd.DataFrame:
        """
        Ottiene tutti gli incroci o filtrati per stato da Supabase
        
        Args:
            stato: Filtro per stato ('attivo', 'chiuso', 'sospeso')
            
        Returns:
            DataFrame con gli incroci
        """
        try:
            if not self.supabase:
                logging.warning("Supabase non disponibile per ottieni_incroci")
                return pd.DataFrame()
            
            # Query base per incroci
            query = self.supabase.supabase.table('incroci').select('*')
            
            if stato:
                query = query.eq('stato', stato)
            
            response = query.order('data_apertura', desc=True).execute()
            
            if not response.data:
                return pd.DataFrame()
            
            # Converti in DataFrame
            df_incroci = pd.DataFrame(response.data)
            
            # Per ogni incrocio, ottieni account e bonus correlati
            incroci_completi = []
            
            for _, incrocio in df_incroci.iterrows():
                incrocio_id = incrocio['id']
                
                # Ottieni account long
                response_account = self.supabase.supabase.table('incroci_account')\
                    .select('*')\
                    .eq('incrocio_id', incrocio_id)\
                    .eq('tipo_posizione', 'long')\
                    .execute()
                
                account_long = response_account.data[0] if response_account.data else {}
                
                # Ottieni account short
                response_account = self.supabase.supabase.table('incroci_account')\
                    .select('*')\
                    .eq('incrocio_id', incrocio_id)\
                    .eq('tipo_posizione', 'short')\
                    .execute()
                
                account_short = response_account.data[0] if response_account.data else {}
                
                # Ottieni bonus
                response_bonus = self.supabase.supabase.table('incroci_bonus')\
                    .select('*')\
                    .eq('incrocio_id', incrocio_id)\
                    .execute()
                
                bonus_totali = sum(bonus.get('importo_bonus', 0) for bonus in response_bonus.data) if response_bonus.data else 0
                
                # Recupera informazioni clienti per ID
                cliente_long_id = None
                cliente_short_id = None
                
                try:
                    # Cerca cliente long per numero conto
                    if account_long.get('numero_conto'):
                        cliente_long_response = self.supabase.supabase.table('clienti').select('id, nome_cliente').eq('numero_conto', account_long['numero_conto']).execute()
                        if cliente_long_response.data:
                            cliente_long_id = cliente_long_response.data[0]['id']
                            cliente_long_nome = cliente_long_response.data[0]['nome_cliente']
                        else:
                            cliente_long_nome = account_long.get('numero_conto', 'N/A')
                    else:
                        cliente_long_nome = 'N/A'
                    
                    # Cerca cliente short per numero conto
                    if account_short.get('numero_conto'):
                        cliente_short_response = self.supabase.supabase.table('clienti').select('id, nome_cliente').eq('numero_conto', account_short['numero_conto']).execute()
                        if cliente_short_response.data:
                            cliente_short_id = cliente_short_response.data[0]['id']
                            cliente_short_nome = cliente_short_response.data[0]['nome_cliente']
                        else:
                            cliente_short_nome = account_short.get('numero_conto', 'N/A')
                    else:
                        cliente_short_nome = 'N/A'
                        
                except Exception as e:
                    logging.warning(f"Errore recupero info clienti: {e}")
                    cliente_long_nome = account_long.get('numero_conto', 'N/A')
                    cliente_short_nome = account_short.get('numero_conto', 'N/A')
                
                # Crea record completo
                incrocio_completo = {
                    'id': incrocio['id'],
                    'nome_incrocio': incrocio['nome_incrocio'],
                    'data_apertura': incrocio['data_apertura'],
                    'data_chiusura': incrocio.get('data_chiusura'),
                    'stato': incrocio['stato'],
                    'pair_trading': incrocio['pair_trading'],
                    'volume_trading': incrocio.get('volume_trading', 0),
                    'note': incrocio.get('note', ''),
                    'cliente_long': cliente_long_nome,
                    'cliente_short': cliente_short_nome,
                    'cliente_long_id': cliente_long_id,
                    'cliente_short_id': cliente_short_id,
                    'broker_long': account_long.get('broker', 'N/A'),
                    'piattaforma_long': account_long.get('piattaforma', 'N/A'),
                    'conto_long': account_long.get('numero_conto', 'N/A'),
                    'volume_long': account_long.get('volume_posizione', 0),
                    'broker_short': account_short.get('broker', 'N/A'),
                    'piattaforma_short': account_short.get('piattaforma', 'N/A'),
                    'conto_short': account_short.get('numero_conto', 'N/A'),
                    'volume_short': account_short.get('volume_posizione', 0),
                    'totale_bonus': bonus_totali
                }
                
                incroci_completi.append(incrocio_completo)
            
            return pd.DataFrame(incroci_completi)
                
        except Exception as e:
            logging.error(f"Errore recupero incroci da Supabase: {e}")
            return pd.DataFrame()
    
    def ottieni_statistiche_incroci(self) -> Dict:
        """
        Ottiene statistiche complete sugli incroci da Supabase
        
        Returns:
            Dizionario con le statistiche
        """
        try:
            # Ottieni tutti gli incroci
            response_incroci = self.supabase.supabase.table('incroci').select('*').execute()
            incroci = response_incroci.data if response_incroci.data else []
            
            # Ottieni tutti gli account
            response_account = self.supabase.supabase.table('incroci_account').select('*').execute()
            accounts = response_account.data if response_account.data else []
            
            # Ottieni tutti i bonus
            response_bonus = self.supabase.supabase.table('incroci_bonus').select('*').execute()
            bonus = response_bonus.data if response_bonus.data else []
            
            # Statistiche generali
            totale_incroci = len(incroci)
            incroci_attivi = len([i for i in incroci if i.get('stato') == 'attivo'])
            incroci_chiusi = len([i for i in incroci if i.get('stato') == 'chiuso'])
            volume_totale = sum(i.get('volume_trading', 0) for i in incroci)
            
            # Statistiche per pair
            pair_stats = {}
            for incrocio in incroci:
                pair = incrocio.get('pair_trading', 'Unknown')
                if pair not in pair_stats:
                    pair_stats[pair] = {'utilizzi': 0, 'volume_totale': 0}
                pair_stats[pair]['utilizzi'] += 1
                pair_stats[pair]['volume_totale'] += incrocio.get('volume_trading', 0)
            
            stats_pair = [(pair, data['utilizzi'], data['volume_totale']) 
                         for pair, data in pair_stats.items()]
            stats_pair.sort(key=lambda x: x[1], reverse=True)
            
            # Statistiche per broker
            broker_stats = {}
            for account in accounts:
                broker = account.get('broker', 'Unknown')
                if broker not in broker_stats:
                    broker_stats[broker] = {'utilizzi': 0, 'incroci_unici': set()}
                broker_stats[broker]['utilizzi'] += 1
                broker_stats[broker]['incroci_unici'].add(account.get('incrocio_id'))
            
            stats_broker = [(broker, data['utilizzi'], len(data['incroci_unici'])) 
                           for broker, data in broker_stats.items()]
            stats_broker.sort(key=lambda x: x[1], reverse=True)
            
            # Statistiche bonus
            totale_bonus = sum(b.get('importo_bonus', 0) for b in bonus)
            numero_bonus = len(bonus)
            bonus_attivi = len([b for b in bonus if b.get('stato_bonus') == 'attivo'])
            
            return {
                'generali': {
                    'totale_incroci': totale_incroci,
                    'incroci_attivi': incroci_attivi,
                    'incroci_chiusi': incroci_chiusi,
                    'volume_totale': volume_totale
                },
                'per_pair': stats_pair,
                'per_broker': stats_broker,
                'bonus': {
                    'totale_bonus': totale_bonus,
                    'numero_bonus': numero_bonus,
                    'bonus_attivi': bonus_attivi
                }
            }
                
        except Exception as e:
            logging.error(f"Errore recupero statistiche incroci da Supabase: {e}")
            return {}
    
    def crea_incrocio(self, dati_incrocio: Dict) -> Tuple[bool, str]:
        """
        Crea un nuovo incrocio tra account in Supabase
        
        Args:
            dati_incrocio: Dizionario con i dati dell'incrocio
            
        Returns:
            (success, incrocio_id o messaggio errore)
        """
        try:
            if not self.supabase:
                logging.warning("Supabase non disponibile per crea_incrocio")
                return False, "Supabase non disponibile"
            
            # Crea incrocio principale
            incrocio_data = {
                'nome_incrocio': dati_incrocio['nome_incrocio'],
                'data_apertura': dati_incrocio['data_apertura'].isoformat() if isinstance(dati_incrocio['data_apertura'], (date, datetime)) else str(dati_incrocio['data_apertura']),
                'pair_trading': dati_incrocio['pair_trading'],
                'volume_trading': dati_incrocio.get('volume_trading', 0),
                'note': dati_incrocio.get('note', ''),
                'stato': 'attivo',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase.supabase.table('incroci').insert(incrocio_data).execute()
            
            if not response.data:
                return False, "Errore creazione incrocio principale"
            
            incrocio_id = response.data[0]['id']
            
            # Crea account long
            account_long_data = {
                'incrocio_id': incrocio_id,
                'tipo_posizione': 'long',
                'broker': dati_incrocio['broker_long'],
                'piattaforma': dati_incrocio['piattaforma_long'],
                'numero_conto': dati_incrocio['conto_long'],
                'volume_posizione': dati_incrocio.get('volume_long', 0),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.supabase.table('incroci_account').insert(account_long_data).execute()
            if not response.data:
                return False, "Errore creazione account long"
            
            # Crea account short
            account_short_data = {
                'incrocio_id': incrocio_id,
                'tipo_posizione': 'short',
                'broker': dati_incrocio['broker_short'],
                'piattaforma': dati_incrocio['piattaforma_short'],
                'numero_conto': dati_incrocio['conto_short'],
                'volume_posizione': dati_incrocio.get('volume_short', 0),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.supabase.table('incroci_account').insert(account_short_data).execute()
            if not response.data:
                return False, "Errore creazione account short"
            
            # Crea bonus se specificato
            if 'bonus' in dati_incrocio:
                for bonus in dati_incrocio['bonus']:
                    bonus_data = {
                        'incrocio_id': incrocio_id,
                        'importo_bonus': bonus.get('importo', bonus.get('importo_bonus', 0)),
                        'data_bonus': bonus.get('data_sblocco', dati_incrocio['data_apertura']).isoformat() if isinstance(bonus.get('data_sblocco', dati_incrocio['data_apertura']), (date, datetime)) else str(bonus.get('data_sblocco', dati_incrocio['data_apertura'])),
                        'note': bonus.get('note', ''),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    response = self.supabase.supabase.table('incroci_bonus').insert(bonus_data).execute()
                    if not response.data:
                        logging.warning(f"Errore creazione bonus: {bonus}")
            
            # INTEGRAZIONE WALLET: Crea transazione wallet per tracciare l'incrocio
            try:
                from components.wallet_transactions_manager import WalletTransactionsManager
                wallet_manager = WalletTransactionsManager()
                
                # Estrai ID clienti dai dati
                cliente_long_id = dati_incrocio.get('account_long_id')
                cliente_short_id = dati_incrocio.get('account_short_id')
                
                # Se sono tuple, estrai l'ID
                if isinstance(cliente_long_id, tuple):
                    cliente_long_id = cliente_long_id[1]
                if isinstance(cliente_short_id, tuple):
                    cliente_short_id = cliente_short_id[1]
                
                if cliente_long_id and cliente_short_id:
                    wallet_success, wallet_message = wallet_manager.create_cross_transaction(
                        incrocio_id=incrocio_id,
                        cliente_long_id=cliente_long_id,
                        cliente_short_id=cliente_short_id,
                        volume_long=dati_incrocio.get('volume_long', 0),
                        volume_short=dati_incrocio.get('volume_short', 0),
                        pair_trading=dati_incrocio.get('pair_trading', '')
                    )
                    
                    if wallet_success:
                        logging.info(f"✅ Transazione wallet creata per incrocio {incrocio_id}")
                    else:
                        logging.warning(f"⚠️ Errore creazione transazione wallet: {wallet_message}")
                else:
                    logging.warning("⚠️ ID clienti non trovati per creazione transazione wallet")
                    
            except Exception as wallet_error:
                logging.error(f"❌ Errore integrazione wallet: {wallet_error}")
                # Non bloccare la creazione dell'incrocio se c'è un errore wallet
            
            logging.info(f"Incrocio creato con ID: {incrocio_id}")
            
            # Invia notifica Telegram per nuovo incrocio
            # Recupera i nomi dei clienti dal database
            cliente_long_name = 'N/A'
            cliente_short_name = 'N/A'
            
            try:
                # Recupera nome cliente long
                if 'account_long_id' in dati_incrocio:
                    cliente_long_id = dati_incrocio['account_long_id']
                    if isinstance(cliente_long_id, tuple):
                        cliente_long_id = cliente_long_id[1]
                    
                    cliente_response = self.supabase.supabase.table('clienti').select('nome_cliente, broker').eq('id', cliente_long_id).execute()
                    if cliente_response.data and len(cliente_response.data) > 0:
                        cliente_data = cliente_response.data[0]
                        cliente_long_name = f"{cliente_data.get('nome_cliente', 'N/A')} - {cliente_data.get('broker', 'N/A')}"
                
                # Recupera nome cliente short
                if 'account_short_id' in dati_incrocio:
                    cliente_short_id = dati_incrocio['account_short_id']
                    if isinstance(cliente_short_id, tuple):
                        cliente_short_id = cliente_short_id[1]
                    
                    cliente_response = self.supabase.supabase.table('clienti').select('nome_cliente, broker').eq('id', cliente_short_id).execute()
                    if cliente_response.data and len(cliente_response.data) > 0:
                        cliente_data = cliente_response.data[0]
                        cliente_short_name = f"{cliente_data.get('nome_cliente', 'N/A')} - {cliente_data.get('broker', 'N/A')}"
                        
            except Exception as e:
                logging.warning(f"Errore recupero nomi clienti per notifica: {e}")
            
            self._send_incrocio_notification('new_incrocio', {
                'nome_incrocio': dati_incrocio['nome_incrocio'],
                'pair_trading': dati_incrocio['pair_trading'],
                'cliente_long': cliente_long_name,
                'cliente_short': cliente_short_name,
                'lot_size': dati_incrocio.get('volume_trading', 'N/A'),
                'created_at': datetime.now().isoformat()
            })
            
            return True, incrocio_id
                
        except Exception as e:
            logging.error(f"Errore creazione incrocio in Supabase: {e}")
            return False, str(e)
    
    def chiudi_incrocio(self, incrocio_id: str, data_chiusura: date, note: str = "") -> bool:
        """
        Chiude un incrocio attivo in Supabase
        
        Args:
            incrocio_id: ID dell'incrocio (UUID)
            data_chiusura: Data di chiusura
            note: Note aggiuntive
            
        Returns:
            True se chiuso con successo
        """
        try:
            # Aggiorna stato incrocio
            response = self.supabase.supabase.table('incroci')\
                .update({
                    'stato': 'chiuso', 
                    'data_chiusura': data_chiusura.isoformat(),
                    'note': note,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', incrocio_id)\
                .execute()
            
            if not response.data:
                return False
            
            logging.info(f"Incrocio {incrocio_id} chiuso correttamente")
            return True
                
        except Exception as e:
            logging.error(f"Errore chiusura incrocio in Supabase: {e}")
            return False

    def aggiungi_bonus(self, incrocio_id: str, tipo_bonus: str, importo_bonus: float, 
                       valuta_bonus: str = 'USD', data_sblocco: str = None, note: str = "") -> bool:
        """
        Aggiunge un bonus CPA a un incrocio in Supabase
        
        Args:
            incrocio_id: ID dell'incrocio (UUID)
            tipo_bonus: Tipo di bonus (es. Welcome Bonus, Deposit Bonus)
            importo_bonus: Importo del bonus
            valuta_bonus: Valuta del bonus (default USD)
            data_sblocco: Data di sblocco del bonus
            note: Note aggiuntive
            
        Returns:
            True se aggiunto con successo
        """
        try:
            if not data_sblocco:
                data_sblocco = datetime.now().strftime('%Y-%m-%d')
            
            bonus_data = {
                'incrocio_id': incrocio_id,
                'importo_bonus': importo_bonus,
                'data_bonus': data_sblocco,
                'note': note,
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.supabase.table('incroci_bonus').insert(bonus_data).execute()
            
            if response.data:
                logging.info(f"Bonus {tipo_bonus} aggiunto all'incrocio {incrocio_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"Errore aggiunta bonus in Supabase: {e}")
            return False

    def elimina_incrocio(self, incrocio_id: str) -> bool:
        """
        Elimina completamente un incrocio da Supabase
        
        Args:
            incrocio_id: ID dell'incrocio da eliminare (UUID)
            
        Returns:
            True se eliminato con successo
        """
        try:
            # Verifica che l'incrocio esista
            response = self.supabase.supabase.table('incroci').select('id').eq('id', incrocio_id).execute()
            if not response.data:
                logging.warning(f"Incrocio {incrocio_id} non trovato")
                return False
            
            # Elimina l'incrocio (le tabelle correlate si eliminano automaticamente per CASCADE)
            response = self.supabase.supabase.table('incroci').delete().eq('id', incrocio_id).execute()
            
            if response.data:
                logging.info(f"Incrocio {incrocio_id} eliminato con successo")
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"Errore eliminazione incrocio da Supabase: {e}")
            return False
    
    def _send_incrocio_notification(self, notification_type: str, data: Dict[str, Any]):
        """Invia notifica Telegram per eventi incroci"""
        try:
            # Inizializza TelegramManager solo se necessario
            if not self.telegram_manager:
                self._init_telegram()
            
            if not self.telegram_manager or not self.telegram_manager.is_configured:
                logging.info("📱 Telegram non configurato, notifica incrocio non inviata")
                return
            
            # Controlla se le notifiche incroci sono abilitate
            if not self._is_notification_enabled(notification_type):
                logging.info(f"🔔 Notifiche {notification_type} disabilitate")
                return
            
            # Invia la notifica
            success, message = self.telegram_manager.send_notification(notification_type, data)
            
            if success:
                logging.info(f"✅ Notifica incrocio '{notification_type}' inviata con successo")
            else:
                logging.warning(f"⚠️ Errore invio notifica incrocio '{notification_type}': {message}")
                
        except Exception as e:
            logging.error(f"❌ Errore invio notifica incrocio '{notification_type}': {e}")
    
    def _is_notification_enabled(self, notification_category: str) -> bool:
        """Controlla se le notifiche per una categoria sono abilitate"""
        try:
            if not self.supabase:
                return True  # Default abilitato se Supabase non disponibile
            
            # Recupera impostazioni notifiche dal database
            response = self.supabase.supabase.table('notification_settings').select('*').eq('notification_type', notification_category).execute()
            
            if response.data and len(response.data) > 0:
                setting = response.data[0]
                return setting.get('is_enabled', True)
            else:
                # Se non trova l'impostazione specifica, usa i default
                default_settings = {
                    'incrocio_new_incrocio': True,
                    'incrocio_closed': True,
                    'incrocio_daily_report': False,
                    'incrocio_long_open_alert': False,
                }
                return default_settings.get(notification_category, True)
                
        except Exception as e:
            logging.error(f"❌ Errore controllo impostazioni notifiche {notification_category}: {e}")
            return True  # Default abilitato in caso di errore
