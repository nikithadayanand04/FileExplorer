"""
File ingestion service for CryptoFS++.
Handles file upload, validation, and initial processing.
"""
import hashlib
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime
from uuid import UUID, uuid4

from app.config import settings
from app.models.file import FileMetadata, FileZone, SensitivityLevel, EncryptionStatus

class FileIngestionService:
    """
    Service for ingesting and validating uploaded files.
    Handles file storage, hash calculation, and metadata creation.
    """
    
    def __init__(self):
        """Initialize file ingestion service."""
        self.upload_dir = settings.UPLOAD_DIR
        self.encrypted_dir = settings.ENCRYPTED_DIR
        
    async def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        uploaded_by: str
    ) -> FileMetadata:
        """
        Ingest an uploaded file.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            mime_type: MIME type of the file
            uploaded_by: User ID who uploaded the file
            
        Returns:
            FileMetadata object
        """
        # Validate file size
        file_size = len(file_content)
        if file_size > settings.MAX_FILE_SIZE:
            raise ValueError(f"File size {file_size} exceeds maximum {settings.MAX_FILE_SIZE}")
        
        # Calculate file hash
        file_hash = self._calculate_hash(file_content)
        
        # Generate unique file ID
        file_id = uuid4()
        
        # Create storage filename
        storage_filename = f"{file_id}_{filename}"
        storage_path = self.upload_dir / storage_filename
        
        # Save file
        async with aiofiles.open(storage_path, 'wb') as f:
            await f.write(file_content)
        
        # Create metadata
        metadata = FileMetadata(
            file_id=file_id,
            filename=storage_filename,
            original_filename=filename,
            file_size=file_size,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            zone=FileZone.PUBLIC,  # Initial zone, will be updated after analysis
            sensitivity_score=0,
            sensitivity_level=SensitivityLevel.LOW,
            encryption_status=EncryptionStatus.PENDING,
            file_hash=file_hash
        )
        
        return metadata
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(content).hexdigest()
    
    async def read_file(self, file_id: UUID) -> Optional[bytes]:
        """
        Read file content by file ID.
        
        Args:
            file_id: UUID of the file
            
        Returns:
            File content bytes or None if not found
        """
        # Find file in upload directory
        for file_path in self.upload_dir.glob(f"{file_id}_*"):
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        
        # Check encrypted directory
        for file_path in self.encrypted_dir.glob(f"{file_id}_*"):
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        
        return None
    
    async def delete_file(self, file_id: UUID) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_id: UUID of the file
            
        Returns:
            True if deleted, False if not found
        """
        deleted = False
        
        # Try upload directory
        for file_path in self.upload_dir.glob(f"{file_id}_*"):
            file_path.unlink()
            deleted = True
        
        # Try encrypted directory
        for file_path in self.encrypted_dir.glob(f"{file_id}_*"):
            file_path.unlink()
            deleted = True
        
        return deleted

