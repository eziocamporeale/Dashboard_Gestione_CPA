#!/usr/bin/env python3
"""
Script di avvio per App Grouped - Dashboard CPA
Versione con schema raggruppato
"""

import subprocess
import sys
import os

def main():
    """Avvia l'app grouped"""
    print("📊 Avvio App Grouped - Dashboard CPA")
    print("=" * 50)
    print("📋 Versione: Schema Raggruppato")
    print("🌐 Porta: 8505")
    print("=" * 50)
    
    # Verifica che app_grouped.py esista
    if not os.path.exists("app_grouped.py"):
        print("❌ Errore: app_grouped.py non trovato!")
        print("💡 Assicurati di essere nella cartella progetti/app_grouped/")
        return
    
    try:
        # Avvia Streamlit
        print("🔄 Avvio Streamlit...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_grouped.py",
            "--server.port", "8505",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 App fermata dall'utente")
    except Exception as e:
        print(f"❌ Errore avvio: {e}")

if __name__ == "__main__":
    main()
