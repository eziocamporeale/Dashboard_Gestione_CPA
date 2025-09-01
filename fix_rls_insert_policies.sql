-- 🔧 CORREZIONE POLICY RLS PER INSERIMENTO DATI INIZIALI
-- Esegui questo script nel SQL Editor di Supabase per permettere l'inserimento di dati

-- 1. DISABILITA TEMPORANEAMENTE RLS PER TUTTE LE TABELLE UTENTI
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_access_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE failed_login_attempts DISABLE ROW LEVEL SECURITY;

-- 2. RIMUOVI TUTTE LE POLICY ESISTENTI
DROP POLICY IF EXISTS "users_view_own_profile" ON users;
DROP POLICY IF EXISTS "users_admin_full_access" ON users;
DROP POLICY IF EXISTS "users_update_own_profile" ON users;
DROP POLICY IF EXISTS "users_insert_policy" ON users;

DROP POLICY IF EXISTS "All authenticated users can view roles" ON user_roles;
DROP POLICY IF EXISTS "All authenticated users can view permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can view their own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;

-- 3. INSERISCI I DATI DI DEFAULT (ORA FUNZIONERÀ)

-- 3.1 Inserisci ruoli predefiniti
INSERT INTO user_roles (role_name, description, permissions, is_active, created_at) VALUES
('admin', 'Amministratore completo del sistema', '["*"]', true, NOW()),
('manager', 'Manager con accesso esteso', '["clienti:read", "clienti:update", "incroci:read", "incroci:update"]', true, NOW()),
('user', 'Utente base con accesso limitato', '["clienti:read", "incroci:read"]', true, NOW());

-- 3.2 Inserisci permessi base
INSERT INTO user_permissions (permission_name, description, resource, action, is_active, created_at) VALUES
('clienti:create', 'Creare nuovi clienti', 'clienti', 'create', true, NOW()),
('clienti:read', 'Visualizzare clienti', 'clienti', 'read', true, NOW()),
('clienti:update', 'Modificare clienti', 'clienti', 'update', true, NOW()),
('clienti:delete', 'Eliminare clienti', 'clienti', 'delete', true, NOW()),
('incroci:create', 'Creare nuovi incroci', 'incroci', 'create', true, NOW()),
('incroci:read', 'Visualizzare incroci', 'incroci', 'read', true, NOW()),
('incroci:update', 'Modificare incroci', 'incroci', 'update', true, NOW()),
('incroci:delete', 'Eliminare incroci', 'incroci', 'delete', true, NOW()),
('users:create', 'Creare nuovi utenti', 'users', 'create', true, NOW()),
('users:read', 'Visualizzare utenti', 'users', 'read', true, NOW()),
('users:update', 'Modificare utenti', 'users', 'update', true, NOW()),
('users:delete', 'Eliminare utenti', 'users', 'delete', true, NOW());

-- 3.3 Inserisci utente admin
INSERT INTO users (username, email, password_hash, full_name, role, is_active, created_at, updated_at) VALUES
('admin', 'admin@cpadashboard.com', '$2b$12$riBfpHpVpccsb7NT7GFIRObLccRmnOiOtsSx65wbMb3C6Cuy/mDfu', 'Amministratore CPA Dashboard', 'admin', true, NOW(), NOW());

-- 3.4 Crea profilo per admin
INSERT INTO user_profiles (user_id, timezone, language, created_at, updated_at)
SELECT id, 'Europe/Rome', 'it', NOW(), NOW() FROM users WHERE username = 'admin';

-- 3.5 Inserisci log di sistema
INSERT INTO user_access_logs (user_id, action, success, details, created_at) VALUES
(NULL, 'system_populated', true, '{"note": "Sistema popolato automaticamente"}', NOW());

-- 4. VERIFICA INSERIMENTO DATI
SELECT 'user_roles' as table_name, COUNT(*) as record_count FROM user_roles
UNION ALL
SELECT 'user_permissions' as table_name, COUNT(*) as record_count FROM user_permissions
UNION ALL
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'user_profiles' as table_name, COUNT(*) as record_count FROM user_profiles
UNION ALL
SELECT 'user_access_logs' as table_name, COUNT(*) as record_count FROM user_access_logs;

-- 5. CREA POLICY RLS CORRETTE (DOPO AVER INSERITO I DATI)

-- 5.1 Policy per tabella users
CREATE POLICY "users_view_own_profile" ON users
    FOR SELECT USING (
        username = current_setting('request.jwt.claims', true)::json->>'username'
        OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

CREATE POLICY "users_admin_full_access" ON users
    FOR ALL USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

CREATE POLICY "users_update_own_profile" ON users
    FOR UPDATE USING (
        username = current_setting('request.jwt.claims', true)::json->>'username'
        OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

CREATE POLICY "users_insert_policy" ON users
    FOR INSERT WITH CHECK (
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

-- 5.2 Policy per altre tabelle
CREATE POLICY "user_roles_view_all" ON user_roles
    FOR SELECT USING (true);

CREATE POLICY "user_permissions_view_all" ON user_permissions
    FOR SELECT USING (true);

CREATE POLICY "user_sessions_own" ON user_sessions
    FOR ALL USING (
        user_id::text = current_setting('request.jwt.claims', true)::json->>'id'
        OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

CREATE POLICY "user_profiles_own" ON user_profiles
    FOR ALL USING (
        user_id::text = current_setting('request.jwt.claims', true)::json->>'id'
        OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

CREATE POLICY "user_access_logs_admin" ON user_access_logs
    FOR ALL USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

CREATE POLICY "failed_login_attempts_admin" ON failed_login_attempts
    FOR ALL USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

-- 6. RIABILITA RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE failed_login_attempts ENABLE ROW LEVEL SECURITY;

-- 7. MESSAGGIO DI SUCCESSO
DO $$
BEGIN
    RAISE NOTICE '✅ SISTEMA POPOLATO E POLICY RLS CORRETTE!';
    RAISE NOTICE '👑 Utente admin: admin/admin123';
    RAISE NOTICE '🏷️ Ruoli: admin, manager, user';
    RAISE NOTICE '🔐 Permessi: 12 permessi base';
    RAISE NOTICE '🔒 RLS attivato con policy corrette';
    RAISE NOTICE '🚀 Sistema pronto per l''uso!';
END $$;
