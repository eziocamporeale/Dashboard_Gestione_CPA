-- 🚫 DISABILITAZIONE RLS SU USER_ACCESS_LOGS - Dashboard Gestione CPA
-- Script per disabilitare RLS su tutte le tabelle di logging e accesso

-- 1. VERIFICA QUALI TABELLE DI LOGGING ESISTONO
SELECT 'Tabelle di logging esistenti:' as info;
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE '%log%' OR tablename LIKE '%access%' OR tablename LIKE '%audit%'
ORDER BY tablename;

-- 2. RIMUOVI TUTTE LE POLICY SU USER_ACCESS_LOGS
DROP POLICY IF EXISTS "Users can view their own access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Users can insert their own access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Admins can view all access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Admins can manage all access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_access_logs;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_access_logs;
DROP POLICY IF EXISTS "Enable update for users on their own logs" ON user_access_logs;
DROP POLICY IF EXISTS "Enable all for admins" ON user_access_logs;

-- 3. RIMUOVI POLICY SU ALTRE TABELLE DI LOGGING (se esistono)
DROP POLICY IF EXISTS "Users can view their own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can insert their own logs" ON user_logs;
DROP POLICY IF EXISTS "Admins can view all logs" ON user_logs;
DROP POLICY IF EXISTS "Admins can manage all logs" ON user_logs;

DROP POLICY IF EXISTS "Users can view their own audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Users can insert their own audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Admins can view all audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Admins can manage all audit logs" ON audit_logs;

-- 4. DISABILITA RLS SU TABELLE DI LOGGING (con controllo)
DO $$
BEGIN
    -- Disabilita RLS su user_access_logs se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_access_logs' AND schemaname = 'public') THEN
        ALTER TABLE user_access_logs DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS disabilitato su tabella user_access_logs';
    ELSE
        RAISE NOTICE 'Tabella user_access_logs non trovata';
    END IF;
    
    -- Disabilita RLS su user_logs se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_logs' AND schemaname = 'public') THEN
        ALTER TABLE user_logs DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS disabilitato su tabella user_logs';
    ELSE
        RAISE NOTICE 'Tabella user_logs non trovata';
    END IF;
    
    -- Disabilita RLS su audit_logs se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'audit_logs' AND schemaname = 'public') THEN
        ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS disabilitato su tabella audit_logs';
    ELSE
        RAISE NOTICE 'Tabella audit_logs non trovata';
    END IF;
END $$;

-- 5. VERIFICA STATO RLS SU TUTTE LE TABELLE
SELECT 'Stato RLS su tutte le tabelle:' as info;
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- 6. VERIFICA POLICY RIMANENTI
SELECT 'Policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- 7. TEST INSERIMENTO LOG (se la tabella esiste)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_access_logs' AND schemaname = 'public') THEN
        INSERT INTO user_access_logs (id, user_id, action, ip_address, user_agent, created_at)
        VALUES (
            gen_random_uuid(),
            (SELECT id FROM users WHERE username = 'admin' LIMIT 1),
            'test_access',
            '127.0.0.1',
            'test_agent',
            NOW()
        );
        RAISE NOTICE '✅ Test inserimento log completato';
        
        -- Pulisci il log di test
        DELETE FROM user_access_logs WHERE action = 'test_access';
        RAISE NOTICE '✅ Log di test rimosso';
    ELSE
        RAISE NOTICE '❌ Tabella user_access_logs non trovata';
    END IF;
END $$;
