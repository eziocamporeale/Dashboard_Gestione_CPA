import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="cpa_database.db"):
        """Inizializza il gestore del database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza il database e crea le tabelle se non esistono"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella principale clienti
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_cliente TEXT NOT NULL,
                email TEXT NOT NULL,
                password_email TEXT,
                broker TEXT NOT NULL,
                data_registrazione DATE NOT NULL,
                deposito REAL NOT NULL,
                piattaforma TEXT NOT NULL,
                numero_conto TEXT NOT NULL,
                password_conto TEXT,
                vps_ip TEXT,
                vps_username TEXT,
                vps_password TEXT,
                data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella per i campi aggiuntivi dinamici
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campi_aggiuntivi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                nome_campo TEXT NOT NULL,
                valore_campo TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clienti (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabella per i broker
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_broker TEXT UNIQUE NOT NULL,
                sito_web TEXT,
                note TEXT
            )
        ''')
        
        # Tabella per le piattaforme
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS piattaforme (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_piattaforma TEXT UNIQUE NOT NULL,
                descrizione TEXT
            )
        ''')
        
        # Inserimento dati di default per le piattaforme
        piattaforme_default = [
            ("MT4", "MetaTrader 4"),
            ("MT5", "MetaTrader 5"),
            ("cTrader", "cTrader"),
            ("Altro", "Altra piattaforma")
        ]
        
        for piattaforma in piattaforme_default:
            cursor.execute('''
                INSERT OR IGNORE INTO piattaforme (nome_piattaforma, descrizione)
                VALUES (?, ?)
            ''', piattaforma)
        
        conn.commit()
        conn.close()
    
    def aggiungi_cliente(self, dati_cliente, campi_aggiuntivi=None):
        """Aggiunge un nuovo cliente al database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Inserimento cliente principale
            cursor.execute('''
                INSERT INTO clienti (
                    nome_cliente, email, password_email, broker, data_registrazione,
                    deposito, piattaforma, numero_conto, password_conto,
                    vps_ip, vps_username, vps_password
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dati_cliente['nome_cliente'],
                dati_cliente['email'],
                dati_cliente.get('password_email', ''),
                dati_cliente['broker'],
                dati_cliente['data_registrazione'],
                dati_cliente['deposito'],
                dati_cliente['piattaforma'],
                dati_cliente['numero_conto'],
                dati_cliente.get('password_conto', ''),
                dati_cliente.get('vps_ip', ''),
                dati_cliente.get('vps_username', ''),
                dati_cliente.get('vps_password', '')
            ))
            
            cliente_id = cursor.lastrowid
            
            # Inserimento campi aggiuntivi se presenti
            if campi_aggiuntivi:
                for campo in campi_aggiuntivi:
                    if campo['nome'] and campo['valore']:
                        cursor.execute('''
                            INSERT INTO campi_aggiuntivi (cliente_id, nome_campo, valore_campo)
                            VALUES (?, ?, ?)
                        ''', (cliente_id, campo['nome'], campo['valore']))
            
            conn.commit()
            conn.close()
            return True, cliente_id
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False, str(e)
    
    def ottieni_tutti_clienti(self):
        """Ottiene tutti i clienti dal database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT c.*, GROUP_CONCAT(ca.nome_campo || ': ' || ca.valore_campo, '; ') as campi_aggiuntivi
                FROM clienti c
                LEFT JOIN campi_aggiuntivi ca ON c.id = ca.cliente_id
                GROUP BY c.id
                ORDER BY c.data_creazione DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def ottieni_statistiche(self):
        """Ottiene le statistiche generali"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Totale clienti
            cursor.execute("SELECT COUNT(*) FROM clienti")
            totale_clienti = cursor.fetchone()[0]
            
            # Broker attivi
            cursor.execute("SELECT COUNT(DISTINCT broker) FROM clienti")
            broker_attivi = cursor.fetchone()[0]
            
            # Depositi totali
            cursor.execute("SELECT SUM(deposito) FROM clienti")
            depositi_totali = cursor.fetchone()[0] or 0
            
            # CPA attive (clienti con deposito > 0)
            cursor.execute("SELECT COUNT(*) FROM clienti WHERE deposito > 0")
            cpa_attive = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'totale_clienti': totale_clienti,
                'broker_attivi': broker_attivi,
                'depositi_totali': depositi_totali,
                'cpa_attive': cpa_attive
            }
            
        except Exception as e:
            return {
                'totale_clienti': 0,
                'broker_attivi': 0,
                'depositi_totali': 0,
                'cpa_attive': 0
            }
    
    def elimina_cliente(self, cliente_id):
        """Elimina un cliente dal database"""
        try:
            import logging
            logging.info(f"🔍 Tentativo eliminazione cliente ID: {cliente_id} (tipo: {type(cliente_id)})")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verifica che il cliente esista prima di eliminarlo
            cursor.execute("SELECT COUNT(*) FROM clienti WHERE id = ?", (cliente_id,))
            count_before = cursor.fetchone()[0]
            logging.info(f"📊 Clienti trovati prima eliminazione: {count_before}")
            
            if count_before == 0:
                logging.warning(f"⚠️ Cliente ID {cliente_id} non trovato nel database")
                conn.close()
                return False
            
            # Esegui eliminazione
            cursor.execute("DELETE FROM clienti WHERE id = ?", (cliente_id,))
            rows_deleted = cursor.rowcount
            logging.info(f"🗑️ Righe eliminate: {rows_deleted}")
            
            # Verifica eliminazione
            cursor.execute("SELECT COUNT(*) FROM clienti WHERE id = ?", (cliente_id,))
            count_after = cursor.fetchone()[0]
            logging.info(f"📊 Clienti trovati dopo eliminazione: {count_after}")
            
            # Commit transazione
            conn.commit()
            logging.info(f"💾 Transazione committata")
            
            conn.close()
            
            success = count_after == 0 and rows_deleted > 0
            logging.info(f"✅ Eliminazione cliente {cliente_id}: {'SUCCESSO' if success else 'FALLITA'}")
            
            return success
            
        except Exception as e:
            import logging
            logging.error(f"❌ Errore eliminazione cliente {cliente_id}: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def modifica_cliente(self, cliente_id, dati_cliente, campi_aggiuntivi=None):
        """Modifica un cliente esistente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Aggiornamento cliente principale
            cursor.execute('''
                UPDATE clienti SET
                    nome_cliente = ?, email = ?, password_email = ?, broker = ?,
                    data_registrazione = ?, deposito = ?, piattaforma = ?,
                    numero_conto = ?, password_conto = ?, vps_ip = ?,
                    vps_username = ?, vps_password = ?, data_modifica = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                dati_cliente['nome_cliente'],
                dati_cliente['email'],
                dati_cliente.get('password_email', ''),
                dati_cliente['broker'],
                dati_cliente['data_registrazione'],
                dati_cliente['deposito'],
                dati_cliente['piattaforma'],
                dati_cliente['numero_conto'],
                dati_cliente.get('password_conto', ''),
                dati_cliente.get('vps_ip', ''),
                dati_cliente.get('vps_username', ''),
                dati_cliente.get('vps_password', ''),
                cliente_id
            ))
            
            # Rimozione campi aggiuntivi esistenti
            cursor.execute("DELETE FROM campi_aggiuntivi WHERE cliente_id = ?", (cliente_id,))
            
            # Inserimento nuovi campi aggiuntivi
            if campi_aggiuntivi:
                for campo in campi_aggiuntivi:
                    if campo['nome'] and campo['valore']:
                        cursor.execute('''
                            INSERT INTO campi_aggiuntivi (cliente_id, nome_campo, valore_campo)
                            VALUES (?, ?, ?)
                        ''', (cliente_id, campo['nome'], campo['valore']))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

    def ottieni_broker_predefiniti(self):
        """Restituisce la lista dei broker predefiniti più comuni"""
        return [
            "FXPro",
            "Pepperstone", 
            "IC Markets",
            "XM",
            "FBS",
            "Exness",
            "RoboForex",
            "Vantage",
            "AvaTrade",
            "Plus500",
            "eToro",
            "IG",
            "Saxo Bank",
            "Interactive Brokers",
            "OANDA",
            "Dukascopy",
            "Swissquote",
            "DEGIRO",
            "Binance",
            "Coinbase"
        ]
    
    def ottieni_tutti_broker(self):
        """Restituisce tutti i broker dal database (predefiniti + personalizzati)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ottieni broker dai clienti esistenti
            cursor.execute("SELECT DISTINCT broker FROM clienti WHERE broker IS NOT NULL AND broker != '' ORDER BY broker")
            broker_db = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # Combina broker predefiniti con quelli del database
            broker_predefiniti = self.ottieni_broker_predefiniti()
            tutti_broker = list(set(broker_predefiniti + broker_db))
            tutti_broker.sort()
            
            return tutti_broker
            
        except Exception as e:
            # In caso di errore, restituisci solo i predefiniti
            return self.ottieni_broker_predefiniti()

    def ottieni_broker(self):
        """Restituisce i broker dalla tabella broker del database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT nome_broker FROM broker ORDER BY nome_broker")
            broker_db = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            if broker_db:
                return pd.DataFrame({'nome_broker': broker_db})
            else:
                return pd.DataFrame()
                
        except Exception as e:
            return pd.DataFrame()

    def esegui_query(self, query, params=None):
        """Esegue una query SQL generica"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
