-- 🚀 AGGIUNTA COLONNA WALLET - Dashboard Gestione CPA
-- Script per aggiungere il campo wallet alla tabella clienti su Supabase

-- Aggiungi colonna wallet alla tabella clienti
ALTER TABLE clienti 
ADD COLUMN wallet TEXT;

-- Commento per documentare la colonna
COMMENT ON COLUMN clienti.wallet IS 'Indirizzo wallet del cliente';

-- Verifica che la colonna sia stata aggiunta
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'clienti' AND column_name = 'wallet';
