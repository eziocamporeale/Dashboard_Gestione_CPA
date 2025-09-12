#!/usr/bin/env python3
"""
🔧 Sistema di Correzione Automatica per Dashboard CPA
Corregge automaticamente i problemi di sicurezza identificati dall'audit
"""

import os
import sys
import git
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityAutoFixer:
    """Sistema di correzione automatica per problemi di sicurezza"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.repo = None
        self.fixes_applied = []
        self.errors = []
        
        try:
            self.repo = git.Repo(project_root)
            logger.info("✅ Repository Git inizializzato per correzioni")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Git: {e}")
            self.repo = None
    
    def fix_database_files(self) -> Dict:
        """Rimuove file database locali"""
        fixes = []
        errors = []
        
        try:
            # Cerca file database
            db_files = list(self.project_root.glob("*.db"))
            db_files.extend(list(self.project_root.glob("*.sqlite")))
            db_files.extend(list(self.project_root.glob("*.sqlite3")))
            
            for db_file in db_files:
                try:
                    # Rimuovi dal tracking Git se tracciato
                    if self.repo:
                        try:
                            # Controlla se il file è tracciato da Git usando git status
                            result = self.repo.git.status('--porcelain', str(db_file))
                            if result.strip():  # Se c'è output, il file è tracciato
                                self.repo.index.remove([str(db_file)])
                                logger.info(f"✅ Rimosso {db_file.name} dal tracking Git")
                                fixes.append(f"Rimosso {db_file.name} dal tracking Git")
                            else:
                                logger.info(f"ℹ️ File {db_file.name} non tracciato da Git")
                        except Exception as git_error:
                            logger.warning(f"⚠️ File {db_file.name} non tracciato da Git: {git_error}")
                    
                    # Elimina il file fisicamente
                    if db_file.exists():
                        db_file.unlink()
                        logger.info(f"✅ Eliminato file database: {db_file.name}")
                        fixes.append(f"Eliminato file database: {db_file.name}")
                    else:
                        logger.info(f"ℹ️ File {db_file.name} già eliminato")
                        fixes.append(f"File {db_file.name} già eliminato")
                    
                except Exception as e:
                    error_msg = f"Errore rimozione {db_file.name}: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
            
            if not db_files:
                fixes.append("Nessun file database trovato")
                
        except Exception as e:
            error_msg = f"Errore controllo file database: {e}"
            logger.error(f"❌ {error_msg}")
            errors.append(error_msg)
        
        return {
            'fixes': fixes,
            'errors': errors,
            'success': len(errors) == 0
        }
    
    def fix_secrets_tracking(self) -> Dict:
        """Verifica e corregge il tracking di secrets.toml"""
        fixes = []
        errors = []
        
        try:
            if not self.repo:
                errors.append("Repository Git non disponibile")
                return {'fixes': fixes, 'errors': errors, 'success': False}
            
            # Controlla se secrets.toml è tracciato
            secrets_file = self.project_root / ".streamlit" / "secrets.toml"
            
            # Controlla se il file esiste
            if secrets_file.exists():
                try:
                    # Controlla se è tracciato da Git usando git status
                    try:
                        # Usa git status per controllare se il file è tracciato
                        result = self.repo.git.status('--porcelain', str(secrets_file))
                        if result.strip():  # Se c'è output, il file è tracciato
                            # Rimuovi dal tracking Git
                            self.repo.index.remove([str(secrets_file)])
                            logger.info("✅ Rimosso secrets.toml dal tracking Git")
                            fixes.append("Rimosso secrets.toml dal tracking Git")
                        else:
                            logger.info("ℹ️ secrets.toml non tracciato da Git")
                            fixes.append("secrets.toml non tracciato da Git")
                    except Exception as git_check_error:
                        logger.warning(f"⚠️ Errore controllo file tracciati: {git_check_error}")
                        logger.info("ℹ️ secrets.toml non tracciato da Git")
                        fixes.append("secrets.toml non tracciato da Git")
                    
                    # Verifica che sia nel .gitignore
                    gitignore_file = self.project_root / ".gitignore"
                    if gitignore_file.exists():
                        content = gitignore_file.read_text()
                        if ".streamlit/secrets.toml" not in content:
                            # Aggiungi al .gitignore
                            content += "\n# Streamlit secrets\n.streamlit/secrets.toml\n"
                            gitignore_file.write_text(content)
                            fixes.append("Aggiunto secrets.toml al .gitignore")
                            logger.info("✅ Aggiunto secrets.toml al .gitignore")
                        else:
                            fixes.append("secrets.toml già nel .gitignore")
                    
                except Exception as e:
                    error_msg = f"Errore gestione secrets.toml: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
            else:
                logger.info("ℹ️ secrets.toml non trovato")
                fixes.append("secrets.toml non trovato")
                
        except Exception as e:
            error_msg = f"Errore controllo secrets.toml: {e}"
            logger.error(f"❌ {error_msg}")
            errors.append(error_msg)
        
        return {
            'fixes': fixes,
            'errors': errors,
            'success': len(errors) == 0
        }
    
    def fix_hardcoded_credentials(self) -> Dict:
        """Identifica e suggerisce correzioni per credenziali hardcoded"""
        fixes = []
        errors = []
        
        try:
            # Pattern comuni di credenziali
            credential_patterns = [
                r'key\s*=\s*["\'][^"\']+["\']',
                r'password\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']'
            ]
            
            import re
            files_with_credentials = []
            
            # Cerca in tutti i file Python
            for py_file in self.project_root.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    for pattern in credential_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            files_with_credentials.append(str(py_file))
                            break
                except Exception:
                    continue
            
            if files_with_credentials:
                fixes.append(f"Trovati {len(files_with_credentials)} file con possibili credenziali")
                fixes.append("Suggerimento: Spostare credenziali in variabili d'ambiente")
                
                # Suggerisci file da controllare
                for file_path in files_with_credentials[:5]:  # Mostra solo i primi 5
                    fixes.append(f"Controllare: {Path(file_path).name}")
            else:
                fixes.append("Nessuna credenziale hardcoded trovata")
                
        except Exception as e:
            error_msg = f"Errore controllo credenziali: {e}"
            logger.error(f"❌ {error_msg}")
            errors.append(error_msg)
        
        return {
            'fixes': fixes,
            'errors': errors,
            'success': len(errors) == 0
        }
    
    def fix_backup_files(self) -> Dict:
        """Rimuove file di backup non necessari"""
        fixes = []
        errors = []
        
        try:
            # Pattern per file di backup
            backup_patterns = [
                "*backup*",
                "*_backup_*",
                "*.backup",
                "*_old.py",
                "*_temp.py",
                "*.tmp"
            ]
            
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(list(self.project_root.glob(pattern)))
            
            # Rimuovi file di backup
            for backup_file in backup_files:
                try:
                    # Rimuovi dal tracking Git se tracciato
                    if self.repo and backup_file.name in [f.name for f in self.repo.index.entries]:
                        self.repo.index.remove([str(backup_file)])
                        logger.info(f"✅ Rimosso {backup_file.name} dal tracking Git")
                        fixes.append(f"Rimosso {backup_file.name} dal tracking Git")
                    
                    # Elimina il file fisicamente
                    backup_file.unlink()
                    logger.info(f"✅ Eliminato file backup: {backup_file.name}")
                    fixes.append(f"Eliminato file backup: {backup_file.name}")
                    
                except Exception as e:
                    error_msg = f"Errore rimozione {backup_file.name}: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
            
            if not backup_files:
                fixes.append("Nessun file backup trovato")
                
        except Exception as e:
            error_msg = f"Errore controllo file backup: {e}"
            logger.error(f"❌ {error_msg}")
            errors.append(error_msg)
        
        return {
            'fixes': fixes,
            'errors': errors,
            'success': len(errors) == 0
        }
    
    def run_all_fixes(self) -> Dict:
        """Esegue tutte le correzioni automatiche"""
        logger.info("🔧 INIZIO CORREZIONI AUTOMATICHE")
        
        all_fixes = []
        all_errors = []
        results = {}
        
        # Esegui tutte le correzioni
        corrections = [
            ("Database Files", self.fix_database_files),
            ("Secrets Tracking", self.fix_secrets_tracking),
            ("Hardcoded Credentials", self.fix_hardcoded_credentials),
            ("Backup Files", self.fix_backup_files)
        ]
        
        for name, fix_func in corrections:
            logger.info(f"🔧 Correzione: {name}")
            result = fix_func()
            results[name] = result
            all_fixes.extend(result['fixes'])
            all_errors.extend(result['errors'])
        
        # Calcola statistiche
        total_fixes = len(all_fixes)
        total_errors = len(all_errors)
        success_rate = (total_fixes / (total_fixes + total_errors)) * 100 if (total_fixes + total_errors) > 0 else 0
        
        logger.info(f"✅ CORREZIONI COMPLETATE: {total_fixes} correzioni, {total_errors} errori")
        
        return {
            'total_fixes': total_fixes,
            'total_errors': total_errors,
            'success_rate': success_rate,
            'fixes': all_fixes,
            'errors': all_errors,
            'results': results
        }
    
    def commit_fixes(self, message: str = "🔧 SECURITY: Correzioni automatiche applicate") -> bool:
        """Committa le correzioni applicate"""
        try:
            if not self.repo:
                logger.error("❌ Repository Git non disponibile")
                return False
            
            # Aggiungi tutti i cambiamenti
            self.repo.index.add(['.'])
            
            # Commit
            self.repo.index.commit(message)
            logger.info(f"✅ Commit creato: {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore commit: {e}")
            return False
