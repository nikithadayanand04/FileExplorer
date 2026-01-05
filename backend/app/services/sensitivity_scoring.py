"""
Sensitivity scoring engine for CryptoFS++.
Determines file sensitivity and zone assignment based on AI analysis.
"""
from app.models.file import FileZone, SensitivityLevel
from app.models.file import FileContentAnalysis
from app.config import settings

class SensitivityScoringEngine:
    """
    Engine for calculating sensitivity scores and determining file zones.
    Uses AI analysis results to make zone assignment decisions.
    """
    
    def __init__(self):
        """Initialize sensitivity scoring engine."""
        self.low_threshold = settings.LOW_THRESHOLD
        self.medium_threshold = settings.MEDIUM_THRESHOLD
        self.high_threshold = settings.HIGH_THRESHOLD
        self.critical_threshold = settings.CRITICAL_THRESHOLD
    
    def calculate_zone(
        self,
        sensitivity_score: int,
        classification: SensitivityLevel,
        detected_entities: list[str]
    ) -> FileZone:
        """
        Determine file zone based on sensitivity score and classification.
        
        Args:
            sensitivity_score: Calculated sensitivity score (0-100)
            classification: AI classification level
            detected_entities: List of detected sensitive entities
            
        Returns:
            FileZone enum value
        """
        # Zone assignment logic
        if sensitivity_score <= self.low_threshold:
            return FileZone.PUBLIC
        elif sensitivity_score <= self.medium_threshold:
            return FileZone.MONITORED
        elif sensitivity_score <= self.high_threshold:
            return FileZone.CRYPTO_VAULT
        else:
            return FileZone.COLD_STORAGE
    
    def should_encrypt(
        self,
        sensitivity_score: int,
        classification: SensitivityLevel,
        detected_entities: list[str]
    ) -> tuple[bool, str]:
        """
        Determine if file should be encrypted based on policy.
        
        Args:
            sensitivity_score: Calculated sensitivity score
            classification: AI classification level
            detected_entities: List of detected sensitive entities
            
        Returns:
            Tuple of (should_encrypt: bool, policy_rule: str)
        """
        # Policy: Encrypt if sensitivity > 70
        if sensitivity_score > 70:
            return True, "SENSITIVITY_THRESHOLD_70"
        
        # Policy: Always encrypt biometric data
        if 'face' in detected_entities or 'biometric' in detected_entities:
            return True, "BIOMETRIC_DATA_POLICY"
        
        # Policy: Always encrypt credentials
        credential_entities = ['api_key', 'password', 'high_entropy_credential']
        if any(entity in detected_entities for entity in credential_entities):
            return True, "CREDENTIAL_POLICY"
        
        # Policy: Encrypt critical classification
        if classification == SensitivityLevel.CRITICAL:
            return True, "CRITICAL_CLASSIFICATION_POLICY"
        
        return False, "BELOW_ENCRYPTION_THRESHOLD"
    
    def get_scoring_explanation(
        self,
        sensitivity_score: int,
        classification: SensitivityLevel,
        zone: FileZone,
        detected_entities: list[str]
    ) -> dict:
        """
        Generate explanation for sensitivity scoring and zone assignment.
        
        Args:
            sensitivity_score: Calculated sensitivity score
            classification: AI classification level
            zone: Assigned file zone
            detected_entities: List of detected sensitive entities
            
        Returns:
            Dictionary with explanation details
        """
        zone_names = {
            FileZone.PUBLIC: "🟢 Public Zone",
            FileZone.MONITORED: "🟡 Monitored Zone",
            FileZone.CRYPTO_VAULT: "🔴 Crypto Vault",
            FileZone.COLD_STORAGE: "🧊 Cold Storage"
        }
        
        return {
            'sensitivity_score': sensitivity_score,
            'classification': classification.value,
            'zone': zone.value,
            'zone_display': zone_names.get(zone, zone.value),
            'detected_entities': detected_entities,
            'scoring_rationale': self._get_rationale(sensitivity_score, detected_entities)
        }
    
    def _get_rationale(self, score: int, entities: list[str]) -> str:
        """Generate rationale for sensitivity score."""
        if score == 0:
            return "No sensitive content detected"
        
        rationale_parts = [f"Score: {score}/100"]
        
        if entities:
            rationale_parts.append(f"Detected: {', '.join(entities)}")
        
        if score > 80:
            rationale_parts.append("Critical sensitivity - multiple high-risk entities detected")
        elif score > 60:
            rationale_parts.append("High sensitivity - sensitive personal or financial data detected")
        elif score > 30:
            rationale_parts.append("Medium sensitivity - some sensitive content detected")
        else:
            rationale_parts.append("Low sensitivity - minimal sensitive content")
        
        return ". ".join(rationale_parts)

