-- 🔍 VERIFICA SOLO user_permissions
-- Dashboard Gestione CPA - Script per vedere la struttura di user_permissions

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
-- VERIFICA SE LA TABELLA È VUOTA
-- ============================================================
SELECT COUNT(*) as total_permissions FROM user_permissions;

-- ============================================================
-- VERIFICA PRIMI 3 RECORD (se esistono)
-- ============================================================
SELECT * FROM user_permissions LIMIT 3;
