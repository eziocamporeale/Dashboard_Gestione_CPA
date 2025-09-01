-- 🔧 CORREZIONE POLICY RLS - TABELLA USERS
-- Esegui questo script nel SQL Editor di Supabase per risolvere il problema di ricorsione

-- 1. DISABILITA TEMPORANEAMENTE RLS PER LA TABELLA USERS
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 2. RIMUOVI LE POLICY PROBLEMATICHE
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Admins can view all users" ON users;

-- 3. CREA POLICY RLS CORRETTE (SENZA RICORSIONE)

-- Policy per utenti che possono vedere il proprio profilo
CREATE POLICY "users_view_own_profile" ON users
    FOR SELECT USING (
        username = current_setting('request.jwt.claims', true)::json->>'username'
    );

-- Policy per admin che possono vedere tutti gli utenti (SENZA RICORSIONE)
CREATE POLICY "users_admin_full_access" ON users
    FOR ALL USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
    );

-- Policy per utenti che possono modificare il proprio profilo
CREATE POLICY "users_update_own_profile" ON users
    FOR UPDATE USING (
        username = current_setting('request.jwt.claims', true)::json->>'username'
    );

-- Policy per inserimento (solo admin o durante registrazione)
CREATE POLICY "users_insert_policy" ON users
    FOR INSERT WITH CHECK (
        current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
        OR 
        current_setting('request.jwt.claims', true)::json->>'username' IS NULL
    );

-- 4. RIABILITA RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 5. VERIFICA CHE LE POLICY SIANO STATE CREATE
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'users';

-- 6. MESSAGGIO DI SUCCESSO
DO $$
BEGIN
    RAISE NOTICE '✅ POLICY RLS CORRETTE PER TABELLA USERS!';
    RAISE NOTICE '🔒 Ricorsione infinita risolta';
    RAISE NOTICE '🚀 Sistema pronto per l''uso';
END $$;
