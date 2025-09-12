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
        # FIX TEMPORANEO: Disabilita traduzioni per evitare loop infiniti
        # Usa sempre l'italiano come lingua di default
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
            
            # Se la lingua è cambiata, aggiorna senza rerun per evitare loop
            if selected_language != current_lang:
                self.set_language(selected_language)
                # Rimuoviamo st.rerun() per evitare loop infinito

# Istanza globale del gestore traduzioni
translation_manager = TranslationManager()

# Funzione di convenienza per le traduzioni
def t(key: str, default: str = None) -> str:
    """Funzione di convenienza per ottenere una traduzione"""
    return translation_manager.t(key, default)
