-- 🔍 VERIFICA SOLO LE COLONNE DELLE TABELLE
-- Dashboard Gestione CPA - Script per vedere le colonne esatte

-- ============================================================
-- VERIFICA COLONNE user_permissions
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'user_permissions' 
ORDER BY ordinal_position;

-- ============================================================
-- VERIFICA COLONNE user_roles
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'user_roles' 
ORDER BY ordinal_position;
