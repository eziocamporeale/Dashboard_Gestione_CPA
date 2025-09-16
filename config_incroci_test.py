#!/usr/bin/env python3
"""
🔧 CONFIGURAZIONE TEST INCROCI MODERNI
File di configurazione per testare la nuova interfaccia incroci
"""

# Flag per abilitare/disabilitare la versione moderna
ENABLE_MODERN_INCROCI = True  # Cambia in False per tornare alla versione originale

# Configurazioni per il test
TEST_CONFIG = {
    'modern_ui': ENABLE_MODERN_INCROCI,
    'show_toggle': True,  # Mostra il toggle nella sidebar
    'default_version': 'modern' if ENABLE_MODERN_INCROCI else 'original',
    'enable_animations': True,
    'enable_advanced_charts': True,
    'enable_wizard': True,
    'enable_analytics': True
}

# Messaggi per il test
TEST_MESSAGES = {
    'toggle_label': '🔄 Versione Interfaccia Incroci',
    'modern_label': '🎨 Moderna',
    'original_label': '📋 Originale',
    'test_mode_warning': '⚠️ Modalità Test Attiva - La versione moderna è in fase di test'
}

def is_modern_enabled():
    """Controlla se la versione moderna è abilitata"""
    return TEST_CONFIG['modern_ui']

def get_test_config():
    """Ottiene la configurazione di test"""
    return TEST_CONFIG

def get_test_messages():
    """Ottiene i messaggi di test"""
    return TEST_MESSAGES


