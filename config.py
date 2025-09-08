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
    
    # Configurazione AI Assistant
    DEEPSEEK_API_KEY = "sk-f7531fb25e8a4ba3ae22d8b33c7d97a1"
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    # Configurazione AI Assistant
    AI_ASSISTANT_CONFIG = {
        'max_tokens': 1500,
        'temperature': 0.7,
        'timeout': 60,
        'retry_attempts': 3,
        'cache_responses': True,
        'cache_duration_hours': 24
    }
    
    # Prompt templates per AI Assistant CPA
    AI_PROMPTS = {
        'client_analysis': """
Analizza i dati del cliente CPA e fornisci insights professionali:

DATI CLIENTE:
- Nome: {nome_cliente}
- Email: {email}
- Broker: {broker}
- Piattaforma: {piattaforma}
- Volume Posizione: {volume_posizione}
- Stato Account: {stato_account}
- Data Registrazione: {data_registrazione}

STORIA INCROCI:
{storia_incroci}

ANALISI RICHIESTA:
1. **Performance Generale**: Valuta la performance del cliente
2. **Gestione Rischi**: Identifica pattern di rischio
3. **Consigli Ottimizzazione**: Suggerimenti per migliorare i risultati
4. **Strategia Personalizzata**: Raccomandazioni specifiche per questo cliente

Risposta in formato markdown, professionale e dettagliata.
""",
        
        'incroci_prediction': """
Analizza i dati degli incroci esistenti e predici la probabilità di successo:

DATI INCROCI ESISTENTI:
{incroci_data}

ANALISI RICHIESTA:
1. **Pattern di Successo**: Identifica i pattern che portano a risultati positivi
2. **Fattori di Rischio**: Elementi che aumentano la probabilità di perdite
3. **Predizione Probabilità**: Stima la probabilità di successo per nuovi incroci
4. **Raccomandazioni**: Suggerimenti per ottimizzare le strategie di incrocio

Risposta in formato markdown, con percentuali e analisi dettagliate.
""",
        
        'broker_optimization': """
Analizza i broker e fornisci consigli di ottimizzazione:

DATI BROKER:
{broker_data}

ANALISI RICHIESTA:
1. **Performance per Broker**: Confronto delle performance tra broker
2. **Ottimizzazione Volumi**: Suggerimenti per bilanciare i volumi
3. **Gestione Rischi**: Strategie per diversificare il rischio
4. **Raccomandazioni Broker**: Quali broker privilegiare e perché

Risposta in formato markdown, con analisi comparative e raccomandazioni specifiche.
""",
        
        'marketing_advice': """
Analizza i dati dei clienti e fornisci consigli di marketing:

DATI CLIENTI:
{clienti_data}

ANALISI RICHIESTA:
1. **Segmentazione Clienti**: Identifica i segmenti più profittevoli
2. **Strategie Acquisizione**: Come attrarre clienti simili ai migliori
3. **Retention Strategy**: Come mantenere i clienti esistenti
4. **Upselling Opportunities**: Opportunità di crescita con clienti attuali

Risposta in formato markdown, con strategie concrete e actionable.
""",
        
        'risk_analysis': """
Analizza i rischi del portafoglio clienti:

DATI PORTAFOGLIO:
{portfolio_data}

ANALISI RICHIESTA:
1. **Identificazione Rischi**: Principali rischi identificati
2. **Concentrazione Rischi**: Analisi della concentrazione del rischio
3. **Mitigazione**: Strategie per ridurre i rischi
4. **Monitoraggio**: Come monitorare i rischi in tempo reale

Risposta in formato markdown, con livelli di rischio e piani di azione.
""",
        
        'report_generation': """
Genera un report professionale sui dati CPA:

DATI REPORT:
{report_data}

REPORT RICHIESTO:
1. **Executive Summary**: Panoramica dei risultati principali
2. **Analisi Dettagliata**: Dettagli delle performance
3. **Trend e Proiezioni**: Analisi dei trend e previsioni
4. **Raccomandazioni**: Azioni consigliate per il futuro

Risposta in formato markdown, professionale e strutturata per presentazioni.
"""
    }
    
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
