#!/usr/bin/env python3
"""
Componente Task Manager per Dashboard_Gestione_CPA
Gestione task giornalieri/settimanali/mensili con collaboratori
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple, Any
import logging
import uuid
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
        self.telegram_manager = None
        self._init_supabase()
        # Non inizializzare TelegramManager qui per evitare loop infinito
        # self._init_telegram()
    
    def _init_supabase(self):
        """Inizializza la connessione Supabase"""
        try:
            from supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
            logger.info("✅ TasksManager inizializzato con Supabase")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase per TasksManager: {e}")
            self.supabase_manager = None
    
    def _init_telegram(self):
        """Inizializza TelegramManager se necessario"""
        try:
            if not self.telegram_manager:
                from components.telegram_manager import TelegramManager
                self.telegram_manager = TelegramManager()
                logger.info("✅ TelegramManager inizializzato per TasksManager")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione TelegramManager: {e}")
    
    def render_tasks_dashboard(self):
        """Rende la dashboard principale dei task"""
        st.header("📋 Task Giornalieri")
        st.info("🎯 **GESTIONE ATTIVITÀ**: Organizza e traccia le attività giornaliere, settimanali e mensili con i collaboratori")
        
        # Controlla se il database è configurato
        if self.supabase_manager:
            st.success("✅ **DATABASE CONFIGURATO** - I task vengono salvati permanentemente")
        else:
            st.warning("⚠️ **DATABASE NON DISPONIBILE** - I task vengono salvati temporaneamente")
            st.info("💡 Per abilitare il salvataggio permanente, configura Supabase nelle Impostazioni")
        
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
        """Tab panoramica"""
        st.subheader("📊 Panoramica Task")
        
        # Statistiche dinamiche
        tasks = self.get_tasks()
        
        if tasks:
            # Calcola statistiche
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get('status') == TaskStatus.COMPLETED.value])
            in_progress_tasks = len([t for t in tasks if t.get('status') == TaskStatus.IN_PROGRESS.value])
            cancelled_tasks = len([t for t in tasks if t.get('status') == TaskStatus.CANCELLED.value])
            
            # Mostra metriche
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📋 Totale Task", total_tasks)
            
            with col2:
                st.metric("✅ Completati", completed_tasks)
            
            with col3:
                st.metric("🔄 In Corso", in_progress_tasks)
            
            with col4:
                st.metric("❌ Cancellati", cancelled_tasks)
            
            # Task di oggi
            st.markdown("---")
            st.subheader("📅 Task di Oggi")
            
            today = date.today()
            today_tasks = [t for t in tasks if t.get('due_date') and datetime.fromisoformat(t['due_date']).date() == today]
            
            if today_tasks:
                for task in today_tasks:
                    priority_icon = "🔴" if task.get('priority') == TaskPriority.URGENT.value else "🟡"
                    st.write(f"{priority_icon} **{task.get('title', 'N/A')}** - {task.get('status', 'N/A')}")
            else:
                st.info("📅 Nessun task in scadenza oggi")
            
            # Task in scadenza
            st.markdown("---")
            st.subheader("⏰ Task in Scadenza")
            
            upcoming_tasks = []
            for task in tasks:
                if task.get('due_date') and task.get('status') in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]:
                    try:
                        due_date = datetime.fromisoformat(task['due_date']).date()
                        days_left = (due_date - today).days
                        if 0 <= days_left <= 3:
                            upcoming_tasks.append((task, days_left))
                    except:
                        continue
            
            if upcoming_tasks:
                for task, days_left in sorted(upcoming_tasks, key=lambda x: x[1]):
                    urgency = "🚨" if days_left <= 1 else "⚠️"
                    st.write(f"{urgency} **{task.get('title', 'N/A')}** - Scade tra {days_left} giorni")
            else:
                st.info("⏰ Nessun task in scadenza nei prossimi 3 giorni")
        else:
            st.info("📋 **Nessun task presente** - Crea il tuo primo task nella tab 'Crea Task'")
    
    def _render_create_task_tab(self):
        """Tab creazione task"""
        st.subheader("➕ Crea Nuovo Task")
        
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("📝 Titolo *", placeholder="Inserisci il titolo del task")
                description = st.text_area("📄 Descrizione", placeholder="Descrivi il task in dettaglio")
                priority = st.selectbox("🔥 Priorità", options=[p.value for p in TaskPriority], index=1)
            
            with col2:
                period = st.selectbox("⏰ Periodo", options=[p.value for p in TaskPeriod], index=0)
                due_date = st.date_input("📅 Scadenza", value=date.today() + timedelta(days=1))
                assigned_to = st.multiselect("👥 Assegnato a", options=self._get_collaborators_for_assignment())
            
            notes = st.text_area("📝 Note", placeholder="Note aggiuntive (opzionale)")
            
            submitted = st.form_submit_button("✅ Crea Task", type="primary")
            
            if submitted:
                if title and due_date:
                    success, message = self._create_task({
                        'title': title,
                        'description': description,
                        'priority': priority,
                        'period': period,
                        'due_date': due_date.isoformat(),
                        'assigned_to': assigned_to,
                        'notes': notes
                    })
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Compila tutti i campi obbligatori")
    
    def _render_manage_tasks_tab(self):
        """Tab gestione task - Versione compatta"""
        st.subheader("📝 Gestisci Task")
        
        # Filtri compatti
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            filter_status = st.selectbox(
                "🔍 Stato",
                options=["Tutti"] + [status.value for status in TaskStatus],
                help="Filtra per stato"
            )
        
        with col_filter2:
            filter_priority = st.selectbox(
                "⚡ Priorità",
                options=["Tutti"] + [priority.value for priority in TaskPriority],
                help="Filtra per priorità"
            )
        
        with col_filter3:
            filter_period = st.selectbox(
                "📅 Periodo",
                options=["Tutti"] + [period.value for period in TaskPeriod],
                help="Filtra per periodo"
            )
        
        # Recupera task con filtri
        status_filter = None if filter_status == "Tutti" else filter_status
        priority_filter = None if filter_priority == "Tutti" else filter_priority
        
        tasks = self.get_tasks(status=status_filter, priority=priority_filter)
        
        # Mostra solo se ci sono task
        if tasks:
            st.markdown("---")
            st.subheader("📋 Lista Task")
            st.success(f"📋 **{len(tasks)} task trovati**")
            
            for task in tasks:
                # Colori per priorità
                priority_colors = {
                    TaskPriority.LOW.value: "🟢",
                    TaskPriority.MEDIUM.value: "🟡", 
                    TaskPriority.HIGH.value: "🟠",
                    TaskPriority.URGENT.value: "🔴"
                }
                
                priority_icon = priority_colors.get(task.get('priority', ''), "⚪")
                
                # Colori per stato
                status_colors = {
                    TaskStatus.TODO.value: "🔵",
                    TaskStatus.IN_PROGRESS.value: "🟡",
                    TaskStatus.COMPLETED.value: "🟢",
                    TaskStatus.CANCELLED.value: "🔴"
                }
                
                status_icon = status_colors.get(task.get('status', ''), "⚪")
                
                with st.expander(f"{priority_icon} {task.get('title', 'N/A')} - {status_icon} {task.get('status', 'N/A')}", expanded=False):
                    # Informazioni task in colonne compatte
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.write(f"**📝 Titolo:** {task.get('title', 'N/A')}")
                        st.write(f"**📄 Descrizione:** {task.get('description', 'N/A')}")
                        st.write(f"**🔥 Priorità:** {task.get('priority', 'N/A')}")
                    
                    with col_info2:
                        st.write(f"**⏰ Periodo:** {task.get('period', 'N/A')}")
                        st.write(f"**📅 Scadenza:** {task.get('due_date', 'N/A')}")
                        st.write(f"**👥 Assegnato a:** {', '.join(task.get('assigned_to', []))}")
                    
                    # Pulsanti azione dinamici
                    task_status = task.get('status')
                    
                    if task_status == TaskStatus.CANCELLED.value:
                        # Solo pulsanti per task cancellati
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        
                        with col_btn1:
                            if st.button("🔄 Riattiva", key=f"reactivate_{task.get('id')}", type="primary"):
                                success, message = self.reactivate_task(task.get('id'))
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        with col_btn2:
                            if st.button("✏️ Modifica", key=f"modify_{task.get('id')}"):
                                st.session_state[f"editing_task_{task.get('id')}"] = True
                                st.rerun()
                        
                        with col_btn3:
                            if st.button("🗑️ Elimina", key=f"delete_{task.get('id')}"):
                                success, message = self.update_task_status(task.get('id'), TaskStatus.CANCELLED.value)
                                if success:
                                    st.success("✅ Task eliminato")
                                    st.rerun()
                    
                    elif task_status == TaskStatus.COMPLETED.value:
                        # Solo pulsanti per task completati
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("✏️ Modifica", key=f"modify_{task.get('id')}"):
                                st.session_state[f"editing_task_{task.get('id')}"] = True
                                st.rerun()
                        
                        with col_btn2:
                            if st.button("❌ Cancella", key=f"cancel_{task.get('id')}"):
                                success, message = self.update_task_status(task.get('id'), TaskStatus.CANCELLED.value)
                                if success:
                                    st.success(message)
                                    st.rerun()
                    
                    else:
                        # Pulsanti per task attivi
                        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                        
                        with col_btn1:
                            if task_status == TaskStatus.TODO.value:
                                if st.button("▶️ Inizia", key=f"start_{task.get('id')}"):
                                    success, message = self.update_task_status(task.get('id'), TaskStatus.IN_PROGRESS.value)
                                    if success:
                                        st.success(message)
                                        st.rerun()
                        
                        with col_btn2:
                            if task_status in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]:
                                if st.button("✅ Completa", key=f"complete_{task.get('id')}"):
                                    success, message = self.update_task_status(task.get('id'), TaskStatus.COMPLETED.value)
                                    if success:
                                        st.success(message)
                                        st.rerun()
                        
                        with col_btn3:
                            if st.button("✏️ Modifica", key=f"modify_{task.get('id')}"):
                                st.session_state[f"editing_task_{task.get('id')}"] = True
                                st.rerun()
                        
                        with col_btn4:
                            if st.button("❌ Cancella", key=f"cancel_{task.get('id')}"):
                                success, message = self.update_task_status(task.get('id'), TaskStatus.CANCELLED.value)
                                if success:
                                    st.success(message)
                                    st.rerun()
                    
                    # Form di modifica task
                    if st.session_state.get(f"editing_task_{task.get('id')}", False):
                        st.markdown("---")
                        st.subheader("✏️ Modifica Task")
                        
                        with st.form(f"edit_task_form_{task.get('id')}"):
                            col_edit1, col_edit2 = st.columns(2)
                            
                            with col_edit1:
                                edit_title = st.text_input("📝 Titolo", value=task.get('title', ''), key=f"edit_title_{task.get('id')}")
                                edit_description = st.text_area("📄 Descrizione", value=task.get('description', ''), key=f"edit_desc_{task.get('id')}")
                                edit_priority = st.selectbox("🔥 Priorità", options=[p.value for p in TaskPriority], index=list(TaskPriority).index(TaskPriority(task.get('priority', TaskPriority.MEDIUM.value))), key=f"edit_priority_{task.get('id')}")
                            
                            with col_edit2:
                                edit_period = st.selectbox("⏰ Periodo", options=[p.value for p in TaskPeriod], index=list(TaskPeriod).index(TaskPeriod(task.get('period', TaskPeriod.DAILY.value))), key=f"edit_period_{task.get('id')}")
                                edit_due_date = st.date_input("📅 Scadenza", value=datetime.fromisoformat(task.get('due_date', datetime.now().isoformat())).date() if task.get('due_date') else datetime.now().date(), key=f"edit_due_{task.get('id')}")
                                edit_assigned = st.multiselect("👥 Assegnato a", options=self._get_collaborators_for_assignment(), default=task.get('assigned_to', []), key=f"edit_assigned_{task.get('id')}")
                            
                            edit_notes = st.text_area("📝 Note", value=task.get('notes', ''), key=f"edit_notes_{task.get('id')}")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                if st.form_submit_button("💾 Salva Modifiche", type="primary"):
                                    edit_data = {
                                        'title': edit_title,
                                        'description': edit_description,
                                        'priority': edit_priority,
                                        'period': edit_period,
                                        'due_date': edit_due_date.isoformat(),
                                        'assigned_to': edit_assigned,
                                        'notes': edit_notes
                                    }
                                    
                                    success, message = self.update_task(task.get('id'), edit_data)
                                    if success:
                                        st.success(message)
                                        st.session_state[f"editing_task_{task.get('id')}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Annulla"):
                                    st.session_state[f"editing_task_{task.get('id')}"] = False
                                    st.rerun()
        else:
            # Interfaccia compatta quando non ci sono task
            st.markdown("---")
            st.info("📋 **Nessun task presente** - Crea il tuo primo task nella tab 'Crea Task'")
            
            # Mostra solo un esempio compatto
            with st.expander("💡 Esempio Task", expanded=False):
                st.write("**📝 Titolo:** Task di esempio")
                st.write("**📄 Descrizione:** Questo è un esempio di task")
                st.write("**🔥 Priorità:** Media")
                st.write("**⏰ Periodo:** Giornaliero")
                
                col_ex1, col_ex2, col_ex3 = st.columns(3)
                with col_ex1:
                    st.button("▶️ Inizia", key="start_example", disabled=True)
                with col_ex2:
                    st.button("✅ Completa", key="complete_example", disabled=True)
                with col_ex3:
                    st.button("❌ Cancella", key="cancel_example", disabled=True)
    
    def _render_collaborators_tab(self):
        """Tab gestione collaboratori"""
        st.subheader("👥 Gestione Collaboratori")
        
        # Mostra collaboratori disponibili
        collaborators = self._get_system_users()
        
        if collaborators:
            st.success(f"👥 **{len(collaborators)} collaboratori** disponibili nel sistema")
            
            # Tabella collaboratori
            collaborator_data = []
            for user in collaborators:
                collaborator_data.append({
                    'Username': user.get('username', 'N/A'),
                    'Email': user.get('email', 'N/A'),
                    'Ruolo': user.get('role', 'N/A'),
                    'Creato': user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'
                })
            
            st.dataframe(collaborator_data, use_container_width=True)
        else:
            st.info("👥 **Nessun collaboratore** trovato nel sistema")
            st.info("💡 I collaboratori vengono recuperati dalla tabella `users` di Supabase")
    
    def _get_collaborators_for_assignment(self) -> List[str]:
        """Recupera lista collaboratori per assegnazione task"""
        try:
            users = self._get_system_users()
            return [user.get('username', 'N/A') for user in users if user.get('username')]
        except Exception as e:
            logger.error(f"❌ Errore recupero collaboratori: {e}")
            return ['admin']  # Fallback
    
    def _get_system_users(self) -> List[Dict[str, Any]]:
        """Recupera utenti dal sistema"""
        try:
            if not self.supabase_manager:
                return []
            
            response = self.supabase_manager.supabase.table('users').select('*').execute()
            
            if response.data:
                logger.info(f"✅ Recuperati {len(response.data)} utenti dal sistema")
                return response.data
            else:
                logger.info("📋 Nessun utente trovato nel sistema")
                return []
                
        except Exception as e:
            logger.error(f"❌ Errore recupero utenti: {e}")
            return []
    
    def _create_task(self, task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Crea un nuovo task"""
        try:
            # Prova prima a salvare nel database
            if self.supabase_manager:
                try:
                    task_id = str(uuid.uuid4())
                    
                    task_record = {
                        'id': task_id,
                        'title': task_data['title'],
                        'description': task_data.get('description', ''),
                        'priority': task_data.get('priority', TaskPriority.MEDIUM.value),
                        'period': task_data.get('period', TaskPeriod.DAILY.value),
                        'due_date': task_data['due_date'],
                        'status': TaskStatus.TODO.value,
                        'assigned_to': task_data.get('assigned_to', []),
                        'notes': task_data.get('notes', ''),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'created_by': 'admin'  # In futuro prendere dall'utente corrente
                    }
                    
                    response = self.supabase_manager.supabase.table('tasks').insert(task_record).execute()
                    
                    if response.data:
                        logger.info(f"✅ Task {task_id} creato nel database")
                        
                        # Invia notifica Telegram
                        self._send_task_notification('task_new_task', {
                            'title': task_data['title'],
                            'description': task_data.get('description', ''),
                            'priority': task_data.get('priority', TaskPriority.MEDIUM.value),
                            'period': task_data.get('period', TaskPeriod.DAILY.value),
                            'due_date': task_data['due_date'],
                            'assigned_to': task_data.get('assigned_to', []),
                            'created_by': 'admin'
                        })
                        
                        return True, "✅ Task creato con successo!"
                    else:
                        return False, "❌ Errore creazione task nel database"
                        
                except Exception as e:
                    logger.error(f"❌ Errore creazione task nel database: {e}")
                    return False, f"❌ Errore database: {e}"
            
            # Fallback: salva in session state
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            task_record = {
                'id': str(uuid.uuid4()),
                'title': task_data['title'],
                'description': task_data.get('description', ''),
                'priority': task_data.get('priority', TaskPriority.MEDIUM.value),
                'period': task_data.get('period', TaskPeriod.DAILY.value),
                'due_date': task_data['due_date'],
                'status': TaskStatus.TODO.value,
                'assigned_to': task_data.get('assigned_to', []),
                'notes': task_data.get('notes', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'created_by': 'admin'
            }
            
            st.session_state.tasks.append(task_record)
            logger.info(f"✅ Task {task_record['id']} creato in session state")
            
            return True, "✅ Task creato con successo!"
            
        except Exception as e:
            logger.error(f"❌ Errore creazione task: {e}")
            return False, f"❌ Errore: {e}"
    
    def get_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recupera i task dal database o session state"""
        try:
            # Prova prima a recuperare dal database
            if self.supabase_manager:
                try:
                    query = self.supabase_manager.supabase.table('tasks').select('*')
                    
                    if status:
                        query = query.eq('status', status)
                    if priority:
                        query = query.eq('priority', priority)
                    
                    response = query.order('created_at', desc=True).execute()
                    
                    if response.data:
                        logger.info(f"✅ Recuperati {len(response.data)} task dal database")
                        return response.data
                    else:
                        logger.info("📋 Nessun task trovato nel database")
                        return []
                        
                except Exception as e:
                    logger.error(f"❌ Errore recupero task dal database: {e}")
                    # Fallback a session state
            
            # Fallback: recupera da session state
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            tasks = st.session_state.tasks
            
            # Applica filtri
            if status:
                tasks = [t for t in tasks if t.get('status') == status]
            if priority:
                tasks = [t for t in tasks if t.get('priority') == priority]
            
            logger.info(f"✅ Recuperati {len(tasks)} task da session state")
            return tasks
            
        except Exception as e:
            logger.error(f"❌ Errore recupero task: {e}")
            return []
    
    def update_task_status(self, task_id: str, new_status: str) -> Tuple[bool, str]:
        """Aggiorna lo stato di un task"""
        try:
            # Prova prima ad aggiornare nel database
            if self.supabase_manager:
                try:
                    update_data = {
                        'status': new_status,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Se completato, aggiungi timestamp completamento
                    if new_status == TaskStatus.COMPLETED.value:
                        update_data['completed_at'] = datetime.now().isoformat()
                    
                    # Se riattivato, rimuovi timestamp completamento
                    if new_status in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]:
                        update_data['completed_at'] = None
                    
                    response = self.supabase_manager.supabase.table('tasks').update(update_data).eq('id', task_id).execute()
                    
                    if response.data:
                        logger.info(f"✅ Task {task_id} aggiornato a {new_status} nel database")
                        
                        # Invia notifica Telegram se task completato
                        if new_status == TaskStatus.COMPLETED.value:
                            # Recupera i dati del task per la notifica
                            task_data = response.data[0] if response.data else {}
                            self._send_task_notification('task_completed', {
                                'title': task_data.get('title', 'N/A'),
                                'completed_by': 'Admin',  # In futuro prendere dall'utente corrente
                                'completed_at': update_data['completed_at']
                            })
                        
                        return True, f"✅ Task aggiornato a {new_status}"
                    else:
                        return False, "❌ Errore aggiornamento task nel database"
                        
                except Exception as e:
                    logger.error(f"❌ Errore aggiornamento task nel database: {e}")
                    return False, f"❌ Errore database: {e}"
            
            # Fallback: aggiorna in session state
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            for task in st.session_state.tasks:
                if task['id'] == task_id:
                    task['status'] = new_status
                    task['updated_at'] = datetime.now().isoformat()
                    
                    if new_status == TaskStatus.COMPLETED.value:
                        task['completed_at'] = datetime.now().isoformat()
                    elif new_status in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]:
                        task['completed_at'] = None
                    
                    logger.info(f"✅ Task {task_id} aggiornato a {new_status} in session state")
                    return True, f"✅ Task aggiornato a {new_status}"
            
            return False, "❌ Task non trovato"
            
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento task {task_id}: {e}")
            return False, f"❌ Errore: {e}"
    
    def reactivate_task(self, task_id: str) -> Tuple[bool, str]:
        """Riattiva un task cancellato"""
        try:
            # Prova prima ad aggiornare nel database
            if self.supabase_manager:
                try:
                    update_data = {
                        'status': TaskStatus.TODO.value,
                        'updated_at': datetime.now().isoformat(),
                        'completed_at': None  # Rimuovi timestamp completamento
                    }
                    
                    response = self.supabase_manager.supabase.table('tasks').update(update_data).eq('id', task_id).execute()
                    
                    if response.data:
                        logger.info(f"✅ Task {task_id} riattivato nel database")
                        
                        # Invia notifica Telegram per task riattivato
                        task_data = response.data[0] if response.data else {}
                        self._send_task_notification('task_new_task', {
                            'title': task_data.get('title', 'N/A'),
                            'description': task_data.get('description', 'N/A'),
                            'priority': task_data.get('priority', 'Media'),
                            'period': task_data.get('period', 'N/A'),
                            'due_date': task_data.get('due_date', 'N/A'),
                            'assigned_to': task_data.get('assigned_to', []),
                            'created_by': 'Admin'
                        })
                        
                        return True, "✅ Task riattivato con successo"
                    else:
                        return False, "❌ Errore riattivazione task nel database"
                        
                except Exception as e:
                    logger.error(f"❌ Errore riattivazione task nel database: {e}")
                    return False, f"❌ Errore database: {e}"
            
            # Fallback: aggiorna in session state
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            for task in st.session_state.tasks:
                if task['id'] == task_id:
                    task['status'] = TaskStatus.TODO.value
                    task['updated_at'] = datetime.now().isoformat()
                    task['completed_at'] = None
                    
                    logger.info(f"✅ Task {task_id} riattivato in session state")
                    return True, "✅ Task riattivato con successo"
            
            return False, "❌ Task non trovato"
            
        except Exception as e:
            logger.error(f"❌ Errore riattivazione task {task_id}: {e}")
            return False, f"❌ Errore: {e}"
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Modifica un task esistente"""
        try:
            # Prova prima ad aggiornare nel database
            if self.supabase_manager:
                try:
                    update_data = {
                        'title': task_data.get('title', ''),
                        'description': task_data.get('description', ''),
                        'priority': task_data.get('priority', TaskPriority.MEDIUM.value),
                        'period': task_data.get('period', TaskPeriod.DAILY.value),
                        'due_date': task_data.get('due_date', ''),
                        'assigned_to': task_data.get('assigned_to', []),
                        'notes': task_data.get('notes', ''),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    response = self.supabase_manager.supabase.table('tasks').update(update_data).eq('id', task_id).execute()
                    
                    if response.data:
                        logger.info(f"✅ Task {task_id} modificato nel database")
                        
                        # Invia notifica Telegram per task modificato
                        self._send_task_notification('task_new_task', {
                            'title': update_data['title'],
                            'description': update_data['description'],
                            'priority': update_data['priority'],
                            'period': update_data['period'],
                            'due_date': update_data['due_date'],
                            'assigned_to': update_data['assigned_to'],
                            'created_by': 'Admin'
                        })
                        
                        return True, "✅ Task modificato con successo"
                    else:
                        return False, "❌ Errore modifica task nel database"
                        
                except Exception as e:
                    logger.error(f"❌ Errore modifica task nel database: {e}")
                    return False, f"❌ Errore database: {e}"
            
            # Fallback: aggiorna in session state
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            for task in st.session_state.tasks:
                if task['id'] == task_id:
                    task.update(update_data)
                    logger.info(f"✅ Task {task_id} modificato in session state")
                    return True, "✅ Task modificato con successo"
            
            return False, "❌ Task non trovato"
            
        except Exception as e:
            logger.error(f"❌ Errore modifica task {task_id}: {e}")
            return False, f"❌ Errore: {e}"
    
    def _send_task_notification(self, notification_type: str, data: Dict[str, Any]):
        """Invia notifica Telegram per eventi task"""
        try:
            # Inizializza TelegramManager solo se necessario
            if not self.telegram_manager:
                self._init_telegram()
            
            if not self.telegram_manager or not self.telegram_manager.is_configured:
                logger.info("📱 Telegram non configurato, notifica task non inviata")
                return
            
            # Controlla se le notifiche per questo tipo specifico sono abilitate
            if not self._is_notification_enabled(notification_type):
                logger.info(f"🔔 Notifiche '{notification_type}' disabilitate")
                return
            
            # Invia la notifica
            success, message = self.telegram_manager.send_notification(notification_type, data)
            
            if success:
                logger.info(f"✅ Notifica task '{notification_type}' inviata con successo")
            else:
                logger.warning(f"⚠️ Errore invio notifica task '{notification_type}': {message}")
                
        except Exception as e:
            logger.error(f"❌ Errore invio notifica task '{notification_type}': {e}")
    
    def _is_notification_enabled(self, notification_type: str) -> bool:
        """Controlla se le notifiche per un tipo specifico sono abilitate"""
        try:
            if not self.supabase_manager:
                # Default settings se Supabase non disponibile
                default_settings = {
                    'task_new_task': True,
                    'task_completed': True,
                    'task_due_soon': True,
                    'task_daily_report': False,
                }
                return default_settings.get(notification_type, True)
            
            # Recupera impostazioni notifiche dal database
            response = self.supabase_manager.supabase.table('notification_settings').select('*').eq('notification_type', notification_type).execute()
            
            if response.data and len(response.data) > 0:
                setting = response.data[0]
                return setting.get('is_enabled', True)
            else:
                # Default settings se nessuna impostazione trovata
                default_settings = {
                    'task_new_task': True,
                    'task_completed': True,
                    'task_due_soon': True,
                    'task_daily_report': False,
                }
                return default_settings.get(notification_type, True)
                
        except Exception as e:
            logger.error(f"❌ Errore controllo impostazioni notifiche {notification_type}: {e}")
            # Default settings in caso di errore
            default_settings = {
                'task_new_task': True,
                'task_completed': True,
                'task_due_soon': True,
                'task_daily_report': False,
            }
            return default_settings.get(notification_type, True)
    
    def check_task_due_notifications(self):
        """Controlla e invia notifiche per task in scadenza"""
        try:
            tasks = self.get_tasks()
            today = date.today()
            
            for task in tasks:
                if not task.get('due_date') or task.get('status') in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
                    continue
                
                try:
                    due_date = datetime.fromisoformat(task['due_date']).date()
                    days_left = (due_date - today).days
                    
                    # Invia notifica se scade tra 1-3 giorni
                    if 1 <= days_left <= 3:
                        self._send_task_notification('task_due_soon', {
                            'title': task.get('title', 'N/A'),
                            'days_left': days_left,
                            'assigned_to': task.get('assigned_to', []),
                            'priority': task.get('priority', 'N/A')
                        })
                except Exception as e:
                    logger.error(f"❌ Errore controllo scadenza task {task.get('id')}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Errore controllo task in scadenza: {e}")
