#!/usr/bin/env python3
"""
Script di test per la Dashboard Gestione CPA
Verifica che tutti i componenti funzionino correttamente
"""

import sys
import os
import sqlite3
from pathlib import Path

# Aggiungi la directory corrente al path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Testa l'importazione di tutti i moduli"""
    print("🧪 Test importazione moduli...")
    
    try:
        from database.database import DatabaseManager
        print("✅ DatabaseManager importato correttamente")
    except ImportError as e:
        print(f"❌ Errore import DatabaseManager: {e}")
        return False
    
    try:
        from components.client_form import ClientForm
        print("✅ ClientForm importato correttamente")
    except ImportError as e:
        print(f"❌ Errore import ClientForm: {e}")
        return False
    
    try:
        from components.client_table import ClientTable
        print("✅ ClientTable importato correttamente")
    except ImportError as e:
        print(f"❌ Errore import ClientTable: {e}")
        return False
    
    try:
        from components.charts import Charts
        print("✅ Charts importato correttamente")
    except ImportError as e:
        print(f"❌ Errore import Charts: {e}")
        return False
    
    try:
        from utils.helpers import validate_email, validate_ip, format_currency, create_sample_data, get_broker_suggestions
        print("✅ Helpers importati correttamente")
    except ImportError as e:
        print(f"❌ Errore import Helpers: {e}")
        return False
    
    try:
        from config import Config
        print("✅ Config importato correttamente")
    except ImportError as e:
        print(f"❌ Errore import Config: {e}")
        return False
    
    return True

def test_database():
    """Testa la creazione e gestione del database"""
    print("\n🗄️ Test database...")
    
    try:
        from database.database import DatabaseManager
        
        # Crea un database temporaneo per i test
        db = DatabaseManager("test_database.db")
        print("✅ Database creato correttamente")
        
        # Test inserimento cliente
        dati_cliente = {
            'nome_cliente': 'Test Cliente',
            'email': 'test@example.com',
            'password_email': 'REMOVED_FOR_SECURITY',
            'broker': 'Test Broker',
            'data_registrazione': '2024-01-01',
            'deposito': 1000.0,
            'piattaforma': 'MT4',
            'numero_conto': '12345',
            'password_conto': 'pass123',
            'vps_ip': '192.168.1.1',
            'vps_username': 'testuser',
            'vps_password': 'vpspass'
        }
        
        campi_aggiuntivi = [
            {'nome': 'Telefono', 'valore': '+39 123 456 789'},
            {'nome': 'Note', 'valore': 'Cliente di test'}
        ]
        
        success, cliente_id = db.aggiungi_cliente(dati_cliente, campi_aggiuntivi)
        
        if success:
            print(f"✅ Cliente inserito con ID: {cliente_id}")
        else:
            print(f"❌ Errore inserimento cliente: {cliente_id}")
            return False
        
        # Test recupero clienti
        df_clienti = db.ottieni_tutti_clienti()
        if not df_clienti.empty:
            print(f"✅ Clienti recuperati: {len(df_clienti)}")
        else:
            print("❌ Nessun cliente recuperato")
            return False
        
        # Test statistiche
        stats = db.ottieni_statistiche()
        if stats['totale_clienti'] > 0:
            print(f"✅ Statistiche recuperate: {stats}")
        else:
            print("❌ Statistiche non recuperate")
            return False
        
        # Test modifica cliente
        dati_cliente['deposito'] = 2000.0
        success = db.modifica_cliente(cliente_id, dati_cliente, campi_aggiuntivi)
        
        if success:
            print("✅ Cliente modificato correttamente")
        else:
            print("❌ Errore modifica cliente")
            return False
        
        # Test eliminazione cliente
        success = db.elimina_cliente(cliente_id)
        
        if success:
            print("✅ Cliente eliminato correttamente")
        else:
            print("❌ Errore eliminazione cliente")
            return False
        
        # Rimuovi il database di test
        try:
            os.remove("test_database.db")
            print("✅ Database di test rimosso")
        except:
            print("⚠️ Impossibile rimuovere database di test")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test database: {e}")
        return False

def test_helpers():
    """Testa le funzioni helper"""
    print("\n🔧 Test funzioni helper...")
    
    try:
        from utils.helpers import validate_email, validate_ip, format_currency, create_sample_data
        
        # Test validazione email
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False
        print("✅ Validazione email funziona")
        
        # Test validazione IP
        assert validate_ip("192.168.1.1") == True
        assert validate_ip("256.256.256.256") == False
        print("✅ Validazione IP funziona")
        
        # Test formattazione valuta
        assert format_currency(1000.50) == "€1,000.50"
        assert format_currency(0) == "€0.00"
        print("✅ Formattazione valuta funziona")
        
        # Test suggerimenti broker
        broker_suggestions = get_broker_suggestions()
        assert len(broker_suggestions) > 0
        print("✅ Suggerimenti broker funzionano")
        
        # Test creazione dati di esempio
        sample_data = create_sample_data()
        assert not sample_data.empty
        print("✅ Dati di esempio creati correttamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test helpers: {e}")
        return False

def test_config():
    """Testa la configurazione"""
    print("\n⚙️ Test configurazione...")
    
    try:
        from config import Config
        
        # Test creazione directory
        Config.create_directories()
        print("✅ Directory create correttamente")
        
        # Test informazioni applicazione
        app_info = Config.get_app_info()
        assert 'title' in app_info
        assert 'version' in app_info
        print("✅ Informazioni applicazione recuperate")
        
        # Test percorso database
        db_url = Config.get_database_url()
        assert 'sqlite' in db_url
        print("✅ URL database generato correttamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test configurazione: {e}")
        return False

def main():
    """Funzione principale per eseguire tutti i test"""
    print("🚀 Avvio test Dashboard Gestione CPA...")
    print("=" * 50)
    
    tests = [
        ("Importazione moduli", test_imports),
        ("Database", test_database),
        ("Funzioni helper", test_helpers),
        ("Configurazione", test_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Errore durante il test {test_name}: {e}")
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
    
    print(f"\nRisultato: {passed}/{total} test superati")
    
    if passed == total:
        print("🎉 Tutti i test sono stati superati! L'applicazione è pronta.")
        return True
    else:
        print("⚠️ Alcuni test sono falliti. Controlla gli errori sopra.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
