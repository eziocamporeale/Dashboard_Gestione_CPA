#!/usr/bin/env python3
"""
Report Generator per Dashboard Gestione CPA
Genera report professionali sui dati CPA
Creato da Ezio Camporeale
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Classe per la generazione di report professionali CPA"""
    
    def __init__(self, supabase_manager=None):
        """Inizializza il generatore di report"""
        self.supabase_manager = supabase_manager
        self.ai_assistant = None
        
        # Inizializza AI Assistant
        try:
            from .ai_core import AIAssistant
            self.ai_assistant = AIAssistant()
            logger.info("✅ ReportGenerator inizializzato con AI Assistant")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione AI Assistant: {e}")
    
    def generate_executive_report(self, report_type: str = "monthly") -> Dict[str, Any]:
        """
        Genera un report esecutivo completo
        
        Args:
            report_type: Tipo di report (monthly, quarterly, yearly)
            
        Returns:
            Dict: Report esecutivo completo
        """
        try:
            # Recupera dati per il report
            report_data = self._get_report_data(report_type)
            
            # Calcola metriche chiave
            key_metrics = self._calculate_key_metrics(report_data)
            
            # Analizza trend e performance
            trend_analysis = self._analyze_trends(report_data)
            
            # Identifica insights e raccomandazioni
            insights = self._generate_insights(report_data, key_metrics, trend_analysis)
            
            # Prepara dati per AI
            ai_data = self._prepare_report_ai_data(report_data, key_metrics, trend_analysis, insights)
            
            # Genera report AI
            ai_report = self.ai_assistant.generate_response('report_generation', ai_data)
            
            return {
                'report_type': report_type,
                'report_data': report_data,
                'key_metrics': key_metrics,
                'trend_analysis': trend_analysis,
                'insights': insights,
                'ai_report': ai_report,
                'generation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore generazione report esecutivo: {e}")
            return {"error": f"Errore durante la generazione: {e}"}
    
    def generate_client_report(self, cliente_id: int) -> Dict[str, Any]:
        """
        Genera un report specifico per un cliente
        
        Args:
            cliente_id: ID del cliente
            
        Returns:
            Dict: Report del cliente
        """
        try:
            # Recupera dati del cliente
            client_data = self._get_client_report_data(cliente_id)
            if not client_data:
                return {"error": "Cliente non trovato"}
            
            # Calcola metriche del cliente
            client_metrics = self._calculate_client_metrics(client_data)
            
            # Analizza performance del cliente
            performance_analysis = self._analyze_client_performance(client_data)
            
            # Genera raccomandazioni specifiche
            recommendations = self._generate_client_recommendations(client_data, client_metrics, performance_analysis)
            
            return {
                'client_data': client_data,
                'client_metrics': client_metrics,
                'performance_analysis': performance_analysis,
                'recommendations': recommendations,
                'generation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore generazione report cliente {cliente_id}: {e}")
            return {"error": f"Errore durante la generazione: {e}"}
    
    def _get_report_data(self, report_type: str) -> Dict[str, Any]:
        """Recupera i dati per il report"""
        try:
            # Determina il periodo di riferimento
            if report_type == "monthly":
                days_back = 30
            elif report_type == "quarterly":
                days_back = 90
            elif report_type == "yearly":
                days_back = 365
            else:
                days_back = 30
            
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    COUNT(DISTINCT cb.id) as total_clients,
                    COUNT(ab.id) as total_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    COUNT(i.id) as total_incroci,
                    SUM(CASE WHEN i.profitto_perdita > 0 THEN i.profitto_perdita ELSE 0 END) as total_profits,
                    SUM(CASE WHEN i.profitto_perdita < 0 THEN i.profitto_perdita ELSE 0 END) as total_losses,
                    SUM(i.profitto_perdita) as net_result,
                    COUNT(CASE WHEN i.stato = 'aperto' THEN 1 END) as open_positions,
                    COUNT(DISTINCT ab.broker) as num_brokers,
                    AVG(ab.volume_posizione) as avg_volume,
                    COUNT(CASE WHEN i.data_apertura >= %s THEN 1 END) as recent_incroci,
                    SUM(CASE WHEN i.data_apertura >= %s AND i.profitto_perdita > 0 THEN i.profitto_perdita ELSE 0 END) as recent_profits,
                    SUM(CASE WHEN i.data_apertura >= %s AND i.profitto_perdita < 0 THEN i.profitto_perdita ELSE 0 END) as recent_losses
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                """
                
                result = self.supabase_manager.execute_query(query, (start_date, start_date, start_date))
                if result and len(result) > 0:
                    return result[0]
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati report: {e}")
            return {}
    
    def _get_client_report_data(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Recupera i dati per il report del cliente"""
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
                    COUNT(CASE WHEN i.stato = 'aperto' THEN 1 END) as open_positions,
                    COUNT(DISTINCT ab.broker) as num_brokers,
                    AVG(i.profitto_perdita) as avg_pnl,
                    STDDEV(i.profitto_perdita) as pnl_volatility,
                    MAX(i.data_apertura) as last_activity,
                    MIN(i.data_apertura) as first_activity,
                    SUM(ib.importo_bonus) as total_bonus_received
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                LEFT JOIN incroci_bonus ib ON i.id = ib.incrocio_id
                WHERE cb.id = %s
                GROUP BY cb.id, cb.nome_cliente, cb.email, cb.created_at
                """
                
                result = self.supabase_manager.execute_query(query, (cliente_id,))
                if result and len(result) > 0:
                    return result[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati report cliente {cliente_id}: {e}")
            return None
    
    def _calculate_key_metrics(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcola le metriche chiave per il report"""
        metrics = {
            'total_clients': report_data.get('total_clients', 0),
            'total_accounts': report_data.get('total_accounts', 0),
            'total_volume': report_data.get('total_volume', 0),
            'total_incroci': report_data.get('total_incroci', 0),
            'total_profits': report_data.get('total_profits', 0),
            'total_losses': report_data.get('total_losses', 0),
            'net_result': report_data.get('net_result', 0),
            'open_positions': report_data.get('open_positions', 0),
            'num_brokers': report_data.get('num_brokers', 0),
            'avg_volume': report_data.get('avg_volume', 0),
            'recent_incroci': report_data.get('recent_incroci', 0),
            'recent_profits': report_data.get('recent_profits', 0),
            'recent_losses': report_data.get('recent_losses', 0)
        }
        
        # Calcola metriche derivate
        if metrics['total_incroci'] > 0:
            metrics['success_rate'] = (metrics['total_profits'] / metrics['total_incroci']) * 100
            metrics['avg_profit_per_incrocio'] = metrics['total_profits'] / metrics['total_incroci']
        else:
            metrics['success_rate'] = 0
            metrics['avg_profit_per_incrocio'] = 0
        
        if metrics['total_accounts'] > 0:
            metrics['avg_volume_per_account'] = metrics['total_volume'] / metrics['total_accounts']
            metrics['avg_incroci_per_account'] = metrics['total_incroci'] / metrics['total_accounts']
        else:
            metrics['avg_volume_per_account'] = 0
            metrics['avg_incroci_per_account'] = 0
        
        if metrics['recent_incroci'] > 0:
            metrics['recent_net_result'] = metrics['recent_profits'] + metrics['recent_losses']
            metrics['recent_success_rate'] = (metrics['recent_profits'] / metrics['recent_incroci']) * 100
        else:
            metrics['recent_net_result'] = 0
            metrics['recent_success_rate'] = 0
        
        return metrics
    
    def _calculate_client_metrics(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcola le metriche specifiche del cliente"""
        metrics = {
            'num_accounts': client_data.get('num_accounts', 0),
            'total_volume': client_data.get('total_volume', 0),
            'num_incroci': client_data.get('num_incroci', 0),
            'total_profits': client_data.get('total_profits', 0),
            'total_losses': client_data.get('total_losses', 0),
            'net_result': client_data.get('net_result', 0),
            'open_positions': client_data.get('open_positions', 0),
            'num_brokers': client_data.get('num_brokers', 0),
            'avg_pnl': client_data.get('avg_pnl', 0),
            'pnl_volatility': client_data.get('pnl_volatility', 0),
            'total_bonus_received': client_data.get('total_bonus_received', 0)
        }
        
        # Calcola metriche derivate
        if metrics['num_incroci'] > 0:
            metrics['success_rate'] = (metrics['total_profits'] / metrics['num_incroci']) * 100
            metrics['avg_profit_per_incrocio'] = metrics['total_profits'] / metrics['num_incroci']
            metrics['avg_loss_per_incrocio'] = metrics['total_losses'] / metrics['num_incroci']
        else:
            metrics['success_rate'] = 0
            metrics['avg_profit_per_incrocio'] = 0
            metrics['avg_loss_per_incrocio'] = 0
        
        if metrics['num_accounts'] > 0:
            metrics['avg_volume_per_account'] = metrics['total_volume'] / metrics['num_accounts']
            metrics['avg_incroci_per_account'] = metrics['num_incroci'] / metrics['num_accounts']
        else:
            metrics['avg_volume_per_account'] = 0
            metrics['avg_incroci_per_account'] = 0
        
        # Calcola CLV (Customer Lifetime Value)
        metrics['clv'] = (metrics['net_result'] + metrics['total_bonus_received']) / max(metrics['num_accounts'], 1)
        
        # Determina tier del cliente
        if metrics['clv'] > 5000:
            metrics['client_tier'] = 'Premium'
        elif metrics['clv'] > 1000:
            metrics['client_tier'] = 'Gold'
        elif metrics['clv'] > 0:
            metrics['client_tier'] = 'Silver'
        else:
            metrics['client_tier'] = 'Bronze'
        
        return metrics
    
    def _analyze_trends(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i trend dei dati"""
        trends = {
            'volume_trend': 'stable',
            'profitability_trend': 'stable',
            'activity_trend': 'stable',
            'broker_diversification_trend': 'stable'
        }
        
        # Analizza trend dei volumi
        total_volume = report_data.get('total_volume', 0)
        avg_volume = report_data.get('avg_volume', 0)
        
        if total_volume > avg_volume * 1.2:
            trends['volume_trend'] = 'increasing'
        elif total_volume < avg_volume * 0.8:
            trends['volume_trend'] = 'decreasing'
        
        # Analizza trend di profittabilità
        net_result = report_data.get('net_result', 0)
        recent_net_result = report_data.get('recent_net_result', 0)
        
        if recent_net_result > net_result * 1.1:
            trends['profitability_trend'] = 'improving'
        elif recent_net_result < net_result * 0.9:
            trends['profitability_trend'] = 'declining'
        
        # Analizza trend di attività
        total_incroci = report_data.get('total_incroci', 0)
        recent_incroci = report_data.get('recent_incroci', 0)
        
        if recent_incroci > total_incroci * 0.3:  # Se gli incroci recenti sono più del 30% del totale
            trends['activity_trend'] = 'increasing'
        elif recent_incroci < total_incroci * 0.1:  # Se gli incroci recenti sono meno del 10% del totale
            trends['activity_trend'] = 'decreasing'
        
        # Analizza trend di diversificazione broker
        num_brokers = report_data.get('num_brokers', 0)
        total_accounts = report_data.get('total_accounts', 1)
        broker_diversification = num_brokers / total_accounts if total_accounts > 0 else 0
        
        if broker_diversification > 0.5:
            trends['broker_diversification_trend'] = 'good'
        elif broker_diversification < 0.2:
            trends['broker_diversification_trend'] = 'poor'
        
        return trends
    
    def _analyze_client_performance(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza la performance del cliente"""
        performance = {
            'overall_performance': 'average',
            'risk_level': 'medium',
            'growth_potential': 'medium',
            'retention_probability': 'medium'
        }
        
        net_result = client_data.get('net_result', 0)
        num_incroci = client_data.get('num_incroci', 1)
        avg_pnl = net_result / num_incroci if num_incroci > 0 else 0
        pnl_volatility = client_data.get('pnl_volatility', 0)
        
        # Valuta performance generale
        if avg_pnl > 500:
            performance['overall_performance'] = 'excellent'
        elif avg_pnl > 100:
            performance['overall_performance'] = 'good'
        elif avg_pnl > 0:
            performance['overall_performance'] = 'average'
        else:
            performance['overall_performance'] = 'poor'
        
        # Valuta livello di rischio
        if pnl_volatility > 1000:
            performance['risk_level'] = 'high'
        elif pnl_volatility > 500:
            performance['risk_level'] = 'medium'
        else:
            performance['risk_level'] = 'low'
        
        # Valuta potenziale di crescita
        num_accounts = client_data.get('num_accounts', 0)
        num_brokers = client_data.get('num_brokers', 0)
        
        if num_accounts < 3 and avg_pnl > 0:
            performance['growth_potential'] = 'high'
        elif num_brokers == 1 and num_accounts > 2:
            performance['growth_potential'] = 'high'
        elif avg_pnl > 200:
            performance['growth_potential'] = 'medium'
        else:
            performance['growth_potential'] = 'low'
        
        # Valuta probabilità di retention
        last_activity = client_data.get('last_activity')
        if last_activity:
            try:
                last_activity_date = datetime.strptime(last_activity, '%Y-%m-%d')
                days_since_activity = (datetime.now() - last_activity_date).days
                
                if days_since_activity < 7:
                    performance['retention_probability'] = 'high'
                elif days_since_activity < 30:
                    performance['retention_probability'] = 'medium'
                else:
                    performance['retention_probability'] = 'low'
            except:
                pass
        
        return performance
    
    def _generate_insights(self, report_data: Dict[str, Any], 
                          key_metrics: Dict[str, Any], 
                          trend_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera insights e raccomandazioni"""
        insights = []
        
        # Insight su volumi
        if trend_analysis['volume_trend'] == 'increasing':
            insights.append({
                'category': 'Volume Growth',
                'insight': 'I volumi stanno crescendo positivamente',
                'recommendation': 'Mantenere la strategia attuale e considerare l\'espansione',
                'priority': 'Medium'
            })
        elif trend_analysis['volume_trend'] == 'decreasing':
            insights.append({
                'category': 'Volume Decline',
                'insight': 'I volumi stanno diminuendo',
                'recommendation': 'Analizzare le cause e implementare strategie di recupero',
                'priority': 'High'
            })
        
        # Insight su profittabilità
        if trend_analysis['profitability_trend'] == 'improving':
            insights.append({
                'category': 'Profitability',
                'insight': 'La profittabilità sta migliorando',
                'recommendation': 'Continuare con le strategie attuali e ottimizzare ulteriormente',
                'priority': 'Low'
            })
        elif trend_analysis['profitability_trend'] == 'declining':
            insights.append({
                'category': 'Profitability',
                'insight': 'La profittabilità sta diminuendo',
                'recommendation': 'Rivedere le strategie di risk management e ottimizzazione',
                'priority': 'High'
            })
        
        # Insight su diversificazione broker
        if trend_analysis['broker_diversification_trend'] == 'poor':
            insights.append({
                'category': 'Risk Management',
                'insight': 'Bassa diversificazione dei broker',
                'recommendation': 'Aggiungere nuovi broker per ridurre la concentrazione del rischio',
                'priority': 'High'
            })
        
        # Insight su success rate
        if key_metrics['success_rate'] < 60:
            insights.append({
                'category': 'Performance',
                'insight': f'Success rate basso ({key_metrics["success_rate"]:.1f}%)',
                'recommendation': 'Implementare training e migliorare le strategie di selezione',
                'priority': 'High'
            })
        elif key_metrics['success_rate'] > 80:
            insights.append({
                'category': 'Performance',
                'insight': f'Success rate eccellente ({key_metrics["success_rate"]:.1f}%)',
                'recommendation': 'Mantenere gli standard elevati e condividere le best practices',
                'priority': 'Low'
            })
        
        return insights
    
    def _generate_client_recommendations(self, client_data: Dict[str, Any], 
                                       client_metrics: Dict[str, Any], 
                                       performance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera raccomandazioni specifiche per il cliente"""
        recommendations = []
        
        # Raccomandazioni basate sulla performance
        if performance_analysis['overall_performance'] == 'poor':
            recommendations.append({
                'category': 'Performance Improvement',
                'recommendation': 'Implementare strategie di risk management più conservative',
                'action': 'Ridurre i volumi e implementare stop-loss più stretti',
                'expected_impact': 'Riduzione perdite del 30%',
                'priority': 'High'
            })
        
        # Raccomandazioni basate sul potenziale di crescita
        if performance_analysis['growth_potential'] == 'high':
            recommendations.append({
                'category': 'Growth Opportunity',
                'recommendation': 'Espandere il numero di account e broker',
                'action': 'Aggiungere 2-3 nuovi account con broker diversi',
                'expected_impact': 'Aumento CLV del 40%',
                'priority': 'Medium'
            })
        
        # Raccomandazioni basate sul rischio
        if performance_analysis['risk_level'] == 'high':
            recommendations.append({
                'category': 'Risk Management',
                'recommendation': 'Ridurre la volatilità delle performance',
                'action': 'Implementare strategie più conservative e diversificare',
                'expected_impact': 'Riduzione volatilità del 25%',
                'priority': 'High'
            })
        
        # Raccomandazioni basate sulla retention
        if performance_analysis['retention_probability'] == 'low':
            recommendations.append({
                'category': 'Retention',
                'recommendation': 'Implementare strategia di re-engagement',
                'action': 'Campagna di comunicazione personalizzata e offerte speciali',
                'expected_impact': 'Ripresa attività del 50%',
                'priority': 'High'
            })
        
        # Raccomandazioni basate sul tier del cliente
        client_tier = client_metrics.get('client_tier', 'Bronze')
        if client_tier == 'Premium':
            recommendations.append({
                'category': 'Premium Service',
                'recommendation': 'Offrire servizi premium esclusivi',
                'action': 'Commissioni ridotte, supporto prioritario, bonus esclusivi',
                'expected_impact': 'Aumento loyalty del 20%',
                'priority': 'Low'
            })
        
        return recommendations
    
    def _prepare_report_ai_data(self, report_data: Dict[str, Any], 
                               key_metrics: Dict[str, Any], 
                               trend_analysis: Dict[str, Any], 
                               insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara i dati per l'analisi AI del report"""
        # Formatta dati del report
        formatted_report_data = f"""
Report CPA - {datetime.now().strftime('%Y-%m-%d')}:

METRICHE CHIAVE:
- Totale Clienti: {key_metrics['total_clients']}
- Totale Account: {key_metrics['total_accounts']}
- Volume Totale: {key_metrics['total_volume']:,.2f}
- Incroci Totali: {key_metrics['total_incroci']}
- Risultato Netto: {key_metrics['net_result']:,.2f}
- Success Rate: {key_metrics['success_rate']:.1f}%
- Posizioni Aperte: {key_metrics['open_positions']}
- Broker Attivi: {key_metrics['num_brokers']}

TREND ANALYSIS:
- Trend Volumi: {trend_analysis['volume_trend']}
- Trend Profittabilità: {trend_analysis['profitability_trend']}
- Trend Attività: {trend_analysis['activity_trend']}
- Diversificazione Broker: {trend_analysis['broker_diversification_trend']}

INSIGHTS PRINCIPALI:
"""
        
        for insight in insights[:5]:  # Top 5 insights
            formatted_report_data += f"- {insight['category']}: {insight['insight']}\n"
        
        return {
            'report_data': formatted_report_data,
            'key_metrics': key_metrics,
            'trend_analysis': trend_analysis,
            'insights': insights
        }
