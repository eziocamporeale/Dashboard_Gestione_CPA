import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from utils.translations import t

class Charts:
    def __init__(self):
        """Inizializza il componente per i grafici"""
        pass
    
    def render_dashboard_charts(self, df_clienti):
        """Rende i grafici per la dashboard principale"""
        
        if df_clienti.empty:
            st.info(t("charts.dashboard.no_data", "Nessun dato disponibile per i grafici"))
            return
        
        # Grafici
        st.subheader(t("charts.dashboard.title", "📈 Grafici Analitici"))
        
        # Grafico 1: Distribuzione per Broker
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.write(f"**{t('charts.dashboard.broker_distribution.title', 'Distribuzione Clienti per Broker')}**")
            broker_counts = df_clienti['broker'].value_counts()
            
            fig_broker = px.pie(
                values=broker_counts.values,
                names=broker_counts.index,
                title=t("charts.dashboard.broker_distribution.chart_title", "Clienti per Broker"),
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_broker.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_broker, width='stretch')
        
        with col_chart2:
            st.write(f"**{t('charts.dashboard.platform_distribution.title', 'Distribuzione per Piattaforma')}**")
            piattaforma_counts = df_clienti['piattaforma'].value_counts()
            
            fig_piattaforma = px.bar(
                x=piattaforma_counts.index,
                y=piattaforma_counts.values,
                title=t("charts.dashboard.platform_distribution.chart_title", "Clienti per Piattaforma"),
                color=piattaforma_counts.values,
                color_continuous_scale='viridis'
            )
            fig_piattaforma.update_layout(
                xaxis_title=t("charts.dashboard.platform_distribution.x_axis", "Piattaforma"), 
                yaxis_title=t("charts.dashboard.platform_distribution.y_axis", "Numero Clienti")
            )
            st.plotly_chart(fig_piattaforma, width='stretch')
        
        # Grafico 2: Depositi per Broker
        st.write(f"**{t('charts.dashboard.deposits_by_broker.title', 'Depositi Totali per Broker')}**")
        depositi_broker = df_clienti.groupby('broker')['deposito'].sum().sort_values(ascending=False)
        
        fig_depositi = px.bar(
            x=depositi_broker.index,
            y=depositi_broker.values,
            title=t("charts.dashboard.deposits_by_broker.chart_title", "Depositi Totali per Broker"),
            color=depositi_broker.values,
            color_continuous_scale='plasma'
        )
        fig_depositi.update_layout(
            xaxis_title=t("charts.dashboard.deposits_by_broker.x_axis", "Broker"),
            yaxis_title=t("charts.dashboard.deposits_by_broker.y_axis", "Depositi Totali (€)"),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_depositi, width='stretch')
        
        # Grafico 3: Trend temporale
        st.write(f"**{t('charts.dashboard.registration_trend.title', 'Trend Registrazioni nel Tempo')}**")
        
        # Converti la colonna data_registrazione in datetime se non lo è già
        if 'data_registrazione' in df_clienti.columns:
            df_clienti['data_registrazione'] = pd.to_datetime(df_clienti['data_registrazione'])
            
            # Raggruppa per mese (evita warning timezone)
            df_clienti['mese'] = df_clienti['data_registrazione'].dt.strftime('%Y-%m')
            registrazioni_mensili = df_clienti.groupby('mese').size().reset_index(name='count')
            
            # Crea grafico con dati puliti
            if not registrazioni_mensili.empty:
                fig_trend = px.line(
                    data_frame=registrazioni_mensili,
                    x='mese',
                    y='count',
                    title=t("charts.dashboard.registration_trend.chart_title", "Registrazioni Mensili"),
                    markers=True
                )
                fig_trend.update_layout(
                    xaxis_title=t("charts.dashboard.registration_trend.x_axis", "Mese"),
                    yaxis_title=t("charts.dashboard.registration_trend.y_axis", "Numero Registrazioni"),
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_trend, width='stretch')
            else:
                st.info(t("charts.dashboard.registration_trend.no_data", "Nessun dato di registrazione disponibile per il grafico"))
    
    def render_summary_charts(self, df_clienti):
        """Rende i grafici per la sezione riepilogo"""
        
        if df_clienti.empty:
            st.info(t("charts.summary.no_data", "Nessun dato disponibile per i grafici"))
            return
        
        # Tabella riassuntiva
        st.subheader(t("charts.summary.title", "📋 Riepilogo Dati"))
        
        # Statistiche per broker - gestisci valori None
        if 'deposito' in df_clienti.columns:
            # Filtra solo i clienti con deposito valido per le statistiche
            df_depositi_validi_stats = df_clienti[df_clienti['deposito'].notna() & (df_clienti['deposito'] > 0)]
            
            if not df_depositi_validi_stats.empty:
                stats_broker = df_depositi_validi_stats.groupby('broker').agg({
                    'id': 'count',
                    'deposito': ['sum', 'mean', 'min', 'max']
                }).round(2)
                
                stats_broker.columns = ['Numero Clienti', 'Depositi Totali', 'Deposito Medio', 'Deposito Min', 'Deposito Max']
                stats_broker = stats_broker.sort_values('Numero Clienti', ascending=False)
                
                st.write(f"**{t('charts.summary.broker_stats.title', 'Statistiche per Broker (solo clienti con deposito):')}**")
                st.dataframe(stats_broker, width='stretch')
            else:
                st.info(t("charts.summary.broker_stats.no_valid_deposits", "Nessun cliente con deposito valido per le statistiche"))
        else:
            st.info(t("charts.summary.broker_stats.deposit_column_missing", "Colonna 'deposito' non disponibile per le statistiche"))
        
        # Grafico a torta per i depositi - gestisci valori None
        if 'deposito' in df_clienti.columns:
            # Filtra solo i clienti con deposito valido
            df_depositi_validi_pie = df_clienti[df_clienti['deposito'].notna() & (df_clienti['deposito'] > 0)]
            
            if not df_depositi_validi_pie.empty:
                depositi_broker = df_depositi_validi_pie.groupby('broker')['deposito'].sum()
                
                fig_depositi_pie = px.pie(
                    values=depositi_broker.values,
                    names=depositi_broker.index,
                    title="Distribuzione Depositi per Broker (solo clienti con deposito)",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_depositi_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_depositi_pie, width='stretch')
            else:
                st.info("Nessun cliente con deposito valido per il grafico a torta")
        else:
            st.info("Colonna 'deposito' non disponibile per il grafico a torta")
        
        # Grafico a barre per piattaforme
        st.write("**Distribuzione per Piattaforma e Broker**")
        
        piattaforma_broker = df_clienti.groupby(['piattaforma', 'broker']).size().unstack(fill_value=0)
        
        fig_piattaforma_broker = px.bar(
            piattaforma_broker,
            title="Clienti per Piattaforma e Broker",
            barmode='group'
        )
        fig_piattaforma_broker.update_layout(
            xaxis_title="Piattaforma",
            yaxis_title="Numero Clienti",
            legend_title="Broker"
        )
        st.plotly_chart(fig_piattaforma_broker, width='stretch')
        
        # Grafico per range di depositi
        st.write("**Distribuzione per Range di Depositi**")
        
        # Crea range di depositi - gestisci valori None
        if 'deposito' in df_clienti.columns:
            # Filtra solo i clienti con deposito valido (non None e > 0)
            df_depositi_validi = df_clienti[df_clienti['deposito'].notna() & (df_clienti['deposito'] > 0)].copy()
            
            if not df_depositi_validi.empty:
                df_depositi_validi['range_deposito'] = pd.cut(
                    df_depositi_validi['deposito'],
                    bins=[0, 1000, 5000, 10000, 50000, float('inf')],
                    labels=['0-1K', '1K-5K', '5K-10K', '10K-50K', '50K+']
                )
                
                range_depositi = df_depositi_validi['range_deposito'].value_counts().sort_index()
                
                fig_range = px.bar(
                    x=range_depositi.index,
                    y=range_depositi.values,
                    title="Distribuzione per Range di Depositi",
                    color=range_depositi.values,
                    color_continuous_scale='viridis'
                )
                fig_range.update_layout(
                    xaxis_title="Range Depositi (€)",
                    yaxis_title="Numero Clienti"
                )
                st.plotly_chart(fig_range, width='stretch')
            else:
                st.info("Nessun cliente con deposito valido per il grafico dei range")
        else:
            st.info("Colonna 'deposito' non disponibile per il grafico dei range")
        
        # Grafico per VPS
        st.write("**Utilizzo VPS**")
        
        vps_stats = {
            'Con VPS': len(df_clienti[df_clienti['vps_ip'].notna() & (df_clienti['vps_ip'] != '')]),
            'Senza VPS': len(df_clienti[df_clienti['vps_ip'].isna() | (df_clienti['vps_ip'] == '')])
        }
        
        fig_vps = px.pie(
            values=list(vps_stats.values()),
            names=list(vps_stats.keys()),
            title="Utilizzo VPS",
            color_discrete_sequence=['#00ff00', '#ff0000']
        )
        fig_vps.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_vps, width='stretch')
    
    def render_export_options(self, df_clienti):
        """Rende le opzioni di esportazione"""
        
        st.subheader("📤 Opzioni di Esportazione")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            if st.button("📊 Esporta Tutti i Dati"):
                csv_all = df_clienti.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica CSV Completo",
                    data=csv_all,
                    file_name=f"clienti_cpa_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_exp2:
            if st.button("📈 Esporta Statistiche"):
                # Crea un dataframe con le statistiche - gestisci valori None
                if 'deposito' in df_clienti.columns:
                    depositi_totali = df_clienti['deposito'].sum() if df_clienti['deposito'].notna().any() else 0
                    cpa_attive = len(df_clienti[df_clienti['deposito'].notna() & (df_clienti['deposito'] > 0)])
                else:
                    depositi_totali = 0
                    cpa_attive = 0
                
                stats_df = pd.DataFrame({
                    'Metrica': ['Totale Clienti', 'Broker Attivi', 'Depositi Totali', 'CPA Attive'],
                    'Valore': [
                        len(df_clienti),
                        df_clienti['broker'].nunique(),
                        f"€{depositi_totali:,.2f}",
                        cpa_attive
                    ]
                })
                
                csv_stats = stats_df.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica Statistiche",
                    data=csv_stats,
                    file_name=f"statistiche_cpa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_exp3:
            if st.button("🔍 Esporta per Broker"):
                # Raggruppa per broker - gestisci valori None
                if 'deposito' in df_clienti.columns:
                    # Filtra solo i clienti con deposito valido
                    df_depositi_validi_export = df_clienti[df_clienti['deposito'].notna() & (df_clienti['deposito'] > 0)]
                    
                    if not df_depositi_validi_export.empty:
                        broker_stats = df_depositi_validi_export.groupby('broker').agg({
                            'id': 'count',
                            'deposito': ['sum', 'mean']
                        }).round(2)
                        
                        broker_stats.columns = ['Numero Clienti', 'Depositi Totali', 'Deposito Medio']
                        broker_stats = broker_stats.reset_index()
                    else:
                        broker_stats = pd.DataFrame(columns=['Broker', 'Numero Clienti', 'Depositi Totali', 'Deposito Medio'])
                else:
                    broker_stats = pd.DataFrame(columns=['Broker', 'Numero Clienti', 'Depositi Totali', 'Deposito Medio'])
                
                csv_broker = broker_stats.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica per Broker",
                    data=csv_broker,
                    file_name=f"statistiche_broker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
