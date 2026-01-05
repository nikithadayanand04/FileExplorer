"""
Blockchain audit and logging models.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class AuditEvent(BaseModel):
    """Blockchain audit event."""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str  # FILE_UPLOAD, ENCRYPTION, ACCESS, ZONE_TRANSITION, etc.
    file_id: Optional[UUID] = None
    user_id: Optional[str] = None
    action: str
    result: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    previous_hash: Optional[str] = None
    block_hash: Optional[str] = None
    block_index: Optional[int] = None

class BlockchainBlock(BaseModel):
    """Blockchain block structure."""
    index: int
    timestamp: datetime
    events: list[AuditEvent]
    previous_hash: str
    hash: str
    nonce: int = 0

