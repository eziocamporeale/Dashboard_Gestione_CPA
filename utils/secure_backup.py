import os
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import json

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class SecureBackupManager:
    """
    Gestore per backup locali sicuri (NON tracciati da Git)
    Salva i dati in una cartella esterna al repository
    """
    
    def __init__(self, backup_dir="~/CPA_Backups_Sicuri"):
        self.backup_dir = Path(backup_dir).expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Crea sottocartelle organizzate
        self.daily_dir = self.backup_dir / "daily"
        self.weekly_dir = self.backup_dir / "weekly"
        self.monthly_dir = self.backup_dir / "monthly"
        
        for dir_path in [self.daily_dir, self.weekly_dir, self.monthly_dir]:
            dir_path.mkdir(exist_ok=True)
        
        logging.info(f"SecureBackupManager inizializzato: {self.backup_dir}")
    
    def create_secure_backup(self, backup_type="manual"):
        """
        Crea un backup sicuro del database
        
        Args:
            backup_type (str): Tipo di backup (manual, auto, critical)
            
        Returns:
            tuple: (success, backup_path, metadata)
        """
        try:
            # Percorso database sorgente
            source_db = Path("cpa_database.db")
            if not source_db.exists():
                return False, "Database sorgente non trovato", None
            
            # Nome file backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"cpa_database_secure_{backup_type}_{timestamp}.db"
            
            # Determina cartella di destinazione
            if backup_type == "daily":
                dest_dir = self.daily_dir
            elif backup_type == "weekly":
                dest_dir = self.weekly_dir
            elif backup_type == "monthly":
                dest_dir = self.monthly_dir
            else:
                dest_dir = self.backup_dir
            
            backup_path = dest_dir / backup_filename
            
            # Copia database
            shutil.copy2(source_db, backup_path)
            
            # Crea metadati
            metadata = self._create_metadata(backup_path, backup_type)
            
            # Salva metadati
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logging.info(f"✅ Backup sicuro creato: {backup_path}")
            return True, str(backup_path), metadata
            
        except Exception as e:
            logging.error(f"❌ Errore durante backup sicuro: {e}")
            return False, str(e), None
    
    def _create_metadata(self, backup_path, backup_type):
        """Crea metadati per il backup"""
        try:
            # Connessione al database per statistiche
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Conta clienti
            cursor.execute("SELECT COUNT(*) FROM clienti")
            clienti_count = cursor.fetchone()[0]
            
            # Conta incroci
            cursor.execute("SELECT COUNT(*) FROM incroci")
            incroci_count = cursor.fetchone()[0]
            
            # Informazioni file
            file_size = backup_path.stat().st_size
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            conn.close()
            
            return {
                "backup_type": "secure_local",
                "backup_category": backup_type,
                "timestamp": datetime.now().isoformat(),
                "source_db": "cpa_database.db",
                "backup_path": str(backup_path),
                "file_size_bytes": file_size,
                "file_size_mb": file_size_mb,
                "statistics": {
                    "clienti_count": clienti_count,
                    "incroci_count": incroci_count
                },
                "security": {
                    "location": "local_only",
                    "git_tracked": False,
                    "encrypted": False,
                    "access": "local_user_only"
                },
                "purpose": "Backup locale sicuro - NON tracciato da Git"
            }
            
        except Exception as e:
            logging.error(f"Errore creazione metadati: {e}")
            return {
                "backup_type": "secure_local",
                "backup_category": backup_type,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def list_secure_backups(self, category=None):
        """
        Lista tutti i backup sicuri disponibili
        
        Args:
            category (str): Filtra per categoria (daily, weekly, monthly, None per tutti)
            
        Returns:
            list: Lista dei backup disponibili
        """
        backups = []
        
        try:
            if category:
                search_dirs = [getattr(self, f"{category}_dir")]
            else:
                search_dirs = [self.daily_dir, self.weekly_dir, self.monthly_dir, self.backup_dir]
            
            for search_dir in search_dirs:
                if search_dir.exists():
                    for db_file in search_dir.glob("*.db"):
                        metadata_file = db_file.with_suffix('.json')
                        
                        backup_info = {
                            "filename": db_file.name,
                            "path": str(db_file),
                            "size_mb": round(db_file.stat().st_size / (1024 * 1024), 2),
                            "modified": datetime.fromtimestamp(db_file.stat().st_mtime),
                            "category": self._get_category_from_path(db_file)
                        }
                        
                        # Aggiungi metadati se disponibili
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                    backup_info["metadata"] = metadata
                            except:
                                pass
                        
                        backups.append(backup_info)
            
            # Ordina per data di modifica (più recenti prima)
            backups.sort(key=lambda x: x["modified"], reverse=True)
            
            return backups
            
        except Exception as e:
            logging.error(f"Errore durante listaggio backup: {e}")
            return []
    
    def _get_category_from_path(self, file_path):
        """Determina la categoria del backup dal percorso"""
        if self.daily_dir in file_path.parents:
            return "daily"
        elif self.weekly_dir in file_path.parents:
            return "weekly"
        elif self.monthly_dir in file_path.parents:
            return "monthly"
        else:
            return "general"
    
    def restore_from_secure_backup(self, backup_path):
        """
        Ripristina il database da un backup sicuro
        
        Args:
            backup_path (str): Percorso del backup da ripristinare
            
        Returns:
            tuple: (success, message)
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return False, "File di backup non trovato"
            
            # Backup del database corrente
            current_db = Path("cpa_database.db")
            if current_db.exists():
                backup_current = f"cpa_database.db.backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(current_db, backup_current)
                logging.info(f"Backup database corrente: {backup_current}")
            
            # Ripristino
            shutil.copy2(backup_file, current_db)
            
            logging.info(f"✅ Database ripristinato da: {backup_path}")
            return True, f"Database ripristinato da {backup_path}"
            
        except Exception as e:
            logging.error(f"❌ Errore durante ripristino: {e}")
            return False, str(e)
    
    def cleanup_old_backups(self, keep_daily=7, keep_weekly=4, keep_monthly=3):
        """
        Pulisce i backup vecchi mantenendo solo i più recenti
        
        Args:
            keep_daily (int): Numero di backup giornalieri da mantenere
            keep_weekly (int): Numero di backup settimanali da mantenere
            keep_monthly (int): Numero di backup mensili da mantenere
        """
        try:
            # Pulisci backup giornalieri
            daily_backups = self.list_secure_backups("daily")
            if len(daily_backups) > keep_daily:
                for backup in daily_backups[keep_daily:]:
                    self._delete_backup(backup["path"])
            
            # Pulisci backup settimanali
            weekly_backups = self.list_secure_backups("weekly")
            if len(weekly_backups) > keep_weekly:
                for backup in weekly_backups[keep_weekly:]:
                    self._delete_backup(backup["path"])
            
            # Pulisci backup mensili
            monthly_backups = self.list_secure_backups("monthly")
            if len(monthly_backups) > keep_monthly:
                for backup in monthly_backups[keep_monthly:]:
                    self._delete_backup(backup["path"])
            
            logging.info("✅ Pulizia backup completata")
            
        except Exception as e:
            logging.error(f"❌ Errore durante pulizia: {e}")
    
    def _delete_backup(self, backup_path):
        """Elimina un backup e i suoi metadati"""
        try:
            backup_file = Path(backup_path)
            metadata_file = backup_file.with_suffix('.json')
            
            if backup_file.exists():
                backup_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
                
            logging.info(f"Backup eliminato: {backup_path}")
            
        except Exception as e:
            logging.error(f"Errore eliminazione backup {backup_path}: {e}")

# Funzioni di utilità per l'integrazione con Streamlit
def create_secure_backup(backup_type="manual"):
    """Crea un backup sicuro"""
    manager = SecureBackupManager()
    return manager.create_secure_backup(backup_type)

def list_secure_backups(category=None):
    """Lista i backup sicuri disponibili"""
    manager = SecureBackupManager()
    return manager.list_secure_backups(category)

def restore_from_secure_backup(backup_path):
    """Ripristina da un backup sicuro"""
    manager = SecureBackupManager()
    return manager.restore_from_secure_backup(backup_path)
