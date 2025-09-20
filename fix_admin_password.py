#!/usr/bin/env python3
"""
Script per correggere la password admin nel database Supabase
Aggiorna la password admin per corrispondere a 'admin123'
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import bcrypt
from supabase_manager import SupabaseManager
from datetime import datetime

def fix_admin_password():
    """Corregge la password admin nel database Supabase"""
    
    print("🔧 Correzione Password Admin")
    print("=" * 50)
    
    try:
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        supabase = supabase_manager.supabase
        
        if not supabase:
            print("❌ Errore: Supabase non configurato")
            return False
        
        # Password admin corretta
        admin_password = "admin123"
        
        # Hash della password con bcrypt
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        print(f"✅ Password admin: {admin_password}")
        print(f"✅ Hash generato: {password_hash[:30]}...")
        
        # Aggiorna la password nel database
        response = supabase.table('users').update({
            'password_hash': password_hash,
            'updated_at': datetime.now().isoformat()
        }).eq('username', 'admin').execute()
        
        if response.data:
            print("✅ Password admin aggiornata con successo!")
            print(f"✅ Utente aggiornato: {response.data[0]['username']}")
            
            # Verifica che la password funzioni
            print("\n🧪 Test Verifica Password")
            test_hash = response.data[0]['password_hash']
            test_valid = bcrypt.checkpw(admin_password.encode('utf-8'), test_hash.encode('utf-8'))
            print(f"✅ Verifica password: {test_valid}")
            
            if test_valid:
                print("\n🎉 Password admin corretta!")
                print("💡 Ora puoi:")
                print("   • Fare login con username: admin, password: admin123")
                print("   • Cambiare la password da entrambe le sezioni")
                return True
            else:
                print("❌ Errore nella verifica password")
                return False
        else:
            print("❌ Errore nell'aggiornamento della password")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante la correzione: {e}")
        return False

def verify_admin_password():
    """Verifica la password admin corrente"""
    
    print("\n🔍 Verifica Password Admin Corrente")
    print("=" * 50)
    
    try:
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        supabase = supabase_manager.supabase
        
        if not supabase:
            print("❌ Errore: Supabase non configurato")
            return False
        
        # Recupera l'utente admin
        response = supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if response.data:
            admin_data = response.data[0]
            current_hash = admin_data['password_hash']
            
            print(f"✅ Username: {admin_data['username']}")
            print(f"✅ Email: {admin_data['email']}")
            print(f"✅ Hash corrente: {current_hash[:30]}...")
            
            # Test con password admin123
            admin_password = "admin123"
            is_valid = bcrypt.checkpw(admin_password.encode('utf-8'), current_hash.encode('utf-8'))
            
            print(f"✅ Password 'admin123' valida: {is_valid}")
            
            if is_valid:
                print("✅ La password admin è già corretta!")
                return True
            else:
                print("❌ La password admin non corrisponde a 'admin123'")
                return False
        else:
            print("❌ Utente admin non trovato nel database")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante la verifica: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Avvio Correzione Password Admin")
    
    # Prima verifica lo stato corrente
    current_valid = verify_admin_password()
    
    if not current_valid:
        print("\n🔧 Correzione necessaria...")
        fix_result = fix_admin_password()
        
        if fix_result:
            print("\n✅ CORREZIONE COMPLETATA!")
        else:
            print("\n❌ CORREZIONE FALLITA!")
    else:
        print("\n✅ Password admin già corretta!")
    
    print("\n" + "=" * 60)
