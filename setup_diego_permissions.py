#!/usr/bin/env python3
"""
🔧 SETUP PERMESSI DIEGO
Script per configurare i permessi di Diego per la gestione wallet
"""

import sys
import os
import logging
from datetime import datetime

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_diego_permissions():
    """Configura i permessi di Diego per la gestione wallet"""
    
    try:
        # Import dei componenti necessari
        from supabase_manager import SupabaseManager
        
        logger.info("🔧 Inizializzazione Supabase...")
        
        # Inizializza Supabase
        supabase_manager = SupabaseManager()
        if not supabase_manager.supabase:
            logger.error("❌ Supabase non configurato")
            return False
        
        logger.info("✅ Supabase inizializzato correttamente")
        
        # Cerca Diego nella tabella users
        logger.info("🔍 Ricerca utente Diego...")
        users_response = supabase_manager.supabase.table('users').select('*').ilike('username', '%diego%').execute()
        
        if not users_response.data:
            logger.error("❌ Utente Diego non trovato")
            logger.info("💡 Creazione utente Diego...")
            
            # Crea utente Diego se non esiste
            diego_data = {
                'username': 'diego',
                'email': 'diego@example.com',
                'full_name': 'Diego',
                'password_hash': 'diego123',  # In produzione, hashare la password
                'role': 'manager',  # Usa 'manager' invece di 'diego'
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = supabase_manager.supabase.table('users').insert(diego_data).execute()
            
            if response.data:
                logger.info("✅ Utente Diego creato con successo")
                diego_id = response.data[0]['id']
            else:
                logger.error("❌ Errore creazione utente Diego")
                return False
        else:
            # Diego esiste già
            diego_user = users_response.data[0]
            diego_id = diego_user['id']
            logger.info(f"✅ Utente Diego trovato (ID: {diego_id})")
            
            # Aggiorna il ruolo di Diego se necessario (usa 'manager' invece di 'diego')
            if diego_user.get('role') not in ['manager', 'admin']:
                logger.info("🔄 Aggiornamento ruolo Diego a 'manager'...")
                update_response = supabase_manager.supabase.table('users').update({
                    'role': 'manager',
                    'updated_at': datetime.now().isoformat()
                }).eq('id', diego_id).execute()
                
                if update_response.data:
                    logger.info("✅ Ruolo Diego aggiornato a 'manager'")
                else:
                    logger.warning("⚠️ Errore aggiornamento ruolo Diego")
        
        # Configura i permessi nella tabella user_roles se esiste
        logger.info("🔧 Configurazione permessi Diego...")
        
        try:
            # Verifica se la tabella user_roles esiste
            roles_response = supabase_manager.supabase.table('user_roles').select('*').eq('role_name', 'diego').execute()
            
            if not roles_response.data:
                # Crea il ruolo Diego con i permessi appropriati
                diego_role_data = {
                    'role_name': 'diego',
                    'description': 'Ruolo per Diego - Gestione transazioni wallet',
                    'permissions': [
                        'wallet:view',
                        'wallet:create', 
                        'wallet:deposit',
                        'wallet:withdrawal'
                    ],
                    'is_active': True,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                role_response = supabase_manager.supabase.table('user_roles').insert(diego_role_data).execute()
                
                if role_response.data:
                    logger.info("✅ Ruolo Diego creato con permessi wallet")
                else:
                    logger.warning("⚠️ Errore creazione ruolo Diego")
            else:
                logger.info("✅ Ruolo Diego già esistente")
                
        except Exception as e:
            logger.warning(f"⚠️ Tabella user_roles non disponibile: {e}")
            logger.info("💡 I permessi saranno gestiti tramite il campo 'role' nella tabella users")
        
        # Configura i permessi nella tabella user_permissions se esiste
        try:
            # Verifica se la tabella user_permissions esiste
            permissions_response = supabase_manager.supabase.table('user_permissions').select('*').eq('permission_name', 'wallet:view').execute()
            
            if permissions_response.data:
                logger.info("🔧 Configurazione permessi specifici Diego...")
                
                # Permessi da assegnare a Diego
                diego_permissions = [
                    'wallet:view',
                    'wallet:create',
                    'wallet:deposit', 
                    'wallet:withdrawal'
                ]
                
                for permission in diego_permissions:
                    # Verifica se il permesso esiste già
                    perm_check = supabase_manager.supabase.table('user_permissions').select('*').eq('permission_name', permission).execute()
                    
                    if not perm_check.data:
                        # Crea il permesso se non esiste
                        perm_data = {
                            'permission_name': permission,
                            'description': f'Permesso {permission}',
                            'resource': permission.split(':')[0],
                            'action': permission.split(':')[1],
                            'is_active': True,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        perm_response = supabase_manager.supabase.table('user_permissions').insert(perm_data).execute()
                        
                        if perm_response.data:
                            logger.info(f"✅ Permesso {permission} creato")
                        else:
                            logger.warning(f"⚠️ Errore creazione permesso {permission}")
                    else:
                        logger.info(f"✅ Permesso {permission} già esistente")
                        
        except Exception as e:
            logger.warning(f"⚠️ Tabella user_permissions non disponibile: {e}")
        
        # Test finale: verifica che Diego possa accedere
        logger.info("🧪 Test accesso Diego...")
        
        # Simula il controllo dei permessi
        try:
            from utils.wallet_permissions import WalletPermissions
            
            # Test dei permessi Diego
            test_permissions = {
                'view': WalletPermissions.can_view_wallet(),
                'create': WalletPermissions.can_create_transaction(),
                'deposit': WalletPermissions.can_deposit(),
                'withdrawal': WalletPermissions.can_withdrawal(),
                'edit': WalletPermissions.can_edit_transaction(),
                'delete': WalletPermissions.can_delete_transaction(),
                'manage': WalletPermissions.can_manage_wallets()
            }
            
            logger.info("📊 Permessi Diego configurati:")
            for perm, status in test_permissions.items():
                status_icon = "✅" if status else "❌"
                logger.info(f"  {status_icon} {perm}: {status}")
            
        except Exception as e:
            logger.warning(f"⚠️ Test permessi non riuscito: {e}")
        
        logger.info("✅ Configurazione permessi Diego completata!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore durante la configurazione: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_diego_info():
    """Mostra informazioni su Diego e i suoi permessi"""
    print("\n" + "="*80)
    print("👤 INFORMAZIONI DIEGO")
    print("="*80)
    print("🔑 Username: diego")
    print("📧 Email: diego@example.com")
    print("👨‍💼 Nome: Diego")
    print("🎭 Ruolo: manager")
    print("")
    print("💰 PERMESSI WALLET:")
    print("✅ Visualizzare transazioni e saldi")
    print("✅ Creare nuove transazioni")
    print("✅ Eseguire depositi da team a cliente")
    print("✅ Eseguire prelievi da cliente a team")
    print("❌ Modificare transazioni esistenti")
    print("❌ Eliminare transazioni")
    print("❌ Gestire wallet e configurazioni")
    print("")
    print("💡 Diego può accedere alla sezione Wallet e utilizzare:")
    print("   • Depositi Team → Cliente")
    print("   • Prelievi Cliente → Team") 
    print("   • Visualizzazione Transazioni")
    print("   • Visualizzazione Saldi Wallet")
    print("="*80)

if __name__ == "__main__":
    print("🔧 SETUP PERMESSI DIEGO")
    print("="*80)
    
    success = setup_diego_permissions()
    
    if success:
        show_diego_info()
        print("\n✅ Setup completato con successo!")
    else:
        print("\n❌ Setup fallito!")
