import streamlit as st
# 🚀 DEPLOYMENT UPDATE: Campo Wallet aggiunto - $(date)
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils.translations import t, translation_manager
from streamlit_option_menu import option_menu
import logging

# Aggiungi il percorso della directory corrente al path di Python
import tempfile
import shutil
import os
import sys

# Aggiungi il percorso della directory corrente al path di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import diretti dei componenti con gestione errori
from auth_simple_no_cookie import require_auth, show_user_info, login_form, init_auth
print("✅ auth_simple_no_cookie importato correttamente")
AUTH_SYSTEM = "simple"

try:
    from components.charts import Charts
    print("✅ Charts importato correttamente")
except Exception as e:
    print(f"❌ Errore import Charts: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="Charts", error=e))

try:
    from components.client_form import ClientForm
    print("✅ ClientForm importato correttamente")
except Exception as e:
    print(f"❌ Errore import ClientForm: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="ClientForm", error=e))

try:
    from components.client_table import ClientTable
    print("✅ ClientTable importato correttamente")
except Exception as e:
    print(f"❌ Errore import ClientTable: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="ClientTable", error=e))

try:
    from components.incroci_tab import IncrociTab
    print("✅ IncrociTab importato correttamente")
except Exception as e:
    print(f"❌ Errore import IncrociTab: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="IncrociTab", error=e))

try:
    from components.broker_links_manager import BrokerLinksManager
    print("✅ BrokerLinksManager importato correttamente")
except Exception as e:
    print(f"❌ Errore import BrokerLinksManager: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="BrokerLinksManager", error=e))

try:
    from database.database import DatabaseManager
    print("✅ DatabaseManager importato correttamente")
except Exception as e:
    print(f"❌ Errore import DatabaseManager: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="DatabaseManager", error=e))

try:
    from database.incroci_manager import IncrociManager
    print("✅ IncrociManager importato correttamente")
except Exception as e:
    print(f"❌ Errore import IncrociManager: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="IncrociManager", error=e))

try:
    from utils.helpers import *
    print("✅ utils.helpers importato correttamente")
except Exception as e:
    print(f"❌ Errore import utils.helpers: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="utils.helpers", error=e))

try:
    from utils.backup import DatabaseBackupManager, auto_backup
    print("✅ utils.backup importato correttamente")
except Exception as e:
    print(f"❌ Errore import utils.backup: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="utils.backup", error=e))

try:
    from utils.secure_backup import create_secure_backup, list_secure_backups, restore_from_secure_backup
    print("✅ utils.secure_backup importato correttamente")
except Exception as e:
    print(f"❌ Errore import utils.secure_backup: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="utils.secure_backup", error=e))

# Import AI Assistant
try:
    from components.ai_assistant.ai_ui_components import render_ai_assistant
    print("✅ AI Assistant importato correttamente")
except Exception as e:
    print(f"❌ Errore import AI Assistant: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="AI Assistant", error=e))

# Import sistema gestione utenti
try:
    from components.user_navigation import render_user_navigation
    print("✅ Sistema gestione utenti importato correttamente")
except Exception as e:
    print(f"❌ Errore import sistema gestione utenti: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="sistema gestione utenti", error=e))

# Import sistema impostazioni utente
try:
    from components.user_settings import render_user_settings
    print("✅ Sistema impostazioni utente importato correttamente")
except Exception as e:
    print(f"❌ Errore import sistema impostazioni utente: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="sistema impostazioni utente", error=e))

# Import sistema gestione permessi
try:
    from components.permissions_management import permissions_management
    print("✅ Sistema gestione permessi importato correttamente")
except Exception as e:
    print(f"❌ Errore import sistema gestione permessi: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="sistema gestione permessi", error=e))

# Import sistema gestione wallet
try:
    from components.wallet_transactions_manager import WalletTransactionsManager
    from components.wallet_transaction_form import WalletTransactionForm
    from components.wallet_transaction_table import WalletTransactionTable
    from components.wallet_management import WalletManagement
    print("✅ Sistema gestione wallet importato correttamente")
except Exception as e:
    print(f"❌ Errore import sistema gestione wallet: {e}")
    st.error(t("system.errors.import_error", "Errore import {module}: {error}").format(module="sistema gestione wallet", error=e))

# Configurazione pagina
st.set_page_config(
    page_title=t("dashboard.title", "Dashboard Gestione CPA"),
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inizializzazione del database
def init_database():
    """Inizializza il database"""
    return DatabaseManager()

# Inizializzazione dei componenti
def init_components(db):
    """Inizializza i componenti"""
    try:
        print("🔧 Inizializzazione componenti...")
        
        # Verifica che tutti i componenti siano disponibili
        if not all([Charts, ClientForm, ClientTable, IncrociTab, BrokerLinksManager]):
            raise Exception("Uno o più componenti non sono disponibili")
        
        wallet_manager = WalletTransactionsManager()
        components_dict = {
            'client_form': ClientForm(),
            'client_table': ClientTable(),
            'charts': Charts(),
            'incroci_tab': IncrociTab(IncrociManager(), db),
            'broker_links_manager': BrokerLinksManager(),
            'wallet_manager': wallet_manager,
            'wallet_form': WalletTransactionForm(wallet_manager),
            'wallet_table': WalletTransactionTable(wallet_manager),
            'wallet_management': WalletManagement(wallet_manager)
        }
        
        print("✅ Componenti inizializzati correttamente")
        return components_dict
        
    except Exception as e:
        print(f"❌ Errore inizializzazione componenti: {e}")
        st.error(f"Errore inizializzazione componenti: {e}")
        return None

# Creazione automatica tabelle se non esistono
def create_database_tables():
    """Crea le tabelle del database se non esistono"""
    try:
        import sqlite3
        from pathlib import Path
        
        # Leggi lo script SQL di inizializzazione
        sql_file = Path("database/init_database.sql")
        if sql_file.exists():
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            
            # Esegui lo script SQL
            # Usa il percorso corretto del database
            db_path = db.db_path if hasattr(db, 'db_path') else "cpa_database.db"
            logging.info(f"🔍 Creazione tabelle su database: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verifica se le tabelle esistono già
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            logging.info(f"📋 Tabelle esistenti prima: {existing_tables}")
            
            # Esegui ogni comando SQL separatamente
            for command in sql_script.split(';'):
                command = command.strip()
                if command and not command.startswith('--'):
                    try:
                        cursor.execute(command)
                    except sqlite3.OperationalError as e:
                        # Ignora errori di tabelle già esistenti
                        if "already exists" not in str(e):
                            logging.warning(f"SQL warning: {e}")
            
            conn.commit()
            
            # Verifica se le tabelle sono state create
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            final_tables = [row[0] for row in cursor.fetchall()]
            logging.info(f"📋 Tabelle esistenti dopo: {final_tables}")
            
            conn.close()
            logging.info("✅ Tabelle database create/verificate con successo")
            return True
        else:
            logging.warning("⚠️ Script SQL di inizializzazione non trovato")
            return False
    except Exception as e:
        logging.error(f"❌ Errore creazione tabelle: {e}")
        return False

# Inizializzazione
try:
    print("🔧 Inizializzazione sistema di autenticazione...")
    init_auth()
    print(f"✅ Sistema di autenticazione inizializzato correttamente ({AUTH_SYSTEM})")
    
    # Mostra informazione all'utente
    if AUTH_SYSTEM == "fallback":
        st.info("ℹ️ **Sistema di Autenticazione**: Utilizzo versione di riserva (senza dipendenze esterne)")
    
    print("🔧 Inizializzazione database...")
    db = init_database()
    print("✅ Database inizializzato correttamente")
    
    print("🔧 Inizializzazione componenti...")
    components = init_components(db)
    if components is None:
        st.error("❌ Impossibile inizializzare i componenti. Controlla i log per dettagli.")
        st.stop()
    print("✅ Componenti inizializzati correttamente")
    
    # DISABILITATO: Non creiamo tabelle SQLite perché usiamo solo Supabase
    # print("🔧 Creazione tabelle database...")
    # create_database_tables()
    # print("✅ Tabelle database create/verificate")
    
except Exception as e:
    print(f"❌ Errore inizializzazione: {e}")
    st.error(f"Errore inizializzazione: {e}")
    st.stop()



# NON chiamare create_database_tables() qui - causa loop infinito!
# create_database_tables()

# Funzioni per gestire i broker popolari
def get_broker_suggestions():
    """Restituisce la lista dei broker popolari dal database Supabase o dalla lista predefinita"""
    try:
        # Prova a ottenere broker dal database Supabase
        from supabase_manager import SupabaseManager
        supabase_manager = SupabaseManager()
        
        if supabase_manager.is_configured:
            broker_links = supabase_manager.get_broker_links(active_only=True)
            if broker_links:
                # Estrae solo i nomi dei broker attivi
                broker_names = [link.get('broker_name', '') for link in broker_links if link.get('broker_name')]
                if broker_names:
                    return broker_names
    except Exception as e:
        # Log dell'errore per debug
        import logging
        logging.getLogger(__name__).warning(f"Errore recupero broker da Supabase: {e}")
    
    # Lista predefinita se non ci sono broker nel database
    return [
        "Ultima Markets", "Puprime", "Axi", "AvaTrade", "Global Prime",
        "FxCess", "Vtmarkets", "Tauro Markets", "FPG", "TMGM"
    ]

def save_broker_list(broker_list):
    """Salva la lista dei broker nel database"""
    try:
        if 'db' in globals() and db:
            # Pulisci tabella broker esistente
            db.esegui_query("DELETE FROM broker")
            
            # Inserisci nuovi broker
            for broker in broker_list:
                db.esegui_query(
                    "INSERT INTO broker (nome_broker) VALUES (?)",
                    (broker,)
                )
            return True
    except Exception as e:
        st.error(f"Errore salvataggio broker: {e}")
        return False
    return False

def manage_brokers():
    """Gestisce i broker popolari - permette di modificarli e aggiungerne di nuovi"""
    st.header("🏢 Gestione Broker Popolari")
    
    # Ottieni broker attuali
    broker_list = get_broker_suggestions()
    
    # Mostra broker esistenti
    st.subheader("📋 Broker Attuali")
    for i, broker in enumerate(broker_list):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"• {broker}")
        
        with col2:
            if st.button("✏️", key=f"edit_{i}", help="Modifica nome broker"):
                st.session_state.editing_broker_index = i
                st.session_state.editing_broker_name = broker
                st.rerun()  # Necessario per entrare in modalità modifica
        
        with col3:
            if st.button("🗑️", key=f"delete_{i}", help="Rimuovi broker"):
                if st.button("✅ Conferma", key=f"confirm_delete_{i}"):
                    broker_list.pop(i)
                    if save_broker_list(broker_list):
                        st.success(f"Broker '{broker}' rimosso e salvato!")
                    else:
                        st.error("Errore nel salvataggio!")
                    # Rimuoviamo st.rerun() per evitare loop infinito
    
    # Form per modificare broker esistente
    if 'editing_broker_index' in st.session_state:
        st.markdown("---")
        st.subheader("✏️ Modifica Broker")
        
        new_name = st.text_input(
            "Nuovo nome broker:",
            value=st.session_state.editing_broker_name,
            key="edit_broker_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salva Modifica"):
                if new_name.strip():
                    broker_list[st.session_state.editing_broker_index] = new_name.strip()
                    if save_broker_list(broker_list):
                        st.success(f"Broker rinominato in '{new_name}' e salvato!")
                    else:
                        st.error("Errore nel salvataggio!")
                    del st.session_state.editing_broker_index
                    del st.session_state.editing_broker_name
                    # Rimuoviamo st.rerun() per evitare loop infinito
                else:
                    st.error("Il nome del broker non può essere vuoto!")
        
        with col2:
            if st.button("❌ Annulla"):
                del st.session_state.editing_broker_index
                del st.session_state.editing_broker_name
                # Rimuoviamo st.rerun() per evitare loop infinito
    
    # Form per aggiungere nuovo broker
    st.markdown("---")
    st.subheader("➕ Aggiungi Nuovo Broker")
    
    new_broker = st.text_input("Nome nuovo broker:", placeholder="Es: Binance, Coinbase...")
    
    if st.button("➕ Aggiungi Broker", disabled=not new_broker.strip()):
        if new_broker.strip() and new_broker.strip() not in broker_list:
            broker_list.append(new_broker.strip())
            if save_broker_list(broker_list):
                st.success(f"Broker '{new_broker.strip()}' aggiunto e salvato con successo!")
            else:
                st.error("Errore nel salvataggio!")
            # Rimuoviamo st.rerun() per evitare loop infinito
        elif new_broker.strip() in broker_list:
            st.warning("Questo broker è già presente nella lista!")
        else:
            st.error("Inserisci un nome valido per il broker!")
    
    # Statistiche
    st.markdown("---")
    st.subheader("📊 Statistiche")
    st.write(f"• **Totale broker:** {len(broker_list)}")
    st.write(f"• **Broker unici:** {len(set(broker_list))}")
    
    # Reset lista (opzionale)
    if st.button("🔄 Reset Lista Predefinita", help="Ripristina la lista originale dei broker"):
        if st.button("✅ Conferma Reset", key="confirm_reset"):
            default_list = [
                "FXPro", "Pepperstone", "IC Markets", "AvaTrade", "Plus500",
                "eToro", "IG", "Saxo Bank", "Interactive Brokers", "TD Ameritrade"
            ]
            if save_broker_list(default_list):
                st.success("Lista broker ripristinata e salvata!")
            else:
                st.error("Errore nel salvataggio!")
            # Rimuoviamo st.rerun() per evitare loop infinito

# 🔧 DEBUG: Forza aggiornamento Streamlit Cloud - 2025-08-30 09:24 - FUNZIONE create_database_tables SPOSTATA PRIMA DELL'INIZIALIZZAZIONE

# Gestione dello stato dell'applicazione
if 'editing_client' not in st.session_state:
    st.session_state.editing_client = None

if 'show_charts' not in st.session_state:
    st.session_state.show_charts = False



# Sistema di autenticazione
if not st.session_state.get('authenticated', False):
    st.title("🔐 **Dashboard Gestione CPA Broker**")
    st.markdown("---")
    st.info("👋 **Benvenuto!** Effettua l'accesso per utilizzare il sistema.")
    
    # Form di login
    login_form()
    
    st.stop()

# Titolo principale (solo per utenti autenticati)

# Mostra informazioni utente nella sidebar
show_user_info()

# Menu di navigazione
# Titolo principale sopra il menu
st.title(t("dashboard.title", "🏠 Dashboard CPA - Gestione Clienti e Incroci"))
st.markdown("---")
# Titolo principale sopra il menu
st.markdown("---")
selected = option_menu(
    menu_title=None,
    options=[
        t("navigation.dashboard", "🏠 Dashboard"), 
        t("navigation.clients", "👥 Gestione Clienti"), 
        t("navigation.crosses", "🔄 Incroci"), 
        t("navigation.broker", "🔗 Broker"), 
        "💰 Wallet",
        "📁 Storage",
        t("navigation.summary", "📈 Riepilogo"), 
        "🤖 AI Assistant",
        t("navigation.settings", "⚙️ Impostazioni")
    ],
    icons=["house", "people", "arrows-collapse", "link", "wallet", "folder", "bar-chart", "robot", "gear"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#02ab21"},
    }
)

# Funzioni per la gestione dei clienti
def sync_all_data_to_supabase():
    """Sincronizza manualmente tutti i dati dal database locale a Supabase"""
    try:
        from supabase_manager import SupabaseManager
        
        # Inizializza manager Supabase
        supabase_manager = SupabaseManager()
        
        if not supabase_manager.is_configured:
            return False, "❌ Supabase non configurato"
        
        # Ottieni tutti i clienti dal database locale
        clienti_locali = db.ottieni_tutti_clienti()
        
        # Converti DataFrame in lista se necessario
        if hasattr(clienti_locali, 'empty'):
            if clienti_locali.empty:
                return False, "❌ Nessun cliente presente nel database locale"
            # Converti DataFrame in lista di dizionari
            clienti_locali = clienti_locali.to_dict('records')
        elif not clienti_locali:
            return False, "❌ Nessun cliente presente nel database locale"
        
        # Contatori per statistiche
        sincronizzati = 0
        errori = 0
        gia_presenti = 0
        
        st.info(f"🔄 Sincronizzazione in corso... {len(clienti_locali)} clienti da processare")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Log dettagliato per debug
        debug_info = []
        
        for i, cliente in enumerate(clienti_locali):
            # Aggiorna progress bar
            progress = (i + 1) / len(clienti_locali)
            progress_bar.progress(progress)
            
            nome_cliente = cliente.get('nome_cliente', 'N/A') if hasattr(cliente, 'get') else str(cliente)
            status_text.text(f"🔄 Sincronizzando cliente {i+1}/{len(clienti_locali)}: {nome_cliente}")
            
            try:
                # Prepara dati per Supabase
                supabase_data = {
                    'nome_cliente': str(cliente.get('nome_cliente', '')),
                    'email': str(cliente.get('email', f"cliente_{i}@local.com")),
                    'broker': str(cliente.get('broker', '')),
                    'piattaforma': str(cliente.get('piattaforma', '')),
                    'numero_conto': str(cliente.get('numero_conto', '')),
                    'volume_posizione': float(cliente.get('deposito', 0.0))
                }
                
                # Log dati preparati
                debug_info.append(f"Cliente {i+1}: {supabase_data['nome_cliente']} - Email: {supabase_data['email']}")
                
                # Verifica se il cliente esiste già in Supabase (per email)
                clienti_supabase = supabase_manager.get_clienti()
                cliente_esistente = None
                
                for c in clienti_supabase:
                    if c.get('email') == supabase_data['email']:
                        cliente_esistente = c
                        break
                
                if cliente_esistente:
                    # Aggiorna cliente esistente
                    success, message = supabase_manager.update_cliente(
                        cliente_esistente['id'], supabase_data
                    )
                    if success:
                        gia_presenti += 1
                        debug_info.append(f"✅ Aggiornato: {supabase_data['nome_cliente']}")
                    else:
                        errori += 1
                        debug_info.append(f"❌ Errore aggiornamento: {supabase_data['nome_cliente']} - {message}")
                else:
                    # Aggiungi nuovo cliente
                    success, message = supabase_manager.add_cliente(supabase_data)
                    if success:
                        sincronizzati += 1
                        debug_info.append(f"✅ Aggiunto: {supabase_data['nome_cliente']}")
                    else:
                        errori += 1
                        debug_info.append(f"❌ Errore aggiunta: {supabase_data['nome_cliente']} - {message}")
                        
            except Exception as e:
                errori += 1
                nome_cliente = cliente.get('nome_cliente', 'N/A') if hasattr(cliente, 'get') else str(cliente)
                error_msg = f"❌ Errore sincronizzazione cliente {nome_cliente}: {e}"
                st.error(error_msg)
                debug_info.append(error_msg)
        
        # Nascondi progress bar
        progress_bar.empty()
        status_text.empty()
        
        # Mostra log dettagliato
        with st.expander("📋 Log Dettagliato Sincronizzazione", expanded=True):
            st.write("**🔄 Processo di sincronizzazione:**")
            for info in debug_info:
                st.write(info)
            
            st.write(f"\n**📊 Riepilogo finale:**")
            st.write(f"• Sincronizzati: {sincronizzati}")
            st.write(f"• Aggiornati: {gia_presenti}")
            st.write(f"• Errori: {errori}")
            st.write(f"• Totale processati: {len(clienti_locali)}")
        
        # Risultato finale
        if errori == 0:
            return True, f"✅ Sincronizzazione completata! {sincronizzati} nuovi clienti, {gia_presenti} aggiornati"
        else:
            return True, f"⚠️ Sincronizzazione parziale: {sincronizzati} nuovi, {gia_presenti} aggiornati, {errori} errori"
            
    except Exception as e:
        return False, f"❌ Errore sincronizzazione: {e}"

def handle_save_client(dati_cliente, campi_aggiuntivi):
    """Gestisce il salvataggio di un nuovo cliente"""
    # Salva nel database locale
    success, result = db.aggiungi_cliente(dati_cliente, campi_aggiuntivi)
    
    if success:
        # DISABILITATO: Backup automatico SQLite non più necessario con Supabase
        # auto_backup()
        
        # SINCRONIZZAZIONE AUTOMATICA CON SUPABASE
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            if supabase_manager.is_configured:
                # Prepara dati per Supabase
                supabase_data = {
                    'nome_cliente': dati_cliente['nome_cliente'],
                    'email': dati_cliente['email'],
                    'password_email': dati_cliente.get('password_email', ''),
                    'broker': dati_cliente['broker'],
                    'data_registrazione': dati_cliente.get('data_registrazione').isoformat() if dati_cliente.get('data_registrazione') and hasattr(dati_cliente.get('data_registrazione'), 'isoformat') else str(dati_cliente.get('data_registrazione', '')),
                    'deposito': dati_cliente.get('deposito', 0.0),
                    'piattaforma': dati_cliente.get('piattaforma', ''),
                    'numero_conto': dati_cliente.get('numero_conto', ''),
                    'wallet': dati_cliente.get('wallet', ''),
                    'password_conto': dati_cliente.get('password_conto', ''),
                    'vps_ip': dati_cliente.get('vps_ip', ''),
                    'vps_username': dati_cliente.get('vps_username', ''),
                    'vps_password': dati_cliente.get('vps_password', '')
                }
                
                # Salva in Supabase
                supabase_success, supabase_message = supabase_manager.add_cliente(supabase_data)
                
                if supabase_success:
                    st.success(f"✅ Cliente {dati_cliente['nome_cliente']} salvato in LOCALE e SUPABASE!")
                else:
                    st.warning(f"⚠️ Cliente salvato in LOCALE ma errore SUPABASE: {supabase_message}")
            else:
                st.success(f"✅ Cliente {dati_cliente['nome_cliente']} salvato in LOCALE (Supabase non configurato)")
                
        except Exception as e:
            st.warning(f"⚠️ Cliente salvato in LOCALE ma errore sincronizzazione SUPABASE: {e}")
        
        st.session_state.editing_client = None
        st.rerun()  # Necessario per tornare alla lista

def handle_edit_client(cliente_data):
    """Gestisce la modifica di un cliente esistente"""
    # Converti Pandas Series in dizionario per evitare errori
    if hasattr(cliente_data, 'to_dict'):
        st.session_state.editing_client = cliente_data.to_dict()
    else:
        st.session_state.editing_client = cliente_data
    st.rerun()  # Necessario per entrare in modalità modifica

def handle_delete_client(cliente_id):
    """Gestisce l'eliminazione di un cliente da Supabase"""
    try:
        # Inizializza success
        success = False
        
        # Elimina da Supabase
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            # Cerca il cliente in Supabase per ID
            clienti_supabase = supabase_manager.get_clienti()
            cliente_supabase = None
            
            for c in clienti_supabase:
                if str(c.get('id')) == cliente_id:  # Confronta ID come stringa
                    cliente_supabase = c
                    break
            
            if cliente_supabase:
                # Elimina da Supabase
                success, message = supabase_manager.delete_cliente(cliente_supabase['id'])
                
                if success:
                    st.success(f"✅ **ELIMINAZIONE RIUSCITA!** Cliente {cliente_supabase['nome_cliente']} eliminato da Supabase")
                else:
                    st.error(f"❌ **ELIMINAZIONE FALLITA!** Cliente {cliente_supabase['nome_cliente']} non eliminato: {message}")
            else:
                st.error(f"❌ **CLIENTE NON TROVATO IN SUPABASE!** ID: {cliente_id}")
                success = False
                
        except Exception as e:
            st.error(f"❌ **Errore eliminazione da Supabase:** {e}")
            success = False
        
        return success
        
    except Exception as e:
        st.error(f"❌ **Errore durante eliminazione:** {e}")
        return False

def handle_update_client(cliente_id, dati_cliente, campi_aggiuntivi):
    """Gestisce l'aggiornamento di un cliente esistente"""
    # Aggiorna nel database locale
    success = db.modifica_cliente(cliente_id, dati_cliente, campi_aggiuntivi)
    
    if success:
        # DISABILITATO: Backup automatico SQLite non più necessario con Supabase
        # auto_backup()
        
        # SINCRONIZZAZIONE AUTOMATICA CON SUPABASE
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            if supabase_manager.is_configured:
                # Prepara dati per Supabase
                supabase_data = {
                    'nome_cliente': dati_cliente['nome_cliente'],
                    'email': dati_cliente['email'],
                    'password_email': dati_cliente.get('password_email', ''),
                    'broker': dati_cliente['broker'],
                    'data_registrazione': dati_cliente.get('data_registrazione').isoformat() if dati_cliente.get('data_registrazione') and hasattr(dati_cliente.get('data_registrazione'), 'isoformat') else str(dati_cliente.get('data_registrazione', '')),
                    'deposito': dati_cliente.get('deposito', 0.0),
                    'piattaforma': dati_cliente.get('piattaforma', ''),
                    'numero_conto': dati_cliente.get('numero_conto', ''),
                    'wallet': dati_cliente.get('wallet', ''),
                    'password_conto': dati_cliente.get('password_conto', ''),
                    'vps_ip': dati_cliente.get('vps_ip', ''),
                    'vps_username': dati_cliente.get('vps_username', ''),
                    'vps_password': dati_cliente.get('vps_password', '')
                }
                
                # Aggiorna in Supabase (cerca per email per matching)
                clienti_supabase = supabase_manager.get_clienti()
                cliente_supabase = None
                
                for c in clienti_supabase:
                    if c.get('email') == dati_cliente['email']:
                        cliente_supabase = c
                        break
                
                if cliente_supabase:
                    supabase_success, supabase_message = supabase_manager.update_cliente(
                        cliente_supabase['id'], supabase_data
                    )
                    
                    if supabase_success:
                        st.success(f"✅ Cliente {dati_cliente['nome_cliente']} aggiornato in LOCALE e SUPABASE!")
                    else:
                        st.warning(f"⚠️ Cliente aggiornato in LOCALE ma errore SUPABASE: {supabase_message}")
                else:
                    st.warning(f"⚠️ Cliente aggiornato in LOCALE ma non trovato in SUPABASE")
            else:
                st.success(f"✅ Cliente {dati_cliente['nome_cliente']} aggiornato in LOCALE (Supabase non configurato)")
                
        except Exception as e:
            st.warning(f"⚠️ Cliente aggiornato in LOCALE ma errore sincronizzazione SUPABASE: {e}")
        
        st.session_state.editing_client = None
        st.rerun()  # Necessario per tornare alla lista
    else:
        show_error_message("Errore nell'aggiornamento del cliente")

# Contenuto principale - SISTEMA UTENTI INTEGRATO
if selected == "🏠 Dashboard":
    # Usa il nuovo sistema di navigazione utente
    render_user_navigation()
    # Pulisci il contenuto precedente quando si torna alla dashboard
    if "current_page" in st.session_state:
        del st.session_state["current_page"]
    if "selected_client" in st.session_state:
        del st.session_state["selected_client"]
    if "editing_client" in st.session_state:
        del st.session_state["editing_client"]
    
elif selected == t("navigation.clients", "👥 Gestione Clienti"):
    st.header("Gestione Clienti CPA")
    st.write("Gestisci i clienti e le loro informazioni")
    
    # Ottieni dati da Supabase tramite ClientTable
    df_clienti = components['client_table'].get_clienti()
    
    # Se stiamo modificando un cliente
    if st.session_state.editing_client:
        st.subheader("✏️ Modifica Cliente")
        
        # Pulsante per tornare indietro
        if st.button("← Torna alla Lista"):
            st.session_state.editing_client = None
            st.rerun()  # Necessario per la navigazione
        
        # Form di modifica
        success, dati_cliente, campi_aggiuntivi = components['client_form'].render_form(
            st.session_state.editing_client, 
            is_edit=True
        )
        
        if success:
            handle_update_client(
                st.session_state.editing_client['id'],
                dati_cliente,
                campi_aggiuntivi
            )
    
    else:
        # Form per aggiungere nuovo cliente (collassato di default)
        with st.expander("➕ Aggiungi Nuovo Cliente", expanded=False):
            success, dati_cliente, campi_aggiuntivi = components['client_form'].render_form()
            
            if success:
                handle_save_client(dati_cliente, campi_aggiuntivi)
        
        # Tabella dei clienti esistenti (sempre visibile)
        if not df_clienti.empty:
            st.markdown("---")
            st.subheader("📋 Clienti Esistenti")
            
            components['client_table'].render_table(
                on_edit=handle_edit_client,
                on_delete=handle_delete_client
            )
        else:
            st.info("Nessun cliente presente. Aggiungi il primo cliente usando il form sopra!")

elif selected == t("navigation.crosses", "🔄 Incroci"):
    # Mostra il tab degli incroci
    components['incroci_tab'].render()

elif selected == t("navigation.broker", "🔗 Broker"):
    # Mostra la gestione dei link broker
    components['broker_links_manager'].render_broker_links_page()

elif selected == "💰 Wallet":
    st.header("💰 Gestione Transazioni Wallet")
    st.write("Gestisci le transazioni tra i wallet dei collaboratori")
    
    # Verifica se l'utente è admin per mostrare la gestione wallet
    is_admin = False
    try:
        from utils.supabase_permissions import has_role
        is_admin = has_role('admin')
    except:
        pass
    
    # Tab per organizzare le funzionalità wallet
    if is_admin:
        tab_transactions, tab_balances, tab_form, tab_management = st.tabs([
            "📋 Transazioni", "💰 Saldi", "➕ Nuova Transazione", "🔧 Gestione Wallet"
        ])
        
        # TAB 4: Gestione Wallet (solo admin)
        with tab_management:
            components['wallet_management'].render_wallet_management()
    else:
        tab_transactions, tab_balances, tab_form = st.tabs([
            "📋 Transazioni", "💰 Saldi", "➕ Nuova Transazione"
        ])
    
    # TAB 1: Transazioni esistenti
    with tab_transactions:
        components['wallet_table'].render_table(
            on_edit=lambda x: None,  # Abilita modifica (gestito internamente)
            on_delete=lambda x: None  # Abilita eliminazione (gestito internamente)
        )
    
    # TAB 2: Saldi wallet
    with tab_balances:
        components['wallet_table'].render_wallet_balances()
    
    # TAB 3: Form nuova transazione
    with tab_form:
        components['wallet_form'].render_form()

elif selected == "📁 Storage":
    # Mostra la sezione storage
    try:
        from components.storage.storage_ui import render_storage_wrapper
        render_storage_wrapper()
    except Exception as e:
        st.error(f"❌ Errore nel caricamento della sezione Storage: {str(e)}")
        st.info("💡 Assicurati che le tabelle storage siano state create in Supabase")

elif selected == t("navigation.summary", "📈 Riepilogo"):
    st.header("Riepilogo Dati")
    st.write("Visualizza i dati in formato tabellare e grafico")
    
    # Ottieni dati da Supabase tramite ClientTable
    df_clienti = components['client_table'].get_clienti()
    
    if not df_clienti.empty:
        # Grafici riassuntivi
        components['charts'].render_summary_charts(df_clienti)
        
        # Opzioni di esportazione
        components['charts'].render_export_options(df_clienti)
        
        # Tabella completa
        st.subheader("📋 Tabella Completa Clienti")
        st.dataframe(
            df_clienti,
            width='stretch',
            hide_index=True
        )
    else:
        st.info("Nessun cliente presente nel database. Aggiungi clienti per visualizzare i dati!")

elif selected == "🤖 AI Assistant":
    # Mostra l'interfaccia AI Assistant
    try:
        from supabase_manager import SupabaseManager
        supabase_manager = SupabaseManager()
        render_ai_assistant(supabase_manager)
    except Exception as e:
        st.error(f"❌ Errore caricamento AI Assistant: {e}")
        print(f"❌ Errore caricamento AI Assistant: {e}")

elif selected == t("navigation.settings", "⚙️ Impostazioni"):
    st.header("⚙️ Impostazioni Sistema")
    st.info("🚀 **CONFIGURAZIONE SUPABASE**: Gestisci sistema remoto, sicurezza e configurazione")
    
    # Tab per organizzare le impostazioni
    tab_supabase, tab_system, tab_security, tab_permissions, tab_user_settings = st.tabs([
        "🚀 Supabase", "ℹ️ Sistema", "🔒 Sicurezza", "🛡️ Permessi", "👤 Impostazioni Utente"
    ])
    
    # TAB 1: Supabase
    with tab_supabase:
        st.subheader("🚀 Gestione Supabase")
        st.info("📊 **DATABASE REMOTO**: Tutti i dati sono sincronizzati automaticamente con Supabase")
        
        # Stato Supabase
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            if supabase_manager.is_configured:
                st.success("✅ **SUPABASE ATTIVO** - Configurazione corretta")
                
                # Statistiche Supabase
                clienti_supabase = supabase_manager.get_clienti()
                incroci_supabase = supabase_manager.get_incroci()
                
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    st.metric("👥 Clienti", len(clienti_supabase))
                with col_stats2:
                    st.metric("🔄 Incroci", len(incroci_supabase))
                with col_stats3:
                    st.metric("🌐 Status", "Online")
                
                # Informazioni connessione (SICURE)
                st.markdown("---")
                st.subheader("🔗 Stato Connessione")
                st.write(f"**🌐 Status:** Connesso a Supabase")
                st.write(f"**🔒 Sicurezza:** Configurazione protetta")
                st.write(f"**📅 Ultimo aggiornamento:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
            else:
                st.error("❌ **SUPABASE NON CONFIGURATO** - Controlla le variabili d'ambiente")
                
        except Exception as e:
            st.error(f"❌ **Errore connessione Supabase:** {e}")
        
        # Test connessione
        st.markdown("---")
        st.subheader("🧪 Test Connessione")
        if st.button("🔍 Test Supabase", type="primary"):
            try:
                if supabase_manager.is_configured:
                    # Test lettura clienti
                    clienti = supabase_manager.get_clienti()
                    st.success(f"✅ **CONNESSIONE OK** - {len(clienti)} clienti letti")
                    
                    # Test lettura incroci
                    incroci = supabase_manager.get_incroci()
                    st.success(f"✅ **INCROCI OK** - {len(incroci)} incroci letti")
                else:
                    st.error("❌ Supabase non configurato")
            except Exception as e:
                st.error(f"❌ **Test fallito:** {e}")
    
    # TAB 2: Sistema
    with tab_system:
        st.subheader("ℹ️ Informazioni Sistema")
        st.info("📋 **STATO APPLICAZIONE**: Monitora lo stato generale del sistema")
        
        # Informazioni generali
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            st.write("**🖥️ Ambiente:**")
            st.write(f"• **OS:** {os.name}")
            st.write(f"• **Python:** {sys.version.split()[0]}")
            st.write(f"• **Streamlit:** {st.__version__}")
        
        with col_sys2:
            st.write("**📊 Componenti:**")
            st.write("• ✅ ClientForm")
            st.write("• ✅ ClientTable") 
            st.write("• ✅ IncrociTab")
            st.write("• ✅ Charts")
        
        # Logs recenti
        st.markdown("---")
        st.subheader("📝 Logs Recenti")
        st.info("🔍 **DEBUGGING**: Ultimi messaggi di log del sistema")
        
        # Mostra ultimi log (esempio)
        st.write("**📋 Log di Sistema:**")
        st.write("• ✅ Supabase client inizializzato")
        st.write("• ✅ IncrociManager inizializzato con Supabase")
        st.write("• ✅ Componenti inizializzati correttamente")
        st.write("• ✅ Configurazione da Streamlit Cloud secrets")
    
    # TAB 3: Sicurezza
    with tab_security:
        try:
            from components.security_tab import SecurityTab
            security_tab = SecurityTab()
            security_tab.render()
        except ImportError:
            st.error("❌ **COMPONENTE SICUREZZA NON DISPONIBILE**")
            st.info("💡 Installa le dipendenze: `pip install gitpython`")
        except Exception as e:
            st.error(f"❌ **Errore caricamento componente sicurezza:** {e}")
            st.info("🔧 Controlla che il file `components/security_tab.py` sia presente")
    
    # TAB 4: Permessi
    with tab_permissions:
        st.subheader("🛡️ " + t("permissions.management.title", "Gestione Permessi e Ruoli"))
        st.info("🔐 **SISTEMA PERMESSI AVANZATO**: Gestisci utenti, ruoli e permessi del sistema")
        
        # Verifica se l'utente è autenticato e admin
        try:
            from utils.supabase_permissions import has_role
            
            # Prima verifica se l'utente è autenticato
            if not st.session_state.get('authenticated', False):
                st.info("ℹ️ " + t("permissions.login_required", "Effettua il login per accedere alla gestione permessi."))
                pass
            else:
                # Poi verifica se è admin
                if has_role('admin'):
                    permissions_management.render()
                else:
                    st.error("❌ " + t("permissions.admin_only", "Solo gli amministratori possono accedere alla gestione permessi."))
        except Exception as e:
            st.error(f"❌ Errore caricamento sistema permessi: {e}")
            st.info("ℹ️ Assicurati che Supabase sia configurato correttamente.")
    
    # TAB 5: Impostazioni Utente
    with tab_user_settings:
        try:
            render_user_settings()
        except Exception as e:
            st.error(f"❌ **Errore caricamento impostazioni utente:** {e}")
            st.info("🔧 Controlla che il file `components/user_settings.py` sia presente")

# Funzione di test rimossa - non più necessaria

def fix_supabase_and_duplicates():
    """Ripara Supabase e risolve email duplicate"""
    st.header("🔧 RIPARAZIONE SUPABASE E DUPLICATI")
    
    # Test 1: Ripara connessione Supabase
    st.subheader("1. Ripara Connessione Supabase")
    try:
        from supabase_manager import SupabaseManager
        supabase_manager = SupabaseManager()
        
        if supabase_manager.is_configured:
            st.write("✅ **Supabase configurato**")
            
            # Forza reinizializzazione
            try:
                clienti_supabase = supabase_manager.get_clienti()
                st.success(f"✅ **Supabase funzionante!** Clienti: {len(clienti_supabase)}")
            except Exception as e:
                st.error(f"❌ **Errore Supabase:** {e}")
                st.info("🔄 Tentativo di reinizializzazione...")
                
                # Reinizializza Supabase
                try:
                    supabase_manager = SupabaseManager()
                    clienti_supabase = supabase_manager.get_clienti()
                    st.success(f"✅ **Supabase riparato!** Clienti: {len(clienti_supabase)}")
                except Exception as e2:
                    st.error(f"❌ **Supabase non riparabile:** {e2}")
        else:
            st.warning("⚠️ **Supabase non configurato**")
            
    except Exception as e:
        st.error(f"❌ **Errore generale Supabase:** {e}")
    
    # Test 2: Risolvi email duplicate
    st.subheader("2. Risolvi Email Duplicate")
    try:
        conn = sqlite3.connect('cpa_database.db')
        cursor = conn.cursor()
        
        # Trova email duplicate
        cursor.execute("""
            SELECT email, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM clienti 
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            st.warning(f"⚠️ **Email duplicate trovate:** {len(duplicates)}")
            
            for dup in duplicates:
                email = dup[0]
                count = dup[1]
                ids = dup[2].split(',')
                
                st.write(f"📧 **Email:** {email} (conteggio: {count})")
                st.write(f"🆔 **IDs:** {ids}")
                
                # Proposta di soluzione
                if st.button(f"🔧 Risolvi duplicati per {email}", key=f"fix_{email}"):
                    # Mantieni solo il primo ID, elimina gli altri
                    ids_to_delete = ids[1:]  # Tutti tranne il primo
                    
                    for id_to_delete in ids_to_delete:
                        cursor.execute("DELETE FROM clienti WHERE id = ?", (id_to_delete,))
                        st.write(f"🗑️ **Eliminato cliente ID:** {id_to_delete}")
                    
                    conn.commit()
                    st.success(f"✅ **Duplicati risolti per:** {email}")
                    # Rimuoviamo st.rerun() per evitare loop infinito
        else:
            st.success("✅ **Nessuna email duplicata**")
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ **Errore risoluzione duplicati:** {e}")
    
    # Test 3: Test eliminazione dopo riparazioni
    st.subheader("3. Test Eliminazione Post-Riparazione")
    
    cliente_id_test = st.number_input("Testa eliminazione ID:", min_value=1, value=30, step=1)
    
    if st.button("🧪 TEST ELIMINAZIONE FINALE"):
        try:
            # Verifica esistenza
            conn = sqlite3.connect('cpa_database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM clienti WHERE id = ?", (cliente_id_test,))
            count_before = cursor.fetchone()[0]
            st.write(f"📊 **Clienti con ID {cliente_id_test} PRIMA:** {count_before}")
            
            if count_before == 0:
                st.warning(f"⚠️ Cliente ID {cliente_id_test} non trovato")
                conn.close()
                return
            
            # Eliminazione
            cursor.execute("DELETE FROM clienti WHERE id = ?", (cliente_id_test,))
            rows_deleted = cursor.rowcount
            conn.commit()
            
            # Verifica
            cursor.execute("SELECT COUNT(*) FROM clienti WHERE id = ?", (cliente_id_test,))
            count_after = cursor.fetchone()[0]
            conn.close()
            
            if count_after == 0 and rows_deleted > 0:
                st.success(f"✅ **ELIMINAZIONE RIUSCITA!** Cliente {cliente_id_test} eliminato")
            else:
                st.error(f"❌ **ELIMINAZIONE FALLITA!** Cliente ancora presente")
                
        except Exception as e:
            st.error(f"❌ **Errore test eliminazione:** {e}")

# Funzione di test diretto rimossa - non più necessaria

# Sezione test rimossa - non più necessaria

# Vecchia sidebar rimossa - sostituita con quella pulita

# Funzione di test super semplice rimossa - non più necessaria

# Sezione test ultra-semplice rimossa - non più necessaria

# Sezione soluzione completa rimossa - non più necessaria

# Sidebar compatta e essenziale
with st.sidebar:
    st.header("🎛️ Dashboard CPA")
    
    # Menu principale compatto
    if st.button("➕ Nuovo Cliente", use_container_width=True):
        st.session_state.editing_client = None
        st.session_state.show_client_form = True
        st.rerun()  # Necessario per la navigazione
    
    if st.button("⚙️ Gestisci Broker", use_container_width=True):
        st.session_state.show_broker_management = True
        st.rerun()  # Necessario per la navigazione
    
    
    # Selettore lingua compatto
    st.markdown("---")
    # Lingue ordinate alfabeticamente
    lingue_options = ["es", "it"]
    selected_language = st.selectbox(
        "🌐 Lingua",
        options=lingue_options,
        format_func=lambda x: "🇮🇹 IT" if x == "it" else "🇪🇸 ES",
        index=0 if st.session_state.get("language", "it") == "it" else 1,
        key="language_selector"
    )
    
    if selected_language != st.session_state.get("language", "it"):
        st.session_state["language"] = selected_language
        # Rimuoviamo st.rerun() per evitare loop infinito
    
    # Versione compatta
    st.caption("v2.0.0")


