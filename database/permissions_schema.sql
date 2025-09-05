-- 🛡️ SCHEMA SISTEMA PERMESSI AVANZATO - Dashboard Gestione CPA
-- Aggiunge gestione utenti, ruoli e permessi granulari al database esistente

-- ========================================
-- TABELLE SISTEMA UTENTI
-- ========================================

-- Tabella utenti sistema (separata dai clienti)
CREATE TABLE IF NOT EXISTS system_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    level INTEGER NOT NULL, -- Gerarchia: 1=user, 2=manager, 3=admin
    is_system BOOLEAN DEFAULT 0, -- Ruoli di sistema non eliminabili
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella permessi
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    resource TEXT NOT NULL, -- 'clienti', 'incroci', 'reports', 'system'
    action TEXT NOT NULL,   -- 'read', 'write', 'delete', 'admin', 'export'
    is_system BOOLEAN DEFAULT 0, -- Permessi di sistema non eliminabili
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella user_roles (many-to-many)
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_by INTEGER,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES system_users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES system_users(id)
);

-- Tabella role_permissions (many-to-many)
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- Tabella user_permissions (permessi personalizzati)
CREATE TABLE IF NOT EXISTS user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted BOOLEAN DEFAULT 1,
    granted_by INTEGER,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES system_users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES system_users(id)
);

-- Tabella audit log per modifiche permessi
CREATE TABLE IF NOT EXISTS permission_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL, -- 'assign_role', 'revoke_role', 'grant_permission', 'revoke_permission'
    target_user_id INTEGER,
    target_role_id INTEGER,
    target_permission_id INTEGER,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES system_users(id),
    FOREIGN KEY (target_user_id) REFERENCES system_users(id)
);

-- ========================================
-- DATI DI DEFAULT
-- ========================================

-- Inserimento ruoli di default
INSERT OR IGNORE INTO roles (name, description, level, is_system) VALUES
('admin', 'Amministratore completo del sistema', 3, 1),
('manager', 'Manager con accesso gestione clienti e incroci', 2, 1),
('operator', 'Operatore con accesso limitato', 1, 1),
('viewer', 'Visualizzatore solo lettura', 1, 1),
('auditor', 'Auditor per report e controlli', 1, 1);

-- Inserimento permessi di default
INSERT OR IGNORE INTO permissions (name, description, resource, action, is_system) VALUES
-- Permessi clienti
('clienti_read', 'Visualizzare clienti', 'clienti', 'read', 1),
('clienti_write', 'Creare/modificare clienti', 'clienti', 'write', 1),
('clienti_delete', 'Eliminare clienti', 'clienti', 'delete', 1),
('clienti_admin', 'Gestione completa clienti', 'clienti', 'admin', 1),

-- Permessi incroci
('incroci_read', 'Visualizzare incroci', 'incroci', 'read', 1),
('incroci_write', 'Creare/modificare incroci', 'incroci', 'write', 1),
('incroci_delete', 'Eliminare incroci', 'incroci', 'delete', 1),
('incroci_admin', 'Gestione completa incroci', 'incroci', 'admin', 1),

-- Permessi reports
('reports_read', 'Visualizzare report', 'reports', 'read', 1),
('reports_write', 'Creare report', 'reports', 'write', 1),
('reports_export', 'Esportare report', 'reports', 'export', 1),

-- Permessi sistema
('users_manage', 'Gestione utenti sistema', 'system', 'admin', 1),
('settings_manage', 'Gestione impostazioni', 'system', 'admin', 1),
('backup_manage', 'Gestione backup', 'system', 'admin', 1),
('logs_view', 'Visualizzare log sistema', 'system', 'read', 1),
('permissions_manage', 'Gestione permessi e ruoli', 'system', 'admin', 1);

-- Inserimento utente admin di default
INSERT OR IGNORE INTO system_users (username, email, password_hash, full_name, is_active) VALUES
('admin', 'admin@cpadashboard.com', 'admin', 'Amministratore CPA Dashboard', 1);

-- Assegnazione ruolo admin all'utente admin
INSERT OR IGNORE INTO user_roles (user_id, role_id, assigned_by) 
SELECT u.id, r.id, u.id 
FROM system_users u, roles r 
WHERE u.username = 'admin' AND r.name = 'admin';

-- Assegnazione permessi admin al ruolo admin
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'admin';

-- ========================================
-- INDICI PER PERFORMANCE
-- ========================================

CREATE INDEX IF NOT EXISTS idx_system_users_username ON system_users(username);
CREATE INDEX IF NOT EXISTS idx_system_users_email ON system_users(email);
CREATE INDEX IF NOT EXISTS idx_system_users_active ON system_users(is_active);
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_level ON roles(level);
CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);
CREATE INDEX IF NOT EXISTS idx_permissions_action ON permissions(action);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_permission_id ON user_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_permission_audit_log_user_id ON permission_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_permission_audit_log_created_at ON permission_audit_log(created_at);

-- ========================================
-- TRIGGER PER AUDIT
-- ========================================

-- Trigger per aggiornare updated_at
CREATE TRIGGER IF NOT EXISTS update_system_users_updated_at
    AFTER UPDATE ON system_users
    FOR EACH ROW
BEGIN
    UPDATE system_users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_roles_updated_at
    AFTER UPDATE ON roles
    FOR EACH ROW
BEGIN
    UPDATE roles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ========================================
-- VISTE UTILI
-- ========================================

-- Vista per utenti con ruoli
CREATE VIEW IF NOT EXISTS v_users_with_roles AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    u.last_login,
    u.created_at,
    GROUP_CONCAT(r.name, ', ') as roles,
    GROUP_CONCAT(r.level, ', ') as role_levels
FROM system_users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
GROUP BY u.id;

-- Vista per ruoli con permessi
CREATE VIEW IF NOT EXISTS v_roles_with_permissions AS
SELECT 
    r.id,
    r.name,
    r.description,
    r.level,
    r.is_system,
    GROUP_CONCAT(p.name, ', ') as permissions,
    COUNT(p.id) as permission_count
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
GROUP BY r.id;

-- Vista per permessi utente (combinati da ruoli e personalizzati)
CREATE VIEW IF NOT EXISTS v_user_permissions AS
SELECT DISTINCT
    u.id as user_id,
    u.username,
    p.id as permission_id,
    p.name as permission_name,
    p.resource,
    p.action,
    CASE 
        WHEN up.id IS NOT NULL THEN 'personal'
        ELSE 'inherited'
    END as permission_type
FROM system_users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
LEFT JOIN user_permissions up ON u.id = up.user_id AND p.id = up.permission_id AND up.granted = 1
WHERE u.is_active = 1 AND p.id IS NOT NULL;

-- ========================================
-- FUNZIONI UTILITY
-- ========================================

-- Funzione per verificare se un utente ha un permesso
-- (da implementare in Python per maggiore flessibilità)

-- ========================================
-- COMMENTI E DOCUMENTAZIONE
-- ========================================

-- Informazioni sulle tabelle create
PRAGMA table_info(system_users);
PRAGMA table_info(roles);
PRAGMA table_info(permissions);
PRAGMA table_info(user_roles);
PRAGMA table_info(role_permissions);
PRAGMA table_info(user_permissions);
PRAGMA table_info(permission_audit_log);

-- Informazioni sui trigger
SELECT name, sql FROM sqlite_master WHERE type = 'trigger' AND name LIKE '%permission%';

-- Informazioni sulle viste
SELECT name, sql FROM sqlite_master WHERE type = 'view' AND name LIKE '%permission%';
