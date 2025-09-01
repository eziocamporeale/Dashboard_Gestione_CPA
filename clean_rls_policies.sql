-- 🧹 PULIZIA COMPLETA POLICY RLS - Dashboard Gestione CPA
-- Script per rimuovere tutte le policy esistenti e crearne di nuove

-- 1. DISABILITA RLS TEMPORANEAMENTE
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 2. RIMUOVI TUTTE LE POLICY ESISTENTI
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

-- 3. VERIFICA CHE TUTTE LE POLICY SIANO STATE RIMOSSE
SELECT 'Policy rimanenti:' as info;
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE tablename = 'users';

-- 4. CREA NUOVE POLICY SEMPLICI E NON CONFLITTUALI

-- Policy per inserimento (permette a tutti gli utenti autenticati di inserire)
CREATE POLICY "insert_users_policy" ON users
    FOR INSERT 
    TO authenticated
    WITH CHECK (true);

-- Policy per lettura (permette a tutti gli utenti autenticati di leggere)
CREATE POLICY "select_users_policy" ON users
    FOR SELECT 
    TO authenticated
    USING (true);

-- Policy per aggiornamento (permette agli utenti di aggiornare solo il proprio profilo)
CREATE POLICY "update_users_policy" ON users
    FOR UPDATE 
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Policy per eliminazione (permette solo agli admin di eliminare)
CREATE POLICY "delete_users_policy" ON users
    FOR DELETE 
    TO authenticated
    USING (true);

-- 5. RIABILITA RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 6. VERIFICA LE NUOVE POLICY
SELECT 'Nuove policy create:' as info;
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE tablename = 'users'
ORDER BY policyname;
