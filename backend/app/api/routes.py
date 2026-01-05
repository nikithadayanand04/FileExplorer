"""
API routes for CryptoFS++ backend.
Defines REST endpoints for file operations, AI analysis, and blockchain audit.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional, List
from uuid import UUID

from app.models.file import FileMetadata, FileContentAnalysis, EncryptionStatus
from app.models.user import UserRole
from app.services.file_ingestion import FileIngestionService
from app.services.content_analysis import ContentAnalysisService
from app.services.sensitivity_scoring import SensitivityScoringEngine
from app.services.encryption_service import EncryptionService
from app.services.policy_engine import PolicyEngine
from app.services.blockchain_logger import BlockchainLogger
from app.services.access_control import AccessControlService
from app.ai.explainability import ExplainabilityEngine

router = APIRouter()

# Initialize services
file_ingestion = FileIngestionService()
content_analysis = ContentAnalysisService()
sensitivity_scoring = SensitivityScoringEngine()
encryption_service = EncryptionService()
policy_engine = PolicyEngine()
blockchain_logger = BlockchainLogger()
access_control = AccessControlService()
explainability = ExplainabilityEngine()

# In-memory storage for demo (replace with database in production)
file_registry: dict[str, FileMetadata] = {}

def get_current_user(user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """Get current user ID from header (simplified auth)."""
    if not user_id:
        user_id = "demo_user"  # Default for demo
    return user_id

def get_user_role(user_id: str) -> UserRole:
    """Get user role (simplified, replace with proper auth)."""
    # Demo: admin for demo_user, user for others
    return UserRole.ADMIN if user_id == "demo_user" else UserRole.USER

@router.post("/files/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload and process a file.
    Automatically analyzes content, assigns zone, and encrypts if needed.
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Ingest file
        metadata = await file_ingestion.ingest_file(
            file_content=file_content,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            uploaded_by=user_id
        )
        
        # Analyze content
        analysis = await content_analysis.analyze_file(
            file_content=file_content,
            mime_type=metadata.mime_type,
            file_id=str(metadata.file_id)
        )
        
        # Update metadata with analysis results
        metadata.sensitivity_score = analysis.sensitivity_score
        metadata.sensitivity_level = analysis.classification
        metadata.detected_entities = analysis.detected_entities
        metadata.classification_reasons = analysis.reasons
        metadata.ai_confidence = analysis.confidence
        
        # Determine zone
        zone = sensitivity_scoring.calculate_zone(
            analysis.sensitivity_score,
            analysis.classification,
            analysis.detected_entities
        )
        metadata.zone = zone
        
        # Decide encryption
        should_encrypt, policy_rule, reasons = policy_engine.decide_encryption(
            analysis.sensitivity_score,
            analysis.classification,
            analysis.detected_entities
        )
        
        if should_encrypt:
            # Encrypt file
            encrypted_path, key_id = await encryption_service.encrypt_and_store(
                file_content,
                str(metadata.file_id),
                metadata.original_filename
            )
            metadata.encryption_status = EncryptionStatus.ENCRYPTED
            metadata.encryption_key_id = key_id
        
        # Store metadata
        file_registry[str(metadata.file_id)] = metadata
        
        # Log to blockchain
        await blockchain_logger.log_event(
            event_type="FILE_UPLOAD",
            action="UPLOAD",
            result="SUCCESS",
            file_id=str(metadata.file_id),
            user_id=user_id,
            metadata={
                "filename": metadata.original_filename,
                "sensitivity_score": metadata.sensitivity_score,
                "zone": metadata.zone.value,
                "encrypted": should_encrypt
            }
        )
        
        # Generate explanation
        explanation = explainability.explain_classification(
            metadata.sensitivity_score,
            metadata.sensitivity_level.value,
            metadata.detected_entities,
            metadata.classification_reasons,
            metadata.ai_confidence
        )
        
        return {
            "file_id": str(metadata.file_id),
            "filename": metadata.original_filename,
            "sensitivity_score": metadata.sensitivity_score,
            "sensitivity_level": metadata.sensitivity_level.value,
            "zone": metadata.zone.value,
            "encryption_status": metadata.encryption_status.value,
            "detected_entities": metadata.detected_entities,
            "classification_reasons": metadata.classification_reasons,
            "ai_confidence": metadata.ai_confidence,
            "explanation": explanation,
            "policy_rule": policy_rule
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files", response_model=List[dict])
async def list_files(user_id: str = Depends(get_current_user)):
    """List all files with metadata."""
    files = []
    for file_id, metadata in file_registry.items():
        files.append({
            "file_id": file_id,
            "filename": metadata.original_filename,
            "file_size": metadata.file_size,
            "mime_type": metadata.mime_type,
            "uploaded_at": metadata.uploaded_at.isoformat(),
            "zone": metadata.zone.value,
            "sensitivity_score": metadata.sensitivity_score,
            "sensitivity_level": metadata.sensitivity_level.value,
            "encryption_status": metadata.encryption_status.value,
            "detected_entities": metadata.detected_entities
        })
    return files

@router.get("/files/{file_id}", response_model=dict)
async def get_file(
    file_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get file metadata and explanation."""
    if file_id not in file_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    metadata = file_registry[file_id]
    user_role = get_user_role(user_id)
    
    # Check access
    allowed, reason, explanations = policy_engine.decide_access(
        user_role,
        metadata.sensitivity_level,
        "READ"
    )
    
    if not allowed:
        # Log denied access
        await blockchain_logger.log_event(
            event_type="ACCESS",
            action="READ",
            result="DENIED",
            file_id=file_id,
            user_id=user_id,
            metadata={"reason": reason}
        )
        raise HTTPException(status_code=403, detail=f"Access denied: {reason}")
    
    # Log allowed access
    await blockchain_logger.log_event(
        event_type="ACCESS",
        action="READ",
        result="ALLOWED",
        file_id=file_id,
        user_id=user_id
    )
    
    # Generate explanations
    classification_explanation = explainability.explain_classification(
        metadata.sensitivity_score,
        metadata.sensitivity_level.value,
        metadata.detected_entities,
        metadata.classification_reasons,
        metadata.ai_confidence
    )
    
    encryption_explanation = explainability.explain_encryption_decision(
        metadata.encryption_status.value == "encrypted",
        "POLICY_RULE",
        metadata.classification_reasons,
        metadata.sensitivity_score
    )
    
    zone_explanation = explainability.explain_zone_assignment(
        metadata.zone.value,
        metadata.sensitivity_score,
        metadata.classification_reasons
    )
    
    return {
        "file_id": file_id,
        "metadata": metadata.dict(),
        "explanations": {
            "classification": classification_explanation,
            "encryption": encryption_explanation,
            "zone": zone_explanation
        }
    }

