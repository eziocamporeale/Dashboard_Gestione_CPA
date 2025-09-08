#!/usr/bin/env python3
"""
AI UI Components per Dashboard Gestione CPA
Interfaccia utente per l'assistente AI
Creato da Ezio Camporeale
"""

import streamlit as st
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_ai_assistant(supabase_manager=None):
    """Renderizza l'interfaccia dell'assistente AI"""
    
    st.markdown("## 🤖 AI Assistant CPA")
    st.markdown("Assistente intelligente per analisi avanzate e consigli professionali")
    
    # Inizializza i moduli AI
    try:
        from .ai_core import AIAssistant
        from .client_analyzer import ClientAnalyzer
        from .incroci_predictor import IncrociPredictor
        from .broker_optimizer import BrokerOptimizer
        from .marketing_advisor import MarketingAdvisor
        from .risk_analyzer import RiskAnalyzer
        from .report_generator import ReportGenerator
        
        # Inizializza i moduli
        ai_assistant = AIAssistant()
        client_analyzer = ClientAnalyzer(supabase_manager)
        incroci_predictor = IncrociPredictor(supabase_manager)
        broker_optimizer = BrokerOptimizer(supabase_manager)
        marketing_advisor = MarketingAdvisor(supabase_manager)
        risk_analyzer = RiskAnalyzer(supabase_manager)
        report_generator = ReportGenerator(supabase_manager)
        
        logger.info("✅ Tutti i moduli AI inizializzati correttamente")
        
    except Exception as e:
        st.error(f"❌ Errore inizializzazione moduli AI: {e}")
        logger.error(f"❌ Errore inizializzazione moduli AI: {e}")
        return
    
    # Test connessione AI
    if st.button("🔍 Test Connessione AI", key="test_ai_connection"):
        with st.spinner("Testando connessione AI..."):
            if ai_assistant.test_connection():
                st.success("✅ Connessione AI attiva!")
            else:
                st.error("❌ Connessione AI non disponibile")
    
    # Tabs per le diverse funzionalità AI
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👤 Analisi Clienti", 
        "📊 Predizione Incroci", 
        "🏢 Ottimizzazione Broker",
        "📈 Consigli Marketing",
        "⚠️ Analisi Rischi",
        "📋 Report Generazione",
        "⚙️ Configurazione"
    ])
    
    with tab1:
        _render_client_analysis_tab(client_analyzer)
    
    with tab2:
        _render_incroci_prediction_tab(incroci_predictor)
    
    with tab3:
        _render_broker_optimization_tab(broker_optimizer)
    
    with tab4:
        _render_marketing_advice_tab(marketing_advisor)
    
    with tab5:
        _render_risk_analysis_tab(risk_analyzer)
    
    with tab6:
        _render_report_generation_tab(report_generator)
    
    with tab7:
        _render_ai_configuration_tab(ai_assistant)

def _render_client_analysis_tab(client_analyzer):
    """Renderizza il tab per l'analisi clienti"""
    st.markdown("### 👤 Analisi Clienti")
    st.markdown("Analizza le performance e fornisce insights sui clienti")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Seleziona Cliente")
        
        # Recupera lista clienti
        clients = _get_clients_for_selection()
        
        if clients:
            client_options = {f"{client['nome_cliente']} (ID: {client['id']})": client['id'] 
                            for client in clients}
            
            selected_client = st.selectbox(
                "Scegli un cliente:",
                options=list(client_options.keys()),
                key="client_selection"
            )
            
            if selected_client:
                client_id = client_options[selected_client]
                
                if st.button("🔍 Analizza Cliente", key="analyze_client"):
                    with st.spinner("Analizzando cliente..."):
                        result = client_analyzer.analyze_client(client_id)
                        
                        if "error" not in result:
                            _display_client_analysis_result(result)
                        else:
                            st.error(f"❌ {result['error']}")
        
        st.markdown("---")
        st.markdown("#### Analisi Generale")
        
        if st.button("📊 Analizza Tutti i Clienti", key="analyze_all_clients"):
            with st.spinner("Analizzando tutti i clienti..."):
                result = client_analyzer.analyze_all_clients()
                
                if "error" not in result:
                    _display_all_clients_analysis(result)
                else:
                    st.error(f"❌ {result['error']}")
    
    with col2:
        st.markdown("#### Risultati Analisi")
        st.info("Seleziona un cliente e clicca 'Analizza Cliente' per vedere i risultati")

