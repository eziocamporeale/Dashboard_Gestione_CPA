#!/usr/bin/env python3
"""
Dashboard Gestione CPA - App Unificata
Versione pulita e moderna con schema raggruppato
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys

# Aggiungi path per import
current_dir = os.getcwd()
app_unified_path = os.path.join(current_dir, 'app_unified')
sys.path.insert(0, app_unified_path)

from database.database_manager import UnifiedDatabaseManager

# Configurazione pagina
st.set_page_config(
    page_title="Dashboard CPA - App Unificata",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione database
@st.cache_resource
def init_database():
    """Inizializza il database unificato"""
    try:
        return UnifiedDatabaseManager()
    except Exception as e:
        st.error(f"❌ Errore inizializzazione database: {e}")
        return None

# Inizializza database
db = init_database()

if db is None:
    st.error("❌ Impossibile inizializzare il database. Verifica la configurazione.")
    st.stop()

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

# ===== GESTIONE CLIENTI BASE =====

def handle_add_base_client():
    """Gestisce l'aggiunta di un nuovo cliente base"""
    st.subheader("➕ Aggiungi Nuovo Cliente Base")
    
    with st.form("add_base_client_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input("Nome Cliente *", key="nome_base")
            email = st.text_input("Email *", key="email_base")
        
        with col2:
            vps = st.text_input("VPS (opzionale)", key="vps_base")
            note_cliente = st.text_area("Note Cliente (opzionale)", key="note_base")
        
        submitted = st.form_submit_button("➕ Crea Cliente Base")
        
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
            
            success, result = db.add_cliente_base(dati_cliente)
            
            if success:
                show_success_message(f"✅ Cliente base {nome_cliente} creato con successo!")
                st.info("🏦 Ora vai alla **Panoramica** e clicca **'+ Aggiungi Account Broker'** per aggiungere i suoi account!")
            else:
                show_error_message(f"❌ Errore creazione cliente: {result}")

def handle_add_broker_account():
    """Gestisce l'aggiunta di un nuovo account broker"""
    st.subheader("🏦 Aggiungi Nuovo Account Broker")
    
    # Ottieni lista clienti base per selezione
    clienti_base = db.get_all_clienti_base()
    
    if not clienti_base:
        st.warning("⚠️ Nessun cliente base presente. Aggiungi prima un cliente base.")
        return
    
    with st.form("add_broker_account_form"):
        # Selezione cliente base
        cliente_options = {f"{c['nome_cliente']} ({c['email']})": c['id'] for c in clienti_base}
        cliente_selezionato = st.selectbox("Cliente Base *", options=list(cliente_options.keys()), key="cliente_select")
        cliente_id = cliente_options[cliente_selezionato]
        
        # Ottieni broker predefiniti
        broker_list = db.get_all_broker()
        broker_options = {b['nome_broker']: b['nome_broker'] for b in broker_list}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Menu a tendina con broker predefiniti + opzione per nuovo
            broker_options['+ Aggiungi Nuovo Broker'] = '+ Aggiungi Nuovo Broker'
            broker_selezionato = st.selectbox("Broker *", options=list(broker_options.keys()), key="broker_select")
            
            # Se seleziona "Aggiungi Nuovo Broker", mostra form per nuovo broker
            if broker_selezionato == '+ Aggiungi Nuovo Broker':
                with st.expander("➕ Aggiungi Nuovo Broker", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nuovo_broker = st.text_input("Nome Nuovo Broker *", key="nuovo_broker")
                        piattaforma_default = st.selectbox("Piattaforma Default", ["MT4", "MT5", "cTrader", "WebTrader", "Mobile"], key="piattaforma_default")
                    with col_b:
                        note_broker = st.text_area("Note Broker", key="note_broker")
                    
                    if st.button("➕ Salva Nuovo Broker", key="save_broker"):
                        if nuovo_broker:
                            dati_broker = {
                                'nome_broker': nuovo_broker,
                                'piattaforma_default': piattaforma_default,
                                'note_broker': note_broker
                            }
                            success, result = db.add_broker(dati_broker)
                            if success:
                                st.success(f"✅ Broker {nuovo_broker} aggiunto!")
                                st.rerun()
                            else:
                                st.error(f"❌ Errore aggiunta broker: {result}")
                        else:
                            st.error("❌ Nome broker obbligatorio!")
                
                # Dopo aver aggiunto il broker, lo seleziona automaticamente
                if 'nuovo_broker' in st.session_state and st.session_state.nuovo_broker:
                    broker_selezionato = st.session_state.nuovo_broker
            
            # Form semplificato per account (solo dati essenziali)
            numero_conto = st.text_input("Numero Conto *", key="conto_account")
            password = st.text_input("Password *", type="password", key="password_account")
            server = st.text_input("Server (opzionale)", key="server_account")
        
        with col2:
            # Campi opzionali avanzati
            with st.expander("⚙️ Impostazioni Avanzate"):
                api_key = st.text_input("API Key", key="api_key_account")
                secret_key = st.text_input("Secret Key", key="secret_key_account")
                ip_address = st.text_input("IP Address", key="ip_account")
                volume_posizione = st.number_input("Volume Posizione", min_value=0.0, value=0.0, step=0.01, key="volume_account")
                ruolo = st.selectbox("Ruolo", ["User", "Admin", "Manager"], key="ruolo_account")
        
        submitted = st.form_submit_button("🏦 Aggiungi Account Broker")
        
        if submitted:
            if not broker_selezionato or broker_selezionato == '+ Aggiungi Nuovo Broker' or not numero_conto or not password:
                show_error_message("❌ Broker, numero conto e password sono obbligatori!")
                return
            
            # Ottieni piattaforma default del broker selezionato
            piattaforma_default = "MT4"  # Default
            for broker in broker_list:
                if broker['nome_broker'] == broker_selezionato:
                    piattaforma_default = broker['piattaforma_default']
                    break
            
            dati_account = {
                'cliente_base_id': cliente_id,
                'broker': broker_selezionato,
                'piattaforma': piattaforma_default,
                'numero_conto': numero_conto,
                'password': password,
                'api_key': api_key if 'api_key' in locals() else '',
                'secret_key': secret_key if 'secret_key' in locals() else '',
                'ip_address': ip_address if 'ip_address' in locals() else '',
                'volume_posizione': volume_posizione if 'volume_posizione' in locals() else 0.0,
                'ruolo': ruolo if 'ruolo' in locals() else 'User'
            }
            
            success, result = db.add_account_broker(dati_account)
            
            if success:
                show_success_message(f"✅ Account broker {broker_selezionato} - {numero_conto} aggiunto con successo!")
            else:
                show_error_message(f"❌ Errore aggiunta account: {result}")

# ===== VISUALIZZAZIONE DATI =====

def show_clients_overview():
    """Mostra panoramica clienti raggruppati"""
    st.subheader("👥 Panoramica Clienti")
    
    # Statistiche generali
    stats = db.get_statistiche()
    
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
    clienti_completi = db.get_all_clienti_completi()
    
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
                
                # Pulsante per aggiungere account broker
                if st.button(f"🏦 + Aggiungi Account Broker", key=f"add_account_{cliente['id']}"):
                    st.session_state.adding_account_for = cliente['id']
                    st.session_state.adding_account_name = cliente['nome_cliente']
            
            with col2:
                # Azioni rapide
                if st.button(f"✏️ Modifica {cliente['nome_cliente']}", key=f"edit_{cliente['id']}"):
                    st.session_state.editing_client = cliente['id']
                
                if st.button(f"🗑️ Elimina {cliente['nome_cliente']}", key=f"delete_{cliente['id']}"):
                    if st.button(f"⚠️ Conferma Eliminazione", key=f"confirm_delete_{cliente['id']}"):
                        if db.delete_cliente_base(cliente['id']):
                            show_success_message(f"✅ Cliente {cliente['nome_cliente']} eliminato!")
                        else:
                            show_error_message("❌ Errore eliminazione cliente")
    
    # Form per aggiungere account broker se richiesto
    if hasattr(st.session_state, 'adding_account_for'):
        show_add_account_form(st.session_state.adding_account_for, st.session_state.adding_account_name)

def show_add_account_form(cliente_id, nome_cliente):
    """Mostra form per aggiungere account broker a un cliente specifico"""
    st.subheader(f"🏦 Aggiungi Account Broker per {nome_cliente}")
    
    # Ottieni broker predefiniti
    broker_list = db.get_all_broker()
    broker_options = {b['nome_broker']: b['nome_broker'] for b in broker_list}
    broker_options['+ Aggiungi Nuovo Broker'] = '+ Aggiungi Nuovo Broker'
    
    with st.form(f"add_account_form_{cliente_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Menu a tendina con broker predefiniti
            broker_selezionato = st.selectbox("Broker *", options=list(broker_options.keys()), key=f"broker_{cliente_id}")
            
            # Se seleziona "Aggiungi Nuovo Broker", mostra form per nuovo broker
            if broker_selezionato == '+ Aggiungi Nuovo Broker':
                with st.expander("➕ Aggiungi Nuovo Broker", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nuovo_broker = st.text_input("Nome Nuovo Broker *", key=f"nuovo_broker_{cliente_id}")
                        piattaforma_default = st.selectbox("Piattaforma Default", ["MT4", "MT5", "cTrader", "WebTrader", "Mobile"], key=f"piattaforma_default_{cliente_id}")
                    with col_b:
                        note_broker = st.text_area("Note Broker", key=f"note_broker_{cliente_id}")
                    
                    if st.button("➕ Salva Nuovo Broker", key=f"save_broker_{cliente_id}"):
                        if nuovo_broker:
                            dati_broker = {
                                'nome_broker': nuovo_broker,
                                'piattaforma_default': piattaforma_default,
                                'note_broker': note_broker
                            }
                            success, result = db.add_broker(dati_broker)
                            if success:
                                st.success(f"✅ Broker {nuovo_broker} aggiunto!")
                                st.rerun()
                            else:
                                st.error(f"❌ Errore aggiunta broker: {result}")
                        else:
                            st.error("❌ Nome broker obbligatorio!")
            
            # Form semplificato per account (solo dati essenziali)
            numero_conto = st.text_input("Numero Conto *", key=f"conto_{cliente_id}")
            password = st.text_input("Password *", type="password", key=f"password_{cliente_id}")
            server = st.text_input("Server (opzionale)", key=f"server_{cliente_id}")
        
        with col2:
            # Campi opzionali avanzati
            with st.expander("⚙️ Impostazioni Avanzate"):
                api_key = st.text_input("API Key", key=f"api_key_{cliente_id}")
                secret_key = st.text_input("Secret Key", key=f"secret_key_{cliente_id}")
                ip_address = st.text_input("IP Address", key=f"ip_{cliente_id}")
                volume_posizione = st.number_input("Volume Posizione", min_value=0.0, value=0.0, step=0.01, key=f"volume_{cliente_id}")
                ruolo = st.selectbox("Ruolo", ["User", "Admin", "Manager"], key=f"ruolo_{cliente_id}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            submitted = st.form_submit_button("🏦 Aggiungi Account")
        
        with col2:
            if st.form_submit_button("❌ Annulla"):
                st.session_state.adding_account_for = None
                st.session_state.adding_account_name = None
                st.rerun()
        
        with col3:
            if st.form_submit_button("🏦 + Altro Account"):
                # Salva account corrente e prepara per il prossimo
                if broker_selezionato and broker_selezionato != '+ Aggiungi Nuovo Broker' and numero_conto and password:
                    # Ottieni piattaforma default del broker selezionato
                    piattaforma_default = "MT4"  # Default
                    for broker in broker_list:
                        if broker['nome_broker'] == broker_selezionato:
                            piattaforma_default = broker['piattaforma_default']
                            break
                    
                    dati_account = {
                        'cliente_base_id': cliente_id,
                        'broker': broker_selezionato,
                        'piattaforma': piattaforma_default,
                        'numero_conto': numero_conto,
                        'password': password,
                        'api_key': api_key if 'api_key' in locals() else '',
                        'secret_key': secret_key if 'secret_key' in locals() else '',
                        'ip_address': ip_address if 'ip_address' in locals() else '',
                        'volume_posizione': volume_posizione if 'volume_posizione' in locals() else 0.0,
                        'ruolo': ruolo if 'ruolo' in locals() else 'User'
                    }
                    
                    success, result = db.add_account_broker(dati_account)
                    
                    if success:
                        st.success(f"✅ Account {broker_selezionato} - {numero_conto} aggiunto! Aggiungi il prossimo...")
                        # Mantieni il form aperto per il prossimo account
                        st.session_state.adding_account_for = cliente_id
                        st.session_state.adding_account_name = nome_cliente
                        st.rerun()
                    else:
                        st.error(f"❌ Errore aggiunta account: {result}")
        
        if submitted:
            if not broker_selezionato or broker_selezionato == '+ Aggiungi Nuovo Broker' or not numero_conto or not password:
                show_error_message("❌ Broker, numero conto e password sono obbligatori!")
                return
            
            # Ottieni piattaforma default del broker selezionato
            piattaforma_default = "MT4"  # Default
            for broker in broker_list:
                if broker['nome_broker'] == broker_selezionato:
                    piattaforma_default = broker['piattaforma_default']
                    break
            
            dati_account = {
                'cliente_base_id': cliente_id,
                'broker': broker_selezionato,
                'piattaforma': piattaforma_default,
                'numero_conto': numero_conto,
                'password': password,
                'api_key': api_key if 'api_key' in locals() else '',
                'secret_key': secret_key if 'secret_key' in locals() else '',
                'ip_address': ip_address if 'ip_address' in locals() else '',
                'volume_posizione': volume_posizione if 'volume_posizione' in locals() else 0.0,
                'ruolo': ruolo if 'ruolo' in locals() else 'User'
            }
            
            success, result = db.add_account_broker(dati_account)
            
            if success:
                show_success_message(f"✅ Account broker {broker_selezionato} - {numero_conto} aggiunto con successo!")
                # Chiudi il form
                st.session_state.adding_account_for = None
                st.session_state.adding_account_name = None
            else:
                show_error_message(f"❌ Errore aggiunta account: {result}")

def show_broker_accounts():
    """Mostra tutti gli account broker"""
    st.subheader("🏦 Account Broker")
    
    accounts = db.get_all_accounts()
    
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

# ===== GRAFICI E STATISTICHE =====

def show_charts():
    """Mostra grafici e statistiche"""
    st.subheader("📊 Grafici e Statistiche")
    
    stats = db.get_statistiche()
    accounts = db.get_all_accounts()
    
    if not accounts:
        st.info("ℹ️ Nessun dato disponibile per i grafici.")
        return
    
    df = pd.DataFrame(accounts)
    
    col1, col2 = st.columns(2)
    
    with col1:
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
        # Grafico distribuzione piattaforme
        if 'piattaforma' in df.columns:
            platform_counts = df['piattaforma'].value_counts()
            
            fig = px.pie(
                values=platform_counts.values,
                names=platform_counts.index,
                title="🖥️ Distribuzione Piattaforme"
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== MAIN APP =====

def main():
    """Funzione principale dell'app"""
    st.title("📊 Dashboard Gestione CPA - App Unificata")
    st.markdown("---")
    
    # Sidebar per navigazione
    st.sidebar.title("🧭 Navigazione")
    
    page = st.sidebar.selectbox(
        "Seleziona Sezione",
        ["🏠 Dashboard", "👥 Gestione Clienti", "🏦 Gestione Account", "📊 Statistiche", "⚙️ Impostazioni"]
    )
    
    # Contenuto principale
    if page == "🏠 Dashboard":
        st.header("🏠 Dashboard Principale")
        show_clients_overview()
        show_charts()
        
    elif page == "👥 Gestione Clienti":
        st.header("👥 Gestione Clienti Base")
        
        tab1, tab2 = st.tabs(["📋 Panoramica", "➕ Nuovo Cliente"])
        
        with tab1:
            show_clients_overview()
        
        with tab2:
            handle_add_base_client()
            
    elif page == "🏦 Gestione Account":
        st.header("🏦 Gestione Account Broker")
        
        tab1, tab2 = st.tabs(["📋 Panoramica Account", "➕ Aggiungi Account"])
        
        with tab1:
            show_broker_accounts()
        
        with tab2:
            handle_add_broker_account()
            
    elif page == "📊 Statistiche":
        st.header("📊 Statistiche Dettagliate")
        show_charts()
        
        # Statistiche aggiuntive
        stats = db.get_statistiche()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Metriche Generali")
            st.metric("👥 Clienti Totali", stats['totale_clienti'])
            st.metric("🏦 Account Totali", stats['totale_account'])
            st.metric("💰 Volume Totale", format_currency(stats['volume_totale']))
        
        with col2:
            st.subheader("🏢 Broker Attivi")
            st.metric("Numero Broker", stats['broker_attivi'])
            
    elif page == "⚙️ Impostazioni":
        st.header("⚙️ Impostazioni")
        
        tab1, tab2, tab3 = st.tabs(["🗄️ Database", "🏢 Gestione Broker", "🔧 Sistema"])
        
        with tab1:
            st.subheader("🗄️ Informazioni Database")
            stats = db.get_statistiche()
            
            st.info(f"""
            **Database Schema Raggruppato**
            - Clienti Base: {stats['totale_clienti']}
            - Account Broker: {stats['totale_account']}
            - Broker Attivi: {stats['broker_attivi']}
            - Volume Totale: {format_currency(stats['volume_totale'])}
            """)
            
            # Test connessione
            if st.button("🔗 Test Connessione Database"):
                if db.test_connection():
                    st.success("✅ Connessione database OK!")
                else:
                    st.error("❌ Errore connessione database")
        
        with tab2:
            st.subheader("🏢 Gestione Broker Predefiniti")
            
            # Lista broker esistenti
            broker_list = db.get_all_broker()
            
            if broker_list:
                st.write("**📋 Broker Configurati:**")
                for broker in broker_list:
                    with st.expander(f"🏢 {broker['nome_broker']} ({broker['piattaforma_default']})", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            if broker['note_broker']:
                                st.info(f"📝 Note: {broker['note_broker']}")
                            st.write(f"📅 Creato: {broker['created_at']}")
                            st.write(f"🔄 Aggiornato: {broker['updated_at']}")
                        
                        with col2:
                            if st.button(f"✏️ Modifica {broker['nome_broker']}", key=f"edit_broker_{broker['id']}"):
                                st.session_state.editing_broker = broker['id']
                            
                            if st.button(f"🗑️ Elimina {broker['nome_broker']}", key=f"delete_broker_{broker['id']}"):
                                if st.button(f"⚠️ Conferma Eliminazione", key=f"confirm_delete_broker_{broker['id']}"):
                                    if db.delete_broker(broker['id']):
                                        show_success_message(f"✅ Broker {broker['nome_broker']} eliminato!")
                                    else:
                                        show_error_message("❌ Errore eliminazione broker")
            else:
                st.info("ℹ️ Nessun broker configurato.")
            
            # Form per aggiungere nuovo broker
            st.subheader("➕ Aggiungi Nuovo Broker")
            
            with st.form("add_broker_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome_broker = st.text_input("Nome Broker *", key="nome_broker_new")
                    piattaforma_default = st.selectbox("Piattaforma Default", ["MT4", "MT5", "cTrader", "WebTrader", "Mobile"], key="piattaforma_default_new")
                
                with col2:
                    note_broker = st.text_area("Note Broker", key="note_broker_new")
                
                submitted = st.form_submit_button("➕ Aggiungi Broker")
                
                if submitted:
                    if not nome_broker:
                        show_error_message("❌ Nome broker obbligatorio!")
                        return
                    
                    dati_broker = {
                        'nome_broker': nome_broker,
                        'piattaforma_default': piattaforma_default,
                        'note_broker': note_broker
                    }
                    
                    success, result = db.add_broker(dati_broker)
                    
                    if success:
                        show_success_message(f"✅ Broker {nome_broker} aggiunto con successo!")
                    else:
                        show_error_message(f"❌ Errore aggiunta broker: {result}")
        
        with tab3:
            st.subheader("🔧 Sistema")
            st.info("Configurazioni di sistema e utilità")
            
            # Test connessione
            if st.button("🔗 Test Connessione Database", key="test_conn_settings"):
                if db.test_connection():
                    st.success("✅ Connessione database OK!")
                else:
                    st.error("❌ Errore connessione database")

if __name__ == "__main__":
    main()
