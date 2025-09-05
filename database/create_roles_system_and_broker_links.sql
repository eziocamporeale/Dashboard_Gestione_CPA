-- Implementazione sistema ruoli e tabella broker_links per Dashboard Gestione CPA
-- Creato da Ezio Camporeale - Adattato dalla struttura DASH_GESTIONE_LEAD

-- ==================== SISTEMA RUOLI ====================

-- Tabella ruoli utenti (come nel progetto LEAD)
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Modifica tabella users esistente per aggiungere role_id
-- Prima aggiungiamo la colonna role_id se non esiste
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'role_id') THEN
        ALTER TABLE users ADD COLUMN role_id INTEGER REFERENCES roles(id);
    END IF;
END $$;

-- Aggiungiamo anche first_name e last_name se non esistono
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'first_name') THEN
        ALTER TABLE users ADD COLUMN first_name VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'last_name') THEN
        ALTER TABLE users ADD COLUMN last_name VARCHAR(50);
    END IF;
END $$;

-- ==================== TABELLA BROKER_LINKS ====================

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

-- ==================== TRIGGER E FUNZIONI ====================

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

-- Trigger per aggiornare updated_at su roles
CREATE OR REPLACE FUNCTION update_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_roles_updated_at();

-- ==================== ROW LEVEL SECURITY (RLS) ====================

-- Abilita RLS
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE broker_links ENABLE ROW LEVEL SECURITY;

-- Politica per accesso completo (admin e manager) - usando la struttura LEAD
CREATE POLICY "Admin and Manager full access" ON broker_links
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id::text = auth.uid()::text
            AND r.name IN ('Admin', 'Manager')
        )
    );

-- Politica per lettura (tutti gli utenti autenticati)
CREATE POLICY "Authenticated users read access" ON broker_links
    FOR SELECT USING (
        auth.uid() IS NOT NULL
    );

-- Politiche per la tabella roles
CREATE POLICY "Admin full access roles" ON roles FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.id::text = auth.uid()::text
        AND r.name = 'Admin'
    )
);

CREATE POLICY "Authenticated users read roles" ON roles FOR SELECT USING (
    auth.uid() IS NOT NULL
);

-- ==================== DATI DI DEFAULT ====================

-- Inserimento ruoli di default (come nel progetto LEAD)
INSERT INTO roles (name, description, permissions) VALUES
('Admin', 'Amministratore completo del sistema', '["all"]'),
('Manager', 'Manager con permessi di gestione team', '["manage_clients", "manage_team", "view_reports"]'),
('User', 'Utente standard con permessi limitati', '["view_clients", "view_reports"]')
ON CONFLICT (name) DO NOTHING;

-- Aggiorna utenti esistenti per assegnare ruolo Admin se hanno role='admin'
UPDATE users 
SET role_id = (SELECT id FROM roles WHERE name = 'Admin')
WHERE role = 'admin' AND role_id IS NULL;

-- Aggiorna utenti esistenti per assegnare ruolo Manager se hanno role='manager'
UPDATE users 
SET role_id = (SELECT id FROM roles WHERE name = 'Manager')
WHERE role = 'manager' AND role_id IS NULL;

-- Aggiorna utenti esistenti per assegnare ruolo User se hanno role='user'
UPDATE users 
SET role_id = (SELECT id FROM roles WHERE name = 'User')
WHERE role = 'user' AND role_id IS NULL;

-- ==================== COMMENTI PER DOCUMENTAZIONE ====================

COMMENT ON TABLE roles IS 'Tabella per gestione ruoli utenti del sistema';
COMMENT ON COLUMN roles.name IS 'Nome del ruolo';
COMMENT ON COLUMN roles.description IS 'Descrizione del ruolo';
COMMENT ON COLUMN roles.permissions IS 'Permessi del ruolo in formato JSON';

COMMENT ON TABLE broker_links IS 'Tabella per gestione link di affiliate dei broker';
COMMENT ON COLUMN broker_links.broker_name IS 'Nome del broker';
COMMENT ON COLUMN broker_links.affiliate_link IS 'Link di affiliate per il broker';
COMMENT ON COLUMN broker_links.is_active IS 'Stato attivo/inattivo del link';
COMMENT ON COLUMN broker_links.created_by IS 'ID dell''utente che ha creato il link';
