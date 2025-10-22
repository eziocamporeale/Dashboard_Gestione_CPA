#!/usr/bin/env python3
"""
Componente Menu Centrale per Dashboard_Gestione_CPA
Menu di navigazione posizionato al centro della dashboard, sempre visibile
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.auth.auth_simple import get_current_user

def render_central_menu(current_page: str = "🏠 Dashboard") -> str:
    """
    Renderizza il menu centrale sempre visibile
    
    Args:
        current_page: Pagina corrente selezionata
        
    Returns:
        str: Pagina selezionata
    """
    
    # CSS per il menu centrale sempre visibile
    st.markdown("""
    <style>
    .menu-buttons {
        margin: 1rem 0;
    }
    .menu-buttons {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .menu-btn {
        background: white;
        color: #333;
        border: 2px solid #e0e0e0;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .menu-btn:hover {
        background: #f5f5f5;
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .menu-btn.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
        font-weight: bold;
    }
    .menu-btn.active:hover {
        background: white;
        color: #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container del menu
    st.markdown("""
    <div class="menu-buttons">
    """, unsafe_allow_html=True)
    
    # Ottieni le opzioni del menu basate sui permessi utente
    current_user = get_current_user()
    menu_options = [
        ("🏠 Dashboard", "🏠 Dashboard"),
        ("👥 Gestione Clienti", "👥 Gestione Clienti"), 
        ("🔄 Incroci", "🔄 Incroci"),
        ("🔗 Broker", "🔗 Broker"),
        ("🖥️ VPS", "🖥️ VPS"),
        ("💰 Wallet", "💰 Wallet"),
        ("📋 Task Giornalieri", "📋 Task Giornalieri"),
        ("📁 Storage", "📁 Storage"),
        ("📈 Riepilogo", "📈 Riepilogo"),
        ("🤖 AI Assistant", "🤖 AI Assistant"),
        ("⚙️ Impostazioni", "⚙️ Impostazioni")
    ]
    
    # Crea i pulsanti del menu direttamente
    cols = st.columns(len(menu_options))
    selected_page = current_page
    
    for i, (display_name, page_value) in enumerate(menu_options):
        with cols[i]:
            is_active = page_value == current_page
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                display_name, 
                key=f"menu_btn_{page_value}",
                help=f"Vai alla sezione {display_name}",
                use_container_width=True,
                type=button_type
            ):
                # Imposta la nuova pagina direttamente
                selected_page = page_value
                st.session_state['current_page'] = page_value
                st.rerun()
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return selected_page

def render_compact_sidebar():
    """
    Renderizza una sidebar compatta solo con info utente e logout
    """
    with st.sidebar:
        st.markdown("### 👤 Utente")
        
        # Informazioni utente
        current_user = get_current_user()
        if current_user:
            st.markdown(f"**👤 {current_user.get('username', 'N/A')}**")
            st.markdown(f"📧 {current_user.get('email', 'N/A')}")
            st.markdown(f"👑 {current_user.get('role', 'N/A')}")
            st.markdown(f"🏢 {current_user.get('name', 'N/A')}")
        
        st.markdown("---")
        
        # Pulsante logout
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            # Pulisci session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
