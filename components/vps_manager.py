"""
🎯 VPS MANAGER - Sistema Gestione VPS Completo
🔒 Gestione sicura dei server VPS con notifiche scadenze
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VPSManager:
    """Gestore VPS per monitoraggio scadenze e gestione credenziali"""
    
    def __init__(self):
        """Inizializza il VPS Manager"""
        self.supabase_manager = None
        self.telegram_manager = None
        self._init_supabase()
        # Non inizializzare TelegramManager qui per evitare loop infinito
        # self._init_telegram()
        logger.info("✅ VPSManager inizializzato")
    
    def _init_supabase(self):
        """Inizializza la connessione Supabase"""
        try:
            from supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
            logger.info("✅ Supabase inizializzato per VPSManager")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase: {e}")
            self.supabase_manager = None
    
    def _init_telegram(self):
        """Inizializza il gestore Telegram"""
        try:
            from components.telegram_manager import TelegramManager
            self.telegram_manager = TelegramManager()
            logger.info("✅ TelegramManager inizializzato per VPSManager")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione TelegramManager: {e}")
            self.telegram_manager = None
    
    def _encrypt_password(self, password: str) -> str:
        """Password VPS senza crittografia (versione semplificata)"""
        return password
    
    def _decrypt_password(self, password: str) -> str:
        """Password VPS senza crittografia (versione semplificata)"""
        return password
    
    def get_all_vps(self) -> List[Dict[str, Any]]:
        """Recupera tutti i VPS dal database"""
        try:
            from supabase_manager import SupabaseManager
            
            supabase_manager = SupabaseManager()
            
            if not supabase_manager.is_configured:
                st.error("❌ Database non configurato")
                return []
            
            # Recupera tutti i clienti con dati VPS
            clienti = supabase_manager.get_clienti()
            
            # Filtra solo i clienti con VPS
            vps_list = []
            for cliente in clienti:
                if cliente.get('vps_ip') and cliente.get('vps_ip').strip():
                    vps_data = {
                        'id': cliente['id'],
                        'nome_cliente': cliente['nome_cliente'],
                        'email': cliente['email'],
                        'broker': cliente['broker'],
                        'vps_ip': cliente.get('vps_ip', ''),
                        'vps_username': cliente.get('vps_username', ''),
                        'vps_password': self._decrypt_password(cliente.get('vps_password', '')),
                        'data_rinnovo': cliente.get('data_rinnovo'),
                        'prezzo_vps': cliente.get('prezzo_vps', 0.0),
                        'created_at': cliente.get('created_at'),
                        'updated_at': cliente.get('updated_at')
                    }
                    vps_list.append(vps_data)
            
            return vps_list
            
        except Exception as e:
            logger.error(f"Errore recupero VPS: {e}")
            st.error(f"❌ Errore recupero VPS: {e}")
            return []
    
    def update_vps_data(self, cliente_id: str, vps_data: Dict[str, Any]) -> bool:
        """Aggiorna i dati VPS di un cliente"""
        try:
            from supabase_manager import SupabaseManager
            
            supabase_manager = SupabaseManager()
            
            if not supabase_manager.is_configured:
                st.error("❌ Database non configurato")
                return False
            
            # Prepara i dati per l'aggiornamento
            update_data = {
                'vps_ip': vps_data.get('vps_ip', ''),
                'vps_username': vps_data.get('vps_username', ''),
                'vps_password': self._encrypt_password(vps_data.get('vps_password', '')),
                'updated_at': datetime.now().isoformat()
            }
            
            # Aggiungi campi opzionali se presenti
            if 'data_rinnovo' in vps_data and vps_data['data_rinnovo']:
                update_data['data_rinnovo'] = vps_data['data_rinnovo']
            
            if 'prezzo_vps' in vps_data and vps_data['prezzo_vps']:
                update_data['prezzo_vps'] = float(vps_data['prezzo_vps'])
            
            # Aggiorna il cliente
            result = supabase_manager.supabase.table('clienti').update(update_data).eq('id', cliente_id).execute()
            
            if result.data:
                # Invia notifica Telegram per aggiornamento VPS
                self._send_vps_notification('vps_updated', {
                    'cliente_id': cliente_id,
                    'vps_ip': vps_data.get('vps_ip', 'N/A'),
                    'data_rinnovo': vps_data.get('data_rinnovo', 'N/A'),
                    'prezzo_vps': vps_data.get('prezzo_vps', 'N/A'),
                    'updated_at': update_data['updated_at']
                })
                
                st.success("✅ Dati VPS aggiornati con successo!")
                return True
            else:
                st.error("❌ Errore aggiornamento dati VPS")
                return False
                
        except Exception as e:
            logger.error(f"Errore aggiornamento VPS: {e}")
            st.error(f"❌ Errore aggiornamento VPS: {e}")
            return False
    
    def get_vps_expiring_soon(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Recupera VPS che scadono nei prossimi N giorni"""
        try:
            all_vps = self.get_all_vps()
            expiring_vps = []
            
            if not all_vps:
                return expiring_vps
            
            # Data limite per le scadenze
            limit_date = datetime.now() + timedelta(days=days_ahead)
            
            for vps in all_vps:
                data_rinnovo = vps.get('data_rinnovo')
                if data_rinnovo:
                    try:
                        # Converte la data stringa in datetime
                        if isinstance(data_rinnovo, str):
                            rinnovo_date = datetime.fromisoformat(data_rinnovo.replace('Z', '+00:00'))
                        else:
                            rinnovo_date = data_rinnovo
                        
                        # Se la data di rinnovo è entro il limite
                        if rinnovo_date.date() <= limit_date.date():
                            # Calcola giorni rimanenti
                            giorni_rimanenti = (rinnovo_date.date() - datetime.now().date()).days
                            vps['giorni_rimanenti'] = giorni_rimanenti
                            expiring_vps.append(vps)
                            
                    except Exception as e:
                        logger.warning(f"Errore parsing data rinnovo per VPS {vps['nome_cliente']}: {e}")
                        continue
            
            # Ordina per giorni rimanenti (più urgenti prima)
            expiring_vps.sort(key=lambda x: x.get('giorni_rimanenti', 999))
            
            return expiring_vps
            
        except Exception as e:
            logger.error(f"Errore recupero VPS in scadenza: {e}")
            return []
    
    def get_vps_statistics(self) -> Dict[str, Any]:
        """Recupera statistiche sui VPS"""
        try:
            all_vps = self.get_all_vps()
            
            if not all_vps:
                return {
                    'totale_vps': 0,
                    'vps_scadenti_30_giorni': 0,
                    'vps_scadenti_15_giorni': 0,
                    'vps_scadenti_7_giorni': 0,
                    'costo_totale_mensile': 0.0
                }
            
            # Statistiche base
            totale_vps = len(all_vps)
            
            # VPS in scadenza
            vps_30_giorni = len(self.get_vps_expiring_soon(30))
            vps_15_giorni = len(self.get_vps_expiring_soon(15))
            vps_7_giorni = len(self.get_vps_expiring_soon(7))
            
            # Costo totale mensile
            costo_totale = sum(
                float(vps.get('prezzo_vps', 0)) for vps in all_vps 
                if vps.get('prezzo_vps')
            )
            
            return {
                'totale_vps': totale_vps,
                'vps_scadenti_30_giorni': vps_30_giorni,
                'vps_scadenti_15_giorni': vps_15_giorni,
                'vps_scadenti_7_giorni': vps_7_giorni,
                'costo_totale_mensile': costo_totale
            }
            
        except Exception as e:
            logger.error(f"Errore calcolo statistiche VPS: {e}")
            return {
                'totale_vps': 0,
                'vps_scadenti_30_giorni': 0,
                'vps_scadenti_15_giorni': 0,
                'vps_scadenti_7_giorni': 0,
                'costo_totale_mensile': 0.0
            }
    
    def export_vps_data(self) -> pd.DataFrame:
        """Esporta tutti i dati VPS in un DataFrame"""
        try:
            all_vps = self.get_all_vps()
            
            if not all_vps:
                return pd.DataFrame()
            
            # Crea DataFrame
            df = pd.DataFrame(all_vps)
            
            # Riordina colonne per una migliore visualizzazione
            column_order = [
                'nome_cliente', 'email', 'broker', 'vps_ip', 
                'vps_username', 'data_rinnovo', 'prezzo_vps', 
                'created_at', 'updated_at'
            ]
            
            # Mantieni solo le colonne esistenti
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            return df
            
        except Exception as e:
            logger.error(f"Errore esportazione dati VPS: {e}")
            return pd.DataFrame()
    
    def _send_vps_notification(self, notification_type: str, data: Dict[str, Any]):
        """Invia notifica Telegram per eventi VPS"""
        try:
            # Inizializza TelegramManager solo se necessario
            if not self.telegram_manager:
                self._init_telegram()
            
            if not self.telegram_manager or not self.telegram_manager.is_configured:
                logger.info("📱 Telegram non configurato, notifica VPS non inviata")
                return
            
            # Controlla se le notifiche VPS sono abilitate
            if not self._is_notification_enabled('vps'):
                logger.info("🔔 Notifiche VPS disabilitate")
                return
            
            # Invia la notifica
            success, message = self.telegram_manager.send_notification(notification_type, data)
            
            if success:
                logger.info(f"✅ Notifica VPS '{notification_type}' inviata con successo")
            else:
                logger.warning(f"⚠️ Errore invio notifica VPS '{notification_type}': {message}")
                
        except Exception as e:
            logger.error(f"❌ Errore invio notifica VPS '{notification_type}': {e}")
    
    def _is_notification_enabled(self, notification_category: str) -> bool:
        """Controlla se le notifiche per una categoria sono abilitate"""
        try:
            if not self.supabase_manager:
                return True  # Default abilitato se Supabase non disponibile
            
            # Recupera impostazioni notifiche dal database
            response = self.supabase_manager.supabase.table('notification_settings').select('*').eq('notification_type', notification_category).execute()
            
            if response.data and len(response.data) > 0:
                setting = response.data[0]
                return setting.get('is_enabled', True)
            else:
                return True  # Default abilitato se nessuna impostazione trovata
                
        except Exception as e:
            logger.error(f"❌ Errore controllo impostazioni notifiche {notification_category}: {e}")
            return True  # Default abilitato in caso di errore
    
    def check_vps_expiring_notifications(self):
        """Controlla VPS in scadenza e invia notifiche"""
        try:
            if not self.telegram_manager or not self.telegram_manager.is_configured:
                return
            
            # Recupera VPS in scadenza (nei prossimi 7 giorni)
            expiring_vps = self.get_vps_expiring_soon(7)
            
            for vps in expiring_vps:
                try:
                    days_left = vps.get('days_until_expiry', 0)
                    
                    # Invia notifica se scade tra 1-7 giorni
                    if 1 <= days_left <= 7:
                        self._send_vps_notification('vps_expiring', {
                            'cliente_nome': vps.get('nome_cliente', 'N/A'),
                            'vps_ip': vps.get('vps_ip', 'N/A'),
                            'data_rinnovo': vps.get('data_rinnovo', 'N/A'),
                            'days_left': days_left,
                            'prezzo_vps': vps.get('prezzo_vps', 'N/A')
                        })
                except Exception as e:
                    logger.error(f"❌ Errore controllo scadenza VPS {vps.get('id')}: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Errore controllo VPS in scadenza: {e}")
