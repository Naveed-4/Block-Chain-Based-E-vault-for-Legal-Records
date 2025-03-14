import hashlib
import json
import os
import secrets
from typing import Dict, Any, Tuple, Optional

class UserAuth:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = storage_path
        self.users_file = os.path.join(storage_path, "users.json")
        self.sessions_file = os.path.join(storage_path, "sessions.json")
        os.makedirs(storage_path, exist_ok=True)
        self.users = self._load_users()
        self.sessions = self._load_sessions()

    def _load_users(self) -> Dict[str, Any]:
        """Load users from file."""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_users(self) -> None:
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def _load_sessions(self) -> Dict[str, Any]:
        """Load sessions from file."""
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_sessions(self) -> None:
        """Save sessions to file."""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)

    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash a password with a salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256((password + salt).encode())
        hashed_password = hash_obj.hexdigest()
        
        return hashed_password, salt

    def register_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Register a new user."""
        if username in self.users:
            raise ValueError("Username already exists")
        
        hashed_password, salt = self._hash_password(password)
        
        user_id = secrets.token_hex(16)
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "salt": salt,
            "role": "user"
        }
        
        self.users[username] = user_data
        self._save_users()
        
        return user_data

    def login(self, username: str, password: str) -> Optional[str]:
        """Login a user and return a session token."""
        if username not in self.users:
            return None
        
        user_data = self.users[username]
        hashed_password, _ = self._hash_password(password, user_data["salt"])
        
        if hashed_password != user_data["hashed_password"]:
            return None
        
        # Create a new session
        session_token = secrets.token_hex(32)
        self.sessions[session_token] = {
            "user_id": user_data["user_id"],
            "username": username
        }
        self._save_sessions()
        
        return session_token

    def logout(self, session_token: str) -> bool:
        """Logout a user by invalidating their session token."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            self._save_sessions()
            return True
        return False

    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user data by session token."""
        if session_token not in self.sessions:
            return None
        
        session_data = self.sessions[session_token]
        username = session_data["username"]
        
        if username not in self.users:
            return None
        
        return self.users[username]

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by user ID."""
        for username, user_data in self.users.items():
            if user_data["user_id"] == user_id:
                return user_data
        return None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change a user's password."""
        if username not in self.users:
            return False
        
        user_data = self.users[username]
        hashed_old_password, _ = self._hash_password(old_password, user_data["salt"])
        
        if hashed_old_password != user_data["hashed_password"]:
            return False
        
        hashed_new_password, salt = self._hash_password(new_password)
        
        user_data["hashed_password"] = hashed_new_password
        user_data["salt"] = salt
        
        self.users[username] = user_data
        self._save_users()
        
        return True