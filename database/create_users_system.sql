-- 🚀 CREAZIONE SISTEMA GESTIONE UTENTI COMPLETO
-- Esegui questo script nel SQL Editor di Supabase

-- 1. TABELLA UTENTI PRINCIPALE
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'manager', 'user')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. TABELLA RUOLI UTENTE
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. TABELLA PERMESSI
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(50) NOT NULL, -- 'clienti', 'incroci', 'users', etc.
    action VARCHAR(20) NOT NULL,   -- 'create', 'read', 'update', 'delete'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. TABELLA SESSIONI UTENTE
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. TABELLA PROFILI UTENTE (estensione)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    avatar_url TEXT,
    phone VARCHAR(20),
    address TEXT,
    preferences JSONB DEFAULT '{}',
    timezone VARCHAR(50) DEFAULT 'Europe/Rome',
    language VARCHAR(10) DEFAULT 'it',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. TABELLA LOG ACCESSI
CREATE TABLE IF NOT EXISTS user_access_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- 'login', 'logout', 'failed_login', 'password_change'
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT true,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. TABELLA TENTATIVI LOGIN FALLITI
CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    attempt_count INTEGER DEFAULT 1,
    first_attempt TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_attempt TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_blocked BOOLEAN DEFAULT false,
    blocked_until TIMESTAMP WITH TIME ZONE
);

-- INDICI PER PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON user_access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_action ON user_access_logs(action);
CREATE INDEX IF NOT EXISTS idx_access_logs_created ON user_access_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_failed_login_username ON failed_login_attempts(username);
CREATE INDEX IF NOT EXISTS idx_failed_login_ip ON failed_login_attempts(ip_address);

-- FUNZIONI DI UTILITÀ
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- TRIGGER PER AGGIORNAMENTO AUTOMATICO updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- FUNZIONE PER CREAZIONE UTENTE COMPLETO
CREATE OR REPLACE FUNCTION create_user_complete(
    p_username VARCHAR(50),
    p_email VARCHAR(100),
    p_password_hash VARCHAR(255),
    p_full_name VARCHAR(100),
    p_role VARCHAR(20) DEFAULT 'user'
)
RETURNS UUID AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Inserisci utente
    INSERT INTO users (username, email, password_hash, full_name, role)
    VALUES (p_username, p_email, p_password_hash, p_full_name, p_role)
    RETURNING id INTO v_user_id;
    
    -- Crea profilo utente
    INSERT INTO user_profiles (user_id)
    VALUES (v_user_id);
    
    -- Log creazione
    INSERT INTO user_access_logs (user_id, action, success, details)
    VALUES (v_user_id, 'user_created', true, jsonb_build_object('role', p_role));
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

-- INSERIMENTO DATI DI DEFAULT

-- 1. Inserisci ruoli predefiniti
INSERT INTO user_roles (role_name, description, permissions) VALUES
('admin', 'Amministratore completo del sistema', '["*"]'),
('manager', 'Manager con accesso esteso', '["clienti:read", "clienti:update", "incroci:read", "incroci:update"]'),
('user', 'Utente base con accesso limitato', '["clienti:read", "incroci:read"]')
ON CONFLICT (role_name) DO NOTHING;

-- 2. Inserisci permessi base
INSERT INTO user_permissions (permission_name, description, resource, action) VALUES
('clienti:create', 'Creare nuovi clienti', 'clienti', 'create'),
('clienti:read', 'Visualizzare clienti', 'clienti', 'read'),
('clienti:update', 'Modificare clienti', 'clienti', 'update'),
('clienti:delete', 'Eliminare clienti', 'clienti', 'delete'),
('incroci:create', 'Creare nuovi incroci', 'incroci', 'create'),
('incroci:read', 'Visualizzare incroci', 'incroci', 'read'),
('incroci:update', 'Modificare incroci', 'incroci', 'update'),
('incroci:delete', 'Eliminare incroci', 'incroci', 'delete'),
('users:create', 'Creare nuovi utenti', 'users', 'create'),
('users:read', 'Visualizzare utenti', 'users', 'read'),
('users:update', 'Modificare utenti', 'users', 'update'),
('users:delete', 'Eliminare utenti', 'users', 'delete')
ON CONFLICT (permission_name) DO NOTHING;

-- 3. Inserisci utente admin di default (password: admin123)
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@cpadashboard.com', '$2b$12$riBfpHpVpccsb7NT7GFIRObLccRmnOiOtsSx65wbMb3C6Cuy/mDfu', 'Amministratore CPA Dashboard', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 4. Crea profilo per admin
INSERT INTO user_profiles (user_id)
SELECT id FROM users WHERE username = 'admin'
ON CONFLICT (user_id) DO NOTHING;

-- POLITICHE RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE failed_login_attempts ENABLE ROW LEVEL SECURITY;

-- POLITICHE RLS PER UTENTI
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Admins can view all users" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = current_setting('request.jwt.claims', true)::json->>'username'
            AND role = 'admin'
        )
    );

-- POLITICHE RLS PER RUOLI
CREATE POLICY "All authenticated users can view roles" ON user_roles
    FOR SELECT USING (auth.role() = 'authenticated');

-- POLITICHE RLS PER PERMESSI
CREATE POLICY "All authenticated users can view permissions" ON user_permissions
    FOR SELECT USING (auth.role() = 'authenticated');

-- POLITICHE RLS PER SESSIONI
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- POLITICHE RLS PER PROFILI
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- MESSAGGIO DI SUCCESSO
DO $$
BEGIN
    RAISE NOTICE '✅ SISTEMA GESTIONE UTENTI CREATO CON SUCCESSO!';
    RAISE NOTICE '📊 Tabelle create: users, user_roles, user_permissions, user_sessions, user_profiles, user_access_logs, failed_login_attempts';
    RAISE NOTICE '👑 Utente admin creato: admin/admin123';
    RAISE NOTICE '🔒 RLS attivato per tutte le tabelle';
    RAISE NOTICE '🚀 Sistema pronto per l''uso!';
END $$;
