#!/usr/bin/env python3
"""
🛡️ COMPONENTE GESTIONE PERMESSI - Dashboard Gestione CPA
Interfaccia per gestire utenti, ruoli e permessi del sistema
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.translations import t
from utils.supabase_permissions import supabase_permission_manager, has_role, has_permission

class PermissionsManagement:
    """Componente per la gestione dei permessi del sistema"""
    
    def __init__(self):
        """Inizializza il componente gestione permessi"""
        self.permission_manager = supabase_permission_manager
    
    def render(self):
        """Rende l'interfaccia principale di gestione permessi"""
        if not has_role('admin'):
            st.error(t("permissions.admin_only", "❌ Solo gli amministratori possono accedere alla gestione permessi."))
            return
        
        st.header("🛡️ " + t("permissions.management.title", "Gestione Permessi e Ruoli"))
        st.markdown("---")
        
        # Tab per le diverse sezioni
        tab_users, tab_roles, tab_permissions, tab_audit = st.tabs([
            t("permissions.tabs.users", "👥 Utenti"),
            t("permissions.tabs.roles", "🎭 Ruoli"),
            t("permissions.tabs.permissions", "🔐 Permessi"),
            t("permissions.tabs.audit", "📋 Audit Log")
        ])
        
        with tab_users:
            self.render_users_tab()
        
        with tab_roles:
            self.render_roles_tab()
        
        with tab_permissions:
            self.render_permissions_tab()
        
        with tab_audit:
            self.render_audit_tab()
    
    def render_users_tab(self):
        """Rende la tab per la gestione utenti"""
        st.subheader("👥 " + t("permissions.users.title", "Gestione Utenti Sistema"))
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Lista utenti
            users = self.get_users_with_roles()
            if users:
                df = pd.DataFrame(users)
                st.dataframe(
                    df,
                    column_config={
                        "username": t("permissions.users.username", "Username"),
                        "email": t("permissions.users.email", "Email"),
                        "full_name": t("permissions.users.full_name", "Nome Completo"),
                        "roles": t("permissions.users.roles", "Ruoli"),
                        "is_active": t("permissions.users.active", "Attivo"),
                        "last_login": t("permissions.users.last_login", "Ultimo Accesso")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(t("permissions.users.no_users", "Nessun utente trovato nel sistema."))
        
        with col2:
            # Azioni rapide
            st.subheader("⚡ " + t("permissions.users.quick_actions", "Azioni Rapide"))
            
            if st.button("➕ " + t("permissions.users.add_user", "Aggiungi Utente")):
                self.show_add_user_form()
            
            if st.button("🔍 " + t("permissions.users.view_details", "Dettagli Utente")):
                self.show_user_details()
    
    def render_roles_tab(self):
        """Rende la tab per la gestione ruoli"""
        st.subheader("🎭 " + t("permissions.roles.title", "Gestione Ruoli"))
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Lista ruoli
            roles = self.permission_manager.get_all_roles()
            if roles:
                df = pd.DataFrame(roles)
                st.dataframe(
                    df,
                    column_config={
                        "name": t("permissions.roles.name", "Nome"),
                        "description": t("permissions.roles.description", "Descrizione"),
                        "level": t("permissions.roles.level", "Livello"),
                        "is_system": t("permissions.roles.system", "Sistema"),
                        "created_at": t("permissions.roles.created", "Creato")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(t("permissions.roles.no_roles", "Nessun ruolo trovato nel sistema."))
        
        with col2:
            # Azioni rapide
            st.subheader("⚡ " + t("permissions.roles.quick_actions", "Azioni Rapide"))
            
            if st.button("➕ " + t("permissions.roles.add_role", "Aggiungi Ruolo")):
                self.show_add_role_form()
            
            if st.button("🔍 " + t("permissions.roles.view_permissions", "Permessi Ruolo")):
                self.show_role_permissions()
    
    def render_permissions_tab(self):
        """Rende la tab per la gestione permessi"""
        st.subheader("🔐 " + t("permissions.permissions.title", "Gestione Permessi"))
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Lista permessi
            permissions = self.permission_manager.get_all_permissions()
            if permissions:
                df = pd.DataFrame(permissions)
                st.dataframe(
                    df,
                    column_config={
                        "name": t("permissions.permissions.name", "Nome"),
                        "description": t("permissions.permissions.description", "Descrizione"),
                        "resource": t("permissions.permissions.resource", "Risorsa"),
                        "action": t("permissions.permissions.action", "Azione"),
                        "is_system": t("permissions.permissions.system", "Sistema"),
                        "created_at": t("permissions.permissions.created", "Creato")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(t("permissions.permissions.no_permissions", "Nessun permesso trovato nel sistema."))
        
        with col2:
            # Azioni rapide
            st.subheader("⚡ " + t("permissions.permissions.quick_actions", "Azioni Rapide"))
            
            if st.button("➕ " + t("permissions.permissions.add_permission", "Aggiungi Permesso")):
                self.show_add_permission_form()
            
            if st.button("🔍 " + t("permissions.permissions.view_matrix", "Matrice Permessi")):
                self.show_permissions_matrix()
    
    def render_audit_tab(self):
        """Rende la tab per l'audit log"""
        st.subheader("📋 " + t("permissions.audit.title", "Audit Log Permessi"))
        
        # Filtri
        col1, col2, col3 = st.columns(3)
        with col1:
            action_filter = st.selectbox(
                t("permissions.audit.action_filter", "Filtra per Azione"),
                ["Tutte", "assign_role", "revoke_role", "grant_permission", "revoke_permission"]
            )
        
        with col2:
            limit = st.slider(
                t("permissions.audit.limit", "Numero record"),
                min_value=10,
                max_value=500,
                value=100,
                step=10
            )
        
        with col3:
            if st.button("🔄 " + t("permissions.audit.refresh", "Aggiorna")):
                st.rerun()
        
        # Audit log
        audit_log = self.permission_manager.get_audit_log(limit)
        if audit_log:
            df = pd.DataFrame(audit_log)
            st.dataframe(
                df,
                column_config={
                    "action": t("permissions.audit.action", "Azione"),
                    "details": t("permissions.audit.details", "Dettagli"),
                    "created_at": t("permissions.audit.timestamp", "Timestamp"),
                    "username": t("permissions.audit.user", "Utente"),
                    "target_username": t("permissions.audit.target_user", "Utente Target"),
                    "role_name": t("permissions.audit.role", "Ruolo"),
                    "permission_name": t("permissions.audit.permission", "Permesso")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(t("permissions.audit.no_logs", "Nessun record di audit trovato."))
    
    def get_users_with_roles(self):
        """Ottiene la lista degli utenti con i loro ruoli"""
        try:
            supabase = self.permission_manager._get_supabase()
            if not supabase:
                return []
            
            # Query diretta alla tabella users esistente
            response = supabase.table('users').select('id, username, email, full_name, role, is_active, created_at').execute()
            
            if response.data:
                # Formatta i dati per la visualizzazione
                users = []
                for user in response.data:
                    users.append({
                        'username': user.get('username', ''),
                        'email': user.get('email', ''),
                        'full_name': user.get('full_name', user.get('username', '')),
                        'roles': user.get('role', 'N/A'),
                        'is_active': '✅' if user.get('is_active', True) else '❌',
                        'last_login': user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'
                    })
                return users
            return []
            
        except Exception as e:
            st.error(f"❌ Errore ottenimento utenti: {e}")
            return []
    
    def show_add_user_form(self):
        """Mostra il form per aggiungere un nuovo utente"""
        st.subheader("➕ " + t("permissions.users.add_new", "Aggiungi Nuovo Utente"))
        
        with st.form("add_user_form"):
            username = st.text_input(t("permissions.users.username", "Username"), placeholder="es. mario.rossi")
            email = st.text_input(t("permissions.users.email", "Email"), placeholder="mario.rossi@example.com")
            full_name = st.text_input(t("permissions.users.full_name", "Nome Completo"), placeholder="Mario Rossi")
            password = st.text_input(t("permissions.users.password", "Password"), type="password")
            
            # Selezione ruoli
            roles = self.permission_manager.get_all_roles()
            role_options = {role['name']: role['id'] for role in roles}
            selected_roles = st.multiselect(
                t("permissions.users.select_roles", "Seleziona Ruoli"),
                options=list(role_options.keys())
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ " + t("permissions.users.create", "Crea Utente"))
            with col2:
                cancel = st.form_submit_button("❌ " + t("permissions.users.cancel", "Annulla"))
            
            if submit and username and email and full_name and password:
                success = self.create_user(username, email, full_name, password, selected_roles)
                if success:
                    st.success(t("permissions.users.created", "✅ Utente creato con successo!"))
                    st.rerun()
                else:
                    st.error(t("permissions.users.creation_error", "❌ Errore nella creazione dell'utente."))
    
    def show_add_role_form(self):
        """Mostra il form per aggiungere un nuovo ruolo"""
        st.subheader("➕ " + t("permissions.roles.add_new", "Aggiungi Nuovo Ruolo"))
        
        with st.form("add_role_form"):
            name = st.text_input(t("permissions.roles.name", "Nome Ruolo"), placeholder="es. editor")
            description = st.text_area(t("permissions.roles.description", "Descrizione"), placeholder="Ruolo per editor di contenuti")
            level = st.selectbox(
                t("permissions.roles.level", "Livello"),
                options=[1, 2, 3],
                format_func=lambda x: f"Livello {x} - {self.get_level_description(x)}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ " + t("permissions.roles.create", "Crea Ruolo"))
            with col2:
                cancel = st.form_submit_button("❌ " + t("permissions.roles.cancel", "Annulla"))
            
            if submit and name and description:
                success = self.create_role(name, description, level)
                if success:
                    st.success(t("permissions.roles.created", "✅ Ruolo creato con successo!"))
                    st.rerun()
                else:
                    st.error(t("permissions.roles.creation_error", "❌ Errore nella creazione del ruolo."))
    
    def show_add_permission_form(self):
        """Mostra il form per aggiungere un nuovo permesso"""
        st.subheader("➕ " + t("permissions.permissions.add_new", "Aggiungi Nuovo Permesso"))
        
        with st.form("add_permission_form"):
            name = st.text_input(t("permissions.permissions.name", "Nome Permesso"), placeholder="es. export_data")
            description = st.text_area(t("permissions.permissions.description", "Descrizione"), placeholder="Permesso per esportare dati")
            resource = st.selectbox(
                t("permissions.permissions.resource", "Risorsa"),
                options=["clienti", "incroci", "reports", "system", "users", "settings"]
            )
            action = st.selectbox(
                t("permissions.permissions.action", "Azione"),
                options=["read", "write", "delete", "admin", "export", "import"]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ " + t("permissions.permissions.create", "Crea Permesso"))
            with col2:
                cancel = st.form_submit_button("❌ " + t("permissions.permissions.cancel", "Annulla"))
            
            if submit and name and description:
                success = self.create_permission(name, description, resource, action)
                if success:
                    st.success(t("permissions.permissions.created", "✅ Permesso creato con successo!"))
                    st.rerun()
                else:
                    st.error(t("permissions.permissions.creation_error", "❌ Errore nella creazione del permesso."))
    
    def show_user_details(self):
        """Mostra i dettagli di un utente specifico"""
        st.subheader("🔍 " + t("permissions.users.details", "Dettagli Utente"))
        
        users = self.get_users_with_roles()
        if not users:
            st.warning(t("permissions.users.no_users_to_select", "Nessun utente disponibile."))
            return
        
        user_options = {f"{u['username']} ({u['full_name']})": u['id'] for u in users}
        selected_user = st.selectbox(
            t("permissions.users.select_user", "Seleziona Utente"),
            options=list(user_options.keys())
        )
        
        if selected_user:
            user_id = user_options[selected_user]
            self.show_user_permissions_details(user_id)
    
    def show_role_permissions(self):
        """Mostra i permessi di un ruolo specifico"""
        st.subheader("🔍 " + t("permissions.roles.permissions", "Permessi Ruolo"))
        
        roles = self.permission_manager.get_all_roles()
        if not roles:
            st.warning(t("permissions.roles.no_roles_to_select", "Nessun ruolo disponibile."))
            return
        
        role_options = {f"{r['name']} (Livello {r['level']})": r['id'] for r in roles}
        selected_role = st.selectbox(
            t("permissions.roles.select_role", "Seleziona Ruolo"),
            options=list(role_options.keys())
        )
        
        if selected_role:
            role_id = role_options[selected_role]
            self.show_role_permissions_details(role_id)
    
    def show_permissions_matrix(self):
        """Mostra la matrice dei permessi"""
        st.subheader("🔍 " + t("permissions.permissions.matrix", "Matrice Permessi"))
        
        roles = self.permission_manager.get_all_roles()
        permissions = self.permission_manager.get_all_permissions()
        
        if not roles or not permissions:
            st.warning(t("permissions.permissions.no_data", "Dati insufficienti per la matrice."))
            return
        
        # Crea matrice
        matrix_data = []
        for role in roles:
            role_perms = self.permission_manager.get_role_permissions(role['id'])
            role_perm_names = {perm['name'] for perm in role_perms}
            
            for perm in permissions:
                matrix_data.append({
                    'role': role['name'],
                    'permission': perm['name'],
                    'resource': perm['resource'],
                    'action': perm['action'],
                    'has_permission': perm['name'] in role_perm_names
                })
        
        if matrix_data:
            df = pd.DataFrame(matrix_data)
            st.dataframe(
                df,
                column_config={
                    "role": t("permissions.matrix.role", "Ruolo"),
                    "permission": t("permissions.matrix.permission", "Permesso"),
                    "resource": t("permissions.matrix.resource", "Risorsa"),
                    "action": t("permissions.matrix.action", "Azione"),
                    "has_permission": t("permissions.matrix.has_permission", "Ha Permesso")
                },
                hide_index=True,
                use_container_width=True
            )
    
    def show_user_permissions_details(self, user_id: str):
        """Mostra i dettagli dei permessi di un utente"""
        user_roles = self.permission_manager.get_user_roles(user_id)
        user_permissions = self.permission_manager.get_user_permissions(user_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎭 " + t("permissions.users.roles", "Ruoli"))
            if user_roles:
                for role in user_roles:
                    st.write(f"• **{role['name']}** - {role['description']}")
            else:
                st.info(t("permissions.users.no_roles", "Nessun ruolo assegnato."))
        
        with col2:
            st.subheader("🔐 " + t("permissions.users.permissions", "Permessi"))
            if user_permissions:
                for perm in sorted(user_permissions):
                    st.write(f"• **{perm}**")
            else:
                st.info(t("permissions.users.no_permissions", "Nessun permesso assegnato."))
    
    def show_role_permissions_details(self, role_id: str):
        """Mostra i dettagli dei permessi di un ruolo"""
        role_permissions = self.permission_manager.get_role_permissions(role_id)
        
        st.subheader("🔐 " + t("permissions.roles.permissions", "Permessi del Ruolo"))
        
        if role_permissions:
            df = pd.DataFrame(role_permissions)
            st.dataframe(
                df,
                column_config={
                    "name": t("permissions.roles.permission_name", "Nome"),
                    "description": t("permissions.roles.permission_description", "Descrizione"),
                    "resource": t("permissions.roles.resource", "Risorsa"),
                    "action": t("permissions.roles.action", "Azione")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(t("permissions.roles.no_permissions", "Nessun permesso assegnato a questo ruolo."))
    
    def create_user(self, username: str, email: str, full_name: str, password: str, roles: list) -> bool:
        """Crea un nuovo utente"""
        try:
            supabase = self.permission_manager._get_supabase()
            if not supabase:
                return False
            
            # Crea utente
            user_data = {
                'username': username,
                'email': email,
                'password_hash': password,  # In produzione, hashare la password
                'full_name': full_name,
                'is_active': True
            }
            
            response = supabase.table('system_users').insert(user_data).execute()
            if not response.data:
                return False
            
            user_id = response.data[0]['id']
            
            # Assegna ruoli
            current_user_id = self.permission_manager.get_user_id(st.session_state.get('username', 'admin'))
            for role_name in roles:
                roles_data = self.permission_manager.get_all_roles()
                role_id = next((r['id'] for r in roles_data if r['name'] == role_name), None)
                if role_id:
                    self.permission_manager.assign_role_to_user(user_id, role_id, current_user_id)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Errore creazione utente: {e}")
            return False
    
    def create_role(self, name: str, description: str, level: int) -> bool:
        """Crea un nuovo ruolo"""
        try:
            supabase = self.permission_manager._get_supabase()
            if not supabase:
                return False
            
            role_data = {
                'name': name,
                'description': description,
                'level': level,
                'is_system': False
            }
            
            response = supabase.table('roles').insert(role_data).execute()
            return bool(response.data)
            
        except Exception as e:
            st.error(f"❌ Errore creazione ruolo: {e}")
            return False
    
    def create_permission(self, name: str, description: str, resource: str, action: str) -> bool:
        """Crea un nuovo permesso"""
        try:
            supabase = self.permission_manager._get_supabase()
            if not supabase:
                return False
            
            permission_data = {
                'name': name,
                'description': description,
                'resource': resource,
                'action': action,
                'is_system': False
            }
            
            response = supabase.table('permissions').insert(permission_data).execute()
            return bool(response.data)
            
        except Exception as e:
            st.error(f"❌ Errore creazione permesso: {e}")
            return False
    
    def get_level_description(self, level: int) -> str:
        """Ottiene la descrizione di un livello"""
        descriptions = {
            1: t("permissions.roles.level_1", "Utente base"),
            2: t("permissions.roles.level_2", "Manager"),
            3: t("permissions.roles.level_3", "Amministratore")
        }
        return descriptions.get(level, t("permissions.roles.level_unknown", "Sconosciuto"))

# Istanza globale del componente
permissions_management = PermissionsManagement()
