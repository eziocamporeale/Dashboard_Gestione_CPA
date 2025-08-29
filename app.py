import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu
import logging

# Configurazione logging per Streamlit Cloud
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Import diretti dei componenti con gestione errori
try:
    from auth_standalone import require_auth, show_user_info, login_form
    print("✅ auth_standalone importato correttamente")
except Exception as e:
    print(f"❌ Errore import auth_standalone: {e}")
    st.error(f"Errore import auth_standalone: {e}")

try:
    from components.charts import Charts
    print("✅ Charts importato correttamente")
except Exception as e:
    print(f"❌ Errore import Charts: {e}")
    st.error(f"Errore import Charts: {e}")

try:
    from components.client_form import ClientForm
    print("✅ ClientForm importato correttamente")
except Exception as e:
    print(f"❌ Errore import ClientForm: {e}")
    st.error(f"Errore import ClientForm: {e}")

try:
    from components.client_table import ClientTable
    print("✅ ClientTable importato correttamente")
except Exception as e:
    print(f"❌ Errore import ClientTable: {e}")
    st.error(f"Errore import ClientTable: {e}")

try:
    from components.incroci_tab import IncrociTab
    print("✅ IncrociTab importato correttamente")
except Exception as e:
    print(f"❌ Errore import IncrociTab: {e}")
    st.error(f"Errore import IncrociTab: {e}")

try:
    from database.database import DatabaseManager
    print("✅ DatabaseManager importato correttamente")
except Exception as e:
    print(f"❌ Errore import DatabaseManager: {e}")
    st.error(f"Errore import DatabaseManager: {e}")

try:
    from database.incroci_manager import IncrociManager
    print("✅ IncrociManager importato correttamente")
except Exception as e:
    print(f"❌ Errore import IncrociManager: {e}")
    st.error(f"Errore import IncrociManager: {e}")

try:
    from utils.helpers import *
    print("✅ utils.helpers importato correttamente")
except Exception as e:
    print(f"❌ Errore import utils.helpers: {e}")
    st.error(f"Errore import utils.helpers: {e}")

try:
    from utils.backup import DatabaseBackupManager, auto_backup
    print("✅ utils.backup importato correttamente")
except Exception as e:
    print(f"❌ Errore import utils.backup: {e}")
    st.error(f"Errore import utils.backup: {e}")

try:
    from utils.secure_backup import create_secure_backup, list_secure_backups, restore_from_secure_backup
    print("✅ utils.secure_backup importato correttamente")
except Exception as e:
    print(f"❌ Errore import utils.secure_backup: {e}")
    st.error(f"Errore import utils.secure_backup: {e}")
import tempfile
import shutil
import os
import sys

