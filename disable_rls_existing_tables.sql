-- 🚫 DISABILITAZIONE RLS SU TABELLE ESISTENTI - Dashboard Gestione CPA
-- Script per disabilitare RLS solo sulle tabelle che esistono realmente

-- 1. VERIFICA QUALI TABELLE ESISTONO
SELECT 'Tabelle esistenti nel database:' as info;
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'user_profiles', 'user_permissions', 'roles')
ORDER BY tablename;

-- 2. RIMUOVI TUTTE LE POLICY ESISTENTI SU USERS (se esiste)
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

-- 3. RIMUOVI TUTTE LE POLICY ESISTENTI SU USER_PROFILES (se esiste)
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Admins can manage all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_profiles;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_profiles;
DROP POLICY IF EXISTS "Enable update for users on their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Enable all for admins" ON user_profiles;

-- 4. RIMUOVI TUTTE LE POLICY ESISTENTI SU USER_PERMISSIONS (se esiste)
DROP POLICY IF EXISTS "Users can view their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can update their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can insert their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Admins can manage all permissions" ON user_permissions;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_permissions;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_permissions;
DROP POLICY IF EXISTS "Enable update for users on their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Enable all for admins" ON user_permissions;

-- 5. DISABILITA RLS SU TABELLE ESISTENTI (con controllo)
DO $$
BEGIN
    -- Disabilita RLS su users se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'users' AND schemaname = 'public') THEN
        ALTER TABLE users DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS disabilitato su tabella users';
    ELSE
        RAISE NOTICE 'Tabella users non trovata';
    END IF;
    
    -- Disabilita RLS su user_profiles se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_profiles' AND schemaname = 'public') THEN
        ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS disabilitato su tabella user_profiles';
    ELSE
        RAISE NOTICE 'Tabella user_profiles non trovata';
    END IF;
    
    -- Disabilita RLS su user_permissions se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_permissions' AND schemaname = 'public') THEN
        ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS disabilitato su tabella user_permissions';
    ELSE
        RAISE NOTICE 'Tabella user_permissions non trovata';
    END IF;
END $$;

-- 6. VERIFICA STATO RLS SU TABELLE ESISTENTI
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'user_profiles', 'user_permissions')
ORDER BY tablename;

-- 7. VERIFICA CHE NON CI SIANO PIÙ POLICY
SELECT 'Policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
AND tablename IN ('users', 'user_profiles', 'user_permissions')
ORDER BY tablename, policyname;

-- 8. TEST INSERIMENTO UTENTE (solo se la tabella users esiste)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'users' AND schemaname = 'public') THEN
        INSERT INTO users (id, username, email, password_hash, full_name, role, is_active, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'test_user_final',
            'test_final@example.com',
            'test_password',
            'Test User Final',
            'user',
            true,
            NOW(),
            NOW()
        );
        RAISE NOTICE 'Test inserimento utente completato';
    ELSE
        RAISE NOTICE 'Tabella users non trovata, impossibile testare inserimento';
    END IF;
END $$;

-- 9. VERIFICA UTENTI NEL SISTEMA (solo se la tabella users esiste)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'users' AND schemaname = 'public') THEN
        RAISE NOTICE 'Utenti nel sistema:';
        PERFORM username, email, full_name, role, is_active 
        FROM users 
        ORDER BY created_at DESC;
    END IF;
END $$;

-- 10. PULISCI L'UTENTE DI TEST (solo se la tabella users esiste)
DELETE FROM users WHERE username = 'test_user_final';
