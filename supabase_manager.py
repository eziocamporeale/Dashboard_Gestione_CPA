"""
🎯 SUPABASE MANAGER - Sistema Database Remoto Professionale
🔒 Gestione separata e sicura per test e validazione
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    """Gestore Supabase per database remoto professionale"""
    
    def __init__(self):
        # Prova prima le variabili ambiente locali
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        # Se non disponibili, prova i secrets di Streamlit Cloud
        if not self.supabase_url or not self.supabase_key:
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'supabase' in st.secrets:
                    self.supabase_url = st.secrets.supabase.url
                    self.supabase_key = st.secrets.supabase.anon_key
                    logger.info("✅ Configurazione da Streamlit Cloud secrets")
            except ImportError:
                pass
        
        self.is_configured = bool(self.supabase_url and self.supabase_key)
        
        if self.is_configured:
            try:
                from supabase import create_client, Client
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client inizializzato")
            except ImportError:
                logger.warning("⚠️ Supabase non installato: pip install supabase")
                self.supabase = None
            except Exception as e:
                logger.error(f"❌ Errore inizializzazione: {e}")
                self.supabase = None
        else:
            logger.warning("⚠️ Variabili ambiente Supabase non configurate")
            self.supabase = None
    
    def test_connection(self) -> Tuple[bool, str]:
        """Testa la connessione a Supabase"""
        if not self.is_configured:
            return False, "❌ Supabase non configurato"
        
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            response = self.supabase.table('clienti').select('count', count='exact').execute()
            return True, "✅ Connessione Supabase attiva"
        except Exception as e:
            return False, f"❌ Errore connessione: {e}"
    
    def get_clienti(self) -> List[Dict[str, Any]]:
        """Recupera tutti i clienti da Supabase"""
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table('clienti').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero clienti: {e}")
            return []
    
    def add_cliente(self, cliente_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiunge un nuovo cliente su Supabase"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            cliente_data['created_at'] = datetime.now().isoformat()
            cliente_data['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('clienti').insert(cliente_data).execute()
            
            if response.data:
                return True, f"✅ Cliente {cliente_data.get('nome_cliente')} aggiunto"
            else:
                return False, "❌ Errore inserimento cliente"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def update_cliente(self, cliente_id: str, cliente_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiorna un cliente esistente su Supabase"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            cliente_data['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('clienti').update(cliente_data).eq('id', cliente_id).execute()
            
            if response.data:
                return True, "✅ Cliente aggiornato con successo"
            else:
                return False, "❌ Cliente non trovato"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def delete_cliente(self, cliente_id: str) -> Tuple[bool, str]:
        """Elimina un cliente da Supabase"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            response = self.supabase.table('clienti').delete().eq('id', cliente_id).execute()
            
            if response.data:
                return True, "✅ Cliente eliminato con successo"
            else:
                return False, "❌ Cliente non trovato"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def get_incroci(self) -> List[Dict[str, Any]]:
        """Recupera tutti gli incroci da Supabase"""
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table('incroci').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero incroci: {e}")
            return []
    
    def add_incrocio(self, incrocio_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiunge un nuovo incrocio su Supabase"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            incrocio_data['created_at'] = datetime.now().isoformat()
            incrocio_data['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('incroci').insert(incrocio_data).execute()
            
            if response.data:
                return True, "✅ Incrocio aggiunto con successo"
            else:
                return False, "❌ Errore inserimento incrocio"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def delete_incrocio(self, incrocio_id: str) -> Tuple[bool, str]:
        """Elimina un incrocio da Supabase"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            response = self.supabase.table('incroci').delete().eq('id', incrocio_id).execute()
            
            if response.data:
                return True, "✅ Incrocio eliminato con successo"
            else:
                return False, "❌ Incrocio non trovato"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def get_database_info(self) -> Dict[str, Any]:
        """Recupera informazioni sul database Supabase"""
        if not self.supabase:
            return {"error": "❌ Supabase non configurato"}
        
        try:
            # Conta clienti
            clienti_count = len(self.get_clienti())
            
            # Conta incroci
            incroci_count = len(self.get_incroci())
            
            return {
                "tipo": "Supabase PostgreSQL",
                "clienti_count": clienti_count,
                "incroci_count": incroci_count,
                "stato": "✅ Attivo",
                "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
        except Exception as e:
            return {"error": f"❌ Errore: {e}"}

    # ========================================
    # METODI PER BROKER LINKS
    # ========================================
    
    def create_broker_link(self, broker_name: str, affiliate_link: str) -> Tuple[bool, str]:
        """Crea un nuovo link broker"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            data = {
                'broker_name': broker_name,
                'affiliate_link': affiliate_link,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('broker_links').insert(data).execute()
            
            if response.data:
                return True, f"✅ Link broker {broker_name} creato"
            else:
                return False, "❌ Errore creazione link broker"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def get_broker_links(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Recupera tutti i link broker da Supabase"""
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table('broker_links').select('*')
            if active_only:
                query = query.eq('is_active', True)
            query = query.order('created_at', desc=True)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Errore recupero broker links: {e}")
            return []
    
    def get_broker_link(self, link_id: int) -> Optional[Dict[str, Any]]:
        """Recupera un singolo link broker"""
        if not self.supabase:
            return None
        
        try:
            response = self.supabase.table('broker_links').select('*').eq('id', link_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ Errore recupero broker link: {e}")
            return None
    
    def update_broker_link(self, link_id: int, broker_name: str, affiliate_link: str, is_active: bool = True) -> Tuple[bool, str]:
        """Aggiorna un link broker esistente"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            data = {
                'broker_name': broker_name,
                'affiliate_link': affiliate_link,
                'is_active': is_active,
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('broker_links').update(data).eq('id', link_id).execute()
            
            if response.data:
                return True, f"✅ Link broker {broker_name} aggiornato"
            else:
                return False, "❌ Errore aggiornamento link broker"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def delete_broker_link(self, link_id: int) -> Tuple[bool, str]:
        """Elimina un link broker"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            response = self.supabase.table('broker_links').delete().eq('id', link_id).execute()
            
            if response.data:
                return True, "✅ Link broker eliminato"
            else:
                return False, "❌ Errore eliminazione link broker"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def toggle_broker_link_status(self, link_id: int) -> Tuple[bool, str]:
        """Attiva/disattiva un link broker"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            # Prima ottieni lo stato attuale
            current = self.get_broker_link(link_id)
            if current is None:
                return False, "❌ Link broker non trovato"
            
            new_status = not current.get('is_active', True)
            data = {
                'is_active': new_status,
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('broker_links').update(data).eq('id', link_id).execute()
            
            if response.data:
                status_text = "attivato" if new_status else "disattivato"
                return True, f"✅ Link broker {status_text}"
            else:
                return False, "❌ Errore cambio stato link broker"
                
        except Exception as e:
            return False, f"❌ Errore: {e}"
    
    def get_broker_links_stats(self) -> Dict[str, Any]:
        """Ottiene le statistiche dei link broker"""
        if not self.supabase:
            return {
                'total_links': 0,
                'active_links': 0,
                'inactive_links': 0
            }
        
        try:
            response = self.supabase.table('broker_links').select('*').execute()
            links = response.data if response.data else []
            
            total_links = len(links)
            active_links = len([l for l in links if l.get('is_active', False)])
            inactive_links = total_links - active_links
            
            return {
                'total_links': total_links,
                'active_links': active_links,
                'inactive_links': inactive_links
            }
        except Exception as e:
            logger.error(f"❌ Errore statistiche broker links: {e}")
            return {
                'total_links': 0,
                'active_links': 0,
                'inactive_links': 0
            }

    # ==================== METODI GESTIONE RUOLI ====================
    
    def get_roles(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i ruoli disponibili"""
        try:
            if not self.is_configured:
                return []
            
            response = self.supabase.table('roles').select('*').order('name').execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero ruoli: {e}")
            return []
    
    def get_role_by_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene un ruolo per ID"""
        try:
            if not self.is_configured:
                return None
            
            response = self.supabase.table('roles').select('*').eq('id', role_id).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"❌ Errore recupero ruolo {role_id}: {e}")
            return None
    
    def get_role_by_name(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Ottiene un ruolo per nome"""
        try:
            if not self.is_configured:
                return None
            
            response = self.supabase.table('roles').select('*').eq('name', role_name).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"❌ Errore recupero ruolo {role_name}: {e}")
            return None
    
    def create_role(self, name: str, description: str = "", permissions: List[str] = None) -> Tuple[bool, str]:
        """Crea un nuovo ruolo"""
        try:
            if not self.is_configured:
                return False, "Supabase non configurato"
            
            if permissions is None:
                permissions = []
            
            data = {
                'name': name,
                'description': description,
                'permissions': permissions
            }
            
            response = self.supabase.table('roles').insert(data).execute()
            
            if response.data:
                logger.info(f"✅ Ruolo '{name}' creato con successo")
                return True, f"Ruolo '{name}' creato con successo"
            else:
                return False, "Errore nella creazione del ruolo"
                
        except Exception as e:
            logger.error(f"❌ Errore creazione ruolo {name}: {e}")
            return False, f"Errore: {e}"
    
    def update_role(self, role_id: int, name: str = None, description: str = None, permissions: List[str] = None) -> Tuple[bool, str]:
        """Aggiorna un ruolo esistente"""
        try:
            if not self.is_configured:
                return False, "Supabase non configurato"
            
            data = {}
            if name is not None:
                data['name'] = name
            if description is not None:
                data['description'] = description
            if permissions is not None:
                data['permissions'] = permissions
            
            if not data:
                return False, "Nessun dato da aggiornare"
            
            response = self.supabase.table('roles').update(data).eq('id', role_id).execute()
            
            if response.data:
                logger.info(f"✅ Ruolo {role_id} aggiornato con successo")
                return True, "Ruolo aggiornato con successo"
            else:
                return False, "Errore nell'aggiornamento del ruolo"
                
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento ruolo {role_id}: {e}")
            return False, f"Errore: {e}"
    
    def delete_role(self, role_id: int) -> Tuple[bool, str]:
        """Elimina un ruolo"""
        try:
            if not self.is_configured:
                return False, "Supabase non configurato"
            
            # Verifica se ci sono utenti che usano questo ruolo
            users_response = self.supabase.table('users').select('id').eq('role_id', role_id).execute()
            if users_response.data:
                return False, f"Impossibile eliminare: {len(users_response.data)} utenti utilizzano questo ruolo"
            
            response = self.supabase.table('roles').delete().eq('id', role_id).execute()
            
            if response.data:
                logger.info(f"✅ Ruolo {role_id} eliminato con successo")
                return True, "Ruolo eliminato con successo"
            else:
                return False, "Errore nell'eliminazione del ruolo"
                
        except Exception as e:
            logger.error(f"❌ Errore eliminazione ruolo {role_id}: {e}")
            return False, f"Errore: {e}"
    
    def assign_role_to_user(self, user_id: str, role_id: int) -> Tuple[bool, str]:
        """Assegna un ruolo a un utente"""
        try:
            if not self.is_configured:
                return False, "Supabase non configurato"
            
            response = self.supabase.table('users').update({'role_id': role_id}).eq('id', user_id).execute()
            
            if response.data:
                logger.info(f"✅ Ruolo {role_id} assegnato all'utente {user_id}")
                return True, "Ruolo assegnato con successo"
            else:
                return False, "Errore nell'assegnazione del ruolo"
                
        except Exception as e:
            logger.error(f"❌ Errore assegnazione ruolo {role_id} a utente {user_id}: {e}")
            return False, f"Errore: {e}"
    
    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """Elimina un utente dal database"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            # Verifica che l'utente esista
            response = self.supabase.table('users').select('username').eq('id', user_id).execute()
            if not response.data:
                return False, "❌ Utente non trovato"
            
            username = response.data[0]['username']
            
            # Elimina l'utente
            delete_response = self.supabase.table('users').delete().eq('id', user_id).execute()
            
            if delete_response.data:
                logger.info(f"✅ Utente {username} eliminato con successo")
                return True, f"✅ Utente {username} eliminato con successo"
            else:
                return False, "❌ Errore durante l'eliminazione"
                
        except Exception as e:
            logger.error(f"❌ Errore eliminazione utente {user_id}: {e}")
            return False, f"❌ Errore: {e}"
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Aggiorna i dati di un utente"""
        if not self.supabase:
            return False, "❌ Client Supabase non disponibile"
        
        try:
            # Verifica che l'utente esista
            response = self.supabase.table('users').select('username').eq('id', user_id).execute()
            if not response.data:
                return False, "❌ Utente non trovato"
            
            username = response.data[0]['username']
            
            # Aggiungi timestamp di aggiornamento
            user_data['updated_at'] = datetime.now().isoformat()
            
            # Aggiorna l'utente
            update_response = self.supabase.table('users').update(user_data).eq('id', user_id).execute()
            
            if update_response.data:
                logger.info(f"✅ Utente {username} aggiornato con successo")
                return True, f"✅ Utente {username} aggiornato con successo"
            else:
                return False, "❌ Errore durante l'aggiornamento"
                
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento utente {user_id}: {e}")
            return False, f"❌ Errore: {e}"

def show_supabase_status():
    """Mostra lo stato di Supabase nell'interfaccia"""
    try:
        import streamlit as st
    except ImportError:
        logger.error("❌ Streamlit non disponibile")
        return False
    
    manager = SupabaseManager()
    
    if not manager.is_configured:
        st.warning("⚠️ **SUPABASE NON CONFIGURATO**")
        st.info("📋 Configura le variabili ambiente SUPABASE_URL e SUPABASE_KEY")
        return False
    
    success, message = manager.test_connection()
    
    if success:
        st.success(f"🔗 **SUPABASE**: {message}")
        return True
    else:
        st.error(f"❌ **SUPABASE**: {message}")
        return False
