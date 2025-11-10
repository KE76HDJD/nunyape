import json
import aiofiles
from typing import Optional, Dict, Any
from pathlib import Path
from .models import User

class StorageManager:
    def __init__(self, storage_path: str = "data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    async def save_user(self, user: User) -> bool:
        """Save user data to storage"""
        try:
            user_file = self.storage_path / f"user_{user.id}.json"
            async with aiofiles.open(user_file, 'w') as f:
                await f.write(user.json())
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user data from storage"""
        try:
            user_file = self.storage_path / f"user_{user_id}.json"
            if not user_file.exists():
                return None
            
            async with aiofiles.open(user_file, 'r') as f:
                data = await f.read()
                user_dict = json.loads(data)
                return User(**user_dict)
        except Exception as e:
            print(f"Error reading user: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user data from storage"""
        try:
            user_file = self.storage_path / f"user_{user_id}.json"
            if user_file.exists():
                user_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

class CacheManager:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cache value with TTL"""
        self._cache[key] = {
            'value': value,
            'expires_at': None  # Simplified implementation
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if key in self._cache:
            return self._cache[key]['value']
        return None
    
    async def delete(self, key: str) -> bool:
        """Delete cache value"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False