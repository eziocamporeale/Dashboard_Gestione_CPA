-- 👥 VERIFICA UTENTI ESISTENTI - Dashboard Gestione CPA
-- Script per visualizzare tutti gli utenti presenti nel database

-- 1. VERIFICA TUTTI GLI UTENTI
SELECT '=== UTENTI PRESENTI NEL SISTEMA ===' as info;

SELECT 
    username,
    email,
    full_name,
    role,
    is_active,
    created_at,
    updated_at
FROM users 
ORDER BY created_at DESC;

-- 2. CONTA TOTALE UTENTI
SELECT '=== STATISTICHE ===' as info;

SELECT 
    COUNT(*) as totale_utenti,
    COUNT(CASE WHEN is_active = true THEN 1 END) as utenti_attivi,
    COUNT(CASE WHEN is_active = false THEN 1 END) as utenti_inattivi,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin,
    COUNT(CASE WHEN role = 'manager' THEN 1 END) as manager,
    COUNT(CASE WHEN role = 'user' THEN 1 END) as user
FROM users;

-- 3. VERIFICA USERNAME DUPLICATI
SELECT '=== USERNAME DUPLICATI ===' as info;

SELECT 
    username,
    COUNT(*) as occorrenze
FROM users 
GROUP BY username 
HAVING COUNT(*) > 1
ORDER BY occorrenze DESC;

-- 4. VERIFICA EMAIL DUPLICATE
SELECT '=== EMAIL DUPLICATE ===' as info;

SELECT 
    email,
    COUNT(*) as occorrenze
FROM users 
WHERE email IS NOT NULL
GROUP BY email 
HAVING COUNT(*) > 1
ORDER BY occorrenze DESC;

-- 5. UTENTI CREATI OGGI
SELECT '=== UTENTI CREATI OGGI ===' as info;

SELECT 
    username,
    email,
    full_name,
    role,
    created_at
FROM users 
WHERE DATE(created_at) = CURRENT_DATE
ORDER BY created_at DESC;
