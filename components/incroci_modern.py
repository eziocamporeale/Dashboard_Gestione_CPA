#!/usr/bin/env python3
"""
🔄 INCROCI MODERN - Nuova Interfaccia Moderna
Interfaccia completamente rinnovata per la gestione degli incroci CPA
Design moderno, responsive e user-friendly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import time
from utils.translations import t

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncrociModern:
    """Interfaccia moderna per la gestione degli incroci CPA"""
    
    def __init__(self, incroci_manager, database_manager):
        """Inizializza l'interfaccia moderna"""
        self.incroci_manager = incroci_manager
        self.database_manager = database_manager
        
        # Aggiungi SupabaseManager per i clienti
        try:
            from supabase_manager import SupabaseManager
            self.supabase_manager = SupabaseManager()
        except Exception as e:
            st.error(f"❌ Errore inizializzazione SupabaseManager: {e}")
            self.supabase_manager = None
        
        # CSS personalizzato per design moderno
        self._load_custom_css()
    
    def _load_custom_css(self):
        """Carica CSS personalizzato per design moderno"""
        st.markdown("""
        <style>
        /* Design System Moderno */
        :root {
            --primary-color: #2563eb;
            --secondary-color: #059669;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --info-color: #3b82f6;
            --background-color: #f8fafc;
            --card-background: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        /* Header Moderno */
        .modern-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--info-color) 100%);
            color: white;
            padding: 2rem 1rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
        }
        
        .modern-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .modern-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        /* Cards Moderne */
        .modern-card {
            background: var(--card-background);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .modern-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }
        
        .modern-card h3 {
            color: var(--text-primary);
            margin: 0 0 1rem 0;
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        /* Metriche Moderne */
        .metric-card {
            background: var(--card-background);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary-color);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin: 0.5rem 0 0 0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Badges Moderni */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .status-active {
            background-color: #dcfce7;
            color: #166534;
        }
        
        .status-closed {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .status-suspended {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        /* Bottoni Moderni */
        .modern-button {
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
        }
        
        .modern-button:hover {
            background: #1d4ed8;
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }
        
        .modern-button-secondary {
            background: var(--secondary-color);
        }
        
        .modern-button-secondary:hover {
            background: #047857;
        }
        
        /* Form Moderni */
        .form-section {
            background: var(--card-background);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow);
        }
        
        .form-section h4 {
            color: var(--text-primary);
            margin: 0 0 1rem 0;
            font-size: 1.125rem;
            font-weight: 600;
        }
        
        /* Tabs Moderni */
        .modern-tabs {
            background: var(--card-background);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }
        
        /* Animazioni */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .modern-header h1 {
                font-size: 2rem;
            }
            
            .metric-value {
                font-size: 2rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render(self):
        """Rende l'interfaccia moderna completa"""
        # Header moderno
        st.markdown("""
        <div class="modern-header fade-in">
            <h1>🔄 Gestione Incroci CPA</h1>
            <p>Piattaforma moderna per la gestione avanzata degli incroci tra account</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Dashboard principale con metriche real-time
        self._render_dashboard_overview()
        
        # Tabs principali con design moderno
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard", "📋 Incroci", "➕ Nuovo", "📈 Analytics", "⚙️ Impostazioni"
        ])
        
        with tab1:
            self._render_dashboard_tab()
        
        with tab2:
            self._render_incroci_tab()
        
        with tab3:
            self._render_nuovo_incrocio_tab()
        
        with tab4:
            self._render_analytics_tab()
        
        with tab5:
            self._render_impostazioni_tab()
    
    def _render_dashboard_overview(self):
        """Rende l'overview del dashboard con metriche principali"""
        stats = self.incroci_manager.ottieni_statistiche_incroci()
        
        if not stats:
            st.warning("⚠️ Nessuna statistica disponibile")
            return
        
        # Metriche principali in cards moderne
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-value">{stats['generali']['totale_incroci']}</div>
                <div class="metric-label">Totale Incroci</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-value" style="color: var(--success-color);">{stats['generali']['incroci_attivi']}</div>
                <div class="metric-label">Incroci Attivi</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-value" style="color: var(--warning-color);">{stats['generali']['volume_totale']:,.0f}</div>
                <div class="metric-label">Volume Totale</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-value" style="color: var(--info-color);">${stats['bonus']['totale_bonus']:,.0f}</div>
                <div class="metric-label">Bonus Totali</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_dashboard_tab(self):
        """Tab dashboard con grafici e insights"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 📊 Dashboard Real-time")
        
        # Grafici principali
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_pair_distribution_chart()
        
        with col2:
            self._render_broker_usage_chart()
        
        # Timeline degli incroci recenti
        st.markdown("### 📅 Timeline Incroci Recenti")
        self._render_recent_incroci_timeline()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_incroci_tab(self):
        """Tab lista incroci con design moderno"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 📋 Gestione Incroci")
        
        # Gestione chiusura incroci moderna
        if st.session_state.get('incrocio_da_chiudere_modern'):
            incrocio_id = st.session_state.incrocio_da_chiudere_modern
            self._close_incrocio(incrocio_id)
            return
        
        # Filtri moderni
        self._render_modern_filters()
        
        # Lista incroci con cards
        self._render_incroci_cards()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_nuovo_incrocio_tab(self):
        """Tab creazione incrocio con wizard moderno"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("### ➕ Nuovo Incrocio")
        
        # Wizard a step
        self._render_incrocio_wizard()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_analytics_tab(self):
        """Tab analytics avanzate"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 📈 Analytics Avanzate")
        
        # Analytics approfondite
        self._render_advanced_analytics()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_impostazioni_tab(self):
        """Tab impostazioni"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Impostazioni")
        
        # Impostazioni sistema
        self._render_system_settings()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_pair_distribution_chart(self):
        """Grafico distribuzione pair"""
        stats = self.incroci_manager.ottieni_statistiche_incroci()
        
        if not stats or not stats['per_pair']:
            st.info("📊 Nessun dato disponibile per la distribuzione pair")
            return
        
        # Prepara dati per il grafico
        pair_data = pd.DataFrame(stats['per_pair'], columns=['Pair', 'Utilizzi', 'Volume'])
        
        # Grafico a torta moderno
        fig = px.pie(
            pair_data, 
            values='Utilizzi', 
            names='Pair',
            title="Distribuzione Incroci per Pair",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            title_font_size=16,
            font=dict(size=12),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_broker_usage_chart(self):
        """Grafico utilizzo broker"""
        stats = self.incroci_manager.ottieni_statistiche_incroci()
        
        if not stats or not stats['per_broker']:
            st.info("📊 Nessun dato disponibile per l'utilizzo broker")
            return
        
        # Prepara dati per il grafico
        broker_data = pd.DataFrame(stats['per_broker'], columns=['Broker', 'Utilizzi', 'Incroci Unici'])
        
        # Grafico a barre moderno
        fig = px.bar(
            broker_data,
            x='Broker',
            y='Utilizzi',
            title="Utilizzo Broker",
            color='Utilizzi',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            title_font_size=16,
            font=dict(size=12),
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_recent_incroci_timeline(self):
        """Timeline degli incroci recenti"""
        incroci_df = self.incroci_manager.ottieni_incroci()
        
        if incroci_df.empty:
            st.info("📅 Nessun incrocio recente")
            return
        
        # Prendi gli ultimi 5 incroci
        recent_incroci = incroci_df.head(5)
        
        for _, incrocio in recent_incroci.iterrows():
            # Determina il colore del badge in base allo stato
            status_class = f"status-{incrocio['stato']}"
            
            st.markdown(f"""
            <div class="modern-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: var(--text-primary);">{incrocio['nome_incrocio']}</h4>
                        <p style="margin: 0.5rem 0; color: var(--text-secondary);">{incrocio['pair_trading']} • {incrocio['volume_trading']} lotti</p>
                    </div>
                    <span class="status-badge {status_class}">{incrocio['stato']}</span>
                </div>
                <div style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                    📅 {incrocio['data_apertura']} • 💰 ${incrocio.get('totale_bonus', 0):,.0f} bonus
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_modern_filters(self):
        """Filtri moderni per la lista incroci"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            stato_filtro = st.selectbox(
                "🔍 Stato",
                ["Tutti", "Attivi", "Chiusi", "Sospesi"],
                key="modern_stato_filter"
            )
        
        with col2:
            pair_filtro = st.selectbox(
                "📊 Pair",
                ["Tutti", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"],
                key="modern_pair_filter"
            )
        
        with col3:
            broker_filtro = st.selectbox(
                "🏢 Broker",
                ["Tutti", "XM", "IC Markets", "Exness", "FXCM"],
                key="modern_broker_filter"
            )
        
        with col4:
            date_range = st.date_input(
                "📅 Periodo",
                value=(date.today() - timedelta(days=30), date.today()),
                key="modern_date_filter"
            )
    
    def _render_incroci_cards(self):
        """Lista incroci con cards moderne"""
        incroci_df = self.incroci_manager.ottieni_incroci()
        
        if incroci_df.empty:
            st.info("📋 Nessun incrocio trovato")
            return
        
        # Mostra incroci in cards moderne
        for _, incrocio in incroci_df.iterrows():
            status_class = f"status-{incrocio['stato']}"
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary);">{incrocio['nome_incrocio']}</h4>
                            <p style="margin: 0.5rem 0; color: var(--text-secondary);">
                                📊 {incrocio['pair_trading']} • 📈 {incrocio['volume_trading']} lotti
                            </p>
                            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                <div>👤 Long: {incrocio['cliente_long']} ({incrocio['broker_long']})</div>
                                <div>👤 Short: {incrocio['cliente_short']} ({incrocio['broker_short']})</div>
                            </div>
                        </div>
                        <span class="status-badge {status_class}">{incrocio['stato']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️ Dettagli", key=f"dett_{incrocio['id']}"):
                    self._show_incrocio_details(incrocio['id'])
            
            with col3:
                if incrocio['stato'] == 'attivo':
                    if st.button("❌ Chiudi", key=f"chiudi_{incrocio['id']}"):
                        st.session_state.incrocio_da_chiudere_modern = incrocio['id']
                        st.rerun()
    
    def _render_incrocio_wizard(self):
        """Wizard moderno per creazione incrocio"""
        # Step indicator
        steps = ["Info Base", "Account Long", "Account Short", "Bonus & Conferma"]
        current_step = st.session_state.get('wizard_step', 0)
        
        # Progress bar
        progress = (current_step + 1) / len(steps)
        st.progress(progress)
        
        # Step content
        if current_step == 0:
            self._render_wizard_step1()
        elif current_step == 1:
            self._render_wizard_step2()
        elif current_step == 2:
            self._render_wizard_step3()
        elif current_step == 3:
            self._render_wizard_step4()
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_step > 0:
                if st.button("⬅️ Indietro"):
                    st.session_state.wizard_step = current_step - 1
                    st.rerun()
        
        with col3:
            if current_step < len(steps) - 1:
                if st.button("Avanti ➡️"):
                    st.session_state.wizard_step = current_step + 1
                    st.rerun()
            else:
                if st.button("🚀 Crea Incrocio", type="primary"):
                    self._create_incrocio_from_wizard()
    
    def _render_wizard_step1(self):
        """Step 1: Informazioni base"""
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### 📝 Informazioni Base")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_incrocio = st.text_input(
                "Nome Incrocio",
                placeholder="es. Incrocio EURUSD Gennaio 2024",
                key="wizard_nome"
            )
            
            pair_trading = st.selectbox(
                "Pair Trading",
                ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"],
                key="wizard_pair"
            )
        
        with col2:
            volume_trading = st.number_input(
                "Volume Trading (lotti)",
                min_value=0.01,
                value=1.0,
                step=0.01,
                key="wizard_volume"
            )
            
            data_apertura = st.date_input(
                "Data Apertura",
                value=date.today(),
                key="wizard_data"
            )
        
        note = st.text_area(
            "Note",
            placeholder="Note aggiuntive sull'incrocio...",
            key="wizard_note"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_wizard_step2(self):
        """Step 2: Account Long"""
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### 📈 Account Long (Buy)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            account_long_id = st.selectbox(
                "Cliente Long",
                options=self.get_clienti_options(),
                key="wizard_long_cliente"
            )
            
            broker_long = st.text_input(
                "Broker Long",
                key="wizard_long_broker",
                disabled=True
            )
        
        with col2:
            piattaforma_long = st.selectbox(
                "Piattaforma Long",
                ["MT4", "MT5", "cTrader", "Altro"],
                key="wizard_long_piattaforma"
            )
            
            volume_long = st.number_input(
                "Volume Long",
                min_value=0.01,
                value=st.session_state.get('wizard_volume', 1.0),
                step=0.01,
                key="wizard_long_volume"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_wizard_step3(self):
        """Step 3: Account Short"""
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### 📉 Account Short (Sell)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            account_short_id = st.selectbox(
                "Cliente Short",
                options=self.get_clienti_options(),
                key="wizard_short_cliente"
            )
            
            broker_short = st.text_input(
                "Broker Short",
                key="wizard_short_broker",
                disabled=True
            )
        
        with col2:
            piattaforma_short = st.selectbox(
                "Piattaforma Short",
                ["MT4", "MT5", "cTrader", "Altro"],
                key="wizard_short_piattaforma"
            )
            
            volume_short = st.number_input(
                "Volume Short",
                min_value=0.01,
                value=st.session_state.get('wizard_volume', 1.0),
                step=0.01,
                key="wizard_short_volume"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_wizard_step4(self):
        """Step 4: Bonus e conferma"""
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### 💰 Bonus CPA (Opzionale)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_bonus = st.text_input(
                "Tipo Bonus",
                placeholder="es. Welcome Bonus",
                key="wizard_bonus_tipo"
            )
        
        with col2:
            importo_bonus = st.number_input(
                "Importo Bonus",
                min_value=0.01,
                value=100.0,
                step=0.01,
                key="wizard_bonus_importo"
            )
        
        with col3:
            valuta_bonus = st.selectbox(
                "Valuta",
                ["USD", "EUR", "GBP"],
                key="wizard_bonus_valuta"
            )
        
        # Preview dell'incrocio
        st.markdown("#### 👀 Anteprima Incrocio")
        self._render_incrocio_preview()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_incrocio_preview(self):
        """Preview dell'incrocio prima della creazione"""
        st.markdown("""
        <div class="modern-card" style="background: #f8fafc;">
            <h4 style="color: var(--text-primary);">📋 Riepilogo Incrocio</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <strong>📝 Nome:</strong> {nome}<br>
                    <strong>📊 Pair:</strong> {pair}<br>
                    <strong>📈 Volume:</strong> {volume} lotti<br>
                    <strong>📅 Data:</strong> {data}
                </div>
                <div>
                    <strong>👤 Long:</strong> {long_cliente}<br>
                    <strong>👤 Short:</strong> {short_cliente}<br>
                    <strong>💰 Bonus:</strong> {bonus}
                </div>
            </div>
        </div>
        """.format(
            nome=st.session_state.get('wizard_nome', 'N/A'),
            pair=st.session_state.get('wizard_pair', 'N/A'),
            volume=st.session_state.get('wizard_volume', 'N/A'),
            data=st.session_state.get('wizard_data', 'N/A'),
            long_cliente=st.session_state.get('wizard_long_cliente', 'N/A'),
            short_cliente=st.session_state.get('wizard_short_cliente', 'N/A'),
            bonus=f"${st.session_state.get('wizard_bonus_importo', 0):,.0f} {st.session_state.get('wizard_bonus_valuta', 'USD')}"
        ), unsafe_allow_html=True)
    
    def _render_advanced_analytics(self):
        """Analytics avanzate"""
        st.markdown("#### 📊 Analytics Avanzate")
        
        # Grafici avanzati
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📈 Performance nel Tempo")
            # Grafico performance nel tempo
            self._render_performance_timeline()
        
        with col2:
            st.markdown("##### 🎯 Analisi Rischio")
            # Grafico analisi rischio
            self._render_risk_analysis()
        
        # Tabelle dettagliate
        st.markdown("##### 📋 Report Dettagliati")
        self._render_detailed_reports()
    
    def _render_performance_timeline(self):
        """Grafico performance nel tempo"""
        # Placeholder per grafico performance
        st.info("📈 Grafico performance nel tempo in sviluppo")
    
    def _render_risk_analysis(self):
        """Grafico analisi rischio"""
        # Placeholder per analisi rischio
        st.info("🎯 Analisi rischio in sviluppo")
    
    def _render_detailed_reports(self):
        """Report dettagliati"""
        # Placeholder per report dettagliati
        st.info("📋 Report dettagliati in sviluppo")
    
    def _render_system_settings(self):
        """Impostazioni sistema"""
        st.markdown("#### ⚙️ Impostazioni Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔔 Notifiche")
            email_notifications = st.checkbox("Notifiche Email", value=True)
            push_notifications = st.checkbox("Notifiche Push", value=False)
            
            st.markdown("##### 🎨 Aspetto")
            theme = st.selectbox("Tema", ["Chiaro", "Scuro", "Auto"])
            language = st.selectbox("Lingua", ["Italiano", "Inglese", "Spagnolo"])
        
        with col2:
            st.markdown("##### 📊 Dashboard")
            auto_refresh = st.checkbox("Aggiornamento Automatico", value=True)
            refresh_interval = st.selectbox("Intervallo Aggiornamento", ["30s", "1m", "5m", "10m"])
            
            st.markdown("##### 🔒 Sicurezza")
            session_timeout = st.selectbox("Timeout Sessione", ["15m", "30m", "1h", "2h"])
            two_factor = st.checkbox("Autenticazione a Due Fattori", value=False)
        
        if st.button("💾 Salva Impostazioni", type="primary"):
            st.success("✅ Impostazioni salvate!")
    
    def _show_incrocio_details(self, incrocio_id):
        """Mostra dettagli completi di un incrocio"""
        st.info(f"👁️ Dettagli incrocio {incrocio_id} in sviluppo")
    
    def _close_incrocio(self, incrocio_id):
        """Chiude un incrocio con bilanciamento automatico"""
        try:
            from components.incroci_close_manager import IncrociCloseManager
            
            # Usa il nuovo sistema di chiusura
            close_manager = IncrociCloseManager()
            
            # Recupera informazioni incrocio
            incroci = self.incroci_manager.ottieni_incroci()
            incrocio_data = None
            
            for _, incrocio in incroci.iterrows():
                if incrocio['id'] == incrocio_id:
                    incrocio_data = incrocio
                    break
            
            if incrocio_data is None:
                st.error("❌ Incrocio non trovato")
                return
            
            # Mostra informazioni incrocio con design moderno
            st.markdown(f"### 🔄 Chiusura: {incrocio_data['nome_incrocio']}")
            
            # Card moderna per informazioni incrocio
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown("""
                <div class="incrocio-card">
                    <h4>👤 Cliente Long (Buy)</h4>
                    <p><strong>Nome:</strong> {cliente_long}</p>
                    <p><strong>Conto:</strong> {conto_long}</p>
                    <p><strong>Broker:</strong> {broker_long}</p>
                </div>
                """.format(
                    cliente_long=incrocio_data['cliente_long'],
                    conto_long=incrocio_data['conto_long'],
                    broker_long=incrocio_data['broker_long']
                ), unsafe_allow_html=True)
            
            with col_info2:
                st.markdown("""
                <div class="incrocio-card">
                    <h4>👤 Cliente Short (Sell)</h4>
                    <p><strong>Nome:</strong> {cliente_short}</p>
                    <p><strong>Conto:</strong> {conto_short}</p>
                    <p><strong>Broker:</strong> {broker_short}</p>
                </div>
                """.format(
                    cliente_short=incrocio_data['cliente_short'],
                    conto_short=incrocio_data['conto_short'],
                    broker_short=incrocio_data['broker_short']
                ), unsafe_allow_html=True)
            
            # Form chiusura con design moderno
            st.markdown("---")
            st.markdown("### 💰 Inserisci Saldi Attuali")
            
            col_saldi1, col_saldi2 = st.columns(2)
            
            with col_saldi1:
                saldo_long_attuale = st.number_input(
                    "💰 Saldo Cliente Long (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Inserisci il saldo attuale del conto Long",
                    key=f"modern_saldo_long_{incrocio_id}"
                )
            
            with col_saldi2:
                saldo_short_attuale = st.number_input(
                    "💰 Saldo Cliente Short (USDT)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Inserisci il saldo attuale del conto Short",
                    key=f"modern_saldo_short_{incrocio_id}"
                )
            
            st.markdown("---")
            st.markdown("### 🏆 Risultato Incrocio")
            
            vincitore = st.radio(
                "🎯 Chi ha vinto l'incrocio?",
                options=["long", "short"],
                format_func=lambda x: {
                    "long": f"👤 {incrocio_data['cliente_long']} (Long/Buy)",
                    "short": f"👤 {incrocio_data['cliente_short']} (Short/Sell)"
                }[x],
                help="Seleziona chi ha vinto l'incrocio",
                key=f"modern_vincitore_{incrocio_id}"
            )
            
            # Note aggiuntive
            note_chiusura = st.text_area(
                "📝 Note Chiusura",
                placeholder="Note aggiuntive sulla chiusura dell'incrocio...",
                help="Note opzionali per la chiusura",
                key=f"modern_note_chiusura_{incrocio_id}"
            )
            
            # Pulsanti con design moderno
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✅ Chiudi Incrocio", type="primary", key=f"modern_confirm_close_{incrocio_id}"):
                    if saldo_long_attuale > 0 and saldo_short_attuale > 0:
                        # Prepara dati per la chiusura
                        incrocio_dict = {
                            'id': incrocio_id,
                            'nome_incrocio': incrocio_data['nome_incrocio'],
                            'pair_trading': incrocio_data['pair_trading'],
                            'cliente_long': {'id': incrocio_data.get('cliente_long_id', ''), 'nome_cliente': incrocio_data['cliente_long']},
                            'cliente_short': {'id': incrocio_data.get('cliente_short_id', ''), 'nome_cliente': incrocio_data['cliente_short']},
                            'note': incrocio_data.get('note', '')
                        }
                        
                        success, message = close_manager._close_cross(
                            incrocio=incrocio_dict,
                            saldo_long_attuale=saldo_long_attuale,
                            saldo_short_attuale=saldo_short_attuale,
                            vincitore=vincitore,
                            note_chiusura=note_chiusura
                        )
                        
                        if success:
                            st.success(message)
                            st.balloons()
                            st.session_state.incrocio_da_chiudere_modern = None
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("❌ Inserisci saldi validi per entrambi i clienti")
            
            with col_btn2:
                if st.button("❌ Annulla", key=f"modern_cancel_close_{incrocio_id}"):
                    st.session_state.incrocio_da_chiudere_modern = None
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Errore chiusura incrocio: {e}")
            logging.error(f"Errore _close_incrocio modern: {e}")
    
    def _create_incrocio_from_wizard(self):
        """Crea incrocio dal wizard"""
        st.success("🚀 Creazione incrocio dal wizard in sviluppo")
        # Reset wizard
        st.session_state.wizard_step = 0
    
    def get_clienti_options(self) -> List[tuple]:
        """Ottiene la lista dei clienti per i selectbox da Supabase"""
        try:
            if self.supabase_manager:
                clienti = self.supabase_manager.get_clienti()
                if clienti:
                    options = [(f"{cliente['nome_cliente']} ({cliente['broker']})", cliente['id']) for cliente in clienti]
                    return options
                else:
                    return []
            else:
                clienti_df = self.database_manager.ottieni_tutti_clienti()
                if not clienti_df.empty:
                    options = [(f"{row['nome_cliente']} ({row['broker']})", row['id']) for _, row in clienti_df.iterrows()]
                    return options
                else:
                    return []
        except Exception as e:
            st.error(f"❌ Errore nel caricamento clienti: {e}")
            return []




