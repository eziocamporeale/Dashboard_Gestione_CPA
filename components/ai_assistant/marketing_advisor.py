#!/usr/bin/env python3
"""
Marketing Advisor per Dashboard Gestione CPA
Fornisce consigli di marketing basati sui dati dei clienti
Creato da Ezio Camporeale
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketingAdvisor:
    """Classe per i consigli di marketing CPA"""
    
    def __init__(self, supabase_manager=None):
        """Inizializza l'advisor di marketing"""
        self.supabase_manager = supabase_manager
        self.ai_assistant = None
        
        # Inizializza AI Assistant
        try:
            from .ai_core import AIAssistant
            self.ai_assistant = AIAssistant()
            logger.info("✅ MarketingAdvisor inizializzato con AI Assistant")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione AI Assistant: {e}")
    
    def generate_marketing_advice(self) -> Dict[str, Any]:
        """
        Genera consigli di marketing basati sui dati dei clienti
        
        Returns:
            Dict: Consigli di marketing
        """
        try:
            # Recupera dati clienti
            client_data = self._get_client_marketing_data()
            
            # Analizza segmentazione clienti
            client_segmentation = self._analyze_client_segmentation(client_data)
            
            # Identifica opportunità di crescita
            growth_opportunities = self._identify_growth_opportunities(client_data)
            
            # Calcola strategie di retention
            retention_strategies = self._calculate_retention_strategies(client_data)
            
            # Prepara dati per AI
            ai_data = self._prepare_marketing_ai_data(client_data, client_segmentation, growth_opportunities, retention_strategies)
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('marketing_advice', ai_data)
            
            return {
                'client_data': client_data,
                'client_segmentation': client_segmentation,
                'growth_opportunities': growth_opportunities,
                'retention_strategies': retention_strategies,
                'ai_analysis': ai_analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore generazione consigli marketing: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def analyze_client_lifetime_value(self) -> Dict[str, Any]:
        """
        Analizza il valore del ciclo di vita dei clienti
        
        Returns:
            Dict: Analisi CLV
        """
        try:
            # Recupera dati CLV
            clv_data = self._get_client_lifetime_value_data()
            
            # Calcola metriche CLV
            clv_metrics = self._calculate_clv_metrics(clv_data)
            
            # Identifica clienti ad alto valore
            high_value_clients = self._identify_high_value_clients(clv_data)
            
            # Calcola strategie di upselling
            upselling_strategies = self._calculate_upselling_strategies(clv_data, high_value_clients)
            
            return {
                'clv_data': clv_data,
                'clv_metrics': clv_metrics,
                'high_value_clients': high_value_clients,
                'upselling_strategies': upselling_strategies,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi CLV: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def _get_client_marketing_data(self) -> List[Dict[str, Any]]:
        """Recupera i dati dei clienti per l'analisi di marketing"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    cb.id,
                    cb.nome_cliente,
                    cb.email,
                    cb.created_at,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(CASE WHEN i.profitto_perdita > 0 THEN i.profitto_perdita ELSE 0 END) as total_profits,
                    SUM(CASE WHEN i.profitto_perdita < 0 THEN i.profitto_perdita ELSE 0 END) as total_losses,
                    SUM(i.profitto_perdita) as net_result,
                    COUNT(CASE WHEN i.profitto_perdita > 0 THEN 1 END) as successful_incroci,
                    COUNT(CASE WHEN i.profitto_perdita < 0 THEN 1 END) as failed_incroci,
                    MAX(i.data_apertura) as last_activity,
                    MIN(i.data_apertura) as first_activity,
                    COUNT(DISTINCT ab.broker) as num_brokers,
                    AVG(ab.volume_posizione) as avg_volume_per_account
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                GROUP BY cb.id, cb.nome_cliente, cb.email, cb.created_at
                ORDER BY net_result DESC
                """
                
                result = self.supabase_manager.execute_query(query)
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati marketing clienti: {e}")
            return []
    
    def _get_client_lifetime_value_data(self) -> List[Dict[str, Any]]:
        """Recupera i dati per il calcolo del CLV"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    cb.id,
                    cb.nome_cliente,
                    cb.email,
                    cb.created_at,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(i.profitto_perdita) as total_pnl,
                    COUNT(CASE WHEN i.profitto_perdita > 0 THEN 1 END) as successful_incroci,
                    COUNT(CASE WHEN i.profitto_perdita < 0 THEN 1 END) as failed_incroci,
                    MAX(i.data_apertura) as last_activity,
                    MIN(i.data_apertura) as first_activity,
                    COUNT(DISTINCT ab.broker) as num_brokers,
                    SUM(ib.importo_bonus) as total_bonus_received,
                    COUNT(ib.id) as num_bonus
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                LEFT JOIN incroci_bonus ib ON i.id = ib.incrocio_id
                GROUP BY cb.id, cb.nome_cliente, cb.email, cb.created_at
                ORDER BY total_pnl DESC
                """
                
                result = self.supabase_manager.execute_query(query)
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati CLV: {e}")
            return []
    
    def _analyze_client_segmentation(self, client_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza la segmentazione dei clienti"""
        if not client_data:
            return {}
        
        segmentation = {
            'total_clients': len(client_data),
            'segments': {
                'high_value': [],
                'medium_value': [],
                'low_value': [],
                'new_clients': [],
                'inactive_clients': []
            },
            'segment_metrics': {}
        }
        
        # Calcola metriche per segmentazione
        total_net_result = sum(client.get('net_result', 0) for client in client_data)
        avg_net_result = total_net_result / len(client_data) if client_data else 0
        
        # Data limite per clienti nuovi (ultimi 30 giorni)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for client in client_data:
            client_name = client.get('nome_cliente', 'Unknown')
            net_result = client.get('net_result', 0)
            num_incroci = client.get('num_incroci', 0)
            last_activity = client.get('last_activity')
            
            # Determina segmento basato su performance
            if net_result > avg_net_result * 1.5:
                segmentation['segments']['high_value'].append({
                    'name': client_name,
                    'net_result': net_result,
                    'num_incroci': num_incroci,
                    'segment': 'High Value'
                })
            elif net_result > avg_net_result * 0.5:
                segmentation['segments']['medium_value'].append({
                    'name': client_name,
                    'net_result': net_result,
                    'num_incroci': num_incroci,
                    'segment': 'Medium Value'
                })
            else:
                segmentation['segments']['low_value'].append({
                    'name': client_name,
                    'net_result': net_result,
                    'num_incroci': num_incroci,
                    'segment': 'Low Value'
                })
            
            # Cliente nuovo (registrato negli ultimi 30 giorni)
            try:
                created_at = datetime.strptime(client.get('created_at', ''), '%Y-%m-%d %H:%M:%S')
                if created_at > thirty_days_ago:
                    segmentation['segments']['new_clients'].append({
                        'name': client_name,
                        'created_at': client.get('created_at'),
                        'segment': 'New Client'
                    })
            except:
                pass
            
            # Cliente inattivo (nessuna attività negli ultimi 30 giorni)
            if last_activity:
                try:
                    last_activity_date = datetime.strptime(last_activity, '%Y-%m-%d')
                    if last_activity_date < thirty_days_ago:
                        segmentation['segments']['inactive_clients'].append({
                            'name': client_name,
                            'last_activity': last_activity,
                            'segment': 'Inactive'
                        })
                except:
                    pass
        
        # Calcola metriche per segmento
        for segment_name, segment_clients in segmentation['segments'].items():
            if segment_clients:
                segmentation['segment_metrics'][segment_name] = {
                    'count': len(segment_clients),
                    'percentage': len(segment_clients) / len(client_data) * 100,
                    'avg_net_result': sum(c.get('net_result', 0) for c in segment_clients) / len(segment_clients)
                }
        
        return segmentation
    
    def _identify_growth_opportunities(self, client_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identifica le opportunità di crescita"""
        opportunities = {
            'upselling_opportunities': [],
            'cross_selling_opportunities': [],
            'retention_opportunities': [],
            'acquisition_opportunities': []
        }
        
        # Opportunità di upselling (clienti con pochi account ma buona performance)
        for client in client_data:
            if (client.get('num_accounts', 0) < 3 and 
                client.get('net_result', 0) > 0 and 
                client.get('successful_incroci', 0) > client.get('failed_incroci', 0)):
                
                opportunities['upselling_opportunities'].append({
                    'client': client.get('nome_cliente', 'Unknown'),
                    'current_accounts': client.get('num_accounts', 0),
                    'net_result': client.get('net_result', 0),
                    'potential': 'High'
                })
        
        # Opportunità di cross-selling (clienti con un solo broker)
        for client in client_data:
            if (client.get('num_brokers', 0) == 1 and 
                client.get('num_incroci', 0) > 5):
                
                opportunities['cross_selling_opportunities'].append({
                    'client': client.get('nome_cliente', 'Unknown'),
                    'current_brokers': client.get('num_brokers', 0),
                    'num_incroci': client.get('num_incroci', 0),
                    'potential': 'Medium'
                })
        
        # Opportunità di retention (clienti inattivi ma con buona performance storica)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        for client in client_data:
            if (client.get('last_activity') and 
                client.get('net_result', 0) > 0):
                try:
                    last_activity_date = datetime.strptime(client.get('last_activity', ''), '%Y-%m-%d')
                    if last_activity_date < thirty_days_ago:
                        opportunities['retention_opportunities'].append({
                            'client': client.get('nome_cliente', 'Unknown'),
                            'last_activity': client.get('last_activity'),
                            'net_result': client.get('net_result', 0),
                            'priority': 'High'
                        })
                except:
                    pass
        
        # Opportunità di acquisizione (analisi dei clienti top per identificare pattern)
        top_clients = sorted(client_data, key=lambda x: x.get('net_result', 0), reverse=True)[:5]
        opportunities['acquisition_opportunities'] = [
            {
                'pattern': 'High Volume, High Success',
                'description': f"Clienti come {client.get('nome_cliente', 'Unknown')} con volume {client.get('total_volume', 0)} e success rate {(client.get('successful_incroci', 0) / client.get('num_incroci', 1) * 100):.1f}%",
                'target_criteria': 'Volume > 10000, Success Rate > 70%'
            }
            for client in top_clients
        ]
        
        return opportunities
    
    def _calculate_retention_strategies(self, client_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola le strategie di retention"""
        strategies = {
            'loyalty_programs': [],
            'personalized_offers': [],
            'risk_mitigation': [],
            'communication_strategies': []
        }
        
        # Programmi di loyalty per clienti ad alto valore
        high_value_clients = [c for c in client_data if c.get('net_result', 0) > 1000]
        for client in high_value_clients:
            strategies['loyalty_programs'].append({
                'client': client.get('nome_cliente', 'Unknown'),
                'tier': 'Gold',
                'benefits': ['Commissioni ridotte', 'Supporto prioritario', 'Bonus esclusivi'],
                'retention_value': 'High'
            })
        
        # Offerte personalizzate basate sui pattern
        for client in client_data:
            if client.get('num_incroci', 0) > 10:
                success_rate = (client.get('successful_incroci', 0) / client.get('num_incroci', 1)) * 100
                if success_rate > 70:
                    strategies['personalized_offers'].append({
                        'client': client.get('nome_cliente', 'Unknown'),
                        'offer_type': 'Volume Bonus',
                        'description': 'Bonus del 5% sui volumi superiori a 5000',
                        'expected_impact': 'Increase volume by 20%'
                    })
        
        # Strategie di mitigazione del rischio
        risky_clients = [c for c in client_data if c.get('failed_incroci', 0) > c.get('successful_incroci', 0)]
        for client in risky_clients:
            strategies['risk_mitigation'].append({
                'client': client.get('nome_cliente', 'Unknown'),
                'risk_level': 'High',
                'strategy': 'Risk Management Training',
                'description': 'Offrire training sulla gestione del rischio',
                'expected_outcome': 'Reduce losses by 30%'
            })
        
        # Strategie di comunicazione
        inactive_clients = [c for c in client_data if c.get('last_activity')]
        thirty_days_ago = datetime.now() - timedelta(days=30)
        for client in inactive_clients:
            try:
                last_activity_date = datetime.strptime(client.get('last_activity', ''), '%Y-%m-%d')
                if last_activity_date < thirty_days_ago:
                    strategies['communication_strategies'].append({
                        'client': client.get('nome_cliente', 'Unknown'),
                        'strategy': 'Re-engagement Campaign',
                        'frequency': 'Weekly',
                        'content': 'Market updates, new opportunities, success stories'
                    })
            except:
                pass
        
        return strategies
    
    def _calculate_clv_metrics(self, clv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola le metriche del CLV"""
        if not clv_data:
            return {}
        
        metrics = {
            'total_clients': len(clv_data),
            'total_clv': 0,
            'avg_clv': 0,
            'median_clv': 0,
            'clv_distribution': {},
            'retention_rate': 0,
            'churn_rate': 0
        }
        
        # Calcola CLV per ogni cliente
        clv_values = []
        for client in clv_data:
            # CLV = (Total P&L + Total Bonus) / Number of Accounts
            total_pnl = client.get('total_pnl', 0)
            total_bonus = client.get('total_bonus_received', 0)
            num_accounts = client.get('num_accounts', 1)
            
            clv = (total_pnl + total_bonus) / num_accounts
            clv_values.append(clv)
        
        if clv_values:
            metrics['total_clv'] = sum(clv_values)
            metrics['avg_clv'] = sum(clv_values) / len(clv_values)
            metrics['median_clv'] = sorted(clv_values)[len(clv_values) // 2]
            
            # Distribuzione CLV
            high_clv = len([c for c in clv_values if c > metrics['avg_clv'] * 1.5])
            medium_clv = len([c for c in clv_values if metrics['avg_clv'] * 0.5 <= c <= metrics['avg_clv'] * 1.5])
            low_clv = len([c for c in clv_values if c < metrics['avg_clv'] * 0.5])
            
            metrics['clv_distribution'] = {
                'high': high_clv,
                'medium': medium_clv,
                'low': low_clv
            }
        
        # Calcola retention rate (clienti attivi negli ultimi 30 giorni)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_clients = 0
        for client in clv_data:
            if client.get('last_activity'):
                try:
                    last_activity_date = datetime.strptime(client.get('last_activity', ''), '%Y-%m-%d')
                    if last_activity_date > thirty_days_ago:
                        active_clients += 1
                except:
                    pass
        
        metrics['retention_rate'] = (active_clients / len(clv_data)) * 100 if clv_data else 0
        metrics['churn_rate'] = 100 - metrics['retention_rate']
        
        return metrics
    
    def _identify_high_value_clients(self, clv_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica i clienti ad alto valore"""
        if not clv_data:
            return []
        
        # Calcola CLV per ogni cliente
        clv_values = []
        for client in clv_data:
            total_pnl = client.get('total_pnl', 0)
            total_bonus = client.get('total_bonus_received', 0)
            num_accounts = client.get('num_accounts', 1)
            clv = (total_pnl + total_bonus) / num_accounts
            clv_values.append(clv)
        
        if not clv_values:
            return []
        
        avg_clv = sum(clv_values) / len(clv_values)
        
        high_value_clients = []
        for i, client in enumerate(clv_data):
            if clv_values[i] > avg_clv * 1.5:  # Cliente con CLV superiore del 50% alla media
                high_value_clients.append({
                    'name': client.get('nome_cliente', 'Unknown'),
                    'clv': clv_values[i],
                    'total_pnl': client.get('total_pnl', 0),
                    'total_bonus': client.get('total_bonus_received', 0),
                    'num_accounts': client.get('num_accounts', 0),
                    'success_rate': (client.get('successful_incroci', 0) / client.get('num_incroci', 1)) * 100 if client.get('num_incroci', 0) > 0 else 0,
                    'value_tier': 'Premium'
                })
        
        return sorted(high_value_clients, key=lambda x: x['clv'], reverse=True)
    
    def _calculate_upselling_strategies(self, clv_data: List[Dict[str, Any]], high_value_clients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calcola le strategie di upselling"""
        strategies = []
        
        for client in high_value_clients:
            # Strategie basate sul numero di account
            if client['num_accounts'] < 5:
                strategies.append({
                    'client': client['name'],
                    'strategy': 'Account Expansion',
                    'description': f"Aggiungere {5 - client['num_accounts']} nuovi account",
                    'expected_clv_increase': client['clv'] * 0.3,
                    'priority': 'High'
                })
            
            # Strategie basate sui broker
            strategies.append({
                'client': client['name'],
                'strategy': 'Broker Diversification',
                'description': 'Aggiungere nuovi broker per diversificare il rischio',
                'expected_clv_increase': client['clv'] * 0.2,
                'priority': 'Medium'
            })
            
            # Strategie basate sui volumi
            strategies.append({
                'client': client['name'],
                'strategy': 'Volume Optimization',
                'description': 'Ottimizzare i volumi per massimizzare i profitti',
                'expected_clv_increase': client['clv'] * 0.15,
                'priority': 'Medium'
            })
        
        return strategies
    
    def _prepare_marketing_ai_data(self, client_data: List[Dict[str, Any]], 
                                 client_segmentation: Dict[str, Any], 
                                 growth_opportunities: Dict[str, Any], 
                                 retention_strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara i dati per l'analisi AI di marketing"""
        # Formatta dati clienti
        formatted_client_data = f"Totale clienti: {len(client_data)}\n\n"
        
        # Top 10 clienti per performance
        top_clients = sorted(client_data, key=lambda x: x.get('net_result', 0), reverse=True)[:10]
        formatted_client_data += "Top 10 clienti per performance:\n"
        for client in top_clients:
            formatted_client_data += f"- {client.get('nome_cliente', 'N/A')}: "
            formatted_client_data += f"P&L: {client.get('net_result', 0)}, "
            formatted_client_data += f"Account: {client.get('num_accounts', 0)}, "
            formatted_client_data += f"Incroci: {client.get('num_incroci', 0)}\n"
        
        return {
            'clienti_data': formatted_client_data,
            'client_segmentation': client_segmentation,
            'growth_opportunities': growth_opportunities,
            'retention_strategies': retention_strategies,
            'total_clients': len(client_data)
        }
