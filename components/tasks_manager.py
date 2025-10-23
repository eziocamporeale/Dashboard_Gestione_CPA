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
        self._init_telegram()
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
    
    def _init_telegram(self):
        """Inizializza il gestore Telegram"""
        try:
            from components.telegram_manager import TelegramManager
            self.telegram_manager = TelegramManager()
            logger.info("✅ TelegramManager inizializzato per TasksManager")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione TelegramManager: {e}")
            self.telegram_manager = None
    
    def render_tasks_dashboard(self):
        """Rende il dashboard principale dei task"""
        st.header("📋 Task Giornalieri")
        st.info("🎯 **GESTIONE ATTIVITÀ**: Organizza e traccia le attività giornaliere, settimanali e mensili con i collaboratori")

        # Avviso sulla persistenza dei dati
        if not self.supabase_manager:
            st.error("❌ **SUPABASE NON CONFIGURATO** - I task vengono salvati temporaneamente")
        else:
            # Controlla se la tabella tasks esiste
            try:
                test_response = self.supabase_manager.supabase.table('tasks').select('*').limit(1).execute()
                if test_response.data is not None:
                    st.success("✅ **DATABASE CONFIGURATO** - I task vengono salvati permanentemente")
                else:
                    st.warning("⚠️ **TABELLA TASKS MANCANTE** - I task vengono salvati temporaneamente")
                    st.info("💡 **Per salvare permanentemente i task:**\n1. Vai al dashboard Supabase\n2. Crea la tabella 'tasks' con i campi necessari\n3. Ricarica questa pagina")
            except Exception as e:
                st.warning("⚠️ **TABELLA TASKS NON TROVATA** - I task vengono salvati temporaneamente")
                st.info("💡 **Per salvare permanentemente i task:**\n1. Vai al dashboard Supabase\n2. Crea la tabella 'tasks' con i campi necessari\n3. Ricarica questa pagina")
        
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
        
        # Recupera task con filtri
        status_filter = None if filter_status == "Tutti" else filter_status
        priority_filter = None if filter_priority == "Tutti" else filter_priority
        
        tasks = self.get_tasks(status=status_filter, priority=priority_filter)
        
        if tasks:
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
                    st.write(f"**📝 Titolo:** {task.get('title', 'N/A')}")
                    st.write(f"**📄 Descrizione:** {task.get('description', 'N/A')}")
                    st.write(f"**🔥 Priorità:** {task.get('priority', 'N/A')}")
                    st.write(f"**⏰ Periodo:** {task.get('period', 'N/A')}")
                    st.write(f"**📅 Scadenza:** {task.get('due_date', 'N/A')}")
                    st.write(f"**👥 Assegnato a:** {', '.join(task.get('assigned_to', []))}")
                    st.write(f"**📅 Creato il:** {task.get('created_at', 'N/A')}")
                    
                    # Pulsanti azione
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if task.get('status') == TaskStatus.TODO.value:
                            if st.button("▶️ Inizia", key=f"start_{task.get('id')}"):
                                success, message = self.update_task_status(task.get('id'), TaskStatus.IN_PROGRESS.value)
                                if success:
                                    st.success(message)
                                    st.rerun()
                    
                    with col_btn2:
                        if task.get('status') in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]:
                            if st.button("✅ Completa", key=f"complete_{task.get('id')}"):
                                success, message = self.update_task_status(task.get('id'), TaskStatus.COMPLETED.value)
                                if success:
                                    st.success(message)
                                    st.rerun()
                    
                    with col_btn3:
                        if st.button("❌ Cancella", key=f"cancel_{task.get('id')}"):
                            success, message = self.update_task_status(task.get('id'), TaskStatus.CANCELLED.value)
                            if success:
                                st.success(message)
                                st.rerun()
        else:
            st.info("📋 **Nessun task presente** - Crea il tuo primo task nella tab 'Crea Task'")
            
            # Esempio di task solo se non ci sono task reali
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
            # Genera ID univoco
            task_id = str(uuid.uuid4())
            
            # Crea oggetto task
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
            
            # Prova prima a salvare nel database
            if self.supabase_manager:
                try:
                    # Inserisci nel database
                    response = self.supabase_manager.supabase.table('tasks').insert(task_data).execute()
                    
                    if response.data:
                        logger.info(f"✅ Task '{title}' salvato nel database con ID {task_id}")
                        
                        # Invia notifica Telegram per nuovo task
                        self._send_task_notification('new_task', task_data)
                        
                        return True, f"✅ Task '{title}' creato e salvato nel database!"
                    else:
                        logger.warning(f"⚠️ Errore salvataggio database per task '{title}', uso sessione temporanea")
                        
                except Exception as db_error:
                    logger.warning(f"⚠️ Database non disponibile per task '{title}': {db_error}")
                    logger.info("💡 Usando salvataggio temporaneo in sessione")
            
            # Fallback: salva nella sessione
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            
            st.session_state.tasks.append(task_data)
            
            logger.info(f"✅ Task '{title}' creato temporaneamente in sessione con ID {task_id}")
            return True, f"✅ Task '{title}' creato! (Salvato temporaneamente - ricarica la pagina per vedere)"
            
        except Exception as e:
            logger.error(f"❌ Errore creazione task: {e}")
            return False, f"❌ Errore nella creazione del task: {e}"
    
    def get_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        """Ottiene la lista dei task"""
        try:
            # Prova prima a recuperare dal database
            if self.supabase_manager:
                try:
                    query = self.supabase_manager.supabase.table('tasks').select('*')
                    
                    # Applica filtri se specificati
                    if status:
                        query = query.eq('status', status)
                    if priority:
                        query = query.eq('priority', priority)
                    
                    response = query.execute()
                    
                    if response.data:
                        logger.info(f"✅ Recuperati {len(response.data)} task dal database")
                        return response.data
                    else:
                        logger.info("📋 Nessun task trovato nel database")
                        
                except Exception as db_error:
                    logger.warning(f"⚠️ Errore recupero task dal database: {db_error}")
                    logger.info("💡 Fallback a sessione temporanea")
            
            # Fallback: usa la sessione
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
                return []
            
            tasks = st.session_state.tasks.copy()
            
            # Applica filtri se specificati
            if status:
                tasks = [task for task in tasks if task['status'] == status]
            
            if priority:
                tasks = [task for task in tasks if task['priority'] == priority]
            
            logger.info(f"📋 Recuperati {len(tasks)} task dalla sessione")
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
                        logger.warning(f"⚠️ Errore aggiornamento database per task {task_id}")
                        
                except Exception as db_error:
                    logger.warning(f"⚠️ Errore aggiornamento database per task {task_id}: {db_error}")
            
            # Fallback: aggiorna nella sessione
            if 'tasks' not in st.session_state:
                return False, "❌ Nessun task trovato"
            
            for task in st.session_state.tasks:
                if task['id'] == task_id:
                    task['status'] = new_status
                    task['updated_at'] = datetime.now().isoformat()
                    
                    if new_status == TaskStatus.COMPLETED.value:
                        task['completed_at'] = datetime.now().isoformat()
                    
                    logger.info(f"✅ Task {task_id} aggiornato a {new_status} in sessione")
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
    
    def _send_task_notification(self, notification_type: str, data: Dict[str, Any]):
        """Invia notifica Telegram per eventi task"""
        try:
            if not self.telegram_manager or not self.telegram_manager.is_configured:
                logger.info("📱 Telegram non configurato, notifica non inviata")
                return
            
            # Controlla se le notifiche task sono abilitate
            if not self._is_notification_enabled('task'):
                logger.info("🔔 Notifiche task disabilitate")
                return
            
            # Invia la notifica
            success, message = self.telegram_manager.send_notification(notification_type, data)
            
            if success:
                logger.info(f"✅ Notifica task '{notification_type}' inviata con successo")
            else:
                logger.warning(f"⚠️ Errore invio notifica task '{notification_type}': {message}")
                
        except Exception as e:
            logger.error(f"❌ Errore invio notifica task '{notification_type}': {e}")
    
    def _is_notification_enabled(self, notification_category: str) -> bool:
        """Controlla se le notifiche per una categoria sono abilitate"""
        try:
            if not self.supabase_manager:
                return True  # Default abilitato se Supabase non disponibile
            
            # Recupera impostazioni notifiche dal database
            response = self.supabase_manager.supabase.table('notification_settings').select('*').eq('notification_type', notification_category).execute()
            
            if response.data and len(response.data) > 0:
                setting = response.data[0]
                return setting.get('is_enabled', True)
            else:
                return True  # Default abilitato se nessuna impostazione trovata
                
        except Exception as e:
            logger.error(f"❌ Errore controllo impostazioni notifiche {notification_category}: {e}")
            return True  # Default abilitato in caso di errore
    
    def check_due_tasks_notifications(self):
        """Controlla task in scadenza e invia notifiche"""
        try:
            if not self.telegram_manager or not self.telegram_manager.is_configured:
                return
            
            # Recupera task in scadenza (nei prossimi 3 giorni)
            tasks = self.get_tasks()
            today = date.today()
            
            for task in tasks:
                if task.get('due_date') and task.get('status') in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]:
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
