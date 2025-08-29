-- Script di inizializzazione database per Streamlit Cloud
-- Contiene solo la struttura delle tabelle, ZERO dati sensibili

-- Tabella clienti
CREATE TABLE IF NOT EXISTS clienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    broker TEXT NOT NULL,
    data_registrazione DATE NOT NULL,
    volume_posizione REAL DEFAULT 0,
    piattaforma TEXT DEFAULT 'MT4',
    numero_conto TEXT,
    api_key TEXT,
    ip_address TEXT,
    ruolo TEXT DEFAULT 'User',
    secret_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella incroci
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

-- Tabella incroci_account
CREATE TABLE IF NOT EXISTS incroci_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incrocio_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    tipo_posizione TEXT NOT NULL CHECK (tipo_posizione IN ('long', 'short')),
    broker TEXT NOT NULL,
    piattaforma TEXT DEFAULT 'MT4',
    numero_conto TEXT,
    volume_posizione REAL DEFAULT 0,
    FOREIGN KEY (incrocio_id) REFERENCES incroci(id),
    FOREIGN KEY (account_id) REFERENCES clienti(id)
);

-- Tabella incroci_bonus
CREATE TABLE IF NOT EXISTS incroci_bonus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incrocio_id INTEGER NOT NULL,
    importo_bonus REAL NOT NULL,
    data_bonus DATE NOT NULL,
    note TEXT,
    FOREIGN KEY (incrocio_id) REFERENCES incroci(id)
);

-- Tabella broker
CREATE TABLE IF NOT EXISTS broker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella piattaforme
CREATE TABLE IF NOT EXISTS piattaforme (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella campi_aggiuntivi
CREATE TABLE IF NOT EXISTS campi_aggiuntivi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_campo TEXT NOT NULL,
    tipo_campo TEXT NOT NULL,
    obbligatorio BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserimento dati di base (NON sensibili)
INSERT OR IGNORE INTO broker (nome, descrizione) VALUES 
('Ultima Markets', 'Broker CFD'),
('FXCM', 'Forex e CFD'),
('IG Markets', 'Trading online'),
('eToro', 'Social trading'),
('Plus500', 'Trading CFD');

INSERT OR IGNORE INTO piattaforme (nome, descrizione) VALUES 
('MT4', 'MetaTrader 4'),
('MT5', 'MetaTrader 5'),
('cTrader', 'cTrader Platform'),
('WebTrader', 'Trading web'),
('Mobile App', 'App mobile');

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_clienti_email ON clienti(email);
CREATE INDEX IF NOT EXISTS idx_clienti_broker ON clienti(broker);
CREATE INDEX IF NOT EXISTS idx_incroci_data ON incroci(data_apertura);
CREATE INDEX IF NOT EXISTS idx_incroci_stato ON incroci(stato);
CREATE INDEX IF NOT EXISTS idx_incroci_account_incrocio ON incroci_account(incrocio_id);
CREATE INDEX IF NOT EXISTS idx_incroci_account_account ON incroci_account(account_id);
