#!/usr/bin/env python3
"""
Script di avvio per App Unificata - Dashboard CPA
Versione avanzata con schema raggruppato e broker predefiniti
"""

import subprocess
import sys
import os

def main():
    """Avvia l'app unificata"""
    print("🚀 Avvio App Unificata - Dashboard CPA")
    print("=" * 50)
    print("📋 Versione: Schema Raggruppato + Broker Predefiniti")
    print("🌐 Porta: 8503")
    print("=" * 50)
    
    # Verifica che app.py esista
    if not os.path.exists("app.py"):
        print("❌ Errore: app.py non trovato!")
        print("💡 Assicurati di essere nella cartella progetti/app_unified/")
        return
    
    try:
        # Avvia Streamlit
        print("🔄 Avvio Streamlit...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8503",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 App fermata dall'utente")
    except Exception as e:
        print(f"❌ Errore avvio: {e}")

if __name__ == "__main__":
    main()
