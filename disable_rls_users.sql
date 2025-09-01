-- 🚫 DISABILITAZIONE COMPLETA RLS - Dashboard Gestione CPA
-- Script per disabilitare RLS sulla tabella users e permettere inserimenti liberi

-- 1. RIMUOVI TUTTE LE POLICY ESISTENTI
DROP POLICY IF EXISTS "delete_users_policy" ON users;
DROP POLICY IF EXISTS "insert_users_policy" ON users;
DROP POLICY IF EXISTS "select_users_policy" ON users;
DROP POLICY IF EXISTS "update_users_policy" ON users;
DROP POLICY IF EXISTS "users_view_own_profile" ON users;
DROP POLICY IF EXISTS "users_admin_full_access" ON users;
DROP POLICY IF EXISTS "users_update_own_profile" ON users;
DROP POLICY IF EXISTS "users_insert_policy" ON users;
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can update their own data" ON users;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON users;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON users;
DROP POLICY IF EXISTS "Enable update for users on their own profile" ON users;
DROP POLICY IF EXISTS "Enable all for admins" ON users;
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Users can insert their own profile" ON users;
DROP POLICY IF EXISTS "Admins can manage all users" ON users;

-- 2. DISABILITA COMPLETAMENTE RLS SULLA TABELLA USERS
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 3. VERIFICA CHE RLS SIA DISABILITATO
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename = 'users';

-- 4. VERIFICA CHE NON CI SIANO PIÙ POLICY
SELECT 'Policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE tablename = 'users';

-- 5. TEST INSERIMENTO UTENTE DI PROVA
INSERT INTO users (id, username, email, password_hash, full_name, role, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'test_user',
    'test@example.com',
    'test_password',
    'Test User',
    'user',
    true,
    NOW(),
    NOW()
);

-- 6. VERIFICA CHE L'INSERIMENTO SIA ANDATO A BUON FINE
SELECT 'Utenti nel sistema:' as info;
SELECT username, email, full_name, role, is_active 
FROM users 
ORDER BY created_at DESC;

-- 7. PULISCI L'UTENTE DI TEST
DELETE FROM users WHERE username = 'test_user';
