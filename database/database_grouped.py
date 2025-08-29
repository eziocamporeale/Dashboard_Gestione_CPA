#!/usr/bin/env python3
"""
Database Manager per il nuovo schema raggruppato
Gestisce clienti base e account broker separatamente
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class GroupedDatabaseManager:
    """Gestisce il database con schema raggruppato"""
    
    def __init__(self, db_path="cpa_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza il database con le nuove tabelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Leggi e esegui schema SQL
            schema_path = "database/schema_raggruppato.sql"
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            cursor.executescript(schema_sql)
            conn.commit()
            conn.close()
            
            logger.info("✅ Database raggruppato inizializzato")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione database: {e}")
    
    # ===== GESTIONE CLIENTI BASE =====
    
    def aggiungi_cliente_base(self, dati_cliente: Dict[str, Any]) -> Tuple[bool, Any]:
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
    
    def ottieni_cliente_base(self, cliente_id: int) -> Optional[Dict[str, Any]]:
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
    
    def ottieni_tutti_clienti_base(self) -> List[Dict[str, Any]]:
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
    
    def modifica_cliente_base(self, cliente_id: int, dati_modifica: Dict[str, Any]) -> bool:
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
    
    def elimina_cliente_base(self, cliente_id: int) -> bool:
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
    
    def aggiungi_account_broker(self, dati_account: Dict[str, Any]) -> Tuple[bool, Any]:
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
    
    def ottieni_account_broker(self, account_id: int) -> Optional[Dict[str, Any]]:
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
    
    def ottieni_account_per_cliente(self, cliente_base_id: int) -> List[Dict[str, Any]]:
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
    
    def ottieni_tutti_account(self) -> List[Dict[str, Any]]:
        """Ottiene tutti gli account broker"""
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
    
    def modifica_account_broker(self, account_id: int, dati_modifica: Dict[str, Any]) -> bool:
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
    
    def elimina_account_broker(self, account_id: int) -> bool:
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
    
    # ===== VISTE E QUERY COMPLESSE =====
    
    def ottieni_cliente_completo(self, cliente_base_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene cliente base con tutti i suoi account"""
        try:
            cliente_base = self.ottieni_cliente_base(cliente_base_id)
            if not cliente_base:
                return None
            
            accounts = self.ottieni_account_per_cliente(cliente_base_id)
            
            return {
                **cliente_base,
                'accounts': accounts
            }
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento cliente completo: {e}")
            return None
    
    def ottieni_tutti_clienti_completi(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i clienti con i loro account"""
        try:
            clienti_base = self.ottieni_tutti_clienti_base()
            clienti_completi = []
            
            for cliente in clienti_base:
                cliente_completo = self.ottieni_cliente_completo(cliente['id'])
                if cliente_completo:
                    clienti_completi.append(cliente_completo)
            
            return clienti_completi
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento clienti completi: {e}")
            return []
    
    def ottieni_statistiche(self) -> Dict[str, Any]:
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
    
    def cerca_clienti(self, query: str) -> List[Dict[str, Any]]:
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
