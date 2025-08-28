#!/usr/bin/env python3
"""
Script di avvio per la Dashboard Gestione CPA
Avvia l'applicazione Streamlit con le configurazioni ottimali
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Controlla che tutte le dipendenze siano installate"""
    print("🔍 Controllo dipendenze...")
    
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'streamlit-option-menu'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MANCANTE")
    
    if missing_packages:
        print(f"\n⚠️ Pacchetti mancanti: {', '.join(missing_packages)}")
        print("Installa le dipendenze con: pip install -r requirements.txt")
        return False
    
    print("✅ Tutte le dipendenze sono installate")
    return True

def check_python_version():
    """Controlla la versione di Python"""
    print("🐍 Controllo versione Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} non supportato")
        print("Richiesto Python 3.8+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def setup_environment():
    """Configura l'ambiente per l'applicazione"""
    print("⚙️ Configurazione ambiente...")
    
    # Imposta variabili d'ambiente
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Crea directory necessarie
    base_dir = Path(__file__).parent
    exports_dir = base_dir / 'exports'
    exports_dir.mkdir(exist_ok=True)
    
    print("✅ Ambiente configurato")
    return True

def start_application():
    """Avvia l'applicazione Streamlit"""
    print("🚀 Avvio Dashboard Gestione CPA...")
    
    app_path = Path(__file__).parent / 'app.py'
    
    if not app_path.exists():
        print(f"❌ File {app_path} non trovato")
        return False
    
    try:
        # Avvia Streamlit
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            str(app_path),
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ]
        
        print(f"📱 Avvio su: http://localhost:8501")
        print("🔄 Per fermare l'applicazione, premi Ctrl+C")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Applicazione fermata dall'utente")
    except Exception as e:
        print(f"❌ Errore nell'avvio: {e}")
        return False
    
    return True

def main():
    """Funzione principale"""
    print("=" * 50)
    print("📊 Dashboard Gestione CPA - Avvio")
    print("=" * 50)
    
    # Controlli preliminari
    if not check_python_version():
        return False
    
    if not check_dependencies():
        return False
    
    if not setup_environment():
        return False
    
    # Avvia l'applicazione
    return start_application()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Errore critico: {e}")
        sys.exit(1)
