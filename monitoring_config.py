#!/usr/bin/env python3
"""
Configurazione per il monitoraggio della Dashboard Gestione CPA
"""

import os
from pathlib import Path

class MonitoringConfig:
    """Configurazione per il monitoraggio"""
    
    # Configurazione generale
    ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
    MONITORING_LOG_LEVEL = os.getenv('MONITORING_LOG_LEVEL', 'INFO')
    
    # Configurazione monitor sistema
    SYSTEM_MONITOR_INTERVAL = int(os.getenv('SYSTEM_MONITOR_INTERVAL', 60))  # secondi
    SYSTEM_METRICS_HISTORY_SIZE = int(os.getenv('SYSTEM_METRICS_HISTORY_SIZE', 1000))
    
    # Configurazione monitor database
    DATABASE_MONITOR_INTERVAL = int(os.getenv('DATABASE_MONITOR_INTERVAL', 300))  # secondi
    DATABASE_METRICS_HISTORY_SIZE = int(os.getenv('DATABASE_METRICS_HISTORY_SIZE', 100))
    
    # Soglie di allarme
    CPU_WARNING_THRESHOLD = float(os.getenv('CPU_WARNING_THRESHOLD', 80.0))  # percentuale
    CPU_CRITICAL_THRESHOLD = float(os.getenv('CPU_CRITICAL_THRESHOLD', 95.0))  # percentuale
    
    MEMORY_WARNING_THRESHOLD = float(os.getenv('MEMORY_WARNING_THRESHOLD', 85.0))  # percentuale
    MEMORY_CRITICAL_THRESHOLD = float(os.getenv('MEMORY_CRITICAL_THRESHOLD', 95.0))  # percentuale
    
    DISK_WARNING_THRESHOLD = float(os.getenv('DISK_WARNING_THRESHOLD', 85.0))  # percentuale
    DISK_CRITICAL_THRESHOLD = float(os.getenv('DISK_CRITICAL_THRESHOLD', 95.0))  # percentuale
    
    DATABASE_QUERY_WARNING_THRESHOLD = float(os.getenv('DATABASE_QUERY_WARNING_THRESHOLD', 1000.0))  # millisecondi
    DATABASE_QUERY_CRITICAL_THRESHOLD = float(os.getenv('DATABASE_QUERY_CRITICAL_THRESHOLD', 5000.0))  # millisecondi
    
    DATABASE_SIZE_WARNING_THRESHOLD = float(os.getenv('DATABASE_SIZE_WARNING_THRESHOLD', 100.0))  # MB
    DATABASE_SIZE_CRITICAL_THRESHOLD = float(os.getenv('DATABASE_SIZE_CRITICAL_THRESHOLD', 500.0))  # MB
    
    # Configurazione notifiche
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
    NOTIFICATION_WEBHOOK = os.getenv('NOTIFICATION_WEBHOOK', '')
    
    # Configurazione esportazione
    ENABLE_METRICS_EXPORT = os.getenv('ENABLE_METRICS_EXPORT', 'true').lower() == 'true'
    METRICS_EXPORT_FORMAT = os.getenv('METRICS_EXPORT_FORMAT', 'json')
    METRICS_EXPORT_INTERVAL = int(os.getenv('METRICS_EXPORT_INTERVAL', 3600))  # secondi
    
    # Configurazione directory
    MONITORING_DATA_DIR = Path(os.getenv('MONITORING_DATA_DIR', './monitoring_data'))
    METRICS_EXPORT_DIR = Path(os.getenv('METRICS_EXPORT_DIR', './exports'))
    
    # Configurazione retention
    METRICS_RETENTION_DAYS = int(os.getenv('METRICS_RETENTION_DAYS', 30))
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 90))
    
    @classmethod
    def create_directories(cls):
        """Crea le directory necessarie per il monitoraggio"""
        cls.MONITORING_DATA_DIR.mkdir(exist_ok=True)
        cls.METRICS_EXPORT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_thresholds(cls):
        """Restituisce tutte le soglie di allarme"""
        return {
            'cpu': {
                'warning': cls.CPU_WARNING_THRESHOLD,
                'critical': cls.CPU_CRITICAL_THRESHOLD
            },
            'memory': {
                'warning': cls.MEMORY_WARNING_THRESHOLD,
                'critical': cls.MEMORY_CRITICAL_THRESHOLD
            },
            'disk': {
                'warning': cls.DISK_WARNING_THRESHOLD,
                'critical': cls.DISK_CRITICAL_THRESHOLD
            },
            'database': {
                'query_warning': cls.DATABASE_QUERY_WARNING_THRESHOLD,
                'query_critical': cls.DATABASE_QUERY_CRITICAL_THRESHOLD,
                'size_warning': cls.DATABASE_SIZE_WARNING_THRESHOLD,
                'size_critical': cls.DATABASE_SIZE_CRITICAL_THRESHOLD
            }
        }
    
    @classmethod
    def get_intervals(cls):
        """Restituisce tutti gli intervalli di monitoraggio"""
        return {
            'system': cls.SYSTEM_MONITOR_INTERVAL,
            'database': cls.DATABASE_MONITOR_INTERVAL,
            'export': cls.METRICS_EXPORT_INTERVAL
        }
    
    @classmethod
    def get_config_summary(cls):
        """Restituisce un riepilogo della configurazione"""
        return {
            'enabled': cls.ENABLE_MONITORING,
            'log_level': cls.MONITORING_LOG_LEVEL,
            'intervals': cls.get_intervals(),
            'thresholds': cls.get_thresholds(),
            'notifications': {
                'enabled': cls.ENABLE_NOTIFICATIONS,
                'email': cls.NOTIFICATION_EMAIL,
                'webhook': cls.NOTIFICATION_WEBHOOK
            },
            'export': {
                'enabled': cls.ENABLE_METRICS_EXPORT,
                'format': cls.METRICS_EXPORT_FORMAT,
                'interval': cls.METRICS_EXPORT_INTERVAL
            },
            'retention': {
                'metrics_days': cls.METRICS_RETENTION_DAYS,
                'log_days': cls.LOG_RETENTION_DAYS
            }
        }
    
    @classmethod
    def validate_config(cls):
        """Valida la configurazione del monitoraggio"""
        errors = []
        
        # Controlla intervalli
        if cls.SYSTEM_MONITOR_INTERVAL < 10:
            errors.append("Intervallo monitor sistema troppo basso (< 10s)")
        
        if cls.DATABASE_MONITOR_INTERVAL < 60:
            errors.append("Intervallo monitor database troppo basso (< 60s)")
        
        # Controlla soglie
        if cls.CPU_WARNING_THRESHOLD >= cls.CPU_CRITICAL_THRESHOLD:
            errors.append("Soglia warning CPU deve essere minore della soglia critica")
        
        if cls.MEMORY_WARNING_THRESHOLD >= cls.MEMORY_CRITICAL_THRESHOLD:
            errors.append("Soglia warning memoria deve essere minore della soglia critica")
        
        if cls.DISK_WARNING_THRESHOLD >= cls.DISK_CRITICAL_THRESHOLD:
            errors.append("Soglia warning disco deve essere minore della soglia critica")
        
        # Controlla notifiche
        if cls.ENABLE_NOTIFICATIONS:
            if not cls.NOTIFICATION_EMAIL and not cls.NOTIFICATION_WEBHOOK:
                errors.append("Notifiche abilitate ma nessun metodo configurato")
        
        return errors

