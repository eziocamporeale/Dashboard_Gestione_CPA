-- 🛡️ SCHEMA SISTEMA PERMESSI AVANZATO - Dashboard Gestione CPA SUPABASE
-- Aggiunge gestione utenti, ruoli e permessi granulari al database Supabase (PostgreSQL)

-- ========================================
-- TABELLE SISTEMA UTENTI
-- ========================================

-- Tabella utenti sistema (separata dai clienti)
CREATE TABLE IF NOT EXISTS system_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS roles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    level INTEGER NOT NULL, -- Gerarchia: 1=user, 2=manager, 3=admin
    is_system BOOLEAN DEFAULT false, -- Ruoli di sistema non eliminabili
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella permessi
CREATE TABLE IF NOT EXISTS permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    resource TEXT NOT NULL, -- 'clienti', 'incroci', 'reports', 'system'
    action TEXT NOT NULL,   -- 'read', 'write', 'delete', 'admin', 'export'
    is_system BOOLEAN DEFAULT false, -- Permessi di sistema non eliminabili
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella user_roles (many-to-many)
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES system_users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES system_users(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- Tabella role_permissions (many-to-many)
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- Tabella user_permissions (permessi personalizzati)
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES system_users(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted BOOLEAN DEFAULT true,
    granted_by UUID REFERENCES system_users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, permission_id)
);

-- Tabella audit log per modifiche permessi
CREATE TABLE IF NOT EXISTS permission_audit_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES system_users(id),
    action TEXT NOT NULL, -- 'assign_role', 'revoke_role', 'grant_permission', 'revoke_permission'
    target_user_id UUID REFERENCES system_users(id),
    target_role_id UUID REFERENCES roles(id),
    target_permission_id UUID REFERENCES permissions(id),
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- DATI DI DEFAULT
-- ========================================

-- Inserimento ruoli di default
INSERT INTO roles (name, description, level, is_system) VALUES
('admin', 'Amministratore completo del sistema', 3, true),
('manager', 'Manager con accesso gestione clienti e incroci', 2, true),
('operator', 'Operatore con accesso limitato', 1, true),
('viewer', 'Visualizzatore solo lettura', 1, true),
('auditor', 'Auditor per report e controlli', 1, true)
ON CONFLICT (name) DO NOTHING;

-- Inserimento permessi di default
INSERT INTO permissions (name, description, resource, action, is_system) VALUES
-- Permessi clienti
('clienti_read', 'Visualizzare clienti', 'clienti', 'read', true),
('clienti_write', 'Creare/modificare clienti', 'clienti', 'write', true),
('clienti_delete', 'Eliminare clienti', 'clienti', 'delete', true),
('clienti_admin', 'Gestione completa clienti', 'clienti', 'admin', true),

-- Permessi incroci
('incroci_read', 'Visualizzare incroci', 'incroci', 'read', true),
('incroci_write', 'Creare/modificare incroci', 'incroci', 'write', true),
('incroci_delete', 'Eliminare incroci', 'incroci', 'delete', true),
('incroci_admin', 'Gestione completa incroci', 'incroci', 'admin', true),

-- Permessi reports
('reports_read', 'Visualizzare report', 'reports', 'read', true),
('reports_write', 'Creare report', 'reports', 'write', true),
('reports_export', 'Esportare report', 'reports', 'export', true),

-- Permessi sistema
('users_manage', 'Gestione utenti sistema', 'system', 'admin', true),
('settings_manage', 'Gestione impostazioni', 'system', 'admin', true),
('backup_manage', 'Gestione backup', 'system', 'admin', true),
('logs_view', 'Visualizzare log sistema', 'system', 'read', true),
('permissions_manage', 'Gestione permessi e ruoli', 'system', 'admin', true)
ON CONFLICT (name) DO NOTHING;

-- Inserimento utente admin di default
INSERT INTO system_users (username, email, password_hash, full_name, is_active) VALUES
('admin', 'admin@cpadashboard.com', 'admin', 'Amministratore CPA Dashboard', true)
ON CONFLICT (username) DO NOTHING;

-- Assegnazione ruolo admin all'utente admin
INSERT INTO user_roles (user_id, role_id, assigned_by) 
SELECT u.id, r.id, u.id 
FROM system_users u, roles r 
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT (user_id, role_id) DO NOTHING;

-- Assegnazione permessi admin al ruolo admin
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

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
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_system_users_updated_at
    BEFORE UPDATE ON system_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- VISTE UTILI
-- ========================================

