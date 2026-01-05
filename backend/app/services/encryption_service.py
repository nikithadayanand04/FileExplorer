"""
Encryption service for CryptoFS++.
Handles AES-256 encryption/decryption with per-file unique keys.
"""
import os
import hashlib
import aiofiles
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode

from app.config import settings
from app.models.file import EncryptionStatus

class EncryptionService:
    """
    Service for encrypting and decrypting files using AES-256.
    Implements per-file unique encryption keys with secure key derivation.
    """
    
    def __init__(self):
        """Initialize encryption service."""
        self.encrypted_dir = settings.ENCRYPTED_DIR
        self.backend = default_backend()
        self.key_derivation_iterations = settings.KEY_DERIVATION_ITERATIONS
    
    def generate_key(self, file_id: str, master_secret: Optional[str] = None) -> bytes:
        """
        Generate unique encryption key for a file.
        Uses PBKDF2 key derivation with file-specific salt.
        
        Args:
            file_id: Unique file identifier
            master_secret: Optional master secret (defaults to settings secret)
            
        Returns:
            32-byte encryption key
        """
        master_secret = master_secret or settings.SECRET_KEY
        master_secret_bytes = master_secret.encode('utf-8')
        
        # Create file-specific salt
        salt = hashlib.sha256(f"{file_id}_{master_secret}".encode()).digest()[:16]
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.key_derivation_iterations,
            backend=self.backend
        )
        
        key = kdf.derive(master_secret_bytes)
        return key
    
    def get_key_id(self, file_id: str) -> str:
        """Generate key identifier for a file."""
        return hashlib.sha256(f"{file_id}_key".encode()).hexdigest()[:16]
    
    async def encrypt_file(
        self,
        file_content: bytes,
        file_id: str,
        storage_path: Path
    ) -> tuple[bytes, str]:
        """
        Encrypt file content using AES-256.
        
        Args:
            file_content: Raw file bytes to encrypt
            file_id: Unique file identifier
            storage_path: Path where encrypted file will be stored
            
        Returns:
            Tuple of (encrypted_content, key_id)
        """
        # Generate unique key for this file
        key = self.generate_key(file_id)
        key_id = self.get_key_id(file_id)
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(file_content) + padder.finalize()
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend IV to encrypted data
        encrypted_with_iv = iv + encrypted_data
        
        # Save encrypted file
        async with aiofiles.open(storage_path, 'wb') as f:
            await f.write(encrypted_with_iv)
        
        return encrypted_with_iv, key_id
    
    async def decrypt_file(
        self,
        encrypted_content: bytes,
        file_id: str
    ) -> bytes:
        """
        Decrypt file content.
        
        Args:
            encrypted_content: Encrypted file bytes (with IV prepended)
            file_id: Unique file identifier
            
        Returns:
            Decrypted file bytes
        """
        # Extract IV (first 16 bytes)
        iv = encrypted_content[:16]
        encrypted_data = encrypted_content[16:]
        
        # Generate same key used for encryption
        key = self.generate_key(file_id)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(padded_data) + unpadder.finalize()
        
        return decrypted_data
    
    async def encrypt_and_store(
        self,
        file_content: bytes,
        file_id: str,
        original_filename: str
    ) -> tuple[Path, str]:
        """
        Encrypt file and store in encrypted directory.
        
        Args:
            file_content: Raw file bytes
            file_id: Unique file identifier
            original_filename: Original filename
            
        Returns:
            Tuple of (storage_path, key_id)
        """
        storage_filename = f"{file_id}_encrypted_{original_filename}"
        storage_path = self.encrypted_dir / storage_filename
        
        encrypted_content, key_id = await self.encrypt_file(
            file_content,
            file_id,
            storage_path
        )
        
        return storage_path, key_id
    
    async def decrypt_and_retrieve(
        self,
        file_id: str,
        encrypted_filename: str
    ) -> Optional[bytes]:
        """
        Decrypt and retrieve file content.
        
        Args:
            file_id: Unique file identifier
            encrypted_filename: Encrypted filename
            
        Returns:
            Decrypted file bytes or None if not found
        """
        encrypted_path = self.encrypted_dir / encrypted_filename
        
        if not encrypted_path.exists():
            return None
        
        async with aiofiles.open(encrypted_path, 'rb') as f:
            encrypted_content = await f.read()
        
        return await self.decrypt_file(encrypted_content, file_id)

