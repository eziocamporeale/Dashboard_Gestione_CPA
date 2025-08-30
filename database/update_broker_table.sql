-- Script per aggiornare la tabella broker con i nuovi broker
-- Eseguire questo script per sincronizzare i broker su Streamlit Cloud

-- Svuota la tabella broker esistente
DELETE FROM broker;

-- Inserisci i nuovi broker
INSERT INTO broker (nome_broker, sito_web, note) VALUES 
('Ultima Markets', 'https://ultimamarkets.com', 'Broker CFD'),
('Puprime', 'https://puprime.com', 'Forex e CFD'),
('Axi', 'https://axi.com', 'Forex e CFD'),
('AvaTrade', 'https://avatrade.com', 'Trading online'),
('Global Prime', 'https://globalprime.com', 'Forex e CFD'),
('FxCess', 'https://fxcess.com', 'Forex e CFD'),
('Vtmarkets', 'https://vtmarkets.com', 'Trading online'),
('Tauro Markets', 'https://tauromarkets.com', 'Forex e CFD'),
('FPG', 'https://fpg.com', 'Trading online'),
('TMGM', 'https://tmgm.com', 'Forex e CFD');

-- Verifica l'inserimento
SELECT 'Broker aggiornati:' as status, COUNT(*) as totale FROM broker;
SELECT nome_broker, sito_web, note FROM broker ORDER BY id;
