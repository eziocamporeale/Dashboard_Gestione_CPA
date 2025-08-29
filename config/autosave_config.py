# Configurazione per l'autosave automatico
# File di configurazione per il sistema di sincronizzazione automatica

# Intervalli di sincronizzazione (in minuti)
AUTOSAVE_CONFIG = {
    # Sincronizzazione automatica del database
    "sync_interval_minutes": 5,  # Ogni 5 minuti
    
    # Backup automatico locale
    "backup_interval_minutes": 10,  # Ogni 10 minuti
    
    # Push automatico su GitHub (solo se ci sono modifiche)
    "auto_push_enabled": True,
    
    # Retry in caso di errore
    "max_retries": 3,
    "retry_delay_seconds": 30,
    
    # Logging
    "log_level": "INFO",
    "log_to_file": False,  # Su Streamlit Cloud solo console
    
    # Notifiche
    "notify_on_error": True,
    "notify_on_success": False,  # Riduce spam
}

# Configurazione per diversi ambienti
ENVIRONMENT_CONFIGS = {
    "development": {
        "sync_interval_minutes": 2,  # Più frequente in sviluppo
        "backup_interval_minutes": 5,
        "auto_push_enabled": False,  # Non pushare in sviluppo
    },
    "production": {
        "sync_interval_minutes": 5,  # Standard per produzione
        "backup_interval_minutes": 10,
        "auto_push_enabled": True,
    },
    "streamlit_cloud": {
        "sync_interval_minutes": 3,  # Più frequente su Streamlit Cloud
        "backup_interval_minutes": 5,
        "auto_push_enabled": False,  # Disabilitato finché non configuriamo Git
    }
}

def get_autosave_config(environment="production"):
    """
    Restituisce la configurazione per l'ambiente specificato
    
    Args:
        environment (str): Ambiente di esecuzione
        
    Returns:
        dict: Configurazione per l'autosave
    """
    base_config = AUTOSAVE_CONFIG.copy()
    
    if environment in ENVIRONMENT_CONFIGS:
        base_config.update(ENVIRONMENT_CONFIGS[environment])
    
    return base_config

def is_autosave_enabled():
    """
    Verifica se l'autosave è abilitato
    
    Returns:
        bool: True se abilitato, False altrimenti
    """
    return True  # Sempre abilitato per ora

def get_sync_interval():
    """
    Restituisce l'intervallo di sincronizzazione in secondi
    
    Returns:
        int: Intervallo in secondi
    """
    config = get_autosave_config()
    return config["sync_interval_minutes"] * 60

def get_backup_interval():
    """
    Restituisce l'intervallo di backup in secondi
    
    Returns:
        int: Intervallo in secondi
    """
    config = get_autosave_config()
    return config["backup_interval_minutes"] * 60
