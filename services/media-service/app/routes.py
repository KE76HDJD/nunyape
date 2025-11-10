from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .models import User, UserCreate, UserUpdate, Token
from .processing import UserProcessor, BatchProcessor

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        processor = UserProcessor()
        result = await processor.process_user_creation(user_data)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        # Return mock user (in real app, this would come from database)
        return User(
            id="user_123",
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    # Mock implementation
    return User(
        id=user_id,
        email="user@example.com",
        first_name="John",
        last_name="Doe",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )

@router.post("/users/batch", response_model=List[dict])
async def create_users_batch(users: List[UserCreate]):
    """Create multiple users in batch"""
    processor = BatchProcessor()
    results = await processor.process_batch(users)
    return results

@router.post("/token", response_model=Token)
async def login_for_access_token():
    """Login to get access token"""
    return Token(
        access_token="mock_jwt_token",
        token_type="bearer",
        expires_in=3600
    )