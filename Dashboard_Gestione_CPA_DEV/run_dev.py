#!/usr/bin/env python3
"""
Script di avvio per Dashboard CPA - PROGETTO SVILUPPO
Versione sperimentale per test e sviluppo
"""

import subprocess
import sys
import os

def main():
    """Avvia il progetto DEV"""
    print("🧪 DASHBOARD CPA - PROGETTO SVILUPPO")
    print("=" * 60)
    print("📋 Versione: Schema Raggruppato + Nuove Funzionalità")
    print("🌐 Porta: 8506 (separata dal progetto stabile)")
    print("⚠️  ATTENZIONE: Questo è un progetto di SVILUPPO!")
    print("=" * 60)
    
    # Verifica che app.py esista
    if not os.path.exists("app.py"):
        print("❌ Errore: app.py non trovato!")
        print("💡 Assicurati di essere nella cartella Dashboard_Gestione_CPA_DEV/")
        return
    
    try:
        # Avvia Streamlit su porta separata
        print("🔄 Avvio Streamlit su porta 8506...")
        print("🌐 URL: http://localhost:8506")
        print("=" * 40)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8506",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Progetto DEV fermato dall'utente")
    except Exception as e:
        print(f"❌ Errore avvio progetto DEV: {e}")

if __name__ == "__main__":
    main()
