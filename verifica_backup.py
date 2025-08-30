#!/usr/bin/env python3
import json

with open('supabase_backup_20250830_114154.json', 'r') as f:
    data = json.load(f)

print("=== STRUTTURA SUPABASE DAL BACKUP ===")
if data:
    print(f"Clienti nel backup: {len(data)}")
    print(f"Colonne: {list(data[0].keys())}")
    
    print("\nPrimo cliente:")
    for key, value in data[0].items():
        print(f"  {key}: {value}")
else:
    print("Backup vuoto")
