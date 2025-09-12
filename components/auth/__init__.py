"""
Sistema di Autenticazione per Dashboard_Gestione_CPA
"""

from .auth_simple import (
    require_auth,
    get_current_user,
    render_login_form,
    render_logout_section,
    SimpleAuthSystem
)

__all__ = [
    'require_auth',
    'get_current_user', 
    'render_login_form',
    'render_logout_section',
    'SimpleAuthSystem'
]
