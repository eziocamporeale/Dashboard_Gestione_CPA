-- 🧹 RIMOZIONE POLICY RLS SPECIFICHE - Dashboard Gestione CPA
-- Script per rimuovere le policy specifiche che sono ancora attive

-- 1. RIMUOVI LE POLICY SPECIFICHE SU USER_PERMISSIONS
DROP POLICY IF EXISTS "All authenticated users can view permissions" ON user_permissions;
DROP POLICY IF EXISTS "Everyone can view permissions" ON user_permissions;
DROP POLICY IF EXISTS "Only admins can manage permissions" ON user_permissions;

-- 2. RIMUOVI ANCHE LE POLICY GENERICHE (per sicurezza)
DROP POLICY IF EXISTS "Users can view their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can update their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can insert their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Admins can manage all permissions" ON user_permissions;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_permissions;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_permissions;
DROP POLICY IF EXISTS "Enable update for users on their own permissions" ON user_permissions;
DROP POLICY IF EXISTS "Enable all for admins" ON user_permissions;

-- 3. DISABILITA RLS SU USER_PERMISSIONS
ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;

-- 4. VERIFICA CHE LE POLICY SIANO STATE RIMOSSE
SELECT 'Policy rimanenti su user_permissions:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE tablename = 'user_permissions'
ORDER BY policyname;

-- 5. VERIFICA STATO RLS SU TUTTE LE TABELLE UTENTI
SELECT 'Stato RLS su tabelle utenti:' as info;
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'user_profiles', 'user_permissions')
ORDER BY tablename;

-- 6. VERIFICA TUTTE LE POLICY RIMANENTI
SELECT 'Tutte le policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
AND tablename IN ('users', 'user_profiles', 'user_permissions')
ORDER BY tablename, policyname;

-- 7. TEST FINALE: PROVA A CREARE UN UTENTE DI TEST
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'users' AND schemaname = 'public') THEN
        INSERT INTO users (id, username, email, password_hash, full_name, role, is_active, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'test_user_final_clean',
            'test_final_clean@example.com',
            'test_password',
            'Test User Final Clean',
            'user',
            true,
            NOW(),
            NOW()
        );
        RAISE NOTICE '✅ Test inserimento utente completato con successo';
        
        -- Mostra l'utente creato
        RAISE NOTICE 'Utente creato: test_user_final_clean';
        
        -- Pulisci l'utente di test
        DELETE FROM users WHERE username = 'test_user_final_clean';
        RAISE NOTICE '✅ Utente di test rimosso';
    ELSE
        RAISE NOTICE '❌ Tabella users non trovata';
    END IF;
END $$;
