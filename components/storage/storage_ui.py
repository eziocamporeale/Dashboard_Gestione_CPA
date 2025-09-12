#!/usr/bin/env python3
"""
Interfaccia Utente per Storage Manager - Dashboard Gestione CPA
Componenti UI per upload, download e gestione file
Creato da Ezio Camporeale per Dashboard Gestione CPA
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.storage.storage_manager import StorageManager
from utils.translations import t

def render_storage_wrapper():
    """
    Wrapper principale per la sezione storage
    """
    st.title("📁 Storage File CPA")
    st.markdown("---")
    
    # Inizializza il manager
    storage_manager = StorageManager()
    
    # Ottieni utente corrente
    current_user = st.session_state.get('user_info', {})
    # Controlla sia role che is_admin per compatibilità
    is_admin = current_user and (
        current_user.get('role') == 'admin' or 
        current_user.get('is_admin', False)
    )
    
    # Mostra informazioni utente
    if current_user:
        role_display = current_user.get('role', 'user').title()
        st.success(f"✅ Loggato come: {current_user.get('username')} ({role_display})")
    else:
        st.error("❌ Nessun utente loggato")
    
    # Layout principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sezione principale (lista file o upload)
        if is_admin:
            # Admin: mostra tab per upload e gestione
            tab1, tab2, tab3 = st.tabs(["📋 Lista File", "⬆️ Carica File", "📊 Statistiche"])
            
            with tab1:
                render_file_list(storage_manager, is_admin=True)
            
            with tab2:
                render_upload_section(storage_manager)
            
            with tab3:
                render_storage_stats(storage_manager)
        else:
            # Utenti normali: solo lista file
            render_file_list(storage_manager, is_admin=False)
    
    with col2:
        # Sidebar con filtri e info
        render_storage_sidebar(storage_manager, is_admin)

def render_upload_section(storage_manager: StorageManager):
    """
    Sezione per il caricamento di file (solo Admin)
    """
    st.subheader("⬆️ Carica Nuovi File")
    
    with st.form("upload_form", clear_on_submit=True):
        # Upload multipli
        uploaded_files = st.file_uploader(
            "Seleziona uno o più file da caricare",
            type=None,  # Accetta tutti i tipi
            accept_multiple_files=True,
            help="Puoi selezionare più file contemporaneamente"
        )
        
        # Categoria
        category = st.selectbox(
            "Categoria",
            options=list(storage_manager.categories.keys()),
            help="Seleziona la categoria appropriata per i file"
        )
        
        # Descrizione
        description = st.text_area(
            "Descrizione (opzionale)",
            placeholder="Inserisci una descrizione per i file...",
            height=100
        )
        
        # Pulsante di caricamento
        submitted = st.form_submit_button("🚀 Carica File", use_container_width=True)
        
        if submitted and uploaded_files:
            if len(uploaded_files) > 10:
                st.warning("⚠️ Puoi caricare massimo 10 file alla volta")
                return
            
            # Carica ogni file
            success_count = 0
            error_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    status_text.text(f"Caricando {uploaded_file.name}...")
                    
                    result = storage_manager.upload_file(
                        uploaded_file=uploaded_file,
                        category=category,
                        description=description
                    )
                    
                    if result['success']:
                        success_count += 1
                        st.success(f"✅ {uploaded_file.name}")
                    else:
                        error_count += 1
                        st.error(f"❌ {uploaded_file.name}: {result['message']}")
                    
                    # Aggiorna progress bar
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                except Exception as e:
                    error_count += 1
                    st.error(f"❌ {uploaded_file.name}: Errore - {str(e)}")
                    progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Risultato finale
            status_text.empty()
            progress_bar.empty()
            
            if success_count > 0:
                st.success(f"🎉 {success_count} file caricati con successo!")
            if error_count > 0:
                st.error(f"⚠️ {error_count} file non sono stati caricati")
            
            # Refresh automatico della pagina
            st.rerun()

def render_file_list(storage_manager: StorageManager, is_admin: bool = False):
    """
    Lista dei file disponibili
    """
    st.subheader("📋 File Disponibili")
    
    # Filtri
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Ordina categorie alfabeticamente
        categories_list = ["Tutte"] + sorted(list(storage_manager.categories.keys()))
        category_filter = st.selectbox(
            "Filtra per categoria",
            options=categories_list,
            key="file_category_filter"
        )
    
    with col2:
        search_term = st.text_input(
            "🔍 Cerca file",
            placeholder="Inserisci il nome del file...",
            key="file_search"
        )
    
    # Recupera file
    files = storage_manager.get_files(
        category=category_filter if category_filter != "Tutte" else None,
        search=search_term if search_term else None
    )
    
    if not files:
        st.info("📭 Nessun file trovato")
        return
    
    # Mostra file in formato tabella
    for file in files:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                # Informazioni file
                st.markdown(f"**{file['original_filename']}**")
                if file['description']:
                    st.caption(f"📝 {file['description']}")
                st.caption(f"📁 {file['category']} • {storage_manager.format_file_size(file['file_size'])} • {file['download_count']} download")
            
            with col2:
                # Data caricamento
                upload_date = datetime.fromisoformat(file['uploaded_at'].replace('Z', '+00:00'))
                st.caption(f"📅 {upload_date.strftime('%d/%m/%Y')}")
            
            with col3:
                # Pulsante download
                if st.button("⬇️", key=f"download_{file['id']}", help="Scarica file"):
                    success, filename, content = storage_manager.download_file(file['id'])
                    if success:
                        st.download_button(
                            label="💾 Scarica",
                            data=content,
                            file_name=filename,
                            mime=file['file_type'],
                            key=f"dl_{file['id']}"
                        )
                    else:
                        st.error(f"Errore: {filename}")
            
            with col4:
                # Pulsante elimina (solo admin)
                if is_admin:
                    if st.button("🗑️", key=f"delete_{file['id']}", help="Elimina file"):
                        if st.session_state.get(f"confirm_delete_{file['id']}", False):
                            result = storage_manager.delete_file(file['id'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
                        else:
                            st.session_state[f"confirm_delete_{file['id']}"] = True
                            st.warning("Clicca di nuovo per confermare l'eliminazione")
            
            st.markdown("---")

def render_storage_sidebar(storage_manager: StorageManager, is_admin: bool):
    """
    Sidebar con informazioni e filtri
    """
    st.subheader("ℹ️ Informazioni")
    
    # Statistiche rapide
    stats = storage_manager.get_storage_stats()
    
    st.metric("📁 File Totali", stats['total_files'])
    st.metric("💾 Spazio Utilizzato", storage_manager.format_file_size(stats['total_size']))
    
    # Categorie
    if stats['categories']:
        st.subheader("📊 Per Categoria")
        for category, data in stats['categories'].items():
            st.write(f"**{category}**: {data['count']} file ({storage_manager.format_file_size(data['size'])})")
    
    # Istruzioni
    st.subheader("📖 Istruzioni")
    
    if is_admin:
        st.info("""
        **Come Admin puoi:**
        - ⬆️ Caricare file multipli
        - 🗑️ Eliminare file esistenti
        - 📊 Visualizzare statistiche dettagliate
        - 🏷️ Categorizzare i file
        """)
    else:
        st.info("""
        **Come utente puoi:**
        - 👀 Visualizzare tutti i file
        - ⬇️ Scaricare i file disponibili
        - 🔍 Cercare file per nome
        - 🏷️ Filtrare per categoria
        """)
    
    # Informazioni tecniche
    with st.expander("🔧 Info Tecniche"):
        st.write(f"**Directory Storage**: `{storage_manager.storage_dir}`")
        st.write(f"**Categorie Supportate**: {len(storage_manager.categories)}")
        st.write(f"**Formati Supportati**: Tutti i tipi di file")
        
        # Mostra categorie specifiche CPA
        st.write("**Categorie CPA:**")
        for cat in storage_manager.categories.keys():
            st.write(f"• {cat}")

def render_storage_stats(storage_manager: StorageManager):
    """
    Statistiche dettagliate dello storage (solo Admin)
    """
    st.subheader("📊 Statistiche Storage")
    
    stats = storage_manager.get_storage_stats()
    
    if stats['total_files'] == 0:
        st.info("📭 Nessun file presente nel sistema")
        return
    
    # Metriche principali
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📁 File Totali", stats['total_files'])
    
    with col2:
        st.metric("💾 Spazio Totale", storage_manager.format_file_size(stats['total_size']))
    
    with col3:
        avg_size = stats['total_size'] / stats['total_files'] if stats['total_files'] > 0 else 0
        st.metric("📏 Dimensione Media", storage_manager.format_file_size(int(avg_size)))
    
    # Grafico categorie
    if stats['categories']:
        st.subheader("📊 Distribuzione per Categoria")
        
        # Prepara dati per il grafico
        categories = list(stats['categories'].keys())
        counts = [stats['categories'][cat]['count'] for cat in categories]
        sizes = [stats['categories'][cat]['size'] for cat in categories]
        
        # Grafico a barre per numero di file
        try:
            import plotly.express as px
            
            fig_count = px.bar(
                x=categories,
                y=counts,
                title="Numero di File per Categoria",
                labels={'x': 'Categoria', 'y': 'Numero di File'}
            )
            st.plotly_chart(fig_count, use_container_width=True)
            
            # Grafico a barre per spazio utilizzato
            fig_size = px.bar(
                x=categories,
                y=[storage_manager.format_file_size(size) for size in sizes],
                title="Spazio Utilizzato per Categoria",
                labels={'x': 'Categoria', 'y': 'Spazio Utilizzato'}
            )
            st.plotly_chart(fig_size, use_container_width=True)
        except ImportError:
            st.warning("Plotly non disponibile per i grafici")
    
    # Tabella dettagliata
    st.subheader("📋 Dettaglio Categorie")
    
    if stats['categories']:
        df_data = []
        for category, data in stats['categories'].items():
            df_data.append({
                'Categoria': category,
                'File': data['count'],
                'Spazio': storage_manager.format_file_size(data['size']),
                'Spazio (bytes)': data['size']
            })
        
        df = pd.DataFrame(df_data)
        df = df.sort_values('Spazio (bytes)', ascending=False)
        df = df.drop('Spazio (bytes)', axis=1)
        
        st.dataframe(df, use_container_width=True)
