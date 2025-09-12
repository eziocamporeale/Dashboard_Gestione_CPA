#!/usr/bin/env python3
"""
Storage Manager per Dashboard Gestione CPA
Gestione completa dei file con permessi differenziati
Creato da Ezio Camporeale per Dashboard Gestione CPA
"""

import os
import uuid
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import streamlit as st
from supabase import create_client, Client
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from supabase_manager import SupabaseManager

class StorageManager:
    """
    Gestore per l'upload, download e gestione dei file nel sistema storage
    Ottimizzato per Dashboard Gestione CPA
    """
    
    def __init__(self):
        """Inizializza il manager dello storage"""
        self.supabase_manager = SupabaseManager()
        self.supabase = self.supabase_manager.supabase
        self.storage_dir = Path(current_dir) / "storage" / "uploads"
        self.temp_dir = Path(current_dir) / "storage" / "temp"
        
        # Crea le directory se non esistono
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Categorie specifiche per CPA
        self.categories = {
            'EA Trading': ['ex4', 'ex5', 'mq4', 'mq5'],
            'Backtest': ['ex4', 'ex5', 'mq4', 'mq5', 'pdf', 'xlsx', 'csv'],
            'Gold Supreme EA': ['ex4', 'ex5', 'mq4', 'mq5'],
            'Backtest EA': ['ex4', 'ex5', 'mq4', 'mq5'],
            'Documenti Broker': ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'],
            'Report CPA': ['pdf', 'xlsx', 'xls', 'docx', 'doc'],
            'Documenti Legali': ['pdf', 'doc', 'docx', 'txt'],
            'Materiale Marketing': ['mp4', 'avi', 'mov', 'ppt', 'pptx', 'pdf', 'jpg', 'png'],
            'Analisi': ['pdf', 'xlsx', 'xls', 'csv', 'png', 'jpg'],
            'Archivi': ['zip', 'rar', '7z', 'tar', 'gz'],
            'Fogli di Calcolo': ['xls', 'xlsx', 'csv', 'ods'],
            'Presentazioni': ['ppt', 'pptx', 'odp'],
            'Immagini': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'],
            'Video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
            'Audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
            'Altro': []
        }
    
    def get_file_category(self, filename: str) -> str:
        """
        Determina la categoria di un file basandosi sull'estensione e sul nome
        Ottimizzato per contesto CPA
        
        Args:
            filename: Nome del file
            
        Returns:
            str: Categoria del file
        """
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        filename_lower = filename.lower()
        
        # Categorie speciali per file MQL4/MQL5
        if extension in ['ex4', 'ex5', 'mq4', 'mq5']:
            if 'gold' in filename_lower and 'supreme' in filename_lower:
                return 'Gold Supreme EA'
            elif any(keyword in filename_lower for keyword in ['backtest', 'test', 'result', 'report']):
                return 'Backtest EA'
            elif any(keyword in filename_lower for keyword in ['ea', 'expert', 'advisor', 'strategy']):
                return 'EA Trading'
            else:
                return 'EA Trading'  # Default per file MQL generici
        
        # Categorizzazione per documenti broker
        if any(keyword in filename_lower for keyword in ['broker', 'contratto', 'accordo', 'certificato']):
            return 'Documenti Broker'
        
        # Categorizzazione per report CPA
        if any(keyword in filename_lower for keyword in ['report', 'cpa', 'mensile', 'trimestrale', 'annuale']):
            return 'Report CPA'
        
        # Categorizzazione per documenti legali
        if any(keyword in filename_lower for keyword in ['privacy', 'policy', 'term', 'condizione', 'legale']):
            return 'Documenti Legali'
        
        # Categorizzazione per materiale marketing
        if any(keyword in filename_lower for keyword in ['marketing', 'promo', 'video', 'presentazione', 'brochure']):
            return 'Materiale Marketing'
        
        # Categorizzazione per analisi
        if any(keyword in filename_lower for keyword in ['analisi', 'studio', 'ricerca', 'grafico', 'chart']):
            return 'Analisi'
        
        # Categorizzazione normale per altri file
        for category, extensions in self.categories.items():
            if extension in extensions and category not in ['EA Trading', 'Backtest', 'Documenti Broker', 
                                                          'Report CPA', 'Documenti Legali', 'Materiale Marketing', 'Analisi']:
                return category
        
        return 'Altro'
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Genera un nome file univoco per evitare conflitti
        
        Args:
            original_filename: Nome originale del file
            
        Returns:
            str: Nome file univoco
        """
        # Estrai nome e estensione
        name, ext = os.path.splitext(original_filename)
        
        # Genera hash univoco
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crea nome univoco
        unique_name = f"{timestamp}_{unique_id}_{name}{ext}"
        
        return unique_name
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calcola l'hash MD5 di un file per verificare l'integrità
        
        Args:
            file_path: Percorso del file
            
        Returns:
            str: Hash MD5 del file
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def upload_file(self, uploaded_file, category: str = None, description: str = None) -> Dict:
        """
        Carica un file nel sistema storage
        
        Args:
            uploaded_file: File caricato da Streamlit
            category: Categoria del file
            description: Descrizione opzionale
            
        Returns:
            Dict: Risultato dell'operazione
        """
        try:
            # Verifica che l'utente sia admin
            current_user = st.session_state.get('user_info', {})
            is_admin = current_user.get('role') == 'admin' or current_user.get('is_admin', False)
            
            if not is_admin:
                return {
                    'success': False,
                    'message': f'Solo gli amministratori possono caricare file. Utente: {current_user.get("username") if current_user else "None"}, Admin: {is_admin}'
                }
            
            # Genera nome file univoco
            unique_filename = self.generate_unique_filename(uploaded_file.name)
            file_path = self.storage_dir / unique_filename
            
            # Percorso relativo per il database (compatibile con deployment)
            relative_path = f"storage/uploads/{unique_filename}"
            
            # Salva il file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Determina categoria se non specificata
            if not category:
                category = self.get_file_category(uploaded_file.name)
            
            # Calcola hash del file
            file_hash = self.calculate_file_hash(str(file_path))
            
            # Ottieni informazioni sul file
            file_size = os.path.getsize(file_path)
            file_type = mimetypes.guess_type(uploaded_file.name)[0] or 'application/octet-stream'
            
            # Inserisci record nel database
            file_data = {
                'filename': unique_filename,
                'original_filename': uploaded_file.name,
                'file_path': relative_path,  # Usa percorso relativo
                'file_size': file_size,
                'file_type': file_type,
                'category': category,
                'description': description or '',
                'uploaded_by': current_user.get('id') or current_user.get('user_id')
            }
            
            # Inserisci record nel database
            result = self.supabase.table('storage_files').insert(file_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': f'File "{uploaded_file.name}" caricato con successo',
                    'file_id': result.data[0]['id']
                }
            else:
                # Se l'inserimento fallisce, elimina il file
                os.remove(file_path)
                return {
                    'success': False,
                    'message': 'Errore durante il salvataggio nel database'
                }
                
        except Exception as e:
            # Se c'è un errore, elimina il file se è stato creato
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            return {
                'success': False,
                'message': f'Errore durante il caricamento: {str(e)}'
            }
    
    def get_files(self, category: str = None, search: str = None) -> List[Dict]:
        """
        Recupera la lista dei file disponibili
        
        Args:
            category: Filtro per categoria
            search: Termine di ricerca nel nome del file
            
        Returns:
            List[Dict]: Lista dei file
        """
        try:
            query = self.supabase.table('storage_files').select('*').eq('is_active', True)
            
            # Applica filtri
            if category and category != 'Tutte':
                query = query.eq('category', category)
            
            if search:
                query = query.ilike('original_filename', f'%{search}%')
            
            # Ordina per data di caricamento (più recenti prima)
            query = query.order('uploaded_at', desc=True)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            st.error(f'Errore durante il recupero dei file: {str(e)}')
            return []
    
    def download_file(self, file_id: int) -> Tuple[bool, str, bytes]:
        """
        Prepara un file per il download
        
        Args:
            file_id: ID del file da scaricare
            
        Returns:
            Tuple[bool, str, bytes]: (successo, nome_file, contenuto_file)
        """
        try:
            # Recupera informazioni sul file
            result = self.supabase.table('storage_files').select('*').eq('id', file_id).eq('is_active', True).execute()
            
            if not result.data:
                return False, "File non trovato", b""
            
            file_info = result.data[0]
            file_path = file_info['file_path']
            
            # Gestisci percorsi relativi e assoluti
            if not os.path.isabs(file_path):
                # Percorso relativo - costruisci il percorso completo
                file_path = Path(current_dir) / file_path
            else:
                # Percorso assoluto - usa così com'è
                file_path = Path(file_path)
            
            # Verifica che il file esista
            if not file_path.exists():
                return False, f"File non trovato nel filesystem: {file_path}", b""
            
            # Leggi il contenuto del file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Registra il download
            current_user = st.session_state.get('user_info', {})
            if current_user:
                download_data = {
                    'file_id': file_id,
                    'downloaded_by': current_user.get('id') or current_user.get('user_id')
                }
                self.supabase.table('storage_downloads').insert(download_data).execute()
                
                # Incrementa contatore download
                self.supabase.table('storage_files').update({
                    'download_count': file_info['download_count'] + 1
                }).eq('id', file_id).execute()
            
            return True, file_info['original_filename'], file_content
            
        except Exception as e:
            st.error(f'Errore durante il download: {str(e)}')
            return False, f"Errore: {str(e)}", b""
    
    def delete_file(self, file_id: int) -> Dict:
        """
        Elimina un file (soft delete)
        
        Args:
            file_id: ID del file da eliminare
            
        Returns:
            Dict: Risultato dell'operazione
        """
        try:
            # Verifica che l'utente sia admin
            current_user = st.session_state.get('user_info', {})
            is_admin = current_user.get('role') == 'admin' or current_user.get('is_admin', False)
            
            if not is_admin:
                return {
                    'success': False,
                    'message': 'Solo gli amministratori possono eliminare file'
                }
            
            # Recupera informazioni sul file
            result = self.supabase.table('storage_files').select('*').eq('id', file_id).execute()
            
            if not result.data:
                return {
                    'success': False,
                    'message': 'File non trovato'
                }
            
            file_info = result.data[0]
            
            # Soft delete nel database
            update_result = self.supabase.table('storage_files').update({
                'is_active': False
            }).eq('id', file_id).execute()
            
            if update_result.data:
                # Opzionalmente, elimina anche il file fisico
                file_path = file_info['file_path']
                if not os.path.isabs(file_path):
                    file_path = Path(current_dir) / file_path
                else:
                    file_path = Path(file_path)
                
                if file_path.exists():
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        st.warning(f'File eliminato dal database ma non dal filesystem: {str(e)}')
                
                return {
                    'success': True,
                    'message': f'File "{file_info["original_filename"]}" eliminato con successo'
                }
            else:
                return {
                    'success': False,
                    'message': 'Errore durante l\'eliminazione'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Errore durante l\'eliminazione: {str(e)}'
            }
    
    def get_storage_stats(self) -> Dict:
        """
        Recupera statistiche sull'utilizzo dello storage
        
        Returns:
            Dict: Statistiche dello storage
        """
        try:
            # Conta file totali
            files_result = self.supabase.table('storage_files').select('id, file_size, category').eq('is_active', True).execute()
            
            if not files_result.data:
                return {
                    'total_files': 0,
                    'total_size': 0,
                    'categories': {}
                }
            
            total_files = len(files_result.data)
            total_size = sum(file['file_size'] for file in files_result.data)
            
            # Raggruppa per categoria
            categories = {}
            for file in files_result.data:
                cat = file['category']
                if cat not in categories:
                    categories[cat] = {'count': 0, 'size': 0}
                categories[cat]['count'] += 1
                categories[cat]['size'] += file['file_size']
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'categories': categories
            }
            
        except Exception as e:
            st.error(f'Errore durante il recupero delle statistiche: {str(e)}')
            return {
                'total_files': 0,
                'total_size': 0,
                'categories': {}
            }
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Formatta la dimensione del file in formato leggibile
        
        Args:
            size_bytes: Dimensione in bytes
            
        Returns:
            str: Dimensione formattata
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
