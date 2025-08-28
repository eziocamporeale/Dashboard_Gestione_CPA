import os
from pathlib import Path

class Config:
    """Configurazione dell'applicazione"""
    
    # Percorso base dell'applicazione
    BASE_DIR = Path(__file__).parent
    
    # Configurazione Database
    DATABASE_PATH = os.getenv('DB_PATH', 'cpa_database.db')
    DATABASE_FULL_PATH = BASE_DIR / DATABASE_PATH
    
    # Configurazione Streamlit
    STREAMLIT_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))
    STREAMLIT_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')
    
    # Configurazione Applicazione
    APP_TITLE = os.getenv('APP_TITLE', 'Dashboard Gestione CPA')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # Configurazione Sicurezza
    ENCRYPT_PASSWORDS = os.getenv('ENCRYPT_PASSWORDS', 'true').lower() == 'true'
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    
    # Configurazione Esportazione
    EXPORT_PATH = Path(os.getenv('EXPORT_PATH', './exports'))
    MAX_EXPORT_SIZE = int(os.getenv('MAX_EXPORT_SIZE', 10000))
    
    # Configurazione UI
    THEME_COLOR = "#02ab21"
    SIDEBAR_STATE = "expanded"
    PAGE_LAYOUT = "wide"
    
    # Configurazione Grafici
    CHART_HEIGHT = 400
    CHART_TEMPLATE = "plotly_white"
    
    # Configurazione Validazione
    MIN_DEPOSIT = 0.0
    MAX_DEPOSIT = 1000000.0
    
    # Configurazione Campi Aggiuntivi
    MAX_CUSTOM_FIELDS = 20
    
    @classmethod
    def create_directories(cls):
        """Crea le directory necessarie"""
        cls.EXPORT_PATH.mkdir(exist_ok=True)
        cls.BASE_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_database_url(cls):
        """Restituisce l'URL del database"""
        return f"sqlite:///{cls.DATABASE_FULL_PATH}"
    
    @classmethod
    def is_production(cls):
        """Controlla se l'ambiente è di produzione"""
        return not cls.DEBUG_MODE
    
    @classmethod
    def get_app_info(cls):
        """Restituisce le informazioni dell'applicazione"""
        return {
            'title': cls.APP_TITLE,
            'version': cls.APP_VERSION,
            'debug': cls.DEBUG_MODE,
            'database_path': str(cls.DATABASE_FULL_PATH),
            'export_path': str(cls.EXPORT_PATH)
        }
