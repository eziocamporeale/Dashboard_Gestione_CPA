#!/usr/bin/env python3
"""
Script di migrazione per convertire il database esistente
dal vecchio schema al nuovo schema raggruppato
"""

import sqlite3
import os
from datetime import datetime
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, db_path="cpa_database.db"):
        self.db_path = db_path
        self.backup_path = f"cpa_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
    def create_backup(self):
        """Crea backup del database esistente"""
        try:
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            logger.info(f"✅ Backup creato: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore creazione backup: {e}")
            return False
    
    def migrate_database(self):
        """Esegue la migrazione completa"""
        try:
            # 1. Crea backup
            if not self.create_backup():
                return False
            
            # 2. Connessione al database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info("🔄 Inizio migrazione database...")
            
            # 3. Crea nuove tabelle
            self._create_new_tables(cursor)
            
            # 4. Migra dati esistenti
            self._migrate_existing_data(cursor)
            
            # 5. Verifica integrità
            self._verify_migration(cursor)
            
            # 6. Commit e chiusura
            conn.commit()
            conn.close()
            
            logger.info("✅ Migrazione completata con successo!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore durante migrazione: {e}")
            return False
    
    def _create_new_tables(self, cursor):
        """Crea le nuove tabelle del schema raggruppato"""
        logger.info("📋 Creazione nuove tabelle...")
        
        # Leggi schema SQL
        schema_path = "database/schema_raggruppato.sql"
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Esegui script SQL
            cursor.executescript(schema_sql)
            logger.info("✅ Nuove tabelle create")
        else:
            logger.error(f"❌ File schema non trovato: {schema_path}")
            raise FileNotFoundError(f"Schema file non trovato: {schema_path}")
    
    def _migrate_existing_data(self, cursor):
        """Migra i dati esistenti al nuovo schema"""
        logger.info("🔄 Migrazione dati esistenti...")
        
        # Ottieni tutti i clienti esistenti
        cursor.execute("SELECT * FROM clienti")
        clienti_esistenti = cursor.fetchall()
        
        logger.info(f"📊 Trovati {len(clienti_esistenti)} clienti da migrare")
        
        for cliente in clienti_esistenti:
            try:
                # Estrai dati cliente
                cliente_id, nome, email, password, broker, data_reg, volume, piattaforma, \
                numero_conto, api_key, ip_address, ruolo, secret_key, created_at, updated_at = cliente
                
                # 1. Inserisci cliente base (se non esiste già)
                cursor.execute("""
                    INSERT OR IGNORE INTO clienti_base (nome_cliente, email, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (nome, email, created_at, updated_at))
                
                # Ottieni ID cliente base
                cursor.execute("SELECT id FROM clienti_base WHERE email = ?", (email,))
                cliente_base_id = cursor.fetchone()[0]
                
                # 2. Inserisci account broker
                cursor.execute("""
                    INSERT INTO account_broker (
                        cliente_base_id, broker, piattaforma, numero_conto, password,
                        api_key, secret_key, ip_address, volume_posizione, ruolo,
                        data_registrazione, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cliente_base_id, broker, piattaforma, numero_conto, password,
                    api_key, secret_key, ip_address, volume, ruolo,
                    data_reg, created_at, updated_at
                ))
                
                logger.info(f"✅ Migrato cliente: {nome} - {broker}")
                
            except Exception as e:
                logger.error(f"❌ Errore migrazione cliente {cliente}: {e}")
                continue
    
    def _verify_migration(self, cursor):
        """Verifica che la migrazione sia avvenuta correttamente"""
        logger.info("🔍 Verifica migrazione...")
        
        # Conta clienti base
        cursor.execute("SELECT COUNT(*) FROM clienti_base")
        clienti_base_count = cursor.fetchone()[0]
        
        # Conta account broker
        cursor.execute("SELECT COUNT(*) FROM account_broker")
        account_count = cursor.fetchone()[0]
        
        # Conta clienti originali
        cursor.execute("SELECT COUNT(*) FROM clienti")
        clienti_originali_count = cursor.fetchone()[0]
        
        logger.info(f"📊 Verifica migrazione:")
        logger.info(f"   • Clienti base: {clienti_base_count}")
        logger.info(f"   • Account broker: {account_count}")
        logger.info(f"   • Clienti originali: {clienti_originali_count}")
        
        if account_count == clienti_originali_count:
            logger.info("✅ Migrazione verificata con successo!")
        else:
            logger.warning("⚠️ Discrepanza nei conteggi - verificare manualmente")
    
    def rollback_migration(self):
        """Ripristina il database dal backup"""
        try:
            import shutil
            if os.path.exists(self.backup_path):
                shutil.copy2(self.backup_path, self.db_path)
                logger.info(f"✅ Rollback completato da: {self.backup_path}")
                return True
            else:
                logger.error("❌ File backup non trovato")
                return False
        except Exception as e:
            logger.error(f"❌ Errore rollback: {e}")
            return False

def main():
    """Funzione principale"""
    print("🚀 MIGRAZIONE DATABASE A SCHEMA RAGGRUPPATO")
    print("=" * 60)
    
    migrator = DatabaseMigrator()
    
    # Chiedi conferma
    response = input("⚠️ ATTENZIONE: Questa operazione modificherà il database. Continuare? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migrazione annullata")
        return
    
    # Esegui migrazione
    if migrator.migrate_database():
        print("\n🎉 MIGRAZIONE COMPLETATA!")
        print(f"📁 Backup salvato in: {migrator.backup_path}")
        print("\n📋 PROSSIMI PASSI:")
        print("1. Testa la nuova applicazione")
        print("2. Verifica che tutti i dati siano corretti")
        print("3. Se tutto OK, puoi eliminare il backup")
        print("4. Se problemi, usa: migrator.rollback_migration()")
    else:
        print("\n❌ MIGRAZIONE FALLITA!")
        print("📁 Backup disponibile per ripristino")

if __name__ == "__main__":
    main()
