#!/usr/bin/env python3
"""
🧪 TELEGRAM NOTIFICATIONS TEST SUITE
Script completo per testare tutte le funzionalità del sistema notifiche Telegram
Creato da Ezio Camporeale
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramNotificationsTester:
    """Tester completo per il sistema notifiche Telegram"""
    
    def __init__(self):
        """Inizializza il tester"""
        self.telegram_manager = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self._init_telegram_manager()
    
    def _init_telegram_manager(self):
        """Inizializza TelegramManager"""
        try:
            from components.telegram_manager import TelegramManager
            self.telegram_manager = TelegramManager()
            logger.info("✅ TelegramManager inizializzato per testing")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione TelegramManager: {e}")
            self.test_results['errors'].append(f"TelegramManager init: {e}")
    
    def run_all_tests(self):
        """Esegue tutti i test"""
        logger.info("🚀 INIZIO TESTING SISTEMA NOTIFICHE TELEGRAM")
        logger.info("=" * 60)
        
        # Test configurazione
        self.test_telegram_configuration()
        
        # Test template messaggi
        self.test_message_templates()
        
        # Test invio messaggi
        self.test_message_sending()
        
        # Test gestione errori
        self.test_error_handling()
        
        # Test statistiche
        self.test_notification_statistics()
        
        # Risultati finali
        self.print_test_results()
    
    def test_telegram_configuration(self):
        """Test configurazione Telegram"""
        logger.info("🔧 TESTING: Configurazione Telegram")
        
        try:
            # Test stato configurazione
            status = self.telegram_manager.get_status()
            logger.info(f"📊 Stato configurazione: {status}")
            
            if status['is_configured']:
                logger.info("✅ Bot Telegram configurato")
                self.test_results['passed'] += 1
            else:
                logger.warning("⚠️ Bot Telegram non configurato - alcuni test potrebbero fallire")
                self.test_results['failed'] += 1
            
            # Test connessione (solo se configurato)
            if status['is_configured']:
                success, message = self.telegram_manager.test_connection()
                if success:
                    logger.info("✅ Test connessione riuscito")
                    self.test_results['passed'] += 1
                else:
                    logger.error(f"❌ Test connessione fallito: {message}")
                    self.test_results['failed'] += 1
                    self.test_results['errors'].append(f"Connection test: {message}")
            
        except Exception as e:
            logger.error(f"❌ Errore test configurazione: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Configuration test: {e}")
    
    def test_message_templates(self):
        """Test template messaggi"""
        logger.info("📝 TESTING: Template Messaggi")
        
        # Dati di test
        test_data = {
            'task_new_task': {
                'title': 'Test Task',
                'description': 'Descrizione test task',
                'priority': 'Alta',
                'period': 'Giornaliero',
                'due_date': '2025-01-15',
                'assigned_to': ['admin', 'test_user'],
                'created_by': 'admin'
            },
            'incrocio_new_incrocio': {
                'nome_incrocio': 'Test Incrocio EURUSD',
                'pair': 'EURUSD',
                'lot_size': '1.0',
                'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
            },
            'cliente_new_client': {
                'nome_cliente': 'Test Cliente',
                'email': 'test@example.com',
                'telefono': '+39 123 456 7890',
                'broker': 'Test Broker',
                'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
            },
            'wallet_new_deposit': {
                'wallet_destinatario': 'Test Wallet',
                'importo': '1000.00',
                'valuta': 'USDT',
                'motivo': 'Deposito test',
                'hash_transazione': 'test_hash_123456',
                'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
            },
            'vps_expiring': {
                'nome_cliente': 'Test Cliente VPS',
                'vps_ip': '192.168.1.100',
                'vps_username': 'testuser',
                'data_rinnovo': (datetime.now() + timedelta(days=3)).strftime('%d/%m/%Y'),
                'prezzo_vps': '50.00',
                'days_left': 3
            }
        }
        
        # Test ogni template
        for notification_type, data in test_data.items():
            try:
                message = self.telegram_manager._format_notification(notification_type, data)
                if message:
                    logger.info(f"✅ Template {notification_type}: OK")
                    logger.debug(f"📄 Messaggio: {message[:100]}...")
                    self.test_results['passed'] += 1
                else:
                    logger.error(f"❌ Template {notification_type}: Fallito")
                    self.test_results['failed'] += 1
                    self.test_results['errors'].append(f"Template {notification_type}: Nessun messaggio generato")
                    
            except Exception as e:
                logger.error(f"❌ Errore template {notification_type}: {e}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"Template {notification_type}: {e}")
    
    def test_message_sending(self):
        """Test invio messaggi"""
        logger.info("📤 TESTING: Invio Messaggi")
        
        if not self.telegram_manager.is_configured:
            logger.warning("⚠️ Bot non configurato - salto test invio messaggi")
            return
        
        # Test messaggio semplice
        try:
            test_message = "🧪 **TEST NOTIFICA**\n\nQuesto è un messaggio di test dal sistema Dashboard CPA!\n\n⏰ " + datetime.now().strftime('%d/%m/%Y %H:%M')
            
            success, message = self.telegram_manager.send_message(test_message)
            if success:
                logger.info("✅ Invio messaggio test riuscito")
                self.test_results['passed'] += 1
            else:
                logger.error(f"❌ Invio messaggio test fallito: {message}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"Message sending: {message}")
                
        except Exception as e:
            logger.error(f"❌ Errore invio messaggio: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Message sending: {e}")
    
    def test_error_handling(self):
        """Test gestione errori"""
        logger.info("🛡️ TESTING: Gestione Errori")
        
        # Test con dati mancanti
        try:
            message = self.telegram_manager._format_notification("invalid_type", {})
            if message is None:
                logger.info("✅ Gestione tipo non valido: OK")
                self.test_results['passed'] += 1
            else:
                logger.error("❌ Gestione tipo non valido: Fallita")
                self.test_results['failed'] += 1
                
        except Exception as e:
            logger.error(f"❌ Errore gestione tipo non valido: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Error handling: {e}")
        
        # Test con dati parziali
        try:
            message = self.telegram_manager._format_notification("task_new_task", {'title': 'Test'})
            if message and 'N/A' in message:
                logger.info("✅ Gestione dati parziali: OK")
                self.test_results['passed'] += 1
            else:
                logger.error("❌ Gestione dati parziali: Fallita")
                self.test_results['failed'] += 1
                
        except Exception as e:
            logger.error(f"❌ Errore gestione dati parziali: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Partial data handling: {e}")
    
    def test_notification_statistics(self):
        """Test statistiche notifiche"""
        logger.info("📊 TESTING: Statistiche Notifiche")
        
        try:
            stats = self.telegram_manager.get_notification_statistics()
            logger.info(f"📈 Statistiche: {stats}")
            
            if 'error' not in stats:
                logger.info("✅ Recupero statistiche: OK")
                self.test_results['passed'] += 1
            else:
                logger.warning(f"⚠️ Errore statistiche: {stats['error']}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"Statistics: {stats['error']}")
                
        except Exception as e:
            logger.error(f"❌ Errore test statistiche: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Statistics test: {e}")
    
    def print_test_results(self):
        """Stampa risultati finali"""
        logger.info("=" * 60)
        logger.info("📋 RISULTATI FINALI TESTING")
        logger.info("=" * 60)
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"✅ Test Passati: {self.test_results['passed']}")
        logger.info(f"❌ Test Falliti: {self.test_results['failed']}")
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            logger.info("\n🚨 ERRORI DETTAGLIATI:")
            for i, error in enumerate(self.test_results['errors'], 1):
                logger.error(f"{i}. {error}")
        
        if success_rate >= 80:
            logger.info("\n🎉 TESTING COMPLETATO CON SUCCESSO!")
        elif success_rate >= 60:
            logger.info("\n⚠️ TESTING COMPLETATO CON AVVERTIMENTI")
        else:
            logger.info("\n❌ TESTING COMPLETATO CON ERRORI CRITICI")
        
        logger.info("=" * 60)

def main():
    """Funzione principale"""
    print("🧪 TELEGRAM NOTIFICATIONS TEST SUITE")
    print("=" * 50)
    
    tester = TelegramNotificationsTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
