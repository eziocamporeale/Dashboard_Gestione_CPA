#!/usr/bin/env python3
"""
Script di avvio per App Hybrid - Dashboard CPA
Versione ibrida che supporta entrambi gli schemi
"""

import subprocess
import sys
import os

def main():
    """Avvia l'app hybrid"""
    print("🔄 Avvio App Hybrid - Dashboard CPA")
    print("=" * 50)
    print("📋 Versione: Schema Originale + Schema Raggruppato")
    print("🌐 Porta: 8504")
    print("=" * 50)
    
    # Verifica che app_hybrid.py esista
    if not os.path.exists("app_hybrid.py"):
        print("❌ Errore: app_hybrid.py non trovato!")
        print("💡 Assicurati di essere nella cartella progetti/app_hybrid/")
        return
    
    try:
        # Avvia Streamlit
        print("🔄 Avvio Streamlit...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_hybrid.py",
            "--server.port", "8504",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 App fermata dall'utente")
    except Exception as e:
        print(f"❌ Errore avvio: {e}")

if __name__ == "__main__":
    main()
