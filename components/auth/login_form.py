#!/usr/bin/env python3
"""
Componente Login Form per DASH_GESTIONE_LEAD
Interfaccia per l'autenticazione utenti
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import Optional, Dict
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.auth.auth_manager import auth_manager
from config import CUSTOM_COLORS

def render_login_form() -> Optional[Dict]:
    """
    Renderizza il form di login e restituisce i dati dell'utente se il login è riuscito
    
    Returns:
        Dict: Dati dell'utente se login riuscito, None altrimenti
    """
    
    # CSS personalizzato per il form di login
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-title {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        color: #666;
        font-size: 1rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.75rem;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.4);
    }
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #c62828;
        margin: 1rem 0;
    }
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container principale del login
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Header del login rimosso - titolo ora nel riquadro viola principale
        
        # Form di login
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### 🔐 Accesso")
            
            # Campo username
            username = st.text_input(
                "👤 Username",
                placeholder="Inserisci il tuo username",
                help="Username di accesso al sistema"
            )
            
            # Campo password
            password = st.text_input(
                "🔑 Password",
                type="password",
                placeholder="Inserisci la tua password",
                help="Password di accesso al sistema"
            )
            
            # Checkbox "Ricorda sessione"
            remember_session = st.checkbox(
                "💾 Mantieni la sessione attiva",
                value=True,
                help="Mantieni la sessione attiva per 30 giorni"
            )
            
            # Pulsante di login
            submit_button = st.form_submit_button(
                "🚀 Accedi",
                use_container_width=True
            )
            
            # Gestione del submit
            if submit_button:
                if not username or not password:
                    st.error("❌ Inserisci username e password")
                    return None
                
                # Tentativo di login
                user_data = auth_manager.login(username, password)
                
                if user_data:
                    st.success(f"✅ Benvenuto, {user_data['first_name']}!")
                    st.balloons()
                    
                    # Imposta il flag per mostrare la sidebar temporaneamente
                    st.session_state['show_sidebar_temporarily'] = True
                    st.session_state['sidebar_timer'] = 2  # 2 secondi
                    
                    return user_data
                else:
                    st.error("❌ Username o password non validi")
                    return None
        
        # Informazioni aggiuntive
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p><em>💡 Contatta l'amministratore per le credenziali di accesso</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return None

def render_logout_section():
    """Renderizza la sezione di logout per utenti autenticati"""
    
    current_user = auth_manager.get_current_user()
    if not current_user:
        return
    
    # Sidebar compatta per informazioni utente e logout
    with st.sidebar:
        st.markdown("### 👤 User")
        
        # Informazioni utente compatte
        st.markdown(f"**{current_user['first_name']} {current_user['last_name']}**")
        st.markdown(f"📧 {current_user['email']}")
        st.markdown(f"🎭 {current_user['role_name']}")
        if current_user.get('department_name'):
            st.markdown(f"🏢 {current_user['department_name']}")
        
        st.markdown("---")
        
        # Pulsante logout compatto
        if st.button("🚪 Logout", use_container_width=True):
            auth_manager.logout()
            st.success("✅ Logout effettuato!")
            st.rerun()

def render_auth_status():
    """Renderizza lo stato di autenticazione"""
    
    if auth_manager.is_authenticated():
        user_info = auth_manager.get_user_info()
        
        # Mostra informazioni utente nella sidebar
        with st.sidebar:
            st.markdown("### 🔐 Stato Autenticazione")
            st.success("✅ Autenticato")
            st.markdown(f"👤 **{user_info['name']}**")
            st.markdown(f"🎭 {user_info['role']}")
            st.markdown(f"🏢 {user_info['department']}")
            
            # Pulsante logout
            if st.button("🚪 Logout", key="logout_btn"):
                auth_manager.logout()
                st.success("✅ Logout effettuato!")
                st.rerun()
    else:
        # Mostra form di login
        return render_login_form()

def main():
    """Funzione principale per testare il componente"""
    st.set_page_config(
        page_title="Login - DASH_GESTIONE_LEAD",
        page_icon="🎯",
        layout="centered"
    )
    
    st.markdown("### Sistema di Autenticazione")
    
    # Test del form di login
    user_data = render_login_form()
    
    if user_data:
        st.success("✅ Login effettuato con successo!")
        st.json(user_data)

if __name__ == "__main__":
    main()
