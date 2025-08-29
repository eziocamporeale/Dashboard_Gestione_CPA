import time
import threading
import logging
from datetime import datetime, timedelta
import subprocess
import os
from pathlib import Path

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class AutoSyncManager:
    """
    Gestore per la sincronizzazione automatica del database
    """
    
    def __init__(self, sync_interval_minutes=5, backup_interval_minutes=10):
        self.sync_interval = sync_interval_minutes * 60  # Converti in secondi
        self.backup_interval = backup_interval_minutes * 60
        self.running = False
        self.thread = None
        
        # Percorsi
        self.repo_path = Path.cwd()
        self.database_path = self.repo_path / "cpa_database.db"
        self.sync_path = self.repo_path / "database_sync"
        
        # Crea cartella sync se non esiste
        self.sync_path.mkdir(exist_ok=True)
        
        logging.info(f"AutoSyncManager inizializzato - Sync ogni {sync_interval_minutes} min, Backup ogni {backup_interval_minutes} min")
    
    def start_auto_sync(self):
        """Avvia la sincronizzazione automatica in background"""
        if self.running:
            logging.warning("AutoSync già attivo")
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
        self.thread.start()
        logging.info("AutoSync avviato in background")
        return True
    
    def stop_auto_sync(self):
        """Ferma la sincronizzazione automatica"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logging.info("AutoSync fermato")
    
    def _auto_sync_loop(self):
        """Loop principale per la sincronizzazione automatica"""
        last_sync = time.time()
        last_backup = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Sincronizzazione automatica
            if current_time - last_sync >= self.sync_interval:
                try:
                    self._perform_auto_sync()
                    last_sync = current_time
                except Exception as e:
                    logging.error(f"Errore durante sync automatico: {e}")
            
            # Backup automatico
            if current_time - last_backup >= self.backup_interval:
                try:
                    self._perform_auto_backup()
                    last_backup = current_time
                except Exception as e:
                    logging.error(f"Errore durante backup automatico: {e}")
            
            # Pausa per evitare loop troppo veloci
            time.sleep(30)  # Controlla ogni 30 secondi
    
    def _perform_auto_sync(self):
        """Esegue la sincronizzazione automatica"""
        try:
            # Importa qui per evitare problemi di import circolare
            from .database_sync import DatabaseSyncManager
            from config.autosave_config import get_autosave_config
            
            sync_manager = DatabaseSyncManager()
            success, message = sync_manager.sync_to_repository()
            
            if success:
                logging.info(f"✅ Sync automatico completato: {message}")
                
                # Push automatico su GitHub (opzionale)
                self._auto_push_to_github()
            else:
                logging.warning(f"⚠️ Sync automatico fallito: {message}")
                
        except Exception as e:
            logging.error(f"❌ Errore durante sync automatico: {e}")
    
    def _perform_auto_backup(self):
        """Esegue il backup automatico"""
        try:
            from .backup import DatabaseBackupManager
            
            backup_manager = DatabaseBackupManager()
            success, message = backup_manager.create_backup("auto_backup")
            
            if success:
                logging.info(f"✅ Backup automatico completato: {message}")
            else:
                logging.warning(f"⚠️ Backup automatico fallito: {message}")
                
        except Exception as e:
            logging.error(f"❌ Errore durante backup automatico: {e}")
    
    def _auto_push_to_github(self):
        """Esegue il push automatico su GitHub"""
        try:
            # Verifica se Git è configurato correttamente
            git_config = subprocess.run(
                ["git", "config", "--get", "user.email"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if git_config.returncode != 0 or not git_config.stdout.strip():
                logging.warning("⚠️ Git non configurato, salto push automatico (solo sync locale)")
                return
            
            # Verifica se ci sono modifiche
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if result.stdout.strip():  # Ci sono modifiche
                logging.info("🔄 Modifiche rilevate, eseguo push automatico...")
                
                # Add e commit
                subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"Auto-sync database {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                    cwd=self.repo_path,
                    check=True
                )
                
                # Push
                subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_path, check=True)
                logging.info("✅ Push automatico completato")
                
            else:
                logging.info("ℹ️ Nessuna modifica da pushare")
                
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Errore durante push automatico: {e}")
        except Exception as e:
            logging.error(f"❌ Errore imprevisto durante push: {e}")
    
    def get_status(self):
        """Restituisce lo stato attuale dell'AutoSync"""
        return {
            "running": self.running,
            "sync_interval_minutes": self.sync_interval // 60,
            "backup_interval_minutes": self.backup_interval // 60,
            "last_sync": getattr(self, '_last_sync_time', 'Mai'),
            "last_backup": getattr(self, '_last_backup_time', 'Mai')
        }

# Funzioni di utilità per l'integrazione con Streamlit
def start_auto_sync(sync_interval_minutes=5, backup_interval_minutes=10):
    """Avvia la sincronizzazione automatica"""
    manager = AutoSyncManager(sync_interval_minutes, backup_interval_minutes)
    return manager.start_auto_sync()

def stop_auto_sync():
    """Ferma la sincronizzazione automatica"""
    # Nota: questa è una implementazione semplificata
    # In un sistema reale, dovresti gestire l'istanza del manager
    logging.info("AutoSync fermato")

def get_auto_sync_status():
    """Restituisce lo stato dell'AutoSync"""
    # Nota: questa è una implementazione semplificata
    return {
        "running": False,  # Per ora sempre False
        "sync_interval_minutes": 5,
        "backup_interval_minutes": 10
    }
