#!/usr/bin/env python3
"""
Sistema di sincronizzazione automatica del database con GitHub
Mantiene i dati permanenti anche dopo riavvii di Streamlit Cloud
"""

import sqlite3
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import logging

class DatabaseSyncManager:
    def __init__(self, db_path="cpa_database.db", sync_dir="database_sync"):
        """Inizializza il gestore di sincronizzazione"""
        self.db_path = db_path
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(exist_ok=True)
        
        # Configura logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
    
    def sync_to_repository(self):
        """Sincronizza il database corrente nel repository per persistenza"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sync_filename = f"cpa_database_sync_{timestamp}.db"
            sync_path = self.sync_dir / sync_filename
            
            # Verifica che il database sorgente esista
            if not os.path.exists(self.db_path):
                self.logger.error(f"Database sorgente non trovato: {self.db_path}")
                return False, "Database sorgente non trovato"
            
            # Copia il database corrente
            shutil.copy2(self.db_path, sync_path)
            
            # Crea metadati della sincronizzazione
            self._create_sync_metadata(sync_path, timestamp)
            
            # Mantieni solo gli ultimi 5 file di sync
            self._cleanup_old_sync_files()
            
            self.logger.info(f"Sincronizzazione completata: {sync_path}")
            return True, str(sync_path)
            
        except Exception as e:
            self.logger.error(f"Errore durante la sincronizzazione: {str(e)}")
            return False, str(e)
    
    def restore_from_latest_sync(self):
        """Ripristina il database dall'ultima sincronizzazione"""
        try:
            # Trova l'ultimo file di sync
            sync_files = list(self.sync_dir.glob("cpa_database_sync_*.db"))
            if not sync_files:
                return False, "Nessun file di sincronizzazione trovato"
            
            # Ordina per timestamp e prendi l'ultimo
            sync_files.sort(key=lambda x: x.name, reverse=True)
            latest_sync = sync_files[0]
            
            # Crea backup del database corrente prima del ripristino
            if os.path.exists(self.db_path):
                backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.db_path, backup_path)
                self.logger.info(f"Backup del database corrente: {backup_path}")
            
            # Ripristina dal sync
            shutil.copy2(latest_sync, self.db_path)
            
            self.logger.info(f"Database ripristinato da: {latest_sync}")
            return True, f"Database ripristinato da {latest_sync.name}"
            
        except Exception as e:
            self.logger.error(f"Errore durante il ripristino: {str(e)}")
            return False, str(e)
    
    def _create_sync_metadata(self, sync_path, timestamp):
        """Crea metadati della sincronizzazione"""
        try:
            # Connessione al database sincronizzato per ottenere statistiche
            conn = sqlite3.connect(sync_path)
            cursor = conn.cursor()
            
            # Conta record nelle tabelle principali
            cursor.execute("SELECT COUNT(*) FROM clienti")
            clienti_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM incroci")
            incroci_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Crea metadati
            metadata = {
                "sync_type": "repository_persistence",
                "timestamp": datetime.now().isoformat(),
                "source_db": self.db_path,
                "sync_path": str(sync_path),
                "statistics": {
                    "clienti_count": clienti_count,
                    "incroci_count": incroci_count
                },
                "purpose": "Persistenza dati tra riavvii Streamlit Cloud"
            }
            
            # Salva metadati
            metadata_path = sync_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Impossibile creare metadati: {str(e)}")
    
    def _cleanup_old_sync_files(self, max_files=5):
        """Pulisce file di sync vecchi mantenendo solo gli ultimi N"""
        try:
            sync_files = list(self.sync_dir.glob("cpa_database_sync_*.db"))
            sync_files.sort(key=lambda x: x.name, reverse=True)
            
            # Rimuovi file in eccesso
            for sync_file in sync_files[max_files:]:
                sync_file.unlink()
                metadata_file = sync_file.with_suffix('.json')
                if metadata_file.exists():
                    metadata_file.unlink()
                self.logger.info(f"File di sync rimosso: {sync_file}")
                
        except Exception as e:
            self.logger.warning(f"Impossibile pulire file di sync vecchi: {str(e)}")
    
    def list_sync_files(self):
        """Lista tutti i file di sincronizzazione disponibili"""
        try:
            sync_files = []
            for sync_file in self.sync_dir.glob("cpa_database_sync_*.db"):
                metadata_file = sync_file.with_suffix('.json')
                metadata = {}
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    except:
                        pass
                
                sync_info = {
                    "filename": sync_file.name,
                    "path": str(sync_file),
                    "size": sync_file.stat().st_size,
                    "modified": datetime.fromtimestamp(sync_file.stat().st_mtime),
                    "metadata": metadata
                }
                sync_files.append(sync_info)
            
            # Ordina per data di modifica (più recenti prima)
            sync_files.sort(key=lambda x: x['modified'], reverse=True)
            return sync_files
            
        except Exception as e:
            self.logger.error(f"Errore nel listare i file di sync: {str(e)}")
            return []
    
    def auto_sync_on_startup(self):
        """Sincronizzazione automatica all'avvio dell'app"""
        try:
            # Se il database corrente è vuoto o ha pochi dati, ripristina dal sync
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM clienti")
                current_clienti = cursor.fetchone()[0]
                conn.close()
                
                # Se ci sono pochi clienti, prova a ripristinare dal sync
                if current_clienti < 3:  # Soglia arbitraria
                    self.logger.info("Database corrente ha pochi dati, tentativo di ripristino dal sync...")
                    success, message = self.restore_from_latest_sync()
                    if success:
                        self.logger.info(f"Ripristino automatico completato: {message}")
                        return True, message
                    else:
                        self.logger.warning(f"Ripristino automatico fallito: {message}")
            
            # Sincronizza il database corrente
            success, message = self.sync_to_repository()
            if success:
                self.logger.info(f"Sincronizzazione automatica completata: {message}")
            else:
                self.logger.warning(f"Sincronizzazione automatica fallita: {message}")
            
            return success, message
            
        except Exception as e:
            self.logger.error(f"Errore durante la sincronizzazione automatica: {str(e)}")
            return False, str(e)

# Funzioni di utilità
def auto_sync_database(db_path="cpa_database.db"):
    """Sincronizzazione automatica del database"""
    sync_manager = DatabaseSyncManager(db_path)
    return sync_manager.auto_sync_on_startup()

def manual_sync_database(db_path="cpa_database.db"):
    """Sincronizzazione manuale del database"""
    sync_manager = DatabaseSyncManager(db_path)
    return sync_manager.sync_to_repository()

def restore_database(db_path="cpa_database.db"):
    """Ripristino del database dall'ultima sincronizzazione"""
    sync_manager = DatabaseSyncManager(db_path)
    return sync_manager.restore_from_latest_sync()

if __name__ == "__main__":
    # Test del sistema di sincronizzazione
    print("🧪 Test sistema di sincronizzazione database...")
    
    sync_manager = DatabaseSyncManager()
    
    # Sincronizzazione automatica
    success, message = sync_manager.auto_sync_on_startup()
    print(f"Sync automatico: {success} - {message}")
    
    # Lista file di sync
    sync_files = sync_manager.list_sync_files()
    print(f"File di sync disponibili: {len(sync_files)}")
    
    # Info database corrente
    if os.path.exists("cpa_database.db"):
        conn = sqlite3.connect("cpa_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clienti")
        clienti_count = cursor.fetchone()[0]
        conn.close()
        print(f"Database corrente: {clienti_count} clienti")