@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Download file.

    For encrypted files, this endpoint returns the raw encrypted bytes
    (ciphertext), so you can inspect or store the encrypted version
    rather than the decrypted plaintext.
    """
    if file_id not in file_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    metadata = file_registry[file_id]
    user_role = get_user_role(user_id)
    
    # Check access
    allowed, reason, _ = policy_engine.decide_access(
        user_role,
        metadata.sensitivity_level,
        "READ"
    )
    
    if not allowed:
        await blockchain_logger.log_event(
            event_type="ACCESS",
            action="DOWNLOAD",
            result="DENIED",
            file_id=file_id,
            user_id=user_id
        )
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get file content
    if metadata.encryption_status.value == "encrypted":
        # Serve the encrypted file bytes directly
        encrypted_path = encryption_service.encrypted_dir / f"{file_id}_encrypted_{metadata.original_filename}"
        try:
            import aiofiles  # Local import to avoid unused import warnings elsewhere
            async with aiofiles.open(encrypted_path, "rb") as f:
                file_content = await f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Encrypted file not found")
    else:
        # Serve original (unencrypted) content
        file_content = await file_ingestion.read_file(UUID(file_id))
    
    if not file_content:
        raise HTTPException(status_code=404, detail="File content not found")
    
    # Log download
    await blockchain_logger.log_event(
        event_type="ACCESS",
        action="DOWNLOAD",
        result="ALLOWED",
        file_id=file_id,
        user_id=user_id
    )
    
    from fastapi.responses import Response

    # If encrypted, expose as generic binary with .enc suffix
    if metadata.encryption_status.value == "encrypted":
        download_name = f"{metadata.original_filename}.enc"
        media_type = "application/octet-stream"
    else:
        download_name = metadata.original_filename
        media_type = metadata.mime_type

    return Response(
        content=file_content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"'
        }
    )

@router.get("/files/{file_id}/explain")
async def explain_file_decisions(
    file_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get AI explanations for file decisions."""
    if file_id not in file_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    metadata = file_registry[file_id]
    
    return {
        "file_id": file_id,
        "explanations": {
            "classification": explainability.explain_classification(
                metadata.sensitivity_score,
                metadata.sensitivity_level.value,
                metadata.detected_entities,
                metadata.classification_reasons,
                metadata.ai_confidence
            ),
            "encryption": explainability.explain_encryption_decision(
                metadata.encryption_status.value == "encrypted",
                "POLICY_RULE",
                metadata.classification_reasons,
                metadata.sensitivity_score
            ),
            "zone": explainability.explain_zone_assignment(
                metadata.zone.value,
                metadata.sensitivity_score,
                metadata.classification_reasons
            )
        }
    }

@router.get("/blockchain/chain")
async def get_blockchain_chain():
    """Get entire blockchain."""
    return {
        "blocks": [
            {
                "index": block.index,
                "timestamp": block.timestamp.isoformat(),
                "events": [e.dict() for e in block.events],
                "hash": block.hash,
                "previous_hash": block.previous_hash
            }
            for block in blockchain_logger.get_chain()
        ]
    }

@router.get("/blockchain/file/{file_id}")
async def get_file_audit_trail(file_id: str):
    """Get audit trail for a specific file."""
    events = blockchain_logger.get_file_audit_trail(file_id)
    return {
        "file_id": file_id,
        "events": [e.dict() for e in events]
    }

@router.get("/blockchain/stats")
async def get_blockchain_stats():
    """Get blockchain statistics."""
    return blockchain_logger.get_chain_stats()

@router.get("/zones")
async def get_zones():
    """Get file zones information."""
    return {
        "zones": [
            {
                "id": "public",
                "name": "🟢 Public Zone",
                "description": "Low sensitivity, unencrypted files",
                "threshold": "0-30"
            },
            {
                "id": "monitored",
                "name": "🟡 Monitored Zone",
                "description": "Medium sensitivity, monitored access",
                "threshold": "31-60"
            },
            {
                "id": "crypto_vault",
                "name": "🔴 Crypto Vault",
                "description": "High sensitivity, encrypted storage",
                "threshold": "61-80"
            },
            {
                "id": "cold_storage",
                "name": "🧊 Cold Storage",
                "description": "Critical files, maximum security",
                "threshold": "81-100"
            }
        ]
    }

