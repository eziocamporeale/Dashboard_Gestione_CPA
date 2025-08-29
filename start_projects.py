#!/usr/bin/env python3
"""
Script principale per avviare i progetti Dashboard CPA
Gestisce l'avvio di tutte le versioni disponibili
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Stampa banner principale"""
    print("=" * 60)
    print("🚀 DASHBOARD GESTIONE CPA - PROGETTI")
    print("=" * 60)
    print("🏠 App Principale: app.py (stabile e funzionante)")
    print("📦 Progetti Alternativi: cartella progetti/")
    print("=" * 60)

def check_app_main():
    """Verifica app principale"""
    if os.path.exists("app.py"):
        print("✅ App Principale (app.py) - DISPONIBILE")
        return True
    else:
        print("❌ App Principale (app.py) - NON TROVATA")
        return False

def list_projects():
    """Lista progetti disponibili"""
    progetti_dir = "progetti"
    if not os.path.exists(progetti_dir):
        print("❌ Cartella progetti/ non trovata")
        return []
    
    projects = []
    for item in os.listdir(progetti_dir):
        item_path = os.path.join(progetti_dir, item)
        if os.path.isdir(item_path):
            # Verifica se ha un file run.py
            if os.path.exists(os.path.join(item_path, "run.py")):
                projects.append(item)
    
    return projects

def start_app_main():
    """Avvia app principale"""
    print("\n🚀 Avvio App Principale...")
    print("🌐 Porta: 8501 (default)")
    print("📋 Versione: Stabile e funzionante")
    print("=" * 40)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n🛑 App principale fermata")
    except Exception as e:
        print(f"❌ Errore avvio app principale: {e}")

def start_project(project_name):
    """Avvia progetto specifico"""
    project_path = os.path.join("progetti", project_name)
    run_script = os.path.join(project_path, "run.py")
    
    if not os.path.exists(run_script):
        print(f"❌ Script di avvio non trovato per {project_name}")
        return
    
    print(f"\n🚀 Avvio Progetto: {project_name}")
    print(f"📁 Cartella: {project_path}")
    print("=" * 40)
    
    try:
        # Cambia directory e avvia
        os.chdir(project_path)
        subprocess.run([sys.executable, "run.py"])
        os.chdir("../..")  # Torna alla root
    except KeyboardInterrupt:
        print(f"\n🛑 Progetto {project_name} fermato")
        os.chdir("../..")  # Torna alla root
    except Exception as e:
        print(f"❌ Errore avvio progetto {project_name}: {e}")
        os.chdir("../..")  # Torna alla root

def main():
    """Funzione principale"""
    print_banner()
    
    # Verifica app principale
    main_available = check_app_main()
    
    # Lista progetti
    projects = list_projects()
    
    if projects:
        print(f"\n📦 Progetti Disponibili ({len(projects)}):")
        for i, project in enumerate(projects, 1):
            print(f"   {i}. {project}")
    else:
        print("\n❌ Nessun progetto trovato")
    
    print("\n" + "=" * 60)
    print("🎯 SCELTA AZIONE:")
    print("=" * 60)
    
    if main_available:
        print("🏠 1. Avvia App Principale (app.py)")
    
    if projects:
        for i, project in enumerate(projects, 2):
            print(f"📦 {i}. Avvia Progetto: {project}")
    
    print("❌ 0. Esci")
    print("=" * 60)
    
    try:
        choice = input("🎯 Scegli opzione (0-{}): ".format(len(projects) + (1 if main_available else 0)))
        
        if choice == "0":
            print("👋 Arrivederci!")
            return
        
        choice_num = int(choice)
        
        if main_available and choice_num == 1:
            start_app_main()
        elif 2 <= choice_num <= len(projects) + 1:
            project_index = choice_num - 2
            start_project(projects[project_index])
        else:
            print("❌ Opzione non valida!")
            
    except ValueError:
        print("❌ Inserisci un numero valido!")
    except KeyboardInterrupt:
        print("\n👋 Arrivederci!")

if __name__ == "__main__":
    main()
