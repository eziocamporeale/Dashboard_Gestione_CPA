"""
Database package per Dashboard_Gestione_CPA
"""

# Import dei moduli principali
try:
    from .database import DatabaseManager
    from .incroci_manager import IncrociManager
except ImportError as e:
    print(f"⚠️ Errore import database modules: {e}")

__all__ = ['DatabaseManager', 'IncrociManager']
