-- NUOVO SCHEMA DATABASE RAGGRUPPATO
-- Separa dati base cliente dagli account broker
-- Permette email duplicate per broker diversi

-- Tabella CLIENTI BASE (dati comuni)
CREATE TABLE IF NOT EXISTS clienti_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT NOT NULL,
    email TEXT NOT NULL,
    vps TEXT,
    note_cliente TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella ACCOUNT BROKER (account specifici per broker)
CREATE TABLE IF NOT EXISTS account_broker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_base_id INTEGER NOT NULL,
    broker TEXT NOT NULL,
    piattaforma TEXT DEFAULT 'MT4',
    numero_conto TEXT NOT NULL,
    password TEXT NOT NULL,
    api_key TEXT,
    secret_key TEXT,
    ip_address TEXT,
    volume_posizione REAL DEFAULT 0,
    ruolo TEXT DEFAULT 'User',
    stato_account TEXT DEFAULT 'attivo',
    data_registrazione DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_base_id) REFERENCES clienti_base(id) ON DELETE CASCADE
);

-- Tabella incroci (mantenuta come prima)
CREATE TABLE IF NOT EXISTS incroci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_apertura DATE NOT NULL,
    data_chiusura DATE,
    stato TEXT DEFAULT 'aperto',
    profitto_perdita REAL DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella incroci_account (mantenuta come esistente per compatibilità)
CREATE TABLE IF NOT EXISTS incroci_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incrocio_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    tipo_posizione TEXT NOT NULL CHECK (tipo_posizione IN ('long', 'short')),
    broker TEXT NOT NULL,
    piattaforma TEXT DEFAULT 'MT4',
    numero_conto TEXT,
    volume_posizione REAL DEFAULT 0,
    data_apertura_posizione DATE,
    data_chiusura_posizione DATE,
    stato_posizione TEXT,
    note_posizione TEXT,
    FOREIGN KEY (incrocio_id) REFERENCES incroci(id)
);

-- Tabella incroci_bonus (mantenuta come prima)
CREATE TABLE IF NOT EXISTS incroci_bonus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incrocio_id INTEGER NOT NULL,
    importo_bonus REAL NOT NULL,
    data_bonus DATE NOT NULL,
    note TEXT,
    FOREIGN KEY (incrocio_id) REFERENCES incroci(id)
);

-- Tabella broker (mantenuta come prima)
CREATE TABLE IF NOT EXISTS broker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_broker TEXT UNIQUE NOT NULL,
    sito_web TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella piattaforme (mantenuta come prima)
CREATE TABLE IF NOT EXISTS piattaforme (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_piattaforma TEXT UNIQUE NOT NULL,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella campi_aggiuntivi (mantenuta come prima)
CREATE TABLE IF NOT EXISTS campi_aggiuntivi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_campo TEXT NOT NULL,
    tipo_campo TEXT NOT NULL,
    obbligatorio BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserimento dati di base (NON sensibili)
INSERT OR IGNORE INTO broker (nome_broker, sito_web, note) VALUES 
('Ultima Markets', 'https://ultimamarkets.com', 'Broker CFD'),
('Axi', 'https://axi.com', 'Forex e CFD'),
('FXCM', 'https://fxcm.com', 'Forex e CFD'),
('IG Markets', 'https://ig.com', 'Trading online'),
('eToro', 'https://etoro.com', 'Social trading'),
('Plus500', 'https://plus500.com', 'Trading CFD');

INSERT OR IGNORE INTO piattaforme (nome_piattaforma, descrizione) VALUES 
('MT4', 'MetaTrader 4'),
('MT5', 'MetaTrader 5'),
('cTrader', 'cTrader Platform'),
('WebTrader', 'Trading web'),
('Mobile App', 'App mobile');

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_clienti_base_email ON clienti_base(email);
CREATE INDEX IF NOT EXISTS idx_clienti_base_nome ON clienti_base(nome_cliente);
CREATE INDEX IF NOT EXISTS idx_account_broker_cliente ON account_broker(cliente_base_id);
CREATE INDEX IF NOT EXISTS idx_account_broker_broker ON account_broker(broker);
CREATE INDEX IF NOT EXISTS idx_account_broker_conto ON account_broker(numero_conto);
CREATE INDEX IF NOT EXISTS idx_incroci_data ON incroci(data_apertura);
CREATE INDEX IF NOT EXISTS idx_incroci_stato ON incroci(stato);
CREATE INDEX IF NOT EXISTS idx_incroci_account_incrocio ON incroci_account(incrocio_id);
CREATE INDEX IF NOT EXISTS idx_incroci_account_account ON incroci_account(account_id);

-- VISTA PER FACILITARE QUERY (opzionale)
CREATE VIEW IF NOT EXISTS v_clienti_completi AS
SELECT 
    cb.id as cliente_id,
    cb.nome_cliente,
    cb.email,
    cb.vps,
    ab.id as account_id,
    ab.broker,
    ab.piattaforma,
    ab.numero_conto,
    ab.volume_posizione,
    ab.stato_account,
    ab.data_registrazione
FROM clienti_base cb
LEFT JOIN account_broker ab ON cb.id = ab.cliente_base_id
ORDER BY cb.nome_cliente, ab.broker;
