-- 🚫 DISABILITAZIONE COMPLETA RLS SU TUTTE LE TABELLE - Dashboard Gestione CPA
-- Script per disabilitare RLS su tutte le tabelle del sistema utenti

-- 1. RIMUOVI TUTTE LE POLICY ESISTENTI SU USERS
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

-- 2. RIMUOVI TUTTE LE POLICY ESISTENTI SU USER_PROFILES
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Admins can manage all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_profiles;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_profiles;
DROP POLICY IF EXISTS "Enable update for users on their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Enable all for admins" ON user_profiles;

-- 3. RIMUOVI TUTTE LE POLICY ESISTENTI SU USER_PERMISSIONS
DROP POLICY IF EXISTS "Users can view their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can update their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can insert their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Admins can manage all permissions" ON user_permissions;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_permissions;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_permissions;
DROP POLICY IF EXISTS "Enable update for users on their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Enable all for admins" ON user_permissions;

-- 4. RIMUOVI TUTTE LE POLICY ESISTENTI SU ROLES
DROP POLICY IF EXISTS "Users can view roles" ON roles;
DROP POLICY IF EXISTS "Users can update roles" ON roles;
DROP POLICY IF EXISTS "Users can insert roles" ON roles;
DROP POLICY IF EXISTS "Admins can manage all roles" ON roles;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON roles;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON roles;
DROP POLICY IF EXISTS "Enable update for users on roles" ON roles;
DROP POLICY IF EXISTS "Enable all for admins" ON roles;

-- 5. DISABILITA COMPLETAMENTE RLS SU TUTTE LE TABELLE
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;
ALTER TABLE roles DISABLE ROW LEVEL SECURITY;

-- 6. VERIFICA CHE RLS SIA DISABILITATO SU TUTTE LE TABELLE
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename IN ('users', 'user_profiles', 'user_permissions', 'roles')
ORDER BY tablename;

-- 7. VERIFICA CHE NON CI SIANO PIÙ POLICY
SELECT 'Policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE tablename IN ('users', 'user_profiles', 'user_permissions', 'roles')
ORDER BY tablename, policyname;

-- 8. TEST INSERIMENTO UTENTE COMPLETO
INSERT INTO users (id, username, email, password_hash, full_name, role, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'test_user_complete',
    'test_complete@example.com',
    'test_password',
    'Test User Complete',
    'user',
    true,
    NOW(),
    NOW()
);

-- 9. VERIFICA CHE L'INSERIMENTO SIA ANDATO A BUON FINE
SELECT 'Utenti nel sistema:' as info;
SELECT username, email, full_name, role, is_active 
FROM users 
ORDER BY created_at DESC;

-- 10. PULISCI L'UTENTE DI TEST
DELETE FROM users WHERE username = 'test_user_complete';
