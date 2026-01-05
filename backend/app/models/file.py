"""
File system models for CryptoFS++.
Defines data structures for files, zones, and metadata.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class FileZone(str, Enum):
    """File storage zones based on sensitivity."""
    PUBLIC = "public"           # 🟢 Low sensitivity
    MONITORED = "monitored"     # 🟡 Medium sensitivity
    CRYPTO_VAULT = "crypto_vault"  # 🔴 High sensitivity
    COLD_STORAGE = "cold_storage"  # 🧊 Critical files

class SensitivityLevel(str, Enum):
    """Sensitivity classification levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EncryptionStatus(str, Enum):
    """File encryption status."""
    UNENCRYPTED = "unencrypted"
    ENCRYPTED = "encrypted"
    PENDING = "pending"

class FileMetadata(BaseModel):
    """Core file metadata."""
    file_id: UUID = Field(default_factory=uuid4)
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str
    zone: FileZone = FileZone.PUBLIC
    sensitivity_score: int = Field(ge=0, le=100, default=0)
    sensitivity_level: SensitivityLevel = SensitivityLevel.LOW
    encryption_status: EncryptionStatus = EncryptionStatus.UNENCRYPTED
    encryption_key_id: Optional[str] = None
    file_hash: str
    detected_entities: List[str] = Field(default_factory=list)
    classification_reasons: List[str] = Field(default_factory=list)
    ai_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "document.pdf",
                "file_size": 1024,
                "mime_type": "application/pdf",
                "zone": "crypto_vault",
                "sensitivity_score": 85,
                "sensitivity_level": "CRITICAL",
                "encryption_status": "encrypted",
                "detected_entities": ["Aadhaar pattern", "Face detected"],
                "classification_reasons": [
                    "Detected Aadhaar-like pattern (XXXX XXXX XXXX)",
                    "Detected human face in image"
                ],
                "ai_confidence": 0.92
            }
        }

class FileContentAnalysis(BaseModel):
    """AI analysis results for file content."""
    file_id: UUID
    text_analysis: Dict[str, Any] = Field(default_factory=dict)
    image_analysis: Dict[str, Any] = Field(default_factory=dict)
    detected_entities: List[str] = Field(default_factory=list)
    sensitivity_score: int = Field(ge=0, le=100)
    classification: SensitivityLevel
    reasons: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

class FileAccessLog(BaseModel):
    """Access attempt log entry."""
    log_id: UUID = Field(default_factory=uuid4)
    file_id: UUID
    user_id: str
    action: str  # READ, WRITE, DELETE, MOVE
    result: str  # ALLOWED, DENIED, BLOCKED
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    blockchain_hash: Optional[str] = None

