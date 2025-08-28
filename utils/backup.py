#!/usr/bin/env python3
"""
Sistema di backup automatico per il database CPA
Previene la perdita di dati con backup incrementali e versioning
"""

import sqlite3
import shutil
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import logging

class DatabaseBackupManager:
    def __init__(self, db_path="cpa_database.db", backup_dir="backups"):
        """Inizializza il gestore di backup"""
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configura logging - solo console per compatibilità Streamlit Cloud
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]  # Solo console, niente file
        )
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self, backup_type="auto"):
        """Crea un backup del database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"cpa_database_{backup_type}_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Verifica che il database sorgente esista
            if not os.path.exists(self.db_path):
                self.logger.error(f"Database sorgente non trovato: {self.db_path}")
                return False, "Database sorgente non trovato"
            
            # Crea backup con SQLite
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            # Backup completo del database
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            # Crea file di metadati del backup
            self._create_backup_metadata(backup_path, backup_type)
            
            # Pulisci backup vecchi (mantieni solo gli ultimi 10)
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup creato con successo: {backup_path}")
            return True, str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Errore durante il backup: {str(e)}")
            return False, str(e)
    
    def _create_backup_metadata(self, backup_path, backup_type):
        """Crea metadati del backup"""
        try:
            # Connessione al backup per ottenere statistiche
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Conta record nelle tabelle principali
            cursor.execute("SELECT COUNT(*) FROM clienti")
            clienti_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM incroci")
            incroci_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Crea metadati
            metadata = {
                "backup_type": backup_type,
                "timestamp": datetime.now().isoformat(),
                "source_db": self.db_path,
                "backup_path": str(backup_path),
                "statistics": {
                    "clienti_count": clienti_count,
                    "incroci_count": incroci_count
                },
            }
            
            # Salva metadati
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Impossibile creare metadati: {str(e)}")
    
    def _cleanup_old_backups(self, max_backups=10):
        """Pulisce backup vecchi mantenendo solo gli ultimi N"""
        try:
            backup_files = list(self.backup_dir.glob("cpa_database_*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Rimuovi backup in eccesso
            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                metadata_file = backup_file.with_suffix('.json')
                if metadata_file.exists():
                    metadata_file.unlink()
                self.logger.info(f"Backup rimosso: {backup_file}")
                
        except Exception as e:
            self.logger.warning(f"Impossibile pulire backup vecchi: {str(e)}")
    
    def restore_backup(self, backup_path):
        """Ripristina un backup"""
        try:
            if not os.path.exists(backup_path):
                return False, "File di backup non trovato"
            
            # Crea backup del database corrente prima del ripristino
            self.create_backup("pre_restore")
            
            # Ripristina il backup
            shutil.copy2(backup_path, self.db_path)
            
            self.logger.info(f"Backup ripristinato con successo da: {backup_path}")
            return True, "Backup ripristinato con successo"
            
        except Exception as e:
            self.logger.error(f"Errore durante il ripristino: {str(e)}")
            return False, str(e)
    
    def list_backups(self):
        """Lista tutti i backup disponibili"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob("cpa_database_*.db"):
                metadata_file = backup_file.with_suffix('.json')
                metadata = {}
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    except:
                        pass
                
                backup_info = {
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "modified": datetime.fromtimestamp(backup_file.stat().st_mtime),
                    "metadata": metadata
                }
                backups.append(backup_info)
            
            # Ordina per data di modifica (più recenti prima)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"Errore nel listare i backup: {str(e)}")
            return []
    
    def get_database_info(self):
        """Ottiene informazioni sul database corrente"""
        try:
            if not os.path.exists(self.db_path):
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Informazioni generali
            cursor.execute("SELECT COUNT(*) FROM clienti")
            clienti_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM incroci")
            incroci_count = cursor.fetchone()[0]
            
            # Ultima modifica
            cursor.execute("SELECT MAX(data_modifica) FROM clienti")
            last_client_update = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "path": self.db_path,
                "size": os.path.getsize(self.db_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(self.db_path)),
                "statistics": {
                    "clienti_count": clienti_count,
                    "incroci_count": incroci_count,
                    "last_client_update": last_client_update
                }
            }
            
        except Exception as e:
            self.logger.error(f"Errore nell'ottenere info database: {str(e)}")
            return None

# Funzione di utilità per backup automatico
def auto_backup(db_path="cpa_database.db"):
    """Esegue backup automatico"""
    backup_manager = DatabaseBackupManager(db_path)
    success, message = backup_manager.create_backup("auto")
    
    if success:
        print(f"✅ Backup automatico completato: {message}")
    else:
        print(f"❌ Backup automatico fallito: {message}")
    
    return success, message

# Funzione per ripristinare l'ultimo backup
def restore_latest_backup(db_path="cpa_database.db"):
    """Ripristina l'ultimo backup disponibile"""
    backup_manager = DatabaseBackupManager(db_path)
    backups = backup_manager.list_backups()
    
    if not backups:
        print("❌ Nessun backup disponibile")
        return False, "Nessun backup disponibile"
    
    latest_backup = backups[0]
    print(f"🔄 Ripristino backup: {latest_backup['filename']}")
    
    success, message = backup_manager.restore_backup(latest_backup['path'])
    
    if success:
        print(f"✅ Ripristino completato: {message}")
    else:
        print(f"❌ Ripristino fallito: {message}")
    
    return success, message

if __name__ == "__main__":
    # Test del sistema di backup
    print("🧪 Test sistema di backup...")
    
    backup_manager = DatabaseBackupManager()
    
    # Crea backup
    success, message = backup_manager.create_backup("test")
    print(f"Backup test: {success} - {message}")
    
    # Lista backup
    backups = backup_manager.list_backups()
    print(f"Backup disponibili: {len(backups)}")
    
    # Info database
    db_info = backup_manager.get_database_info()
    if db_info:
        print(f"Database corrente: {db_info['statistics']['clienti_count']} clienti")
