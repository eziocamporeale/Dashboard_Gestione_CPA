-- 🔍 VERIFICA STRUTTURA ESATTA TABELLA user_permissions
-- Dashboard Gestione CPA - Script per verificare la struttura reale

-- ============================================================
-- VERIFICA STRUTTURA ESATTA user_permissions
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_name = 'user_permissions' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA STRUTTURA ESATTA user_roles
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_name = 'user_roles' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA SE LE TABELLE ESISTONO
-- ============================================================
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_name IN ('user_roles', 'user_permissions')
ORDER BY table_name;

-- ============================================================
-- VERIFICA CONTENUTO TABELLE (se esistono)
-- ============================================================
-- Prova a vedere se ci sono dati
SELECT 'user_roles' as table_name, COUNT(*) as record_count FROM user_roles
UNION ALL
SELECT 'user_permissions', COUNT(*) FROM user_permissions;

-- ============================================================
-- VERIFICA RELAZIONI ESISTENTI
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
    AND tc.table_name IN ('user_roles', 'user_permissions');
