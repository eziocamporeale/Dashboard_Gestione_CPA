#!/usr/bin/env python3
"""
Test script per ClientTable con Supabase
"""

from components.client_table import ClientTable

def test_client_table():
    print("=== 🧪 TEST CLIENTTABLE CON SUPABASE ===")
    
    try:
        # 1. Crea ClientTable
        ct = ClientTable()
        print("✅ ClientTable creato")
        
        # 2. Recupera clienti da Supabase
        clienti = ct.get_clienti()
        print(f"✅ Clienti recuperati da Supabase: {len(clienti)}")
        
        # 3. Mostra primi 3 clienti
        print("📋 Primi 3 clienti:")
        for i in range(min(3, len(clienti))):
            nome = clienti.iloc[i]['nome_cliente']
            email = clienti.iloc[i]['email']
            broker = clienti.iloc[i]['broker']
            print(f"  - {nome} ({email}) - {broker}")
        
        # 4. Verifica colonne
        print(f"📊 Colonne disponibili: {list(clienti.columns)}")
        
        print("🎉 ClientTable funziona perfettamente con Supabase!")
        return True
        
    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        return False

if __name__ == "__main__":
    test_client_table()
