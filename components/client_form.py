import streamlit as st
from datetime import datetime
from utils.translations import t

class ClientForm:
    def __init__(self):
        """Inizializza il form per i clienti"""
        pass
    
    def render_form(self, dati_cliente=None, is_edit=False):
        """Rende il form per inserimento/modifica cliente"""
        
        # Form per aggiungere/modificare cliente
        with st.expander(t("clients.add_new_client", "➕ Aggiungi Nuovo Cliente") if not is_edit else t("clients.edit_client", "✏️ Modifica Cliente"), expanded=True):
            st.subheader(t("clients.client_info", "Informazioni Cliente"))
            
            col1, col2 = st.columns(2)
            
            with col1:
                nome_cliente = st.text_input(
                    t("clients.form.name", "Nome Cliente *"), 
                    value=dati_cliente.get('nome_cliente', '') if dati_cliente else '',
                    help=t("clients.help.name", "Nome completo del cliente")
                )
                
                email = st.text_input(
                    t("clients.form.email", "Email *"), 
                    value=dati_cliente.get('email', '') if dati_cliente else '',
                    help=t("clients.help.email", "Indirizzo email del cliente")
                )
                
                password_email = st.text_input(
                    t("clients.form.password_email", "Password Email"), 
                    value=dati_cliente.get('password_email', '') if dati_cliente else '',
                    type="password",
                    help=t("clients.help.password_email", "Password per l'accesso all'email")
                )
                
                # Campo broker con menu a tendina e possibilità di aggiungerne di nuovi
                broker_options = ["Ultima Markets", "Puprime", "Axi", "Global Prime", "FxCess", "Vtmarkets", "Tauro Markets", "FPG", "TMGM", "Altro"]
                
                # Se è una modifica e il broker non è nella lista, aggiungilo
                if dati_cliente and dati_cliente.get('broker') and dati_cliente.get('broker') not in broker_options:
                    broker_options.insert(-1, dati_cliente.get('broker'))
                
                broker_selection = st.selectbox(
                    t("clients.form.broker", "Broker *"), 
                    options=broker_options,
                    index=broker_options.index(dati_cliente.get('broker', 'Ultima Markets')) if dati_cliente and dati_cliente.get('broker') in broker_options else 0,
                    help=t("clients.help.broker", "Seleziona il broker o scegli 'Altro' per inserirne uno nuovo")
                )
                
                # Se seleziona "Altro", mostra campo di testo per inserire nuovo broker
                if broker_selection == "Altro":
                    broker = st.text_input(
                        t("clients.form.new_broker", "Nome Nuovo Broker *"),
                        value="",
                        help=t("clients.help.new_broker", "Inserisci il nome del nuovo broker")
                    )
                else:
                    broker = broker_selection
                
                data_registrazione = st.date_input(
                    t("clients.form.registration_date", "Data Registrazione *"), 
                    value=datetime.fromisoformat(dati_cliente.get('data_registrazione', datetime.now().isoformat())).date() if dati_cliente and dati_cliente.get('data_registrazione') else datetime.now().date(),
                    help=t("clients.help.registration_date", "Data di registrazione del cliente")
                )
            
            with col2:
                deposito = st.number_input(
                    t("clients.form.deposit", "Deposito (€) *"), 
                    min_value=0.0, 
                    step=0.01,
                    value=float(dati_cliente.get('deposito', 0.0) or 0.0) if dati_cliente else 0.0,
                    help=t("clients.help.deposit", "Importo del deposito iniziale")
                )
                
                piattaforma = st.selectbox(
                    t("clients.form.platform", "Piattaforma *"), 
                    ["MT4", "MT5", "cTrader", "Altro"],
                    index=["MT4", "MT5", "cTrader", "Altro"].index(dati_cliente.get('piattaforma', 'MT4')) if dati_cliente else 0,
                    help=t("clients.help.platform", "Piattaforma di trading utilizzata")
                )
                
                numero_conto = st.text_input(
                    t("clients.form.account_number", "Numero Conto *"), 
                    value=dati_cliente.get('numero_conto', '') if dati_cliente else '',
                    help=t("clients.help.account_number", "Numero del conto di trading")
                )
                
                wallet = st.text_input(
                    t("clients.form.wallet", "Wallet *"), 
                    value=dati_cliente.get("wallet", "") if dati_cliente else "",
                    help=t("clients.help.wallet", "Indirizzo wallet del cliente")
                )

                password_conto = st.text_input(
                    t("clients.form.account_password", "Password Conto"), 
                    value=dati_cliente.get('password_conto', '') if dati_cliente else '',
                    type="password",
                    help=t("clients.help.account_password", "Password per l'accesso al conto di trading")
                )
            
            # Sezione VPS
            st.subheader(t("clients.form.vps_info", "Informazioni VPS"))
            col_vps1, col_vps2, col_vps3 = st.columns(3)
            
            with col_vps1:
                vps_ip = st.text_input(
                    t("clients.form.vps_ip", "IP VPS"), 
                    value=dati_cliente.get('vps_ip', '') if dati_cliente else '',
                    help=t("clients.help.vps_ip", "Indirizzo IP del server VPS")
                )
            
            with col_vps2:
                vps_username = st.text_input(
                    t("clients.form.vps_username", "Username VPS"), 
                    value=dati_cliente.get('vps_username', '') if dati_cliente else '',
                    help=t("clients.help.vps_username", "Username per l'accesso al VPS")
                )
            
            with col_vps3:
                vps_password = st.text_input(
                    t("clients.form.vps_password", "Password VPS"), 
                    value=dati_cliente.get('vps_password', '') if dati_cliente else '',
                    type="password",
                    help=t("clients.help.vps_password", "Password per l'accesso al VPS")
                )
            
            # Campi aggiuntivi dinamici
            st.subheader(t("clients.form.additional_fields", "Campi Aggiuntivi"))
            
            if 'campi_aggiuntivi' not in st.session_state:
                st.session_state.campi_aggiuntivi = []
            
            # Se è una modifica, carica i campi esistenti
            if is_edit and dati_cliente and 'campi_aggiuntivi' in dati_cliente and dati_cliente['campi_aggiuntivi']:
                if not st.session_state.campi_aggiuntivi:
                    st.session_state.campi_aggiuntivi = []
                    for campo in dati_cliente['campi_aggiuntivi']:
                        if isinstance(campo, str) and ':' in campo:
                            nome, valore = campo.split(':', 1)
                            st.session_state.campi_aggiuntivi.append({'nome': nome.strip(), 'valore': valore.strip()})
                        else:
                            st.session_state.campi_aggiuntivi.append({'nome': '', 'valore': ''})
            
            # Rendering dei campi aggiuntivi
            for i, campo in enumerate(st.session_state.campi_aggiuntivi):
                col_nome, col_valore, col_del = st.columns([2, 2, 1])
                with col_nome:
                    campo['nome'] = st.text_input(
                        f"{t('clients.form.field_name', 'Nome Campo')} {i+1}", 
                        value=campo['nome'], 
                        key=f"nome_{i}",
                        help=t("clients.help.field_name", "Nome del campo aggiuntivo")
                    )
                with col_valore:
                    campo['valore'] = st.text_input(
                        f"{t('clients.form.field_value', 'Valore')} {i+1}", 
                        value=campo['valore'], 
                        key=f"valore_{i}",
                        help=t("clients.help.field_value", "Valore del campo aggiuntivo")
                    )
                with col_del:
                    if st.button(t("common.delete", "🗑️"), key=f"del_{i}", help=t("clients.help.delete_field", "Elimina questo campo")):
                        st.session_state.campi_aggiuntivi.pop(i)
                        st.rerun()
            
            # Pulsante per aggiungere nuovi campi
            if st.button(t("clients.form.add_field", "➕ Aggiungi Campo"), help=t("clients.help.add_field", "Aggiungi un nuovo campo personalizzato")):
                st.session_state.campi_aggiuntivi.append({'nome': '', 'valore': ''})
                st.rerun()
            
            # Pulsante salva
            button_text = t("clients.form.update_client", "💾 Aggiorna Cliente") if is_edit else t("clients.form.save_client", "💾 Salva Cliente")
            if st.button(button_text, type="primary", help=t("clients.help.save_client", "Salva le informazioni del cliente")):
                if nome_cliente and email and broker and data_registrazione and deposito and piattaforma and numero_conto:
                    # Preparazione dati per il salvataggio
                    dati_salvataggio = {
                        'nome_cliente': nome_cliente,
                        'email': email,
                        'password_email': password_email,
                        'broker': broker,
                        'data_registrazione': data_registrazione,
                        'deposito': deposito,  # Campo per il deposito del cliente
                        'piattaforma': piattaforma,
                        'numero_conto': numero_conto,
                        'password_conto': password_conto,
                        'vps_ip': vps_ip,
                        'vps_username': vps_username,
                        'vps_password': vps_password
                    }
                    
                    # Filtra i campi aggiuntivi vuoti
                    campi_validi = [campo for campo in st.session_state.campi_aggiuntivi if campo['nome'] and campo['valore']]
                    
                    return True, dati_salvataggio, campi_validi
                else:
                    st.error(t("clients.form.fill_required", "Compila tutti i campi obbligatori!"))
                    return False, None, None
            
            return False, None, None
