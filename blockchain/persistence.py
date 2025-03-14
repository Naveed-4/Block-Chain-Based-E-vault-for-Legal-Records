import json
import os
from typing import Dict, Any
from blockchain.blockchain import Blockchain

class BlockchainPersistence:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = storage_path
        self.blockchain_file = os.path.join(storage_path, "blockchain.json")
        os.makedirs(storage_path, exist_ok=True)

    def save_blockchain(self, blockchain: Blockchain) -> None:
        """Save blockchain to file."""
        blockchain_data = blockchain.to_dict()
        with open(self.blockchain_file, 'w') as f:
            json.dump(blockchain_data, f, indent=2)

    def load_blockchain(self) -> Blockchain:
        """Load blockchain from file."""
        blockchain = Blockchain()
        if os.path.exists(self.blockchain_file):
            with open(self.blockchain_file, 'r') as f:
                try:
                    blockchain_data = json.load(f)
                    blockchain.from_dict(blockchain_data)
                except json.JSONDecodeError:
                    # If the file is corrupted, start with a new blockchain
                    pass
        return blockchain