# Configurazione di default per sviluppo
DEFAULT_CONFIG = {
    'ENABLE_MONITORING': 'true',
    'SYSTEM_MONITOR_INTERVAL': '60',
    'DATABASE_MONITOR_INTERVAL': '300',
    'CPU_WARNING_THRESHOLD': '80.0',
    'MEMORY_WARNING_THRESHOLD': '85.0',
    'DISK_WARNING_THRESHOLD': '85.0',
    'ENABLE_NOTIFICATIONS': 'false',
    'ENABLE_METRICS_EXPORT': 'true'
}

def create_default_env_file():
    """Crea un file .env di esempio per il monitoraggio"""
    env_content = "# Configurazione Monitoraggio Dashboard Gestione CPA\n"
    env_content += "# Copia questo file in .env e modifica i valori secondo le tue esigenze\n\n"
    
    for key, value in DEFAULT_CONFIG.items():
        env_content += f"{key}={value}\n"
    
    env_content += "\n# Soglie di allarme aggiuntive\n"
    env_content += "CPU_CRITICAL_THRESHOLD=95.0\n"
    env_content += "MEMORY_CRITICAL_THRESHOLD=95.0\n"
    env_content += "DISK_CRITICAL_THRESHOLD=95.0\n"
    env_content += "DATABASE_QUERY_WARNING_THRESHOLD=1000.0\n"
    env_content += "DATABASE_SIZE_WARNING_THRESHOLD=100.0\n"
    
    env_content += "\n# Configurazione notifiche\n"
    env_content += "NOTIFICATION_EMAIL=admin@example.com\n"
    env_content += "NOTIFICATION_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz\n"
    
    env_content += "\n# Configurazione esportazione\n"
    env_content += "METRICS_EXPORT_FORMAT=json\n"
    env_content += "METRICS_EXPORT_INTERVAL=3600\n"
    
    env_content += "\n# Configurazione retention\n"
    env_content += "METRICS_RETENTION_DAYS=30\n"
    env_content += "LOG_RETENTION_DAYS=90\n"
    
    return env_content

if __name__ == "__main__":
    # Crea file .env di esempio
    env_content = create_default_env_file()
    
    with open('env.monitoring.example', 'w') as f:
        f.write(env_content)
    
    print("File env.monitoring.example creato")
    
    # Mostra configurazione corrente
    config = MonitoringConfig()
    print("\nConfigurazione corrente:")
    print("Configurazione monitoraggio:")
    print(f"  Abilitato: {config.ENABLE_MONITORING}")
    print(f"  Log level: {config.MONITORING_LOG_LEVEL}")
    print(f"  Intervallo sistema: {config.SYSTEM_MONITOR_INTERVAL}s")
    print(f"  Intervallo database: {config.DATABASE_MONITOR_INTERVAL}s")
    
    # Valida configurazione
    errors = config.validate_config()
    if errors:
        print("\nErrori di configurazione:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configurazione valida")
