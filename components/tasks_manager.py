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
            from supabase_manager import SupabaseManager
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
        
        # Calcola statistiche reali
        tasks = self.get_tasks()
        collaborators = self._get_system_users()
        
        total_tasks = len(tasks)
        in_progress = len([task for task in tasks if task['status'] == TaskStatus.IN_PROGRESS.value])
        completed = len([task for task in tasks if task['status'] == TaskStatus.COMPLETED.value])
        total_collaborators = len(collaborators)
        
        with col1:
            st.metric("📋 Task Totali", total_tasks, "0")
        with col2:
            st.metric("⏳ In Corso", in_progress, "0")
        with col3:
            st.metric("✅ Completati", completed, "0")
        with col4:
            st.metric("👥 Collaboratori", total_collaborators, "0")
        
        # Task di oggi
        st.markdown("---")
        st.subheader("📅 Task di Oggi")
        st.info("📋 **ATTIVITÀ GIORNALIERE**: Task programmati per oggi")
        
        # Filtra task di oggi
        today = date.today()
        today_tasks = [task for task in tasks if task.get('due_date') == today.isoformat()]
        
        if today_tasks:
            st.success(f"📋 **{len(today_tasks)} task** programmati per oggi")
            for task in today_tasks:
                priority_color = {
                    TaskPriority.LOW.value: "🟢",
                    TaskPriority.MEDIUM.value: "🟡", 
                    TaskPriority.HIGH.value: "🟠",
                    TaskPriority.URGENT.value: "🔴"
                }.get(task['priority'], "⚪")
                
                st.write(f"{priority_color} **{task['title']}** - {task['priority']} - Assegnato a: {', '.join(task.get('assigned_to', []))}")
        else:
            st.write("• Nessun task programmato per oggi")
        
        # Task in scadenza
        st.markdown("---")
        st.subheader("⏰ Task in Scadenza")
        st.info("🚨 **ATTENZIONE**: Task che scadono nei prossimi 3 giorni")
        
        # Filtra task in scadenza (nei prossimi 3 giorni)
        three_days_later = today + timedelta(days=3)
        upcoming_tasks = []
        
        for task in tasks:
            if task.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(task['due_date']).date()
                    if today <= due_date <= three_days_later:
                        upcoming_tasks.append(task)
                except:
                    continue
        
        if upcoming_tasks:
            st.warning(f"🚨 **{len(upcoming_tasks)} task** in scadenza nei prossimi 3 giorni")
            for task in upcoming_tasks:
                try:
                    due_date = datetime.fromisoformat(task['due_date']).date()
                    days_left = (due_date - today).days
                    
                    priority_color = {
                        TaskPriority.LOW.value: "🟢",
                        TaskPriority.MEDIUM.value: "🟡", 
                        TaskPriority.HIGH.value: "🟠",
                        TaskPriority.URGENT.value: "🔴"
                    }.get(task['priority'], "⚪")
                    
                    urgency_text = "OGGI!" if days_left == 0 else f"tra {days_left} giorni"
                    st.write(f"{priority_color} **{task['title']}** - Scade {urgency_text} - {task['priority']}")
                except:
                    continue
        else:
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
                    options=self.get_collaborators_for_assignment(),
                    help="Collaboratori assegnati al task (basati sugli account utenti)"
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
        st.info("🤝 **TEAM MANAGEMENT**: Collaboratori basati sugli account utenti del sistema")
        
        # Lista collaboratori dal sistema utenti
        st.markdown("---")
        st.subheader("👥 Lista Collaboratori")
        
        try:
            # Ottieni lista utenti dal sistema di autenticazione
            users = self._get_system_users()
            
            if users:
                st.success(f"✅ **{len(users)} collaboratori** trovati nel sistema")
                
                # Mostra collaboratori in colonne
                cols_per_row = 3
                for i in range(0, len(users), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(users):
                            user = users[i + j]
                            with col:
                                # Calcola statistiche task per questo utente
                                task_stats = self._get_user_task_stats(user['username'])
                                
                                st.markdown(f"""
                                **👤 {user.get('name', user['username'])}**
                                - Username: {user['username']}
                                - Ruolo: {user.get('role', 'N/A')}
                                - Email: {user.get('email', 'N/A')}
                                - Task assegnati: {task_stats['assigned']}
                                - Task completati: {task_stats['completed']}
                                """)
            else:
                st.warning("⚠️ **Nessun collaboratore trovato** - Crea account utenti nel sistema")
                st.info("💡 **Come aggiungere collaboratori:**")
                st.write("1. Vai alla sezione **⚙️ Impostazioni**")
                st.write("2. Tab **🛡️ Permessi**")
                st.write("3. Crea nuovi account utenti")
                st.write("4. I nuovi utenti appariranno automaticamente qui")
                
        except Exception as e:
            st.error(f"❌ **Errore caricamento collaboratori**: {e}")
            st.info("🔧 Controlla la connessione al database utenti")
        
        # Informazioni aggiuntive
        st.markdown("---")
        st.subheader("ℹ️ Informazioni Sistema")
        st.info("📋 **GESTIONE AUTOMATICA**: I collaboratori vengono sincronizzati automaticamente con gli account utenti del sistema")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.write("**✅ Vantaggi:**")
            st.write("• Sincronizzazione automatica")
            st.write("• Gestione centralizzata")
            st.write("• Controllo accessi integrato")
            st.write("• Ruoli e permessi unificati")
        
        with col_info2:
            st.write("**🔧 Come funziona:**")
            st.write("• Ogni account utente = Collaboratore")
            st.write("• Ruoli dal sistema di autenticazione")
            st.write("• Statistiche task automatiche")
            st.write("• Aggiornamento in tempo reale")
    
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
    
    def _get_system_users(self) -> List[Dict]:
        """Ottiene la lista degli utenti dal sistema di autenticazione"""
        try:
            logger.info("🔍 Tentativo recupero utenti dal sistema...")
            
            if not self.supabase_manager:
                logger.warning("❌ Supabase non disponibile per recupero utenti")
                return []
            
            logger.info("✅ SupabaseManager disponibile, eseguo query...")
            
            # Recupera utenti dalla tabella users
            response = self.supabase_manager.supabase.table('users').select('*').execute()
            
            logger.info(f"📊 Risposta query: {len(response.data) if response.data else 0} utenti")
            
            if response.data:
                logger.info(f"✅ Recuperati {len(response.data)} utenti dal sistema")
                return response.data
            else:
                logger.warning("⚠️ Nessun utente trovato nel sistema")
                return []
                
        except Exception as e:
            logger.error(f"❌ Errore recupero utenti: {e}")
            return []
    
    def _get_user_task_stats(self, username: str) -> Dict[str, int]:
        """Calcola le statistiche task per un utente specifico"""
        try:
            if 'tasks' not in st.session_state:
                return {'assigned': 0, 'completed': 0, 'in_progress': 0}
            
            user_tasks = [task for task in st.session_state.tasks if username in task.get('assigned_to', [])]
            
            stats = {
                'assigned': len(user_tasks),
                'completed': len([task for task in user_tasks if task['status'] == TaskStatus.COMPLETED.value]),
                'in_progress': len([task for task in user_tasks if task['status'] == TaskStatus.IN_PROGRESS.value])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Errore calcolo statistiche utente {username}: {e}")
            return {'assigned': 0, 'completed': 0, 'in_progress': 0}
    
    def get_collaborators_for_assignment(self) -> List[str]:
        """Ottiene la lista dei collaboratori per l'assegnazione task"""
        try:
            users = self._get_system_users()
            collaborators = []
            
            for user in users:
                # Usa il nome completo se disponibile, altrimenti username
                display_name = user.get('name', user['username'])
                collaborators.append(display_name)
            
            return collaborators
            
        except Exception as e:
            logger.error(f"❌ Errore recupero collaboratori per assegnazione: {e}")
            return ["Admin"]  # Fallback
