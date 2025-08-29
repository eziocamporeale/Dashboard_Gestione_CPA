"""
🔧 CONFIGURAZIONE SUPABASE
📋 Impostazioni per database remoto professionale
"""

import os

class SupabaseConfig:
    """Configurazione centralizzata per Supabase"""
    
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.SUPABASE_URL and cls.SUPABASE_ANON_KEY)

def get_supabase_setup_instructions():
    return """
🚀 **CONFIGURAZIONE SUPABASE:**
1. Vai su [supabase.com](https://supabase.com)
2. Crea nuovo progetto
3. Copia URL e API Key
4. Imposta variabili ambiente
"""
