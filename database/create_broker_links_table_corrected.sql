-- Creazione tabella broker_links per gestione link di affiliate
-- Creato da Ezio Camporeale per Dashboard Gestione CPA
-- ADATTATO per la struttura del progetto CPA (campo role diretto invece di tabella roles separata)

-- Tabella principale broker_links
CREATE TABLE IF NOT EXISTS broker_links (
    id SERIAL PRIMARY KEY,
    broker_name VARCHAR(255) NOT NULL,
    affiliate_link TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_broker_links_broker_name ON broker_links(broker_name);
CREATE INDEX IF NOT EXISTS idx_broker_links_is_active ON broker_links(is_active);
CREATE INDEX IF NOT EXISTS idx_broker_links_created_at ON broker_links(created_at);
CREATE INDEX IF NOT EXISTS idx_broker_links_created_by ON broker_links(created_by);

-- Trigger per aggiornare updated_at automaticamente
CREATE OR REPLACE FUNCTION update_broker_links_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_broker_links_updated_at
    BEFORE UPDATE ON broker_links
    FOR EACH ROW
    EXECUTE FUNCTION update_broker_links_updated_at();

-- Politiche RLS (Row Level Security)
ALTER TABLE broker_links ENABLE ROW LEVEL SECURITY;

-- Politica per accesso completo (admin e manager) - ADATTATA per struttura CPA
CREATE POLICY "Admin and Manager full access" ON broker_links
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id::text = auth.uid()::text
            AND u.role IN ('admin', 'manager')
        )
    );

-- Politica per lettura (tutti gli utenti autenticati)
CREATE POLICY "Authenticated users read access" ON broker_links
    FOR SELECT USING (
        auth.uid() IS NOT NULL
    );

-- Commenti per documentazione
COMMENT ON TABLE broker_links IS 'Tabella per gestione link di affiliate dei broker';
COMMENT ON COLUMN broker_links.broker_name IS 'Nome del broker';
COMMENT ON COLUMN broker_links.affiliate_link IS 'Link di affiliate per il broker';
COMMENT ON COLUMN broker_links.is_active IS 'Stato attivo/inattivo del link';
COMMENT ON COLUMN broker_links.created_by IS 'ID dell''utente che ha creato il link';
