-- Schema Database Dashboard Gestione CPA
-- Questo file contiene la struttura completa del database

-- Tabella principale clienti
CREATE TABLE IF NOT EXISTS clienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT NOT NULL,
    email TEXT NOT NULL,
    password_email TEXT,
    broker TEXT NOT NULL,
    data_registrazione DATE NOT NULL,
    deposito REAL NOT NULL,
    piattaforma TEXT NOT NULL,
    numero_conto TEXT NOT NULL,
    password_conto TEXT,
    vps_ip TEXT,
    vps_username TEXT,
    vps_password TEXT,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per i campi aggiuntivi dinamici
CREATE TABLE IF NOT EXISTS campi_aggiuntivi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    nome_campo TEXT NOT NULL,
    valore_campo TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clienti (id) ON DELETE CASCADE
);

-- Tabella per i broker
CREATE TABLE IF NOT EXISTS broker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_broker TEXT UNIQUE NOT NULL,
    sito_web TEXT,
    note TEXT
);

-- Tabella per le piattaforme
CREATE TABLE IF NOT EXISTS piattaforme (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_piattaforma TEXT UNIQUE NOT NULL,
    descrizione TEXT
);

-- Inserimento dati di default per le piattaforme
INSERT OR IGNORE INTO piattaforme (nome_piattaforma, descrizione) VALUES
    ("MT4", "MetaTrader 4"),
    ("MT5", "MetaTrader 5"),
    ("cTrader", "cTrader"),
    ("NinjaTrader", "NinjaTrader"),
    ("TradingView", "TradingView"),
    ("ProRealTime", "ProRealTime"),
    ("MetaStock", "MetaStock"),
    ("Amibroker", "Amibroker"),
    ("Altro", "Altra piattaforma");

-- Inserimento broker di esempio
INSERT OR IGNORE INTO broker (nome_broker, sito_web, note) VALUES
    ("FXPro", "https://www.fxpro.com", "Broker regolamentato CySEC"),
    ("Pepperstone", "https://www.pepperstone.com", "Broker australiano"),
    ("IC Markets", "https://www.icmarkets.com", "Broker con spread bassi"),
    ("AvaTrade", "https://www.avatrade.com", "Broker irlandese"),
    ("Plus500", "https://www.plus500.com", "Broker CFD"),
    ("eToro", "https://www.etoro.com", "Social trading"),
    ("IG Group", "https://www.ig.com", "Broker britannico"),
    ("CMC Markets", "https://www.cmcmarkets.com", "Broker CFD"),
    ("Saxo Bank", "https://www.saxobank.com", "Banca di investimento"),
    ("Interactive Brokers", "https://www.interactivebrokers.com", "Broker USA");

-- Indici per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_clienti_broker ON clienti(broker);
CREATE INDEX IF NOT EXISTS idx_clienti_piattaforma ON clienti(piattaforma);
CREATE INDEX IF NOT EXISTS idx_clienti_data_registrazione ON clienti(data_registrazione);
CREATE INDEX IF NOT EXISTS idx_clienti_email ON clienti(email);
CREATE INDEX IF NOT EXISTS idx_campi_aggiuntivi_cliente_id ON campi_aggiuntivi(cliente_id);

-- Trigger per aggiornare automaticamente data_modifica
CREATE TRIGGER IF NOT EXISTS update_clienti_modifica
    AFTER UPDATE ON clienti
    FOR EACH ROW
BEGIN
    UPDATE clienti SET data_modifica = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Vista per statistiche rapide
CREATE VIEW IF NOT EXISTS v_statistiche_clienti AS
SELECT 
    COUNT(*) as totale_clienti,
    COUNT(DISTINCT broker) as broker_attivi,
    SUM(deposito) as depositi_totali,
    COUNT(CASE WHEN deposito > 0 THEN 1 END) as cpa_attive,
    AVG(deposito) as deposito_medio,
    MIN(deposito) as deposito_min,
    MAX(deposito) as deposito_max
FROM clienti;

-- Vista per clienti con campi aggiuntivi
CREATE VIEW IF NOT EXISTS v_clienti_completi AS
SELECT 
    c.*,
    GROUP_CONCAT(ca.nome_campo || ': ' || ca.valore_campo, '; ') as campi_aggiuntivi
FROM clienti c
LEFT JOIN campi_aggiuntivi ca ON c.id = ca.cliente_id
GROUP BY c.id;

-- Vista per statistiche per broker
CREATE VIEW IF NOT EXISTS v_statistiche_broker AS
SELECT 
    broker,
    COUNT(*) as numero_clienti,
    SUM(deposito) as depositi_totali,
    AVG(deposito) as deposito_medio,
    MIN(deposito) as deposito_min,
    MAX(deposito) as deposito_max
FROM clienti
GROUP BY broker
ORDER BY numero_clienti DESC;

-- Vista per statistiche per piattaforma
CREATE VIEW IF NOT EXISTS v_statistiche_piattaforma AS
SELECT 
    piattaforma,
    COUNT(*) as numero_clienti,
    SUM(deposito) as depositi_totali,
    AVG(deposito) as deposito_medio
FROM clienti
GROUP BY piattaforma
ORDER BY numero_clienti DESC;

-- Vista per trend mensili
CREATE VIEW IF NOT EXISTS v_trend_mensili AS
SELECT 
    strftime('%Y-%m', data_registrazione) as mese,
    COUNT(*) as nuovi_clienti,
    SUM(deposito) as depositi_mensili
FROM clienti
GROUP BY strftime('%Y-%m', data_registrazione)
ORDER BY mese DESC;

-- Commenti sulle tabelle
PRAGMA table_info(clienti);
PRAGMA table_info(campi_aggiuntivi);
PRAGMA table_info(broker);
PRAGMA table_info(piattaforme);

-- Informazioni sui trigger
SELECT name, sql FROM sqlite_master WHERE type = 'trigger';

-- Informazioni sulle viste
SELECT name, sql FROM sqlite_master WHERE type = 'view';
