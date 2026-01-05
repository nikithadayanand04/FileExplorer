"""
Policy decision engine for CryptoFS++.
Makes autonomous decisions about encryption, access control, and file handling.
"""
from typing import Dict, Any, List
from app.models.file import FileMetadata, SensitivityLevel, EncryptionStatus, FileZone
from app.models.user import UserRole

class PolicyEngine:
    """
    Autonomous policy decision engine.
    Makes encryption, access control, and zone assignment decisions based on policies.
    """
    
    def __init__(self):
        """Initialize policy engine with default policies."""
        self.policies = self._initialize_policies()
    
    def _initialize_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize policy rules."""
        return {
            'encryption_policy': {
                'sensitivity_threshold': 70,
                'always_encrypt_entities': ['face', 'id_card', 'api_key', 'password', 'aadhaar', 'pan', 'ssn'],
                'always_encrypt_classifications': [SensitivityLevel.CRITICAL, SensitivityLevel.HIGH]
            },
            'access_control_policy': {
                'role_permissions': {
                    UserRole.ADMIN: ['READ', 'WRITE', 'DELETE', 'MOVE'],
                    UserRole.USER: ['READ', 'WRITE'],
                    UserRole.VIEWER: ['READ'],
                    UserRole.GUEST: []
                },
                'sensitivity_restrictions': {
                    SensitivityLevel.CRITICAL: [UserRole.ADMIN],
                    SensitivityLevel.HIGH: [UserRole.ADMIN, UserRole.USER],
                    SensitivityLevel.MEDIUM: [UserRole.ADMIN, UserRole.USER, UserRole.VIEWER],
                    SensitivityLevel.LOW: [UserRole.ADMIN, UserRole.USER, UserRole.VIEWER, UserRole.GUEST]
                }
            },
            'zone_policy': {
                'auto_move_threshold': 10,  # Score change threshold for auto-move
                'require_approval_zones': [FileZone.COLD_STORAGE]
            }
        }
    
    def decide_encryption(
        self,
        sensitivity_score: int,
        classification: SensitivityLevel,
        detected_entities: List[str]
    ) -> tuple[bool, str, List[str]]:
        """
        Decide if file should be encrypted based on policies.
        
        Args:
            sensitivity_score: File sensitivity score
            classification: AI classification level
            detected_entities: List of detected sensitive entities
            
        Returns:
            Tuple of (should_encrypt, policy_rule, reasons)
        """
        reasons = []
        policy = self.policies['encryption_policy']
        
        # Check sensitivity threshold
        if sensitivity_score > policy['sensitivity_threshold']:
            reasons.append(f"Sensitivity score {sensitivity_score} exceeds threshold {policy['sensitivity_threshold']}")
            return True, "SENSITIVITY_THRESHOLD", reasons
        
        # Check always-encrypt entities
        for entity in detected_entities:
            if entity in policy['always_encrypt_entities']:
                reasons.append(f"Detected always-encrypt entity: {entity}")
                return True, "ALWAYS_ENCRYPT_ENTITY", reasons
        
        # Check classification
        if classification in policy['always_encrypt_classifications']:
            reasons.append(f"Classification {classification.value} requires encryption")
            return True, "CLASSIFICATION_POLICY", reasons
        
        return False, "NO_ENCRYPTION_REQUIRED", ["File does not meet encryption criteria"]
    
    def decide_access(
        self,
        user_role: UserRole,
        file_sensitivity: SensitivityLevel,
        action: str,
        behavioral_flags: List[str] = None
    ) -> tuple[bool, str, List[str]]:
        """
        Decide if user should have access to file.
        
        Args:
            user_role: User's role
            file_sensitivity: File sensitivity level
            action: Requested action (READ, WRITE, DELETE, MOVE)
            behavioral_flags: List of behavioral anomaly flags
            
        Returns:
            Tuple of (allowed, reason, explanation)
        """
        behavioral_flags = behavioral_flags or []
        reasons = []
        
        policy = self.policies['access_control_policy']
        
        # Check role permissions
        role_permissions = policy['role_permissions'].get(user_role, [])
        if action not in role_permissions:
            reasons.append(f"Role {user_role.value} does not have {action} permission")
            return False, "INSUFFICIENT_ROLE_PERMISSIONS", reasons
        
        # Check sensitivity restrictions
        allowed_roles = policy['sensitivity_restrictions'].get(file_sensitivity, [])
        if user_role not in allowed_roles:
            reasons.append(f"File sensitivity {file_sensitivity.value} restricts access to {[r.value for r in allowed_roles]}")
            return False, "SENSITIVITY_RESTRICTION", reasons
        
        # Check behavioral flags
        if behavioral_flags:
            critical_flags = ['suspicious_access_pattern', 'multiple_failed_attempts', 'unusual_time']
            if any(flag in behavioral_flags for flag in critical_flags):
                reasons.append(f"Behavioral flags detected: {', '.join(behavioral_flags)}")
                return False, "BEHAVIORAL_ANOMALY", reasons
        
        reasons.append(f"Access granted: {user_role.value} has {action} permission for {file_sensitivity.value} files")
        return True, "ACCESS_GRANTED", reasons
    
    def decide_zone_transition(
        self,
        current_zone: FileZone,
        new_sensitivity_score: int,
        previous_score: int
    ) -> tuple[FileZone, bool, str]:
        """
        Decide if file should transition to a different zone.
        
        Args:
            current_zone: Current file zone
            new_sensitivity_score: New sensitivity score
            previous_score: Previous sensitivity score
            
        Returns:
            Tuple of (new_zone, should_transition, reason)
        """
        score_change = abs(new_sensitivity_score - previous_score)
        policy = self.policies['zone_policy']
        
        # Determine target zone based on score
        if new_sensitivity_score <= 30:
            target_zone = FileZone.PUBLIC
        elif new_sensitivity_score <= 60:
            target_zone = FileZone.MONITORED
        elif new_sensitivity_score <= 80:
            target_zone = FileZone.CRYPTO_VAULT
        else:
            target_zone = FileZone.COLD_STORAGE
        
        # Check if transition is needed
        if target_zone == current_zone:
            return current_zone, False, "Zone assignment unchanged"
        
        # Check if score change is significant enough
        if score_change < policy['auto_move_threshold']:
            return current_zone, False, f"Score change {score_change} below threshold {policy['auto_move_threshold']}"
        
        # Check if approval required
        if target_zone in policy['require_approval_zones']:
            return target_zone, True, f"Transition to {target_zone.value} requires approval"
        
        return target_zone, True, f"Sensitivity score change ({previous_score} → {new_sensitivity_score}) triggers zone transition"
    
    def get_policy_explanation(
        self,
        decision_type: str,
        decision_result: tuple
    ) -> Dict[str, Any]:
        """
        Generate human-readable explanation for policy decision.
        
        Args:
            decision_type: Type of decision (encryption, access, zone_transition)
            decision_result: Result tuple from decision method
            
        Returns:
            Dictionary with explanation details
        """
        if decision_type == 'encryption':
            should_encrypt, rule, reasons = decision_result
            return {
                'decision': 'ENCRYPT' if should_encrypt else 'NO_ENCRYPTION',
                'policy_rule': rule,
                'reasons': reasons,
                'explanation': self._format_encryption_explanation(should_encrypt, rule, reasons)
            }
        elif decision_type == 'access':
            allowed, reason, explanations = decision_result
            return {
                'decision': 'ALLOWED' if allowed else 'DENIED',
                'reason': reason,
                'explanations': explanations,
                'explanation': self._format_access_explanation(allowed, reason, explanations)
            }
        elif decision_type == 'zone_transition':
            new_zone, should_transition, reason = decision_result
            return {
                'decision': 'TRANSITION' if should_transition else 'NO_TRANSITION',
                'new_zone': new_zone.value if should_transition else None,
                'reason': reason,
                'explanation': self._format_zone_explanation(should_transition, new_zone, reason)
            }
        
        return {'error': 'Unknown decision type'}
    
    def _format_encryption_explanation(self, should_encrypt: bool, rule: str, reasons: List[str]) -> str:
        """Format encryption decision explanation."""
        if should_encrypt:
            return f"**Encryption Required**\n\nPolicy Rule: {rule}\n\nReasons:\n" + "\n".join(f"  - {r}" for r in reasons)
        else:
            return f"**No Encryption Required**\n\nPolicy Rule: {rule}\n\nReasons:\n" + "\n".join(f"  - {r}" for r in reasons)
    
    def _format_access_explanation(self, allowed: bool, reason: str, explanations: List[str]) -> str:
        """Format access decision explanation."""
        status = "**ALLOWED**" if allowed else "**DENIED**"
        return f"{status}\n\nReason: {reason}\n\nDetails:\n" + "\n".join(f"  - {e}" for e in explanations)
    
    def _format_zone_explanation(self, should_transition: bool, new_zone: FileZone, reason: str) -> str:
        """Format zone transition explanation."""
        if should_transition:
            return f"**Zone Transition Required**\n\nNew Zone: {new_zone.value}\n\nReason: {reason}"
        else:
            return f"**No Zone Transition**\n\nReason: {reason}"

