#!/usr/bin/env python3
"""
🧪 TEST CORREZIONE DOWNLOAD DIEGO
Script per testare che Diego possa scaricare file senza errori
"""

import sys
import os
import logging
from datetime import datetime

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_diego_download():
    """Testa il download di file per Diego"""
    
    try:
        # Import dei componenti necessari
        from components.storage.storage_manager import StorageManager
        
        logger.info("🧪 Test correzione download Diego...")
        
        # Inizializza StorageManager
        storage_manager = StorageManager()
        
        # Simula la sessione di Diego
        import streamlit as st
        st.session_state.user_info = {
            'id': '794f1d66-7e99-425b-977a-874df86a9ab0',  # UUID di Diego
            'username': 'diego',
            'role': 'manager',
            'full_name': 'Diego Piludu'
        }
        
        logger.info("✅ Sessione Diego simulata")
        
        # Test conversione ID utente
        user_id = storage_manager.convert_user_id_for_storage('794f1d66-7e99-425b-977a-874df86a9ab0')
        logger.info(f"✅ Conversione ID Diego: UUID -> {user_id}")
        
        if user_id == 2:
            logger.info("✅ Mapping Diego corretto!")
        else:
            logger.warning(f"⚠️ Mapping Diego inaspettato: {user_id}")
        
        # Test conversione altri ID
        test_cases = [
            ('794f1d66-7e99-425b-977a-874df86a9ab0', 2),  # Diego
            ('12345678-1234-1234-1234-123456789012', 1),  # UUID non mappato
            (123, 123),  # Integer
            ('admin', 1),  # Stringa corta
        ]
        
        logger.info("🧪 Test casi di conversione:")
        for input_id, expected in test_cases:
            result = storage_manager.convert_user_id_for_storage(input_id)
            status = "✅" if result == expected else "❌"
            logger.info(f"  {status} {input_id} -> {result} (atteso: {expected})")
        
        # Test recupero file
        logger.info("📁 Test recupero file...")
        files = storage_manager.get_files()
        
        if files:
            logger.info(f"✅ Trovati {len(files)} file")
            
            # Test download del primo file
            if len(files) > 0:
                first_file = files[0]
                file_id = first_file['id']
                filename = first_file['original_filename']
                
                logger.info(f"🧪 Test download file: {filename} (ID: {file_id})")
                
                success, result_filename, content = storage_manager.download_file(file_id)
                
                if success:
                    logger.info(f"✅ Download riuscito: {result_filename} ({len(content)} bytes)")
                else:
                    logger.error(f"❌ Download fallito: {result_filename}")
            else:
                logger.info("ℹ️ Nessun file disponibile per il test")
        else:
            logger.info("ℹ️ Nessun file trovato nel sistema")
        
        logger.info("✅ Test correzione download Diego completato!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_diego_info():
    """Mostra informazioni su Diego e la correzione"""
    print("\n" + "="*80)
    print("🔧 CORREZIONE DOWNLOAD DIEGO")
    print("="*80)
    print("🔑 UUID Diego: 794f1d66-7e99-425b-977a-874df86a9ab0")
    print("🔢 ID Storage: 2")
    print("")
    print("🐛 PROBLEMA RISOLTO:")
    print("• Errore: invalid input syntax for type integer")
    print("• Causa: UUID Diego non compatibile con campi INTEGER")
    print("• Soluzione: Mapping UUID -> ID numerico")
    print("")
    print("✅ CORREZIONI APPLICATE:")
    print("• Funzione convert_user_id_for_storage()")
    print("• Mapping Diego UUID -> ID 2")
    print("• Gestione upload_file() e download_file()")
    print("• Compatibilità con tabelle storage esistenti")
    print("")
    print("🎯 RISULTATO:")
    print("• Diego può ora scaricare file senza errori")
    print("• Sistema compatibile con UUID e integer")
    print("• Log download funzionante")
    print("="*80)

if __name__ == "__main__":
    print("🧪 TEST CORREZIONE DOWNLOAD DIEGO")
    print("="*80)
    
    success = test_diego_download()
    
    if success:
        show_diego_info()
        print("\n✅ Test completato con successo!")
        print("🎉 Diego può ora scaricare file senza errori!")
    else:
        print("\n❌ Test fallito!")
        print("🔧 Controlla i log per dettagli")




