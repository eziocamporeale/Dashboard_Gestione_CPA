import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu

# Import dei componenti
from database.database import DatabaseManager
from database.incroci_manager import IncrociManager
from components.client_form import ClientForm
from components.client_table import ClientTable
from components.charts import Charts
from components.incroci_tab import IncrociTab
from components.auth import require_auth, show_user_info, login_form
from utils.helpers import *

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
    return {
        'client_form': ClientForm(),
        'client_table': ClientTable(),
        'charts': Charts(),
        'incroci_tab': IncrociTab(IncrociManager(db.db_path), db)
    }

# Inizializzazione
db = init_database()
components = init_components()

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
def handle_save_client(dati_cliente, campi_aggiuntivi):
    """Gestisce il salvataggio di un nuovo cliente"""
    success, result = db.aggiungi_cliente(dati_cliente, campi_aggiuntivi)
    if success:
        show_success_message(f"Cliente {dati_cliente['nome_cliente']} salvato con successo!")
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
    """Gestisce l'eliminazione di un cliente"""
    # Verifica permessi
    if not st.session_state.get('authenticated', False):
        st.error("🔒 Accesso richiesto per eliminare clienti")
        return
    
    # Mostra conferma semplice
    if st.button(f"❌ Conferma Eliminazione Cliente {cliente_id}", key=f"confirm_delete_{cliente_id}", type="primary"):
        # Elimina il cliente dopo conferma
        success = db.elimina_cliente(cliente_id)
        
        if success:
            st.success(f"✅ Cliente {cliente_id} eliminato con successo!")
            st.rerun()
        else:
            st.error(f"❌ Errore nell'eliminazione del cliente {cliente_id}")
    else:
        st.info(f"⚠️ Clicca 'Conferma Eliminazione' per eliminare il cliente {cliente_id}")

def handle_update_client(cliente_id, dati_cliente, campi_aggiuntivi):
    """Gestisce l'aggiornamento di un cliente esistente"""
    success = db.modifica_cliente(cliente_id, dati_cliente, campi_aggiuntivi)
    if success:
        show_success_message(f"Cliente {dati_cliente['nome_cliente']} aggiornato con successo!")
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
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nessun cliente presente nel database. Aggiungi clienti per visualizzare i dati!")

elif selected == "⚙️ Impostazioni":
    st.header("Impostazioni")
    st.write("Configura le impostazioni dell'applicazione")
    
    # Configurazione database
    st.subheader("🗄️ Database")
    
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
    
    # Esportazione dati
    st.subheader("📤 Esportazione")
    
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
    
    # Informazioni sistema
    st.subheader("ℹ️ Informazioni Sistema")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.write(f"**Versione:** 1.0.0")
        st.write(f"**Database:** SQLite")
        st.write(f"**Framework:** Streamlit")
    
    with col_info2:
        st.write(f"**Data Creazione:** {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"**Ultimo Aggiornamento:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.write(f"**Stato:** Attivo")

# Sidebar con informazioni aggiuntive
with st.sidebar:
    st.header("ℹ️ Informazioni")
    st.write("Dashboard per la gestione delle CPA dei broker")
    
    # Statistiche rapide
    df_clienti = db.ottieni_tutti_clienti()
    stats = db.ottieni_statistiche()
    
    st.header("📊 Statistiche Rapide")
    st.write(f"**Clienti Totali:** {stats['totale_clienti']}")
    st.write(f"**Broker Attivi:** {stats['broker_attivi']}")
    st.write(f"**Depositi Totali:** {format_currency(stats['depositi_totali'])}")
    
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
