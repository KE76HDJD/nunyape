import asyncio
from typing import List, Dict, Any
import json
from datetime import datetime
from .models import User, UserCreate

class UserProcessor:
    def __init__(self):
        self.processing_queue = asyncio.Queue()
        
    async def process_user_creation(self, user_data: UserCreate) -> Dict[str, Any]:
        """Process user creation with validation and setup"""
        try:
            # Simulate processing steps
            await self.validate_user_data(user_data)
            await self.create_user_profile(user_data)
            await self.send_welcome_email(user_data)
            
            return {
                "status": "success",
                "message": "User processed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_user_data(self, user_data: UserCreate):
        """Validate user data before processing"""
        # Simulate validation logic
        await asyncio.sleep(0.1)
        if len(user_data.password) < 8:
            raise ValueError("Password must be at least 8 characters")
    
    async def create_user_profile(self, user_data: UserCreate):
        """Create user profile in database"""
        # Simulate database operation
        await asyncio.sleep(0.2)
    
    async def send_welcome_email(self, user_data: UserCreate):
        """Send welcome email to new user"""
        # Simulate email sending
        await asyncio.sleep(0.1)

class BatchProcessor:
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        
    async def process_batch(self, users: List[UserCreate]) -> List[Dict[str, Any]]:
        """Process multiple users in batches"""
        results = []
        for i in range(0, len(users), self.batch_size):
            batch = users[i:i + self.batch_size]
            batch_tasks = [self._process_single_user(user) for user in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        return results
    
    async def _process_single_user(self, user: UserCreate) -> Dict[str, Any]:
        """Process a single user"""
        processor = UserProcessor()
        return await processor.process_user_creation(user)