#!/usr/bin/env python3
"""
Gestione degli incroci tra account CPA
Permette di tracciare gli account in hedging per sbloccare bonus senza rischio
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import logging

class IncrociManager:
    """Gestisce gli incroci tra account CPA"""
    
    def __init__(self, db_path: str):
        """Inizializza il manager degli incroci"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza le tabelle per gli incroci"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Crea le tabelle direttamente
                conn.executescript("""
                    -- Tabella principale degli incroci
                    CREATE TABLE IF NOT EXISTS incroci (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome_incrocio TEXT NOT NULL,
                        data_apertura DATE NOT NULL,
                        data_chiusura DATE,
                        stato TEXT DEFAULT 'attivo' CHECK(stato IN ('attivo', 'chiuso', 'sospeso')),
                        pair_trading TEXT NOT NULL,
                        volume_trading REAL NOT NULL,
                        note TEXT,
                        data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Tabella per gli account coinvolti nell'incrocio
                    CREATE TABLE IF NOT EXISTS incroci_account (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        incrocio_id INTEGER NOT NULL,
                        account_id INTEGER NOT NULL,
                        tipo_posizione TEXT NOT NULL CHECK(tipo_posizione IN ('long', 'short')),
                        broker TEXT NOT NULL,
                        piattaforma TEXT NOT NULL,
                        numero_conto TEXT NOT NULL,
                        volume_posizione REAL NOT NULL,
                        data_apertura_posizione DATE,
                        data_chiusura_posizione DATE,
                        stato_posizione TEXT DEFAULT 'aperta' CHECK(stato_posizione IN ('aperta', 'chiusa')),
                        note_posizione TEXT,
                        FOREIGN KEY (incrocio_id) REFERENCES incroci(id) ON DELETE CASCADE
                    );

                    -- Tabella per i bonus CPA sbloccati
                    CREATE TABLE IF NOT EXISTS incroci_bonus (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        incrocio_id INTEGER NOT NULL,
                        tipo_bonus TEXT NOT NULL,
                        importo_bonus REAL NOT NULL,
                        valuta_bonus TEXT DEFAULT 'USD',
                        data_sblocco DATE,
                        stato_bonus TEXT DEFAULT 'attivo' CHECK(stato_bonus IN ('attivo', 'utilizzato', 'scaduto')),
                        note_bonus TEXT,
                        FOREIGN KEY (incrocio_id) REFERENCES incroci(id) ON DELETE CASCADE
                    );
                """)
                
                conn.commit()
                logging.info("Database incroci inizializzato correttamente")
                
        except Exception as e:
            logging.error(f"Errore inizializzazione database incroci: {e}")
            raise
    
    def crea_incrocio(self, dati_incrocio: Dict) -> Tuple[bool, int]:
        """
        Crea un nuovo incrocio tra account
        
        Args:
            dati_incrocio: Dizionario con i dati dell'incrocio
            
        Returns:
            (success, incrocio_id)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Inserisci incrocio principale
                cursor.execute("""
                    INSERT INTO incroci (nome_incrocio, data_apertura, pair_trading, volume_trading, note)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    dati_incrocio['nome_incrocio'],
                    dati_incrocio['data_apertura'],
                    dati_incrocio['pair_trading'],
                    dati_incrocio['volume_trading'],
                    dati_incrocio.get('note', '')
                ))
                
                incrocio_id = cursor.lastrowid
                
                # Inserisci account long
                cursor.execute("""
                    INSERT INTO incroci_account (incrocio_id, account_id, tipo_posizione, broker, 
                                               piattaforma, numero_conto, volume_posizione, data_apertura_posizione)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incrocio_id,
                    dati_incrocio['account_long_id'],
                    'long',
                    dati_incrocio['broker_long'],
                    dati_incrocio['piattaforma_long'],
                    dati_incrocio['conto_long'],
                    dati_incrocio['volume_long'],
                    dati_incrocio['data_apertura']
                ))
                
                # Inserisci account short
                cursor.execute("""
                    INSERT INTO incroci_account (incrocio_id, account_id, tipo_posizione, broker, 
                                               piattaforma, numero_conto, volume_posizione, data_apertura_posizione)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incrocio_id,
                    dati_incrocio['account_short_id'],
                    'short',
                    dati_incrocio['broker_short'],
                    dati_incrocio['piattaforma_short'],
                    dati_incrocio['conto_short'],
                    dati_incrocio['volume_short'],
                    dati_incrocio['data_apertura']
                ))
                
                # Inserisci bonus se specificato
                if 'bonus' in dati_incrocio:
                    for bonus in dati_incrocio['bonus']:
                        cursor.execute("""
                            INSERT INTO incroci_bonus (incrocio_id, tipo_bonus, importo_bonus, valuta_bonus, data_sblocco)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            incrocio_id,
                            bonus['tipo'],
                            bonus['importo'],
                            bonus.get('valuta', 'USD'),
                            bonus.get('data_sblocco', dati_incrocio['data_apertura'])
                        ))
                
                conn.commit()
                logging.info(f"Incrocio creato con ID: {incrocio_id}")
                return True, incrocio_id
                
        except Exception as e:
            logging.error(f"Errore creazione incrocio: {e}")
            return False, str(e)
    
    def ottieni_incroci(self, stato: Optional[str] = None) -> pd.DataFrame:
        """
        Ottiene tutti gli incroci o filtrati per stato
        
        Args:
            stato: Filtro per stato ('attivo', 'chiuso', 'sospeso')
            
        Returns:
            DataFrame con gli incroci
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if stato:
                    query = """
                        SELECT i.*, 
                               c1.nome_cliente as cliente_long, 
                               c2.nome_cliente as cliente_short,
                               ia1.broker as broker_long,
                               ia1.piattaforma as piattaforma_long,
                               ia1.numero_conto as conto_long,
                               ia1.volume_posizione as volume_long,
                               ia2.broker as broker_short,
                               ia2.piattaforma as piattaforma_short,
                               ia2.numero_conto as conto_short,
                               ia2.volume_posizione as volume_short,
                               COALESCE(SUM(b.importo_bonus), 0) as totale_bonus
                        FROM incroci i
                        JOIN incroci_account ia1 ON i.id = ia1.incrocio_id AND ia1.tipo_posizione = 'long'
                        JOIN incroci_account ia2 ON i.id = ia2.incrocio_id AND ia2.tipo_posizione = 'short'
                        JOIN clienti c1 ON ia1.account_id = c1.id
                        JOIN clienti c2 ON ia2.account_id = c2.id
                        LEFT JOIN incroci_bonus b ON i.id = b.incrocio_id
                        WHERE i.stato = ?
                        GROUP BY i.id
                        ORDER BY i.data_apertura DESC
                    """
                    df = pd.read_sql_query(query, conn, params=(stato,))
                else:
                    query = """
                        SELECT i.*, 
                               c1.nome_cliente as cliente_long, 
                               c2.nome_cliente as cliente_short,
                               ia1.broker as broker_long,
                               ia1.piattaforma as piattaforma_long,
                               ia1.numero_conto as conto_long,
                               ia1.volume_posizione as volume_long,
                               ia2.broker as broker_short,
                               ia2.piattaforma as piattaforma_short,
                               ia2.numero_conto as conto_short,
                               ia2.volume_posizione as volume_short,
                               COALESCE(SUM(b.importo_bonus), 0) as totale_bonus
                        FROM incroci i
                        JOIN incroci_account ia1 ON i.id = ia1.incrocio_id AND ia1.tipo_posizione = 'long'
                        JOIN incroci_account ia2 ON i.id = ia2.incrocio_id AND ia2.tipo_posizione = 'short'
                        JOIN clienti c1 ON ia1.account_id = c1.id
                        JOIN clienti c2 ON ia2.account_id = c2.id
                        LEFT JOIN incroci_bonus b ON i.id = b.incrocio_id
                        GROUP BY i.id
                        ORDER BY i.data_apertura DESC
                    """
                    df = pd.read_sql_query(query, conn)
                
                return df
                
        except Exception as e:
            logging.error(f"Errore recupero incroci: {e}")
            return pd.DataFrame()
    
    def ottieni_statistiche_incroci(self) -> Dict:
        """
        Ottiene statistiche complete sugli incroci
        
        Returns:
            Dizionario con le statistiche
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Statistiche generali
                cursor.execute("""
                    SELECT 
                        COUNT(*) as totale_incroci,
                        COUNT(CASE WHEN stato = 'attivo' THEN 1 END) as incroci_attivi,
                        COUNT(CASE WHEN stato = 'chiuso' THEN 1 END) as incroci_chiusi,
                        SUM(volume_trading) as volume_totale
                    FROM incroci
                """)
                stats_generali = cursor.fetchone()
                
                # Statistiche per pair
                cursor.execute("""
                    SELECT pair_trading, COUNT(*) as utilizzi, SUM(volume_trading) as volume_totale
                    FROM incroci
                    GROUP BY pair_trading
                    ORDER BY utilizzi DESC
                """)
                stats_pair = cursor.fetchall()
                
                # Statistiche per broker
                cursor.execute("""
                    SELECT 
                        broker, 
                        COUNT(*) as utilizzi,
                        COUNT(DISTINCT incrocio_id) as incroci_unici
                    FROM incroci_account
                    GROUP BY broker
                    ORDER BY utilizzi DESC
                """)
                stats_broker = cursor.fetchall()
                
                # Bonus totali
                cursor.execute("""
                    SELECT 
                        SUM(importo_bonus) as totale_bonus,
                        COUNT(*) as numero_bonus,
                        COUNT(CASE WHEN stato_bonus = 'attivo' THEN 1 END) as bonus_attivi
                    FROM incroci_bonus
                """)
                stats_bonus = cursor.fetchone()
                
                return {
                    'generali': {
                        'totale_incroci': stats_generali[0],
                        'incroci_attivi': stats_generali[1],
                        'incroci_chiusi': stats_generali[2],
                        'volume_totale': stats_generali[3] or 0
                    },
                    'per_pair': stats_pair,
                    'per_broker': stats_broker,
                    'bonus': {
                        'totale_bonus': stats_bonus[0] or 0,
                        'numero_bonus': stats_bonus[1],
                        'bonus_attivi': stats_bonus[2]
                    }
                }
                
        except Exception as e:
            logging.error(f"Errore recupero statistiche incroci: {e}")
            return {}
    
    def chiudi_incrocio(self, incrocio_id: int, data_chiusura: date, note: str = "") -> bool:
        """
        Chiude un incrocio attivo
        
        Args:
            incrocio_id: ID dell'incrocio
            data_chiusura: Data di chiusura
            note: Note aggiuntive
            
        Returns:
            True se chiuso con successo
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Aggiorna stato incrocio
                cursor.execute("""
                    UPDATE incroci 
                    SET stato = 'chiuso', data_chiusura = ?, note = ?
                    WHERE id = ?
                """, (data_chiusura, note, incrocio_id))
                
                # Aggiorna stato account
                cursor.execute("""
                    UPDATE incroci_account 
                    SET stato_posizione = 'chiusa', data_chiusura_posizione = ?
                    WHERE incrocio_id = ?
                """, (data_chiusura, incrocio_id))
                
                conn.commit()
                logging.info(f"Incrocio {incrocio_id} chiuso correttamente")
                return True
                
        except Exception as e:
            logging.error(f"Errore chiusura incrocio: {e}")
            return False

    def aggiungi_bonus(self, incrocio_id: int, tipo_bonus: str, importo_bonus: float, 
                       valuta_bonus: str = 'USD', data_sblocco: str = None, note: str = "") -> bool:
        """
        Aggiunge un bonus CPA a un incrocio
        
        Args:
            incrocio_id: ID dell'incrocio
            tipo_bonus: Tipo di bonus (es. Welcome Bonus, Deposit Bonus)
            importo_bonus: Importo del bonus
            valuta_bonus: Valuta del bonus (default USD)
            data_sblocco: Data di sblocco del bonus
            note: Note aggiuntive
            
        Returns:
            True se aggiunto con successo
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if not data_sblocco:
                    data_sblocco = datetime.now().strftime('%Y-%m-%d')
                
                cursor.execute("""
                    INSERT INTO incroci_bonus (incrocio_id, tipo_bonus, importo_bonus, valuta_bonus, data_sblocco, note_bonus)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (incrocio_id, tipo_bonus, importo_bonus, valuta_bonus, data_sblocco, note))
                
                conn.commit()
                logging.info(f"Bonus {tipo_bonus} aggiunto all'incrocio {incrocio_id}")
                return True
                
        except Exception as e:
            logging.error(f"Errore aggiunta bonus: {e}")
            return False

    def elimina_incrocio(self, incrocio_id: int) -> bool:
        """
        Elimina completamente un incrocio dal database
        
        Args:
            incrocio_id: ID dell'incrocio da eliminare
            
        Returns:
            True se eliminato con successo
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verifica che l'incrocio esista
                cursor.execute("SELECT id FROM incroci WHERE id = ?", (incrocio_id,))
                if not cursor.fetchone():
                    logging.warning(f"Incrocio {incrocio_id} non trovato")
                    return False
                
                # Elimina l'incrocio (le tabelle correlate si eliminano automaticamente per CASCADE)
                cursor.execute("DELETE FROM incroci WHERE id = ?", (incrocio_id,))
                
                conn.commit()
                logging.info(f"Incrocio {incrocio_id} eliminato con successo")
                return True
                
        except Exception as e:
            logging.error(f"Errore eliminazione incrocio: {e}")
            return False
