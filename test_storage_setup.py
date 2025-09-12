#!/usr/bin/env python3
"""
Script di test per verificare il setup dello storage
Creato da Ezio Camporeale per Dashboard Gestione CPA
"""

import sys
from pathlib import Path
from supabase import create_client, Client

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from supabase_manager import SupabaseManager

def test_database_connection():
    """
    Testa la connessione al database
    """
    try:
        print("🔄 Test connessione database...")
        supabase_manager = SupabaseManager()
        supabase = supabase_manager.supabase
        
        # Test connessione base
        result = supabase.table('users').select('id').limit(1).execute()
        print("✅ Connessione database OK")
        return True, supabase
        
    except Exception as e:
        print(f"❌ Errore connessione database: {str(e)}")
        return False, None

def test_storage_tables(supabase: Client):
    """
    Testa se le tabelle storage esistono
    """
    try:
        print("\n🔍 Test esistenza tabelle storage...")
        
        # Test tabella storage_files
        try:
            result = supabase.table('storage_files').select('id').limit(1).execute()
            print("✅ Tabella 'storage_files' trovata")
            storage_files_ok = True
        except Exception as e:
            print(f"❌ Tabella 'storage_files' non trovata: {str(e)}")
            storage_files_ok = False
        
        # Test tabella storage_downloads
        try:
            result = supabase.table('storage_downloads').select('id').limit(1).execute()
            print("✅ Tabella 'storage_downloads' trovata")
            storage_downloads_ok = True
        except Exception as e:
            print(f"❌ Tabella 'storage_downloads' non trovata: {str(e)}")
            storage_downloads_ok = False
        
        return storage_files_ok and storage_downloads_ok
        
    except Exception as e:
        print(f"❌ Errore test tabelle: {str(e)}")
        return False

def test_storage_manager():
    """
    Testa il StorageManager
    """
    try:
        print("\n🧪 Test StorageManager...")
        
        from components.storage.storage_manager import StorageManager
        
        # Inizializza il manager
        storage_manager = StorageManager()
        print("✅ StorageManager inizializzato")
        
        # Test categorie
        categories = list(storage_manager.categories.keys())
        print(f"✅ Categorie supportate: {len(categories)}")
        for cat in categories:
            print(f"   - {cat}")
        
        # Test statistiche
        stats = storage_manager.get_storage_stats()
        print(f"✅ Statistiche recuperate: {stats['total_files']} file")
        
        # Test formattazione dimensioni
        test_sizes = [0, 1024, 1048576, 1073741824]
        for size in test_sizes:
            formatted = storage_manager.format_file_size(size)
            print(f"   {size} bytes = {formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore StorageManager: {str(e)}")
        return False

def test_storage_ui():
    """
    Testa i componenti UI dello storage
    """
    try:
        print("\n🎨 Test componenti UI...")
        
        from components.storage.storage_ui import render_storage_wrapper
        print("✅ Componente render_storage_wrapper importato")
        
        from components.storage.storage_manager import StorageManager
        storage_manager = StorageManager()
        
        # Test che le funzioni non lancino errori
        files = storage_manager.get_files()
        print(f"✅ get_files() funziona: {len(files)} file trovati")
        
        stats = storage_manager.get_storage_stats()
        print(f"✅ get_storage_stats() funziona: {stats['total_files']} file totali")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore componenti UI: {str(e)}")
        return False

def test_file_operations():
    """
    Testa le operazioni sui file
    """
    try:
        print("\n📁 Test operazioni file...")
        
        from components.storage.storage_manager import StorageManager
        storage_manager = StorageManager()
        
        # Test generazione nome file univoco
        test_filename = "test_file.pdf"
        unique_name = storage_manager.generate_unique_filename(test_filename)
        print(f"✅ Generazione nome univoco: {test_filename} -> {unique_name}")
        
        # Test categoria file
        test_files = [
            "Gold_Supreme_EA_v2.0.ex4",
            "backtest_report_2024.pdf", 
            "broker_contract.pdf",
            "cpa_report_monthly.xlsx",
            "marketing_video.mp4"
        ]
        
        for filename in test_files:
            category = storage_manager.get_file_category(filename)
            print(f"   {filename} -> {category}")
        
        # Test formattazione dimensioni
        test_sizes = [0, 1024, 1048576, 1073741824, 1099511627776]
        for size in test_sizes:
            formatted = storage_manager.format_file_size(size)
            print(f"   {size} bytes -> {formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore operazioni file: {str(e)}")
        return False

def test_storage_directories():
    """
    Testa che le directory storage esistano
    """
    try:
        print("\n📂 Test directory storage...")
        
        from components.storage.storage_manager import StorageManager
        storage_manager = StorageManager()
        
        # Test directory uploads
        if storage_manager.storage_dir.exists():
            print(f"✅ Directory uploads: {storage_manager.storage_dir}")
        else:
            print(f"❌ Directory uploads non trovata: {storage_manager.storage_dir}")
            return False
        
        # Test directory temp
        if storage_manager.temp_dir.exists():
            print(f"✅ Directory temp: {storage_manager.temp_dir}")
        else:
            print(f"❌ Directory temp non trovata: {storage_manager.temp_dir}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Errore directory storage: {str(e)}")
        return False

def main():
    """
    Esegue tutti i test
    """
    print("🚀 Test Setup Storage - Dashboard Gestione CPA")
    print("=" * 60)
    
    # Test connessione database
    db_ok, supabase = test_database_connection()
    if not db_ok:
        print("\n❌ Setup fallito: impossibile connettersi al database")
        return False
    
    # Test tabelle storage
    tables_ok = test_storage_tables(supabase)
    if not tables_ok:
        print("\n❌ Setup fallito: tabelle storage non trovate")
        print("   Esegui prima il setup manuale seguendo le istruzioni in create_storage_tables.sql")
        return False
    
    # Test directory storage
    dirs_ok = test_storage_directories()
    if not dirs_ok:
        print("\n❌ Setup fallito: directory storage non trovate")
        return False
    
    # Test StorageManager
    manager_ok = test_storage_manager()
    if not manager_ok:
        print("\n❌ Setup fallito: StorageManager non funziona")
        return False
    
    # Test componenti UI
    ui_ok = test_storage_ui()
    if not ui_ok:
        print("\n❌ Setup fallito: componenti UI non funzionano")
        return False
    
    # Test operazioni file
    file_ops_ok = test_file_operations()
    if not file_ops_ok:
        print("\n❌ Setup fallito: operazioni file non funzionano")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 TUTTI I TEST SUPERATI!")
    print("✅ Storage setup completato con successo")
    print("✅ Puoi ora usare la sezione Storage nell'app")
    print("\n🚀 Per avviare l'app:")
    print("   streamlit run app.py")
    print("\n📋 Categorie CPA supportate:")
    print("   • EA Trading (ex4, ex5, mq4, mq5)")
    print("   • Backtest (risultati e report)")
    print("   • Documenti Broker (contratti, certificati)")
    print("   • Report CPA (mensili, trimestrali)")
    print("   • Documenti Legali (privacy, termini)")
    print("   • Materiale Marketing (video, presentazioni)")
    print("   • Analisi (grafici, studi)")
    print("   • E molte altre...")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
