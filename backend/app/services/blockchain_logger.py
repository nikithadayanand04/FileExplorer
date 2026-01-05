"""
Blockchain audit logging service for CryptoFS++.
Implements immutable event logging using a simulated blockchain ledger.
"""
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from uuid import uuid4
import aiofiles

from app.config import settings
from app.models.audit import AuditEvent, BlockchainBlock

class BlockchainLogger:
    """
    Lightweight blockchain-based audit logger.
    Creates immutable blocks of audit events for trust and transparency.
    """
    
    def __init__(self):
        """Initialize blockchain logger."""
        self.ledger_file = settings.BLOCKCHAIN_FILE
        self.chain: List[BlockchainBlock] = []
        self.pending_events: List[AuditEvent] = []
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize blockchain with genesis block."""
        if self.ledger_file.exists():
            self._load_chain()
        else:
            # Create genesis block
            genesis_block = BlockchainBlock(
                index=0,
                timestamp=datetime.utcnow(),
                events=[],
                previous_hash="0" * 64,
                hash=self._calculate_block_hash(0, datetime.utcnow(), [], "0" * 64)
            )
            self.chain = [genesis_block]
            # Save synchronously during initialization
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule it
                    asyncio.create_task(self._save_chain())
                else:
                    loop.run_until_complete(self._save_chain())
            except RuntimeError:
                # No event loop, save synchronously using aiofiles sync API
                import json
                chain_data = {
                    'blocks': [
                        {
                            'index': genesis_block.index,
                            'timestamp': genesis_block.timestamp.isoformat(),
                            'events': [],
                            'previous_hash': genesis_block.previous_hash,
                            'hash': genesis_block.hash
                        }
                    ]
                }
                with open(self.ledger_file, 'w') as f:
                    json.dump(chain_data, f, indent=2, default=str)
    
    def _calculate_block_hash(
        self,
        index: int,
        timestamp: datetime,
        events: List[AuditEvent],
        previous_hash: str
    ) -> str:
        """Calculate SHA-256 hash of block."""
        block_string = json.dumps({
            'index': index,
            'timestamp': timestamp.isoformat(),
            'events': [e.dict() for e in events],
            'previous_hash': previous_hash
        }, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    async def log_event(
        self,
        event_type: str,
        action: str,
        result: str,
        file_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an audit event to the blockchain.
        
        Args:
            event_type: Type of event (FILE_UPLOAD, ENCRYPTION, ACCESS, etc.)
            action: Action performed
            result: Result of action (ALLOWED, DENIED, SUCCESS, FAILED)
            file_id: Optional file ID
            user_id: Optional user ID
            metadata: Optional additional metadata
            
        Returns:
            AuditEvent object
        """
        # Get previous block hash
        previous_hash = self.chain[-1].hash if self.chain else "0" * 64
        
        # Create audit event
        event = AuditEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            file_id=file_id,
            user_id=user_id,
            action=action,
            result=result,
            metadata=metadata or {},
            previous_hash=previous_hash
        )
        
        # Add to pending events
        self.pending_events.append(event)
        
        # Create block if we have enough events (or immediately for critical events)
        if len(self.pending_events) >= 5 or event_type in ['ACCESS', 'ENCRYPTION']:
            await self._create_block()
        
        return event
    
    async def _create_block(self):
        """Create a new block with pending events."""
        if not self.pending_events:
            return
        
        # Get previous block
        previous_block = self.chain[-1] if self.chain else None
        previous_hash = previous_block.hash if previous_block else "0" * 64
        
        # Calculate block hash for events
        for event in self.pending_events:
            event.previous_hash = previous_hash
        
        # Create new block
        new_index = len(self.chain)
        block_timestamp = datetime.utcnow()
        
        # Calculate hash
        block_hash = self._calculate_block_hash(
            new_index,
            block_timestamp,
            self.pending_events,
            previous_hash
        )
        
        # Set block hash and index for events
        for i, event in enumerate(self.pending_events):
            event.block_hash = block_hash
            event.block_index = new_index
        
        # Create block
        new_block = BlockchainBlock(
            index=new_index,
            timestamp=block_timestamp,
            events=self.pending_events.copy(),
            previous_hash=previous_hash,
            hash=block_hash
        )
        
        # Add to chain
        self.chain.append(new_block)
        
        # Clear pending events
        self.pending_events = []
        
        # Save chain
        await self._save_chain()
    
    async def _save_chain(self):
        """Save blockchain to file."""
        chain_data = {
            'blocks': [
                {
                    'index': block.index,
                    'timestamp': block.timestamp.isoformat(),
                    'events': [e.dict() for e in block.events],
                    'previous_hash': block.previous_hash,
                    'hash': block.hash
                }
                for block in self.chain
            ]
        }
        
        async with aiofiles.open(self.ledger_file, 'w') as f:
            await f.write(json.dumps(chain_data, indent=2, default=str))
    
    def _load_chain(self):
        """Load blockchain from file."""
        try:
            with open(self.ledger_file, 'r') as f:
                chain_data = json.load(f)
            
            self.chain = []
            for block_data in chain_data.get('blocks', []):
                events = []
                for event_data in block_data.get('events', []):
                    # Ensure event_id exists
                    if 'event_id' not in event_data:
                        event_data['event_id'] = str(uuid4())
                    events.append(AuditEvent(**event_data))
                
                block = BlockchainBlock(
                    index=block_data['index'],
                    timestamp=datetime.fromisoformat(block_data['timestamp']),
                    events=events,
                    previous_hash=block_data['previous_hash'],
                    hash=block_data['hash']
                )
                self.chain.append(block)
        except Exception as e:
            print(f"Error loading chain: {e}")
            self.chain = []
    
    def get_chain(self) -> List[BlockchainBlock]:
        """Get entire blockchain."""
        return self.chain
    
    def get_file_audit_trail(self, file_id: str) -> List[AuditEvent]:
        """Get all audit events for a specific file."""
        events = []
        for block in self.chain:
            for event in block.events:
                if event.file_id == file_id:
                    events.append(event)
        return events
    
    def get_user_audit_trail(self, user_id: str) -> List[AuditEvent]:
        """Get all audit events for a specific user."""
        events = []
        for block in self.chain:
            for event in block.events:
                if event.user_id == user_id:
                    events.append(event)
        return events
    
    def verify_chain(self) -> bool:
        """Verify blockchain integrity."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify previous hash
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Verify block hash
            calculated_hash = self._calculate_block_hash(
                current_block.index,
                current_block.timestamp,
                current_block.events,
                current_block.previous_hash
            )
            if calculated_hash != current_block.hash:
                return False
        
        return True
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics."""
        total_events = sum(len(block.events) for block in self.chain)
        return {
            'total_blocks': len(self.chain),
            'total_events': total_events,
            'pending_events': len(self.pending_events),
            'chain_valid': self.verify_chain(),
            'last_block_hash': self.chain[-1].hash if self.chain else None
        }

