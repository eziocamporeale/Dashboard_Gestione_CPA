import json
import os
import streamlit as st

def t(key, default=None):
    """Funzione di convenienza per le traduzioni"""
    return translation_manager.t(key, default)

class TranslationManager:
    def __init__(self):
        self.locales_dir = "locales"
        self.default_language = "it"
        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        """Carica tutte le traduzioni dai file JSON"""
        try:
            # Carica traduzione italiana
            it_file = os.path.join(self.locales_dir, "it.json")
            if os.path.exists(it_file):
                with open(it_file, "r", encoding="utf-8") as f:
                    self.translations["it"] = json.load(f)
            
            # Carica traduzione spagnola
            es_file = os.path.join(self.locales_dir, "es.json")
            if os.path.exists(es_file):
                with open(es_file, "r", encoding="utf-8") as f:
                    self.translations["es"] = json.load(f)
                    
        except Exception as e:
            self.translations = {"it": {"error": "Errore"}, "es": {"error": "Error"}}

    def t(self, key, default=None):
        """Restituisce la traduzione per la chiave specificata"""
        try:
            # Ottieni la lingua corrente
            current_lang = st.session_state.get("language", self.default_language)
            
            # Se non c'è traduzione per questa lingua, usa l'italiano
            if current_lang not in self.translations:
                current_lang = self.default_language
            
            # Naviga nella struttura JSON usando la chiave
            keys = key.split('.')
            value = self.translations[current_lang]
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # Se non trova la traduzione, prova con l'italiano
                    if current_lang != self.default_language:
                        value = self.translations[self.default_language]
                        for k2 in keys:
                            if isinstance(value, dict) and k2 in value:
                                value = value[k2]
                            else:
                                return default or key
                    else:
                        return default or key
            
            return value if isinstance(value, str) else (default or key)
            
        except Exception as e:
            return default or key

# Istanza globale del gestore traduzioni
translation_manager = TranslationManager()
