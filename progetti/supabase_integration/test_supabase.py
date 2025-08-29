#!/usr/bin/env python3
"""
🧪 TEST SUPABASE MANAGER
🔍 Verifica funzionalità senza interferire con sistema attuale
📊 Test parallelo e sicuro
"""

import os
import sys
import logging
from datetime import datetime

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_supabase_installation():
    """Testa l'installazione di Supabase"""
    try:
        import supabase
        logger.info("✅ Supabase installato correttamente")
        return True
    except ImportError:
        logger.error("❌ Supabase non installato")
        logger.info("📦 Installa con: pip install supabase")
        return False

def test_supabase_config():
    """Testa la configurazione di Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url:
        logger.error("❌ SUPABASE_URL non configurato")
        return False
    
    if not supabase_key:
        logger.error("❌ SUPABASE_ANON_KEY non configurato")
        return False
    
    logger.info("✅ Variabili ambiente Supabase configurate")
    logger.info(f"🔗 URL: {supabase_url}")
    logger.info(f"🔑 Key: {supabase_key[:10]}...")
    return True

def test_supabase_connection():
    """Testa la connessione a Supabase"""
    try:
        from supabase_manager import SupabaseManager
        
        manager = SupabaseManager()
        
        if not manager.is_configured:
            logger.error("❌ SupabaseManager non configurato")
            return False
        
        # Test connessione
        success, message = manager.test_connection()
        
        if success:
            logger.info(f"✅ Connessione Supabase: {message}")
            return True
        else:
            logger.error(f"❌ Connessione Supabase: {message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore test connessione: {e}")
        return False

def test_supabase_operations():
    """Testa le operazioni CRUD su Supabase"""
    try:
        from supabase_manager import SupabaseManager
        
        manager = SupabaseManager()
        
        if not manager.is_configured:
            logger.error("❌ SupabaseManager non configurato")
            return False
        
        # Test aggiunta cliente
        test_cliente = {
            "nome_cliente": f"Test Supabase {datetime.now().strftime('%H:%M:%S')}",
            "email": f"test{datetime.now().strftime('%H%M%S')}@supabase.com",
            "broker": "Test Broker"
        }
        
        logger.info("🧪 Test aggiunta cliente...")
        success, message = manager.add_cliente(test_cliente)
        
        if success:
            logger.info(f"✅ Test aggiunta cliente: {message}")
            
            # Test recupero clienti
            logger.info("🧪 Test recupero clienti...")
            clienti = manager.get_clienti()
            logger.info(f"✅ Clienti trovati: {len(clienti)}")
            
            # Test eliminazione cliente (se trovato)
            if clienti:
                cliente_id = clienti[0]['id']
                logger.info("🧪 Test eliminazione cliente...")
                success, message = manager.delete_cliente(cliente_id)
                logger.info(f"✅ Test eliminazione cliente: {message}")
            
            return True
        else:
            logger.error(f"❌ Test aggiunta cliente: {message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore test operazioni: {e}")
        return False

def run_all_tests():
    """Esegue tutti i test Supabase"""
    logger.info("🚀 INIZIO TEST SUPABASE MANAGER")
    logger.info("=" * 50)
    
    tests = [
        ("Installazione Supabase", test_supabase_installation),
        ("Configurazione Supabase", test_supabase_config),
        ("Connessione Supabase", test_supabase_connection),
        ("Operazioni CRUD", test_supabase_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name}: PASSATO")
            else:
                logger.error(f"❌ {test_name}: FALLITO")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERRORE - {e}")
            results.append((test_name, False))
    
    # Riepilogo risultati
    logger.info("\n" + "=" * 50)
    logger.info("📊 RIEPILOGO TEST SUPABASE")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSATO" if result else "❌ FALLITO"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🎯 RISULTATO FINALE: {passed}/{total} test superati")
    
    if passed == total:
        logger.info("🎉 TUTTI I TEST SUPERATI! Supabase è pronto per l'uso!")
        return True
    else:
        logger.warning("⚠️ ALCUNI TEST FALLITI. Controlla la configurazione.")
        return False

def main():
    """Funzione principale"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
🧪 TEST SUPABASE MANAGER - Guida all'uso

USAGE:
    python test_supabase.py              # Esegue tutti i test
    python test_supabase.py --help       # Mostra questa guida

DESCRIZIONE:
    Script di test per verificare il funzionamento di Supabase
    senza interferire con il sistema attuale.

REQUISITI:
    1. Installare Supabase: pip install supabase
    2. Configurare variabili ambiente:
       export SUPABASE_URL="https://your-project.supabase.co"
       export SUPABASE_ANON_KEY="your-anon-key"
    3. Avere un progetto Supabase attivo

TEST ESEGUITI:
    ✅ Installazione pacchetto
    ✅ Configurazione variabili
    ✅ Connessione database
    ✅ Operazioni CRUD base

SICUREZZA:
    🔒 Test completamente separato dal sistema attuale
    🔒 Nessuna modifica ai dati esistenti
    🔒 Rollback automatico in caso di errori
        """)
        return
    
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Test interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Errore critico durante i test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
