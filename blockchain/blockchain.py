import hashlib
import json
import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict[str, Any]], 
                 previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the hash of the block."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """Mine a new block."""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []

    def create_genesis_block(self) -> Block:
        """Create the genesis block."""
        return Block(0, time.time(), [], "0")

    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]

    def add_block(self, transactions: List[Dict[str, Any]]) -> Block:
        """Add a new block to the chain."""
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            transactions=transactions,
            previous_hash=latest_block.hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block

    def add_transaction(self, transaction: Dict[str, Any]) -> int:
        """Add a new transaction to pending transactions."""
        self.pending_transactions.append(transaction)
        return self.get_latest_block().index + 1

    def mine_pending_transactions(self) -> Block:
        """Mine pending transactions into a new block."""
        if not self.pending_transactions:
            return None
            
        new_block = self.add_block(self.pending_transactions)
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check if the hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if the previous hash reference is correct
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_block_by_hash(self, hash_value: str) -> Block:
        """Get a block by its hash."""
        for block in self.chain:
            if block.hash == hash_value:
                return block
        return None

    def get_transactions_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific user."""
        user_transactions = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get("user_id") == user_id:
                    transaction_copy = transaction.copy()
                    transaction_copy["block_hash"] = block.hash
                    transaction_copy["timestamp"] = block.timestamp
                    user_transactions.append(transaction_copy)
        return user_transactions

    def to_dict(self) -> Dict[str, Any]:
        """Convert blockchain to dictionary."""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": self.pending_transactions,
            "difficulty": self.difficulty
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load blockchain from dictionary."""
        self.difficulty = data.get("difficulty", 2)
        self.pending_transactions = data.get("pending_transactions", [])
        
        # Recreate the chain
        self.chain = []
        for block_data in data.get("chain", []):
            block = Block(
                index=block_data["index"],
                timestamp=block_data["timestamp"],
                transactions=block_data["transactions"],
                previous_hash=block_data["previous_hash"]
            )
            block.nonce = block_data["nonce"]
            block.hash = block_data["hash"]
            self.chain.append(block)