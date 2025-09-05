-- ========================================
-- CORREZIONE DEFINITIVA RLS POLICIES E INSERIMENTO BROKER
-- Dashboard Gestione CPA
-- ========================================

-- 1. DISABILITA RLS TEMPORANEAMENTE per inserire i broker
ALTER TABLE broker_links DISABLE ROW LEVEL SECURITY;

-- 2. Inserisce i broker predefiniti (solo se non esistono già)
INSERT INTO broker_links (broker_name, affiliate_link, is_active, created_at, updated_at) 
SELECT * FROM (VALUES
    ('Ultima Markets', 'https://ultimamarkets.com', true, NOW(), NOW()),
    ('Puprime', 'https://puprime.com', true, NOW(), NOW()),
    ('Axi', 'https://axi.com', true, NOW(), NOW()),
    ('Global Prime', 'https://globalprime.com', true, NOW(), NOW()),
    ('FxCess', 'https://fxcess.com', true, NOW(), NOW()),
    ('Vtmarkets', 'https://vtmarkets.com', true, NOW(), NOW()),
    ('Tauro Markets', 'https://tauromarkets.com', true, NOW(), NOW()),
    ('FPG', 'https://fpg.com', true, NOW(), NOW()),
    ('TMGM', 'https://tmgm.com', true, NOW(), NOW())
) AS new_brokers(broker_name, affiliate_link, is_active, created_at, updated_at)
WHERE NOT EXISTS (
    SELECT 1 FROM broker_links 
    WHERE broker_links.broker_name = new_brokers.broker_name
);

-- 3. RIABILITA RLS
ALTER TABLE broker_links ENABLE ROW LEVEL SECURITY;

-- 4. Rimuove tutte le policies esistenti
DROP POLICY IF EXISTS "broker_links_read_policy" ON broker_links;
DROP POLICY IF EXISTS "broker_links_insert_policy" ON broker_links;
DROP POLICY IF EXISTS "broker_links_update_policy" ON broker_links;
DROP POLICY IF EXISTS "broker_links_delete_policy" ON broker_links;
DROP POLICY IF EXISTS "Admin and Manager full access" ON broker_links;
DROP POLICY IF EXISTS "Authenticated users read broker_links" ON broker_links;
DROP POLICY IF EXISTS "Allow authenticated users to read broker_links" ON broker_links;
DROP POLICY IF EXISTS "Allow admin to manage broker_links" ON broker_links;
DROP POLICY IF EXISTS "Allow admin and manager to insert broker_links" ON broker_links;
DROP POLICY IF EXISTS "Allow admin and manager to update broker_links" ON broker_links;
DROP POLICY IF EXISTS "Allow admin and manager to delete broker_links" ON broker_links;

-- 5. Crea nuove policies semplici e funzionanti
CREATE POLICY "broker_links_read_policy" ON broker_links
    FOR SELECT USING (true);

CREATE POLICY "broker_links_insert_policy" ON broker_links
    FOR INSERT WITH CHECK (true);

CREATE POLICY "broker_links_update_policy" ON broker_links
    FOR UPDATE USING (true);

CREATE POLICY "broker_links_delete_policy" ON broker_links
    FOR DELETE USING (true);

-- 6. Verifica inserimento
SELECT 'Broker inseriti:' as status;
SELECT broker_name, affiliate_link, is_active FROM broker_links ORDER BY broker_name;

-- 7. Mostra statistiche
SELECT 
    COUNT(*) as totale_broker,
    COUNT(*) FILTER (WHERE is_active = true) as broker_attivi,
    COUNT(*) FILTER (WHERE is_active = false) as broker_inattivi
FROM broker_links;
