import streamlit as st
import pandas as pd
from datetime import datetime
import re

def validate_email(email):
    """Valida il formato dell'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_ip(ip):
    """Valida il formato dell'IP"""
    if not ip:
        return True  # IP opzionale
    
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None

def format_currency(amount):
    """Formatta un importo in valuta"""
    if amount is None:
        return "€0.00"
    return f"€{amount:,.2f}"

def format_date(date):
    """Formatta una data"""
    if isinstance(date, str):
        try:
            date = pd.to_datetime(date)
        except:
            return date
    
    if hasattr(date, 'strftime'):
        return date.strftime('%d/%m/%Y')
    return str(date)

def format_datetime(datetime_obj):
    """Formatta una data e ora"""
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = pd.to_datetime(datetime_obj)
        except:
            return datetime_obj
    
    if hasattr(datetime_obj, 'strftime'):
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    return str(datetime_obj)

def clean_dataframe(df):
    """Pulisce il dataframe per la visualizzazione"""
    if df.empty:
        return df
    
    # Rimuovi colonne con tutti i valori nulli
    df = df.dropna(axis=1, how='all')
    
    # Sostituisci valori nulli con stringhe vuote per le colonne di testo
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        df[col] = df[col].fillna('')
    
    # Sostituisci valori nulli con 0 per le colonne numeriche
    numeric_columns = df.select_dtypes(include=['number']).columns
    for col in numeric_columns:
        df[col] = df[col].fillna(0)
    
    return df

def get_broker_suggestions():
    """Restituisce suggerimenti per i broker più comuni"""
    return [
        "FXPro", "Pepperstone", "IC Markets", "AvaTrade", "Plus500",
        "eToro", "IG Group", "CMC Markets", "Saxo Bank", "Interactive Brokers",
        "OANDA", "Dukascopy", "FXCM", "Gain Capital", "Monex"
    ]

def get_platform_suggestions():
    """Restituisce suggerimenti per le piattaforme"""
    return [
        "MT4", "MT5", "cTrader", "NinjaTrader", "TradingView",
        "ProRealTime", "MetaStock", "Amibroker", "Altro"
    ]

def create_sample_data():
    """Crea dati di esempio per testare l'applicazione"""
    sample_data = {
        'nome_cliente': ['Mario Rossi', 'Giulia Bianchi', 'Luca Verdi', 'Anna Neri'],
        'email': ['mario.rossi@email.com', 'giulia.bianchi@email.com', 'luca.verdi@email.com', 'anna.neri@email.com'],
        'broker': ['FXPro', 'Pepperstone', 'IC Markets', 'AvaTrade'],
        'data_registrazione': ['2024-01-15', '2024-02-01', '2024-02-15', '2024-03-01'],
        'deposito': [5000.0, 10000.0, 7500.0, 15000.0],
        'piattaforma': ['MT5', 'MT4', 'cTrader', 'MT5'],
        'numero_conto': ['12345', '67890', '11111', '22222'],
        'vps_ip': ['192.168.1.100', '192.168.1.101', '192.168.1.102', '192.168.1.103']
    }
    
    return pd.DataFrame(sample_data)

def show_success_message(message):
    """Mostra un messaggio di successo"""
    st.success(message)

def show_error_message(message):
    """Mostra un messaggio di errore"""
    st.error(message)

def show_info_message(message):
    """Mostra un messaggio informativo"""
    st.info(message)

def show_warning_message(message):
    """Mostra un messaggio di avvertimento"""
    st.warning(message)

def create_download_button(data, filename, button_text="💾 Scarica"):
    """Crea un pulsante di download"""
    return st.download_button(
        label=button_text,
        data=data,
        file_name=filename,
        mime="text/csv"
    )

def format_phone_number(phone):
    """Formatta un numero di telefono"""
    if not phone:
        return ""
    
    # Rimuovi tutti i caratteri non numerici
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11:
        return f"+{digits[:1]} {digits[1:4]}-{digits[4:7]}-{digits[7:]}"
    
    return phone

def validate_phone_number(phone):
    """Valida un numero di telefono"""
    if not phone:
        return True  # Telefono opzionale
    
    # Rimuovi tutti i caratteri non numerici
    digits = re.sub(r'\D', '', phone)
    
    # Controlla se ha almeno 10 cifre
    return len(digits) >= 10
