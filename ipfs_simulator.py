import hashlib
import os
import json
import shutil
from datetime import datetime
import base64


class IPFSSimulator:
    def __init__(self, storage_path='static/ipfs_storage'):
        self.storage_path = storage_path
        self.metadata_file = os.path.join(storage_path, 'metadata.json')
        self._ensure_storage_exists()
        self.metadata = self._load_metadata()
    
    def _ensure_storage_exists(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _generate_cid(self, content):
        if isinstance(content, bytes):
            hash_input = content
        else:
            hash_input = content.encode('utf-8')
        
        content_hash = hashlib.sha256(hash_input).hexdigest()
        cid = f"Qm{content_hash[:44]}"
        return cid
    
    def add_file(self, file_path, original_filename=None):
        if not os.path.exists(file_path):
            return None, "File not found"
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        cid = self._generate_cid(content)
        
        ext = os.path.splitext(file_path)[1] if not original_filename else os.path.splitext(original_filename)[1]
        stored_path = os.path.join(self.storage_path, f"{cid}{ext}")
        
        shutil.copy(file_path, stored_path)
        
        self.metadata[cid] = {
            'original_filename': original_filename or os.path.basename(file_path),
            'stored_path': stored_path,
            'size': len(content),
            'added_at': str(datetime.utcnow()),
            'content_type': self._get_content_type(ext)
        }
        self._save_metadata()
        
        return cid, None
    
    def add_json(self, data):
        json_content = json.dumps(data, indent=2)
        cid = self._generate_cid(json_content)
        
        stored_path = os.path.join(self.storage_path, f"{cid}.json")
        with open(stored_path, 'w') as f:
            f.write(json_content)
        
        self.metadata[cid] = {
            'original_filename': 'data.json',
            'stored_path': stored_path,
            'size': len(json_content),
            'added_at': str(datetime.utcnow()),
            'content_type': 'application/json'
        }
        self._save_metadata()
        
        return cid
    
    def get_file(self, cid):
        if cid not in self.metadata:
            return None, "CID not found"
        
        file_info = self.metadata[cid]
        stored_path = file_info['stored_path']
        
        if not os.path.exists(stored_path):
            return None, "File not found in storage"
        
        return stored_path, None
    
    def get_json(self, cid):
        file_path, error = self.get_file(cid)
        if error:
            return None, error
        
        with open(file_path, 'r') as f:
            return json.load(f), None
    
    def get_file_info(self, cid):
        if cid not in self.metadata:
            return None
        return self.metadata[cid]
    
    def pin(self, cid):
        if cid in self.metadata:
            self.metadata[cid]['pinned'] = True
            self._save_metadata()
            return True
        return False
    
    def unpin(self, cid):
        if cid in self.metadata:
            self.metadata[cid]['pinned'] = False
            self._save_metadata()
            return True
        return False
    
    def remove(self, cid):
        if cid not in self.metadata:
            return False
        
        file_info = self.metadata[cid]
        if file_info.get('pinned'):
            return False
        
        if os.path.exists(file_info['stored_path']):
            os.remove(file_info['stored_path'])
        
        del self.metadata[cid]
        self._save_metadata()
        return True
    
    def _get_content_type(self, extension):
        content_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.json': 'application/json',
            '.html': 'text/html',
            '.txt': 'text/plain'
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
    
    def get_gateway_url(self, cid):
        return f"/ipfs/{cid}"
    
    def list_all(self):
        return list(self.metadata.keys())
    
    def get_stats(self):
        total_size = sum(info['size'] for info in self.metadata.values())
        pinned_count = sum(1 for info in self.metadata.values() if info.get('pinned'))
        
        return {
            'total_files': len(self.metadata),
            'total_size': total_size,
            'pinned_files': pinned_count,
            'storage_path': self.storage_path
        }


ipfs = IPFSSimulator()
