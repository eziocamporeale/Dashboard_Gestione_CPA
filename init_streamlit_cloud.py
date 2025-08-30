#!/usr/bin/env python3
"""
Script di inizializzazione forzata per Streamlit Cloud
Crea le tabelle mancanti nel database locale
"""

import sqlite3
import os
import streamlit as st

def init_database_streamlit_cloud():
    """Inizializza il database per Streamlit Cloud"""
    
    # Percorso database per Streamlit Cloud
    db_path = "cpa_database.db"
    
    try:
        # Connessione al database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        st.info("🔧 Inizializzazione database per Streamlit Cloud...")
        
        # Verifica tabelle esistenti
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelle_esistenti = [row[0] for row in cursor.fetchall()]
        
        st.write(f"📋 Tabelle esistenti: {tabelle_esistenti}")
        
        # Crea tabella incroci se non esiste
        if 'incroci' not in tabelle_esistenti:
            st.write("➕ Creazione tabella incroci...")
            cursor.execute("""
                CREATE TABLE incroci (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_incrocio TEXT NOT NULL,
                    data_apertura DATE NOT NULL,
                    data_chiusura DATE,
                    stato TEXT DEFAULT 'attivo',
                    pair_trading TEXT,
                    volume_trading REAL DEFAULT 0,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            st.success("✅ Tabella incroci creata!")
        
        # Crea tabella incroci_account se non esiste
        if 'incroci_account' not in tabelle_esistenti:
            st.write("➕ Creazione tabella incroci_account...")
            cursor.execute("""
                CREATE TABLE incroci_account (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incrocio_id INTEGER NOT NULL,
                    tipo_posizione TEXT NOT NULL CHECK (tipo_posizione IN ('long', 'short')),
                    broker TEXT NOT NULL,
                    piattaforma TEXT DEFAULT 'MT4',
                    numero_conto TEXT,
                    volume_posizione REAL DEFAULT 0,
                    note_posizione TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            st.success("✅ Tabella incroci_account creata!")
        
        # Crea tabella incroci_bonus se non esiste
        if 'incroci_bonus' not in tabelle_esistenti:
            st.write("➕ Creazione tabella incroci_bonus...")
            cursor.execute("""
                CREATE TABLE incroci_bonus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incrocio_id INTEGER NOT NULL,
                    importo_bonus REAL NOT NULL,
                    data_bonus DATE NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            st.success("✅ Tabella incroci_bonus creata!")
        
        # Commit delle modifiche
        conn.commit()
        
        # Verifica finale
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelle_finali = [row[0] for row in cursor.fetchall()]
        
        st.success(f"🎉 Database inizializzato! Tabelle: {tabelle_finali}")
        
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"❌ Errore inizializzazione database: {e}")
        return False

if __name__ == "__main__":
    st.title("🔧 Inizializzazione Database Streamlit Cloud")
    
    if st.button("🚀 Inizializza Database"):
        success = init_database_streamlit_cloud()
        if success:
            st.balloons()
            st.success("🎉 Database inizializzato con successo!")
        else:
            st.error("❌ Errore durante l'inizializzazione")
