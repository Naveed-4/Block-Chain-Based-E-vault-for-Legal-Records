import os
import hashlib
import json
import time
from typing import Dict, Any, Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

class DocumentStorage:
    def __init__(self, storage_path: str = "storage/documents"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.metadata_file = os.path.join(storage_path, "metadata.json")
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self) -> None:
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _generate_document_hash(self, content: bytes) -> str:
        """Generate a hash for the document content."""
        return hashlib.sha256(content).hexdigest()

    def _encrypt_document(self, content: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """Encrypt document content using AES."""
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(content, AES.block_size))
        iv = cipher.iv
        return ct_bytes, iv

    def _decrypt_document(self, encrypted_content: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt document content using AES."""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(encrypted_content), AES.block_size)
        return pt

    def store_document(self, user_id: str, document_name: str, 
                       document_content: bytes, document_type: str, 
                       encryption_key: bytes = None) -> Dict[str, Any]:
        """Store a document and return its metadata."""
        if encryption_key is None:
            encryption_key = get_random_bytes(32)
            
        # Generate document hash
        document_hash = self._generate_document_hash(document_content)
        
        # Encrypt document
        encrypted_content, iv = self._encrypt_document(document_content, encryption_key)
        
        # Create document metadata
        document_metadata = {
            "user_id": user_id,
            "name": document_name,
            "type": document_type,
            "hash": document_hash,
            "size": len(document_content),
            "created_at": time.time(),
            "iv": base64.b64encode(iv).decode("utf-8"),
            "encryption_key": base64.b64encode(encryption_key).decode("utf-8"),
        }
        
        # Save encrypted document
        document_path = os.path.join(self.storage_path, document_hash)
        with open(document_path, 'wb') as f:
            f.write(encrypted_content)
        
        # Update metadata
        self.metadata[document_hash] = document_metadata
        self._save_metadata()
        
        return document_metadata

    def retrieve_document(self, document_hash: str) -> Tuple[bytes, Dict[str, Any]]:
        """Retrieve a document by its hash."""
        if document_hash not in self.metadata:
            raise ValueError(f"Document with hash {document_hash} not found")
        
        document_metadata = self.metadata[document_hash]
        document_path = os.path.join(self.storage_path, document_hash)
        
        if not os.path.exists(document_path):
            raise ValueError(f"Document file not found for hash {document_hash}")
        
        # Read encrypted content
        with open(document_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Decrypt document
        iv = base64.b64decode(document_metadata["iv"])
        encryption_key = base64.b64decode(document_metadata["encryption_key"])
        decrypted_content = self._decrypt_document(encrypted_content, encryption_key, iv)
        
        return decrypted_content, document_metadata

    def delete_document(self, document_hash: str) -> bool:
        """Delete a document by its hash."""
        if document_hash not in self.metadata:
            return False
        
        document_path = os.path.join(self.storage_path, document_hash)
        if os.path.exists(document_path):
            os.remove(document_path)
        
        del self.metadata[document_hash]
        self._save_metadata()
        
        return True

    def get_user_documents(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all documents for a specific user."""
        user_documents = {}
        for doc_hash, metadata in self.metadata.items():
            if metadata.get("user_id") == user_id:
                user_documents[doc_hash] = metadata
        return user_documents