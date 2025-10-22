#!/usr/bin/env python3
"""
Componente Task Manager per Dashboard_Gestione_CPA
Gestione task giornalieri/settimanali/mensili con collaboratori
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from enum import Enum

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Priorità dei task"""
    LOW = "Bassa"
    MEDIUM = "Media"
    HIGH = "Alta"
    URGENT = "Urgente"

class TaskStatus(Enum):
    """Stato dei task"""
    TODO = "Da Fare"
    IN_PROGRESS = "In Corso"
    COMPLETED = "Completato"
    CANCELLED = "Cancellato"

class TaskPeriod(Enum):
    """Periodo dei task"""
    DAILY = "Giornaliero"
    WEEKLY = "Settimanale"
    MONTHLY = "Mensile"
    CUSTOM = "Personalizzato"

class TasksManager:
    """Gestore per i task giornalieri/settimanali/mensili"""
    
    def __init__(self):
        """Inizializza il gestore task"""
        self.supabase_manager = None
        self._init_supabase()
        logger.info("✅ TasksManager inizializzato correttamente")
    
    def _init_supabase(self):
        """Inizializza la connessione Supabase"""
        try:
            from database.supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
            logger.info("✅ Supabase inizializzato per TasksManager")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase: {e}")
            self.supabase_manager = None
    
    def render_tasks_dashboard(self):
        """Rende il dashboard principale dei task"""
        st.header("📋 Task Giornalieri")
        st.info("🎯 **GESTIONE ATTIVITÀ**: Organizza e traccia le attività giornaliere, settimanali e mensili con i collaboratori")
        
        # Tab per organizzare le funzionalità
        tab_overview, tab_create, tab_manage, tab_collaborators = st.tabs([
            "📊 Panoramica", "➕ Crea Task", "📝 Gestisci Task", "👥 Collaboratori"
        ])
        
        with tab_overview:
            self._render_overview_tab()
        
        with tab_create:
            self._render_create_task_tab()
        
        with tab_manage:
            self._render_manage_tasks_tab()
        
        with tab_collaborators:
            self._render_collaborators_tab()
    
    def _render_overview_tab(self):
        """Tab panoramica task"""
        st.subheader("📊 Panoramica Task")
        
        # Statistiche rapide
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Task Totali", "0", "0")
        with col2:
            st.metric("⏳ In Corso", "0", "0")
        with col3:
            st.metric("✅ Completati", "0", "0")
        with col4:
            st.metric("👥 Collaboratori", "0", "0")
        
        # Task di oggi
        st.markdown("---")
        st.subheader("📅 Task di Oggi")
        st.info("📋 **ATTIVITÀ GIORNALIERE**: Task programmati per oggi")
        
        # Placeholder per task di oggi
        st.write("• Nessun task programmato per oggi")
        
        # Task in scadenza
        st.markdown("---")
        st.subheader("⏰ Task in Scadenza")
        st.info("🚨 **ATTENZIONE**: Task che scadono nei prossimi 3 giorni")
        
        # Placeholder per task in scadenza
        st.write("• Nessun task in scadenza")
    
    def _render_create_task_tab(self):
        """Tab creazione task"""
        st.subheader("➕ Crea Nuovo Task")
        
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                task_title = st.text_input(
                    "📝 Titolo Task",
                    placeholder="Es: Controllo saldi clienti",
                    help="Titolo descrittivo del task"
                )
                
                task_description = st.text_area(
                    "📄 Descrizione",
                    placeholder="Descrizione dettagliata del task...",
                    help="Descrizione completa del task"
                )
                
                task_priority = st.selectbox(
                    "⚡ Priorità",
                    options=[priority.value for priority in TaskPriority],
                    help="Livello di priorità del task"
                )
            
            with col2:
                task_period = st.selectbox(
                    "📅 Periodo",
                    options=[period.value for period in TaskPeriod],
                    help="Frequenza del task"
                )
                
                due_date = st.date_input(
                    "📆 Scadenza",
                    value=date.today() + timedelta(days=1),
                    help="Data di scadenza del task"
                )
                
                assigned_to = st.multiselect(
                    "👥 Assegna a",
                    options=["Admin", "Collaboratore 1", "Collaboratore 2"],
                    help="Collaboratori assegnati al task"
                )
            
            # Pulsanti
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submitted = st.form_submit_button("✅ Crea Task", type="primary")
            
            with col_btn2:
                if st.form_submit_button("❌ Annulla"):
                    st.rerun()
            
            if submitted:
                if task_title and task_description:
                    success, message = self._create_task(
                        title=task_title,
                        description=task_description,
                        priority=task_priority,
                        period=task_period,
                        due_date=due_date,
                        assigned_to=assigned_to
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Compila tutti i campi obbligatori")
    
    def _render_manage_tasks_tab(self):
        """Tab gestione task"""
        st.subheader("📝 Gestisci Task")
        
        # Filtri
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            filter_status = st.selectbox(
                "🔍 Filtra per Stato",
                options=["Tutti"] + [status.value for status in TaskStatus],
                help="Filtra i task per stato"
            )
        
        with col_filter2:
            filter_priority = st.selectbox(
                "⚡ Filtra per Priorità",
                options=["Tutti"] + [priority.value for priority in TaskPriority],
                help="Filtra i task per priorità"
            )
        
        with col_filter3:
            filter_period = st.selectbox(
                "📅 Filtra per Periodo",
                options=["Tutti"] + [period.value for period in TaskPeriod],
                help="Filtra i task per periodo"
            )
        
        # Lista task
        st.markdown("---")
        st.subheader("📋 Lista Task")
        
        # Placeholder per lista task
        st.info("📋 **Nessun task presente** - Crea il tuo primo task nella tab 'Crea Task'")
        
        # Esempio di task
        with st.expander("📝 Esempio Task", expanded=False):
            st.write("**Titolo:** Controllo saldi clienti")
            st.write("**Descrizione:** Verificare i saldi di tutti i clienti e aggiornare il database")
            st.write("**Priorità:** Alta")
            st.write("**Periodo:** Giornaliero")
            st.write("**Scadenza:** 23/10/2025")
            st.write("**Assegnato a:** Admin")
            st.write("**Stato:** Da Fare")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("▶️ Inizia", key="start_example"):
                    st.success("✅ Task iniziato!")
            with col_btn2:
                if st.button("✅ Completa", key="complete_example"):
                    st.success("✅ Task completato!")
            with col_btn3:
                if st.button("❌ Cancella", key="cancel_example"):
                    st.warning("⚠️ Task cancellato!")
    
    def _render_collaborators_tab(self):
        """Tab gestione collaboratori"""
        st.subheader("👥 Gestione Collaboratori")
        st.info("🤝 **TEAM MANAGEMENT**: Gestisci i collaboratori e le loro assegnazioni")
        
        # Lista collaboratori
        st.markdown("---")
        st.subheader("👥 Lista Collaboratori")
        
        # Placeholder per collaboratori
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **👤 Admin**
            - Ruolo: Amministratore
            - Task assegnati: 0
            - Task completati: 0
            """)
        
        with col2:
            st.markdown("""
            **👤 Collaboratore 1**
            - Ruolo: Operatore
            - Task assegnati: 0
            - Task completati: 0
            """)
        
        with col3:
            st.markdown("""
            **👤 Collaboratore 2**
            - Ruolo: Operatore
            - Task assegnati: 0
            - Task completati: 0
            """)
        
        # Aggiungi collaboratore
        st.markdown("---")
        st.subheader("➕ Aggiungi Collaboratore")
        
        with st.form("add_collaborator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                collaborator_name = st.text_input(
                    "👤 Nome Collaboratore",
                    placeholder="Es: Mario Rossi",
                    help="Nome completo del collaboratore"
                )
                
                collaborator_email = st.text_input(
                    "📧 Email",
                    placeholder="mario.rossi@example.com",
                    help="Email del collaboratore"
                )
            
            with col2:
                collaborator_role = st.selectbox(
                    "👑 Ruolo",
                    options=["Operatore", "Supervisore", "Amministratore"],
                    help="Ruolo del collaboratore"
                )
                
                collaborator_department = st.text_input(
                    "🏢 Dipartimento",
                    placeholder="Es: Gestione Clienti",
                    help="Dipartimento di appartenenza"
                )
            
            submitted = st.form_submit_button("✅ Aggiungi Collaboratore", type="primary")
            
            if submitted:
                if collaborator_name and collaborator_email:
                    st.success(f"✅ Collaboratore {collaborator_name} aggiunto con successo!")
                else:
                    st.error("❌ Compila tutti i campi obbligatori")
    
    def _create_task(self, title: str, description: str, priority: str, period: str, 
                    due_date: date, assigned_to: List[str]) -> Tuple[bool, str]:
        """Crea un nuovo task"""
        try:
            # Per ora salva in session state (in futuro integreremo con Supabase)
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            task_id = f"task_{len(st.session_state.tasks) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            task_data = {
                'id': task_id,
                'title': title,
                'description': description,
                'priority': priority,
                'period': period,
                'due_date': due_date.isoformat(),
                'assigned_to': assigned_to,
                'status': TaskStatus.TODO.value,
                'created_at': datetime.now().isoformat(),
                'created_by': 'Admin'  # In futuro prendere dall'utente corrente
            }
            
            st.session_state.tasks.append(task_data)
            
            logger.info(f"✅ Task creato: {title}")
            return True, f"✅ Task '{title}' creato con successo!"
            
        except Exception as e:
            logger.error(f"❌ Errore creazione task: {e}")
            return False, f"❌ Errore nella creazione del task: {e}"
    
    def get_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        """Ottiene la lista dei task"""
        try:
            if 'tasks' not in st.session_state:
                return []
            
            tasks = st.session_state.tasks.copy()
            
            # Filtri
            if status:
                tasks = [task for task in tasks if task['status'] == status]
            
            if priority:
                tasks = [task for task in tasks if task['priority'] == priority]
            
            return tasks
            
        except Exception as e:
            logger.error(f"❌ Errore recupero task: {e}")
            return []
    
    def update_task_status(self, task_id: str, new_status: str) -> Tuple[bool, str]:
        """Aggiorna lo stato di un task"""
        try:
            if 'tasks' not in st.session_state:
                return False, "❌ Nessun task trovato"
            
            for task in st.session_state.tasks:
                if task['id'] == task_id:
                    task['status'] = new_status
                    task['updated_at'] = datetime.now().isoformat()
                    
                    logger.info(f"✅ Task {task_id} aggiornato a {new_status}")
                    return True, f"✅ Task aggiornato a {new_status}"
            
            return False, "❌ Task non trovato"
            
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento task: {e}")
            return False, f"❌ Errore nell'aggiornamento: {e}"
