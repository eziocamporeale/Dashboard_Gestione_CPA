import streamlit as st
import streamlit_authenticator as stauth
import yaml
from pathlib import Path
import hashlib
import secrets
import logging

# Configura il logger
logger = logging.getLogger(__name__)

class SimpleAuthSystem:
    """Sistema di autenticazione semplice e funzionante come Dash Finanze"""
    
    def __init__(self):
        self.config_path = Path("auth_config.yaml")
        self.load_config()
    
    def load_config(self):
        """Carica la configurazione degli utenti"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as file:
                self.config = yaml.load(file, Loader=yaml.SafeLoader)
        else:
            self.config = self.create_default_config()
            self.save_config()
    
    def save_config(self):
        """Salva la configurazione degli utenti"""
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)
    
    def create_default_config(self):
        """Crea configurazione di default con utente admin"""
        return {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@cpadashboard.com',
                        'name': 'Amministratore CPA Dashboard',
                        'password': stauth.Hasher(['admin123']).generate()[0]
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': secrets.token_hex(16),
                'name': 'cpa_dashboard_cookie'
            }
        }
    
    def hash_password(self, password):
        """Genera hash della password"""
        return stauth.Hasher([password]).generate()[0]
    
    def create_user(self, username, email, password, name):
        """Crea un nuovo utente nella configurazione"""
        try:
            # Verifica se l'utente esiste già
            if username in self.config['credentials']['usernames']:
                return False, "Username già esistente"
            
            # Crea utente nella configurazione
            hashed_password = self.hash_password(password)
            self.config['credentials']['usernames'][username] = {
                'email': email,
                'name': name,
                'password': hashed_password
            }
            self.save_config()
            
            return True, "Utente creato con successo"
                
        except Exception as e:
            return False, f"Errore nella creazione utente: {str(e)}"
    
    def authenticate(self):
        """Autentica l'utente e restituisce l'oggetto authenticator"""
        authenticator = stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'],
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days']
        )
        return authenticator

# Istanza globale del sistema di autenticazione
auth_system = SimpleAuthSystem()

# Funzioni di interfaccia per compatibilità
def init_auth():
    """Inizializza il sistema di autenticazione"""
    global auth_system
    auth_system = SimpleAuthSystem()
    logger.info("✅ Sistema di autenticazione semplice inizializzato")

def login_form():
    """Mostra il form di login e gestisce l'autenticazione - SEMPLICE COME DASH FINANZE"""
    try:
        if not auth_system.config:
            st.error("❌ Configurazione autenticazione non disponibile")
            return False
        
        # Crea l'authenticator
        authenticator = auth_system.authenticate()
        
        # Mostra il form di login - SEMPLICE COME DASH FINANZE
        name, authentication_status, username = authenticator.login('main', key='Login')
        
        # Gestisci il risultato del login
        if authentication_status:
            # Login riuscito
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.name = name
            st.session_state.roles = 'admin' if username == 'admin' else 'user'
            
            logger.info(f"✅ Login riuscito per utente: {username}")
            st.success(f'✅ Benvenuto {name}!')
            
            # Riavvia l'app per mostrare la dashboard
            st.rerun()
            return True
            
        elif authentication_status is False:
            st.error('❌ Username o password non corretti')
            return False
            
        # Se authentication_status è None, il form non è stato ancora inviato
        return False
        
    except Exception as e:
        logger.error(f"❌ Errore nel form di login: {e}")
        st.error(f"❌ Errore sistema di autenticazione: {e}")
        return False

def show_user_info():
    """Mostra informazioni sull'utente corrente"""
    if st.session_state.get('authenticated', False):
        username = st.session_state.get('username', 'N/A')
        name = st.session_state.get('name', 'N/A')
        role = st.session_state.get('roles', 'user')
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 **Informazioni Utente**")
        st.sidebar.info(f"**Username:** {username}")
        st.sidebar.info(f"**Nome:** {name}")
        st.sidebar.info(f"**Ruolo:** {role.title()}")
        
        if st.sidebar.button("🚪 **Logout**"):
            logout_user()

def logout_user():
    """Funzione semplice per il logout"""
    try:
        username = st.session_state.get('username', 'Unknown')
        logger.info(f"🔧 Logout richiesto per utente: {username}")
        
        # Pulisci la sessione
        keys_to_remove = ['authenticated', 'username', 'name', 'roles']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.info(f"✅ Logout completato per {username}")
        st.success(f"✅ Logout completato! Arrivederci {username}!")
        st.rerun()
        
    except Exception as e:
        logger.error(f"❌ Errore durante logout: {e}")
        st.error("❌ Errore durante il logout")

def require_auth():
    """Richiede autenticazione per accedere alla pagina"""
    if not st.session_state.get('authenticated', False):
        st.error("❌ Accesso non autorizzato. Effettua il login.")
        st.stop()

def get_current_user():
    """Ottiene l'utente corrente"""
    return st.session_state.get('username', None)

def get_current_role():
    """Ottiene il ruolo dell'utente corrente"""
    return st.session_state.get('roles', 'user')

def has_permission(permission: str) -> bool:
    """Verifica se l'utente ha una determinata permission"""
    role = get_current_role()
    
    if role == 'admin':
        return True  # Admin ha tutti i permessi
    
    # Altre logiche per altri ruoli
    return False
