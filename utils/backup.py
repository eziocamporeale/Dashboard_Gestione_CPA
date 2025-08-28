#!/usr/bin/env python3
"""
Modulo per la gestione dei backup del database
"""

import os
import shutil
import sqlite3
from datetime import datetime
import streamlit as st

# Import diretti
from utils.logger import log_info, log_error, log_warning

class DatabaseBackup:
    """Gestore dei backup del database"""
    
    def __init__(self, db_path="cpa_database.db", backup_dir="backups"):
        """Inizializza il gestore backup"""
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurazione backup
        self.max_backups = 10  # Numero massimo di backup da mantenere
        self.backup_format = "sqlite"  # Formato backup: sqlite, zip, json
    
    def create_backup(self, backup_name=None):
        """Crea un backup del database"""
        try:
            if not self.db_path.exists():
                log_error(f"Database non trovato: {self.db_path}")
                return False, "Database non trovato"
            
            # Nome del backup
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"cpa_database_backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.db"
            
            # Crea il backup
            shutil.copy2(self.db_path, backup_path)
            
            # Verifica il backup
            if self._verify_backup(backup_path):
                log_info(f"Backup creato con successo: {backup_path}")
                
                # Pulisci i backup vecchi
                self._cleanup_old_backups()
                
                return True, str(backup_path)
            else:
                log_error(f"Verifica backup fallita: {backup_path}")
                backup_path.unlink()  # Rimuovi il backup non valido
                return False, "Verifica backup fallita"
                
        except Exception as e:
            log_error(f"Errore durante la creazione del backup: {e}")
            return False, str(e)
    
    def create_zip_backup(self, backup_name=None):
        """Crea un backup compresso del database"""
        try:
            if not self.db_path.exists():
                log_error(f"Database non trovato: {self.db_path}")
                return False, "Database non trovato"
            
            # Nome del backup
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"cpa_database_backup_{timestamp}"
            
            zip_path = self.backup_dir / f"{backup_name}.zip"
            
            # Crea il backup compresso
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.db_path, self.db_path.name)
                
                # Aggiungi metadati
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'database_size': self.db_path.stat().st_size,
                    'backup_type': 'zip',
                    'version': '1.0'
                }
                
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            log_info(f"Backup ZIP creato con successo: {zip_path}")
            
            # Pulisci i backup vecchi
            self._cleanup_old_backups()
            
            return True, str(zip_path)
            
        except Exception as e:
            log_error(f"Errore durante la creazione del backup ZIP: {e}")
            return False, str(e)
    
    def create_json_backup(self, backup_name=None):
        """Crea un backup in formato JSON del database"""
        try:
            if not self.db_path.exists():
                log_error(f"Database non trovato: {self.db_path}")
                return False, "Database non trovato"
            
            # Nome del backup
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"cpa_database_backup_{timestamp}"
            
            json_path = self.backup_dir / f"{backup_name}.json"
            
            # Connessione al database
            conn = sqlite3.connect(self.db_path)
            
            # Estrai tutti i dati
            backup_data = {}
            
            # Ottieni lista delle tabelle
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Estrai dati da ogni tabella
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                table_data = {
                    'columns': columns,
                    'rows': [dict(zip(columns, row)) for row in rows]
                }
                
                backup_data[table] = table_data
            
            # Aggiungi metadati
            backup_data['_metadata'] = {
                'backup_date': datetime.now().isoformat(),
                'database_size': self.db_path.stat().st_size,
                'backup_type': 'json',
                'version': '1.0',
                'tables': tables
            }
            
            # Salva il backup JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            conn.close()
            
            log_info(f"Backup JSON creato con successo: {json_path}")
            
            # Pulisci i backup vecchi
            self._cleanup_old_backups()
            
            return True, str(json_path)
            
        except Exception as e:
            log_error(f"Errore durante la creazione del backup JSON: {e}")
            return False, str(e)
    
    def restore_backup(self, backup_path):
        """Ripristina un backup"""
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                log_error(f"Backup non trovato: {backup_path}")
                return False, "Backup non trovato"
            
            # Crea backup del database corrente prima del ripristino
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = f"pre_restore_backup_{timestamp}"
            self.create_backup(safety_backup)
            
            # Ripristina il backup
            if backup_path.suffix == '.db':
                # Backup SQLite diretto
                shutil.copy2(backup_path, self.db_path)
                
            elif backup_path.suffix == '.zip':
                # Backup ZIP
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Estrai il database
                    db_name = self.db_path.name
                    zipf.extract(db_name, self.backup_dir)
                    
                    # Sposta il database estratto
                    extracted_db = self.backup_dir / db_name
                    shutil.move(extracted_db, self.db_path)
                    
            elif backup_path.suffix == '.json':
                # Backup JSON
                self._restore_from_json(backup_path)
                
            else:
                log_error(f"Formato backup non supportato: {backup_path.suffix}")
                return False, "Formato backup non supportato"
            
            # Verifica il ripristino
            if self._verify_backup(self.db_path):
                log_info(f"Backup ripristinato con successo: {backup_path}")
                return True, "Backup ripristinato con successo"
            else:
                log_error(f"Verifica ripristino fallita: {backup_path}")
                return False, "Verifica ripristino fallita"
                
        except Exception as e:
            log_error(f"Errore durante il ripristino del backup: {e}")
            return False, str(e)
    
    def _restore_from_json(self, json_path):
        """Ripristina il database da un backup JSON"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Rimuovi il database esistente
            if self.db_path.exists():
                self.db_path.unlink()
            
            # Crea nuovo database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ricrea le tabelle e inserisci i dati
            for table_name, table_data in backup_data.items():
                if table_name == '_metadata':
                    continue
                
                # Crea la tabella
                columns = table_data['columns']
                placeholders = ', '.join(['?' for _ in columns])
                create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
                cursor.execute(create_sql)
                
                # Inserisci i dati
                for row in table_data['rows']:
                    values = [row[col] for col in columns]
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log_error(f"Errore durante il ripristino da JSON: {e}")
            raise
    
    def _verify_backup(self, backup_path):
        """Verifica che un backup sia valido"""
        try:
            # Prova ad aprire il database
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Controlla che le tabelle principali esistano
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['clienti', 'campi_aggiuntivi', 'broker', 'piattaforme']
            
            for table in required_tables:
                if table not in tables:
                    conn.close()
                    return False
            
            # Controlla che ci sia almeno un record nella tabella piattaforme
            cursor.execute("SELECT COUNT(*) FROM piattaforme")
            count = cursor.fetchone()[0]
            
            conn.close()
            
            return count > 0
            
        except Exception as e:
            log_error(f"Errore durante la verifica del backup: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Pulisce i backup vecchi mantenendo solo i più recenti"""
        try:
            # Ottieni tutti i file di backup
            backup_files = []
            
            for ext in ['.db', '.zip', '.json']:
                backup_files.extend(self.backup_dir.glob(f"*{ext}"))
            
            # Ordina per data di modifica (più recenti prima)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Mantieni solo i backup più recenti
            if len(backup_files) > self.max_backups:
                files_to_remove = backup_files[self.max_backups:]
                
                for file_path in files_to_remove:
                    file_path.unlink()
                    log_info(f"Backup vecchio rimosso: {file_path}")
                    
        except Exception as e:
            log_error(f"Errore durante la pulizia dei backup: {e}")
    
    def list_backups(self):
        """Lista tutti i backup disponibili"""
        try:
            backups = []
            
            for ext in ['.db', '.zip', '.json']:
                for backup_file in self.backup_dir.glob(f"*{ext}"):
                    stat = backup_file.stat()
                    backup_info = {
                        'name': backup_file.name,
                        'path': str(backup_file),
                        'size': stat.st_size,
                        'size_mb': stat.st_size / (1024 * 1024),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'type': ext[1:]  # Rimuovi il punto
                    }
                    backups.append(backup_info)
            
            # Ordina per data di modifica (più recenti prima)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
            return backups
            
        except Exception as e:
            log_error(f"Errore durante il listing dei backup: {e}")
            return []
    
    def get_backup_stats(self):
        """Restituisce statistiche sui backup"""
        try:
            backups = self.list_backups()
            
            total_backups = len(backups)
            total_size = sum(b['size'] for b in backups)
            total_size_mb = total_size / (1024 * 1024)
            
            # Raggruppa per tipo
            by_type = {}
            for backup in backups:
                backup_type = backup['type']
                if backup_type not in by_type:
                    by_type[backup_type] = {'count': 0, 'size': 0}
                by_type[backup_type]['count'] += 1
                by_type[backup_type]['size'] += backup['size']
            
            return {
                'total_backups': total_backups,
                'total_size_bytes': total_size,
                'total_size_mb': total_size_mb,
                'by_type': by_type,
                'backup_directory': str(self.backup_dir),
                'max_backups': self.max_backups
            }
            
        except Exception as e:
            log_error(f"Errore nel calcolo delle statistiche backup: {e}")
            return {}

# Funzioni di convenienza
def create_backup(db_path="cpa_database.db", backup_type="sqlite"):
    """Crea un backup del database"""
    backup_manager = DatabaseBackup(db_path)
    
    if backup_type == "zip":
        return backup_manager.create_zip_backup()
    elif backup_type == "json":
        return backup_manager.create_json_backup()
    else:
        return backup_manager.create_backup()

def restore_backup(backup_path, db_path="cpa_database.db"):
    """Ripristina un backup"""
    backup_manager = DatabaseBackup(db_path)
    return backup_manager.restore_backup(backup_path)

def list_backups(db_path="cpa_database.db"):
    """Lista tutti i backup disponibili"""
    backup_manager = DatabaseBackup(db_path)
    return backup_manager.list_backups()

def get_backup_stats(db_path="cpa_database.db"):
    """Restituisce statistiche sui backup"""
    backup_manager = DatabaseBackup(db_path)
    return backup_manager.get_backup_stats()