def _render_incroci_prediction_tab(incroci_predictor):
    """Renderizza il tab per la predizione incroci"""
    st.markdown("### 📊 Predizione Incroci")
    st.markdown("Analizza i pattern storici e predice la probabilità di successo")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Configurazione Predizione")
        
        # Input per la predizione
        broker1 = st.text_input("Broker 1:", key="broker1_input")
        broker2 = st.text_input("Broker 2:", key="broker2_input")
        volume = st.number_input("Volume Posizione:", min_value=0.0, value=1000.0, key="volume_input")
        
        if st.button("🔮 Predici Successo", key="predict_incroci"):
            if broker1 and broker2:
                broker_data = {
                    'broker1': broker1,
                    'broker2': broker2,
                    'volume_posizione': volume
                }
                
                with st.spinner("Calcolando predizione..."):
                    result = incroci_predictor.predict_incroci_success(broker_data)
                    
                    if "error" not in result:
                        _display_prediction_result(result)
                    else:
                        st.error(f"❌ {result['error']}")
            else:
                st.warning("⚠️ Inserisci entrambi i broker")
        
        st.markdown("---")
        st.markdown("#### Analisi Trend")
        
        if st.button("📈 Analizza Trend Incroci", key="analyze_trends"):
            with st.spinner("Analizzando trend..."):
                result = incroci_predictor.analyze_incroci_trends()
                
                if "error" not in result:
                    _display_trend_analysis(result)
                else:
                    st.error(f"❌ {result['error']}")
    
    with col2:
        st.markdown("#### Risultati Predizione")
        st.info("Configura i parametri e clicca 'Predici Successo' per vedere i risultati")

def _render_broker_optimization_tab(broker_optimizer):
    """Renderizza il tab per l'ottimizzazione broker"""
    st.markdown("### 🏢 Ottimizzazione Broker")
    st.markdown("Analizza e ottimizza la distribuzione dei broker")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Analisi Broker")
        
        if st.button("🔍 Analizza Performance Broker", key="analyze_broker_performance"):
            with st.spinner("Analizzando performance broker..."):
                result = broker_optimizer.optimize_broker_distribution()
                
                if "error" not in result:
                    _display_broker_optimization_result(result)
                else:
                    st.error(f"❌ {result['error']}")
        
        st.markdown("---")
        st.markdown("#### Analisi Rischi")
        
        if st.button("⚠️ Analizza Rischi Broker", key="analyze_broker_risks"):
            with st.spinner("Analizzando rischi broker..."):
                result = broker_optimizer.analyze_broker_risks()
                
                if "error" not in result:
                    _display_broker_risks_result(result)
                else:
                    st.error(f"❌ {result['error']}")
    
    with col2:
        st.markdown("#### Risultati Ottimizzazione")
        st.info("Clicca sui pulsanti per vedere le analisi dei broker")

def _render_marketing_advice_tab(marketing_advisor):
    """Renderizza il tab per i consigli di marketing"""
    st.markdown("### 📈 Consigli Marketing")
    st.markdown("Strategie di marketing basate sui dati dei clienti")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Analisi Marketing")
        
        if st.button("📊 Genera Consigli Marketing", key="generate_marketing_advice"):
            with st.spinner("Generando consigli marketing..."):
                result = marketing_advisor.generate_marketing_advice()
                
                if "error" not in result:
                    _display_marketing_advice_result(result)
                else:
                    st.error(f"❌ {result['error']}")
        
        st.markdown("---")
        st.markdown("#### Analisi CLV")
        
        if st.button("💰 Analizza Customer Lifetime Value", key="analyze_clv"):
            with st.spinner("Analizzando CLV..."):
                result = marketing_advisor.analyze_client_lifetime_value()
                
                if "error" not in result:
                    _display_clv_analysis_result(result)
                else:
                    st.error(f"❌ {result['error']}")
    
    with col2:
        st.markdown("#### Risultati Marketing")
        st.info("Clicca sui pulsanti per vedere i consigli di marketing")

