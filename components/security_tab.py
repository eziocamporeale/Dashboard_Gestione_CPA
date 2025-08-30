#!/usr/bin/env python3
"""
🔒 Security Tab Component per Dashboard CPA
Gestisce audit di sicurezza automatico e manuale
"""

import streamlit as st
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
import time

# Aggiungi utils al path
sys.path.append(str(Path(__file__).parent.parent / 'utils'))

try:
    from security_audit import SecurityAuditor
    SECURITY_AUDITOR_AVAILABLE = True
except ImportError:
    SECURITY_AUDITOR_AVAILABLE = False
    st.warning("⚠️ Security Auditor non disponibile. Installa le dipendenze necessarie.")

class SecurityTab:
    """Tab per la gestione della sicurezza del progetto"""
    
    def __init__(self):
        self.auditor = None
        self.last_audit = None
        
        # Inizializza session state se non esiste
        if 'audit_schedule_days' not in st.session_state:
            st.session_state.audit_schedule_days = 7  # Default: audit ogni 7 giorni
        
        # Inizializza auditor se disponibile
        if SECURITY_AUDITOR_AVAILABLE:
            try:
                self.auditor = SecurityAuditor()
                st.session_state.security_auditor_ready = True
            except Exception as e:
                st.error(f"❌ Errore inizializzazione Security Auditor: {e}")
                st.session_state.security_auditor_ready = False
        else:
            st.session_state.security_auditor_ready = False
    
    def render(self):
        """Rende il tab completo della sicurezza"""
        st.header("🔒 Sicurezza Progetto")
        st.info("🛡️ **MONITORAGGIO CONTINUO**: Controlla automaticamente la sicurezza del progetto")
        
        # Tab per organizzare le funzionalità
        tab_audit, tab_schedule, tab_history, tab_settings = st.tabs([
            "🔍 Audit Sicurezza", "⏰ Pianificazione", "📋 Cronologia", "⚙️ Impostazioni"
        ])
        
        # TAB 1: Audit Sicurezza
        with tab_audit:
            self._render_audit_tab()
        
        # TAB 2: Pianificazione
        with tab_schedule:
            self._render_schedule_tab()
        
        # TAB 3: Cronologia
        with tab_history:
            self._render_history_tab()
        
        # TAB 4: Impostazioni
        with tab_settings:
            self._render_settings_tab()
    
    def _render_audit_tab(self):
        """Rende il tab per l'audit di sicurezza"""
        st.subheader("🔍 Audit di Sicurezza")
        
        if not st.session_state.get('security_auditor_ready', False):
            st.error("❌ Security Auditor non disponibile")
            st.info("💡 Installa le dipendenze: `pip install gitpython`")
            return
        
        # Controllo automatico se necessario
        self._check_automatic_audit()
        
        # Pulsanti per audit manuale
        col_audit1, col_audit2, col_audit3 = st.columns(3)
        
        with col_audit1:
            if st.button("🔍 Audit Completo", type="primary", help="Esegue un audit completo di sicurezza"):
                self._run_full_audit()
        
        with col_audit2:
            if st.button("⚡ Audit Rapido", help="Esegue un audit rapido (solo controlli critici)"):
                self._run_quick_audit()
        
        with col_audit3:
            if st.button("🔄 Ricarica", help="Ricarica i risultati dell'ultimo audit"):
                st.rerun()
        
        # Mostra risultati audit
        self._display_audit_results()
    
    def _render_schedule_tab(self):
        """Rende il tab per la pianificazione degli audit"""
        st.subheader("⏰ Pianificazione Audit Automatici")
        
        # Configurazione intervallo audit
        st.write("**📅 Frequenza Audit Automatici:**")
        
        col_sched1, col_sched2 = st.columns([2, 1])
        
        with col_sched1:
            new_schedule = st.selectbox(
                "Intervallo tra audit:",
                options=[1, 3, 7, 14, 30],
                index=2,  # Default: 7 giorni
                format_func=lambda x: f"Ogni {x} {'giorno' if x == 1 else 'giorni'}",
                key="audit_schedule_select"
            )
        
        with col_sched2:
            if st.button("💾 Salva Pianificazione"):
                self.audit_schedule_days = new_schedule
                st.session_state.audit_schedule_days = new_schedule
                st.success(f"✅ Audit programmati ogni {new_schedule} {'giorno' if new_schedule == 1 else 'giorni'}")
                st.rerun()
        
        # Stato audit automatici
        st.markdown("---")
        st.subheader("📊 Stato Audit Automatici")
        
        if 'last_audit_date' in st.session_state:
            last_audit = st.session_state.last_audit_date
            days_since = (datetime.now() - last_audit).days
            next_audit = last_audit + timedelta(days=st.session_state.audit_schedule_days)
            
            col_status1, col_status2, col_status3 = st.columns(3)
            
            with col_status1:
                st.metric("🕒 Ultimo Audit", last_audit.strftime('%d/%m/%Y'))
            
            with col_status2:
                st.metric("📅 Prossimo Audit", next_audit.strftime('%d/%m/%Y'))
            
            with col_status3:
                if days_since >= self.audit_schedule_days:
                    st.metric("⚠️ Stato", "Audit Scaduto", delta=f"+{days_since - self.audit_schedule_days} giorni")
                else:
                    st.metric("✅ Stato", "In Regola", delta=f"-{self.audit_schedule_days - days_since} giorni")
            
            # Barra progresso
            progress = min(1.0, days_since / self.audit_schedule_days)
            st.progress(progress)
            
            if progress >= 1.0:
                st.warning("⚠️ **AUDIT SCADUTO!** Esegui un nuovo audit per mantenere la sicurezza aggiornata.")
                if st.button("🔍 Esegui Audit Ora", type="secondary"):
                    self._run_full_audit()
        else:
            st.info("ℹ️ Nessun audit eseguito. Esegui il primo audit per iniziare il monitoraggio.")
    
    def _render_history_tab(self):
        """Rende il tab per la cronologia degli audit"""
        st.subheader("📋 Cronologia Audit")
        
        # Carica cronologia audit
        audit_history = self._load_audit_history()
        
        if not audit_history:
            st.info("ℹ️ Nessun audit nella cronologia.")
            return
        
        # Filtri per cronologia
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_score = st.selectbox(
                "Filtra per punteggio:",
                options=["Tutti", "90-100", "70-89", "0-69"],
                key="filter_score"
            )
        
        with col_filter2:
            filter_days = st.selectbox(
                "Filtra per periodo:",
                options=["Tutti", "Ultimi 7 giorni", "Ultimi 30 giorni", "Ultimi 90 giorni"],
                key="filter_days"
            )
        
        # Applica filtri
        filtered_history = self._apply_history_filters(audit_history, filter_score, filter_days)
        
        # Mostra cronologia filtrata
        if filtered_history:
            st.write(f"**📊 Audit trovati:** {len(filtered_history)}")
            
            for audit in filtered_history:
                with st.expander(f"🔒 {audit['timestamp']} - Punteggio: {audit['score']}/100"):
                    self._display_audit_summary(audit)
        else:
            st.info("ℹ️ Nessun audit corrisponde ai filtri selezionati.")
    
    def _render_settings_tab(self):
        """Rende il tab per le impostazioni di sicurezza"""
        st.subheader("⚙️ Impostazioni Sicurezza")
        
        # Configurazioni generali
        st.write("**🔧 Configurazioni Generali:**")
        
        # Notifiche
        enable_notifications = st.checkbox(
            "🔔 Abilita notifiche per audit scaduti",
            value=st.session_state.get('security_notifications', True),
            key="security_notifications"
        )
        
        # Salvataggio automatico report
        auto_save_reports = st.checkbox(
            "💾 Salva automaticamente i report di sicurezza",
            value=st.session_state.get('auto_save_reports', True),
            key="auto_save_reports"
        )
        
        # Livello di dettaglio audit
        audit_detail_level = st.selectbox(
            "📊 Livello di dettaglio audit:",
            options=["Base", "Standard", "Dettagliato"],
            index=1,
            key="audit_detail_level"
        )
        
        # Salva impostazioni
        if st.button("💾 Salva Impostazioni"):
            st.session_state.security_notifications = enable_notifications
            st.session_state.auto_save_reports = auto_save_reports
            st.session_state.audit_detail_level = audit_detail_level
            st.success("✅ Impostazioni salvate!")
        
        # Informazioni sistema
        st.markdown("---")
        st.subheader("ℹ️ Informazioni Sistema")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.write("**🔒 Sicurezza:**")
            st.write(f"• Security Auditor: {'✅ Disponibile' if SECURITY_AUDITOR_AVAILABLE else '❌ Non disponibile'}")
            st.write(f"• Repository Git: {'✅ Inizializzato' if self.auditor and self.auditor.repo else '❌ Non disponibile'}")
            st.write(f"• Notifiche: {'✅ Abilitate' if st.session_state.get('security_notifications', True) else '❌ Disabilitate'}")
        
        with col_info2:
            st.write("**📁 File di Sistema:**")
            st.write(f"• .gitignore: {'✅ Presente' if Path('.gitignore').exists() else '❌ Mancante'}")
            st.write(f"• .streamlit/: {'✅ Presente' if Path('.streamlit').exists() else '❌ Mancante'}")
            st.write(f"• secrets.toml: {'✅ Presente' if Path('.streamlit/secrets.toml').exists() else '❌ Mancante'}")
    
    def _check_automatic_audit(self):
        """Controlla se è necessario eseguire un audit automatico"""
        if not st.session_state.get('last_audit_date'):
            return
        
        last_audit = st.session_state.last_audit_date
        days_since = (datetime.now() - last_audit).days
        
        if days_since >= st.session_state.audit_schedule_days:
            st.warning(f"⚠️ **AUDIT AUTOMATICO SCADUTO!** Ultimo audit: {days_since} giorni fa")
            
            if st.button("🔍 Esegui Audit Automatico", type="secondary"):
                self._run_full_audit()
    
    def _run_full_audit(self):
        """Esegue un audit completo"""
        if not self.auditor:
            st.error("❌ Security Auditor non disponibile")
            return
        
        with st.spinner("🔍 Esecuzione audit completo..."):
            try:
                report = self.auditor.run_full_audit()
                
                # Salva risultati
                st.session_state.last_audit_report = report
                st.session_state.last_audit_date = datetime.now()
                st.session_state.last_audit_type = "Completo"
                
                # Salva in cronologia
                self._save_audit_to_history(report)
                
                st.success("✅ Audit completo completato!")
                
                # Salva report se abilitato
                if st.session_state.get('auto_save_reports', True):
                    report_file = self.auditor.save_report()
                    if report_file:
                        st.info(f"📁 Report salvato in: {report_file}")
                
            except Exception as e:
                st.error(f"❌ Errore durante audit: {e}")
    
    def _run_quick_audit(self):
        """Esegue un audit rapido"""
        if not self.auditor:
            st.error("❌ Security Auditor non disponibile")
            return
        
        with st.spinner("⚡ Esecuzione audit rapido..."):
            try:
                report = self.auditor.run_quick_audit()
                
                # Salva risultati
                st.session_state.last_audit_report = report
                st.session_state.last_audit_date = datetime.now()
                st.session_state.last_audit_type = "Rapido"
                
                # Salva in cronologia
                self._save_audit_to_history(report)
                
                st.success("✅ Audit rapido completato!")
                
            except Exception as e:
                st.error(f"❌ Errore durante audit: {e}")
    
    def _display_audit_results(self):
        """Mostra i risultati dell'ultimo audit"""
        if not st.session_state.get('last_audit_report'):
            st.info("ℹ️ Esegui un audit per vedere i risultati.")
            return
        
        report = st.session_state.last_audit_report
        
        # Header risultati
        col_result1, col_result2, col_result3 = st.columns(3)
        
        with col_result1:
            st.metric("📊 Punteggio", f"{report['overall_score']}/100")
        
        with col_result2:
            st.metric("✅ Controlli", f"{report['checks_passed']}/{report['total_checks']}")
        
        with col_result3:
            st.metric("🚨 Issues", len(report['issues']))
        
        # Barra punteggio
        score_color = "green" if report['overall_score'] >= 90 else "orange" if report['overall_score'] >= 70 else "red"
        st.progress(report['overall_score'] / 100)
        
        # Dettagli risultati
        with st.expander("📋 Dettagli Audit", expanded=True):
            # Raccomandazioni
            if report['recommendations']:
                st.write("**📋 Raccomandazioni:**")
                for rec in report['recommendations']:
                    st.write(f"• {rec}")
            
            # Issues critiche
            if report['issues']:
                st.write("**🚨 Issues Critiche:**")
                for issue in report['issues']:
                    st.error(issue)
            
            # Warnings
            if report['warnings']:
                st.write("**⚠️ Warnings:**")
                for warning in report['warnings']:
                    st.warning(warning)
            
            # Timestamp
            st.write(f"**🕒 Audit eseguito:** {report['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
            st.write(f"**🔍 Tipo audit:** {st.session_state.get('last_audit_type', 'Sconosciuto')}")
    
    def _save_audit_to_history(self, report):
        """Salva l'audit nella cronologia"""
        history_file = Path('security_reports') / 'audit_history.json'
        history_file.parent.mkdir(exist_ok=True)
        
        # Carica cronologia esistente
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Aggiungi nuovo audit
        audit_entry = {
            'timestamp': report['timestamp'].isoformat(),
            'score': report['overall_score'],
            'type': st.session_state.get('last_audit_type', 'Sconosciuto'),
            'issues_count': len(report['issues']),
            'warnings_count': len(report['warnings']),
            'checks_passed': report['checks_passed'],
            'total_checks': report['total_checks']
        }
        
        history.append(audit_entry)
        
        # Mantieni solo ultimi 100 audit
        if len(history) > 100:
            history = history[-100:]
        
        # Salva cronologia
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            st.error(f"❌ Errore salvataggio cronologia: {e}")
    
    def _load_audit_history(self):
        """Carica la cronologia degli audit"""
        history_file = Path('security_reports') / 'audit_history.json'
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Converti timestamp in datetime
            for audit in history:
                audit['timestamp'] = datetime.fromisoformat(audit['timestamp'])
            
            return history
        except Exception as e:
            st.error(f"❌ Errore caricamento cronologia: {e}")
            return []
    
    def _apply_history_filters(self, history, filter_score, filter_days):
        """Applica filtri alla cronologia"""
        filtered = history.copy()
        
        # Filtro punteggio
        if filter_score != "Tutti":
            if filter_score == "90-100":
                filtered = [h for h in filtered if 90 <= h['score'] <= 100]
            elif filter_score == "70-89":
                filtered = [h for h in filtered if 70 <= h['score'] <= 89]
            elif filter_score == "0-69":
                filtered = [h for h in filtered if 0 <= h['score'] <= 69]
        
        # Filtro periodo
        if filter_days != "Tutti":
            now = datetime.now()
            if filter_days == "Ultimi 7 giorni":
                filtered = [h for h in filtered if (now - h['timestamp']).days <= 7]
            elif filter_days == "Ultimi 30 giorni":
                filtered = [h for h in filtered if (now - h['timestamp']).days <= 30]
            elif filter_days == "Ultimi 90 giorni":
                filtered = [h for h in filtered if (now - h['timestamp']).days <= 90]
        
        return filtered
    
    def _display_audit_summary(self, audit):
        """Mostra un riassunto di un audit specifico"""
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        
        with col_sum1:
            st.metric("📊 Punteggio", f"{audit['score']}/100")
        
        with col_sum2:
            st.metric("🚨 Issues", audit['issues_count'])
        
        with col_sum3:
            st.metric("⚠️ Warnings", audit['warnings_count'])
        
        st.write(f"**🔍 Tipo:** {audit['type']}")
        st.write(f"**✅ Controlli:** {audit['checks_passed']}/{audit['total_checks']}")
        st.write(f"**🕒 Eseguito:** {audit['timestamp'].strftime('%d/%m/%Y %H:%M')}")
        
        # Barra punteggio
        score_color = "green" if audit['score'] >= 90 else "orange" if audit['score'] >= 70 else "red"
        st.progress(audit['score'] / 100)