-- Vista per utenti con ruoli
CREATE OR REPLACE VIEW v_users_with_roles AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    u.last_login,
    u.created_at,
    STRING_AGG(r.name, ', ') as roles,
    STRING_AGG(r.level::text, ', ') as role_levels
FROM system_users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
GROUP BY u.id, u.username, u.email, u.full_name, u.is_active, u.last_login, u.created_at;

-- Vista per ruoli con permessi
CREATE OR REPLACE VIEW v_roles_with_permissions AS
SELECT 
    r.id,
    r.name,
    r.description,
    r.level,
    r.is_system,
    STRING_AGG(p.name, ', ') as permissions,
    COUNT(p.id) as permission_count
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
GROUP BY r.id, r.name, r.description, r.level, r.is_system;

-- Vista per permessi utente (combinati da ruoli e personalizzati)
CREATE OR REPLACE VIEW v_user_permissions AS
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
LEFT JOIN user_permissions up ON u.id = up.user_id AND p.id = up.permission_id AND up.granted = true
WHERE u.is_active = true AND p.id IS NOT NULL;

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Abilita RLS su tutte le tabelle
ALTER TABLE system_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE permission_audit_log ENABLE ROW LEVEL SECURITY;

-- Policy per system_users (solo admin può gestire)
CREATE POLICY "Admin can manage system users" ON system_users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per ruoli (solo admin può gestire)
CREATE POLICY "Admin can manage roles" ON roles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per permessi (solo admin può gestire)
CREATE POLICY "Admin can manage permissions" ON permissions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per user_roles (solo admin può gestire)
CREATE POLICY "Admin can manage user roles" ON user_roles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per role_permissions (solo admin può gestire)
CREATE POLICY "Admin can manage role permissions" ON role_permissions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per user_permissions (solo admin può gestire)
CREATE POLICY "Admin can manage user permissions" ON user_permissions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per audit log (solo admin può vedere)
CREATE POLICY "Admin can view audit log" ON permission_audit_log
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policy per inserimento audit log (tutti gli utenti autenticati)
CREATE POLICY "Authenticated users can insert audit log" ON permission_audit_log
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- ========================================
-- FUNZIONI UTILITY
-- ========================================

-- Funzione per verificare se un utente ha un permesso
CREATE OR REPLACE FUNCTION user_has_permission(user_id UUID, permission_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    has_perm BOOLEAN := false;
BEGIN
    -- Verifica permessi ereditati dai ruoli
    SELECT EXISTS (
        SELECT 1 FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN user_roles ur ON rp.role_id = ur.role_id
        WHERE ur.user_id = user_id AND p.name = permission_name
    ) INTO has_perm;
    
    -- Se non ha permesso dai ruoli, verifica permessi personalizzati
    IF NOT has_perm THEN
        SELECT EXISTS (
            SELECT 1 FROM permissions p
            JOIN user_permissions up ON p.id = up.permission_id
            WHERE up.user_id = user_id AND p.name = permission_name AND up.granted = true
        ) INTO has_perm;
    END IF;
    
    RETURN has_perm;
END;
$$ LANGUAGE plpgsql;

-- Funzione per verificare se un utente ha un ruolo
CREATE OR REPLACE FUNCTION user_has_role(user_id UUID, role_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = user_id AND r.name = role_name
    );
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- COMMENTI E DOCUMENTAZIONE
-- ========================================

-- Commenti sulle tabelle
COMMENT ON TABLE system_users IS 'Utenti del sistema con credenziali e informazioni personali';
COMMENT ON TABLE roles IS 'Ruoli disponibili nel sistema con livelli di accesso';
COMMENT ON TABLE permissions IS 'Permessi granulari per risorse e azioni specifiche';
COMMENT ON TABLE user_roles IS 'Assegnazione ruoli agli utenti (many-to-many)';
COMMENT ON TABLE role_permissions IS 'Assegnazione permessi ai ruoli (many-to-many)';
COMMENT ON TABLE user_permissions IS 'Permessi personalizzati per utenti specifici';
COMMENT ON TABLE permission_audit_log IS 'Log delle modifiche ai permessi per audit';

-- Informazioni sulle tabelle create
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name IN ('system_users', 'roles', 'permissions', 'user_roles', 'role_permissions', 'user_permissions', 'permission_audit_log')
ORDER BY table_name, ordinal_position;

-- Informazioni sui trigger
SELECT trigger_name, event_manipulation, action_statement 
FROM information_schema.triggers 
WHERE trigger_name LIKE '%permission%';

-- Informazioni sulle viste
SELECT table_name, view_definition 
FROM information_schema.views 
WHERE table_name LIKE 'v_%permission%';
