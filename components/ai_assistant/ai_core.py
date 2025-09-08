#!/usr/bin/env python3
"""
AI Core Module per Dashboard Gestione CPA
Gestisce le chiamate API DeepSeek e la logica di base
Creato da Ezio Camporeale
"""

import requests
import json
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAssistant:
    """Classe principale per gestire le chiamate API DeepSeek"""
    
    def __init__(self):
        """Inizializza l'assistente AI"""
        from config import Config
        
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
        self.model = Config.DEEPSEEK_MODEL
        self.config = Config.AI_ASSISTANT_CONFIG
        self.prompts = Config.AI_PROMPTS
        
        # Cache per le risposte
        self.cache = {}
        
        logger.info("🤖 AI Assistant inizializzato per Dashboard CPA")
    
    def test_connection(self) -> bool:
        """Testa la connessione con l'API DeepSeek"""
        try:
            test_prompt = "Test di connessione API DeepSeek"
            response = self._make_api_call(test_prompt)
            return bool(response)
        except Exception as e:
            logger.error(f"❌ Test connessione fallito: {e}")
            return False
    
    def generate_response(self, prompt_type: str, data: Dict[str, Any]) -> str:
        """
        Genera una risposta AI basata sul tipo di prompt e i dati forniti
        
        Args:
            prompt_type: Tipo di prompt (client_analysis, incroci_prediction, etc.)
            data: Dati da inserire nel prompt
            
        Returns:
            str: Risposta generata dall'AI
        """
        try:
            # Controlla cache
            cache_key = self._generate_cache_key(prompt_type, data)
            if self.config['cache_responses'] and cache_key in self.cache:
                cached_response = self.cache[cache_key]
                if self._is_cache_valid(cached_response):
                    logger.info("📋 Risposta recuperata dalla cache")
                    return cached_response['response']
            
            # Genera prompt
            if prompt_type not in self.prompts:
                raise ValueError(f"Tipo prompt non valido: {prompt_type}")
            
            prompt_template = self.prompts[prompt_type]
            formatted_prompt = prompt_template.format(**data)
            
            # Chiama API con retry
            response = self._make_api_call_with_retry(formatted_prompt)
            
            if response:
                # Salva in cache
                if self.config['cache_responses']:
                    self.cache[cache_key] = {
                        'response': response,
                        'timestamp': datetime.now(),
                        'prompt_type': prompt_type
                    }
                
                logger.info(f"✅ Risposta AI generata per {prompt_type}")
                return response
            else:
                return self._get_fallback_response(prompt_type)
                
        except Exception as e:
            logger.error(f"❌ Errore generazione risposta AI: {e}")
            return self._get_fallback_response(prompt_type)
    
    def _make_api_call_with_retry(self, prompt: str) -> Optional[str]:
        """Effettua chiamata API con retry e backoff esponenziale"""
        for attempt in range(self.config['retry_attempts']):
            try:
                response = self._make_api_call(prompt)
                if response:
                    return response
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ Timeout API (tentativo {attempt + 1}) - Timeout: {self.config['timeout']}s")
                if attempt < self.config['retry_attempts'] - 1:
                    time.sleep(3 ** attempt)  # Backoff più lungo per timeout
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Errore richiesta API (tentativo {attempt + 1}): {e}")
                if attempt < self.config['retry_attempts'] - 1:
                    time.sleep(2 ** attempt)  # Backoff esponenziale
                    
            except Exception as e:
                logger.error(f"❌ Errore generico chiamata API: {e}")
                break
        
        logger.error("❌ Tutti i tentativi API falliti")
        return None
    
    def _make_api_call(self, prompt: str) -> Optional[str]:
        """Effettua una singola chiamata API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Sei un assistente AI specializzato nell\'analisi di dati finanziari e CPA. Fornisci risposte professionali, dettagliate e actionable in italiano.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': self.config['max_tokens'],
            'temperature': self.config['temperature']
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
        else:
            logger.error(f"❌ Errore API: {response.status_code} - {response.text}")
            
        return None
    
    def _generate_cache_key(self, prompt_type: str, data: Dict[str, Any]) -> str:
        """Genera una chiave unica per la cache"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(f"{prompt_type}:{data_str}".encode()).hexdigest()
    
    def _is_cache_valid(self, cached_response: Dict[str, Any]) -> bool:
        """Controlla se la risposta in cache è ancora valida"""
        cache_duration = timedelta(hours=self.config['cache_duration_hours'])
        return datetime.now() - cached_response['timestamp'] < cache_duration
    
    def _get_fallback_response(self, prompt_type: str) -> str:
        """Risposta di fallback quando l'API non è disponibile"""
        fallback_responses = {
            'client_analysis': """**Analisi Cliente (Modalità Offline)**

⚠️ **Servizio AI temporaneamente non disponibile**

**Analisi di Base:**
- Cliente registrato e attivo
- Account broker configurato
- Volume posizione standard

**Raccomandazioni Generali:**
1. Monitorare regolarmente le performance
2. Diversificare i broker per ridurre i rischi
3. Mantenere volumi bilanciati
4. Documentare tutte le operazioni

*Il servizio AI sarà ripristinato a breve.*""",
            
            'incroci_prediction': """**Predizione Incroci (Modalità Offline)**

⚠️ **Servizio AI temporaneamente non disponibile**

**Analisi di Base:**
- Pattern storici da considerare
- Diversificazione broker importante
- Gestione del rischio fondamentale

**Raccomandazioni Generali:**
1. Analizzare i trend storici
2. Diversificare le posizioni
3. Monitorare i volumi
4. Gestire il rischio attentamente

*Il servizio AI sarà ripristinato a breve.*""",
            
            'broker_optimization': """**Ottimizzazione Broker (Modalità Offline)**

⚠️ **Servizio AI temporaneamente non disponibile**

**Strategie di Base:**
- Diversificazione tra broker
- Bilanciamento dei volumi
- Monitoraggio delle performance

**Raccomandazioni Generali:**
1. Non concentrare tutto su un broker
2. Monitorare le commissioni
3. Verificare la liquidità
4. Mantenere backup sempre attivi

*Il servizio AI sarà ripristinato a breve.*""",
            
            'marketing_advice': """**Consigli Marketing (Modalità Offline)**

⚠️ **Servizio AI temporaneamente non disponibile**

**Strategie di Base:**
- Segmentazione clienti per performance
- Retention basata sui risultati
- Upselling per clienti profittevoli

**Raccomandazioni Generali:**
1. Identificare i clienti top performer
2. Creare programmi di loyalty
3. Offrire servizi premium
4. Monitorare la soddisfazione

*Il servizio AI sarà ripristinato a breve.*""",
            
            'risk_analysis': """**Analisi Rischi (Modalità Offline)**

⚠️ **Servizio AI temporaneamente non disponibile**

**Rischi Identificati:**
- Concentrazione su singoli broker
- Volumi non bilanciati
- Mancanza di diversificazione

**Raccomandazioni Generali:**
1. Diversificare i broker
2. Bilanciare i volumi
3. Monitorare i rischi
4. Avere piani di contingenza

*Il servizio AI sarà ripristinato a breve.*""",
            
            'report_generation': """**Report Generato (Modalità Offline)**

⚠️ **Servizio AI temporaneamente non disponibile**

**Report di Base:**
- Panoramica generale dei dati
- Statistiche principali
- Trend identificati

**Sezioni Incluse:**
1. Executive Summary
2. Analisi Performance
3. Trend e Proiezioni
4. Raccomandazioni

*Il servizio AI sarà ripristinato a breve.*"""
        }
        
        return fallback_responses.get(prompt_type, "Risposta non disponibile in modalità offline.")
    
    def clear_cache(self):
        """Pulisce la cache delle risposte"""
        self.cache.clear()
        logger.info("🗑️ Cache AI pulita")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche sulla cache"""
        return {
            'total_cached': len(self.cache),
            'cache_enabled': self.config['cache_responses'],
            'cache_duration_hours': self.config['cache_duration_hours']
        }
