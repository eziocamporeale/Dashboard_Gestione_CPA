import logging
import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Gestore dei log per l'applicazione Dashboard Gestione CPA"""
    
    def __init__(self, name="cpa_dashboard", level=logging.INFO):
        """Inizializza il logger"""
        self.name = name
        self.level = level
        
        # Crea la directory logs se non esiste
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configura il logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Evita duplicazione degli handler
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura gli handler per il logging"""
        
        # Handler per console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Handler per file
        log_file = self.logs_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Aggiungi gli handler
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Log di livello INFO"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log di livello WARNING"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log di livello ERROR"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log di livello DEBUG"""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log di livello CRITICAL"""
        self.logger.critical(message)
    
    def log_operation(self, operation, details=None, user=None):
        """Log di un'operazione specifica"""
        message = f"OPERAZIONE: {operation}"
        if user:
            message += f" - UTENTE: {user}"
        if details:
            message += f" - DETTAGLI: {details}"
        
        self.info(message)
    
    def log_error(self, error, context=None):
        """Log di un errore con contesto"""
        message = f"ERRORE: {error}"
        if context:
            message += f" - CONTESTO: {context}"
        
        self.error(message)
    
    def log_database_operation(self, operation, table, record_id=None, details=None):
        """Log di un'operazione sul database"""
        message = f"DB {operation.upper()}: Tabella={table}"
        if record_id:
            message += f", ID={record_id}"
        if details:
            message += f", Dettagli={details}"
        
        self.info(message)
    
    def log_user_action(self, action, user=None, target=None, result=None):
        """Log di un'azione dell'utente"""
        message = f"AZIONE UTENTE: {action}"
        if user:
            message += f" - UTENTE: {user}"
        if target:
            message += f" - TARGET: {target}"
        if result:
            message += f" - RISULTATO: {result}"
        
        self.info(message)
    
    def log_performance(self, operation, duration, details=None):
        """Log delle performance"""
        message = f"PERFORMANCE: {operation} - DURATA: {duration:.3f}s"
        if details:
            message += f" - DETTAGLI: {details}"
        
        self.info(message)
    
    def log_security(self, event, user=None, ip=None, details=None):
        """Log di eventi di sicurezza"""
        message = f"SICUREZZA: {event}"
        if user:
            message += f" - UTENTE: {user}"
        if ip:
            message += f" - IP: {ip}"
        if details:
            message += f" - DETTAGLI: {details}"
        
        self.warning(message)
    
    def cleanup_old_logs(self, days_to_keep=30):
        """Pulisce i log vecchi"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self.logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.info(f"Log file rimosso: {log_file}")
        
        except Exception as e:
            self.error(f"Errore durante la pulizia dei log: {e}")
    
    def get_log_stats(self):
        """Restituisce statistiche sui log"""
        try:
            total_files = len(list(self.logs_dir.glob("*.log")))
            total_size = sum(f.stat().st_size for f in self.logs_dir.glob("*.log"))
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'logs_directory': str(self.logs_dir)
            }
        
        except Exception as e:
            self.error(f"Errore nel calcolo delle statistiche log: {e}")
            return {}

# Istanza globale del logger
logger = Logger()

# Funzioni di convenienza
def log_info(message):
    """Log di livello INFO"""
    logger.info(message)

def log_warning(message):
    """Log di livello WARNING"""
    logger.warning(message)

def log_error(message):
    """Log di livello ERROR"""
    logger.error(message)

def log_debug(message):
    """Log di livello DEBUG"""
    logger.debug(message)

def log_critical(message):
    """Log di livello CRITICAL"""
    logger.critical(message)

def log_operation(operation, details=None, user=None):
    """Log di un'operazione"""
    logger.log_operation(operation, details, user)

def log_database_operation(operation, table, record_id=None, details=None):
    """Log di un'operazione sul database"""
    logger.log_database_operation(operation, table, record_id, details)

def log_user_action(action, user=None, target=None, result=None):
    """Log di un'azione dell'utente"""
    logger.log_user_action(action, user, target, result)

def log_performance(operation, duration, details=None):
    """Log delle performance"""
    logger.log_performance(operation, duration, details)

def log_security(event, user=None, ip=None, details=None):
    """Log di eventi di sicurezza"""
    logger.log_security(event, user, ip, details)
