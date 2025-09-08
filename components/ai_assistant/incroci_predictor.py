#!/usr/bin/env python3
"""
Incroci Predictor per Dashboard Gestione CPA
Analizza i dati degli incroci e predice la probabilità di successo
Creato da Ezio Camporeale
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncrociPredictor:
    """Classe per la predizione e analisi degli incroci CPA"""
    
    def __init__(self, supabase_manager=None):
        """Inizializza il predittore incroci"""
        self.supabase_manager = supabase_manager
        self.ai_assistant = None
        
        # Inizializza AI Assistant
        try:
            from .ai_core import AIAssistant
            self.ai_assistant = AIAssistant()
            logger.info("✅ IncrociPredictor inizializzato con AI Assistant")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione AI Assistant: {e}")
    
    def predict_incroci_success(self, broker_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predice la probabilità di successo per un nuovo incrocio
        
        Args:
            broker_data: Dati dei broker coinvolti nell'incrocio
            
        Returns:
            Dict: Predizione e analisi
        """
        try:
            # Recupera dati storici incroci
            historical_data = self._get_historical_incroci_data()
            
            # Analizza pattern storici
            patterns = self._analyze_historical_patterns(historical_data)
            
            # Calcola probabilità di successo
            success_probability = self._calculate_success_probability(broker_data, patterns)
            
            # Prepara dati per AI
            ai_data = self._prepare_prediction_ai_data(historical_data, broker_data, patterns)
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('incroci_prediction', ai_data)
            
            return {
                'success_probability': success_probability,
                'patterns': patterns,
                'broker_data': broker_data,
                'ai_analysis': ai_analysis,
                'prediction_date': datetime.now().isoformat(),
                'confidence_level': self._calculate_confidence_level(historical_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Errore predizione incroci: {e}")
            return {"error": f"Errore durante la predizione: {e}"}
    
    def analyze_incroci_trends(self) -> Dict[str, Any]:
        """
        Analizza i trend degli incroci esistenti
        
        Returns:
            Dict: Analisi dei trend
        """
        try:
            # Recupera tutti i dati incroci
            all_incroci = self._get_all_incroci_data()
            
            # Analizza trend temporali
            temporal_trends = self._analyze_temporal_trends(all_incroci)
            
            # Analizza trend per broker
            broker_trends = self._analyze_broker_trends(all_incroci)
            
            # Analizza trend per volumi
            volume_trends = self._analyze_volume_trends(all_incroci)
            
            # Prepara dati per AI
            ai_data = {
                'incroci_data': self._format_incroci_for_ai(all_incroci),
                'temporal_trends': temporal_trends,
                'broker_trends': broker_trends,
                'volume_trends': volume_trends
            }
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response('incroci_prediction', ai_data)
            
            return {
                'total_incroci': len(all_incroci),
                'temporal_trends': temporal_trends,
                'broker_trends': broker_trends,
                'volume_trends': volume_trends,
                'ai_analysis': ai_analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi trend incroci: {e}")
            return {"error": f"Errore durante l'analisi: {e}"}
    
    def _get_historical_incroci_data(self) -> List[Dict[str, Any]]:
        """Recupera i dati storici degli incroci"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
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
                    ia.piattaforma,
                    ia.volume_posizione,
                    ia.data_apertura_posizione,
                    ia.data_chiusura_posizione,
                    ia.stato_posizione,
                    ib.importo_bonus,
                    ib.data_bonus
                FROM incroci i
                LEFT JOIN incroci_account ia ON i.id = ia.incrocio_id
                LEFT JOIN incroci_bonus ib ON i.id = ib.incrocio_id
                WHERE i.data_apertura >= %s
                ORDER BY i.data_apertura DESC
                """
                
                # Ultimi 6 mesi
                six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
                result = self.supabase_manager.execute_query(query, (six_months_ago,))
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero dati storici incroci: {e}")
            return []
    
    def _get_all_incroci_data(self) -> List[Dict[str, Any]]:
        """Recupera tutti i dati degli incroci"""
        try:
            if self.supabase_manager and self.supabase_manager.supabase:
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
                    ia.piattaforma,
                    ia.volume_posizione,
                    ia.data_apertura_posizione,
                    ia.data_chiusura_posizione,
                    ia.stato_posizione,
                    ib.importo_bonus,
                    ib.data_bonus
                FROM incroci i
                LEFT JOIN incroci_account ia ON i.id = ia.incrocio_id
                LEFT JOIN incroci_bonus ib ON i.id = ib.incrocio_id
                ORDER BY i.data_apertura DESC
                """
                
                result = self.supabase_manager.execute_query(query)
                return result or []
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero tutti i dati incroci: {e}")
            return []
    
    def _analyze_historical_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza i pattern storici degli incroci"""
        if not historical_data:
            return {}
        
        patterns = {
            'total_incroci': len(historical_data),
            'successful_incroci': 0,
            'failed_incroci': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'best_broker': '',
            'worst_broker': '',
            'best_timeframe': '',
            'volume_patterns': {}
        }
        
        # Analizza successi/fallimenti
        profits = [inc['profitto_perdita'] for inc in historical_data if inc['profitto_perdita'] is not None]
        if profits:
            positive_profits = [p for p in profits if p > 0]
            negative_profits = [p for p in profits if p < 0]
            
            patterns['successful_incroci'] = len(positive_profits)
            patterns['failed_incroci'] = len(negative_profits)
            patterns['avg_profit'] = sum(positive_profits) / len(positive_profits) if positive_profits else 0
            patterns['avg_loss'] = sum(negative_profits) / len(negative_profits) if negative_profits else 0
        
        # Analizza per broker
        broker_performance = {}
        for inc in historical_data:
            broker = inc.get('broker', 'Unknown')
            if broker not in broker_performance:
                broker_performance[broker] = {'total': 0, 'profits': 0, 'losses': 0}
            
            broker_performance[broker]['total'] += 1
            if inc.get('profitto_perdita', 0) > 0:
                broker_performance[broker]['profits'] += 1
            elif inc.get('profitto_perdita', 0) < 0:
                broker_performance[broker]['losses'] += 1
        
        if broker_performance:
            # Trova il broker migliore e peggiore
            best_broker_score = -1
            worst_broker_score = 1
            
            for broker, perf in broker_performance.items():
                if perf['total'] > 0:
                    success_rate = perf['profits'] / perf['total']
                    if success_rate > best_broker_score:
                        best_broker_score = success_rate
                        patterns['best_broker'] = broker
                    if success_rate < worst_broker_score:
                        worst_broker_score = success_rate
                        patterns['worst_broker'] = broker
        
        return patterns
    
    def _analyze_temporal_trends(self, all_incroci: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza i trend temporali degli incroci"""
        if not all_incroci:
            return {}
        
        # Raggruppa per mese
        monthly_data = {}
        for inc in all_incroci:
            if inc.get('data_apertura'):
                try:
                    month_key = inc['data_apertura'][:7]  # YYYY-MM
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'total': 0, 'profits': 0, 'total_pnl': 0}
                    
                    monthly_data[month_key]['total'] += 1
                    if inc.get('profitto_perdita', 0) > 0:
                        monthly_data[month_key]['profits'] += 1
                    monthly_data[month_key]['total_pnl'] += inc.get('profitto_perdita', 0)
                except:
                    continue
        
        return {
            'monthly_data': monthly_data,
            'trend_direction': 'up' if len(monthly_data) > 1 else 'stable',
            'best_month': max(monthly_data.keys(), key=lambda k: monthly_data[k]['total_pnl']) if monthly_data else None
        }
    
    def _analyze_broker_trends(self, all_incroci: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza i trend per broker"""
        if not all_incroci:
            return {}
        
        broker_stats = {}
        for inc in all_incroci:
            broker = inc.get('broker', 'Unknown')
            if broker not in broker_stats:
                broker_stats[broker] = {
                    'total': 0, 'profits': 0, 'total_pnl': 0, 
                    'avg_volume': 0, 'volumes': []
                }
            
            broker_stats[broker]['total'] += 1
            if inc.get('profitto_perdita', 0) > 0:
                broker_stats[broker]['profits'] += 1
            broker_stats[broker]['total_pnl'] += inc.get('profitto_perdita', 0)
            
            if inc.get('volume_posizione'):
                broker_stats[broker]['volumes'].append(inc['volume_posizione'])
        
        # Calcola medie
        for broker, stats in broker_stats.items():
            if stats['volumes']:
                stats['avg_volume'] = sum(stats['volumes']) / len(stats['volumes'])
            stats['success_rate'] = stats['profits'] / stats['total'] if stats['total'] > 0 else 0
        
        return broker_stats
    
    def _analyze_volume_trends(self, all_incroci: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza i trend per volumi"""
        if not all_incroci:
            return {}
        
        volumes = [inc.get('volume_posizione', 0) for inc in all_incroci if inc.get('volume_posizione')]
        if not volumes:
            return {}
        
        return {
            'min_volume': min(volumes),
            'max_volume': max(volumes),
            'avg_volume': sum(volumes) / len(volumes),
            'median_volume': sorted(volumes)[len(volumes) // 2],
            'volume_ranges': {
                'low': len([v for v in volumes if v < sum(volumes) / len(volumes) * 0.5]),
                'medium': len([v for v in volumes if sum(volumes) / len(volumes) * 0.5 <= v <= sum(volumes) / len(volumes) * 1.5]),
                'high': len([v for v in volumes if v > sum(volumes) / len(volumes) * 1.5])
            }
        }
    
    def _calculate_success_probability(self, broker_data: Dict[str, Any], patterns: Dict[str, Any]) -> float:
        """Calcola la probabilità di successo per un nuovo incrocio"""
        if not patterns:
            return 0.5  # Probabilità neutra se non ci sono dati storici
        
        base_probability = patterns.get('successful_incroci', 0) / patterns.get('total_incroci', 1)
        
        # Aggiusta basato sui broker coinvolti
        broker_adjustment = 0
        if broker_data.get('broker') == patterns.get('best_broker'):
            broker_adjustment = 0.1  # +10% per il broker migliore
        elif broker_data.get('broker') == patterns.get('worst_broker'):
            broker_adjustment = -0.1  # -10% per il broker peggiore
        
        # Aggiusta basato sul volume
        volume_adjustment = 0
        avg_volume = patterns.get('volume_patterns', {}).get('avg_volume', 0)
        if broker_data.get('volume_posizione', 0) > avg_volume * 1.5:
            volume_adjustment = -0.05  # -5% per volumi troppo alti
        elif broker_data.get('volume_posizione', 0) < avg_volume * 0.5:
            volume_adjustment = -0.02  # -2% per volumi troppo bassi
        
        final_probability = base_probability + broker_adjustment + volume_adjustment
        return max(0, min(1, final_probability))  # Mantieni tra 0 e 1
    
    def _calculate_confidence_level(self, historical_data: List[Dict[str, Any]]) -> str:
        """Calcola il livello di confidenza della predizione"""
        data_points = len(historical_data)
        
        if data_points >= 100:
            return "Alta"
        elif data_points >= 50:
            return "Media"
        elif data_points >= 20:
            return "Bassa"
        else:
            return "Molto Bassa"
    
    def _prepare_prediction_ai_data(self, historical_data: List[Dict[str, Any]], 
                                   broker_data: Dict[str, Any], 
                                   patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara i dati per l'analisi AI della predizione"""
        # Formatta dati storici
        formatted_historical = ""
        for inc in historical_data[:20]:  # Ultimi 20 incroci
            formatted_historical += f"- Data: {inc.get('data_apertura', 'N/A')}, "
            formatted_historical += f"Broker: {inc.get('broker', 'N/A')}, "
            formatted_historical += f"P&L: {inc.get('profitto_perdita', 0)}, "
            formatted_historical += f"Volume: {inc.get('volume_posizione', 0)}\n"
        
        return {
            'incroci_data': formatted_historical,
            'patterns': patterns,
            'broker_data': broker_data,
            'total_historical': len(historical_data)
        }
    
    def _format_incroci_for_ai(self, all_incroci: List[Dict[str, Any]]) -> str:
        """Formatta i dati degli incroci per l'AI"""
        formatted_data = f"Totale incroci analizzati: {len(all_incroci)}\n\n"
        
        # Statistiche generali
        profits = [inc.get('profitto_perdita', 0) for inc in all_incroci if inc.get('profitto_perdita')]
        if profits:
            positive = len([p for p in profits if p > 0])
            negative = len([p for p in profits if p < 0])
            formatted_data += f"Successi: {positive}, Fallimenti: {negative}\n"
            formatted_data += f"Profitto medio: {sum(p for p in profits if p > 0) / positive if positive > 0 else 0:.2f}\n"
            formatted_data += f"Perdita media: {sum(p for p in profits if p < 0) / negative if negative > 0 else 0:.2f}\n\n"
        
        # Top 10 incroci migliori
        best_incroci = sorted(all_incroci, key=lambda x: x.get('profitto_perdita', 0), reverse=True)[:10]
        formatted_data += "Top 10 incroci migliori:\n"
        for inc in best_incroci:
            formatted_data += f"- {inc.get('data_apertura', 'N/A')}: {inc.get('profitto_perdita', 0)} ({inc.get('broker', 'N/A')})\n"
        
        return formatted_data
