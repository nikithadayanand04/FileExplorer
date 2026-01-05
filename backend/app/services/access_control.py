"""
Zero-trust access control service for CryptoFS++.
Implements AI-enhanced behavioral analysis and dynamic permission enforcement.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.user import UserRole
from app.models.file import SensitivityLevel
from app.models.audit import AuditEvent

class AccessControlService:
    """
    Zero-trust access control service with behavioral anomaly detection.
    Analyzes access patterns and enforces dynamic permissions.
    """
    
    def __init__(self):
        """Initialize access control service."""
        self.access_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.suspicious_patterns: Dict[str, List[str]] = defaultdict(list)
    
    def analyze_access_request(
        self,
        user_id: str,
        file_id: str,
        action: str,
        file_sensitivity: SensitivityLevel,
        user_role: UserRole,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> tuple[bool, List[str], Dict[str, Any]]:
        """
        Analyze access request and determine if it should be allowed.
        
        Args:
            user_id: User requesting access
            file_id: File being accessed
            action: Requested action (READ, WRITE, DELETE, MOVE)
            file_sensitivity: File sensitivity level
            user_role: User's role
            ip_address: Optional IP address
            user_agent: Optional user agent string
            
        Returns:
            Tuple of (allowed, behavioral_flags, analysis_metadata)
        """
        behavioral_flags = []
        analysis_metadata = {
            'access_time': datetime.utcnow(),
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        # Check for suspicious access patterns
        flags = self._detect_behavioral_anomalies(
            user_id, file_id, action, ip_address
        )
        behavioral_flags.extend(flags)
        
        # Check access frequency
        recent_accesses = self._get_recent_accesses(user_id, file_id, minutes=5)
        if len(recent_accesses) > 10:
            behavioral_flags.append('high_frequency_access')
            analysis_metadata['access_frequency'] = len(recent_accesses)
        
        # Check for failed attempts
        recent_failures = self._get_recent_failures(user_id, minutes=15)
        if len(recent_failures) > 3:
            behavioral_flags.append('multiple_failed_attempts')
            analysis_metadata['recent_failures'] = len(recent_failures)
        
        # Check unusual access time (simplified: outside 9-5)
        current_hour = datetime.utcnow().hour
        if current_hour < 9 or current_hour > 17:
            behavioral_flags.append('unusual_time')
            analysis_metadata['access_hour'] = current_hour
        
        # Check IP consistency
        if ip_address:
            user_ips = self._get_user_ips(user_id)
            if len(user_ips) > 3 and ip_address not in user_ips:
                behavioral_flags.append('ip_inconsistency')
                analysis_metadata['ip_history'] = list(user_ips)
        
        # Determine if access should be allowed based on flags
        critical_flags = ['multiple_failed_attempts', 'suspicious_access_pattern']
        allowed = not any(flag in behavioral_flags for flag in critical_flags)
        
        # Record access attempt
        self._record_access_attempt(user_id, file_id, action, allowed, ip_address)
        
        analysis_metadata['behavioral_flags'] = behavioral_flags
        analysis_metadata['allowed'] = allowed
        
        return allowed, behavioral_flags, analysis_metadata
    
    def _detect_behavioral_anomalies(
        self,
        user_id: str,
        file_id: str,
        action: str,
        ip_address: Optional[str]
    ) -> List[str]:
        """Detect behavioral anomalies in access pattern."""
        flags = []
        
        # Check for rapid file switching
        recent_files = [
            access['file_id']
            for access in self.access_history.get(user_id, [])[-10:]
            if (datetime.utcnow() - access['timestamp']).seconds < 60
        ]
        unique_files = len(set(recent_files))
        if unique_files > 5:
            flags.append('rapid_file_switching')
        
        # Check for access pattern (trying to access many sensitive files)
        sensitive_accesses = [
            access
            for access in self.access_history.get(user_id, [])
            if access.get('sensitivity') in ['HIGH', 'CRITICAL']
        ]
        if len(sensitive_accesses) > 10:
            flags.append('suspicious_access_pattern')
        
        return flags
    
    def _get_recent_accesses(
        self,
        user_id: str,
        file_id: str,
        minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent access attempts for user-file pair."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            access
            for access in self.access_history.get(user_id, [])
            if access['file_id'] == file_id and access['timestamp'] > cutoff
        ]
    
    def _get_recent_failures(self, user_id: str, minutes: int = 15) -> List[datetime]:
        """Get recent failed access attempts."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            failure_time
            for failure_time in self.failed_attempts.get(user_id, [])
            if failure_time > cutoff
        ]
    
    def _get_user_ips(self, user_id: str) -> set:
        """Get set of IP addresses used by user."""
        ips = set()
        for access in self.access_history.get(user_id, []):
            if access.get('ip_address'):
                ips.add(access['ip_address'])
        return ips
    
    def _record_access_attempt(
        self,
        user_id: str,
        file_id: str,
        action: str,
        allowed: bool,
        ip_address: Optional[str]
    ):
        """Record access attempt in history."""
        self.access_history[user_id].append({
            'file_id': file_id,
            'action': action,
            'allowed': allowed,
            'timestamp': datetime.utcnow(),
            'ip_address': ip_address
        })
        
        # Keep only last 100 accesses per user
        if len(self.access_history[user_id]) > 100:
            self.access_history[user_id] = self.access_history[user_id][-100:]
        
        # Record failures
        if not allowed:
            self.failed_attempts[user_id].append(datetime.utcnow())
            # Keep only last 20 failures
            if len(self.failed_attempts[user_id]) > 20:
                self.failed_attempts[user_id] = self.failed_attempts[user_id][-20:]
    
    def require_reauthentication(self, user_id: str) -> bool:
        """Determine if user should re-authenticate."""
        recent_failures = self._get_recent_failures(user_id, minutes=30)
        return len(recent_failures) > 5
    
    def get_user_access_summary(self, user_id: str) -> Dict[str, Any]:
        """Get access summary for a user."""
        accesses = self.access_history.get(user_id, [])
        recent_failures = self._get_recent_failures(user_id, minutes=60)
        
        return {
            'total_accesses': len(accesses),
            'recent_failures': len(recent_failures),
            'unique_files_accessed': len(set(a['file_id'] for a in accesses)),
            'requires_reauthentication': self.require_reauthentication(user_id),
            'suspicious_patterns': self.suspicious_patterns.get(user_id, [])
        }
    
    def reset_user_flags(self, user_id: str):
        """Reset behavioral flags for a user (admin action)."""
        if user_id in self.failed_attempts:
            self.failed_attempts[user_id] = []
        if user_id in self.suspicious_patterns:
            self.suspicious_patterns[user_id] = []

