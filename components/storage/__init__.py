"""
Componente Storage per Dashboard Gestione CPA
Gestione file con permessi differenziati per Admin e utenti
Creato da Ezio Camporeale per Dashboard Gestione CPA
"""

from .storage_manager import StorageManager
from .storage_ui import render_storage_wrapper

__all__ = ['StorageManager', 'render_storage_wrapper']
