#!/usr/bin/env python3
"""
Componente per gestione Link Broker - Dashboard Gestione CPA
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import re
import os
import sys

# Aggiungi il percorso della directory corrente al path di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from supabase_manager import SupabaseManager

class BrokerLinksManager:
    """Gestore per i link broker"""
    
    def __init__(self):
        """Inizializza il gestore"""
        self.supabase_manager = SupabaseManager()
        self.setup_session_state()
    
    def setup_session_state(self):
        """Inizializza lo stato della sessione"""
        if 'broker_links_editing' not in st.session_state:
            st.session_state.broker_links_editing = None
        if 'broker_links_show_form' not in st.session_state:
            st.session_state.broker_links_show_form = False
    
    def has_permission(self) -> bool:
        """Verifica se l'utente ha i permessi per gestire i broker links"""
        try:
            # Importa le funzioni di autenticazione
            from auth_simple_no_cookie import has_permission, get_current_role
            
            # Verifica se l'utente è autenticato
            if not st.session_state.get('authenticated', False):
                return False
            
            # Verifica permessi usando la nuova struttura ruoli
            current_role = get_current_role()
            
            # Admin e Manager possono gestire i broker links
            if current_role in ['admin', 'manager']:
                return True
            
            # Altri ruoli non hanno accesso
            return False
            
        except Exception as e:
            st.error(f"❌ Errore verifica permessi: {e}")
            return False
    
    def render_broker_links_page(self):
        """Rende la pagina principale dei broker links"""
        st.header("🔗 Gestione Link Broker")
        st.markdown("Gestisci i link di affiliate per i broker")
        
        # Verifica permessi
        if not self.has_permission():
            st.error("❌ Non hai i permessi per accedere a questa sezione")
            st.info("🔒 Solo Admin e Manager possono gestire i broker links")
            return
        
        # Statistiche
        self.render_stats()
        
        # Azioni rapide
        self.render_quick_actions()
        
        # Form per aggiungere/modificare
        if st.session_state.broker_links_show_form:
            self.render_broker_link_form()
        
        # Tabella dei link broker
        self.render_broker_links_table()
    
    def render_stats(self):
        """Rende le statistiche dei broker links"""
        try:
            stats = self.get_broker_links_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📊 Totale Link",
                    value=stats.get('total_links', 0),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="✅ Link Attivi",
                    value=stats.get('active_links', 0),
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="⏸️ Link Inattivi",
                    value=stats.get('inactive_links', 0),
                    delta=None
                )
            
            with col4:
                active_percentage = 0
                if stats.get('total_links', 0) > 0:
                    active_percentage = round((stats.get('active_links', 0) / stats.get('total_links', 1)) * 100, 1)
                
                st.metric(
                    label="📈 % Attivi",
                    value=f"{active_percentage}%",
                    delta=None
                )
                
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
    
    def render_quick_actions(self):
        """Rende le azioni rapide"""
        st.subheader("⚡ Azioni Rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Nuovo Link Broker", use_container_width=True, type="primary"):
                st.session_state.broker_links_show_form = True
                st.session_state.broker_links_editing = None
                st.rerun()
        
        with col2:
            if st.button("🔄 Aggiorna", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📊 Statistiche", use_container_width=True):
                self.show_detailed_stats()
        
        with col4:
            if st.button("🗑️ Elimina Multipli", use_container_width=True):
                self.show_delete_multiple_modal()
    
    def render_broker_link_form(self):
        """Rende il form per aggiungere/modificare link broker"""
        st.subheader("📝 Form Link Broker")
        
        # Recupera dati per modifica
        editing_link = None
        if st.session_state.broker_links_editing:
            editing_link = self.get_broker_link(st.session_state.broker_links_editing)
        
        with st.form("broker_link_form", clear_on_submit=True):
            # Campi del form
            broker_name = st.text_input(
                "🏢 Nome Broker *",
                value=editing_link.get('broker_name', '') if editing_link else '',
                placeholder="Es. eToro, Plus500, IG Markets",
                help="Inserisci il nome del broker"
            )
            
            affiliate_link = st.text_input(
                "🔗 Link Affiliate *",
                value=editing_link.get('affiliate_link', '') if editing_link else '',
                placeholder="https://www.broker.com/affiliate/your-link",
                help="Inserisci il link di affiliate completo"
            )
            
            is_active = st.checkbox(
                "✅ Link Attivo",
                value=editing_link.get('is_active', True) if editing_link else True,
                help="Attiva/disattiva il link"
            )
            
            # Pulsanti
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submitted = st.form_submit_button(
                    "💾 Salva Link",
                    type="primary"
                )
            
            with col2:
                if st.form_submit_button("❌ Annulla"):
                    st.session_state.broker_links_show_form = False
                    st.session_state.broker_links_editing = None
                    st.rerun()
            
            with col3:
                if editing_link and st.form_submit_button("🗑️ Elimina"):
                    self.delete_broker_link(editing_link['id'])
                    st.session_state.broker_links_show_form = False
                    st.session_state.broker_links_editing = None
                    st.rerun()
            
            # Gestione submit
            if submitted:
                # Validazione al momento del submit
                validation_errors = []
                if not broker_name.strip():
                    validation_errors.append("❌ Nome broker obbligatorio")
                
                if not affiliate_link.strip():
                    validation_errors.append("❌ Link affiliate obbligatorio")
                
                # Mostra errori di validazione
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    return  # Non procedere se ci sono errori
                
                # Se non ci sono errori, procedi con il salvataggio
                if editing_link:
                    # Modifica link esistente
                    success = self.update_broker_link(
                        editing_link['id'],
                        broker_name.strip(),
                        affiliate_link.strip(),
                        is_active
                    )
                    if success:
                        st.success("✅ Link broker aggiornato con successo!")
                        st.session_state.broker_links_show_form = False
                        st.session_state.broker_links_editing = None
                        st.rerun()
                    else:
                        st.error("❌ Errore aggiornamento link broker")
                else:
                    # Crea nuovo link
                    link_id = self.create_broker_link(
                        broker_name.strip(),
                        affiliate_link.strip()
                    )
                    if link_id:
                        st.success("✅ Link broker creato con successo!")
                        st.session_state.broker_links_show_form = False
                        st.rerun()
                    else:
                        st.error("❌ Errore creazione link broker")
    
    def render_broker_links_table(self):
        """Rende la tabella dei link broker"""
        st.subheader("📋 Lista Link Broker")
        
        try:
            # Ottieni tutti i link broker
            broker_links = self.get_broker_links(active_only=False)
            
            if not broker_links:
                st.info("📭 Nessun link broker trovato")
                return
            
            # Converti in DataFrame
            df = pd.DataFrame(broker_links)
            
            # Formatta le colonne
            if not df.empty:
                # Formatta le date
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                if 'updated_at' in df.columns:
                    df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%d/%m/%Y %H:%M')
                
                # Formatta lo stato
                if 'is_active' in df.columns:
                    df['Stato'] = df['is_active'].apply(lambda x: "✅ Attivo" if x else "⏸️ Inattivo")
                
                # Formatta il link (tronca se troppo lungo)
                if 'affiliate_link' in df.columns:
                    df['Link'] = df['affiliate_link'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
                
                # Seleziona colonne da mostrare
                display_columns = ['id', 'broker_name', 'Link', 'Stato', 'created_at']
                if 'updated_at' in df.columns:
                    display_columns.append('updated_at')
                
                display_df = df[display_columns].copy()
                display_df.columns = ['ID', 'Broker', 'Link Affiliate', 'Stato', 'Creato il', 'Aggiornato il'] if 'updated_at' in df.columns else ['ID', 'Broker', 'Link Affiliate', 'Stato', 'Creato il']
                
                # Mostra la tabella
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Azioni per ogni riga
                self.render_broker_link_actions(df)
                
        except Exception as e:
            st.error(f"❌ Errore caricamento link broker: {e}")
    
    def render_broker_link_actions(self, df: pd.DataFrame):
        """Rende le azioni per ogni link broker"""
        st.subheader("🔧 Azioni")
        
        # Selezione link per azioni (ordinata alfabeticamente)
        broker_list = df['broker_name'].tolist()
        broker_list.sort()
        selected_broker = st.selectbox(
            "Seleziona un link broker per le azioni:",
            options=broker_list,
            index=0 if not df.empty else None
        )
        
        if selected_broker:
            selected_row = df[df['broker_name'] == selected_broker].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Modifica", key=f"edit_{selected_row['id']}", use_container_width=True):
                    st.session_state.broker_links_editing = selected_row['id']
                    st.session_state.broker_links_show_form = True
                    st.rerun()
            
            with col2:
                status_text = "Disattiva" if selected_row.get('is_active', True) else "Attiva"
                if st.button(f"🔄 {status_text}", key=f"toggle_{selected_row['id']}", use_container_width=True):
                    self.toggle_broker_link_status(selected_row['id'])
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Elimina", key=f"delete_{selected_row['id']}", use_container_width=True):
                    self.show_delete_modal(selected_row)
            
            with col4:
                if st.button("🔗 Copia Link", key=f"copy_{selected_row['id']}", use_container_width=True):
                    st.write("Link copiato negli appunti!")
                    st.code(selected_row['affiliate_link'])
    
    def show_delete_modal(self, broker_link: Dict):
        """Mostra il modal di conferma eliminazione"""
        st.warning("⚠️ Conferma Eliminazione")
        st.write(f"Sei sicuro di voler eliminare il link per **{broker_link['broker_name']}**?")
        st.write(f"Link: `{broker_link['affiliate_link']}`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Conferma Eliminazione", type="primary"):
                if self.delete_broker_link(broker_link['id']):
                    st.success("✅ Link broker eliminato con successo!")
                    st.rerun()
                else:
                    st.error("❌ Errore eliminazione link broker")
        
        with col2:
            if st.button("❌ Annulla"):
                st.rerun()
    
    def show_delete_multiple_modal(self):
        """Mostra il modal per eliminazione multipla"""
        st.warning("⚠️ Eliminazione Multipla")
        st.write("Seleziona i link broker da eliminare:")
        
        try:
            broker_links = self.get_broker_links(active_only=False)
            
            if not broker_links:
                st.info("📭 Nessun link broker da eliminare")
                return
            
            # Checkbox per selezione multipla
            selected_ids = []
            for link in broker_links:
                if st.checkbox(
                    f"{link['broker_name']} - {link['affiliate_link'][:50]}...",
                    key=f"delete_multiple_{link['id']}"
                ):
                    selected_ids.append(link['id'])
            
            if selected_ids:
                st.write(f"📋 Selezionati {len(selected_ids)} link per eliminazione")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🗑️ Elimina Selezionati", type="primary"):
                        success_count = 0
                        for link_id in selected_ids:
                            if self.delete_broker_link(link_id):
                                success_count += 1
                        
                        if success_count == len(selected_ids):
                            st.success(f"✅ {success_count} link eliminati con successo!")
                        else:
                            st.warning(f"⚠️ {success_count}/{len(selected_ids)} link eliminati")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Annulla"):
                        st.rerun()
            else:
                st.info("📝 Seleziona almeno un link per eliminare")
                
        except Exception as e:
            st.error(f"❌ Errore caricamento link: {e}")
    
    def show_detailed_stats(self):
        """Mostra statistiche dettagliate"""
        st.subheader("📊 Statistiche Dettagliate")
        
        try:
            stats = self.get_broker_links_stats()
            broker_links = self.get_broker_links(active_only=False)
            
            # Statistiche generali
            st.write("**Statistiche Generali:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Totale Link", stats.get('total_links', 0))
                st.metric("Link Attivi", stats.get('active_links', 0))
            
            with col2:
                st.metric("Link Inattivi", stats.get('inactive_links', 0))
                if stats.get('total_links', 0) > 0:
                    active_percentage = round((stats.get('active_links', 0) / stats.get('total_links', 1)) * 100, 1)
                    st.metric("Percentuale Attivi", f"{active_percentage}%")
            
            # Lista dettagliata
            if broker_links:
                st.write("**Lista Dettagliata:**")
                df = pd.DataFrame(broker_links)
                
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                
                st.dataframe(
                    df[['broker_name', 'affiliate_link', 'is_active', 'created_at']],
                    use_container_width=True,
                    hide_index=True
                )
            
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
    
    # Metodi per interazione con Supabase
    def create_broker_link(self, broker_name: str, affiliate_link: str) -> Optional[int]:
        """Crea un nuovo link broker"""
        try:
            success, message = self.supabase_manager.create_broker_link(broker_name, affiliate_link)
            if success:
                # Recupera l'ID del link appena creato
                links = self.supabase_manager.get_broker_links(active_only=False)
                if links:
                    return links[0]['id']  # Il primo è quello appena creato
            else:
                st.error(message)
            return None
        except Exception as e:
            st.error(f"❌ Errore creazione link broker: {e}")
            return None
    
    def get_broker_links(self, active_only: bool = True) -> List[Dict]:
        """Ottiene tutti i link broker"""
        try:
            return self.supabase_manager.get_broker_links(active_only)
        except Exception as e:
            st.error(f"❌ Errore recupero link broker: {e}")
            return []
    
    def get_broker_link(self, link_id: int) -> Optional[Dict]:
        """Ottiene un singolo link broker"""
        try:
            return self.supabase_manager.get_broker_link(link_id)
        except Exception as e:
            st.error(f"❌ Errore recupero link broker: {e}")
            return None
    
    def update_broker_link(self, link_id: int, broker_name: str, affiliate_link: str, is_active: bool = True) -> bool:
        """Aggiorna un link broker"""
        try:
            success, message = self.supabase_manager.update_broker_link(link_id, broker_name, affiliate_link, is_active)
            if not success:
                st.error(message)
            return success
        except Exception as e:
            st.error(f"❌ Errore aggiornamento link broker: {e}")
            return False
    
    def delete_broker_link(self, link_id: int) -> bool:
        """Elimina un link broker"""
        try:
            success, message = self.supabase_manager.delete_broker_link(link_id)
            if not success:
                st.error(message)
            return success
        except Exception as e:
            st.error(f"❌ Errore eliminazione link broker: {e}")
            return False
    
    def toggle_broker_link_status(self, link_id: int) -> bool:
        """Attiva/disattiva un link broker"""
        try:
            success, message = self.supabase_manager.toggle_broker_link_status(link_id)
            if not success:
                st.error(message)
            return success
        except Exception as e:
            st.error(f"❌ Errore cambio stato link broker: {e}")
            return False
    
    def get_broker_links_stats(self) -> Dict:
        """Ottiene le statistiche dei link broker"""
        try:
            return self.supabase_manager.get_broker_links_stats()
        except Exception as e:
            st.error(f"❌ Errore statistiche link broker: {e}")
            return {
                'total_links': 0,
                'active_links': 0,
                'inactive_links': 0
            }
    
    def is_valid_url(self, url: str) -> bool:
        """Valida se l'URL è valido"""
        url_pattern = re.compile(
            r'^https?://'  # http:// o https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # dominio
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # porta opzionale
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
