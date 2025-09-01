-- 🔍 VERIFICA STRUTTURA TABELLE UTENTI
-- Dashboard Gestione CPA - Script per verificare la struttura delle tabelle

-- ============================================================
-- VERIFICA STRUTTURA TABELLA users
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA TABELLA user_roles
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_roles' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA TABELLA user_permissions
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_permissions' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA TABELLA user_profiles
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_profiles' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA TABELLA user_sessions
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_sessions' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA TABELLA user_access_logs
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_access_logs' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA TABELLA failed_login_attempts
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'failed_login_attempts' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA RELAZIONI E FOREIGN KEYS
-- ============================================================
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name IN ('users', 'user_roles', 'user_permissions', 'user_profiles', 'user_sessions', 'user_access_logs', 'failed_login_attempts');
