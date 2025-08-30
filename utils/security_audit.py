#!/usr/bin/env python3
"""
🔒 Security Audit Script per Dashboard CPA
Verifica automatica della sicurezza del progetto
"""

import os
import sys
import git
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Auditor di sicurezza per il progetto Dashboard CPA"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.repo = None
        self.security_report = {
            'timestamp': datetime.now(),
            'overall_score': 0,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'checks_passed': 0,
            'total_checks': 0
        }
        
        try:
            self.repo = git.Repo(project_root)
            logger.info("✅ Repository Git inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Git: {e}")
            self.repo = None
    
    def run_full_audit(self) -> Dict:
        """Esegue un audit completo di sicurezza"""
        logger.info("🔒 INIZIO AUDIT DI SICUREZZA COMPLETO")
        
        # Reset report
        self.security_report = {
            'timestamp': datetime.now(),
            'overall_score': 0,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'checks_passed': 0,
            'total_checks': 0
        }
        
        # Esegui tutti i controlli
        self._check_database_files()
        self._check_sensitive_files()
        self._check_git_history()
        self._check_credentials()
        self._check_backup_files()
        self._check_environment_files()
        self._check_streamlit_secrets()
        
        # Calcola punteggio finale
        self._calculate_security_score()
        
        logger.info(f"🔒 AUDIT COMPLETATO - Punteggio: {self.security_report['overall_score']}/100")
        return self.security_report
    
    def run_quick_audit(self) -> Dict:
        """Esegue un audit rapido (solo controlli critici)"""
        logger.info("⚡ INIZIO AUDIT RAPIDO")
        
        self.security_report = {
            'timestamp': datetime.now(),
            'overall_score': 0,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'checks_passed': 0,
            'total_checks': 0
        }
        
        # Solo controlli critici
        self._check_database_files()
        self._check_credentials()
        self._check_streamlit_secrets()
        
        self._calculate_security_score()
        return self.security_report
    
    def _check_database_files(self):
        """Verifica presenza di file database nella repo"""
        logger.info("🔍 Controllo file database...")
        self.security_report['total_checks'] += 1
        
        database_patterns = ['*.db', '*.sqlite', '*.sqlite3']
        database_files = []
        
        for pattern in database_patterns:
            database_files.extend(self.project_root.glob(pattern))
        
        # Controlla anche cartelle specifiche
        database_dirs = ['backups', 'database_sync', 'data']
        for dir_name in database_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                database_files.extend(dir_path.glob('*.db'))
                database_files.extend(dir_path.glob('*.sqlite'))
        
        if database_files:
            issue_msg = f"🚨 TROVATI {len(database_files)} FILE DATABASE: {[f.name for f in database_files]}"
            self.security_report['issues'].append(issue_msg)
            logger.error(issue_msg)
        else:
            self.security_report['checks_passed'] += 1
            logger.info("✅ Nessun file database trovato nella repo")
    
    def _check_sensitive_files(self):
        """Verifica presenza di file sensibili"""
        logger.info("🔍 Controllo file sensibili...")
        self.security_report['total_checks'] += 1
        
        sensitive_patterns = [
            '*.env*', '*secret*', '*key*', '*password*', 
            '*credential*', '*token*', '*config*'
        ]
        
        sensitive_files = []
        for pattern in sensitive_patterns:
            sensitive_files.extend(self.project_root.glob(pattern))
        
        # Filtra file sicuri
        safe_files = [
            '.gitignore', '.streamlit/config.toml', 'config.py',
            'requirements.txt', 'README.md'
        ]
        
        actual_sensitive = []
        for file_path in sensitive_files:
            if file_path.name not in safe_files and not file_path.name.startswith('.'):
                actual_sensitive.append(file_path)
        
        if actual_sensitive:
            warning_msg = f"⚠️ TROVATI {len(actual_sensitive)} FILE POTENZIALMENTE SENSIBILI: {[f.name for f in actual_sensitive]}"
            self.security_report['warnings'].append(warning_msg)
            logger.warning(warning_msg)
        else:
            self.security_report['checks_passed'] += 1
            logger.info("✅ Nessun file sensibile identificato")
    
    def _check_git_history(self):
        """Verifica cronologia Git per file sensibili"""
        logger.info("🔍 Controllo cronologia Git...")
        self.security_report['total_checks'] += 1
        
        if not self.repo:
            self.security_report['warnings'].append("⚠️ Repository Git non disponibile")
            return
        
        try:
            # Controlla ultimi 20 commit per file database
            commits_with_db = []
            for commit in list(self.repo.iter_commits())[:20]:
                for file_path in commit.stats.files.keys():
                    if file_path.endswith(('.db', '.sqlite')):
                        commits_with_db.append((commit.hexsha[:8], file_path))
            
            if commits_with_db:
                warning_msg = f"⚠️ TROVATI {len(commits_with_db)} COMMIT CON DATABASE: {commits_with_db[:5]}"
                self.security_report['warnings'].append(warning_msg)
                logger.warning(warning_msg)
            else:
                self.security_report['checks_passed'] += 1
                logger.info("✅ Nessun database nei commit recenti")
                
        except Exception as e:
            self.security_report['warnings'].append(f"⚠️ Errore controllo cronologia Git: {e}")
            logger.warning(f"Errore controllo cronologia Git: {e}")
    
    def _check_credentials(self):
        """Verifica presenza di credenziali hardcoded"""
        logger.info("🔍 Controllo credenziali hardcoded...")
        self.security_report['total_checks'] += 1
        
        python_files = list(self.project_root.glob('**/*.py'))
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        files_with_credentials = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in credential_patterns:
                        if re.search(pattern, content):
                            files_with_credentials.append((py_file.name, pattern))
                            break
            except Exception as e:
                logger.warning(f"Errore lettura file {py_file}: {e}")
        
        if files_with_credentials:
            warning_msg = f"⚠️ TROVATI {len(files_with_credentials)} FILE CON PATTERN CREDENZIALI: {files_with_credentials[:3]}"
            self.security_report['warnings'].append(warning_msg)
            logger.warning(warning_msg)
        else:
            self.security_report['checks_passed'] += 1
            logger.info("✅ Nessuna credenziale hardcoded identificata")
    
    def _check_backup_files(self):
        """Verifica presenza di file di backup"""
        logger.info("🔍 Controllo file di backup...")
        self.security_report['total_checks'] += 1
        
        backup_patterns = ['*backup*', '*sync*', '*export*']
        backup_files = []
        
        for pattern in backup_patterns:
            backup_files.extend(self.project_root.glob(pattern))
        
        # Filtra file sicuri
        safe_backup = ['backup.py', 'secure_backup.py', 'database_sync.py']
        actual_backup = [f for f in backup_files if f.name not in safe_backup and not f.name.startswith('.')]
        
        if actual_backup:
            warning_msg = f"⚠️ TROVATI {len(actual_backup)} FILE DI BACKUP: {[f.name for f in actual_backup[:5]]}"
            self.security_report['warnings'].append(warning_msg)
            logger.warning(warning_msg)
        else:
            self.security_report['checks_passed'] += 1
            logger.info("✅ Nessun file di backup identificato")
    
    def _check_environment_files(self):
        """Verifica file di ambiente"""
        logger.info("🔍 Controllo file di ambiente...")
        self.security_report['total_checks'] += 1
        
        env_files = list(self.project_root.glob('.env*'))
        env_files.extend(list(self.project_root.glob('env*')))
        
        if env_files:
            warning_msg = f"⚠️ TROVATI {len(env_files)} FILE DI AMBIENTE: {[f.name for f in env_files]}"
            self.security_report['warnings'].append(warning_msg)
            logger.warning(warning_msg)
        else:
            self.security_report['checks_passed'] += 1
            logger.info("✅ Nessun file di ambiente identificato")
    
    def _check_streamlit_secrets(self):
        """Verifica configurazione Streamlit secrets"""
        logger.info("🔍 Controllo Streamlit secrets...")
        self.security_report['total_checks'] += 1
        
        secrets_file = self.project_root / '.streamlit' / 'secrets.toml'
        config_file = self.project_root / '.streamlit' / 'config.toml'
        
        if secrets_file.exists():
            # Verifica se è tracciato da Git
            if self.repo and secrets_file in self.repo.untracked_files:
                self.security_report['checks_passed'] += 1
                logger.info("✅ Streamlit secrets.toml NON tracciato da Git (SICURO)")
            else:
                issue_msg = "🚨 Streamlit secrets.toml è tracciato da Git (RISCHIOSO!)"
                self.security_report['issues'].append(issue_msg)
                logger.error(issue_msg)
        else:
            self.security_report['checks_passed'] += 1
            logger.info("✅ Streamlit secrets.toml non presente")
        
        if config_file.exists():
            # Verifica contenuto config.toml
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'password' in content.lower() or 'key' in content.lower():
                        warning_msg = "⚠️ config.toml potrebbe contenere informazioni sensibili"
                        self.security_report['warnings'].append(warning_msg)
                        logger.warning(warning_msg)
                    else:
                        logger.info("✅ config.toml sembra sicuro")
            except Exception as e:
                logger.warning(f"Errore lettura config.toml: {e}")
    
    def _calculate_security_score(self):
        """Calcola punteggio di sicurezza finale"""
        if self.security_report['total_checks'] == 0:
            self.security_report['overall_score'] = 0
            return
        
        # Calcolo punteggio: 70% per issues, 20% per warnings, 10% per checks passed
        issues_penalty = len(self.security_report['issues']) * 20
        warnings_penalty = len(self.security_report['warnings']) * 5
        checks_bonus = (self.security_report['checks_passed'] / self.security_report['total_checks']) * 10
        
        score = 100 - issues_penalty - warnings_penalty + checks_bonus
        self.security_report['overall_score'] = max(0, min(100, int(score)))
        
        # Aggiungi raccomandazioni basate sui risultati
        if self.security_report['issues']:
            self.security_report['recommendations'].append("🚨 RISOLVI IMMEDIATAMENTE le ISSUES identificate")
        
        if self.security_report['warnings']:
            self.security_report['recommendations'].append("⚠️ Rivedi i WARNINGS per migliorare la sicurezza")
        
        if self.security_report['overall_score'] >= 90:
            self.security_report['recommendations'].append("✅ Eccellente! Mantieni questo livello di sicurezza")
        elif self.security_report['overall_score'] >= 70:
            self.security_report['recommendations'].append("🟡 Buono, ma ci sono margini di miglioramento")
        else:
            self.security_report['recommendations'].append("🔴 Attenzione! La sicurezza necessita di interventi urgenti")
    
    def get_security_summary(self) -> str:
        """Restituisce un riassunto leggibile del report"""
        report = self.security_report
        
        summary = f"""
🔒 REPORT SICUREZZA - {report['timestamp'].strftime('%d/%m/%Y %H:%M')}
{'='*50}

📊 PUNTEGGIO TOTALE: {report['overall_score']}/100

✅ CONTROLLI SUPERATI: {report['checks_passed']}/{report['total_checks']}

🚨 ISSUES CRITICHE: {len(report['issues'])}
⚠️ WARNINGS: {len(report['warnings'])}

📋 RACCOMANDAZIONI:
"""
        
        for rec in report['recommendations']:
            summary += f"• {rec}\n"
        
        if report['issues']:
            summary += "\n🚨 ISSUES CRITICHE:\n"
            for issue in report['issues']:
                summary += f"• {issue}\n"
        
        if report['warnings']:
            summary += "\n⚠️ WARNINGS:\n"
            for warning in report['warnings']:
                summary += f"• {warning}\n"
        
        return summary
    
    def save_report(self, filename: str = None) -> str:
        """Salva il report su file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"security_audit_{timestamp}.txt"
        
        filepath = self.project_root / 'security_reports' / filename
        filepath.parent.mkdir(exist_ok=True)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.get_security_summary())
            
            logger.info(f"✅ Report salvato in: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"❌ Errore salvataggio report: {e}")
            return ""

def main():
    """Funzione principale per test dello script"""
    print("🔒 SECURITY AUDITOR - Dashboard CPA")
    print("="*50)
    
    auditor = SecurityAuditor()
    
    # Esegui audit completo
    print("\n🔍 Esecuzione audit completo...")
    report = auditor.run_full_audit()
    
    # Mostra riassunto
    print(auditor.get_security_summary())
    
    # Salva report
    report_file = auditor.save_report()
    if report_file:
        print(f"\n📁 Report salvato in: {report_file}")

if __name__ == "__main__":
    main()