# Configurazione pagina
st.set_page_config(
    page_title="Dashboard Gestione CPA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione del database
@st.cache_resource
def init_database():
    """Inizializza il database"""
    return DatabaseManager()

# Inizializzazione dei componenti
@st.cache_resource
def init_components():
    """Inizializza i componenti"""
    try:
        print("🔧 Inizializzazione componenti...")
        
        # Verifica che tutti i componenti siano disponibili
        if not all([Charts, ClientForm, ClientTable, IncrociTab]):
            raise Exception("Uno o più componenti non sono disponibili")
        
        components_dict = {
            'client_form': ClientForm(),
            'client_table': ClientTable(),
            'charts': Charts(),
            'incroci_tab': IncrociTab(IncrociManager(db.db_path), db)
        }
        
        print("✅ Componenti inizializzati correttamente")
        return components_dict
        
    except Exception as e:
        print(f"❌ Errore inizializzazione componenti: {e}")
        st.error(f"Errore inizializzazione componenti: {e}")
        return None

# Inizializzazione
try:
    print("🔧 Inizializzazione database...")
    db = init_database()
    print("✅ Database inizializzato correttamente")
    
    print("🔧 Inizializzazione componenti...")
    components = init_components()
    if components is None:
        st.error("❌ Impossibile inizializzare i componenti. Controlla i log per dettagli.")
        st.stop()
    print("✅ Componenti inizializzati correttamente")
    
except Exception as e:
    print(f"❌ Errore inizializzazione: {e}")
    st.error(f"Errore inizializzazione: {e}")
    st.stop()

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

# Crea le tabelle all'avvio
create_database_tables()

# 🔧 DEBUG: Forza aggiornamento Streamlit Cloud - 2025-08-29 21:45

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
    login_form()
    st.stop()

# Titolo principale (solo per utenti autenticati)
st.title("📊 Dashboard Gestione CPA Broker")
st.markdown("---")

# Mostra informazioni utente nella sidebar
show_user_info()

# Menu di navigazione
selected = option_menu(
    menu_title=None,
    options=["🏠 Dashboard", "👥 Gestione Clienti", "🔄 Incroci", "📈 Riepilogo", "⚙️ Impostazioni"],
    icons=["house", "people", "arrows-collapse", "bar-chart", "gear"],
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
                    'volume_posizione': float(cliente.get('volume_posizione', 0.0))
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
        # Backup automatico dopo aggiunta cliente
        auto_backup()
        
        # SINCRONIZZAZIONE AUTOMATICA CON SUPABASE
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            if supabase_manager.is_configured:
                # Prepara dati per Supabase
                supabase_data = {
                    'nome_cliente': dati_cliente['nome_cliente'],
                    'email': dati_cliente['email'],
                    'broker': dati_cliente['broker'],
                    'piattaforma': dati_cliente.get('piattaforma', ''),
                    'numero_conto': dati_cliente.get('numero_conto', ''),
                    'volume_posizione': dati_cliente.get('volume_posizione', 0.0)
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
        st.rerun()
    else:
        show_error_message(f"Errore nel salvataggio: {result}")

def handle_edit_client(cliente_data):
    """Gestisce la modifica di un cliente esistente"""
    # Converti Pandas Series in dizionario per evitare errori
    if hasattr(cliente_data, 'to_dict'):
        st.session_state.editing_client = cliente_data.to_dict()
    else:
        st.session_state.editing_client = cliente_data
    st.rerun()

def handle_delete_client(cliente_id):
    """Gestisce l'eliminazione di un cliente - VERSIONE COMPLETA CON CHIAVI SEMPLICI"""
    st.write(f"🔍 **FUNZIONE CHIAMATA:** handle_delete_client con ID {cliente_id}")
    
    # Verifica permessi
    if not st.session_state.get('authenticated', False):
        st.error("🔒 Accesso richiesto per eliminare clienti")
        return
    
    # Gestisci lo stato di conferma per questo cliente
    delete_key = f"delete_confirm_{cliente_id}"
    if delete_key not in st.session_state:
        st.session_state[delete_key] = False
    
    # Se non è ancora stata richiesta la conferma, mostra il pulsante elimina
    if not st.session_state[delete_key]:
        st.write(f"🔍 **Stato conferma:** {st.session_state[delete_key]}")
        
        # Pulsante elimina con chiave SEMPLICE
        if st.button(f"🗑️ Elimina Cliente {cliente_id}", key=f"elimina_semplice_{cliente_id}"):
            st.write("✅ PULSANTE ELIMINA CLICCATO!")
            st.session_state[delete_key] = True
            st.rerun()
    
    # Se è richiesta la conferma, mostra i pulsanti di conferma
    else:
        st.write(f"🔍 **Conferma eliminazione per cliente {cliente_id}**")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"✅ Conferma Eliminazione", key=f"conferma_{cliente_id}"):
                # Elimina il cliente dal database
                try:
                    cliente_id_int = int(cliente_id)
                    success = db.elimina_cliente(cliente_id_int)
                    
                    if success:
                        st.success(f"✅ Cliente {cliente_id_int} eliminato con successo!")
                        # Reset dello stato
                        st.session_state[delete_key] = False
                        st.rerun()
                    else:
                        st.error(f"❌ Errore nell'eliminazione del cliente {cliente_id_int}")
                        st.session_state[delete_key] = False
                except Exception as e:
                    st.error(f"❌ Errore: {e}")
                    st.session_state[delete_key] = False
        
        with col2:
            if st.button(f"❌ Annulla", key=f"annulla_{cliente_id}"):
                st.session_state[delete_key] = False
                st.rerun()
        
        st.warning(f"⚠️ Sei sicuro di voler eliminare il cliente {cliente_id}?")

def handle_update_client(cliente_id, dati_cliente, campi_aggiuntivi):
    """Gestisce l'aggiornamento di un cliente esistente"""
    # Aggiorna nel database locale
    success = db.modifica_cliente(cliente_id, dati_cliente, campi_aggiuntivi)
    
    if success:
        # Backup automatico dopo modifica cliente
        auto_backup()
        
        # SINCRONIZZAZIONE AUTOMATICA CON SUPABASE
        try:
            from supabase_manager import SupabaseManager
            supabase_manager = SupabaseManager()
            
            if supabase_manager.is_configured:
                # Prepara dati per Supabase
                supabase_data = {
                    'nome_cliente': dati_cliente['nome_cliente'],
                    'email': dati_cliente['email'],
                    'broker': dati_cliente['broker'],
                    'piattaforma': dati_cliente.get('piattaforma', ''),
                    'numero_conto': dati_cliente.get('numero_conto', ''),
                    'volume_posizione': dati_cliente.get('volume_posizione', 0.0)
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
        st.rerun()
    else:
        show_error_message("Errore nell'aggiornamento del cliente")

# Contenuto principale
if selected == "🏠 Dashboard":
    st.header("Dashboard Principale")
    st.write("Benvenuto nella dashboard per la gestione delle CPA dei broker")
    
    # Ottieni dati dal database
    df_clienti = db.ottieni_tutti_clienti()
    stats = db.ottieni_statistiche()
    
    # Statistiche rapide
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Totale Clienti", value=stats['totale_clienti'])
    
    with col2:
        st.metric(label="Broker Attivi", value=stats['broker_attivi'])
    
    with col3:
        st.metric(label="Depositi Totali", value=format_currency(stats['depositi_totali']))
    
    with col4:
        st.metric(label="CPA Attive", value=stats['cpa_attive'])
    
    # Grafici della dashboard
    if not df_clienti.empty:
        components['charts'].render_dashboard_charts(df_clienti)
    else:
        st.info("Aggiungi il primo cliente per visualizzare i grafici!")

elif selected == "👥 Gestione Clienti":
    st.header("Gestione Clienti CPA")
    st.write("Gestisci i clienti e le loro informazioni")
    
    # Ottieni dati dal database
    df_clienti = db.ottieni_tutti_clienti()
    
    # Se stiamo modificando un cliente
    if st.session_state.editing_client:
        st.subheader("✏️ Modifica Cliente")
        
        # Pulsante per tornare indietro
        if st.button("← Torna alla Lista"):
            st.session_state.editing_client = None
            st.rerun()
        
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
                df_clienti,
                on_edit=handle_edit_client,
                on_delete=handle_delete_client
            )
        else:
            st.info("Nessun cliente presente. Aggiungi il primo cliente usando il form sopra!")

elif selected == "🔄 Incroci":
    # Mostra il tab degli incroci
    components['incroci_tab'].render()

elif selected == "📈 Riepilogo":
    st.header("Riepilogo Dati")
    st.write("Visualizza i dati in formato tabellare e grafico")
    
    # Ottieni dati dal database
    df_clienti = db.ottieni_tutti_clienti()
    
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

elif selected == "⚙️ Impostazioni":
    st.header("⚙️ Impostazioni Sistema")
    st.info("🔧 **CONFIGURAZIONE COMPLETA**: Gestisci database, backup, sicurezza e sistema remoto")
    
    # Tab per organizzare le impostazioni
    tab_config, tab_backup, tab_supabase, tab_system = st.tabs([
        "🗄️ Database", "💾 Backup & Sicurezza", "🚀 Supabase", "ℹ️ Sistema"
    ])
    
    # TAB 1: Database
    with tab_config:
        st.subheader("🗄️ Gestione Database")
        st.write("Configura e gestisci il database locale dell'applicazione")
    
    col_db1, col_db2 = st.columns(2)
    
    with col_db1:
        if st.button("🔄 Ricrea Database", help="Ricrea le tabelle del database"):
            db.init_database()
            show_success_message("Database ricreato con successo!")
    
    with col_db2:
        if st.button("📊 Inserisci Dati di Esempio", help="Inserisce dati di esempio per testare l'applicazione"):
            sample_data = create_sample_data()
            
            for _, row in sample_data.iterrows():
                dati_cliente = {
                    'nome_cliente': row['nome_cliente'],
                    'email': row['email'],
                    'password_email': '',
                    'broker': row['broker'],
                    'data_registrazione': datetime.strptime(row['data_registrazione'], '%Y-%m-%d').date(),
                    'deposito': row['deposito'],
                    'piattaforma': row['piattaforma'],
                    'numero_conto': row['numero_conto'],
                    'password_conto': '',
                    'vps_ip': row['vps_ip'],
                    'vps_username': '',
                    'vps_password': ''
                }
                
                db.aggiungi_cliente(dati_cliente)
            
            show_success_message("Dati di esempio inseriti con successo!")
            st.rerun()
    
        # Stato database corrente
        st.markdown("---")
        st.subheader("📊 Stato Database Corrente")
        
        backup_manager = DatabaseBackupManager()
        db_info = backup_manager.get_database_info()
        
        if db_info:
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("💾 Dimensione", f"{db_info['size'] / 1024:.1f} KB")
            with col_info2:
                st.metric("📊 Clienti", db_info.get('clienti_count', 0))
            with col_info3:
                st.metric("🔄 Incroci", db_info.get('incroci_count', 0))
            
            st.write(f"**📍 Percorso:** `{db_info['path']}`")
            st.write(f"**🕒 Ultimo aggiornamento:** {db_info.get('ultimo_aggiornamento', 'N/A')}")
        else:
            st.error("❌ Impossibile ottenere informazioni sul database")
    
    # TAB 2: Backup & Sicurezza
    with tab_backup:
        st.subheader("💾 Gestione Backup & Sicurezza")
        st.info("⚠️ **IMPORTANTE**: I backup vengono creati automaticamente dopo ogni operazione critica per prevenire la perdita di dati.")
        
        # Backup Manuali
        st.subheader("📋 Backup Manuali")
        col_backup1, col_backup2, col_backup3 = st.columns(3)
        
        with col_backup1:
            if st.button("🔄 Crea Backup Manuale"):
                success, message = auto_backup()
                if success:
                    st.success(f"✅ Backup creato: {message}")
                else:
                    st.error(f"❌ Backup fallito: {message}")
        
        with col_backup2:
            if st.button("📋 Lista Backup"):
                backup_manager = DatabaseBackupManager()
                backups = backup_manager.list_backups()
                
                if backups:
                    st.write(f"**Backup disponibili:** {len(backups)}")
                    for i, backup in enumerate(backups[:5]):
                        st.write(f"{i+1}. {backup['filename']} - {backup['modified'].strftime('%d/%m/%Y %H:%M')}")
                        if backup['metadata'] and 'statistics' in backup['metadata']:
                            stats = backup['metadata']['statistics']
                            st.write(f"   📊 {stats.get('clienti_count', 0)} clienti, {stats.get('incroci_count', 0)} incroci")
                else:
                    st.warning("Nessun backup disponibile")
        
        with col_backup3:
            if st.button("💾 Download Backup Completo"):
                try:
                    backup_manager = DatabaseBackupManager()
                    success, backup_path = backup_manager.create_backup("download_istantaneo")
                    if success:
                        with open(backup_path, "rb") as file:
                            st.download_button(
                                label="📥 Scarica Database Completo",
                                data=file.read(),
                                file_name=f"cpa_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                                mime="application/octet-stream"
                            )
                        st.success("✅ Backup pronto per il download!")
                    else:
                        st.error(f"❌ Errore creazione backup: {backup_path}")
                except Exception as e:
                    st.error(f"❌ Errore durante download: {e}")
        
        # Sincronizzazione Manuale con Supabase
        st.markdown("---")
        st.subheader("🔄 Sincronizzazione Manuale Supabase")
        st.info("🔄 **SINCRONIZZAZIONE**: Carica manualmente tutti i dati dal database locale a Supabase")
        
        col_sync1, col_sync2 = st.columns(2)
        
        with col_sync1:
            if st.button("🔄 Sincronizza Tutti i Dati", type="primary"):
                success, message = sync_all_data_to_supabase()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with col_sync2:
            # Mostra stato sincronizzazione
            try:
                from supabase_manager import SupabaseManager
                supabase_manager = SupabaseManager()
                
                if supabase_manager.is_configured:
                    clienti_supabase = supabase_manager.get_clienti()
                    clienti_locali = db.ottieni_tutti_clienti()
                    
                    st.write("**📊 Stato Sincronizzazione:**")
                    st.write(f"• **Locale:** {len(clienti_locali)} clienti")
                    st.write(f"• **Supabase:** {len(clienti_supabase)} clienti")
                    
                    if len(clienti_locali) == len(clienti_supabase):
                        st.success("✅ **SINCRONIZZATO**")
                    else:
                        st.warning(f"⚠️ **NON SINCRONIZZATO** (differenza: {abs(len(clienti_locali) - len(clienti_supabase))})")
                else:
                    st.warning("⚠️ Supabase non configurato")
            except Exception as e:
                st.error(f"❌ Errore verifica stato: {e}")
        
        # Backup Sicuri Locali
        st.markdown("---")
        st.subheader("🔒 Backup Sicuri Locali")
        st.warning("⚠️ **SICUREZZA MASSIMA**: Questi backup sono salvati SOLO in locale e NON sono visibili su GitHub!")
        st.info("💾 **LOCAZIONE**: ~/CPA_Backups_Sicuri/ (cartella esterna al progetto)")
        
        col_secure1, col_secure2, col_secure3 = st.columns(3)
        
        with col_secure1:
            if st.button("🔒 Crea Backup Sicuro"):
                success, backup_path, metadata = create_secure_backup("manual")
                if success:
                    st.success(f"✅ Backup sicuro creato: {backup_path}")
                    if metadata:
                        st.write(f"📊 {metadata['statistics']['clienti_count']} clienti, {metadata['statistics']['incroci_count']} incroci")
                else:
                    st.error(f"❌ Errore backup sicuro: {backup_path}")
        
        with col_secure2:
            if st.button("📋 Lista Backup Sicuri"):
                secure_backups = list_secure_backups()
                if secure_backups:
                    st.write(f"🔒 **Backup sicuri disponibili:** {len(secure_backups)}")
                    for i, backup in enumerate(secure_backups[:5]):
                        st.write(f"{i+1}. {backup['filename']} - {backup['modified'].strftime('%d/%m/%Y %H:%M')}")
                        st.write(f"   📁 {backup['category']} - {backup['size_mb']} MB")
                        if 'metadata' in backup and 'statistics' in backup['metadata']:
                            stats = backup['metadata']['statistics']
                            st.write(f"📊 {stats.get('clienti_count', 0)} clienti, {stats.get('incroci_count', 0)} incroci")
                else:
                    st.warning("Nessun backup sicuro disponibile")
        
        with col_secure3:
            if st.button("🔄 Ripristina da Backup Sicuro"):
                secure_backups = list_secure_backups()
                if secure_backups:
                    backup_options = [f"{b['filename']} ({b['category']})" for b in secure_backups[:5]]
                    selected_backup = st.selectbox("Seleziona backup da ripristinare:", backup_options)
                    
                    if st.button("✅ Conferma Ripristino"):
                        selected_index = backup_options.index(selected_backup)
                        backup_path = secure_backups[selected_index]['path']
                        success, message = restore_from_secure_backup(backup_path)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ Ripristino fallito: {message}")
                else:
                    st.warning("Nessun backup sicuro disponibile per il ripristino")
        
        # Import Manuale Database
        st.markdown("---")
        st.subheader("📥 Import Manuale Database")
        st.info("🤝 **COLLABORAZIONE TEAM**: I collaboratori possono importare database esportati dal tuo PC per sincronizzare i dati.")
        st.warning("⚠️ **ATTENZIONE**: Importa solo file database che ti fidi completamente!")
        
        col_import1, col_import2 = st.columns(2)
        
        with col_import1:
            uploaded_file = st.file_uploader(
                "📁 Carica File Database (.db)",
                type=['db'],
                help="Seleziona un file database (.db) esportato dal PC principale"
            )
            
            if uploaded_file is not None:
                file_size = len(uploaded_file.getvalue())
                file_size_mb = round(file_size / (1024 * 1024), 2)
                st.write(f"📊 **File caricato:** {uploaded_file.name}")
                st.write(f"💾 **Dimensione:** {file_size_mb} MB")
                
                if st.button("✅ Conferma Import Database", type="primary"):
                    try:
                        current_db_path = db.db_path if hasattr(db, 'db_path') else "cpa_database.db"
                        backup_name = f"backup_prima_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        
                        if os.path.exists(current_db_path):
                            shutil.copy2(current_db_path, f"{backup_name}")
                            st.success(f"✅ Backup database corrente: {backup_name}")
                        
                        with open(current_db_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        st.success("✅ Database importato con successo!")
                        st.info("🔄 L'app si riavvierà automaticamente per applicare le modifiche...")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Errore durante l'import: {e}")
                        st.error("Il database originale è rimasto intatto.")
        
        with col_import2:
            st.write("**📋 Istruzioni per i Collaboratori:**")
            st.write("1. **Richiedi** il file database al responsabile")
            st.write("2. **Carica** il file .db usando il pulsante a sinistra")
            st.write("3. **Conferma** l'import per applicare i dati")
            st.write("4. **L'app si riavvia** automaticamente")
            st.write("")
            st.write("**🔒 Sicurezza:**")
            st.write("• Solo file .db sono accettati")
            st.write("• Backup automatico prima dell'import")
            st.write("• Database originale protetto")
    
    # TAB 3: Supabase
    with tab_supabase:
        st.subheader("🚀 SUPABASE - Database Remoto Professionale")
        st.info("🔒 **DATABASE PROFESSIONALE**: Sistema remoto enterprise-grade con backup automatici e sicurezza massima!")
        
        col_supabase1, col_supabase2 = st.columns(2)
        
        with col_supabase1:
            if st.button("🔗 Test Connessione Supabase"):
                try:
                    from supabase_manager import show_supabase_status
                    show_supabase_status()
                except ImportError:
                    st.warning("⚠️ **SUPABASE NON INSTALLATO**")
                    st.info("📦 Installa le dipendenze:")
                    st.code("pip install -r requirements_supabase.txt")
                except Exception as e:
                    st.error(f"❌ Errore test: {e}")
        
        with col_supabase2:
            if st.button("📋 Configura Supabase"):
                st.info("🔧 **CONFIGURAZIONE SUPABASE:**")
                st.write("1. **Crea account** su [supabase.com](https://supabase.com)")
                st.write("2. **Crea progetto** con nome 'cpa-dashboard'")
                st.write("3. **Copia URL** e API Key dal dashboard")
                st.write("4. **Imposta variabili ambiente:**")
                st.code("""
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
                """)
                st.success("✅ Dopo la configurazione, riavvia l'app!")
        
        # Stato Supabase
        try:
            from supabase_manager import show_supabase_status
            show_supabase_status()
        except ImportError:
            st.warning("⚠️ **SUPABASE**: Pacchetto non installato")
        except Exception as e:
            st.error(f"❌ **SUPABASE**: Errore {e}")
        
        # Istruzioni dettagliate
        st.markdown("---")
        st.subheader("📚 Guida Completa Supabase")
        
        with st.expander("🚀 **COME INIZIARE CON SUPABASE**", expanded=False):
            st.write("""
            **STEP 1: Account e Progetto**
            - Vai su [supabase.com](https://supabase.com)
            - Crea account con GitHub
            - Crea nuovo progetto 'cpa-dashboard'
            - Scegli regione Europa per performance ottimali
            
            **STEP 2: Configurazione**
            - Copia URL progetto dal dashboard
            - Copia anon key dalla sezione API
            - Imposta variabili ambiente nel tuo sistema
            
            **STEP 3: Test e Validazione**
            - Esegui test connessione
            - Verifica operazioni CRUD
            - Testa performance e sicurezza
            """)
        
        with st.expander("🔒 **SICUREZZA E COMPLIANCE**", expanded=False):
            st.write("""
            **Caratteristiche di Sicurezza:**
            - 🔐 Autenticazione JWT sicura
            - 🛡️ Row Level Security (RLS) per isolamento dati
            - 🔒 Encryption at rest automatico
            - 🌐 SSL/TLS per tutte le connessioni
            - 📋 Audit logs completi
            
            **Compliance:**
            - ✅ GDPR compliant
            - ✅ SOC 2 certificato
            - ✅ ISO 27001 certificato
            """)
        
        with st.expander("💰 **COSTI E PIANI**", expanded=False):
            st.write("""
            **Piano Gratuito (Perfetto per iniziare):**
            - 💾 500MB database
            - 🌐 2GB bandwidth/mese
            - 📊 50,000 richieste/mese
            - 🔐 50,000 utenti autenticati
            
            **Piano Pro ($25/mese):**
            - 💾 8GB database
            - 🌐 250GB bandwidth/mese
            - 📊 500,000 richieste/mese
            - 🚀 Supporto prioritario
            """)
    
    # TAB 4: Sistema
    with tab_system:
        st.subheader("ℹ️ Informazioni Sistema")
        st.write("Configurazione e stato generale dell'applicazione")
        
        # Informazioni base
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            st.write(f"**📱 Versione:** 1.0.0")
            st.write(f"**🗄️ Database:** SQLite")
            st.write(f"**🎨 Framework:** Streamlit")
            st.write(f"**🐍 Python:** {sys.version.split()[0]}")
        
        with col_sys2:
            st.write(f"**📅 Data Creazione:** {datetime.now().strftime('%d/%m/%Y')}")
            st.write(f"**🕒 Ultimo Aggiornamento:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            st.write(f"**🟢 Stato:** Attivo")
            st.write(f"**🌐 Ambiente:** {'Streamlit Cloud' if 'STREAMLIT_SERVER_PORT' in os.environ else 'Locale'}")
        
        # Esportazione dati
        st.markdown("---")
        st.subheader("📤 Esportazione Dati")
    
    df_clienti = db.ottieni_tutti_clienti()
    
    if not df_clienti.empty:
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button("📊 Esporta Tutti i Dati"):
                csv_data = df_clienti.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica CSV Completo",
                    data=csv_data,
                    file_name=f"clienti_cpa_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_exp2:
            if st.button("📈 Esporta Statistiche"):
                stats = db.ottieni_statistiche()
                stats_df = pd.DataFrame([
                    ['Totale Clienti', stats['totale_clienti']],
                    ['Broker Attivi', stats['broker_attivi']],
                    ['Depositi Totali', f"€{stats['depositi_totali']:,.2f}"],
                    ['CPA Attive', stats['cpa_attive']]
                ], columns=['Metrica', 'Valore'])
                
                csv_stats = stats_df.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica Statistiche",
                    data=csv_stats,
                    file_name=f"statistiche_cpa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.warning("Nessun cliente presente per l'esportazione")
        
        # Logs e debugging
        st.markdown("---")
        st.subheader("📋 Logs e Debugging")
        
        col_log1, col_log2 = st.columns(2)
        
        with col_log1:
            if st.button("📊 Mostra Logs Recenti"):
                try:
                    # Mostra ultimi log se disponibili
                    log_file = "logs/cpa_dashboard.log"
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            recent_logs = lines[-20:]  # Ultime 20 righe
                            st.text_area("📋 Ultimi Logs:", value=''.join(recent_logs), height=200)
                    else:
                        st.info("File di log non trovato")
                except Exception as e:
                    st.error(f"Errore lettura logs: {e}")
        
        with col_log2:
            if st.button("🧹 Pulisci Logs"):
                try:
                    log_file = "logs/cpa_dashboard.log"
                    if os.path.exists(log_file):
                        # Crea backup del log
                        backup_log = f"logs/cpa_dashboard_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                        shutil.copy2(log_file, backup_log)
                        
                        # Pulisci il log principale
                        with open(log_file, 'w') as f:
                            f.write(f"# Log pulito il {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                        
                        st.success(f"✅ Logs puliti! Backup salvato in: {backup_log}")
                    else:
                        st.info("File di log non trovato")
                except Exception as e:
                    st.error(f"Errore pulizia logs: {e}")

# Sidebar con informazioni aggiuntive
with st.sidebar:
    st.header("ℹ️ Informazioni")
    st.write("Dashboard per la gestione delle CPA dei broker")
    
    # Azioni rapide
    st.header("🔧 Azioni Rapide")
    
    if st.button("➕ Nuovo Cliente"):
        st.session_state.editing_client = None
        st.rerun()
    
    if st.button("📊 Aggiorna Dati"):
        st.rerun()
    
    # Informazioni sui broker più comuni
    st.header("🏢 Broker Popolari")
    broker_suggestions = get_broker_suggestions()[:5]
    for broker in broker_suggestions:
        st.write(f"• {broker}")
    
    # Link utili
    st.header("🔗 Link Utili")
    st.write("• [Documentazione Streamlit](https://docs.streamlit.io/)")
    st.write("• [Plotly Charts](https://plotly.com/python/)")
    st.write("• [SQLite Tutorial](https://www.sqlitetutorial.net/)")
