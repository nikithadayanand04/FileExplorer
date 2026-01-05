"""
User and access control models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class UserRole(str, Enum):
    """User role levels."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    GUEST = "guest"

class User(BaseModel):
    """User model."""
    user_id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    access_history: List[str] = Field(default_factory=list)
    
class AccessRequest(BaseModel):
    """Access request model."""
    request_id: UUID = Field(default_factory=uuid4)
    user_id: str
    file_id: UUID
    action: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

