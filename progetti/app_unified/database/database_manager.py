#!/usr/bin/env python3
"""
Database Manager Unificato per Schema Raggruppato
Gestisce clienti base e account broker in modo pulito e efficiente
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedDatabaseManager:
    """Database Manager unificato per schema raggruppato"""
    
    def __init__(self, db_path="cpa_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crea tabelle se non esistono
            self._create_tables(cursor)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database unificato inizializzato correttamente")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione database: {e}")
            raise
    
    def _create_tables(self, cursor):
        """Crea le tabelle del database"""
        
        # Tabella clienti base
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clienti_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_cliente TEXT NOT NULL,
                email TEXT NOT NULL,
                vps TEXT,
                note_cliente TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella account broker
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_broker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_base_id INTEGER NOT NULL,
                broker TEXT NOT NULL,
                piattaforma TEXT DEFAULT 'MT4',
                numero_conto TEXT NOT NULL,
                password TEXT NOT NULL,
                api_key TEXT,
                secret_key TEXT,
                ip_address TEXT,
                volume_posizione REAL DEFAULT 0,
                ruolo TEXT DEFAULT 'User',
                stato_account TEXT DEFAULT 'attivo',
                data_registrazione DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_base_id) REFERENCES clienti_base(id) ON DELETE CASCADE
            )
        """)
        
        # Tabella incroci (mantenuta per compatibilità)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incroci (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_apertura DATE NOT NULL,
                data_chiusura DATE,
                stato TEXT DEFAULT 'aperto',
                profitto_perdita REAL DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella incroci_account (modificata per schema raggruppato)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incroci_account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incrocio_id INTEGER NOT NULL,
                account_broker_id INTEGER NOT NULL,
                tipo_posizione TEXT NOT NULL CHECK (tipo_posizione IN ('long', 'short')),
                volume_posizione REAL DEFAULT 0,
                data_apertura_posizione DATE,
                data_chiusura_posizione DATE,
                stato_posizione TEXT,
                note_posizione TEXT,
                FOREIGN KEY (incrocio_id) REFERENCES incroci(id),
                FOREIGN KEY (account_broker_id) REFERENCES account_broker(id)
            )
        """)
        
        # Tabella broker predefiniti
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS broker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_broker TEXT NOT NULL UNIQUE,
                piattaforma_default TEXT DEFAULT 'MT4',
                note_broker TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella piattaforme
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS piattaforme (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_piattaforma TEXT NOT NULL UNIQUE,
                descrizione TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inserisci broker predefiniti se non esistono
        broker_predefiniti = [
            ('AxiTrader', 'MT4', 'Broker australiano'),
            ('IC Markets', 'MT4', 'Broker australiano'),
            ('Pepperstone', 'MT4', 'Broker australiano'),
            ('FXPro', 'MT4', 'Broker cipriota'),
            ('XM', 'MT4', 'Broker cipriota'),
            ('FBS', 'MT4', 'Broker internazionale'),
            ('Exness', 'MT4', 'Broker internazionale'),
            ('RoboForex', 'MT4', 'Broker internazionale')
        ]
        
        for nome, piattaforma, note in broker_predefiniti:
            cursor.execute("""
                INSERT OR IGNORE INTO broker (nome_broker, piattaforma_default, note_broker)
                VALUES (?, ?, ?)
            """, (nome, piattaforma, note))
        
        # Inserisci piattaforme predefinite
        piattaforme_predefinite = [
            ('MT4', 'MetaTrader 4'),
            ('MT5', 'MetaTrader 5'),
            ('cTrader', 'cTrader Platform'),
            ('WebTrader', 'Web Trading Platform'),
            ('Mobile', 'Mobile Trading App')
        ]
        
        for nome, descrizione in piattaforme_predefinite:
            cursor.execute("""
                INSERT OR IGNORE INTO piattaforme (nome_piattaforma, descrizione)
                VALUES (?, ?)
            """, (nome, descrizione))
        
        # Indici per performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clienti_base_email ON clienti_base(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clienti_base_nome ON clienti_base(nome_cliente)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_broker_cliente ON account_broker(cliente_base_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_broker_broker ON account_broker(broker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_broker_conto ON account_broker(numero_conto)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_broker_nome ON broker(nome_broker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_piattaforme_nome ON piattaforme(nome_piattaforma)")
        
        logger.info("✅ Tabelle create correttamente")
    
    # ===== GESTIONE CLIENTI BASE =====
    
    def add_cliente_base(self, dati_cliente: Dict[str, Any]) -> Tuple[bool, Any]:
        """Aggiunge un nuovo cliente base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO clienti_base (nome_cliente, email, vps, note_cliente, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                dati_cliente['nome_cliente'],
                dati_cliente['email'],
                dati_cliente.get('vps', ''),
                dati_cliente.get('note_cliente', ''),
                datetime.now(),
                datetime.now()
            ))
            
            cliente_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cliente base aggiunto: {dati_cliente['nome_cliente']}")
            return True, cliente_id
            
        except Exception as e:
            logger.error(f"❌ Errore aggiunta cliente base: {e}")
            return False, str(e)
    
    def get_cliente_base(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene un cliente base per ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome_cliente, email, vps, note_cliente, created_at, updated_at
                FROM clienti_base WHERE id = ?
            """, (cliente_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'nome_cliente': result[1],
                    'email': result[2],
                    'vps': result[3],
                    'note_cliente': result[4],
                    'created_at': result[5],
                    'updated_at': result[6]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento cliente base: {e}")
            return None
    
    def get_all_clienti_base(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i clienti base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome_cliente, email, vps, note_cliente, created_at, updated_at
                FROM clienti_base ORDER BY nome_cliente
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            clienti = []
            for result in results:
                clienti.append({
                    'id': result[0],
                    'nome_cliente': result[1],
                    'email': result[2],
                    'vps': result[3],
                    'note_cliente': result[4],
                    'created_at': result[5],
                    'updated_at': result[6]
                })
            
            return clienti
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento clienti base: {e}")
            return []
    
    def update_cliente_base(self, cliente_id: int, dati_modifica: Dict[str, Any]) -> bool:
        """Modifica un cliente base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Costruisci query dinamica
            fields = []
            values = []
            for key, value in dati_modifica.items():
                if key in ['nome_cliente', 'email', 'vps', 'note_cliente']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(datetime.now())  # updated_at
            values.append(cliente_id)      # WHERE id = ?
            
            query = f"""
                UPDATE clienti_base 
                SET {', '.join(fields)}, updated_at = ?
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cliente base modificato: {cliente_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore modifica cliente base: {e}")
            return False
    
    def delete_cliente_base(self, cliente_id: int) -> bool:
        """Elimina un cliente base e tutti i suoi account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Elimina prima gli account (CASCADE)
            cursor.execute("DELETE FROM account_broker WHERE cliente_base_id = ?", (cliente_id,))
            
            # Poi elimina il cliente base
            cursor.execute("DELETE FROM clienti_base WHERE id = ?", (cliente_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cliente base eliminato: {cliente_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore eliminazione cliente base: {e}")
            return False
    
    # ===== GESTIONE ACCOUNT BROKER =====
    
    def add_account_broker(self, dati_account: Dict[str, Any]) -> Tuple[bool, Any]:
        """Aggiunge un nuovo account broker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO account_broker (
                    cliente_base_id, broker, piattaforma, numero_conto, password,
                    api_key, secret_key, ip_address, volume_posizione, ruolo,
                    data_registrazione, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dati_account['cliente_base_id'],
                dati_account['broker'],
                dati_account.get('piattaforma', 'MT4'),
                dati_account['numero_conto'],
                dati_account['password'],
                dati_account.get('api_key', ''),
                dati_account.get('secret_key', ''),
                dati_account.get('ip_address', ''),
                dati_account.get('volume_posizione', 0.0),
                dati_account.get('ruolo', 'User'),
                dati_account.get('data_registrazione', date.today()),
                datetime.now(),
                datetime.now()
            ))
            
            account_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Account broker aggiunto: {dati_account['broker']} - {dati_account['numero_conto']}")
            return True, account_id
            
        except Exception as e:
            logger.error(f"❌ Errore aggiunta account broker: {e}")
            return False, str(e)
    
    def get_account_broker(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene un account broker per ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, cliente_base_id, broker, piattaforma, numero_conto, password,
                       api_key, secret_key, ip_address, volume_posizione, ruolo,
                       stato_account, data_registrazione, created_at, updated_at
                FROM account_broker WHERE id = ?
            """, (account_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'cliente_base_id': result[1],
                    'broker': result[2],
                    'piattaforma': result[3],
                    'numero_conto': result[4],
                    'password': result[5],
                    'api_key': result[6],
                    'secret_key': result[7],
                    'ip_address': result[8],
                    'volume_posizione': result[9],
                    'ruolo': result[10],
                    'stato_account': result[11],
                    'data_registrazione': result[12],
                    'created_at': result[13],
                    'updated_at': result[14]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento account broker: {e}")
            return None
    
    def get_accounts_by_cliente(self, cliente_base_id: int) -> List[Dict[str, Any]]:
        """Ottiene tutti gli account broker di un cliente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, broker, piattaforma, numero_conto, volume_posizione,
                       stato_account, data_registrazione, created_at
                FROM account_broker 
                WHERE cliente_base_id = ? 
                ORDER BY broker, numero_conto
            """, (cliente_base_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            accounts = []
            for result in results:
                accounts.append({
                    'id': result[0],
                    'broker': result[1],
                    'piattaforma': result[2],
                    'numero_conto': result[3],
                    'volume_posizione': result[4],
                    'stato_account': result[5],
                    'data_registrazione': result[6],
                    'created_at': result[7]
                })
            
            return accounts
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento account per cliente: {e}")
            return []
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Ottiene tutti gli account broker con info cliente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ab.id, ab.broker, ab.piattaforma, ab.numero_conto, ab.volume_posizione,
                       ab.stato_account, ab.data_registrazione, ab.created_at,
                       cb.nome_cliente, cb.email
                FROM account_broker ab
                JOIN clienti_base cb ON ab.cliente_base_id = cb.id
                ORDER BY cb.nome_cliente, ab.broker
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            accounts = []
            for result in results:
                accounts.append({
                    'id': result[0],
                    'broker': result[1],
                    'piattaforma': result[2],
                    'numero_conto': result[3],
                    'volume_posizione': result[4],
                    'stato_account': result[5],
                    'data_registrazione': result[6],
                    'created_at': result[7],
                    'nome_cliente': result[8],
                    'email': result[9]
                })
            
            return accounts
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento tutti account: {e}")
            return []
    
    def update_account_broker(self, account_id: int, dati_modifica: Dict[str, Any]) -> bool:
        """Modifica un account broker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Costruisci query dinamica
            fields = []
            values = []
            for key, value in dati_modifica.items():
                if key in ['broker', 'piattaforma', 'numero_conto', 'password', 'api_key', 
                          'secret_key', 'ip_address', 'volume_posizione', 'ruolo', 'stato_account']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(datetime.now())  # updated_at
            values.append(account_id)      # WHERE id = ?
            
            query = f"""
                UPDATE account_broker 
                SET {', '.join(fields)}, updated_at = ?
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Account broker modificato: {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore modifica account broker: {e}")
            return False
    
    def delete_account_broker(self, account_id: int) -> bool:
        """Elimina un account broker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM account_broker WHERE id = ?", (account_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Account broker eliminato: {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore eliminazione account broker: {e}")
            return False
    
    # ===== QUERY COMPLESSE =====
    
    def get_cliente_completo(self, cliente_base_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene cliente base con tutti i suoi account"""
        try:
            cliente_base = self.get_cliente_base(cliente_base_id)
            if not cliente_base:
                return None
            
            accounts = self.get_accounts_by_cliente(cliente_base_id)
            
            return {
                **cliente_base,
                'accounts': accounts
            }
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento cliente completo: {e}")
            return None
    
    def get_all_clienti_completi(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i clienti con i loro account"""
        try:
            clienti_base = self.get_all_clienti_base()
            clienti_completi = []
            
            for cliente in clienti_base:
                cliente_completo = self.get_cliente_completo(cliente['id'])
                if cliente_completo:
                    clienti_completi.append(cliente_completo)
            
            return clienti_completi
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento clienti completi: {e}")
            return []
    
    def get_statistiche(self) -> Dict[str, Any]:
        """Ottiene statistiche del database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conta clienti base
            cursor.execute("SELECT COUNT(*) FROM clienti_base")
            totale_clienti = cursor.fetchone()[0]
            
            # Conta account broker
            cursor.execute("SELECT COUNT(*) FROM account_broker")
            totale_account = cursor.fetchone()[0]
            
            # Conta broker attivi
            cursor.execute("SELECT COUNT(DISTINCT broker) FROM account_broker")
            broker_attivi = cursor.fetchone()[0]
            
            # Volume totale
            cursor.execute("SELECT SUM(volume_posizione) FROM account_broker")
            volume_totale = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'totale_clienti': totale_clienti,
                'totale_account': totale_account,
                'broker_attivi': broker_attivi,
                'volume_totale': volume_totale
            }
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento statistiche: {e}")
            return {}
    
    def search_clienti(self, query: str) -> List[Dict[str, Any]]:
        """Cerca clienti per nome o email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT cb.id, cb.nome_cliente, cb.email, cb.vps
                FROM clienti_base cb
                WHERE cb.nome_cliente LIKE ? OR cb.email LIKE ?
                ORDER BY cb.nome_cliente
            """, (f'%{query}%', f'%{query}%'))
            
            results = cursor.fetchall()
            conn.close()
            
            clienti = []
            for result in results:
                clienti.append({
                    'id': result[0],
                    'nome_cliente': result[1],
                    'email': result[2],
                    'vps': result[3]
                })
            
            return clienti
            
        except Exception as e:
            logger.error(f"❌ Errore ricerca clienti: {e}")
            return []
    
    # ===== GESTIONE BROKER PREDEFINITI =====
    
    def get_all_broker(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i broker predefiniti"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome_broker, piattaforma_default, note_broker, created_at, updated_at
                FROM broker ORDER BY nome_broker
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            broker_list = []
            for result in results:
                broker_list.append({
                    'id': result[0],
                    'nome_broker': result[1],
                    'piattaforma_default': result[2],
                    'note_broker': result[3],
                    'created_at': result[4],
                    'updated_at': result[5]
                })
            
            return broker_list
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento broker: {e}")
            return []
    
    def add_broker(self, dati_broker: Dict[str, Any]) -> Tuple[bool, Any]:
        """Aggiunge un nuovo broker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO broker (nome_broker, piattaforma_default, note_broker, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                dati_broker['nome_broker'],
                dati_broker.get('piattaforma_default', 'MT4'),
                dati_broker.get('note_broker', ''),
                datetime.now(),
                datetime.now()
            ))
            
            broker_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Broker aggiunto: {dati_broker['nome_broker']}")
            return True, broker_id
            
        except Exception as e:
            logger.error(f"❌ Errore aggiunta broker: {e}")
            return False, str(e)
    
    def update_broker(self, broker_id: int, dati_modifica: Dict[str, Any]) -> bool:
        """Modifica un broker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fields = []
            values = []
            for key, value in dati_modifica.items():
                if key in ['nome_broker', 'piattaforma_default', 'note_broker']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(datetime.now())  # updated_at
            values.append(broker_id)      # WHERE id = ?
            
            query = f"""
                UPDATE broker 
                SET {', '.join(fields)}, updated_at = ?
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Broker modificato: {broker_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore modifica broker: {e}")
            return False
    
    def delete_broker(self, broker_id: int) -> bool:
        """Elimina un broker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM broker WHERE id = ?", (broker_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Broker eliminato: {broker_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore eliminazione broker: {e}")
            return False
    
    def get_all_piattaforme(self) -> List[Dict[str, Any]]:
        """Ottiene tutte le piattaforme"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome_piattaforma, descrizione, created_at
                FROM piattaforme ORDER BY nome_piattaforma
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            piattaforme_list = []
            for result in results:
                piattaforme_list.append({
                    'id': result[0],
                    'nome_piattaforma': result[1],
                    'descrizione': result[2],
                    'created_at': result[3]
                })
            
            return piattaforme_list
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento piattaforme: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Testa la connessione al database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test query semplice
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Errore test connessione: {e}")
            return False