def _render_risk_analysis_tab(risk_analyzer):
    """Renderizza il tab per l'analisi dei rischi"""
    st.markdown("### ⚠️ Analisi Rischi")
    st.markdown("Analizza i rischi del portafoglio e dei clienti")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Analisi Portafoglio")
        
        if st.button("🔍 Analizza Rischi Portafoglio", key="analyze_portfolio_risks"):
            with st.spinner("Analizzando rischi portafoglio..."):
                result = risk_analyzer.analyze_portfolio_risks()
                
                if "error" not in result:
                    _display_portfolio_risks_result(result)
                else:
                    st.error(f"❌ {result['error']}")
        
        st.markdown("---")
        st.markdown("#### Analisi Cliente")
        
        # Selezione cliente per analisi rischi
        clients = _get_clients_for_selection()
        if clients:
            client_options = {f"{client['nome_cliente']} (ID: {client['id']})": client['id'] 
                            for client in clients}
            
            selected_client = st.selectbox(
                "Scegli cliente per analisi rischi:",
                options=list(client_options.keys()),
                key="risk_client_selection"
            )
            
            if selected_client:
                client_id = client_options[selected_client]
                
                if st.button("⚠️ Analizza Rischi Cliente", key="analyze_client_risks"):
                    with st.spinner("Analizzando rischi cliente..."):
                        result = risk_analyzer.analyze_client_risks(client_id)
                        
                        if "error" not in result:
                            _display_client_risks_result(result)
                        else:
                            st.error(f"❌ {result['error']}")
    
    with col2:
        st.markdown("#### Risultati Analisi Rischi")
        st.info("Clicca sui pulsanti per vedere le analisi dei rischi")

def _render_report_generation_tab(report_generator):
    """Renderizza il tab per la generazione report"""
    st.markdown("### 📋 Generazione Report")
    st.markdown("Genera report professionali sui dati CPA")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Report Esecutivo")
        
        report_type = st.selectbox(
            "Tipo di report:",
            options=["monthly", "quarterly", "yearly"],
            key="report_type_selection"
        )
        
        if st.button("📊 Genera Report Esecutivo", key="generate_executive_report"):
            with st.spinner("Generando report esecutivo..."):
                result = report_generator.generate_executive_report(report_type)
                
                if "error" not in result:
                    _display_executive_report_result(result)
                else:
                    st.error(f"❌ {result['error']}")
        
        st.markdown("---")
        st.markdown("#### Report Cliente")
        
        # Selezione cliente per report
        clients = _get_clients_for_selection()
        if clients:
            client_options = {f"{client['nome_cliente']} (ID: {client['id']})": client['id'] 
                            for client in clients}
            
            selected_client = st.selectbox(
                "Scegli cliente per report:",
                options=list(client_options.keys()),
                key="report_client_selection"
            )
            
            if selected_client:
                client_id = client_options[selected_client]
                
                if st.button("📋 Genera Report Cliente", key="generate_client_report"):
                    with st.spinner("Generando report cliente..."):
                        result = report_generator.generate_client_report(client_id)
                        
                        if "error" not in result:
                            _display_client_report_result(result)
                        else:
                            st.error(f"❌ {result['error']}")
    
    with col2:
        st.markdown("#### Risultati Report")
        st.info("Seleziona il tipo di report e clicca per generarlo")

def _render_ai_configuration_tab(ai_assistant):
    """Renderizza il tab per la configurazione AI"""
    st.markdown("### ⚙️ Configurazione AI")
    st.markdown("Gestisci le impostazioni dell'assistente AI")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Stato Sistema")
        
        # Test connessione
        if st.button("🔍 Test Connessione", key="test_connection_config"):
            with st.spinner("Testando connessione..."):
                if ai_assistant.test_connection():
                    st.success("✅ Connessione AI attiva!")
                else:
                    st.error("❌ Connessione AI non disponibile")
        
        # Statistiche cache
        cache_stats = ai_assistant.get_cache_stats()
        st.markdown("#### Statistiche Cache")
        st.write(f"**Risposte in cache:** {cache_stats['total_cached']}")
        st.write(f"**Cache abilitata:** {'Sì' if cache_stats['cache_enabled'] else 'No'}")
        st.write(f"**Durata cache:** {cache_stats['cache_duration_hours']} ore")
        
        if st.button("🗑️ Pulisci Cache", key="clear_cache"):
            ai_assistant.clear_cache()
            st.success("✅ Cache pulita!")
    
    with col2:
        st.markdown("#### Informazioni Sistema")
        
        st.markdown("**Versione AI Assistant:** 1.0.0")
        st.markdown("**Modello:** DeepSeek Chat")
        st.markdown("**Timeout:** 60 secondi")
        st.markdown("**Tentativi:** 3")
        st.markdown("**Temperatura:** 0.7")
        st.markdown("**Max Tokens:** 1500")

def _get_clients_for_selection():
    """Recupera la lista dei clienti per la selezione"""
    try:
        # Simula il recupero dei clienti (da implementare con Supabase)
        return [
            {'id': 1, 'nome_cliente': 'Cliente Test 1'},
            {'id': 2, 'nome_cliente': 'Cliente Test 2'},
            {'id': 3, 'nome_cliente': 'Cliente Test 3'}
        ]
    except Exception as e:
        logger.error(f"❌ Errore recupero clienti: {e}")
        return []

