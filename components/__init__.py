"""
Components package per Dashboard_Gestione_CPA
"""

# Import dei moduli principali
try:
    from . import auth
    from . import layout
    from . import storage
except ImportError as e:
    print(f"⚠️ Errore import components: {e}")

__all__ = ['auth', 'layout', 'storage']
