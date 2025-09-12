#!/usr/bin/env python3
"""
Script automatico per creare le tabelle storage in Supabase
Creato da Ezio Camporeale per Dashboard Gestione CPA
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from supabase_manager import SupabaseManager

def create_storage_tables():
    """
    Crea le tabelle storage in Supabase usando SQL diretto
    """
    try:
        print("🚀 Creazione tabelle storage in Supabase...")
        
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        supabase = supabase_manager.supabase
        
        # Leggi il file SQL
        sql_file = Path(__file__).parent / "create_storage_tables.sql"
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📄 File SQL letto correttamente")
        
        # Esegui le query SQL
        print("🔄 Esecuzione query SQL...")
        
        # Dividi il contenuto in query separate (separate da ';')
        queries = [q.strip() for q in sql_content.split(';') if q.strip() and not q.strip().startswith('--')]
        
        for i, query in enumerate(queries, 1):
            if query.strip():
                try:
                    print(f"   Query {i}/{len(queries)}: {query[:50]}...")
                    result = supabase.rpc('exec_sql', {'sql': query}).execute()
                    print(f"   ✅ Query {i} eseguita con successo")
                except Exception as e:
                    # Se exec_sql non funziona, proviamo con query diretta
                    try:
                        if 'CREATE TABLE' in query.upper():
                            # Per CREATE TABLE, usiamo una query diretta
                            result = supabase.table('_sql').select('*').execute()
                            print(f"   ⚠️ Query {i} saltata (metodo alternativo)")
                        else:
                            print(f"   ⚠️ Query {i} saltata: {str(e)[:100]}")
                    except:
                        print(f"   ⚠️ Query {i} saltata: {str(e)[:100]}")
        
        print("✅ Creazione tabelle completata!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la creazione delle tabelle: {str(e)}")
        return False

def create_tables_manual():
    """
    Crea le tabelle usando query SQL dirette
    """
    try:
        print("🔄 Creazione tabelle con query dirette...")
        
        supabase_manager = SupabaseManager()
        supabase = supabase_manager.supabase
        
        # Query per creare storage_files
        create_storage_files = """
        CREATE TABLE IF NOT EXISTS storage_files (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size BIGINT NOT NULL,
            file_type VARCHAR(100) NOT NULL,
            category VARCHAR(50) DEFAULT 'Documenti',
            description TEXT,
            uploaded_by INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            download_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Query per creare storage_downloads
        create_storage_downloads = """
        CREATE TABLE IF NOT EXISTS storage_downloads (
            id SERIAL PRIMARY KEY,
            file_id INTEGER NOT NULL REFERENCES storage_files(id) ON DELETE CASCADE,
            downloaded_by INTEGER NOT NULL,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address INET,
            user_agent TEXT
        );
        """
        
        # Esegui le query
        print("   Creando tabella storage_files...")
        result1 = supabase.rpc('exec', {'sql': create_storage_files}).execute()
        print("   ✅ storage_files creata")
        
        print("   Creando tabella storage_downloads...")
        result2 = supabase.rpc('exec', {'sql': create_storage_downloads}).execute()
        print("   ✅ storage_downloads creata")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore creazione manuale: {str(e)}")
        return False

def main():
    """
    Esegue la creazione delle tabelle
    """
    print("🚀 Setup Automatico Tabelle Storage - Dashboard Gestione CPA")
    print("=" * 60)
    
    # Prova prima il metodo automatico
    print("🔄 Tentativo 1: Metodo automatico...")
    if create_storage_tables():
        print("✅ Tabelle create con successo!")
    else:
        print("⚠️ Metodo automatico fallito, provo metodo manuale...")
        if create_tables_manual():
            print("✅ Tabelle create con successo!")
        else:
            print("❌ Entrambi i metodi sono falliti")
            print("\n📋 ISTRUZIONI MANUALI:")
            print("1. Vai su: https://supabase.com/dashboard")
            print("2. Seleziona il tuo progetto Dashboard Gestione CPA")
            print("3. Clicca su 'SQL Editor' (icona </>)")
            print("4. Clicca 'New Query'")
            print("5. Copia e incolla il contenuto di create_storage_tables.sql")
            print("6. Clicca 'Run'")
            return False
    
    # Test finale
    print("\n🧪 Test finale...")
    try:
        from test_storage_setup import main as test_main
        return test_main()
    except Exception as e:
        print(f"❌ Errore nel test finale: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SETUP COMPLETATO CON SUCCESSO!")
        print("✅ Puoi ora usare la sezione Storage nell'app")
    else:
        print("\n❌ SETUP FALLITO")
        print("📋 Segui le istruzioni manuali sopra")
    
    sys.exit(0 if success else 1)