def _display_client_analysis_result(result):
    """Mostra i risultati dell'analisi cliente"""
    st.markdown("#### 📊 Risultati Analisi Cliente")
    
    # Metriche
    metrics = result.get('metrics', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Totale Incroci", metrics.get('total_incroci', 0))
    with col2:
        st.metric("Profitti Totali", f"{metrics.get('total_profits', 0):.2f}")
    with col3:
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
    with col4:
        st.metric("P&L Medio", f"{metrics.get('avg_profit', 0):.2f}")
    
    # Analisi AI
    st.markdown("#### 🤖 Analisi AI")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_all_clients_analysis(result):
    """Mostra i risultati dell'analisi di tutti i clienti"""
    st.markdown("#### 📊 Analisi Generale Clienti")
    
    # Metriche aggregate
    metrics = result.get('aggregated_metrics', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Totale Clienti", metrics.get('total_clients', 0))
    with col2:
        st.metric("Totale Account", metrics.get('total_accounts', 0))
    with col3:
        st.metric("Risultato Netto", f"{metrics.get('net_result', 0):.2f}")
    with col4:
        st.metric("Account per Cliente", f"{metrics.get('avg_accounts_per_client', 0):.1f}")
    
    # Analisi AI
    st.markdown("#### 🤖 Analisi AI")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_prediction_result(result):
    """Mostra i risultati della predizione"""
    st.markdown("#### 🔮 Risultati Predizione")
    
    # Probabilità di successo
    success_prob = result.get('success_probability', 0)
    confidence = result.get('confidence_level', 'N/A')
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Probabilità Successo", f"{success_prob * 100:.1f}%")
    with col2:
        st.metric("Livello Confidenza", confidence)
    
    # Analisi AI
    st.markdown("#### 🤖 Analisi Predizione")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_trend_analysis(result):
    """Mostra i risultati dell'analisi trend"""
    st.markdown("#### 📈 Analisi Trend Incroci")
    
    # Metriche trend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Incroci", result.get('total_incroci', 0))
    with col2:
        st.metric("Trend Temporali", result.get('temporal_trends', {}).get('trend_direction', 'N/A'))
    with col3:
        st.metric("Broker Analizzati", len(result.get('broker_trends', {})))
    
    # Analisi AI
    st.markdown("#### 🤖 Analisi Trend")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_broker_optimization_result(result):
    """Mostra i risultati dell'ottimizzazione broker"""
    st.markdown("#### 🏢 Risultati Ottimizzazione Broker")
    
    # Performance analysis
    performance = result.get('performance_analysis', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Totale Broker", performance.get('total_brokers', 0))
    with col2:
        st.metric("Volume Totale", f"{performance.get('total_volume', 0):.2f}")
    with col3:
        st.metric("Risultato Netto", f"{performance.get('total_net_result', 0):.2f}")
    
    # Analisi AI
    st.markdown("#### 🤖 Analisi Ottimizzazione")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_broker_risks_result(result):
    """Mostra i risultati dell'analisi rischi broker"""
    st.markdown("#### ⚠️ Risultati Analisi Rischi Broker")
    
    # Risk concentration
    concentration = result.get('risk_concentration', {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Livello Rischio", concentration.get('risk_level', 'N/A'))
    with col2:
        st.metric("Volume Totale", f"{concentration.get('total_volume', 0):.2f}")
    
    # High risk brokers
    high_risk = result.get('high_risk_brokers', [])
    if high_risk:
        st.markdown("#### 🚨 Broker ad Alto Rischio")
        for broker in high_risk:
            st.warning(f"**{broker['broker']}** - Score: {broker['risk_score']}")

def _display_marketing_advice_result(result):
    """Mostra i risultati dei consigli di marketing"""
    st.markdown("#### 📈 Risultati Consigli Marketing")
    
    # Client segmentation
    segmentation = result.get('client_segmentation', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Totale Clienti", segmentation.get('total_clients', 0))
    with col2:
        st.metric("Clienti High Value", len(segmentation.get('segments', {}).get('high_value', [])))
    with col3:
        st.metric("Clienti Nuovi", len(segmentation.get('segments', {}).get('new_clients', [])))
    
    # Analisi AI
    st.markdown("#### 🤖 Consigli Marketing")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_clv_analysis_result(result):
    """Mostra i risultati dell'analisi CLV"""
    st.markdown("#### 💰 Risultati Analisi CLV")
    
    # CLV metrics
    metrics = result.get('clv_metrics', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CLV Medio", f"{metrics.get('avg_clv', 0):.2f}")
    with col2:
        st.metric("Retention Rate", f"{metrics.get('retention_rate', 0):.1f}%")
    with col3:
        st.metric("Churn Rate", f"{metrics.get('churn_rate', 0):.1f}%")
    
    # High value clients
    high_value = result.get('high_value_clients', [])
    if high_value:
        st.markdown("#### 👑 Clienti ad Alto Valore")
        for client in high_value[:5]:  # Top 5
            st.info(f"**{client['name']}** - CLV: {client['clv']:.2f} ({client['value_tier']})")

def _display_portfolio_risks_result(result):
    """Mostra i risultati dell'analisi rischi portafoglio"""
    st.markdown("#### ⚠️ Risultati Analisi Rischi Portafoglio")
    
    # Overall risk score
    risk_score = result.get('overall_risk_score', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score Rischio", f"{risk_score.get('overall_score', 0):.2f}")
    with col2:
        st.metric("Livello Rischio", risk_score.get('overall_level', 'N/A'))
    with col3:
        st.metric("Fattori Rischio", len(risk_score.get('risk_factors', [])))
    
    # Risk factors
    risk_factors = risk_score.get('risk_factors', [])
    if risk_factors:
        st.markdown("#### 🚨 Fattori di Rischio Identificati")
        for factor in risk_factors:
            st.warning(f"• {factor}")
    
    # Analisi AI
    st.markdown("#### 🤖 Analisi Rischi")
    st.markdown(result.get('ai_analysis', 'Nessuna analisi disponibile'))

def _display_client_risks_result(result):
    """Mostra i risultati dell'analisi rischi cliente"""
    st.markdown("#### ⚠️ Risultati Analisi Rischi Cliente")
    
    # Client risk score
    risk_score = result.get('client_risk_score', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score Rischio", f"{risk_score.get('overall_score', 0):.2f}")
    with col2:
        st.metric("Livello Rischio", risk_score.get('overall_level', 'N/A'))
    with col3:
        st.metric("Volume Score", risk_score.get('volume_score', 0))
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        st.markdown("#### 💡 Raccomandazioni")
        for rec in recommendations:
            st.info(f"**{rec['category']}:** {rec['recommendation']}")

def _display_executive_report_result(result):
    """Mostra i risultati del report esecutivo"""
    st.markdown("#### 📊 Report Esecutivo")
    
    # Key metrics
    metrics = result.get('key_metrics', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Totale Clienti", metrics.get('total_clients', 0))
    with col2:
        st.metric("Volume Totale", f"{metrics.get('total_volume', 0):.2f}")
    with col3:
        st.metric("Risultato Netto", f"{metrics.get('net_result', 0):.2f}")
    with col4:
        st.metric("Success Rate", f"{metrics.get('success_rate', 0):.1f}%")
    
    # Insights
    insights = result.get('insights', [])
    if insights:
        st.markdown("#### 💡 Insights Principali")
        for insight in insights:
            priority_color = "🔴" if insight['priority'] == 'High' else "🟡" if insight['priority'] == 'Medium' else "🟢"
            st.markdown(f"{priority_color} **{insight['category']}:** {insight['insight']}")
    
    # Analisi AI
    st.markdown("#### 🤖 Report AI")
    st.markdown(result.get('ai_report', 'Nessun report disponibile'))

def _display_client_report_result(result):
    """Mostra i risultati del report cliente"""
    st.markdown("#### 📋 Report Cliente")
    
    # Client metrics
    metrics = result.get('client_metrics', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Account", metrics.get('num_accounts', 0))
    with col2:
        st.metric("Volume Totale", f"{metrics.get('total_volume', 0):.2f}")
    with col3:
        st.metric("CLV", f"{metrics.get('clv', 0):.2f}")
    with col4:
        st.metric("Tier", metrics.get('client_tier', 'N/A'))
    
    # Performance analysis
    performance = result.get('performance_analysis', {})
    st.markdown("#### 📈 Analisi Performance")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Performance", performance.get('overall_performance', 'N/A'))
    with col2:
        st.metric("Rischio", performance.get('risk_level', 'N/A'))
    with col3:
        st.metric("Crescita", performance.get('growth_potential', 'N/A'))
    with col4:
        st.metric("Retention", performance.get('retention_probability', 'N/A'))
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        st.markdown("#### 💡 Raccomandazioni")
        for rec in recommendations:
            priority_color = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
            st.markdown(f"{priority_color} **{rec['category']}:** {rec['recommendation']}")
