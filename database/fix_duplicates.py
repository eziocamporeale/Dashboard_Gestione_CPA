#!/usr/bin/env python3
"""
Script per correggere i duplicati creati durante la migrazione
Consolida clienti con email identica in un unico cliente base
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_duplicate_clients():
    """Corregge i clienti duplicati"""
    try:
        conn = sqlite3.connect('cpa_database.db')
        cursor = conn.cursor()
        
        print("🔧 CORREZIONE CLIENTI DUPLICATI")
        print("=" * 50)
        
        # 1. Trova clienti con email duplicata
        cursor.execute("""
            SELECT email, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM clienti_base 
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("✅ Nessun duplicato trovato!")
            return
        
        print(f"📋 Trovati {len(duplicates)} gruppi di duplicati:")
        
        for email, count, ids in duplicates:
            print(f"   • Email: {email} - {count} duplicati")
            id_list = [int(x) for x in ids.split(',')]
            
            # 2. Mantieni il primo cliente (ID più basso)
            main_client_id = min(id_list)
            duplicate_ids = [x for x in id_list if x != main_client_id]
            
            print(f"     Mantengo cliente ID: {main_client_id}")
            print(f"     Elimino duplicati ID: {duplicate_ids}")
            
            # 3. Sposta tutti gli account dei duplicati al cliente principale
            for dup_id in duplicate_ids:
                cursor.execute("""
                    UPDATE account_broker 
                    SET cliente_base_id = ? 
                    WHERE cliente_base_id = ?
                """, (main_client_id, dup_id))
                
                print(f"       ✅ Account spostati da {dup_id} a {main_client_id}")
            
            # 4. Elimina i clienti duplicati
            for dup_id in duplicate_ids:
                cursor.execute("DELETE FROM clienti_base WHERE id = ?", (dup_id,))
                print(f"       ✅ Cliente duplicato {dup_id} eliminato")
            
            # 5. Aggiorna nome del cliente principale se necessario
            cursor.execute("""
                SELECT nome_cliente FROM clienti_base WHERE id = ?
            """, (main_client_id,))
            
            current_name = cursor.fetchone()[0]
            if " - " in current_name:
                # Rimuovi suffisso broker dal nome
                clean_name = current_name.split(" - ")[0]
                cursor.execute("""
                    UPDATE clienti_base 
                    SET nome_cliente = ? 
                    WHERE id = ?
                """, (clean_name, main_client_id))
                print(f"       ✅ Nome cliente pulito: {clean_name}")
        
        # 6. Commit e verifica
        conn.commit()
        
        # Verifica finale
        cursor.execute("SELECT COUNT(*) FROM clienti_base")
        final_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM account_broker")
        final_accounts = cursor.fetchone()[0]
        
        print(f"\n📊 VERIFICA FINALE:")
        print(f"   • Clienti base: {final_count}")
        print(f"   • Account broker: {final_accounts}")
        
        conn.close()
        
        print("\n🎉 CORREZIONE COMPLETATA!")
        
    except Exception as e:
        logger.error(f"❌ Errore correzione duplicati: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def show_final_structure():
    """Mostra la struttura finale corretta"""
    try:
        from database.database_grouped import GroupedDatabaseManager
        
        print("\n🔍 STRUTTURA FINALE CORRETTA")
        print("=" * 50)
        
        db = GroupedDatabaseManager()
        
        # Statistiche
        stats = db.ottieni_statistiche()
        print(f"📊 STATISTICHE:")
        print(f"   • Clienti base: {stats['totale_clienti']}")
        print(f"   • Account broker: {stats['totale_account']}")
        print(f"   • Broker attivi: {stats['broker_attivi']}")
        
        # Clienti completi
        print(f"\n👥 CLIENTI COMPLETI:")
        clienti_completi = db.ottieni_tutti_clienti_completi()
        
        for cliente in clienti_completi:
            print(f"\n👤 {cliente['nome_cliente']} ({cliente['email']}):")
            if cliente['vps']:
                print(f"   🖥️ VPS: {cliente['vps']}")
            
            for account in cliente['accounts']:
                print(f"   🏦 {account['broker']} - Conto: {account['numero_conto']} ({account['piattaforma']})")
                if account['volume_posizione']:
                    print(f"      💰 Volume: {account['volume_posizione']}")
        
    except Exception as e:
        print(f"❌ Errore visualizzazione: {e}")

if __name__ == "__main__":
    print("🚀 CORREZIONE DUPLICATI POST-MIGRAZIONE")
    print("=" * 60)
    
    # Esegui correzione
    fix_duplicate_clients()
    
    # Mostra struttura finale
    show_final_structure()
