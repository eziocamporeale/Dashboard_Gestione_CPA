#!/usr/bin/env python3
"""
🔍 CONFRONTO SUPABASE vs EXCEL
📊 Analisi delle discrepanze tra database remoto e backup locale
"""

import pandas as pd
from supabase_manager import SupabaseManager

def main():
    print("=== 🔍 CONFRONTO SUPABASE vs EXCEL ===")
    
    # 1. Connessione a Supabase
    print("\n1️⃣ Connessione a Supabase...")
    sm = SupabaseManager()
    success, message = sm.test_connection()
    print(f"   {message}")
    
    if not success:
        print("❌ Impossibile continuare senza connessione Supabase")
        return
    
    # 2. Recupero clienti da Supabase
    print("\n2️⃣ Recupero clienti da Supabase...")
    clienti_supabase = sm.get_clienti()
    df_supabase = pd.DataFrame(clienti_supabase)
    
    print(f"   ✅ Clienti in Supabase: {len(df_supabase)}")
    if not df_supabase.empty:
        print(f"   📋 Colonne disponibili: {df_supabase.columns.tolist()}")
    
    # 3. Lettura file Excel
    print("\n3️⃣ Lettura file Excel...")
    try:
        df_excel = pd.read_excel('./confronto_backup_database_20250830_103657.xlsx')
        print(f"   ✅ Righe in Excel: {len(df_excel)}")
        print(f"   📋 Colonne Excel: {df_excel.columns.tolist()}")
    except Exception as e:
        print(f"   ❌ Errore lettura Excel: {e}")
        return
    
    # 4. Analisi delle discrepanze
    print("\n4️⃣ Analisi delle discrepanze...")
    
    if not df_supabase.empty and 'id' in df_supabase.columns:
        # Filtra solo i clienti attuali (non backup)
        df_excel_attuali = df_excel[df_excel['Stato'] == 'ATTUALE']
        
        print(f"   📊 Clienti attuali in Excel: {len(df_excel_attuali)}")
        print(f"   📊 Clienti in Supabase: {len(df_supabase)}")
        
        # Confronta ID (Supabase usa UUID, Excel usa ID numerici)
        id_excel = set(df_excel_attuali['ID'].astype(int))
        id_supabase = set(df_supabase['id'])  # Mantieni UUID come stringhe
        
        # Per il confronto, usiamo email + nome + broker
        print(f"\n   🔍 ANALISI DETTAGLIATA:")
        print(f"   📊 Clienti attuali in Excel: {len(df_excel_attuali)}")
        print(f"   📊 Clienti in Supabase: {len(df_supabase)}")
        
        # Mostra clienti Excel attuali
        print(f"\n   📋 CLIENTI ATTUALI IN EXCEL:")
        for _, cliente in df_excel_attuali.iterrows():
            print(f"      ID {cliente['ID']}: {cliente['Nome Cliente']} - {cliente['Email']} - {cliente['Broker']} - €{cliente['Deposito']}")
        
        # Mostra clienti in Supabase
        print(f"\n   📋 CLIENTI IN SUPABASE:")
        for _, cliente in df_supabase.iterrows():
            print(f"      UUID {cliente['id'][:8]}...: {cliente['nome_cliente']} - {cliente['email']} - {cliente['broker']}")
        
        # Analisi per email (più affidabile)
        email_excel = set(df_excel_attuali['Email'].str.lower())
        email_supabase = set(df_supabase['email'].str.lower())
        
        email_mancanti = email_excel - email_supabase
        email_extra = email_supabase - email_excel
        email_comuni = email_excel & email_supabase
        
        print(f"\n   🔍 ANALISI PER EMAIL:")
        print(f"   📧 Email mancanti in Supabase: {len(email_mancanti)}")
        if email_mancanti:
            for email in email_mancanti:
                print(f"      {email}")
        
        print(f"   📧 Email extra in Supabase: {len(email_extra)}")
        if email_extra:
            for email in email_extra:
                print(f"      {email}")
        
        print(f"   📧 Email comuni: {len(email_comuni)}")
        if email_comuni:
            for email in email_comuni:
                print(f"      {email}")
        
        # Analisi finale
        print(f"\n   📊 RIEPILOGO:")
        print(f"   ✅ Clienti Excel attuali: {len(df_excel_attuali)}")
        print(f"   ✅ Clienti Supabase: {len(df_supabase)}")
        print(f"   🔍 Email mancanti in Supabase: {len(email_mancanti)}")
        print(f"   🔍 Email extra in Supabase: {len(email_extra)}")
        print(f"   ✅ Email comuni: {len(email_comuni)}")
        
    else:
        print("   ⚠️ Supabase non ha dati o colonna 'id' mancante")
        print("   📋 Dati Supabase disponibili:")
        if not df_supabase.empty:
            print(df_supabase.head())

if __name__ == "__main__":
    main()
