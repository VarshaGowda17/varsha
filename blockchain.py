import hashlib
import json
import time
from datetime import datetime
import uuid


class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': str(self.timestamp),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty=2):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash
    
    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': str(self.timestamp),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class LocalBlockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.certificate_registry = {}
        self.create_genesis_block()
    
    def create_genesis_block(self):
        genesis_block = Block(0, datetime.utcnow(), {
            'type': 'genesis',
            'message': 'Genesis Block - Certificate Verification Blockchain',
            'university': 'Global University',
            'initialized': str(datetime.utcnow())
        }, '0')
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_certificate(self, certificate_id, certificate_hash, student_name, course_name, issuer):
        transaction_data = {
            'type': 'certificate_issue',
            'certificate_id': certificate_id,
            'certificate_hash': certificate_hash,
            'student_name': student_name,
            'course_name': course_name,
            'issuer': issuer,
            'action': 'ISSUED',
            'timestamp': str(datetime.utcnow())
        }
        
        new_block = Block(
            len(self.chain),
            datetime.utcnow(),
            transaction_data,
            self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        self.certificate_registry[certificate_id] = {
            'hash': certificate_hash,
            'block_number': new_block.index,
            'block_hash': new_block.hash,
            'status': 'active',
            'issued_at': str(datetime.utcnow())
        }
        
        tx_hash = hashlib.sha256(f"{certificate_id}{new_block.hash}{time.time()}".encode()).hexdigest()
        
        return {
            'success': True,
            'transaction_hash': tx_hash,
            'block_number': new_block.index,
            'block_hash': new_block.hash,
            'certificate_id': certificate_id,
            'gas_used': 21000 + (len(json.dumps(transaction_data)) * 68)
        }
    
    def verify_certificate(self, certificate_id, certificate_hash=None):
        if certificate_id not in self.certificate_registry:
            return {
                'valid': False,
                'status': 'NOT_FOUND',
                'message': 'Certificate not found on blockchain',
                'blockchain_verified': False
            }
        
        cert_data = self.certificate_registry[certificate_id]
        
        if cert_data['status'] == 'revoked':
            return {
                'valid': False,
                'status': 'REVOKED',
                'message': 'Certificate has been revoked',
                'blockchain_verified': True,
                'block_number': cert_data['block_number'],
                'issued_at': cert_data['issued_at']
            }
        
        if certificate_hash and cert_data['hash'] != certificate_hash:
            return {
                'valid': False,
                'status': 'HASH_MISMATCH',
                'message': 'Certificate hash does not match blockchain record',
                'blockchain_verified': True
            }
        
        return {
            'valid': True,
            'status': 'VALID',
            'message': 'Certificate is valid and verified on blockchain',
            'blockchain_verified': True,
            'block_number': cert_data['block_number'],
            'block_hash': cert_data['block_hash'],
            'issued_at': cert_data['issued_at'],
            'certificate_hash': cert_data['hash']
        }
    
    def revoke_certificate(self, certificate_id, reason=""):
        if certificate_id not in self.certificate_registry:
            return {
                'success': False,
                'message': 'Certificate not found'
            }
        
        transaction_data = {
            'type': 'certificate_revoke',
            'certificate_id': certificate_id,
            'action': 'REVOKED',
            'reason': reason,
            'timestamp': str(datetime.utcnow())
        }
        
        new_block = Block(
            len(self.chain),
            datetime.utcnow(),
            transaction_data,
            self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        self.certificate_registry[certificate_id]['status'] = 'revoked'
        self.certificate_registry[certificate_id]['revoked_at'] = str(datetime.utcnow())
        self.certificate_registry[certificate_id]['revocation_block'] = new_block.index
        
        tx_hash = hashlib.sha256(f"revoke{certificate_id}{new_block.hash}{time.time()}".encode()).hexdigest()
        
        return {
            'success': True,
            'transaction_hash': tx_hash,
            'block_number': new_block.index
        }
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_chain_info(self):
        return {
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'is_valid': self.is_chain_valid(),
            'latest_block': self.get_latest_block().to_dict(),
            'total_certificates': len(self.certificate_registry)
        }
    
    def get_all_blocks(self):
        return [block.to_dict() for block in self.chain]
    
    def get_certificate_history(self, certificate_id):
        history = []
        for block in self.chain:
            if isinstance(block.data, dict) and block.data.get('certificate_id') == certificate_id:
                history.append({
                    'block_number': block.index,
                    'action': block.data.get('action'),
                    'timestamp': block.data.get('timestamp'),
                    'block_hash': block.hash
                })
        return history


blockchain = LocalBlockchain(difficulty=2)
