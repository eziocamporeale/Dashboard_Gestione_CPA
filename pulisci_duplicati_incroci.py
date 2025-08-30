#!/usr/bin/env python3
"""
Script per pulire i duplicati degli incroci e mantenere solo i 5 originali
"""

from supabase_manager import SupabaseManager
from collections import Counter

def pulisci_duplicati_incroci():
    print("=== 🧹 PULIZIA DUPLICATI INCROCI ===")
    
    try:
        # 1. Connessione a Supabase
        sb = SupabaseManager()
        
        # 2. Recupera tutti gli incroci
        incroci = sb.get_incroci()
        print(f"📊 Incroci totali prima pulizia: {len(incroci)}")
        
        # 3. Analizza duplicati
        nomi = [c['nome_incrocio'] for c in incroci]
        counter = Counter(nomi)
        print("📋 Analisi duplicati:")
        for nome, count in counter.items():
            print(f"  - {nome}: {count} volte")
        
        # 4. Identifica i duplicati da eliminare
        da_eliminare = []
        incroci_per_nome = {}
        
        for incrocio in incroci:
            nome = incrocio['nome_incrocio']
            if nome not in incroci_per_nome:
                incroci_per_nome[nome] = []
            incroci_per_nome[nome].append(incrocio)
        
        # 5. Mantieni solo i primi per ogni nome
        for nome, lista_incroci in incroci_per_nome.items():
            if nome == "EURUSD Agosto":
                # Mantieni solo 1 EURUSD Agosto
                da_eliminare.extend(lista_incroci[1:])
            elif nome == "GBPUSD Agosto":
                # Mantieni solo 2 GBPUSD Agosto
                da_eliminare.extend(lista_incroci[2:])
        
        print(f"🗑️ Incroci da eliminare: {len(da_eliminare)}")
        
        # 6. Elimina i duplicati
        eliminati = 0
        for incrocio in da_eliminare:
            incrocio_id = incrocio['id']
            print(f"🔄 Eliminazione incrocio {incrocio['nome_incrocio']} (ID: {incrocio_id})...")
            
            # Elimina prima gli account associati
            result = sb.supabase.table('incroci_account').delete().eq('incrocio_id', incrocio_id).execute()
            print(f"  ✅ Account eliminati")
            
            # Elimina i bonus associati
            result = sb.supabase.table('incroci_bonus').delete().eq('incrocio_id', incrocio_id).execute()
            print(f"  ✅ Bonus eliminati")
            
            # Elimina l'incrocio
            result = sb.supabase.table('incroci').delete().eq('id', incrocio_id).execute()
            if result.data:
                print(f"  ✅ Incrocio eliminato")
                eliminati += 1
            else:
                print(f"  ❌ Errore eliminazione incrocio")
        
        print(f"🎉 PULIZIA COMPLETATA! Eliminati {eliminati} incroci duplicati")
        
        # 7. Verifica finale
        incroci_finali = sb.get_incroci()
        print(f"📊 Incroci totali dopo pulizia: {len(incroci_finali)}")
        print("📋 Lista finale:")
        for incrocio in incroci_finali:
            print(f"  - {incrocio['nome_incrocio']} ({incrocio['pair_trading']}) - {incrocio['stato']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la pulizia: {e}")
        return False

if __name__ == "__main__":
    pulisci_duplicati_incroci()
