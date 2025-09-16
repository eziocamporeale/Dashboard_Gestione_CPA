#!/usr/bin/env python3
"""
🧪 TEST SETUP INCROCI MODERNI
Script per verificare che il setup del test funzioni correttamente
"""

import sys
import os
import logging
from datetime import datetime

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_config_file():
    """Testa il file di configurazione"""
    try:
        from config_incroci_test import is_modern_enabled, get_test_config, get_test_messages
        
        logger.info("🧪 Test file di configurazione...")
        
        # Test funzioni base
        modern_enabled = is_modern_enabled()
        config = get_test_config()
        messages = get_test_messages()
        
        logger.info(f"✅ Modern UI abilitato: {modern_enabled}")
        logger.info(f"✅ Configurazione caricata: {len(config)} parametri")
        logger.info(f"✅ Messaggi caricati: {len(messages)} messaggi")
        
        # Verifica parametri essenziali
        required_keys = ['modern_ui', 'show_toggle', 'default_version']
        for key in required_keys:
            if key in config:
                logger.info(f"✅ Parametro '{key}': {config[key]}")
            else:
                logger.error(f"❌ Parametro '{key}' mancante")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore test configurazione: {e}")
        return False

def test_modern_component():
    """Testa il componente moderno"""
    try:
        logger.info("🧪 Test componente IncrociModern...")
        
        # Importa le dipendenze
        from database.incroci_manager import IncrociManager
        from components.incroci_modern import IncrociModern
        
        # Mock database manager
        class MockDatabaseManager:
            def ottieni_tutti_clienti(self):
                return []
        
        # Inizializza componenti
        incroci_manager = IncrociManager()
        db_manager = MockDatabaseManager()
        
        # Crea componente moderno
        modern_component = IncrociModern(incroci_manager, db_manager)
        
        logger.info("✅ Componente IncrociModern inizializzato correttamente")
        
        # Test metodi principali
        methods_to_test = [
            'render', '_render_dashboard_overview', '_render_dashboard_tab',
            '_render_incroci_tab', '_render_nuovo_incrocio_tab',
            '_render_analytics_tab', '_render_impostazioni_tab'
        ]
        
        for method_name in methods_to_test:
            if hasattr(modern_component, method_name):
                logger.info(f"✅ Metodo '{method_name}' disponibile")
            else:
                logger.error(f"❌ Metodo '{method_name}' mancante")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore test componente moderno: {e}")
        return False

def test_original_component():
    """Testa il componente originale"""
    try:
        logger.info("🧪 Test componente IncrociTab originale...")
        
        from components.incroci_tab import IncrociTab
        from database.incroci_manager import IncrociManager
        
        # Mock database manager
        class MockDatabaseManager:
            def ottieni_tutti_clienti(self):
                return []
        
        # Inizializza componenti
        incroci_manager = IncrociManager()
        db_manager = MockDatabaseManager()
        
        # Crea componente originale
        original_component = IncrociTab(incroci_manager, db_manager)
        
        logger.info("✅ Componente IncrociTab originale inizializzato correttamente")
        
        # Test metodi principali
        methods_to_test = [
            'render', 'render_lista_incroci', 'render_nuovo_incrocio',
            'render_statistiche', 'render_ricerca'
        ]
        
        for method_name in methods_to_test:
            if hasattr(original_component, method_name):
                logger.info(f"✅ Metodo '{method_name}' disponibile")
            else:
                logger.error(f"❌ Metodo '{method_name}' mancante")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore test componente originale: {e}")
        return False

def test_app_integration():
    """Testa l'integrazione con app.py"""
    try:
        logger.info("🧪 Test integrazione app.py...")
        
        # Verifica che i file necessari esistano
        required_files = [
            'app.py',
            'config_incroci_test.py',
            'components/incroci_modern.py',
            'components/incroci_tab.py'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                logger.info(f"✅ File '{file_path}' presente")
            else:
                logger.error(f"❌ File '{file_path}' mancante")
                return False
        
        # Test import delle configurazioni
        try:
            from config_incroci_test import is_modern_enabled, get_test_config, get_test_messages
            logger.info("✅ Import configurazioni funzionante")
        except Exception as e:
            logger.error(f"❌ Errore import configurazioni: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore test integrazione: {e}")
        return False

def run_all_tests():
    """Esegue tutti i test"""
    logger.info("🚀 Avvio test completo setup incroci moderni...")
    
    tests = [
        ("Configurazione", test_config_file),
        ("Componente Moderno", test_modern_component),
        ("Componente Originale", test_original_component),
        ("Integrazione App", test_app_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ Test '{test_name}' PASSATO")
            else:
                logger.error(f"❌ Test '{test_name}' FALLITO")
                
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' ERRORE: {e}")
            results.append((test_name, False))
    
    # Riepilogo finale
    logger.info(f"\n{'='*60}")
    logger.info("📊 RIEPILOGO TEST")
    logger.info(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSATO" if result else "❌ FALLITO"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nRisultato: {passed}/{total} test passati")
    
    if passed == total:
        logger.info("🎉 TUTTI I TEST SONO PASSATI!")
        logger.info("🚀 Il setup è pronto per il test della nuova interfaccia!")
        return True
    else:
        logger.error("⚠️ ALCUNI TEST SONO FALLITI!")
        logger.error("🔧 Controlla gli errori sopra prima di procedere")
        return False

def show_instructions():
    """Mostra le istruzioni per il test"""
    print("\n" + "="*80)
    print("🧪 SETUP TEST INCROCI MODERNI COMPLETATO")
    print("="*80)
    print("")
    print("📋 COME PROCEDERE:")
    print("1. Vai alla sezione '🔄 Incroci' nell'applicazione")
    print("2. Guarda la sidebar - vedrai '🔧 Test Interfaccia'")
    print("3. Usa il radio button per scegliere tra:")
    print("   • 🎨 Moderna (nuova interfaccia)")
    print("   • 📋 Originale (interfaccia attuale)")
    print("")
    print("✅ SICUREZZA:")
    print("• L'interfaccia originale rimane intatta")
    print("• Tutti i dati sono preservati")
    print("• Nessun rischio di perdita di funzionalità")
    print("• Rollback immediato possibile")
    print("")
    print("🔧 CONFIGURAZIONE:")
    print("• Modifica config_incroci_test.py per cambiare impostazioni")
    print("• ENABLE_MODERN_INCROCI = True/False per abilitare/disabilitare")
    print("")
    print("📚 DOCUMENTAZIONE:")
    print("• Leggi TEST_INCROCI_MODERNI.md per istruzioni dettagliate")
    print("• Leggi INCROCI_IMPROVEMENT_PLAN.md per il piano completo")
    print("="*80)

if __name__ == "__main__":
    print("🧪 TEST SETUP INCROCI MODERNI")
    print("="*60)
    
    success = run_all_tests()
    
    if success:
        show_instructions()
        print("\n✅ Setup completato con successo!")
        print("🎉 Puoi ora testare la nuova interfaccia!")
    else:
        print("\n❌ Setup fallito!")
        print("🔧 Risolvi gli errori prima di procedere")
    
    sys.exit(0 if success else 1)

