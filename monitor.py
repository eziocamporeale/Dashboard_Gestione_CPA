#!/usr/bin/env python3
"""
Sistema di monitoraggio per l'applicazione Dashboard Gestione CPA
"""

import streamlit as st
import psutil
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Import diretti
from utils.logger import log_info, log_error, log_warning
from utils.backup import get_backup_stats

class SystemMonitor:
    """Monitor del sistema"""
    
    def __init__(self):
        """Inizializza il monitor del sistema"""
        self.monitoring = False
        self.metrics_queue = queue.Queue()
        self.metrics_history = []
        self.max_history = 1000  # Numero massimo di metriche da mantenere
        
    def start_monitoring(self, interval=60):
        """Avvia il monitoraggio del sistema"""
        if self.monitoring:
            log_warning("Monitoraggio già attivo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        log_info(f"Monitoraggio sistema avviato (intervallo: {interval}s)")
    
    def stop_monitoring(self):
        """Ferma il monitoraggio del sistema"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        
        log_info("Monitoraggio sistema fermato")
    
    def _monitor_loop(self, interval):
        """Loop principale di monitoraggio"""
        while self.monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_queue.put(metrics)
                self._store_metrics(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                log_error(f"Errore nel loop di monitoraggio: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Raccoglie le metriche del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memoria
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Rete
            network = psutil.net_io_counters()
            
            # Processi
            processes = len(psutil.pids())
            
            # Tempo di sistema
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'freq_mhz': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'percent': memory.percent,
                    'used_gb': memory.used / (1024**3)
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'system': {
                    'processes': processes,
                    'uptime_seconds': uptime,
                    'boot_time': datetime.fromtimestamp(boot_time).isoformat()
                }
            }
            
            return metrics
            
        except Exception as e:
            log_error(f"Errore nella raccolta metriche sistema: {e}")
            return None
    
    def _store_metrics(self, metrics):
        """Salva le metriche nella cronologia"""
        if metrics:
            self.metrics_history.append(metrics)
            
            # Mantieni solo le metriche più recenti
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_current_metrics(self):
        """Restituisce le metriche correnti del sistema"""
        return self._collect_system_metrics()
    
    def get_metrics_history(self, hours=24):
        """Restituisce la cronologia delle metriche"""
        if not self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = []
        for metric in self.metrics_history:
            metric_time = datetime.fromisoformat(metric['timestamp'])
            if metric_time >= cutoff_time:
                filtered_metrics.append(metric)
        
        return filtered_metrics
    
    def get_system_health(self):
        """Valuta la salute del sistema"""
        try:
            metrics = self.get_current_metrics()
            if not metrics:
                return {'status': 'unknown', 'issues': ['Impossibile raccogliere metriche']}
            
            issues = []
            status = 'healthy'
            
            # Controllo CPU
            if metrics['cpu']['percent'] > 80:
                issues.append(f"CPU alta: {metrics['cpu']['percent']}%")
                status = 'warning'
            
            # Controllo memoria
            if metrics['memory']['percent'] > 85:
                issues.append(f"Memoria alta: {metrics['memory']['percent']}%")
                status = 'warning'
            
            # Controllo disco
            if metrics['disk']['percent'] > 90:
                issues.append(f"Disco quasi pieno: {metrics['disk']['percent']:.1f}%")
                status = 'critical'
            
            return {
                'status': status,
                'issues': issues,
                'timestamp': metrics['timestamp']
            }
            
        except Exception as e:
            log_error(f"Errore nella valutazione salute sistema: {e}")
            return {'status': 'error', 'issues': [str(e)]}

class DatabaseMonitor:
    """Monitor del database"""
    
    def __init__(self, db_path="cpa_database.db"):
        """Inizializza il monitor del database"""
        self.db_path = Path(db_path)
        self.monitoring = False
        self.metrics_history = []
        self.max_history = 100
    
    def start_monitoring(self, interval=300):  # 5 minuti
        """Avvia il monitoraggio del database"""
        if self.monitoring:
            log_warning("Monitoraggio database già attivo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        log_info(f"Monitoraggio database avviato (intervallo: {interval}s)")
    
    def stop_monitoring(self):
        """Ferma il monitoraggio del database"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        
        log_info("Monitoraggio database fermato")
    
    def _monitor_loop(self, interval):
        """Loop principale di monitoraggio database"""
        while self.monitoring:
            try:
                metrics = self._collect_database_metrics()
                self._store_metrics(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                log_error(f"Errore nel loop di monitoraggio database: {e}")
                time.sleep(interval)
    
    def _collect_database_metrics(self):
        """Raccoglie le metriche del database"""
        try:
            if not self.db_path.exists():
                return None
            
            # Statistiche file
            stat = self.db_path.stat()
            file_size = stat.st_size
            
            # Connessione al database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conta record nelle tabelle principali
            tables = ['clienti', 'campi_aggiuntivi', 'broker', 'piattaforme']
            table_counts = {}
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except:
                    table_counts[table] = 0
            
            # Statistiche performance
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM clienti")
            query_time = time.time() - start_time
            
            # Controlla integrità
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            conn.close()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'file_size_bytes': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'table_counts': table_counts,
                'total_records': sum(table_counts.values()),
                'query_performance_ms': query_time * 1000,
                'integrity_check': integrity_result,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            return metrics
            
        except Exception as e:
            log_error(f"Errore nella raccolta metriche database: {e}")
            return None
    
    def _store_metrics(self, metrics):
        """Salva le metriche nella cronologia"""
        if metrics:
            self.metrics_history.append(metrics)
            
            # Mantieni solo le metriche più recenti
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_database_health(self):
        """Valuta la salute del database"""
        try:
            metrics = self._collect_database_metrics()
            if not metrics:
                return {'status': 'unknown', 'issues': ['Impossibile raccogliere metriche']}
            
            issues = []
            status = 'healthy'
            
            # Controllo integrità
            if metrics['integrity_check'] != 'ok':
                issues.append(f"Integrità database compromessa: {metrics['integrity_check']}")
                status = 'critical'
            
            # Controllo performance query
            if metrics['query_performance_ms'] > 1000:  # > 1 secondo
                issues.append(f"Query lenta: {metrics['query_performance_ms']:.1f}ms")
                status = 'warning'
            
            # Controllo dimensione file
            if metrics['file_size_mb'] > 100:  # > 100MB
                issues.append(f"Database grande: {metrics['file_size_mb']:.1f}MB")
                status = 'warning'
            
            return {
                'status': status,
                'issues': issues,
                'timestamp': metrics['timestamp']
            }
            
        except Exception as e:
            log_error(f"Errore nella valutazione salute database: {e}")
            return {'status': 'error', 'issues': [str(e)]}
    
    def get_database_stats(self):
        """Restituisce statistiche del database"""
        try:
            metrics = self._collect_database_metrics()
            if not metrics:
                return {}
            
            # Aggiungi statistiche backup
            backup_stats = get_backup_stats(str(self.db_path))
            
            return {
                'database': metrics,
                'backup': backup_stats
            }
            
        except Exception as e:
            log_error(f"Errore nel recupero statistiche database: {e}")
            return {}

class ApplicationMonitor:
    """Monitor dell'applicazione"""
    
    def __init__(self):
        """Inizializza il monitor dell'applicazione"""
        self.system_monitor = SystemMonitor()
        self.database_monitor = DatabaseMonitor()
        self.start_time = datetime.now()
        
    def start_monitoring(self):
        """Avvia tutto il monitoraggio"""
        self.system_monitor.start_monitoring()
        self.database_monitor.start_monitoring()
        
        log_info("Monitoraggio applicazione avviato")
    
    def stop_monitoring(self):
        """Ferma tutto il monitoraggio"""
        self.system_monitor.stop_monitoring()
        self.database_monitor.stop_monitoring()
        
        log_info("Monitoraggio applicazione fermato")
    
    def get_overall_health(self):
        """Restituisce la salute generale dell'applicazione"""
        system_health = self.system_monitor.get_system_health()
        database_health = self.database_monitor.get_database_health()
        
        # Determina lo stato generale
        if system_health['status'] == 'critical' or database_health['status'] == 'critical':
            overall_status = 'critical'
        elif system_health['status'] == 'warning' or database_health['status'] == 'warning':
            overall_status = 'warning'
        elif system_health['status'] == 'healthy' and database_health['status'] == 'healthy':
            overall_status = 'healthy'
        else:
            overall_status = 'unknown'
        
        # Combina tutti gli issue
        all_issues = system_health.get('issues', []) + database_health.get('issues', [])
        
        return {
            'status': overall_status,
            'system': system_health,
            'database': database_health,
            'all_issues': all_issues,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_monitoring_report(self):
        """Genera un report completo di monitoraggio"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'overall_health': self.get_overall_health(),
                'system_metrics': self.system_monitor.get_current_metrics(),
                'database_stats': self.database_monitor.get_database_stats(),
                'system_history': self.system_monitor.get_metrics_history(hours=1),
                'database_history': self.database_monitor.metrics_history[-10:] if self.database_monitor.metrics_history else []
            }
            
            return report
            
        except Exception as e:
            log_error(f"Errore nella generazione report monitoraggio: {e}")
            return {'error': str(e)}
    
    def export_monitoring_data(self, format='json', filepath=None):
        """Esporta i dati di monitoraggio"""
        try:
            report = self.get_monitoring_report()
            
            if format == 'json':
                if not filepath:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filepath = f"monitoring_report_{timestamp}.json"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                log_info(f"Report monitoraggio esportato: {filepath}")
                return True, filepath
            
            else:
                return False, f"Formato non supportato: {format}"
                
        except Exception as e:
            log_error(f"Errore nell'esportazione dati monitoraggio: {e}")
            return False, str(e)

# Istanza globale del monitor
app_monitor = ApplicationMonitor()

# Funzioni di convenienza
def start_monitoring():
    """Avvia il monitoraggio dell'applicazione"""
    app_monitor.start_monitoring()

def stop_monitoring():
    """Ferma il monitoraggio dell'applicazione"""
    app_monitor.stop_monitoring()

def get_health_status():
    """Restituisce lo stato di salute dell'applicazione"""
    return app_monitor.get_overall_health()

def get_monitoring_report():
    """Restituisce un report di monitoraggio"""
    return app_monitor.get_monitoring_report()

def export_monitoring_data(format='json', filepath=None):
    """Esporta i dati di monitoraggio"""
    return app_monitor.export_monitoring_data(format, filepath)
