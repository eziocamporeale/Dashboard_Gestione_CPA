-- 🔧 CORREZIONE POLICY RLS PER INSERIMENTO UTENTI - Dashboard Gestione CPA
-- Script per permettere la creazione di nuovi utenti

-- 1. DISABILITA TEMPORANEAMENTE RLS PER INSERIMENTO
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 2. RIMUOVI POLICY ESISTENTI PROBLEMATICHE
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Users can insert their own profile" ON users;
DROP POLICY IF EXISTS "Admins can manage all users" ON users;

-- 3. CREA NUOVE POLICY CORRETTE PER INSERIMENTO
CREATE POLICY "Enable insert for authenticated users" ON users
    FOR INSERT 
    TO authenticated
    WITH CHECK (true);

-- 4. CREA POLICY PER LETTURA
CREATE POLICY "Enable read access for authenticated users" ON users
    FOR SELECT 
    TO authenticated
    USING (true);

-- 5. CREA POLICY PER AGGIORNAMENTO
CREATE POLICY "Enable update for users on their own profile" ON users
    FOR UPDATE 
    TO authenticated
    USING (auth.uid()::text = id::text)
    WITH CHECK (auth.uid()::text = id::text);

-- 6. CREA POLICY PER AMMINISTRATORI (gestione completa)
CREATE POLICY "Enable all for admins" ON users
    FOR ALL 
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

-- 7. RIABILITA RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 8. VERIFICA CHE LE POLICY SIANO ATTIVE
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE tablename = 'users';
