-- 🚀 CREAZIONE TABELLE UTENTI PER SISTEMA DI AUTENTICAZIONE AVANZATO
-- Esegui questo script nel SQL Editor di Supabase

-- 1. Tabella utenti principale
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'manager', 'user')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabella sessioni utente
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabella permessi utente
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(50) NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    UNIQUE(user_id, permission)
);

-- 4. Tabella tentativi di login falliti (per rate limiting)
CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    ip_address INET,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT
);

-- 5. Indici per performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_failed_login_username ON failed_login_attempts(username);
CREATE INDEX IF NOT EXISTS idx_failed_login_attempted_at ON failed_login_attempts(attempted_at);

-- 6. Funzione per aggiornare timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 7. Trigger per aggiornare timestamp
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 8. Funzione per pulire sessioni scadute
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ language 'plpgsql';

-- 9. Funzione per pulire tentativi di login vecchi
CREATE OR REPLACE FUNCTION cleanup_old_failed_attempts()
RETURNS void AS $$
BEGIN
    DELETE FROM failed_login_attempts WHERE attempted_at < NOW() - INTERVAL '15 minutes';
END;
$$ language 'plpgsql';

-- 10. Inserimento utente admin di default (password: admin123 - CAMBIALA!)
INSERT INTO users (username, email, password_hash, full_name, role) 
VALUES (
    'admin', 
    'admin@cpadashboard.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO6e', -- admin123
    'Amministratore CPA Dashboard',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- 11. Inserimento permessi admin
INSERT INTO user_permissions (user_id, permission, granted_by)
SELECT id, 'read', id FROM users WHERE username = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO user_permissions (user_id, permission, granted_by)
SELECT id, 'write', id FROM users WHERE username = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO user_permissions (user_id, permission, granted_by)
SELECT id, 'delete', id FROM users WHERE username = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO user_permissions (user_id, permission, granted_by)
SELECT id, 'admin', id FROM users WHERE username = 'admin'
ON CONFLICT DO NOTHING;

-- 12. Commenti per documentazione
COMMENT ON TABLE users IS 'Tabella principale per gestione utenti del sistema CPA';
COMMENT ON TABLE user_sessions IS 'Gestione sessioni utente attive';
COMMENT ON TABLE user_permissions IS 'Permessi specifici per ogni utente';
COMMENT ON TABLE failed_login_attempts IS 'Tracciamento tentativi di login falliti per sicurezza';

-- 13. Politiche RLS (Row Level Security) - IMPORTANTE!
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE failed_login_attempts ENABLE ROW LEVEL SECURITY;

-- 14. Politiche per utenti (solo admin può vedere tutti)
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id OR auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admin can manage all users" ON users
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- 15. Politiche per sessioni
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id OR auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can manage own sessions" ON user_sessions
    FOR ALL USING (auth.uid() = user_id OR auth.jwt() ->> 'role' = 'admin');

-- 16. Politiche per permessi
CREATE POLICY "Users can view own permissions" ON user_permissions
    FOR SELECT USING (auth.uid() = user_id OR auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can manage all permissions" ON user_permissions
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- 17. Politiche per tentativi falliti (solo admin)
CREATE POLICY "Admin can view failed attempts" ON failed_login_attempts
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "System can insert failed attempts" ON failed_login_attempts
    FOR INSERT WITH CHECK (true);

-- 18. Messaggio di completamento
DO $$
BEGIN
    RAISE NOTICE '🎉 TABELLE UTENTI CREATE CON SUCCESSO!';
    RAISE NOTICE '✅ Sistema di autenticazione pronto per l''uso';
    RAISE NOTICE '⚠️ IMPORTANTE: Cambia la password dell''admin di default!';
    RAISE NOTICE '🔐 Username: admin, Password: admin123 (CAMBIALA!)';
END $$;
