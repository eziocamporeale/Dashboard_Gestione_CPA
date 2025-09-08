#!/usr/bin/env python3
"""
Broker Optimizer per Dashboard Gestione CPA
Analizza e ottimizza la distribuzione dei broker
Creato da Ezio Camporeale
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrokerOptimizer:
    """Classe per l'ottimizzazione dei broker CPA"""
    
    def __init__(self, supabase_manager=None):
        """Inizializza l'ottimizzatore broker"""
        self.supabase_manager = supabase_manager
        self.ai_assistant = None
        
        # Inizializza AI Assistant
        try:
            from .ai_core import AIAssistant
            self.ai_assistant = AIAssistant()
            logger.info("✅ BrokerOptimizer inizializzato con AI Assistant")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione AI Assistant: {e}")
    
    def optimize_broker_distribution(self) -> Dict[str, Any]:
        """
        Ottimizza la distribuzione dei broker per massimizzare i profitti
        
        Returns:
            Dict: Raccomandazioni di ottimizzazione
        """
        try:
            # Recupera dati broker
            broker_data = self._get_broker_performance_data()
            
            # Analizza performance per broker
            performance_analysis = self._analyze_broker_performance(broker_data)
            
            # Calcola raccomandazioni di ottimizzazione
            optimization_recommendations = self._calculate_optimization_recommendations(performance_analysis)
            
            # Prepara dati per AI
            ai_data = self._prepare_broker_ai_data(broker_data, performance_analysis, optimization_recommendations)
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('broker_optimization', ai_data)
            
            return {
                'broker_data': broker_data,
                'performance_analysis': performance_analysis,
                'optimization_recommendations': optimization_recommendations,
                'ai_analysis': ai_analysis,
                'optimization_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore ottimizzazione broker: {e}")
            return {"error": f"Errore durante l'ottimizzazione: {e}"}
    
    def analyze_broker_risks(self) -> Dict[str, Any]:
        """
        Analizza i rischi associati ai broker
        
        Returns:
            Dict: Analisi dei rischi per broker
        """
        try:
            # Recupera dati broker con focus sui rischi
            risk_data = self._get_broker_risk_data()
            
            # Analizza concentrazione del rischio
            risk_concentration = self._analyze_risk_concentration(risk_data)
            
            # Identifica broker ad alto rischio
            high_risk_brokers = self._identify_high_risk_brokers(risk_data)
            
            # Calcola raccomandazioni di mitigazione
            mitigation_recommendations = self._calculate_mitigation_recommendations(risk_concentration, high_risk_brokers)
            
            return {
                'risk_data': risk_data,
                'risk_concentration': risk_concentration,
                'high_risk_brokers': high_risk_brokers,
                'mitigation_recommendations': mitigation_recommendations,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi rischi broker: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def _get_broker_performance_data(self) -> List[Dict[str, Any]]:
        """Recupera i dati di performance per broker"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    ab.broker,
                    ab.piattaforma,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    AVG(ab.volume_posizione) as avg_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(CASE WHEN i.profitto_perdita > 0 THEN i.profitto_perdita ELSE 0 END) as total_profits,
                    SUM(CASE WHEN i.profitto_perdita < 0 THEN i.profitto_perdita ELSE 0 END) as total_losses,
                    SUM(i.profitto_perdita) as net_result,
                    COUNT(CASE WHEN i.profitto_perdita > 0 THEN 1 END) as successful_incroci,
                    COUNT(CASE WHEN i.profitto_perdita < 0 THEN 1 END) as failed_incroci,
                    MAX(i.data_apertura) as last_incrocio_date,
                    MIN(i.data_apertura) as first_incrocio_date
                FROM account_broker ab
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                GROUP BY ab.broker, ab.piattaforma
                ORDER BY net_result DESC
                """
                
                result = self.supabase_manager.execute_query(query)
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati performance broker: {e}")
            return []
    
    def _get_broker_risk_data(self) -> List[Dict[str, Any]]:
        """Recupera i dati di rischio per broker"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    ab.broker,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(i.profitto_perdita) as net_result,
                    COUNT(CASE WHEN i.stato = 'aperto' THEN 1 END) as open_positions,
                    COUNT(CASE WHEN i.profitto_perdita < -1000 THEN 1 END) as high_loss_incroci,
                    AVG(i.profitto_perdita) as avg_pnl,
                    STDDEV(i.profitto_perdita) as pnl_volatility,
                    COUNT(DISTINCT cb.id) as unique_clients
                FROM account_broker ab
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                LEFT JOIN clienti_base cb ON ab.cliente_base_id = cb.id
                GROUP BY ab.broker
                ORDER BY total_volume DESC
                """
                
                result = self.supabase_manager.execute_query(query)
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati rischio broker: {e}")
            return []
    
    def _analyze_broker_performance(self, broker_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza le performance dei broker"""
        if not broker_data:
            return {}
        
        analysis = {
            'total_brokers': len(broker_data),
            'total_accounts': sum(broker.get('num_accounts', 0) for broker in broker_data),
            'total_volume': sum(broker.get('total_volume', 0) for broker in broker_data),
            'total_net_result': sum(broker.get('net_result', 0) for broker in broker_data),
            'broker_rankings': [],
            'performance_metrics': {}
        }
        
        # Calcola metriche per broker
        for broker in broker_data:
            broker_name = broker.get('broker', 'Unknown')
            
            # Calcola success rate
            total_incroci = broker.get('num_incroci', 0)
            successful_incroci = broker.get('successful_incroci', 0)
            success_rate = (successful_incroci / total_incroci * 100) if total_incroci > 0 else 0
            
            # Calcola ROI
            total_volume = broker.get('total_volume', 0)
            net_result = broker.get('net_result', 0)
            roi = (net_result / total_volume * 100) if total_volume > 0 else 0
            
            # Calcola efficienza
            avg_volume = broker.get('avg_volume', 0)
            efficiency = net_result / avg_volume if avg_volume > 0 else 0
            
            broker_metrics = {
                'broker': broker_name,
                'num_accounts': broker.get('num_accounts', 0),
                'total_volume': total_volume,
                'num_incroci': total_incroci,
                'success_rate': success_rate,
                'net_result': net_result,
                'roi': roi,
                'efficiency': efficiency,
                'avg_volume': avg_volume
            }
            
            analysis['broker_rankings'].append(broker_metrics)
        
        # Ordina per performance
        analysis['broker_rankings'].sort(key=lambda x: x['net_result'], reverse=True)
        
        # Calcola metriche aggregate
        if analysis['broker_rankings']:
            best_broker = analysis['broker_rankings'][0]
            worst_broker = analysis['broker_rankings'][-1]
            
            analysis['performance_metrics'] = {
                'best_broker': best_broker['broker'],
                'best_roi': best_broker['roi'],
                'worst_broker': worst_broker['broker'],
                'worst_roi': worst_broker['roi'],
                'avg_roi': sum(b['roi'] for b in analysis['broker_rankings']) / len(analysis['broker_rankings']),
                'avg_success_rate': sum(b['success_rate'] for b in analysis['broker_rankings']) / len(analysis['broker_rankings'])
            }
        
        return analysis
    
    def _analyze_risk_concentration(self, risk_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza la concentrazione del rischio"""
        if not risk_data:
            return {}
        
        total_volume = sum(broker.get('total_volume', 0) for broker in risk_data)
        total_accounts = sum(broker.get('num_accounts', 0) for broker in risk_data)
        
        concentration_analysis = {
            'total_volume': total_volume,
            'total_accounts': total_accounts,
            'volume_concentration': {},
            'account_concentration': {},
            'risk_level': 'Medium'
        }
        
        # Analizza concentrazione per volume
        for broker in risk_data:
            broker_name = broker.get('broker', 'Unknown')
            volume_share = (broker.get('total_volume', 0) / total_volume * 100) if total_volume > 0 else 0
            account_share = (broker.get('num_accounts', 0) / total_accounts * 100) if total_accounts > 0 else 0
            
            concentration_analysis['volume_concentration'][broker_name] = volume_share
            concentration_analysis['account_concentration'][broker_name] = account_share
        
        # Determina livello di rischio
        max_volume_share = max(concentration_analysis['volume_concentration'].values()) if concentration_analysis['volume_concentration'] else 0
        max_account_share = max(concentration_analysis['account_concentration'].values()) if concentration_analysis['account_concentration'] else 0
        
        if max_volume_share > 50 or max_account_share > 50:
            concentration_analysis['risk_level'] = 'High'
        elif max_volume_share > 30 or max_account_share > 30:
            concentration_analysis['risk_level'] = 'Medium'
        else:
            concentration_analysis['risk_level'] = 'Low'
        
        return concentration_analysis
    
    def _identify_high_risk_brokers(self, risk_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica i broker ad alto rischio"""
        high_risk_brokers = []
        
        for broker in risk_data:
            broker_name = broker.get('broker', 'Unknown')
            risk_factors = []
            risk_score = 0
            
            # Fattori di rischio
            if broker.get('pnl_volatility', 0) > 1000:
                risk_factors.append("Alta volatilità P&L")
                risk_score += 2
            
            if broker.get('high_loss_incroci', 0) > 5:
                risk_factors.append("Molte perdite elevate")
                risk_score += 2
            
            if broker.get('open_positions', 0) > 10:
                risk_factors.append("Troppe posizioni aperte")
                risk_score += 1
            
            if broker.get('avg_pnl', 0) < -500:
                risk_factors.append("Performance negativa media")
                risk_score += 2
            
            if broker.get('unique_clients', 0) < 3:
                risk_factors.append("Pochi clienti unici")
                risk_score += 1
            
            if risk_score >= 3:
                high_risk_brokers.append({
                    'broker': broker_name,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'recommendations': self._get_broker_risk_recommendations(risk_factors)
                })
        
        return high_risk_brokers
    
    def _get_broker_risk_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Genera raccomandazioni per broker ad alto rischio"""
        recommendations = []
        
        if "Alta volatilità P&L" in risk_factors:
            recommendations.append("Ridurre i volumi per questo broker")
        
        if "Molte perdite elevate" in risk_factors:
            recommendations.append("Implementare stop-loss più stretti")
        
        if "Troppe posizioni aperte" in risk_factors:
            recommendations.append("Chiudere alcune posizioni aperte")
        
        if "Performance negativa media" in risk_factors:
            recommendations.append("Considerare la sospensione temporanea")
        
        if "Pochi clienti unici" in risk_factors:
            recommendations.append("Diversificare la base clienti")
        
        return recommendations
    
    def _calculate_optimization_recommendations(self, performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcola le raccomandazioni di ottimizzazione"""
        recommendations = {
            'volume_reallocation': {},
            'broker_priorities': [],
            'risk_mitigation': [],
            'growth_opportunities': []
        }
        
        if not performance_analysis.get('broker_rankings'):
            return recommendations
        
        broker_rankings = performance_analysis['broker_rankings']
        
        # Raccomandazioni per riallocazione volumi
        best_brokers = [b for b in broker_rankings if b['roi'] > performance_analysis['performance_metrics']['avg_roi']]
        worst_brokers = [b for b in broker_rankings if b['roi'] < performance_analysis['performance_metrics']['avg_roi']]
        
        for best_broker in best_brokers[:3]:  # Top 3 broker
            recommendations['volume_reallocation'][best_broker['broker']] = {
                'action': 'increase',
                'reason': f"ROI del {best_broker['roi']:.2f}%",
                'suggested_increase': 20
            }
        
        for worst_broker in worst_brokers[:3]:  # Bottom 3 broker
            recommendations['volume_reallocation'][worst_broker['broker']] = {
                'action': 'decrease',
                'reason': f"ROI del {worst_broker['roi']:.2f}%",
                'suggested_decrease': 15
            }
        
        # Priorità broker
        recommendations['broker_priorities'] = [
            {
                'broker': b['broker'],
                'priority': 'High' if b['roi'] > 10 else 'Medium' if b['roi'] > 0 else 'Low',
                'reason': f"ROI: {b['roi']:.2f}%, Success Rate: {b['success_rate']:.1f}%"
            }
            for b in broker_rankings[:5]
        ]
        
        # Mitigazione rischi
        if performance_analysis['performance_metrics']['avg_success_rate'] < 60:
            recommendations['risk_mitigation'].append("Success rate generale bassa - implementare training")
        
        if len(broker_rankings) < 3:
            recommendations['risk_mitigation'].append("Pochi broker attivi - diversificare")
        
        # Opportunità di crescita
        high_performance_brokers = [b for b in broker_rankings if b['roi'] > 15]
        if high_performance_brokers:
            recommendations['growth_opportunities'].append(
                f"Espandere con {high_performance_brokers[0]['broker']} (ROI: {high_performance_brokers[0]['roi']:.2f}%)"
            )
        
        return recommendations
    
    def _calculate_mitigation_recommendations(self, risk_concentration: Dict[str, Any], 
                                             high_risk_brokers: List[Dict[str, Any]]) -> List[str]:
        """Calcola le raccomandazioni di mitigazione del rischio"""
        recommendations = []
        
        # Raccomandazioni basate sulla concentrazione
        if risk_concentration.get('risk_level') == 'High':
            recommendations.append("Ridurre la concentrazione su broker singoli")
            recommendations.append("Diversificare i volumi tra più broker")
        
        # Raccomandazioni per broker ad alto rischio
        for broker in high_risk_brokers:
            recommendations.extend(broker['recommendations'])
        
        # Raccomandazioni generali
        if len(high_risk_brokers) > 2:
            recommendations.append("Implementare monitoraggio rischi più frequente")
            recommendations.append("Stabilire limiti di esposizione per broker")
        
        return list(set(recommendations))  # Rimuovi duplicati
    
    def _prepare_broker_ai_data(self, broker_data: List[Dict[str, Any]], 
                               performance_analysis: Dict[str, Any], 
                               optimization_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara i dati per l'analisi AI dei broker"""
        # Formatta dati broker
        formatted_broker_data = ""
        for broker in broker_data[:10]:  # Top 10 broker
            formatted_broker_data += f"- {broker.get('broker', 'N/A')}: "
            formatted_broker_data += f"{broker.get('num_accounts', 0)} account, "
            formatted_broker_data += f"Volume: {broker.get('total_volume', 0)}, "
            formatted_broker_data += f"P&L: {broker.get('net_result', 0)}, "
            formatted_broker_data += f"Success Rate: {(broker.get('successful_incroci', 0) / broker.get('num_incroci', 1) * 100):.1f}%\n"
        
        return {
            'broker_data': formatted_broker_data,
            'performance_analysis': performance_analysis,
            'optimization_recommendations': optimization_recommendations,
            'total_brokers': len(broker_data)
        }
