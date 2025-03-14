import time
from typing import Dict, Any, List, Tuple, Optional
import os
import base64

from blockchain.blockchain import Blockchain
from blockchain.persistence import BlockchainPersistence
from storage.document_storage import DocumentStorage
from blockchain.auth import UserAuth

class EVaultController:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = storage_path
        self.blockchain_persistence = BlockchainPersistence(storage_path)
        self.blockchain = self.blockchain_persistence.load_blockchain()
        self.document_storage = DocumentStorage(os.path.join(storage_path, "documents"))
        self.auth = UserAuth(storage_path)

    def register_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Register a new user."""
        return self.auth.register_user(username, password, email)

    def login(self, username: str, password: str) -> Optional[str]:
        """Login a user and return a session token."""
        return self.auth.login(username, password)

    def logout(self, session_token: str) -> bool:
        """Logout a user."""
        return self.auth.logout(session_token)

    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user data by session token."""
        return self.auth.get_user_by_session(session_token)

    def upload_document(self, session_token: str, document_name: str, 
                        document_content: bytes, document_type: str) -> Dict[str, Any]:
        """Upload a document to the vault."""
        # Verify user session
        user_data = self.auth.get_user_by_session(session_token)
        if not user_data:
            raise ValueError("Invalid session")
        
        user_id = user_data["user_id"]
        
        # Store document
        document_metadata = self.document_storage.store_document(
            user_id=user_id,
            document_name=document_name,
            document_content=document_content,
            document_type=document_type
        )
        
        # Create blockchain transaction
        transaction = {
            "type": "document_upload",
            "user_id": user_id,
            "document_hash": document_metadata["hash"],
            "document_name": document_name,
            "document_type": document_type,
            "timestamp": time.time()
        }
        
        self.blockchain.add_transaction(transaction)
        self.blockchain.mine_pending_transactions()
        
        # Save blockchain state
        self.blockchain_persistence.save_blockchain(self.blockchain)
        
        return document_metadata

    def get_document(self, session_token: str, document_hash: str) -> Tuple[bytes, Dict[str, Any]]:
        """Get a document from the vault."""
        # Verify user session
        user_data = self.auth.get_user_by_session(session_token)
        if not user_data:
            raise ValueError("Invalid session")
        
        user_id = user_data["user_id"]
        
        # Retrieve document
        document_content, document_metadata = self.document_storage.retrieve_document(document_hash)
        
        # Verify document ownership
        if document_metadata["user_id"] != user_id:
            raise ValueError("Access denied")
        
        return document_content, document_metadata

    def transfer_document(self, session_token: str, document_hash: str, 
                          recipient_username: str) -> Dict[str, Any]:
        """Transfer a document to another user."""
        # Verify user session
        user_data = self.auth.get_user_by_session(session_token)
        if not user_data:
            raise ValueError("Invalid session")
        
        user_id = user_data["user_id"]
        
        # Verify document ownership
        _, document_metadata = self.document_storage.retrieve_document(document_hash)
        if document_metadata["user_id"] != user_id:
            raise ValueError("Access denied")
        
        # Verify recipient exists
        recipient_user = None
        for username, user_data in self.auth.users.items():
            if username == recipient_username:
                recipient_user = user_data
                break
        
        if not recipient_user:
            raise ValueError(f"Recipient user '{recipient_username}' not found")
        
        # Create blockchain transaction
        transaction = {
            "type": "document_transfer",
            "sender_id": user_id,
            "recipient_id": recipient_user["user_id"],
            "document_hash": document_hash,
            "document_name": document_metadata["name"],
            "timestamp": time.time()
        }
        
        # Update document ownership
        document_content, _ = self.document_storage.retrieve_document(document_hash)
        
        # Re-upload with new owner
        new_document_metadata = self.document_storage.store_document(
            user_id=recipient_user["user_id"],
            document_name=document_metadata["name"],
            document_content=document_content,
            document_type=document_metadata["type"],
            encryption_key=base64.b64decode(document_metadata["encryption_key"])
        )
        
        # Add transaction to blockchain
        self.blockchain.add_transaction(transaction)
        self.blockchain.mine_pending_transactions()
        
        # Save blockchain state
        self.blockchain_persistence.save_blockchain(self.blockchain)
        
        return new_document_metadata

    def get_user_documents(self, session_token: str) -> Dict[str, Dict[str, Any]]:
        """Get all documents for the current user."""
        # Verify user session
        user_data = self.auth.get_user_by_session(session_token)
        if not user_data:
            raise ValueError("Invalid session")
        
        user_id = user_data["user_id"]
        
        # Get documents
        return self.document_storage.get_user_documents(user_id)

    def get_document_history(self, session_token: str, document_hash: str) -> List[Dict[str, Any]]:
        """Get the transaction history for a document."""
        # Verify user session
        user_data = self.auth.get_user_by_session(session_token)
        if not user_data:
            raise ValueError("Invalid session")
        
        # Get document history from blockchain
        document_history = []
        for block in self.blockchain.chain:
            for transaction in block.transactions:
                if transaction.get("document_hash") == document_hash:
                    transaction_copy = transaction.copy()
                    transaction_copy["block_hash"] = block.hash
                    transaction_copy["block_index"] = block.index
                    document_history.append(transaction_copy)
        
        return document_history

    def get_user_transactions(self, session_token: str) -> List[Dict[str, Any]]:
        """Get all transactions for the current user."""
        # Verify user session
        user_data = self.auth.get_user_by_session(session_token)
        if not user_data:
            raise ValueError("Invalid session")
        
        user_id = user_data["user_id"]
        
        # Get transactions
        return self.blockchain.get_transactions_by_user(user_id)

    def verify_blockchain(self) -> bool:
        """Verify the integrity of the blockchain."""
        return self.blockchain.is_chain_valid()