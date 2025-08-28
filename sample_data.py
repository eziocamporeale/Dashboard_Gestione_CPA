#!/usr/bin/env python3
"""
Script per inserire dati di esempio nella Dashboard Gestione CPA
Utile per testare l'applicazione con dati realistici
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Aggiungi la directory corrente al path
sys.path.append(str(Path(__file__).parent))

def create_sample_data():
    """Crea dati di esempio realistici per i broker"""
    
    # Broker popolari
    brokers = [
        "FXPro", "Pepperstone", "IC Markets", "AvaTrade", "Plus500",
        "eToro", "IG Group", "CMC Markets", "Saxo Bank", "Interactive Brokers",
        "OANDA", "Dukascopy", "FXCM", "Gain Capital", "Monex"
    ]
    
    # Piattaforme
    platforms = ["MT4", "MT5", "cTrader", "NinjaTrader", "TradingView"]
    
    # Nomi italiani
    first_names = [
        "Mario", "Giulia", "Luca", "Anna", "Marco", "Sofia", "Alessandro", "Chiara",
        "Giuseppe", "Valentina", "Roberto", "Federica", "Antonio", "Elisa", "Davide"
    ]
    
    last_names = [
        "Rossi", "Bianchi", "Verdi", "Neri", "Marroni", "Gialli", "Blu", "Viola",
        "Rosa", "Arancioni", "Grigi", "Neri", "Bianchi", "Verdi", "Rossi"
    ]
    
    # Domini email
    email_domains = [
        "gmail.com", "yahoo.it", "hotmail.com", "outlook.com", "libero.it",
        "virgilio.it", "alice.it", "tiscali.it", "fastwebnet.it", "aruba.it"
    ]
    
    # Campi aggiuntivi comuni
    custom_fields = [
        {"nome": "Telefono", "valore": "+39 123 456 789"},
        {"nome": "WhatsApp", "valore": "+39 987 654 321"},
        {"nome": "Skype", "valore": "username.skype"},
        {"nome": "Telegram", "valore": "@username_telegram"},
        {"nome": "Note", "valore": "Cliente attivo"},
        {"nome": "Referente", "valore": "Mario Rossi"},
        {"nome": "Categoria", "valore": "Premium"},
        {"nome": "Fonte", "valore": "Social Media"},
        {"nome": "Campagna", "valore": "Q4 2024"},
        {"nome": "Priorità", "valore": "Alta"}
    ]
    
    # Genera dati di esempio
    sample_data = []
    
    for i in range(25):  # 25 clienti di esempio
        # Nome casuale
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Email
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_domains)}"
        
        # Broker e piattaforma
        broker = random.choice(brokers)
        platform = random.choice(platforms)
        
        # Data registrazione (ultimi 12 mesi)
        days_ago = random.randint(0, 365)
        registration_date = datetime.now() - timedelta(days=days_ago)
        
        # Deposito (range realistico)
        deposit = random.uniform(1000, 50000)
        
        # Numero conto
        account_number = f"{random.randint(10000, 99999)}"
        
        # VPS (50% probabilità)
        has_vps = random.random() < 0.5
        vps_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}" if has_vps else ""
        vps_username = f"user{random.randint(100, 999)}" if has_vps else ""
        
        # Campi aggiuntivi (1-3 campi casuali)
        num_custom_fields = random.randint(1, 3)
        selected_custom_fields = random.sample(custom_fields, num_custom_fields)
        
        # Crea record cliente
        cliente = {
            'nome_cliente': full_name,
            'email': email,
            'password_email': f"pass{random.randint(1000, 9999)}",
            'broker': broker,
            'data_registrazione': registration_date.date(),
            'deposito': round(deposit, 2),
            'piattaforma': platform,
            'numero_conto': account_number,
            'password_conto': f"mt{random.randint(10000, 99999)}",
            'vps_ip': vps_ip,
            'vps_username': vps_username,
            'vps_password': f"vps{random.randint(1000, 9999)}" if has_vps else "",
            'campi_aggiuntivi': selected_custom_fields
        }
        
        sample_data.append(cliente)
    
    return sample_data

def insert_sample_data():
    """Inserisce i dati di esempio nel database"""
    
    try:
        from database.database import DatabaseManager
        
        print("🗄️ Connessione al database...")
        db = DatabaseManager()
        
        print("📊 Creazione dati di esempio...")
        sample_data = create_sample_data()
        
        print(f"💾 Inserimento {len(sample_data)} clienti...")
        
        success_count = 0
        error_count = 0
        
        for i, cliente in enumerate(sample_data, 1):
            try:
                # Estrai i campi aggiuntivi
                campi_aggiuntivi = cliente.pop('campi_aggiuntivi')
                
                # Inserisci il cliente
                success, result = db.aggiungi_cliente(cliente, campi_aggiuntivi)
                
                if success:
                    success_count += 1
                    print(f"✅ Cliente {i}/{len(sample_data)} inserito: {cliente['nome_cliente']}")
                else:
                    error_count += 1
                    print(f"❌ Errore inserimento cliente {i}: {result}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Errore inserimento cliente {i}: {e}")
        
        print("\n" + "=" * 50)
        print("📊 RIEPILOGO INSERIMENTO")
        print("=" * 50)
        print(f"✅ Clienti inseriti con successo: {success_count}")
        print(f"❌ Errori di inserimento: {error_count}")
        print(f"📈 Totale tentativi: {len(sample_data)}")
        
        if success_count > 0:
            # Mostra statistiche
            stats = db.ottieni_statistiche()
            print(f"\n📊 Statistiche Database:")
            print(f"   • Totale clienti: {stats['totale_clienti']}")
            print(f"   • Broker attivi: {stats['broker_attivi']}")
            print(f"   • Depositi totali: €{stats['depositi_totali']:,.2f}")
            print(f"   • CPA attive: {stats['cpa_attive']}")
        
        return success_count > 0
        
    except ImportError as e:
        print(f"❌ Errore importazione: {e}")
        print("Assicurati di essere nella directory corretta e che tutte le dipendenze siano installate")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False

def main():
    """Funzione principale"""
    print("🚀 Inserimento Dati di Esempio - Dashboard Gestione CPA")
    print("=" * 60)
    
    print("⚠️  ATTENZIONE: Questo script inserirà 25 clienti di esempio nel database")
    print("    I dati sono generati casualmente e servono solo per testare l'applicazione")
    print()
    
    # Chiedi conferma
    response = input("Procedi con l'inserimento? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes', 's', 'si']:
        print("❌ Operazione annullata")
        return False
    
    print()
    
    # Inserisci i dati
    success = insert_sample_data()
    
    if success:
        print("\n🎉 Inserimento completato con successo!")
        print("Ora puoi avviare l'applicazione e vedere i dati di esempio")
        print("\nPer avviare l'applicazione:")
        print("  python run.py")
        print("  oppure")
        print("  streamlit run app.py")
    else:
        print("\n❌ Inserimento fallito. Controlla gli errori sopra.")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Operazione interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore critico: {e}")
        sys.exit(1)
