#!/usr/bin/env python3
"""
Modulo AI Assistant per Dashboard Gestione CPA
Integrazione DeepSeek API per analisi avanzate
Creato da Ezio Camporeale
"""

# Import dei moduli AI
from .ai_core import AIAssistant
from .client_analyzer import ClientAnalyzer
from .incroci_predictor import IncrociPredictor
from .broker_optimizer import BrokerOptimizer
from .marketing_advisor import MarketingAdvisor
from .risk_analyzer import RiskAnalyzer
from .report_generator import ReportGenerator
from .ai_ui_components import render_ai_assistant

__all__ = [
    'AIAssistant',
    'ClientAnalyzer', 
    'IncrociPredictor',
    'BrokerOptimizer',
    'MarketingAdvisor',
    'RiskAnalyzer',
    'ReportGenerator',
    'render_ai_assistant'
]
