-- 🚫 DISABILITAZIONE RLS SU TABELLE DI LOGGING ESISTENTI - Dashboard Gestione CPA
-- Script per disabilitare RLS solo sulle tabelle che esistono realmente

-- 1. VERIFICA QUALI TABELLE DI LOGGING ESISTONO REALMENTE
SELECT 'Tabelle di logging esistenti:' as info;
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND (tablename LIKE '%log%' OR tablename LIKE '%access%' OR tablename LIKE '%audit%')
ORDER BY tablename;

-- 2. RIMUOVI POLICY SU USER_ACCESS_LOGS (solo se esiste)
DROP POLICY IF EXISTS "Users can view their own access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Users can insert their own access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Admins can view all access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Admins can manage all access logs" ON user_access_logs;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON user_access_logs;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON user_access_logs;
DROP POLICY IF EXISTS "Enable update for users on their own logs" ON user_access_logs;
DROP POLICY IF EXISTS "Enable all for admins" ON user_access_logs;

-- 3. DISABILITA RLS SU TABELLE DI LOGGING ESISTENTI (con controllo)
DO $$
BEGIN
    -- Disabilita RLS su user_access_logs se esiste
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_access_logs' AND schemaname = 'public') THEN
        ALTER TABLE user_access_logs DISABLE ROW LEVEL SECURITY;
        RAISE NOTICE '✅ RLS disabilitato su tabella user_access_logs';
    ELSE
        RAISE NOTICE '❌ Tabella user_access_logs non trovata';
    END IF;
    
    -- Disabilita RLS su altre tabelle di logging se esistono
    -- (aggiungi qui altre tabelle se necessario)
END $$;

-- 4. VERIFICA STATO RLS SU TUTTE LE TABELLE
SELECT 'Stato RLS su tutte le tabelle:' as info;
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- 5. VERIFICA POLICY RIMANENTI
SELECT 'Policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- 6. TEST INSERIMENTO LOG (solo se la tabella esiste)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'user_access_logs' AND schemaname = 'public') THEN
        -- Prova a inserire un log di test
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
        RAISE NOTICE '❌ Tabella user_access_logs non trovata - impossibile testare inserimento';
    END IF;
END $$;

-- 7. VERIFICA UTENTI ESISTENTI
SELECT 'Utenti presenti nel sistema:' as info;
SELECT username, email, full_name, role, is_active, created_at
FROM users 
ORDER BY created_at DESC;
