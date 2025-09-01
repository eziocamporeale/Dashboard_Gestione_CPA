#!/usr/bin/env python3
"""
🔍 VERIFICA STRUTTURA TABELLE SUPABASE - Dashboard CPA
Script per identificare la struttura esatta delle tabelle e colonne
"""

import sys
import os

# Aggiungi il path per i moduli locali
sys.path.append(os.path.join(os.path.dirname(__file__), 'progetti', 'supabase_integration'))

from supabase_manager import SupabaseManager

def print_log(message, level="INFO"):
    """Stampa log formattato su terminale"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def verify_table_structure():
    """Verifica la struttura esatta delle tabelle Supabase"""
    
    print_log("🔍 VERIFICA STRUTTURA TABELLE SUPABASE", "START")
    print_log("=" * 60)
    
    try:
        # Inizializza Supabase
        print_log("🔌 Connessione a Supabase...")
        supabase_manager = SupabaseManager()
        print_log("✅ Connessione Supabase stabilita")
        
        # Lista tabelle da verificare
        tables_to_check = [
            'users',
            'user_profiles', 
            'user_roles',
            'user_permissions',
            'user_sessions',
            'user_access_logs',
            'failed_login_attempts'
        ]
        
        for table_name in tables_to_check:
            print_log(f"🔍 Verifica tabella: {table_name}")
            print_log("-" * 40)
            
            try:
                # Prova a selezionare tutti i record
                response = supabase_manager.supabase.table(table_name).select('*').limit(1).execute()
                
                if response.data:
                    print_log(f"✅ Tabella '{table_name}' trovata e accessibile")
                    print_log(f"📊 Record di esempio:")
                    
                    # Mostra struttura del primo record
                    first_record = response.data[0]
                    for key, value in first_record.items():
                        print_log(f"   {key}: {type(value).__name__} = {value}")
                        
                else:
                    print_log(f"⚠️ Tabella '{table_name}' trovata ma vuota")
                    
            except Exception as e:
                print_log(f"❌ Errore accesso tabella '{table_name}': {e}", "ERROR")
            
            print_log("")
        
        # Verifica specifica struttura colonne
        print_log("🔍 VERIFICA STRUTTURA COLONNE SPECIFICHE")
        print_log("=" * 60)
        
        # Tabella users
        print_log("👥 Tabella 'users' - Struttura colonne:")
        try:
            response = supabase_manager.supabase.table('users').select('*').limit(1).execute()
            if response.data:
                columns = list(response.data[0].keys())
                for col in columns:
                    print_log(f"   ✅ Colonna: {col}")
            else:
                print_log("   ⚠️ Tabella vuota, non posso determinare colonne")
        except Exception as e:
            print_log(f"   ❌ Errore: {e}", "ERROR")
        
        # Tabella user_roles
        print_log("👑 Tabella 'user_roles' - Struttura colonne:")
        try:
            response = supabase_manager.supabase.table('user_roles').select('*').limit(1).execute()
            if response.data:
                columns = list(response.data[0].keys())
                for col in columns:
                    print_log(f"   ✅ Colonna: {col}")
            else:
                print_log("   ⚠️ Tabella vuota, non posso determinare colonne")
        except Exception as e:
            print_log(f"   ❌ Errore: {e}", "ERROR")
        
        # Tabella user_permissions
        print_log("🔐 Tabella 'user_permissions' - Struttura colonne:")
        try:
            response = supabase_manager.supabase.table('user_permissions').select('*').limit(1).execute()
            if response.data:
                columns = list(response.data[0].keys())
                for col in columns:
                    print_log(f"   ✅ Colonna: {col}")
            else:
                print_log("   ⚠️ Tabella vuota, non posso determinare colonne")
        except Exception as e:
            print_log(f"   ❌ Errore: {e}", "ERROR")
        
        # Test inserimento semplice per verificare RLS
        print_log("🧪 TEST INSERIMENTO SEMPLICE (verifica RLS)")
        print_log("=" * 60)
        
        # Test tabella users
        print_log("👤 Test inserimento tabella 'users':")
        try:
            test_user = {
                'username': 'test_user_temp',
                'email': 'test@temp.com',
                'full_name': 'Test User Temp',
                'role': 'user',
                'is_active': True
            }
            
            response = supabase_manager.supabase.table('users').insert(test_user).execute()
            if response.data:
                print_log("   ✅ Inserimento riuscito (RLS non attivo o policy permissiva)")
                # Rimuovi record di test
                supabase_manager.supabase.table('users').delete().eq('username', 'test_user_temp').execute()
                print_log("   🧹 Record di test rimosso")
            else:
                print_log("   ❌ Inserimento fallito")
                
        except Exception as e:
            print_log(f"   ❌ Errore inserimento: {e}", "ERROR")
        
        print_log("")
        print_log("🎯 RACCOMANDAZIONI BASATE SULLA VERIFICA:")
        print_log("=" * 60)
        
        print_log("1. 🔍 Se le colonne hanno nomi diversi, aggiorna lo script di ripristino")
        print_log("2. 🔒 Se RLS blocca inserimenti, correggi le policies")
        print_log("3. 🔄 Riprova il ripristino con struttura corretta")
        
    except Exception as e:
        print_log(f"❌ Errore generale: {e}", "ERROR")
        import traceback
        print_log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")

if __name__ == "__main__":
    print_log("🚀 AVVIO VERIFICA STRUTTURA TABELLE", "START")
    verify_table_structure()
    print_log("🏁 VERIFICA COMPLETATA", "END")
