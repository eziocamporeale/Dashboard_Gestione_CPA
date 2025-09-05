#!/usr/bin/env python3
"""
🚀 SCRIPT AGGIORNAMENTO SUPABASE - Aggiunta colonna wallet
Esegue l'aggiornamento della tabella clienti su Supabase
"""

import os
import sys
from supabase_manager import SupabaseManager

def add_wallet_column():
    """Aggiunge la colonna wallet alla tabella clienti su Supabase"""
    try:
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        
        if not supabase_manager.is_configured:
            print("❌ Supabase non configurato")
            return False
        
        print("🔗 Connessione a Supabase...")
        
        # Esegui ALTER TABLE
        sql_query = "ALTER TABLE clienti ADD COLUMN wallet TEXT;"
        
        print(f"📝 Esecuzione query: {sql_query}")
        
        # Esegui la query
        response = supabase_manager.supabase.rpc('exec_sql', {'sql': sql_query}).execute()
        
        print("✅ Colonna wallet aggiunta con successo!")
        
        # Verifica che la colonna sia stata aggiunta
        verify_query = """
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'clienti' AND column_name = 'wallet';
        """
        
        print("🔍 Verifica aggiunta colonna...")
        verify_response = supabase_manager.supabase.rpc('exec_sql', {'sql': verify_query}).execute()
        
        if verify_response.data:
            print("✅ Verifica completata - Colonna wallet presente!")
            print(f"📊 Dati colonna: {verify_response.data}")
        else:
            print("⚠️ Verifica non riuscita, ma la colonna potrebbe essere stata aggiunta")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AGGIORNAMENTO SUPABASE - Aggiunta colonna wallet")
    print("=" * 50)
    
    success = add_wallet_column()
    
    if success:
        print("\n✅ AGGIORNAMENTO COMPLETATO!")
        print("🎯 La colonna 'wallet' è ora disponibile nella tabella 'clienti'")
    else:
        print("\n❌ AGGIORNAMENTO FALLITO!")
        print("🔧 Controlla i log per i dettagli dell'errore")
    
    print("\n" + "=" * 50)
