import json
import os
import streamlit as st

class TranslationManager:
    """Gestore delle traduzioni per l'applicazione"""
    
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
                with open(it_file, 'r', encoding='utf-8') as f:
                    self.translations["it"] = json.load(f)
            
            # Carica traduzione spagnola
            es_file = os.path.join(self.locales_dir, "es.json")
            if os.path.exists(es_file):
                with open(es_file, 'r', encoding='utf-8') as f:
                    self.translations["es"] = json.load(f)
                    
        except Exception as e:
            st.error(f"Errore nel caricamento delle traduzioni: {e}")
            # Fallback: usa traduzioni hardcoded
            self.translations = {
                "it": {"error": "Errore nel caricamento traduzioni"},
                "es": {"error": "Error al cargar traducciones"}
            }
    
    def get_language(self) -> str:
        """Restituisce la lingua corrente"""
        return st.session_state.get("language", self.default_language)
    
    def set_language(self, language: str):
        """Imposta la lingua corrente"""
        if language in self.translations:
            st.session_state["language"] = language
        else:
            st.warning(f"Lingua '{language}' non supportata. Usando italiano.")
            st.session_state["language"] = self.default_language
    
    def t(self, key: str, default: str = None) -> str:
        """
        Restituisce la traduzione per la chiave specificata
        
        Args:
            key: Chiave della traduzione (es. "dashboard.title")
            default: Valore di default se la traduzione non viene trovata
        
        Returns:
            Stringa tradotta
        """
        try:
            # Ottieni la lingua corrente
            current_lang = self.get_language()
            
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
    
    def get_available_languages(self) -> dict:
        """Restituisce le lingue disponibili"""
        return {
            "it": "Italiano",
            "es": "Español"
        }
    
    def render_language_selector(self):
        """Rende il selettore di lingua nell'interfaccia"""
        languages = self.get_available_languages()
        current_lang = self.get_language()
        
        # Selettore di lingua nella sidebar
        with st.sidebar:
            st.markdown("---")
            selected_language = st.selectbox(
                "🌐 Seleziona Lingua",
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=list(languages.keys()).index(current_lang) if current_lang in languages else 0,
                key="language_selector"
            )
            
            # Se la lingua è cambiata, aggiorna
            if selected_language != current_lang:
                self.set_language(selected_language)
                st.rerun()

# Istanza globale del gestore traduzioni
translation_manager = TranslationManager()

# Funzione di convenienza per le traduzioni
def t(key: str, default: str = None) -> str:
    """Funzione di convenienza per ottenere una traduzione"""
    return translation_manager.t(key, default)
