#!/usr/bin/env python3
"""
Script per inserire dati di esempio per gli incroci CPA
"""

from database.incroci_manager import IncrociManager
from database.database import DatabaseManager
from datetime import date, datetime
import os

def create_sample_incroci():
    """Crea incroci di esempio per testare la funzionalità"""
    
    # Inizializza i manager
    db_path = "./data/cpa_dashboard.db"
    db = DatabaseManager(db_path)
    incroci_mgr = IncrociManager(db_path)
    
    print("🚀 Creazione incroci di esempio...")
    
    # Verifica che ci siano clienti nel database
    clienti_df = db.ottieni_tutti_clienti()
    if clienti_df.empty:
        print("❌ Nessun cliente presente nel database. Crea prima alcuni clienti!")
        return
    
    print(f"✅ Trovati {len(clienti_df)} clienti nel database")
    
    # Crea incroci di esempio
    incroci_esempio = [
        {
            'nome_incrocio': 'Incrocio EURUSD Gennaio 2024',
            'data_apertura': date(2024, 1, 15),
            'pair_trading': 'EUR/USD',
            'volume_trading': 2.0,
            'note': 'Incrocio per sbloccare welcome bonus su FXPro e Pepperstone',
            'account_long_id': clienti_df.iloc[0]['id'] if len(clienti_df) > 0 else 1,
            'broker_long': 'FXPro',
            'piattaforma_long': 'MT5',
            'conto_long': '12345678',
            'volume_long': 2.0,
            'account_short_id': clienti_df.iloc[1]['id'] if len(clienti_df) > 1 else 2,
            'broker_short': 'Pepperstone',
            'piattaforma_short': 'MT4',
            'conto_short': '87654321',
            'volume_short': 2.0,
            'bonus': [
                {
                    'tipo': 'Welcome Bonus',
                    'importo': 200.0,
                    'valuta': 'USD',
                    'data_sblocco': date(2024, 1, 15)
                }
            ]
        }
    ]
    
    # Inserisci gli incroci
    incroci_creati = 0
    for incrocio in incroci_esempio:
        try:
            success, incrocio_id = incroci_mgr.crea_incrocio(incrocio)
            if success:
                print(f"✅ Incrocio creato: {incrocio['nome_incrocio']} (ID: {incrocio_id})")
                incroci_creati += 1
            else:
                print(f"❌ Errore creazione incrocio: {incrocio['nome_incrocio']}")
        except Exception as e:
            print(f"❌ Errore creazione incrocio: {e}")
    
    print(f"\n🎉 Creazione completata! {incroci_creati} incroci creati con successo.")

if __name__ == "__main__":
    create_sample_incroci()
