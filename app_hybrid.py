#!/usr/bin/env python3
"""
Dashboard Gestione CPA - Versione Ibrida
Supporta sia il vecchio schema che il nuovo schema raggruppato
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu
import logging
import os
import sys

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Import componenti
from components.charts import Charts
from components.client_form import ClientForm
from components.client_table import ClientTable
from components.incroci_tab import IncrociTab
from database.database import DatabaseManager
from database.database_grouped import GroupedDatabaseManager
from database.incroci_manager import IncrociManager
from utils.helpers import *
from utils.backup import DatabaseBackupManager, auto_backup
from utils.secure_backup import create_secure_backup, list_secure_backups, restore_from_secure_backup
from utils.logger import logger

# Configurazione pagina
st.set_page_config(
    page_title="Dashboard CPA - Versione Ibrida",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione database
@st.cache_resource
def init_databases():
    """Inizializza entrambi i database (vecchio e nuovo schema)"""
    try:
        # Database vecchio schema
        db_old = DatabaseManager()
        
        # Database nuovo schema raggruppato
        db_new = GroupedDatabaseManager()
        
        return db_old, db_new
    except Exception as e:
        st.error(f"❌ Errore inizializzazione database: {e}")
        return None, None

# Inizializzazione
db_old, db_new = init_databases()

if db_old is None or db_new is None:
    st.error("❌ Impossibile inizializzare i database. Verifica la configurazione.")
    st.stop()

# Inizializzazione componenti
@st.cache_resource
def init_components():
    """Inizializza i componenti"""
    return {
        'client_form': ClientForm(),
        'client_table': ClientTable(),
        'charts': Charts(),
        'incroci_tab': IncrociTab(IncrociManager(db_old.db_path), db_old)
    }

components = init_components()

# Funzioni helper
def format_currency(value):
    """Formatta valore come valuta"""
    if value is None or value == 0:
        return "€0.00"
    return f"€{value:,.2f}"

def show_success_message(message):
    """Mostra messaggio di successo"""
    st.success(message)
    st.rerun()

def show_error_message(message):
    """Mostra messaggio di errore"""
    st.error(message)

# ===== GESTIONE SCHEMA IBRIDO =====

def show_schema_selector():
    """Mostra selettore schema database"""
    st.sidebar.title("🗄️ Schema Database")
    
    schema_mode = st.sidebar.radio(
        "Modalità Database",
        ["🔄 Schema Originale", "🚀 Schema Raggruppato"],
        help="Scegli quale schema utilizzare per la gestione dei dati"
    )
    
    return schema_mode

def show_old_schema_interface():
    """Interfaccia per il vecchio schema"""
    st.header("📊 Dashboard - Schema Originale")
    
    # Menu principale
    selected = option_menu(
        menu_title=None,
        options=["🏠 Dashboard", "👥 Clienti", "📈 Incroci CPA", "💾 Backup & Sicurezza", "⚙️ Impostazioni"],
        icons=["house", "people", "graph-up", "shield-check", "gear"],
        orientation="horizontal",
    )
    
    if selected == "🏠 Dashboard":
        show_old_dashboard()
    elif selected == "👥 Clienti":
        show_old_clients()
    elif selected == "📈 Incroci CPA":
        show_old_incroci()
    elif selected == "💾 Backup & Sicurezza":
        show_old_backup()
    elif selected == "⚙️ Impostazioni":
        show_old_settings()

def show_new_schema_interface():
    """Interfaccia per il nuovo schema raggruppato"""
    st.header("🚀 Dashboard - Schema Raggruppato")
    
    # Menu principale
    selected = option_menu(
        menu_title=None,
        options=["🏠 Dashboard", "👥 Gestione Clienti", "🏦 Gestione Account", "📊 Statistiche", "⚙️ Impostazioni"],
        icons=["house", "people", "bank", "bar-chart", "gear"],
        orientation="horizontal",
    )
    
    if selected == "🏠 Dashboard":
        show_new_dashboard()
    elif selected == "👥 Gestione Clienti":
        show_new_clients()
    elif selected == "🏦 Gestione Account":
        show_new_accounts()
    elif selected == "📊 Statistiche":
        show_new_statistics()
    elif selected == "⚙️ Impostazioni":
        show_new_settings()

# ===== INTERFACCE VECCHIO SCHEMA =====

def show_old_dashboard():
    """Dashboard del vecchio schema"""
    st.subheader("🏠 Dashboard Principale")
    
    # Statistiche
    try:
        stats = db_old.ottieni_statistiche()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Clienti Totali", stats.get('totale_clienti', 0))
        
        with col2:
            st.metric("🏢 Broker Attivi", stats.get('broker_attivi', 0))
        
        with col3:
            st.metric("💰 Depositi Totali", format_currency(stats.get('depositi_totali', 0)))
        
        with col4:
            st.metric("📈 Incroci Attivi", stats.get('incroci_attivi', 0))
            
    except Exception as e:
        st.error(f"❌ Errore caricamento statistiche: {e}")

def show_old_clients():
    """Gestione clienti vecchio schema"""
    st.subheader("👥 Gestione Clienti")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista Clienti", "➕ Aggiungi Cliente", "📊 Statistiche"])
    
    with tab1:
        try:
            clienti = db_old.ottieni_tutti_clienti()
            if hasattr(clienti, 'empty') and not clienti.empty:
                st.dataframe(clienti, use_container_width=True)
            else:
                st.info("ℹ️ Nessun cliente presente.")
        except Exception as e:
            st.error(f"❌ Errore caricamento clienti: {e}")
    
    with tab2:
        components['client_form'].render()
    
    with tab3:
        try:
            stats = db_old.ottieni_statistiche()
            st.write("**📊 Statistiche Clienti:**")
            st.write(f"• Totale clienti: {stats.get('totale_clienti', 0)}")
            st.write(f"• Broker attivi: {stats.get('broker_attivi', 0)}")
            st.write(f"• Depositi totali: {format_currency(stats.get('depositi_totali', 0))}")
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")

def show_old_incroci():
    """Gestione incroci vecchio schema"""
    st.subheader("📈 Gestione Incroci CPA")
    components['incroci_tab'].render()

def show_old_backup():
    """Backup e sicurezza vecchio schema"""
    st.subheader("💾 Backup & Sicurezza")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💾 Backup Database")
        if st.button("🔄 Backup Automatico"):
            if auto_backup():
                st.success("✅ Backup completato!")
            else:
                st.error("❌ Errore backup")
        
        if st.button("🔒 Backup Sicuro"):
            if create_secure_backup():
                st.success("✅ Backup sicuro completato!")
            else:
                st.error("❌ Errore backup sicuro")
    
    with col2:
        st.subheader("📋 Lista Backup")
        backups = list_secure_backups()
        if backups:
            for backup in backups:
                st.write(f"📁 {backup['filename']} - {backup['size']} - {backup['date']}")

def show_old_settings():
    """Impostazioni vecchio schema"""
    st.subheader("⚙️ Impostazioni")
    
    st.info("🔧 Configurazione Schema Originale")
    
    # Informazioni database
    try:
        stats = db_old.ottieni_statistiche()
        st.write("**📊 Database Originale:**")
        st.write(f"• Clienti: {stats.get('totale_clienti', 0)}")
        st.write(f"• Broker: {stats.get('broker_attivi', 0)}")
        st.write(f"• Depositi: {format_currency(stats.get('depositi_totali', 0))}")
    except Exception as e:
        st.error(f"❌ Errore: {e}")

# ===== INTERFACCE NUOVO SCHEMA =====

def show_new_dashboard():
    """Dashboard del nuovo schema raggruppato"""
    st.subheader("🏠 Dashboard Principale")
    
    # Statistiche
    try:
        stats = db_new.ottieni_statistiche()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Clienti Base", stats['totale_clienti'])
        
        with col2:
            st.metric("🏦 Account Broker", stats['totale_account'])
        
        with col3:
            st.metric("🏢 Broker Attivi", stats['broker_attivi'])
        
        with col4:
            st.metric("💰 Volume Totale", format_currency(stats['volume_totale']))
        
        # Lista clienti completi
        st.subheader("👥 Panoramica Clienti")
        clienti_completi = db_new.ottieni_tutti_clienti_completi()
        
        if not clienti_completi:
            st.info("ℹ️ Nessun cliente presente.")
            return
        
        for cliente in clienti_completi:
            with st.expander(f"👤 {cliente['nome_cliente']} ({cliente['email']})", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if cliente['vps']:
                        st.info(f"🖥️ VPS: {cliente['vps']}")
                    if cliente['note_cliente']:
                        st.info(f"📝 Note: {cliente['note_cliente']}")
                    
                    st.write("**🏦 Account Broker:**")
                    if cliente['accounts']:
                        for account in cliente['accounts']:
                            account_info = f"• {account['broker']} - Conto: {account['numero_conto']} ({account['piattaforma']})"
                            if account['volume_posizione']:
                                account_info += f" - Volume: {format_currency(account['volume_posizione'])}"
                            st.write(account_info)
                    else:
                        st.write("Nessun account broker presente")
                
                with col2:
                    if st.button(f"✏️ Modifica {cliente['nome_cliente']}", key=f"edit_{cliente['id']}"):
                        st.session_state.editing_client = cliente['id']
                    
                    if st.button(f"🗑️ Elimina {cliente['nome_cliente']}", key=f"delete_{cliente['id']}"):
                        if st.button(f"⚠️ Conferma Eliminazione", key=f"confirm_delete_{cliente['id']}"):
                            if db_new.elimina_cliente_base(cliente['id']):
                                show_success_message(f"✅ Cliente {cliente['nome_cliente']} eliminato!")
                            else:
                                show_error_message("❌ Errore eliminazione cliente")
                            
    except Exception as e:
        st.error(f"❌ Errore caricamento dashboard: {e}")

def show_new_clients():
    """Gestione clienti nuovo schema"""
    st.subheader("👥 Gestione Clienti Base")
    
    tab1, tab2 = st.tabs(["📋 Panoramica", "➕ Aggiungi Cliente"])
    
    with tab1:
        show_new_dashboard()  # Riutilizza la dashboard
    
    with tab2:
        st.subheader("➕ Aggiungi Nuovo Cliente Base")
        
        with st.form("add_base_client_form"):
            nome_cliente = st.text_input("Nome Cliente *", key="nome_base")
            email = st.text_input("Email *", key="email_base")
            vps = st.text_input("VPS (opzionale)", key="vps_base")
            note_cliente = st.text_area("Note Cliente (opzionale)", key="note_base")
            
            submitted = st.form_submit_button("➕ Aggiungi Cliente Base")
            
            if submitted:
                if not nome_cliente or not email:
                    show_error_message("❌ Nome e email sono obbligatori!")
                    return
                
                dati_cliente = {
                    'nome_cliente': nome_cliente,
                    'email': email,
                    'vps': vps,
                    'note_cliente': note_cliente
                }
                
                success, result = db_new.aggiungi_cliente_base(dati_cliente)
                
                if success:
                    show_success_message(f"✅ Cliente base {nome_cliente} aggiunto con successo!")
                    auto_backup()
                else:
                    show_error_message(f"❌ Errore aggiunta cliente: {result}")

def show_new_accounts():
    """Gestione account broker nuovo schema"""
    st.subheader("🏦 Gestione Account Broker")
    
    tab1, tab2 = st.tabs(["📋 Panoramica Account", "➕ Aggiungi Account"])
    
    with tab1:
        try:
            accounts = db_new.ottieni_tutti_account()
            
            if not accounts:
                st.info("ℹ️ Nessun account broker presente.")
                return
            
            # Converti in DataFrame per visualizzazione
            df = pd.DataFrame(accounts)
            
            # Mostra tabella
            st.dataframe(
                df[['nome_cliente', 'broker', 'piattaforma', 'numero_conto', 'volume_posizione', 'stato_account']],
                use_container_width=True,
                hide_index=True
            )
            
            # Grafico distribuzione broker
            if len(accounts) > 1:
                broker_counts = df['broker'].value_counts()
                
                fig = px.pie(
                    values=broker_counts.values,
                    names=broker_counts.index,
                    title="📊 Distribuzione Account per Broker"
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Errore caricamento account: {e}")
    
    with tab2:
        st.subheader("🏦 Aggiungi Nuovo Account Broker")
        
        # Ottieni lista clienti base per selezione
        try:
            clienti_base = db_new.ottieni_tutti_clienti_base()
            
            if not clienti_base:
                st.warning("⚠️ Nessun cliente base presente. Aggiungi prima un cliente base.")
                return
            
            with st.form("add_broker_account_form"):
                # Selezione cliente base
                cliente_options = {f"{c['nome_cliente']} ({c['email']})": c['id'] for c in clienti_base}
                cliente_selezionato = st.selectbox("Cliente Base *", options=list(cliente_options.keys()), key="cliente_select")
                cliente_id = cliente_options[cliente_selezionato]
                
                broker = st.text_input("Broker *", key="broker_account")
                piattaforma = st.selectbox("Piattaforma", ["MT4", "MT5", "cTrader", "WebTrader", "Mobile"], key="piattaforma_account")
                numero_conto = st.text_input("Numero Conto *", key="conto_account")
                password = st.text_input("Password *", type="password", key="password_account")
                api_key = st.text_input("API Key (opzionale)", key="api_key_account")
                secret_key = st.text_input("Secret Key (opzionale)", key="secret_key_account")
                ip_address = st.text_input("IP Address (opzionale)", key="ip_account")
                volume_posizione = st.number_input("Volume Posizione", min_value=0.0, value=0.0, step=0.01, key="volume_account")
                ruolo = st.selectbox("Ruolo", ["User", "Admin", "Manager"], key="ruolo_account")
                
                submitted = st.form_submit_button("🏦 Aggiungi Account Broker")
                
                if submitted:
                    if not broker or not numero_conto or not password:
                        show_error_message("❌ Broker, numero conto e password sono obbligatori!")
                        return
                    
                    dati_account = {
                        'cliente_base_id': cliente_id,
                        'broker': broker,
                        'piattaforma': piattaforma,
                        'numero_conto': numero_conto,
                        'password': password,
                        'api_key': api_key,
                        'secret_key': secret_key,
                        'ip_address': ip_address,
                        'volume_posizione': volume_posizione,
                        'ruolo': ruolo
                    }
                    
                    success, result = db_new.aggiungi_account_broker(dati_account)
                    
                    if success:
                        show_success_message(f"✅ Account broker {broker} - {numero_conto} aggiunto con successo!")
                        auto_backup()
                    else:
                        show_error_message(f"❌ Errore aggiunta account: {result}")
                        
        except Exception as e:
            st.error(f"❌ Errore caricamento clienti base: {e}")

def show_new_statistics():
    """Statistiche nuovo schema"""
    st.subheader("📊 Statistiche Dettagliate")
    
    try:
        stats = db_new.ottieni_statistiche()
        accounts = db_new.ottieni_tutti_account()
        
        if not accounts:
            st.info("ℹ️ Nessun dato disponibile per i grafici.")
            return
        
        df = pd.DataFrame(accounts)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Metriche Generali")
            st.metric("👥 Clienti Totali", stats['totale_clienti'])
            st.metric("🏦 Account Totali", stats['totale_account'])
            st.metric("💰 Volume Totale", format_currency(stats['volume_totale']))
            
            # Grafico volume per broker
            if 'volume_posizione' in df.columns and df['volume_posizione'].sum() > 0:
                volume_by_broker = df.groupby('broker')['volume_posizione'].sum()
                
                fig = px.bar(
                    x=volume_by_broker.index,
                    y=volume_by_broker.values,
                    title="💰 Volume per Broker",
                    labels={'x': 'Broker', 'y': 'Volume (€)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏢 Broker Attivi")
            st.metric("Numero Broker", stats['broker_attivi'])
            
            # Grafico distribuzione piattaforme
            if 'piattaforma' in df.columns:
                platform_counts = df['piattaforma'].value_counts()
                
                fig = px.pie(
                    values=platform_counts.values,
                    names=platform_counts.index,
                    title="🖥️ Distribuzione Piattaforme"
                )
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"❌ Errore caricamento statistiche: {e}")

def show_new_settings():
    """Impostazioni nuovo schema"""
    st.subheader("⚙️ Impostazioni Schema Raggruppato")
    
    try:
        stats = db_new.ottieni_statistiche()
        
        st.info(f"""
        **🗄️ Database Schema Raggruppato**
        - Clienti Base: {stats['totale_clienti']}
        - Account Broker: {stats['totale_account']}
        - Broker Attivi: {stats['broker_attivi']}
        - Volume Totale: {format_currency(stats['volume_totale'])}
        """)
        
        # Backup manuale
        if st.button("💾 Backup Manuale"):
            if auto_backup():
                st.success("✅ Backup completato con successo!")
            else:
                st.error("❌ Errore durante il backup")
        
        # Informazioni migrazione
        st.subheader("🔄 Informazioni Migrazione")
        st.success("✅ Database migrato con successo al nuovo schema raggruppato!")
        st.info("""
        **🎯 Vantaggi del Nuovo Schema:**
        - ✅ Email duplicate gestite correttamente
        - ✅ Dati raggruppati per cliente
        - ✅ Account broker separati ma collegati
        - ✅ Struttura scalabile per futuri broker
        """)
        
    except Exception as e:
        st.error(f"❌ Errore caricamento impostazioni: {e}")

# ===== MAIN APP =====

def main():
    """Funzione principale dell'app"""
    st.title("📊 Dashboard Gestione CPA - Versione Ibrida")
    st.markdown("---")
    
    # Selettore schema
    schema_mode = show_schema_selector()
    
    # Mostra interfaccia appropriata
    if schema_mode == "🔄 Schema Originale":
        show_old_schema_interface()
    else:
        show_new_schema_interface()

if __name__ == "__main__":
    main()
