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
