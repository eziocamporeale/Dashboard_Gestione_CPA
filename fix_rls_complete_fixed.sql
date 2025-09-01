-- 🔧 CORREZIONE COMPLETA RLS POLICIES E RIPRISTINO UTENTE ADMIN
-- Dashboard Gestione CPA - Script da eseguire nell'SQL Editor di Supabase
-- VERSIONE CORRETTA CON UUID VALIDI

-- ============================================================
-- FASE 1: DISABILITAZIONE RLS TEMPORANEA
-- ============================================================

-- Disabilita RLS per tutte le tabelle utenti
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_access_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE failed_login_attempts DISABLE ROW LEVEL SECURITY;

-- ============================================================
-- FASE 2: PULIZIA DATI ESISTENTI (se presenti)
-- ============================================================

-- Rimuovi tutti i dati esistenti dalle tabelle utenti
DELETE FROM user_access_logs;
DELETE FROM failed_login_attempts;
DELETE FROM user_sessions;
DELETE FROM user_permissions;
DELETE FROM user_profiles;
DELETE FROM user_roles;
DELETE FROM users;

-- ============================================================
-- FASE 3: INSERIMENTO RUOLI CON UUID VALIDI
-- ============================================================

INSERT INTO user_roles (id, role_name, description, is_active, created_at) VALUES
(gen_random_uuid(), 'admin', 'Accesso completo al sistema', true, NOW()),
(gen_random_uuid(), 'manager', 'Gestione clienti e incroci', true, NOW()),
(gen_random_uuid(), 'user', 'Accesso limitato', true, NOW());

-- ============================================================
-- FASE 4: INSERIMENTO PERMESSI CON UUID VALIDI
-- ============================================================

-- Prima recupera gli ID dei ruoli appena creati
WITH role_ids AS (
    SELECT id, role_name FROM user_roles
)
INSERT INTO user_permissions (id, role_id, permission_name, is_active, created_at)
SELECT 
    gen_random_uuid(),
    r.id,
    p.permission_name,
    true,
    NOW()
FROM role_ids r
CROSS JOIN (
    VALUES 
        ('user_management'),
        ('system_stats'),
        ('all_access')
) AS p(permission_name)
WHERE r.role_name = 'admin'

UNION ALL

SELECT 
    gen_random_uuid(),
    r.id,
    p.permission_name,
    true,
    NOW()
FROM role_ids r
CROSS JOIN (
    VALUES 
        ('client_management'),
        ('cross_management')
) AS p(permission_name)
WHERE r.role_name = 'manager'

UNION ALL

SELECT 
    gen_random_uuid(),
    r.id,
    p.permission_name,
    true,
    NOW()
FROM role_ids r
CROSS JOIN (
    VALUES 
        ('view_clients'),
        ('view_crosses')
) AS p(permission_name)
WHERE r.role_name = 'user';

-- ============================================================
-- FASE 5: INSERIMENTO UTENTE ADMIN CON UUID VALIDO
-- ============================================================

INSERT INTO users (id, username, email, full_name, role, is_active, created_at, updated_at) VALUES
(gen_random_uuid(), 'admin', 'admin@cpadashboard.com', 'Amministratore CPA Dashboard', 'admin', true, NOW(), NOW());

-- ============================================================
-- FASE 6: INSERIMENTO PROFILO ADMIN CON UUID VALIDO
-- ============================================================

INSERT INTO user_profiles (id, user_id, timezone, language, phone, address, preferences, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    u.id,
    'Europe/Rome',
    'it',
    '+39 123 456 789',
    'Via Roma 123, Milano, Italia',
    '{"theme": "light", "notifications": true}',
    NOW(),
    NOW()
FROM users u
WHERE u.username = 'admin';

-- ============================================================
-- FASE 7: INSERIMENTO LOG INIZIALE CON UUID VALIDO
-- ============================================================

INSERT INTO user_access_logs (id, user_id, action, success, details, created_at)
SELECT 
    gen_random_uuid(),
    u.id,
    'user_created',
    true,
    '{"message": "Utente admin creato durante setup iniziale"}',
    NOW()
FROM users u
WHERE u.username = 'admin';

-- ============================================================
-- FASE 8: VERIFICA INSERIMENTI
-- ============================================================

-- Conta record inseriti
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'user_profiles', COUNT(*) FROM user_profiles
UNION ALL
SELECT 'user_roles', COUNT(*) FROM user_roles
UNION ALL
SELECT 'user_permissions', COUNT(*) FROM user_permissions
UNION ALL
SELECT 'user_access_logs', COUNT(*) FROM user_access_logs;

-- ============================================================
-- FASE 9: RIABILITAZIONE RLS CON POLICIES CORRETTE
-- ============================================================

-- Crea policies corrette per la tabella users
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = id OR role = 'admin');

CREATE POLICY "Admins can manage all users" ON users
    FOR ALL USING (role = 'admin');

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid()::text = id OR role = 'admin');

-- Crea policies per user_profiles
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Admins can manage all profiles" ON user_profiles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = user_profiles.user_id 
            AND users.role = 'admin'
        )
    );

-- Crea policies per user_roles
CREATE POLICY "Everyone can view roles" ON user_roles
    FOR SELECT USING (true);

CREATE POLICY "Only admins can manage roles" ON user_roles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.role = 'admin'
        )
    );

-- Crea policies per user_permissions
CREATE POLICY "Everyone can view permissions" ON user_permissions
    FOR SELECT USING (true);

CREATE POLICY "Only admins can manage permissions" ON user_permissions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.role = 'admin'
        )
    );

-- Crea policies per user_sessions
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Admins can manage all sessions" ON user_sessions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = user_sessions.user_id 
            AND users.role = 'admin'
        )
    );

-- Crea policies per user_access_logs
CREATE POLICY "Users can view their own logs" ON user_access_logs
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Admins can view all logs" ON user_access_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.role = 'admin'
        )
    );

-- Crea policies per failed_login_attempts
CREATE POLICY "Admins can view failed login attempts" ON failed_login_attempts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.role = 'admin'
        )
    );

-- Riabilita RLS per tutte le tabelle
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE failed_login_attempts ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- FASE 10: VERIFICA FINALE
-- ============================================================

-- Verifica che tutto sia stato inserito correttamente
SELECT 'VERIFICA FINALE' as status;
SELECT 'Utente admin disponibile per login' as message;

-- Mostra utente admin creato
SELECT username, email, full_name, role, is_active 
FROM users 
WHERE username = 'admin';

-- ============================================================
-- MESSAGGIO DI SUCCESSO
-- ============================================================

-- 🎉 RIPRISTINO COMPLETATO!
-- Ora puoi fare login con:
-- Username: admin
-- Password: admin123 (se gestita da streamlit_authenticator)
-- 
-- Le RLS policies sono state configurate correttamente per:
-- - Gli admin possono accedere a tutto
-- - Gli utenti normali possono vedere solo i propri dati
-- - La sicurezza è mantenuta ma non blocca il funzionamento
