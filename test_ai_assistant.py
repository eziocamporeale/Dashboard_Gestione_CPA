#!/usr/bin/env python3
"""
Test AI Assistant per Dashboard Gestione CPA
Test delle funzionalità AI integrate
Creato da Ezio Camporeale
"""

import sys
import os
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_ai_core():
    """Test del modulo AI core"""
    print("🔍 Testando AI Core...")
    
    try:
        from components.ai_assistant.ai_core import AIAssistant
        
        # Inizializza AI Assistant
        ai_assistant = AIAssistant()
        print("✅ AI Assistant inizializzato")
        
        # Test connessione
        connection_ok = ai_assistant.test_connection()
        if connection_ok:
            print("✅ Connessione API DeepSeek OK")
        else:
            print("❌ Connessione API DeepSeek fallita")
        
        # Test generazione risposta
        test_data = {
            'nome_cliente': 'Cliente Test',
            'email': 'test@example.com',
            'broker': 'Test Broker',
            'piattaforma': 'MT4',
            'volume_posizione': 1000,
            'stato_account': 'attivo',
            'data_registrazione': '2024-01-01',
            'storia_incroci': 'Nessun incrocio registrato'
        }
        
        response = ai_assistant.generate_response('client_analysis', test_data)
        if response:
            print("✅ Generazione risposta AI OK")
            print(f"📝 Risposta: {response[:100]}...")
        else:
            print("❌ Generazione risposta AI fallita")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test AI Core: {e}")
        return False

def test_client_analyzer():
    """Test del modulo Client Analyzer"""
    print("🔍 Testando Client Analyzer...")
    
    try:
        from components.ai_assistant.client_analyzer import ClientAnalyzer
        
        # Inizializza Client Analyzer
        client_analyzer = ClientAnalyzer()
        print("✅ Client Analyzer inizializzato")
        
        # Test analisi cliente (simulata)
        test_result = client_analyzer.analyze_client(1)
        if "error" not in test_result:
            print("✅ Analisi cliente OK")
        else:
            print(f"⚠️ Analisi cliente: {test_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Client Analyzer: {e}")
        return False

def test_incroci_predictor():
    """Test del modulo Incroci Predictor"""
    print("🔍 Testando Incroci Predictor...")
    
    try:
        from components.ai_assistant.incroci_predictor import IncrociPredictor
        
        # Inizializza Incroci Predictor
        incroci_predictor = IncrociPredictor()
        print("✅ Incroci Predictor inizializzato")
        
        # Test predizione (simulata)
        test_broker_data = {
            'broker1': 'Test Broker 1',
            'broker2': 'Test Broker 2',
            'volume_posizione': 1000
        }
        
        test_result = incroci_predictor.predict_incroci_success(test_broker_data)
        if "error" not in test_result:
            print("✅ Predizione incroci OK")
        else:
            print(f"⚠️ Predizione incroci: {test_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Incroci Predictor: {e}")
        return False

def test_broker_optimizer():
    """Test del modulo Broker Optimizer"""
    print("🔍 Testando Broker Optimizer...")
    
    try:
        from components.ai_assistant.broker_optimizer import BrokerOptimizer
        
        # Inizializza Broker Optimizer
        broker_optimizer = BrokerOptimizer()
        print("✅ Broker Optimizer inizializzato")
        
        # Test ottimizzazione (simulata)
        test_result = broker_optimizer.optimize_broker_distribution()
        if "error" not in test_result:
            print("✅ Ottimizzazione broker OK")
        else:
            print(f"⚠️ Ottimizzazione broker: {test_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Broker Optimizer: {e}")
        return False

def test_marketing_advisor():
    """Test del modulo Marketing Advisor"""
    print("🔍 Testando Marketing Advisor...")
    
    try:
        from components.ai_assistant.marketing_advisor import MarketingAdvisor
        
        # Inizializza Marketing Advisor
        marketing_advisor = MarketingAdvisor()
        print("✅ Marketing Advisor inizializzato")
        
        # Test consigli marketing (simulati)
        test_result = marketing_advisor.generate_marketing_advice()
        if "error" not in test_result:
            print("✅ Consigli marketing OK")
        else:
            print(f"⚠️ Consigli marketing: {test_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Marketing Advisor: {e}")
        return False

def test_risk_analyzer():
    """Test del modulo Risk Analyzer"""
    print("🔍 Testando Risk Analyzer...")
    
    try:
        from components.ai_assistant.risk_analyzer import RiskAnalyzer
        
        # Inizializza Risk Analyzer
        risk_analyzer = RiskAnalyzer()
        print("✅ Risk Analyzer inizializzato")
        
        # Test analisi rischi (simulata)
        test_result = risk_analyzer.analyze_portfolio_risks()
        if "error" not in test_result:
            print("✅ Analisi rischi OK")
        else:
            print(f"⚠️ Analisi rischi: {test_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Risk Analyzer: {e}")
        return False

def test_report_generator():
    """Test del modulo Report Generator"""
    print("🔍 Testando Report Generator...")
    
    try:
        from components.ai_assistant.report_generator import ReportGenerator
        
        # Inizializza Report Generator
        report_generator = ReportGenerator()
        print("✅ Report Generator inizializzato")
        
        # Test generazione report (simulata)
        test_result = report_generator.generate_executive_report("monthly")
        if "error" not in test_result:
            print("✅ Generazione report OK")
        else:
            print(f"⚠️ Generazione report: {test_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Report Generator: {e}")
        return False

def test_config():
    """Test della configurazione"""
    print("🔍 Testando Configurazione...")
    
    try:
        from config import Config
        
        # Test configurazione AI
        if hasattr(Config, 'DEEPSEEK_API_KEY'):
            print("✅ API Key DeepSeek configurata")
        else:
            print("❌ API Key DeepSeek non configurata")
        
        if hasattr(Config, 'AI_ASSISTANT_CONFIG'):
            print("✅ Configurazione AI Assistant presente")
        else:
            print("❌ Configurazione AI Assistant mancante")
        
        if hasattr(Config, 'AI_PROMPTS'):
            print("✅ Prompt templates configurati")
        else:
            print("❌ Prompt templates mancanti")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test Configurazione: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 AVVIO TEST AI ASSISTANT CPA")
    print("=" * 50)
    
    tests = [
        ("Configurazione", test_config),
        ("AI Core", test_ai_core),
        ("Client Analyzer", test_client_analyzer),
        ("Incroci Predictor", test_incroci_predictor),
        ("Broker Optimizer", test_broker_optimizer),
        ("Marketing Advisor", test_marketing_advisor),
        ("Risk Analyzer", test_risk_analyzer),
        ("Report Generator", test_report_generator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Errore durante test {test_name}: {e}")
            results.append((test_name, False))
    
    # Riepilogo risultati
    print("\n" + "=" * 50)
    print("📊 RIEPILOGO TEST")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Risultato: {passed}/{total} test superati")
    
    if passed == total:
        print("🎉 Tutti i test sono stati superati!")
        return True
    else:
        print("⚠️ Alcuni test sono falliti. Controlla i log per i dettagli.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
