#!/usr/bin/env python3
"""
Client Analyzer per Dashboard Gestione CPA
Analizza i dati dei clienti e fornisce insights professionali
Creato da Ezio Camporeale
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientAnalyzer:
    """Classe per l'analisi avanzata dei clienti CPA"""
    
    def __init__(self, supabase_manager=None):
        """Inizializza l'analizzatore clienti"""
        self.supabase_manager = supabase_manager
        self.ai_assistant = None
        
        # Inizializza AI Assistant
        try:
            from .ai_core import AIAssistant
            self.ai_assistant = AIAssistant()
            logger.info("✅ ClientAnalyzer inizializzato con AI Assistant")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione AI Assistant: {e}")
    
    def analyze_client(self, cliente_id: int) -> Dict[str, Any]:
        """
        Analizza un cliente specifico
        
        Args:
            cliente_id: ID del cliente da analizzare
            
        Returns:
            Dict: Risultati dell'analisi
        """
        try:
            # Recupera dati cliente
            client_data = self._get_client_data(cliente_id)
            if not client_data:
                return {"error": "Cliente non trovato"}
            
            # Recupera storia incroci
            incroci_history = self._get_client_incroci_history(cliente_id)
            
            # Prepara dati per AI
            ai_data = self._prepare_ai_data(client_data, incroci_history)
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('client_analysis', ai_data)
            
            # Calcola metriche di base
            metrics = self._calculate_client_metrics(client_data, incroci_history)
            
            return {
                'client_data': client_data,
                'incroci_history': incroci_history,
                'metrics': metrics,
                'ai_analysis': ai_analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi cliente {cliente_id}: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def analyze_all_clients(self) -> Dict[str, Any]:
        """
        Analizza tutti i clienti per una panoramica generale
        
        Returns:
            Dict: Analisi aggregata di tutti i clienti
        """
        try:
            # Recupera tutti i clienti
            all_clients = self._get_all_clients_data()
            if not all_clients:
                return {"error": "Nessun cliente trovato"}
            
            # Analisi aggregata
            aggregated_metrics = self._calculate_aggregated_metrics(all_clients)
            
            # Prepara dati per AI
            ai_data = {
                'clienti_data': self._format_clients_for_ai(all_clients),
                'aggregated_metrics': aggregated_metrics
            }
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('marketing_advice', ai_data)
            
            return {
                'total_clients': len(all_clients),
                'aggregated_metrics': aggregated_metrics,
                'ai_analysis': ai_analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi tutti i clienti: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def _get_client_data(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Recupera i dati di un cliente specifico"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                # Query per recuperare dati cliente con account broker
                query = """
                SELECT 
                    cb.id,
                    cb.nome_cliente,
                    cb.email,
                    cb.vps,
                    cb.note_cliente,
                    cb.created_at,
                    ab.broker,
                    ab.piattaforma,
                    ab.numero_conto,
                    ab.volume_posizione,
                    ab.ruolo,
                    ab.stato_account,
                    ab.data_registrazione
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                WHERE cb.id = %s
                """
                
                result = self.supabase_manager.execute_query(query, (cliente_id,))
                if result and len(result) > 0:
                    return result[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati cliente {cliente_id}: {e}")
            return None
    
    def _get_client_incroci_history(self, cliente_id: int) -> List[Dict[str, Any]]:
        """Recupera la storia degli incroci per un cliente"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                # Query per recuperare incroci del cliente
                query = """
                SELECT 
                    i.id,
                    i.data_apertura,
                    i.data_chiusura,
                    i.stato,
                    i.profitto_perdita,
                    i.note,
                    ia.tipo_posizione,
                    ia.broker,
                    ia.volume_posizione,
                    ia.data_apertura_posizione,
                    ia.data_chiusura_posizione,
                    ia.stato_posizione
                FROM incroci i
                JOIN incroci_account ia ON i.id = ia.incrocio_id
                JOIN account_broker ab ON ia.account_id = ab.id
                WHERE ab.cliente_base_id = %s
                ORDER BY i.data_apertura DESC
                LIMIT 50
                """
                
                result = self.supabase_manager.execute_query(query, (cliente_id,))
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero incroci cliente {cliente_id}: {e}")
            return []
    
    def _get_all_clients_data(self) -> List[Dict[str, Any]]:
        """Recupera i dati di tutti i clienti"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    cb.id,
                    cb.nome_cliente,
                    cb.email,
                    cb.created_at,
                    COUNT(ab.id) as num_accounts,
                    AVG(ab.volume_posizione) as avg_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(CASE WHEN i.profitto_perdita > 0 THEN i.profitto_perdita ELSE 0 END) as total_profits,
                    SUM(CASE WHEN i.profitto_perdita < 0 THEN i.profitto_perdita ELSE 0 END) as total_losses
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci i ON ab.id = i.id
                GROUP BY cb.id, cb.nome_cliente, cb.email, cb.created_at
                ORDER BY cb.created_at DESC
                """
                
                result = self.supabase_manager.execute_query(query)
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero tutti i clienti: {e}")
            return []
    
    def _prepare_ai_data(self, client_data: Dict[str, Any], incroci_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara i dati per l'analisi AI"""
        # Formatta la storia incroci
        storia_incroci = ""
        if incroci_history:
            for incrocio in incroci_history[:10]:  # Ultimi 10 incroci
                storia_incroci += f"- Data: {incrocio.get('data_apertura', 'N/A')}, "
                storia_incroci += f"Stato: {incrocio.get('stato', 'N/A')}, "
                storia_incroci += f"P&L: {incrocio.get('profitto_perdita', 0)}, "
                storia_incroci += f"Broker: {incrocio.get('broker', 'N/A')}\n"
        else:
            storia_incroci = "Nessun incrocio registrato"
        
        return {
            'nome_cliente': client_data.get('nome_cliente', 'N/A'),
            'email': client_data.get('email', 'N/A'),
            'broker': client_data.get('broker', 'N/A'),
            'piattaforma': client_data.get('piattaforma', 'N/A'),
            'volume_posizione': client_data.get('volume_posizione', 0),
            'stato_account': client_data.get('stato_account', 'N/A'),
            'data_registrazione': client_data.get('data_registrazione', 'N/A'),
            'storia_incroci': storia_incroci
        }
    
    def _format_clients_for_ai(self, clients_data: List[Dict[str, Any]]) -> str:
        """Formatta i dati dei clienti per l'AI"""
        formatted_data = ""
        for client in clients_data[:20]:  # Top 20 clienti
            formatted_data += f"- {client.get('nome_cliente', 'N/A')}: "
            formatted_data += f"{client.get('num_accounts', 0)} account, "
            formatted_data += f"{client.get('num_incroci', 0)} incroci, "
            formatted_data += f"Profitti: {client.get('total_profits', 0)}, "
            formatted_data += f"Perdite: {client.get('total_losses', 0)}\n"
        
        return formatted_data
    
    def _calculate_client_metrics(self, client_data: Dict[str, Any], incroci_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola le metriche di base per un cliente"""
        metrics = {
            'total_incroci': len(incroci_history),
            'total_profits': 0,
            'total_losses': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'avg_loss': 0
        }
        
        if incroci_history:
            profits = [inc['profitto_perdita'] for inc in incroci_history if inc['profitto_perdita'] > 0]
            losses = [inc['profitto_perdita'] for inc in incroci_history if inc['profitto_perdita'] < 0]
            
            metrics['total_profits'] = sum(profits)
            metrics['total_losses'] = sum(losses)
            metrics['win_rate'] = len(profits) / len(incroci_history) * 100 if incroci_history else 0
            metrics['avg_profit'] = sum(profits) / len(profits) if profits else 0
            metrics['avg_loss'] = sum(losses) / len(losses) if losses else 0
        
        return metrics
    
    def _calculate_aggregated_metrics(self, clients_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola le metriche aggregate per tutti i clienti"""
        if not clients_data:
            return {}
        
        total_clients = len(clients_data)
        total_accounts = sum(client.get('num_accounts', 0) for client in clients_data)
        total_incroci = sum(client.get('num_incroci', 0) for client in clients_data)
        total_profits = sum(client.get('total_profits', 0) for client in clients_data)
        total_losses = sum(client.get('total_losses', 0) for client in clients_data)
        
        return {
            'total_clients': total_clients,
            'total_accounts': total_accounts,
            'total_incroci': total_incroci,
            'total_profits': total_profits,
            'total_losses': total_losses,
            'net_result': total_profits + total_losses,
            'avg_accounts_per_client': total_accounts / total_clients if total_clients > 0 else 0,
            'avg_incroci_per_client': total_incroci / total_clients if total_clients > 0 else 0
        }
