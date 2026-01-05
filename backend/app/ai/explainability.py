"""
Explainable AI module for generating human-readable explanations
of AI decisions and classifications.
"""
from typing import Dict, Any, List
from datetime import datetime

class ExplainabilityEngine:
    """
    Generates explainable, human-readable explanations for AI decisions.
    Provides reasoning, confidence scores, and policy triggers.
    """
    
    def __init__(self):
        """Initialize explainability engine."""
        self.explanation_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize explanation templates for different scenarios."""
        return {
            'encryption': "This file was encrypted because: {reasons}",
            'zone_assignment': "File assigned to {zone} zone because: {reasons}",
            'access_denied': "Access denied because: {reasons}",
            'sensitivity_classification': "File classified as {classification} because: {reasons}",
            'policy_trigger': "Policy rule '{rule}' triggered: {reason}"
        }
    
    def explain_classification(
        self,
        sensitivity_score: int,
        classification: str,
        detected_entities: List[str],
        reasons: List[str],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Generate explanation for file classification decision.
        
        Args:
            sensitivity_score: Calculated sensitivity score (0-100)
            classification: Sensitivity level (LOW/MEDIUM/HIGH/CRITICAL)
            detected_entities: List of detected entity types
            reasons: List of detection reasons
            confidence: AI confidence score (0-1)
            
        Returns:
            Dictionary with explanation components
        """
        explanation_parts = []
        
        # Start with classification
        explanation_parts.append(
            f"This file has been classified as **{classification}** "
            f"(sensitivity score: {sensitivity_score}/100)"
        )
        
        # Add detected entities
        if detected_entities:
            entity_list = ", ".join(detected_entities)
            explanation_parts.append(f"Detected sensitive content: {entity_list}")
        
        # Add specific reasons
        if reasons:
            explanation_parts.append("Specific findings:")
            for i, reason in enumerate(reasons, 1):
                explanation_parts.append(f"  {i}. {reason}")
        
        # Add confidence
        confidence_percent = int(confidence * 100)
        explanation_parts.append(
            f"AI confidence: {confidence_percent}%"
        )
        
        # Determine zone recommendation
        zone = self._score_to_zone(sensitivity_score)
        explanation_parts.append(
            f"Recommended zone: **{zone.replace('_', ' ').title()}**"
        )
        
        full_explanation = "\n\n".join(explanation_parts)
        
        return {
            'summary': f"File classified as {classification} with {sensitivity_score}/100 sensitivity",
            'full_explanation': full_explanation,
            'detected_entities': detected_entities,
            'reasons': reasons,
            'confidence': confidence,
            'confidence_percent': confidence_percent,
            'sensitivity_score': sensitivity_score,
            'classification': classification,
            'recommended_zone': zone,
            'explained_at': datetime.utcnow().isoformat()
        }
    
    def explain_encryption_decision(
        self,
        encrypted: bool,
        policy_rule: str,
        reasons: List[str],
        sensitivity_score: int
    ) -> Dict[str, Any]:
        """
        Generate explanation for encryption decision.
        
        Args:
            encrypted: Whether file was encrypted
            policy_rule: Policy rule that triggered encryption
            reasons: List of reasons for encryption
            sensitivity_score: File sensitivity score
            
        Returns:
            Dictionary with encryption explanation
        """
        if encrypted:
            explanation = f"This file was **automatically encrypted** because:\n\n"
            explanation += f"**Policy Rule**: {policy_rule}\n\n"
            explanation += "**Reasons**:\n"
            for i, reason in enumerate(reasons, 1):
                explanation += f"  {i}. {reason}\n"
            explanation += f"\n**Sensitivity Score**: {sensitivity_score}/100"
            
            summary = f"File encrypted due to {policy_rule} (sensitivity: {sensitivity_score})"
        else:
            explanation = f"This file was **not encrypted** because:\n\n"
            explanation += f"**Sensitivity Score**: {sensitivity_score}/100 (below encryption threshold)\n"
            explanation += "**Policy**: Only files with sensitivity > 70 are automatically encrypted"
            
            summary = f"File not encrypted (sensitivity: {sensitivity_score} < threshold)"
        
        return {
            'encrypted': encrypted,
            'summary': summary,
            'full_explanation': explanation,
            'policy_rule': policy_rule,
            'reasons': reasons,
            'sensitivity_score': sensitivity_score,
            'explained_at': datetime.utcnow().isoformat()
        }
    
    def explain_zone_assignment(
        self,
        zone: str,
        sensitivity_score: int,
        reasons: List[str]
    ) -> Dict[str, Any]:
        """Generate explanation for zone assignment."""
        zone_names = {
            'public': '🟢 Public Zone',
            'monitored': '🟡 Monitored Zone',
            'crypto_vault': '🔴 Crypto Vault',
            'cold_storage': '🧊 Cold Storage'
        }
        
        zone_display = zone_names.get(zone, zone)
        
        explanation = f"File assigned to **{zone_display}**\n\n"
        explanation += f"**Sensitivity Score**: {sensitivity_score}/100\n\n"
        explanation += "**Assignment Logic**:\n"
        
        if sensitivity_score <= 30:
            explanation += "  - Low sensitivity (0-30) → Public Zone"
        elif sensitivity_score <= 60:
            explanation += "  - Medium sensitivity (31-60) → Monitored Zone"
        elif sensitivity_score <= 80:
            explanation += "  - High sensitivity (61-80) → Crypto Vault"
        else:
            explanation += "  - Critical sensitivity (81-100) → Cold Storage"
        
        if reasons:
            explanation += "\n\n**Reasons**:\n"
            for i, reason in enumerate(reasons, 1):
                explanation += f"  {i}. {reason}\n"
        
        return {
            'zone': zone,
            'zone_display': zone_display,
            'summary': f"File assigned to {zone_display}",
            'full_explanation': explanation,
            'sensitivity_score': sensitivity_score,
            'reasons': reasons,
            'explained_at': datetime.utcnow().isoformat()
        }
    
    def explain_access_decision(
        self,
        allowed: bool,
        user_role: str,
        file_sensitivity: int,
        reasons: List[str],
        behavioral_flags: List[str] = None
    ) -> Dict[str, Any]:
        """Generate explanation for access control decision."""
        behavioral_flags = behavioral_flags or []
        
        if allowed:
            explanation = f"**Access ALLOWED**\n\n"
            explanation += f"**User Role**: {user_role}\n"
            explanation += f"**File Sensitivity**: {file_sensitivity}/100\n"
        else:
            explanation = f"**Access DENIED**\n\n"
            explanation += f"**User Role**: {user_role}\n"
            explanation += f"**File Sensitivity**: {file_sensitivity}/100\n"
        
        if reasons:
            explanation += "\n**Reasons**:\n"
            for i, reason in enumerate(reasons, 1):
                explanation += f"  {i}. {reason}\n"
        
        if behavioral_flags:
            explanation += "\n**Behavioral Flags**:\n"
            for flag in behavioral_flags:
                explanation += f"  - {flag}\n"
        
        return {
            'allowed': allowed,
            'summary': f"Access {'ALLOWED' if allowed else 'DENIED'}",
            'full_explanation': explanation,
            'user_role': user_role,
            'file_sensitivity': file_sensitivity,
            'reasons': reasons,
            'behavioral_flags': behavioral_flags,
            'explained_at': datetime.utcnow().isoformat()
        }
    
    def _score_to_zone(self, score: int) -> str:
        """Convert sensitivity score to zone name."""
        if score <= 30:
            return 'public'
        elif score <= 60:
            return 'monitored'
        elif score <= 80:
            return 'crypto_vault'
        else:
            return 'cold_storage'

