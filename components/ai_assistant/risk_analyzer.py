#!/usr/bin/env python3
"""
Risk Analyzer per Dashboard Gestione CPA
Analizza i rischi del portafoglio clienti e fornisce raccomandazioni
Creato da Ezio Camporeale
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """Classe per l'analisi dei rischi CPA"""
    
    def __init__(self, supabase_manager=None):
        """Inizializza l'analizzatore di rischio"""
        self.supabase_manager = supabase_manager
        self.ai_assistant = None
        
        # Inizializza AI Assistant
        try:
            from .ai_core import AIAssistant
            self.ai_assistant = AIAssistant()
            logger.info("✅ RiskAnalyzer inizializzato con AI Assistant")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione AI Assistant: {e}")
    
    def analyze_portfolio_risks(self) -> Dict[str, Any]:
        """
        Analizza i rischi del portafoglio completo
        
        Returns:
            Dict: Analisi completa dei rischi
        """
        try:
            # Recupera dati del portafoglio
            portfolio_data = self._get_portfolio_data()
            
            # Analizza concentrazione dei rischi
            concentration_risks = self._analyze_concentration_risks(portfolio_data)
            
            # Analizza rischi operativi
            operational_risks = self._analyze_operational_risks(portfolio_data)
            
            # Analizza rischi di mercato
            market_risks = self._analyze_market_risks(portfolio_data)
            
            # Calcola score di rischio complessivo
            overall_risk_score = self._calculate_overall_risk_score(concentration_risks, operational_risks, market_risks)
            
            # Genera raccomandazioni di mitigazione
            mitigation_recommendations = self._generate_mitigation_recommendations(concentration_risks, operational_risks, market_risks)
            
            # Prepara dati per AI
            ai_data = self._prepare_risk_ai_data(portfolio_data, concentration_risks, operational_risks, market_risks, overall_risk_score)
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('risk_analysis', ai_data)
            
            return {
                'portfolio_data': portfolio_data,
                'concentration_risks': concentration_risks,
                'operational_risks': operational_risks,
                'market_risks': market_risks,
                'overall_risk_score': overall_risk_score,
                'mitigation_recommendations': mitigation_recommendations,
                'ai_analysis': ai_analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi rischi portafoglio: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def analyze_client_risks(self, cliente_id: int) -> Dict[str, Any]:
        """
        Analizza i rischi specifici di un cliente
        
        Args:
            cliente_id: ID del cliente da analizzare
            
        Returns:
            Dict: Analisi dei rischi del cliente
        """
        try:
            # Recupera dati del cliente
            client_data = self._get_client_risk_data(cliente_id)
            if not client_data:
                return {"error": "Cliente non trovato"}
            
            # Analizza rischi specifici del cliente
            client_risks = self._analyze_client_specific_risks(client_data)
            
            # Calcola score di rischio del cliente
            client_risk_score = self._calculate_client_risk_score(client_risks)
            
            # Genera raccomandazioni specifiche
            client_recommendations = self._generate_client_recommendations(client_risks, client_risk_score)
            
            return {
                'client_data': client_data,
                'client_risks': client_risks,
                'client_risk_score': client_risk_score,
                'recommendations': client_recommendations,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi rischi cliente {cliente_id}: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def _get_portfolio_data(self) -> Dict[str, Any]:
        """Recupera i dati del portafoglio completo"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                # Query per dati aggregati del portafoglio
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
                    COUNT(CASE WHEN i.profitto_perdita < -1000 THEN 1 END) as high_loss_positions,
                    COUNT(DISTINCT ab.broker) as num_brokers,
                    AVG(ab.volume_posizione) as avg_volume,
                    STDDEV(ab.volume_posizione) as volume_volatility
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                """
                
                result = self.supabase_manager.execute_query(query)
                if result and len(result) > 0:
                    return result[0]
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati portafoglio: {e}")
            return {}
    
    def _get_client_risk_data(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Recupera i dati di rischio per un cliente specifico"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                query = """
                SELECT 
                    cb.id,
                    cb.nome_cliente,
                    cb.email,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(CASE WHEN i.profitto_perdita > 0 THEN i.profitto_perdita ELSE 0 END) as total_profits,
                    SUM(CASE WHEN i.profitto_perdita < 0 THEN i.profitto_perdita ELSE 0 END) as total_losses,
                    SUM(i.profitto_perdita) as net_result,
                    COUNT(CASE WHEN i.stato = 'aperto' THEN 1 END) as open_positions,
                    COUNT(CASE WHEN i.profitto_perdita < -1000 THEN 1 END) as high_loss_positions,
                    COUNT(DISTINCT ab.broker) as num_brokers,
                    AVG(i.profitto_perdita) as avg_pnl,
                    STDDEV(i.profitto_perdita) as pnl_volatility,
                    MAX(i.data_apertura) as last_activity,
                    MIN(i.data_apertura) as first_activity
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                WHERE cb.id = %s
                GROUP BY cb.id, cb.nome_cliente, cb.email
                """
                
                result = self.supabase_manager.execute_query(query, (cliente_id,))
                if result and len(result) > 0:
                    return result[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati rischio cliente {cliente_id}: {e}")
            return None
    
    def _analyze_concentration_risks(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i rischi di concentrazione"""
        risks = {
            'broker_concentration': {},
            'volume_concentration': {},
            'client_concentration': {},
            'risk_level': 'Low'
        }
        
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
                # Analizza concentrazione per broker
                broker_query = """
                SELECT 
                    ab.broker,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    COUNT(i.id) as num_incroci,
                    SUM(i.profitto_perdita) as net_result
                FROM account_broker ab
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                GROUP BY ab.broker
                ORDER BY total_volume DESC
                """
                
                broker_data = self.supabase_manager.execute_query(broker_query)
                if broker_data:
                    total_volume = sum(broker.get('total_volume', 0) for broker in broker_data)
                    total_accounts = sum(broker.get('num_accounts', 0) for broker in broker_data)
                    
                    for broker in broker_data:
                        broker_name = broker.get('broker', 'Unknown')
                        volume_share = (broker.get('total_volume', 0) / total_volume * 100) if total_volume > 0 else 0
                        account_share = (broker.get('num_accounts', 0) / total_accounts * 100) if total_accounts > 0 else 0
                        
                        risks['broker_concentration'][broker_name] = {
                            'volume_share': volume_share,
                            'account_share': account_share,
                            'risk_level': 'High' if volume_share > 40 else 'Medium' if volume_share > 20 else 'Low'
                        }
                
                # Analizza concentrazione per clienti
                client_query = """
                SELECT 
                    cb.nome_cliente,
                    COUNT(ab.id) as num_accounts,
                    SUM(ab.volume_posizione) as total_volume,
                    SUM(i.profitto_perdita) as net_result
                FROM clienti_base cb
                LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
                LEFT JOIN incroci_account ia ON ab.id = ia.account_id
                LEFT JOIN incroci i ON ia.incrocio_id = i.id
                GROUP BY cb.id, cb.nome_cliente
                ORDER BY total_volume DESC
                LIMIT 10
                """
                
                client_data = self.supabase_manager.execute_query(client_query)
                if client_data:
                    total_volume = sum(client.get('total_volume', 0) for client in client_data)
                    
                    for client in client_data:
                        client_name = client.get('nome_cliente', 'Unknown')
                        volume_share = (client.get('total_volume', 0) / total_volume * 100) if total_volume > 0 else 0
                        
                        risks['client_concentration'][client_name] = {
                            'volume_share': volume_share,
                            'num_accounts': client.get('num_accounts', 0),
                            'net_result': client.get('net_result', 0),
                            'risk_level': 'High' if volume_share > 20 else 'Medium' if volume_share > 10 else 'Low'
                        }
                
                # Determina livello di rischio generale
                max_broker_concentration = max(
                    (broker['volume_share'] for broker in risks['broker_concentration'].values()), 
                    default=0
                )
                max_client_concentration = max(
                    (client['volume_share'] for client in risks['client_concentration'].values()), 
                    default=0
                )
                
                if max_broker_concentration > 50 or max_client_concentration > 30:
                    risks['risk_level'] = 'High'
                elif max_broker_concentration > 30 or max_client_concentration > 15:
                    risks['risk_level'] = 'Medium'
                else:
                    risks['risk_level'] = 'Low'
        
        except Exception as e:
            logger.error(f"❌ Errore analisi concentrazione rischi: {e}")
        
        return risks
    
    def _analyze_operational_risks(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i rischi operativi"""
        risks = {
            'open_positions_risk': {},
            'high_loss_positions': {},
            'volatility_risk': {},
            'risk_level': 'Low'
        }
        
        # Analisi posizioni aperte
        open_positions = portfolio_data.get('open_positions', 0)
        total_incroci = portfolio_data.get('total_incroci', 1)
        open_positions_ratio = open_positions / total_incroci if total_incroci > 0 else 0
        
        risks['open_positions_risk'] = {
            'count': open_positions,
            'ratio': open_positions_ratio,
            'risk_level': 'High' if open_positions_ratio > 0.3 else 'Medium' if open_positions_ratio > 0.15 else 'Low'
        }
        
        # Analisi perdite elevate
        high_loss_positions = portfolio_data.get('high_loss_positions', 0)
        high_loss_ratio = high_loss_positions / total_incroci if total_incroci > 0 else 0
        
        risks['high_loss_positions'] = {
            'count': high_loss_positions,
            'ratio': high_loss_ratio,
            'risk_level': 'High' if high_loss_ratio > 0.1 else 'Medium' if high_loss_ratio > 0.05 else 'Low'
        }
        
        # Analisi volatilità
        volume_volatility = portfolio_data.get('volume_volatility', 0)
        avg_volume = portfolio_data.get('avg_volume', 1)
        volatility_ratio = volume_volatility / avg_volume if avg_volume > 0 else 0
        
        risks['volatility_risk'] = {
            'volatility': volume_volatility,
            'volatility_ratio': volatility_ratio,
            'risk_level': 'High' if volatility_ratio > 0.5 else 'Medium' if volatility_ratio > 0.3 else 'Low'
        }
        
        # Determina livello di rischio operativo generale
        risk_scores = [
            risks['open_positions_risk']['risk_level'],
            risks['high_loss_positions']['risk_level'],
            risks['volatility_risk']['risk_level']
        ]
        
        if 'High' in risk_scores:
            risks['risk_level'] = 'High'
        elif 'Medium' in risk_scores:
            risks['risk_level'] = 'Medium'
        else:
            risks['risk_level'] = 'Low'
        
        return risks
    
    def _analyze_market_risks(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i rischi di mercato"""
        risks = {
            'broker_diversification': {},
            'volume_distribution': {},
            'performance_consistency': {},
            'risk_level': 'Low'
        }
        
        # Analisi diversificazione broker
        num_brokers = portfolio_data.get('num_brokers', 0)
        total_accounts = portfolio_data.get('total_accounts', 1)
        broker_diversification = num_brokers / total_accounts if total_accounts > 0 else 0
        
        risks['broker_diversification'] = {
            'num_brokers': num_brokers,
            'diversification_ratio': broker_diversification,
            'risk_level': 'High' if broker_diversification < 0.2 else 'Medium' if broker_diversification < 0.4 else 'Low'
        }
        
        # Analisi distribuzione volumi
        total_volume = portfolio_data.get('total_volume', 0)
        avg_volume = portfolio_data.get('avg_volume', 0)
        volume_distribution_risk = 'Low'
        
        if total_volume > 0 and avg_volume > 0:
            # Calcola coefficiente di variazione
            volume_volatility = portfolio_data.get('volume_volatility', 0)
            cv = volume_volatility / avg_volume if avg_volume > 0 else 0
            
            if cv > 0.8:
                volume_distribution_risk = 'High'
            elif cv > 0.5:
                volume_distribution_risk = 'Medium'
        
        risks['volume_distribution'] = {
            'total_volume': total_volume,
            'avg_volume': avg_volume,
            'volatility': portfolio_data.get('volume_volatility', 0),
            'risk_level': volume_distribution_risk
        }
        
        # Analisi consistenza performance
        total_profits = portfolio_data.get('total_profits', 0)
        total_losses = portfolio_data.get('total_losses', 0)
        net_result = portfolio_data.get('net_result', 0)
        
        if total_profits > 0 and total_losses < 0:
            profit_loss_ratio = abs(total_profits / total_losses) if total_losses != 0 else float('inf')
            consistency_risk = 'High' if profit_loss_ratio < 1.5 else 'Medium' if profit_loss_ratio < 2.0 else 'Low'
        else:
            consistency_risk = 'High' if net_result < 0 else 'Low'
        
        risks['performance_consistency'] = {
            'total_profits': total_profits,
            'total_losses': total_losses,
            'net_result': net_result,
            'profit_loss_ratio': abs(total_profits / total_losses) if total_losses != 0 else 0,
            'risk_level': consistency_risk
        }
        
        # Determina livello di rischio di mercato generale
        risk_scores = [
            risks['broker_diversification']['risk_level'],
            risks['volume_distribution']['risk_level'],
            risks['performance_consistency']['risk_level']
        ]
        
        if 'High' in risk_scores:
            risks['risk_level'] = 'High'
        elif 'Medium' in risk_scores:
            risks['risk_level'] = 'Medium'
        else:
            risks['risk_level'] = 'Low'
        
        return risks
    
    def _calculate_overall_risk_score(self, concentration_risks: Dict[str, Any], 
                                    operational_risks: Dict[str, Any], 
                                    market_risks: Dict[str, Any]) -> Dict[str, Any]:
        """Calcola il punteggio di rischio complessivo"""
        # Mappa livelli di rischio a punteggi numerici
        risk_levels = {'Low': 1, 'Medium': 2, 'High': 3}
        
        concentration_score = risk_levels.get(concentration_risks.get('risk_level', 'Low'), 1)
        operational_score = risk_levels.get(operational_risks.get('risk_level', 'Low'), 1)
        market_score = risk_levels.get(market_risks.get('risk_level', 'Low'), 1)
        
        # Calcola punteggio medio ponderato
        overall_score = (concentration_score * 0.4 + operational_score * 0.4 + market_score * 0.2)
        
        # Determina livello di rischio complessivo
        if overall_score >= 2.5:
            overall_level = 'High'
        elif overall_score >= 1.5:
            overall_level = 'Medium'
        else:
            overall_level = 'Low'
        
        return {
            'overall_score': overall_score,
            'overall_level': overall_level,
            'concentration_score': concentration_score,
            'operational_score': operational_score,
            'market_score': market_score,
            'risk_factors': self._identify_key_risk_factors(concentration_risks, operational_risks, market_risks)
        }
    
    def _identify_key_risk_factors(self, concentration_risks: Dict[str, Any], 
                                 operational_risks: Dict[str, Any], 
                                 market_risks: Dict[str, Any]) -> List[str]:
        """Identifica i fattori di rischio chiave"""
        risk_factors = []
        
        # Fattori di concentrazione
        if concentration_risks.get('risk_level') == 'High':
            risk_factors.append("Alta concentrazione su broker/clienti singoli")
        
        # Fattori operativi
        if operational_risks.get('open_positions_risk', {}).get('risk_level') == 'High':
            risk_factors.append("Troppe posizioni aperte")
        
        if operational_risks.get('high_loss_positions', {}).get('risk_level') == 'High':
            risk_factors.append("Molte perdite elevate")
        
        if operational_risks.get('volatility_risk', {}).get('risk_level') == 'High':
            risk_factors.append("Alta volatilità dei volumi")
        
        # Fattori di mercato
        if market_risks.get('broker_diversification', {}).get('risk_level') == 'High':
            risk_factors.append("Bassa diversificazione broker")
        
        if market_risks.get('performance_consistency', {}).get('risk_level') == 'High':
            risk_factors.append("Performance inconsistente")
        
        return risk_factors
    
    def _analyze_client_specific_risks(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i rischi specifici di un cliente"""
        risks = {
            'volume_risk': {},
            'performance_risk': {},
            'concentration_risk': {},
            'activity_risk': {},
            'risk_level': 'Low'
        }
        
        # Rischio volume
        total_volume = client_data.get('total_volume', 0)
        num_accounts = client_data.get('num_accounts', 1)
        avg_volume_per_account = total_volume / num_accounts if num_accounts > 0 else 0
        
        risks['volume_risk'] = {
            'total_volume': total_volume,
            'avg_volume_per_account': avg_volume_per_account,
            'risk_level': 'High' if avg_volume_per_account > 10000 else 'Medium' if avg_volume_per_account > 5000 else 'Low'
        }
        
        # Rischio performance
        net_result = client_data.get('net_result', 0)
        num_incroci = client_data.get('num_incroci', 1)
        avg_pnl = net_result / num_incroci if num_incroci > 0 else 0
        pnl_volatility = client_data.get('pnl_volatility', 0)
        
        risks['performance_risk'] = {
            'net_result': net_result,
            'avg_pnl': avg_pnl,
            'pnl_volatility': pnl_volatility,
            'risk_level': 'High' if avg_pnl < -500 or pnl_volatility > 1000 else 'Medium' if avg_pnl < 0 else 'Low'
        }
        
        # Rischio concentrazione
        num_brokers = client_data.get('num_brokers', 0)
        broker_diversification = num_brokers / num_accounts if num_accounts > 0 else 0
        
        risks['concentration_risk'] = {
            'num_brokers': num_brokers,
            'broker_diversification': broker_diversification,
            'risk_level': 'High' if broker_diversification < 0.3 else 'Medium' if broker_diversification < 0.6 else 'Low'
        }
        
        # Rischio attività
        last_activity = client_data.get('last_activity')
        activity_risk = 'Low'
        
        if last_activity:
            try:
                last_activity_date = datetime.strptime(last_activity, '%Y-%m-%d')
                days_since_activity = (datetime.now() - last_activity_date).days
                
                if days_since_activity > 30:
                    activity_risk = 'High'
                elif days_since_activity > 14:
                    activity_risk = 'Medium'
            except:
                pass
        
        risks['activity_risk'] = {
            'last_activity': last_activity,
            'risk_level': activity_risk
        }
        
        # Determina livello di rischio generale del cliente
        risk_scores = [
            risks['volume_risk']['risk_level'],
            risks['performance_risk']['risk_level'],
            risks['concentration_risk']['risk_level'],
            risks['activity_risk']['risk_level']
        ]
        
        if 'High' in risk_scores:
            risks['risk_level'] = 'High'
        elif 'Medium' in risk_scores:
            risks['risk_level'] = 'Medium'
        else:
            risks['risk_level'] = 'Low'
        
        return risks
    
    def _calculate_client_risk_score(self, client_risks: Dict[str, Any]) -> Dict[str, Any]:
        """Calcola il punteggio di rischio del cliente"""
        risk_levels = {'Low': 1, 'Medium': 2, 'High': 3}
        
        volume_score = risk_levels.get(client_risks.get('volume_risk', {}).get('risk_level', 'Low'), 1)
        performance_score = risk_levels.get(client_risks.get('performance_risk', {}).get('risk_level', 'Low'), 1)
        concentration_score = risk_levels.get(client_risks.get('concentration_risk', {}).get('risk_level', 'Low'), 1)
        activity_score = risk_levels.get(client_risks.get('activity_risk', {}).get('risk_level', 'Low'), 1)
        
        overall_score = (volume_score + performance_score + concentration_score + activity_score) / 4
        
        if overall_score >= 2.5:
            overall_level = 'High'
        elif overall_score >= 1.5:
            overall_level = 'Medium'
        else:
            overall_level = 'Low'
        
        return {
            'overall_score': overall_score,
            'overall_level': overall_level,
            'volume_score': volume_score,
            'performance_score': performance_score,
            'concentration_score': concentration_score,
            'activity_score': activity_score
        }
    
    def _generate_mitigation_recommendations(self, concentration_risks: Dict[str, Any], 
                                          operational_risks: Dict[str, Any], 
                                          market_risks: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera raccomandazioni di mitigazione del rischio"""
        recommendations = []
        
        # Raccomandazioni per concentrazione
        if concentration_risks.get('risk_level') == 'High':
            recommendations.append({
                'category': 'Concentration Risk',
                'priority': 'High',
                'recommendation': 'Diversificare i broker e ridurre la concentrazione su clienti singoli',
                'action': 'Aggiungere nuovi broker e limitare l\'esposizione per cliente',
                'expected_impact': 'Riduzione rischio del 40%'
            })
        
        # Raccomandazioni operative
        if operational_risks.get('open_positions_risk', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Operational Risk',
                'priority': 'High',
                'recommendation': 'Ridurre il numero di posizioni aperte',
                'action': 'Implementare limiti automatici e chiudere posizioni in perdita',
                'expected_impact': 'Riduzione rischio del 30%'
            })
        
        if operational_risks.get('high_loss_positions', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Operational Risk',
                'priority': 'Medium',
                'recommendation': 'Implementare stop-loss più stretti',
                'action': 'Definire limiti di perdita per ogni posizione',
                'expected_impact': 'Riduzione perdite del 25%'
            })
        
        # Raccomandazioni di mercato
        if market_risks.get('broker_diversification', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Market Risk',
                'priority': 'Medium',
                'recommendation': 'Aumentare la diversificazione dei broker',
                'action': 'Aggiungere almeno 2-3 nuovi broker',
                'expected_impact': 'Riduzione rischio del 20%'
            })
        
        if market_risks.get('performance_consistency', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Market Risk',
                'priority': 'Medium',
                'recommendation': 'Migliorare la consistenza delle performance',
                'action': 'Implementare strategie di risk management più conservative',
                'expected_impact': 'Miglioramento stabilità del 15%'
            })
        
        return recommendations
    
    def _generate_client_recommendations(self, client_risks: Dict[str, Any], 
                                       client_risk_score: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera raccomandazioni specifiche per il cliente"""
        recommendations = []
        
        # Raccomandazioni basate sui rischi identificati
        if client_risks.get('volume_risk', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Volume Risk',
                'priority': 'High',
                'recommendation': 'Ridurre i volumi per questo cliente',
                'action': 'Limitare i volumi a massimo 5000 per account',
                'expected_impact': 'Riduzione rischio del 50%'
            })
        
        if client_risks.get('performance_risk', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Performance Risk',
                'priority': 'High',
                'recommendation': 'Implementare monitoraggio più frequente',
                'action': 'Controlli giornalieri e stop-loss automatici',
                'expected_impact': 'Riduzione perdite del 40%'
            })
        
        if client_risks.get('concentration_risk', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Concentration Risk',
                'priority': 'Medium',
                'recommendation': 'Diversificare i broker per questo cliente',
                'action': 'Aggiungere almeno 2 nuovi broker',
                'expected_impact': 'Riduzione rischio del 30%'
            })
        
        if client_risks.get('activity_risk', {}).get('risk_level') == 'High':
            recommendations.append({
                'category': 'Activity Risk',
                'priority': 'Medium',
                'recommendation': 'Riattivare il cliente',
                'action': 'Campagna di re-engagement e offerte speciali',
                'expected_impact': 'Ripresa attività del 60%'
            })
        
        return recommendations
    
    def _prepare_risk_ai_data(self, portfolio_data: Dict[str, Any], 
                            concentration_risks: Dict[str, Any], 
                            operational_risks: Dict[str, Any], 
                            market_risks: Dict[str, Any], 
                            overall_risk_score: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara i dati per l'analisi AI dei rischi"""
        # Formatta dati del portafoglio
        formatted_portfolio_data = f"""
Portafoglio CPA - Analisi Rischi:
- Totale Clienti: {portfolio_data.get('total_clients', 0)}
- Totale Account: {portfolio_data.get('total_accounts', 0)}
- Volume Totale: {portfolio_data.get('total_volume', 0)}
- Incroci Totali: {portfolio_data.get('total_incroci', 0)}
- Risultato Netto: {portfolio_data.get('net_result', 0)}
- Posizioni Aperte: {portfolio_data.get('open_positions', 0)}
- Broker Attivi: {portfolio_data.get('num_brokers', 0)}

Rischi Identificati:
- Concentrazione: {concentration_risks.get('risk_level', 'N/A')}
- Operativi: {operational_risks.get('risk_level', 'N/A')}
- Mercato: {market_risks.get('risk_level', 'N/A')}
- Score Complessivo: {overall_risk_score.get('overall_score', 0):.2f} ({overall_risk_score.get('overall_level', 'N/A')})
"""
        
        return {
            'portfolio_data': formatted_portfolio_data,
            'concentration_risks': concentration_risks,
            'operational_risks': operational_risks,
            'market_risks': market_risks,
            'overall_risk_score': overall_risk_score
        }
